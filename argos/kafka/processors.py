import pydoc
import pandas
from . import toPandasDeserializer
from hera import datalayer
import dask.dataframe
from kafka import KafkaConsumer, KafkaProducer
from argos import tbHome
import json
from multiprocessing import Process
import os
import time

METEOROLOGY = 'meteorological'

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
    def tbConf(self):
        return self._tbConf

    @property
    def defaultSaveFolder(self):
        return self._defaultSaveFolder


    def __init__(self, projectName, kafkaHost, tbConf, config, defaultSaveFolder):
        """
        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param tbConf: The thingsboard configuration dict
        :param config: Configuration json file/dict for the consumers
        """

        self._projectName = projectName
        self._kafkaHost = kafkaHost
        self._tbConf = tbConf
        self._config = config
        self._defaultSaveFolder = defaultSaveFolder

        if type(config) is str:
            with open(self.config, 'r') as configFile:
                config = json.load(configFile)
        self._consumersConf = config

    def run(self):
        pList = []
        for topic, topicConfig in self.consumersConf.items():
            slideWindow = str(topicConfig.get('slideWindow'))

            if slideWindow != 'None':
                docList = datalayer.Measurements.getDocuments(self.projectName, deviceName=topic)
                if docList:
                    resource = docList[0].resource
                else:
                    resource = os.path.join(self.defaultSaveFolder, topic)
                    desc = dict(deviceName=topic)
                    datalayer.Measurements.addDocument(projectName=self.projectName,
                                                       resource=resource,
                                                       dataFormat=datalayer.datatypes.PARQUET,
                                                       type=METEOROLOGY,
                                                       desc=desc
                                                       )

            for window in topicConfig['processesConfig']:
                processesDict = self.consumersConf[topic]['processesConfig'][window]
                if slideWindow != 'None':
                    sp = SlideProcessor(self.projectName, self.kafkaHost, topic, resource, slideWindow, processesDict)
                    pList.append(sp)
                else:
                    wp = WindowProcessor(self.projectName, self.kafkaHost, topic, resource, window, self.tbConf, processesDict)
                    pList.append(wp)

        print('---- starting processes ----')

        for p in pList:
            p = Process(target=self._startProcesses, args=(p, ))
            p.start()

        print('---- ready ----')

    def _startProcesses(self, processor):
        processor.start()


class AbstractProcessor(object):
    _projectName = None
    _kafkaHost = None
    _topic = None
    _processesDict = None

    _kafkaConsumer = None

    @property
    def projectName(self):
        return self._projectName

    @property
    def kafkaHost(self):
        return self._kafkaHost

    @property
    def kafkaConsumer(self):
        return self._kafkaConsumer

    @property
    def topic(self):
        return self._topic

    @property
    def resource(self):
        return self._resource

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

    def __init__(self, projectName, kafkaHost, topic, resource, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param tbConf: The thingsboard configuration dictionary
        :param topic: The topic to process
        :param resource: The path to the parquet
        :param processesDict: The configuration dictionary of the processes to run
        """
        self._projectName = projectName
        self._kafkaHost = kafkaHost
        self._topic = topic
        self._resource = resource
        self._processesDict = processesDict

        self._kafkaConsumer = KafkaConsumer(topic,
                                            bootstrap_servers=kafkaHost,
                                            auto_offset_reset='latest',
                                            enable_auto_commit=True
                                            )

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

    def __init__(self, projectName, kafkaHost, topic, resource, window, tbConf, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param tbConf: The thingsboard configuration dictionary
        :param topic: The topic to process
        :param resource: The path to the parquet
        :param window: The window size, in seconds, to process
        :param processesDict: The configuration dictionary of the processes to run
        """

        super().__init__(projectName, kafkaHost, topic, resource, processesDict)

        self._tbCredentialMap = tbConf

        self._window = window

        # self._initiateClient()

        self._windowTime = None

    def setClient(self, client):
        self._client = client

    def _getData(self, message):
        if self.window=='None':
            data = toPandasDeserializer(message=message.value)
        else:
            self._windowTime = pandas.Timestamp(message.value.decode('utf-8')) - pandas.Timedelta(f'{self.window}s')
            endTime = pandas.Timestamp(message.value.decode('utf-8')) - pandas.Timedelta('0.001ms')
            data = dask.dataframe.read_parquet(path=self.resource)[self.windowTime:endTime].compute()
        return data

    def start(self):
        for message in self.kafkaConsumer:
            data = self._getData(message=message)
            for process, processArgs in self.processesDict.items():
                pydoc.locate(process)(processor=self, data=data, **processArgs)
            # del(data)


class SlideProcessor(AbstractProcessor):
    _slideWindow = None
    _df = None
    _lastTime = None
    _resampled_df = None

    @property
    def slideWindow(self):
        return self._slideWindow

    def __init__(self, projectName, kafkaHost, topic, resource, slideWindow, processesDict):
        """

        :param projectName: The project name
        :param kafkaHost: The kafka host IP
        :param topic: The topic to process
        :param resource: The path to the parquet
        :param slideWindow: The sliding window size, in seconds
        :param processesDict: The configuration dictionary of the processes to run
        """
        super().__init__(projectName, kafkaHost, topic, resource, processesDict)

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
                    data = self._resampled_df.get_group(timeList[-2])
                    self._df = self._df[timeList[-1]:]
            except Exception as exception:
                print(f'Exception {exception} handled')
                self._df = pandas.DataFrame()
                self._lastTime = None
        newWindowTime = None if data is None else self._lastTime + pandas.Timedelta(f'{self.slideWindow}s')
        return data, newWindowTime

    def start(self):
        producer = KafkaProducer(bootstrap_servers=self.kafkaHost)
        for message in self.kafkaConsumer:
            data, newWindowTime = self.processMessage(message)
            if data is not None:
                for saveFunction, saveArguments in self.processesDict.items():
                    pydoc.locate(saveFunction)(processor=self, data=data, **saveArguments)
                # del(data)
                window_topic = f"{self.topic}-calc"
                newMessage = str(newWindowTime).encode('utf-8')
                producer.send(window_topic, newMessage)
                producer.flush()

