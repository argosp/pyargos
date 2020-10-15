import pydoc
import pandas
from . import toPandasDeserializer
from hera import datalayer
# from hera.datalayer import createDBConnection, getMongoConfigFromJson
# from hera.datalayer import Measurements_Collection
from kafka import KafkaConsumer, KafkaProducer
from argos import tbHome
import json
import paho.mqtt.client as mqtt
import logging
import time
from multiprocessing import Pool
import getpass
import os


class ConsumersHandler(object):

    _slideWindow = None
    _saveProperties = None

    @property
    def config(self):
        return self._config

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
    def expConf(self):
        return self._expConf

    @property
    def runFile(self):
        return self._runFile

    def __init__(self, projectName, kafkaHost, expConf, config, runFile):
        """
        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param expConf: The experiment configuration json file path
        :param config: Configuration json file for the consumers
        :param runFile: Path to the script file to run
        """

        self._projectName = projectName
        self._kafkaHost = kafkaHost
        self._expConf = expConf
        self._config = config
        self._runFile = runFile

        with open(self.config, 'r') as configFile:
            self._consumersConf = json.load(configFile)

        poolNum = 0
        for topic, topicDict in self.consumersConf.items():
            for window, processesDict in topicDict['processesConfig'].items():
                    poolNum += len(processesDict)

        self._poolNum = poolNum

    def run(self):
        with Pool(self._poolNum) as p:
            startProcessesInputs = []
            for topic, topicConfig in self.consumersConf.items():
                slideWindow = str(topicConfig.get('slideWindow'))
                for window in topicConfig['processesConfig']:
                    startProcessesInputs.append((topic, window, slideWindow))
            print('---- ready ----')
            p.starmap(self._startProcesses, startProcessesInputs)

    def _startProcesses(self, topic, window, slideWindow):
        os.system(f'python {self.runFile} --config {self.config} --kafkaHost {self.kafkaHost} --projectName {self.projectName} --expConf {self.expConf} --topic {topic} --window {window} --slideWindow {slideWindow}')


class AbstractProcessor(object):
    _projectName = None
    _kafkaHost = None
    _topic = None
    _processesDict = None

    _kafkaProducer = None
    _kafkaConsumer = None

    _Measurements = None

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
    def topic(self):
        return self._topic

    @property
    def processesDict(self):
        return self._processesDict

    @property
    def station(self):
        return self.topic.split('-')[0]

    @property
    def instrument(self):
        return self.topic.split('-')[1]

    @property
    def height(self):
        return int(self.topic.split('-')[2])

    @property
    def baseName(self):
        return f'{self.station}-{self.instrument}-{self.height}'

    # @property
    # def Measurements(self):
    #     return self._Measurements

    def __init__(self, projectName, kafkaHost, topic, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param expConf: The experiment configuration json file path
        :param topic: The topic to process
        :param processesDict: The configuration dictionary of the processes to run
        """
        self._projectName = projectName
        self._kafkaHost = kafkaHost
        self._topic = topic
        self._processesDict = processesDict

        self._kafkaProducer = KafkaProducer(bootstrap_servers=kafkaHost)
        self._kafkaConsumer = KafkaConsumer(topic,
                                            bootstrap_servers=kafkaHost,
                                            auto_offset_reset='latest',
                                            enable_auto_commit=True
                                            # group_id=group_id
                                            )

        # user = getpass.getuser()
        # alias = f'{self.topic}'
        # createDBConnection(user=user,
        #                    mongoConfig=getMongoConfigFromJson(user=user),
        #                    alias=alias
        #                    )
        #
        # self._Measurements =  Measurements_Collection(user=user, alias=alias)


class WindowProcessor(AbstractProcessor):
    _window = None

    _client = None
    _windowTime = None

    @property
    def tbh(self):
        return tbHome(self._tbCredentialMap["connection"])

    @property
    def tbHost(self):
        return self._tbCredentialMap["connection"]["server"]["ip"]

    @property
    def window(self):
        return self._window

    @property
    def client(self):
        return self._client

    @property
    def windowTime(self):
        return self._windowTime

    def __init__(self, projectName, kafkaHost, expConf, topic, window, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param expConf: The path to the experiment configuration file
        :param topic: The topic to process
        :param window: The window size, in seconds, to process
        :param processesDict: The configuration dictionary of the processes to run
        """

        super().__init__(projectName, kafkaHost, topic, processesDict)

        with open(expConf, 'r') as jsonFile:
            self._tbCredentialMap = json.load(jsonFile)

        self._window = window

        self._initiateClient()

        self._windowTime = None

    def on_disconnect(self, client, userdata, rc=0):
        logging.debug("DisConnected result code " + str(rc))
        client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
        else:
            print("Connection failed")

    def _initiateClient(self):
        if self.window=='None':
            devices = self.tbh.deviceHome.getAllEntitiesName()
            if self.topic in devices:
                #print('Connecting to %s' % deviceName)
                client = mqtt.Client("Me_%s" % self.topic)
                client.on_connect = self.on_connect

                accessToken = self.tbh.deviceHome.createProxy(self.topic).getCredentials()
                client.username_pw_set(accessToken, password=None)
                client.on_disconnect = self.on_disconnect
                client.connect(host=self.tbHost, port=1883)
                self._client = client
                client.loop_start()
                time.sleep(0.01)

    def _getData(self, message):
        if self.window=='None':
            data = toPandasDeserializer(message=message.value)
        else:
            self._windowTime = pandas.Timestamp(message.value.decode('utf-8')) - pandas.Timedelta(f'{self.window}s')
            endTime = pandas.Timestamp(message.value.decode('utf-8')) - pandas.Timedelta('0.001ms')
            data = datalayer.Measurements.getDocuments(projectName=self.projectName,
                                                  station=self.station,
                                                  instrument=self.instrument,
                                                  height=self.height
                                                  )[0].getData()[self.windowTime:endTime].compute()
        return data

    def start(self):
        for message in self.kafkaConsumer:
            data = self._getData(message=message)
            for process, processArgs in self.processesDict.items():
                pydoc.locate(process)(processor=self, data=data, **processArgs)
            del(data)


class SlideProcessor(AbstractProcessor):
    _slideWindow = None
    _df = None
    _lastTime = None
    _resampled_df = None

    @property
    def slideWindow(self):
        return self._slideWindow

    def __init__(self, projectName, kafkaHost, topic, slideWindow, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param expConf: The path to the experiment configuration file
        :param topic: The topic to process
        :param slideWindow: The sliding window size, in seconds
        :param processesDict: The configuration dictionary of the processes to run
        """
        super().__init__(projectName, kafkaHost, topic, processesDict)

        self._slideWindow = slideWindow

        self._df = pandas.DataFrame()
        self._lastTime = None

    def processMessage(self, message):
        self._df = self._df.append(toPandasDeserializer(message.value), sort=True)
        if self._lastTime is None or (self._lastTime + pandas.Timedelta('%ss' % self.slideWindow) <= self._df.tail(1).index[0]):
            self._resampled_df = self._df.resample('%ss' % self.slideWindow)
        timeList = list(self._resampled_df.groups.keys())
        data = None
        if len(timeList) > 1:
            try:
                if self._lastTime != timeList[-2]:
                    self._lastTime = timeList[-2]
                    # start = timeList[0]
                    # end = timeList[1]
                    # mask = (self._df.index>=start)*(self._df.index<end)
                    # data = self._df[mask]
                    data = self._resampled_df.get_group(timeList[-2])
                    self._df = self._df[timeList[-1]:]
            except Exception as exception:
                print(f'Exception {exception} handled')
                self._df = pandas.DataFrame()
                self._lastTime = None
        newWindowTime = None if data is None else self._lastTime + pandas.Timedelta(f'{self.slideWindow}s')
        return data, newWindowTime

    def start(self):
        for message in self.kafkaConsumer:
            data, newWindowTime = self.processMessage(message)
            if data is not None:
                for saveFunction, saveArguments in self.processesDict.items():
                    pydoc.locate(saveFunction)(processor=self, data=data, **saveArguments)
                del(data)
                window_topic = f"{self.topic}-calc"
                newMessage = str(newWindowTime).encode('utf-8')
                self.kafkaProducer.send(window_topic, newMessage)
