import pydoc
import pandas
from . import toPandasDeserializer
from kafka import KafkaConsumer, KafkaProducer
from argos import tbHome
import json
import paho.mqtt.client as mqtt
import logging
import time


class Processor(object):
    _projectName = None
    _kafkaHost = None
    _topic = None
    _window = None
    _slide = None
    _processes = None
    _tbCredentialMap = None

    _windowProcessor = None
    _kafkaProducer = None
    _kafkaConsumer = None

    _clients = None

    @property
    def clients(self):
        return self._clients

    @property
    def tbh(self):
        return tbHome(self._tbCredentialMap["connection"])

    @property
    def tbHost(self):
        return self._tbCredentialMap["connection"]["server"]["ip"]

    @property
    def projectName(self):
        return self._projectName

    @property
    def kafkaHost(self):
        return self._kafkaHost

    @property
    def kafkaProducer(self):
        return self._kafkaProducer

    @property
    def kafkaConsumer(self):
        return self._kafkaConsumer

    @property
    def processesDict(self):
        return self._processesDict

    @property
    def topic(self):
        return self._topic

    @property
    def window(self):
        return self._window

    @property
    def slide(self):
        return self._slide

    @property
    def currentWindowTime(self):
        return self._currentWindowTime

    def __init__(self, projectName, kafkaHost, expConf, topic, window, slide, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param expConf: The path to the experiment configuration file
        :param topic: The topic to process
        :param window: The window to process in seconds
        :param slide: The slide of the window in seconds
        :param processesDict: The dictionary of the processes to run.
        """
        self._projectName = projectName
        self._kafkaHost = kafkaHost
        self._topic = topic
        self._window = window
        self._slide = slide
        self._processesDict = processesDict

        with open(expConf, 'r') as jsonFile:
            self._tbCredentialMap = json.load(jsonFile)

        self._windowProcessor = WindowProcessor(window=window, slide=slide)
        self._kafkaProducer = KafkaProducer(bootstrap_servers=kafkaHost)
        self._kafkaConsumer = KafkaConsumer(topic,
                                            bootstrap_servers=kafkaHost,
                                            auto_offset_reset='latest',
                                            enable_auto_commit=True
                                            # group_id=group_id
                                            )

        self._clients = dict()
        self._initiateClients()

        self._currentWindowTime = None

    def on_disconnect(self, client, userdata, rc=0):
        logging.debug("DisConnected result code " + str(rc))
        client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
        else:
            print("Connection failed")

    def _initiateClients(self):
        devices = self.tbh.deviceHome.getAllEntitiesName()
        for deviceName in devices:
            if self.topic in deviceName and self.window is None:
                #print('Connecting to %s' % deviceName)
                client = mqtt.Client("Me_%s" % deviceName)
                client.on_connect = self.on_connect

                accessToken = self.tbh.deviceHome.createProxy(deviceName).getCredentials()
                client.username_pw_set(accessToken, password=None)
                client.on_disconnect = self.on_disconnect
                client.connect(host=self.tbHost, port=1883)
                self._clients[deviceName] = client
                client.loop_start()
                time.sleep(0.01)

    def getClient(self, deviceName):
        return self.clients[deviceName]

    def start(self):
        for message in self.kafkaConsumer:
            if self.window is None:
                data = self._windowProcessor.processMessage(message=message)
                self._currentWindowTime = None
            else:
                data, self._currentWindowTime = self._windowProcessor.processMessage(message=message)
            if data is not None:
                for process, processArgs in self.processesDict.items():
                    pydoc.locate(process)(processor=self, data=data, **processArgs)


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
            self._df = self._df.reset_index().drop_duplicates().set_index('index')
            self._resampled_df = self._df.resample('%ss' % self.slide)
        timeList = list(self._resampled_df.groups.keys())
        data = None
        if len(timeList) > self._n:
            try:
                if self._lastTime != timeList[0]:
                    self._lastTime = timeList[0]
                    dataList = []
                    for i in range(self._n):
                        dataList.append(self._resampled_df.get_group(timeList[i]))
                    data = pandas.concat(dataList)
                    self._df = self._df[timeList[1]:]
            except Exception as exception:
                print(f'Exception {exception} handled')
                self._df = pandas.DataFrame()
                self._lastTime = None
        return data, timeList[0]

    def processMessageWithoutWindow(self, message):
        return toPandasDeserializer(message.value)