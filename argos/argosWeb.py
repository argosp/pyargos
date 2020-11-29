from gql import gql, Client, AIOHTTPTransport
import pandas
import json
import os
from typing import Union


class GQLDataLayer:
    _client = None
    _experiments = None
    _experimentsDict = dict()

    @property
    def experiments(self):
        return self._experiments

    def __init__(self, url: str, token: str = ''):
        """
        A data layer to get information from the graphql server

        :param url: The url of the graphql server
        :param authorization: the authorization token
        """

        headers = None if token=='' else dict(authorization=token)
        transport = AIOHTTPTransport(url=url, headers=headers)
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

        self._initExperiments()

    def _initExperiments(self):
        """

        :return:
        """
        query = '''
        {
            experiments{
                id
                name
                description
                status
            }
        }
        '''
        result = self._client.execute(gql(query))['experiments']
        self._experiments = pandas.DataFrame(result).set_index('id') if result else pandas.DataFrame()
        for id in self._experiments.index:
            expDesc = self._experiments.loc[id].to_dict()
            expDesc['id'] = id
            self._experimentsDict[id] = dict(desc=expDesc, client=self._client)

    def getExperiment(self, experimentId: str):
        """
        Gets an Experiment object of a specific experiment by id

        :param experimentId: The experiment id
        :return: Experiment object
        """
        if type(self._experimentsDict[experimentId]) is dict:
            self._experimentsDict[experimentId] = Experiment(**self._experimentsDict[experimentId])
        return self._experimentsDict[experimentId]

    def getExperimentByName(self, experimentName: str):
        """
        Gets an Experiment object of a specific experiment by name

        :param experimentName: The experiment name
        :return: Experiment object
        """
        experimentId = self.experiments.query(f"name=='{experimentName}'").index[0]
        experiment = self.getExperiment(experimentId=experimentId)
        return experiment

    def getThingsboardSetupConf(self, experimentName: str):
        """
        Gets the thingsboard setup configuration.
        Its usage is for the setup of the devices in thingsboard.

        :param experimentName: The experiment name
        :return: dict
        """
        experiment = self.getExperimentByName(experimentName=experimentName)
        devices = experiment.devices[['deviceTypeName', 'deviceName']]
        return [devices.loc[key].to_dict() for key in devices.index]

    def getThingsboardTrialLoadConf(self, experimentName: str, trialSetName: str, trialName: str, trialType: str = 'deploy'):
        """
        Gets the thingsboard trial loading configuration
        Its usage is for the load of the relevant attributes of the devices in thingsboard.

        :param experimentName: The experiment name
        :param trialSetName: The trial set name
        :param trialName: The trial name
        :param trialType: 'design'/'deploy'
        :return: dict
        """
        assert(trialType in ['design', 'deploy'])
        experiment = self.getExperimentByName(experimentName=experimentName)
        trialSet = experiment.getTrialSetByName(trialSetName=trialSetName)
        trial = trialSet.getTrialByName(trialName=trialName)
        if trialType == 'deploy':
            devices = trial.deployedEntities
        else:
            devices = trial.entities
        devicesList = []
        for deviceKey in devices.index:
            deviceDict = {}
            deviceDict.update(devices[['deviceName', 'deviceTypeName']].loc[deviceKey].to_dict())
            deviceDict['attributes'] = devices.drop(columns=['deviceName', 'deviceTypeName', 'deviceTypeKey']
                                                    ).loc[deviceKey].dropna().to_dict()
            devicesList.append(deviceDict)
        return devicesList

    def getKafkaConsumersConf(self, experimentName: str, configFile: Union[str, dict]):
        """
        Gets the kafka consumers configuration.
        Its usage is for the run of the kafka consumers (processes).

        :param experimentName: The experiment name
        :param configFile: The config json/dict for this function.
        :return:
        """
        consumersConf = {}

        if type(configFile) is str:
            with open(configFile, 'r') as myFile:
                configFile = json.load(myFile)

        devicesList = self.getThingsboardSetupConf(experimentName=experimentName)
        for deviceDict in devicesList:
            deviceName = deviceDict['deviceName']
            deviceType = deviceDict['deviceTypeName']
            deviceTypeConfig = configFile[deviceType]
            slide = deviceTypeConfig['slide']
            toParquet = deviceTypeConfig['toParquet']
            consumersConf[deviceName] = dict(slideWindow=slide, processesConfig={"None":{toParquet[0]: toParquet[1]}})
            processes = deviceTypeConfig['processes']
            calcDeviceName = f'{deviceName}-calc'
            consumersConf[calcDeviceName] = dict(processesConfig=processes)
            for window in processes:
                windowDeviceName = f'{deviceName}-{window}-{slide}'
                consumersConf[windowDeviceName] = dict(processesConfig={"None": {"argos.kafka.processes.to_thingsboard": {}}})
        return consumersConf

    def getFinalizeConf(self, experimentName: str):
        """
        Gets the finalize configuration.
        Its usage is for the update of the devices attributes in the

        :param experimentName:
        :return:
        """
        experiment = self.getExperimentByName(experimentName=experimentName)
        devicesDescDict = {}
        for trialSetName in experiment.trialSets['name']:
            trialSet = experiment.getTrialSetByName(trialSetName=trialSetName)
            for trialName in trialSet.trials['name']:
                deployed_df = self.getThingsboardTrialLoadConf(experimentName=experimentName,
                                                               trialSetName=trialSetName,
                                                               trialName=trialName
                                                               )
                for deviceDict in deployed_df:
                    deviceName = deviceDict['deviceName']
                    deviceType = deviceDict['deviceTypeName']
                    attributes = deviceDict['attributes']
                    currentDeviceDesc = devicesDescDict.setdefault(deviceName, {'deviceName': deviceName,
                                                                                'deviceType': deviceType
                                                                                }
                                                                   )
                    currentDeviceDesc[f'{trialName}_attributes'] = attributes
        return devicesDescDict





class Experiment:
    _desc = None
    _trialSets = None
    _trialSetsDict = dict()
    _deviceTypes = None
    _deviceTypesDict = dict()

    @property
    def id(self):
        return self._desc['id']

    @property
    def name(self):
        return self._desc['name']

    @property
    def description(self):
        return self._desc['description']

    @property
    def status(self):
        return self._desc['status']

    @property
    def trialSets(self):
        return self._trialSets

    @property
    def deviceTypes(self):
        return self._deviceTypes

    @property
    def devices(self):
        devicesDfList = []
        for deviceTypeKey in self._deviceTypesDict:
            deviceType = self.getDeviceType(deviceTypeKey=deviceTypeKey)
            tmp_df = deviceType.devices
            tmp_df = tmp_df.rename(columns={'name':'deviceName'})
            tmp_df['deviceTypeName'] = deviceType.name
            tmp_df = tmp_df[['deviceName', 'deviceTypeName', 'deviceTypeKey']]
            devicesDfList.append(tmp_df)
        devices = pandas.concat(devicesDfList)
        dfList = []
        for deviceKey in devices.index:
            deviceType = self.getDeviceType(deviceTypeKey=devices.loc[deviceKey]['deviceTypeKey'])
            deviceProperties = deviceType.getDevice(deviceKey=deviceKey).properties
            deviceProperties = pandas.DataFrame(data=[deviceProperties['val'].values],
                                                columns=deviceProperties['label'].values,
                                                index=[deviceKey]
                                                )
            dfList.append(deviceProperties.dropna(axis=1,
                                                  how='all'
                                                  )
                          )
        new_df = pandas.concat(dfList, sort=False)
        return new_df.join(devices)

    def __init__(self, desc: dict, client: Client):
        """
        Experiment object contains information on a specific experiment

        :param desc: A dictionary with information on the experiment
        :param client: GraphQL client
        """
        self._desc = desc
        self._client = client

        self._initTrialSets()
        self._initDeviceTypes()

    def _initTrialSets(self):
        query = '''
        {
            trialSets(experimentId: "%s"){
                key
                id
                name
                description
                numberOfTrials
                properties{
                    key
                    type
                    id
                    label
                    description
                    trialField
                    value
                }
                state
            }
        }
        ''' % self.id
        result = self._client.execute(gql(query))['trialSets']
        self._trialSets = pandas.DataFrame(result).set_index('key') if result else pandas.DataFrame()
        for key in self._trialSets.index:
            trialSetDesc = self._trialSets.loc[key].to_dict()
            trialSetDesc['key'] = key
            self._trialSetsDict[key] = dict(experiment=self, desc=trialSetDesc, client=self._client)

    def _initDeviceTypes(self):
        query = '''
        {
            deviceTypes(experimentId: "%s"){
                key
                id
                name
                numberOfDevices
                state
                properties{
                    key
                    type
                    id
                    label
                    description
                    value
                }
            }
        }
        ''' % self.id
        result = self._client.execute(gql(query))['deviceTypes']
        self._deviceTypes = pandas.DataFrame(result).set_index('key') if result else pandas.DataFrame()
        for key in self._deviceTypes.index:
            deviceTypeDesc = self._deviceTypes.loc[key].to_dict()
            deviceTypeDesc['key'] = key
            self._deviceTypesDict[key] = dict(experiment=self, desc=deviceTypeDesc, client=self._client)

    def getDeviceType(self, deviceTypeKey: str):
        """
        Gets a DeviceType object of a specific device

        :param deviceTypeKey: The device type key
        :return: DeviceType object
        """
        if type(self._deviceTypesDict[deviceTypeKey]) is dict:
            self._deviceTypesDict[deviceTypeKey] = DeviceType(**self._deviceTypesDict[deviceTypeKey])
        return self._deviceTypesDict.get(deviceTypeKey)

    def getTrialSet(self, trialSetKey: str):
        """
        Gets a TrialSet object of a specific trial set

        :param trialSetKey: The trial set key
        :return: TrialSet object
        """
        if type(self._trialSetsDict[trialSetKey]) is dict:
            self._trialSetsDict[trialSetKey] = TrialSet(**self._trialSetsDict[trialSetKey])
        return self._trialSetsDict.get(trialSetKey)

    def getTrialSetByName(self, trialSetName: str):
        """
        Gets a TrialSet object of a specific trial set by trial set name

        :param trialSetName: The trial set name
        :return: TrialSet object
        """
        trialSetKey = self.trialSets.query(f'name=="{trialSetName}"').index[0]
        trialSet = self.getTrialSet(trialSetKey=trialSetKey)
        return trialSet


class TrialSet:
    _experiment = None
    _desc = None
    _client = None
    _trials = None
    _trialsDict = dict()

    @property
    def key(self):
        return self._desc['key']

    @property
    def id(self):
        return self._desc['id']

    @property
    def name(self):
        return self._desc['name']

    @property
    def description(self):
        return self._desc['description']

    @property
    def numberOfTrials(self):
        return self._desc['numberOfTrials']

    @property
    def properties(self):
        return pandas.DataFrame(self._desc['properties']).set_index('key') if self._desc['properties'] else pandas.DataFrame()

    @property
    def state(self):
        return self._desc['state']

    @property
    def trials(self):
        return self._trials

    def __init__(self, experiment: Experiment, desc: dict, client: Client):
        """
        Trial set object contains information on a specific trial set

        :param experimentId: The experiment id
        :param desc: A dictionary with information on the trial set
        :param client: GraphQL client
        """
        self._experiment = experiment
        self._desc = desc
        self._client = client

        self._initTrials()

    def _initTrials(self):
        query = '''
        {
            trials(experimentId: "%s", trialSetKey: "%s"){
                key
                id
                name
                created
                status
                cloneFrom
                numberOfDevices
                state
                properties{
                    val
                    key
                }
                entities{
                    typeKey
                    properties{
                        val
                        key
                    }
                    key
                    type
                }
                deployedEntities{
                    typeKey
                    properties{
                        val
                        key
                    }
                    key
                    type
                }
            }
        }
        ''' % (self._experiment.id, self.key)
        result = self._client.execute(gql(query))['trials']
        self._trials = pandas.DataFrame(result).set_index('key') if result else pandas.DataFrame()
        for key in self._trials.index:
            trialDesc = self._trials.loc[key].to_dict()
            trialDesc['key'] = key
            self._trialsDict[key] = dict(experiment=self._experiment, trialSet=self, desc=trialDesc, client=self._client)

    def getTrial(self, trialKey: str):
        """
        Gets a Trial object of a specific trial

        :param trialKey: The trial key
        :return: Trial object
        """
        if type(self._trialsDict[trialKey]) is dict:
            self._trialsDict[trialKey] = Trial(**self._trialsDict[trialKey])
        return self._trialsDict.get(trialKey)

    def getTrialByName(self, trialName: str):
        """
        Gets a Trial object of a specific trial by trial name

        :param trialName: The trial name
        :return: Trial object
        """
        trialKey = self.trials.query(f"name=='{trialName}'").index[0]
        trial = self.getTrial(trialKey=trialKey)
        return trial


class Trial:
    _experiment = None
    _trialSet = None
    _desc = None
    _client = None

    @property
    def key(self):
        return self._desc['key']

    @property
    def id(self):
        return self._desc['id']

    @property
    def name(self):
        return self._desc['name']

    @property
    def trialSetKey(self):
        return self._desc['trialSetKey']

    @property
    def created(self):
        return self._desc['created']

    @property
    def status(self):
        return self._desc['status']

    @property
    def cloneFrom(self):
        return self._desc['cloneFrom']

    @property
    def numberOfDevices(self):
        return self._desc['numberOfDevices']

    @property
    def state(self):
        return self._desc['state']

    @property
    def properties(self):
        return pandas.DataFrame(self._desc['properties']).set_index('key') if self._desc['properties'] else pandas.DataFrame()

    @property
    def entities(self):
        entities = pandas.DataFrame(self._desc['entities']).set_index('key')
        dfList = []
        for deviceKey in entities.index:
            deviceType = self._experiment.getDeviceType(deviceTypeKey=entities.loc[deviceKey]['typeKey'])
            properties = pandas.DataFrame(self._desc['entities']).set_index('key').loc[deviceKey]['properties']
            data = []
            columns = []
            for property in properties:
                propertyKey = property['key']
                propertyLabel = deviceType.properties.loc[propertyKey]['label']
                propertyType = deviceType.properties.loc[propertyKey]['type']
                if propertyType == 'location':
                    try:
                        locationDict = json.loads(property['val'])
                        locationName = locationDict['name']
                        latitude = locationDict['coordinates'][0]
                        longitude = locationDict['coordinates'][1]
                        data += [locationName, latitude, longitude]
                    except TypeError:
                        data += [None]*3
                    columns += ['locationName', 'latitude', 'longitude']
                else:
                    data.append(property['val'])
                    columns.append(propertyLabel)
            deviceProperties = deviceType.getDevice(deviceKey=deviceKey).properties
            deviceProperties = pandas.DataFrame(data=[deviceProperties['val'].values],
                                                columns=deviceProperties['label'].values,
                                                index=[deviceKey]
                                                )
            dfList.append(pandas.DataFrame(data=[data],
                                           columns=columns,
                                           index=[deviceKey]
                                           )
                          .join(deviceProperties[list(set(deviceProperties.columns)-set(columns))].dropna(axis=1,
                                                                                                          how='all'
                                                                                                          ),
                                how='left'
                                )
                          )
        new_df = pandas.concat(dfList, sort=False)
        experimentDevices = self._experiment.devices
        return new_df.join(experimentDevices[list(set(experimentDevices.columns)-set(new_df.columns))],
                           how='left').dropna(axis=1, how='all')

    @property
    def deployedEntities(self):
        if not self._desc['deployedEntities']:
            return pandas.DataFrame()
        else:
            deployedEntities = pandas.DataFrame(self._desc['deployedEntities']).set_index('key')
            dfList = []
            for deviceKey in deployedEntities.index:
                deviceType = self._experiment.getDeviceType(deviceTypeKey=deployedEntities.loc[deviceKey]['typeKey'])
                properties = pandas.DataFrame(self._desc['deployedEntities']).set_index('key').loc[deviceKey]['properties']
                data = []
                columns = []
                for property in properties:
                    propertyKey = property['key']
                    propertyLabel = deviceType.properties.loc[propertyKey]['label']
                    propertyType = deviceType.properties.loc[propertyKey]['type']
                    if propertyType == 'location':
                        try:
                            locationDict = json.loads(property['val'])
                            locationName = locationDict['name']
                            latitude = locationDict['coordinates'][0]
                            longitude = locationDict['coordinates'][1]
                            data += [locationName, latitude, longitude]
                        except TypeError:
                            data += [None] * 3
                        columns += ['locationName', 'latitude', 'longitude']
                    else:
                        data.append(property['val'])
                        columns.append(propertyLabel)
                deviceProperties = deviceType.getDevice(deviceKey=deviceKey).properties
                deviceProperties = pandas.DataFrame(data=[deviceProperties['val'].values],
                                                    columns=deviceProperties['label'].values,
                                                    index=[deviceKey]
                                                    )
                dfList.append(pandas.DataFrame(data=[data],
                                               columns=columns,
                                               index=[deviceKey]
                                               )
                              .join(deviceProperties[list(set(deviceProperties.columns) - set(columns))].dropna(axis=1,
                                                                                                                how='all'
                                                                                                                ),
                                    how='left'
                                    )
                              )
            new_df = pandas.concat(dfList, sort=False)
            experimentDevices = self._experiment.devices
            return new_df.join(experimentDevices[list(set(experimentDevices.columns) - set(new_df.columns))],
                               how='left').dropna(axis=1, how='all')

    def __init__(self, experiment: Experiment, trialSet: TrialSet, desc: dict, client: Client):
        """
        Trial object contains information on a specific trial

        :param experiment: The experiment object
        :param trialSet: The trial set object
        :param desc: A dictionary with information on the trial
        :param client: GraphQL client
        """
        self._experiment = experiment
        self._trialSet = trialSet
        self._desc = desc
        self._client = client


class DeviceType:
    _experiment = None
    _desc = None
    _client = None
    _devices = None
    _devicesDict = dict()

    @property
    def key(self):
        return self._desc['key']

    @property
    def id(self):
        return self._desc['id']

    @property
    def name(self):
        return self._desc['name']

    @property
    def numberOfDevices(self):
        return self._desc['numberOfDevices']

    @property
    def state(self):
        return self._desc['state']

    @property
    def properties(self):
        return pandas.DataFrame(self._desc['properties']).set_index('key') if self._desc['properties'] else pandas.DataFrame()

    @property
    def devices(self):
        return self._devices

    def __init__(self, experiment: Experiment, desc: dict, client: Client):
        """
        DeviceType object contains information on a specific device type

        :param experiment: The experiment object
        :param desc: A dictionary with information on the trial
        :param client: GraphQL client
        """
        self._experiment = experiment
        self._desc = desc
        self._client = client

        self._initDevices()

    def _initDevices(self):
        query = '''
        {
            devices(experimentId: "%s", deviceTypeKey: "%s"){
                key
                id
                name
                deviceTypeKey
                state
                properties{
                    val
                    key
                }
            }
        }
        ''' % (self._experiment.id, self.key)
        result = self._client.execute(gql(query))['devices']
        self._devices = pandas.DataFrame(result).set_index('key') if result else pandas.DataFrame()
        for key in self._devices.index:
            deviceDesc = self._devices.loc[key].to_dict()
            deviceDesc['key'] = key
            self._devicesDict[key] = dict(experiment=self._experiment, deviceType=self, desc=deviceDesc, client=self._client)

    def getDevice(self, deviceKey: str):
        """
        Gets a Device object of a specific device

        :param deviceKey: The device key
        :return:
        """
        if type(self._devicesDict[deviceKey]) is dict:
            self._devicesDict[deviceKey] = Device(**self._devicesDict[deviceKey])
        return self._devicesDict[deviceKey]


class Device:
    _experiment = None
    _deviceType = None
    _trial = None
    _desc = None
    _client = None
    
    @property
    def key(self):
        return self._desc['key']
    
    @property
    def id(self):
        return self._desc['id']
    
    @property
    def name(self):
        return self._desc['name']
    
    @property
    def deviceTypeKey(self):
        return self._desc['deviceTypeKey']
    
    @property
    def state(self):
        return self._desc['state']
    
    @property
    def properties(self):
        df = pandas.DataFrame(self._desc['properties']).set_index('key') if self._desc['properties'] else pandas.DataFrame()
        return df.join(self._deviceType.properties,
                       how='left'
                       )

    def __init__(self, experiment: str, deviceType: DeviceType, desc: dict, client: Client, trial: Trial = None):
        """

        :param experiment: The experiment object
        :param deviceType: The DeviceType object
        :param desc: A dictionary with information on the device
        :param client: GraphQL client
        :param trialKey: The trial object (optional)
        """
        self._experiment = experiment
        self._deviceType = deviceType
        self._trial = trial
        self._desc = desc
        self._client = client
