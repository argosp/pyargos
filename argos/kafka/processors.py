import pydoc
import pandas
from . import toPandasDeserializer
from kafka import KafkaConsumer, KafkaProducer
from argos import tbHome
import json
import paho.mqtt.client as mqtt
import logging
from multiprocessing import Pool


class ProjectProcessor(object):
    _projectName = None
    _kafkaHost = None
    _consumersConf = None

    _kafkaProducer = None

    _tbh = None
    _tbHost = None

    _clients = None

    @property
    def consumersConf(self):
        return self._consumersConf

    @property
    def projectName(self):
        return self._projectName

    @property
    def kafkaHost(self):
        return self._kafkaHost

    @property
    def tbh(self):
        return self._tbh

    @property
    def tbHost(self):
        return self._tbHost

    @property
    def clients(self):
        return self._clients

    @property
    def kafkaProducer(self):
        return self._kafkaProducer

    def __init__(self, projectName, kafkaHost, expConf, consumersConf):
        self._projectName = projectName
        self._kafkaHost = kafkaHost

        self._kafkaProducer = KafkaProducer(bootstrap_servers=kafkaHost)

        with open(expConf,'r') as jsonFile:
            credentialMap = json.load(jsonFile)
        self._tbh = tbHome(credentialMap["connection"])
        self._tbHost = credentialMap["connection"]["server"]["ip"]

        self._clients = dict()

        self._consumersConf = consumersConf

    def getClient(self, deviceName):
        if deviceName not in self.clients:
            client = mqtt.Client("Me_%s" % deviceName)
            client.on_connect = self._on_connect

            accessToken = self.tbh.deviceHome.createProxy(deviceName).getCredentials()
            client.username_pw_set(accessToken, password=None)
            client.on_disconnect = self._on_disconnect
            client.connect(host=self.tbHost, port=1883)
            self._clients[deviceName] = client
            client.loop_start()
        return self.clients[deviceName]

    def start(self):
        with Pool(self._getPoolNum()) as p:
            startProcessesInputs = []
            for topic, topicDict in self.consumersConf.items():
                for window, windowDict in topicDict.items():
                    window = None if window == 'None' else int(window)
                    for slide, slideDict in windowDict.items():
                        slide = None if slide == 'None' else int(slide)
                        startProcessesInputs.append((topic, window, slide, slideDict))
            print('---- ready ----')
            p.starmap(self._startProcesses, startProcessesInputs)

    def _startProcesses(self, topic, window, slide, processesDict):
        ConsumerProcessor(self, topic, window, slide, processesDict).start()

    @staticmethod
    def _on_disconnect(client, userdata, rc=0):
        logging.debug("DisConnected result code " + str(rc))
        client.loop_stop()

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
        else:
            print("Connection failed")

    def _getPoolNum(self):
        poolNum = 0
        for topic, topicDict in self.consumersConf.items():
            for window, windowDict in topicDict.items():
                for slide, slideDict in windowDict.items():
                    poolNum += len(slideDict)
        return poolNum


class ConsumerProcessor(object):
    _projectProcessor = None
    _topic = None
    _window = None
    _slide = None

    _windowProcessor = None
    _kafkaConsumer = None

    @property
    def kafkaConsumer(self):
        return self._kafkaConsumer

    @property
    def processesDict(self):
        return self._processesDict

    @property
    def window(self):
        return self._window

    @property
    def slide(self):
        return self._slide

    def __init__(self, projectProcessor, topic, window, slide, processesDict):
        self._projectProcessor = projectProcessor
        self._topic = topic
        self._window = window
        self._slide = slide
        self._processesDict = processesDict

        self._windowProcessor = WindowProcessor(window=window, slide=slide)

        self._kafkaConsumer = KafkaConsumer(topic,
                                            bootstrap_servers=projectProcessor.kafkaHost,
                                            auto_offset_reset='latest',
                                            enable_auto_commit=True
                                            # group_id=group_id
                                            )

    def getClient(self, deviceName):
        self._projectProcessor.getClient(deviceName=deviceName)

    def start(self):
        for message in self.kafkaConsumer:
            if self.window is None:
                data = self._windowProcessor.processMessage(message=message)
                windowFirstTime = None
            else:
                data, windowFirstTime = self._windowProcessor.processMessage(message=message)
            if data is not None:
                for process, processArgs in self.processesDict.items():
                    if windowFirstTime is None:
                        pydoc.locate(process)(processor=self._projectProcessor, data=data, **processArgs)
                    else:
                        pydoc.locate(process)(processor=self._projectProcessor, data=data, windowFirstTime=windowFirstTime, **processArgs)


class WindowProcessor(object):
    _window = None
    _slide = None
    _df = None
    _lastTime = None
    _resampled_df = None

    @property
    def window(self):
        return self._window

    @property
    def slide(self):
        return self._slide

    def __init__(self, window, slide):
        """
        :param window: Time window size in seconds if None no window
        :param slide: Sliding time in seconds if None no slide(and window also None)
        """
        self._window = window
        self._slide = slide
        self._df = pandas.DataFrame()

        if self.window is not None:
            self._n = int(self.window/self.slide)
        else:
            self._n = None

        self._lastTime = None

    def processMessage(self, message):
        if self.window is None:
            data = self.processMessageWithoutWindow(message=message)
        else:
            data = self.processMessageWithWindow(message=message)
        return data

    def processMessageWithWindow(self, message):
        self._df = self._df.append(toPandasDeserializer(message.value), sort=True)
        if self._lastTime is None or (self._lastTime + pandas.Timedelta('%ss' % self.slide) < self._df.tail(1).index[0]):
            self._resampled_df = self._df.resample('%ss' % self.slide)
        timeList = list(self._resampled_df.groups.keys())
        data = None
        if len(timeList) > self._n:
            try:
                if self._lastTime != timeList[0]:
                    self._lastTime = timeList[0]
                    data = self._resampled_df.get_group(timeList[0])
                    self._df = self._df[timeList[1]:]
            except Exception as exception:
                print(f'Exception {exception} handled')
        return data, timeList[0]

    def processMessageWithoutWindow(self, message):
        return toPandasDeserializer(message.value)