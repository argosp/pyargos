from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from .abstractDatalayer import abstractDatalayerFactory

import pandas
import json
import os
from typing import Union


class GQLDataLayerFactory(abstractDatalayerFactory):
    """
        The configuration

        also include:

        "graphql": {
            "url": "...",
            "token": "..."
        }


    """
    _client = None
    _experiment = None

    @property
    def experiment(self):
        return self._experiment

    @property
    def argosWebConfiguration(self):
        return self._configuration['graphql']

    def __init__(self, experimentConfiguration: Union[str, dict]):
        """

        A data layer to get information from the graphql server

        :param url: The url of the graphql server
        :param authorization: the authorization token
        """

        super().__init__(experimentConfiguration)

        url = self.argosWebConfiguration['url']
        token = self.argosWebConfiguration['token']

        headers = None if token=='' else dict(authorization=token)
        transport = AIOHTTPTransport(url=url, headers=headers)
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

        experimentDict = self.listExperiments().query(f"name=='{self.experimentName}'").reset_index().iloc[0].to_dict()
        self._experiment = Experiment(desc=experimentDict,client=self._client)


    def getExperiment(self):
        return self._experiment

    def listExperiments(self):
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
        return pandas.DataFrame(result).set_index('id') if result else pandas.DataFrame()

    #
    # def getThingsboardTrialLoadConf(self, experimentName: str, trialSetName: str, trialName: str, trialType: str = 'deploy'):
    #     """
    #     Gets the thingsboard trial loading configuration
    #     Its usage is for the load of the relevant attributes of the devices in thingsboard.
    #
    #     :param experimentName: The experiment name
    #     :param trialSetName: The trial set name
    #     :param trialName: The trial name
    #     :param trialType: 'design'/'deploy'
    #     :return: dict
    #     """
    #     assert(trialType in ['design', 'deploy'])
    #     experiment = self.getExperimentByName(experimentName=experimentName)
    #     trialSet = experiment.getTrialSetByName(trialSetName=trialSetName)
    #     trial = trialSet.getTrialByName(trialName=trialName)
    #     if trialType == 'deploy':
    #         devices = trial.deployedEntities
    #     else:
    #         devices = trial.entities
    #     devicesList = []
    #     for deviceKey in devices.index:
    #         deviceDict = {}
    #         deviceDict.update(devices[['deviceName', 'deviceTypeName']].loc[deviceKey].to_dict())
    #         deviceDict['attributes'] = devices.drop(columns=['deviceName', 'deviceTypeName', 'deviceTypeKey']
    #                                                 ).loc[deviceKey].dropna().to_dict()
    #         devicesList.append(deviceDict)
    #     return devicesList
    #
    # def getKafkaConsumersConf(self, experimentName: str, configFile: Union[str, dict]):
    #     """
    #     Gets the kafka consumers configuration.
    #     Its usage is for the run of the kafka consumers (processes).
    #
    #     :param experimentName: The experiment name
    #     :param configFile: The config json/dict for this function.
    #     :return:
    #     """
    #     consumersConf = {}
    #
    #     if type(configFile) is str:
    #         with open(configFile, 'r') as myFile:
    #             configFile = json.load(myFile)
    #
    #     devicesList = self.getExperimentDevices(experimentName=experimentName)
    #     for deviceDict in devicesList:
    #         deviceName = deviceDict['deviceName']
    #         deviceType = deviceDict['deviceTypeName']
    #         deviceTypeConfig = configFile[deviceType]
    #         slide = deviceTypeConfig['slide']
    #         toParquet = deviceTypeConfig['toParquet']
    #         consumersConf[deviceName] = dict(slideWindow=slide, processesConfig={"None":{toParquet[0]: toParquet[1]}})
    #         processes = deviceTypeConfig['processes']
    #         calcDeviceName = f'{deviceName}-calc'
    #         consumersConf[calcDeviceName] = dict(processesConfig=processes)
    #         for window in processes:
    #             windowDeviceName = f'{deviceName}-{window}-{slide}'
    #             consumersConf[windowDeviceName] = dict(processesConfig={"None": {"argos.kafka.processes.to_thingsboard": {}}})
    #     return consumersConf
    #
    # def getFinalizeConf(self, experimentName: str):
    #     """
    #     Gets the finalize configuration.
    #     Its usage is for the update of the devices attributes in the
    #
    #     :param experimentName:
    #     :return:
    #     """
    #     experiment = self.getExperimentByName(experimentName=experimentName)
    #     devicesDescDict = {}
    #     for trialSetName in experiment.trialSets['name']:
    #         trialSet = experiment.getTrialSetByName(trialSetName=trialSetName)
    #         for trialName in trialSet.trials['name']:
    #             deployed_df = self.getThingsboardTrialLoadConf(experimentName=experimentName,
    #                                                            trialSetName=trialSetName,
    #                                                            trialName=trialName
    #                                                            )
    #             for deviceDict in deployed_df:
    #                 deviceName = deviceDict['deviceName']
    #                 deviceType = deviceDict['deviceTypeName']
    #                 attributes = deviceDict['attributes']
    #                 currentDeviceDesc = devicesDescDict.setdefault(deviceName, {'deviceName': deviceName,
    #                                                                             'deviceType': deviceType
    #                                                                             }
    #                                                                )
    #                 currentDeviceDesc[f'{trialName}_attributes'] = attributes
    #     return devicesDescDict


class Experiment:
    _desc = None
    _trialSets = None
    _trialSetsDict = None

    _deviceTypesDict = None
    _client = None


    @property
    def client(self):
        return self._client

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

    def trialSet(self,item :str = None ):
        if item is None:
            return self._trialSetsDict.keys()
        else:
            return self._trialSetsDict[item]

    def deviceType(self,item:str = None):
        if item is None:
            return self._deviceTypesDict.keys()
        else:
            return self._deviceTypesDict[item]


    def __init__(self, desc: dict, client: Client):
        """
        Experiment object contains information on a specific experiment

        :param desc: A dictionary with information on the experiment
        :param client: GraphQL client
        """

        self._trialSetsDict = dict()
        self._deviceTypesDict = dict()

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

        for trialset in result:
            self._trialSetsDict[trialset['name']] = TrialSet(experiment=self, metadata=trialset)

    def _initDeviceTypes(self):
        query = '''
        {
            deviceTypes(experimentId: "%s"){
                key
                id
                name
                numberOfDevices
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

        for deviceType in result:
            self._deviceTypesDict[deviceType['name']] = DeviceType(experiment=self,metadata = deviceType)

    def toJSON(self,allData=True):
        """
            Archive the data of the experiment.

            The archive of the experiment is comprised of the following files:

            Files:
                'Devices' - A list of all the devices.
                            [  ...
                                {
                                "deviceName": ....,
                                "deviceTypeName": ....
                                },

                            ]

                TBD.

                TrialSets - A list of all the trialsets.

                            The Json of the pandas:
                            key  | id | numberOfTrials


                trials/


        :param allData: bool
                If true, archive all the trial sets and the trials.

        :return: dict
                The dict
        """
        pass

    def getExperimentDevices(self):
        """
            Returns the list of all the devices

        :return: dict
            Return a list of the devices.
        """

        retList = []

        for devicetypeName, deviceTypeObj in self._deviceTypesDict.items():
            for deviceName in deviceTypeObj.devices():
                retList.append(dict(deviceName=deviceName,deviceTypeName=devicetypeName))

        return retList



class TrialSet:
    _experiment = None
    _metadata = None

    _trialsDict = None

    @property
    def client(self):
        return self.experiment.client

    @property
    def experiment(self):
        return self._experiment

    @property
    def key(self):
        return self._metadata['key']

    @property
    def id(self):
        return self._metadata['id']

    @property
    def name(self):
        return self._metadata['name']

    @property
    def description(self):
        return self._metadata['description']

    @property
    def numberOfTrials(self):
        return self._metadata['numberOfTrials']

    @property
    def properties(self):
        if 'properties' in self._metadata:
            ret = pandas.DataFrame(self._metadata['properties']).set_index('key')
        else:
            ret = pandas.DataFrame()

        return ret

    @property
    def trials(self):
        return self._trialsDict.keys()

    def __getitem__(self, item):
        return self._trialsDict[item]

    def __init__(self, experiment: Experiment,metadata : dict):
        """
        Trial set object contains information on a specific trial set

        :param experimentId: The experiment id
        :param desc: A dictionary with information on the trial set
        :param client: GraphQL client
        """
        self._experiment = experiment
        self._metadata = metadata

        self._trialsDict = dict()

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

        result = self.client.execute(gql(query))['trials']

        for trial in result:
            self._trialsDict[trial['name']] = Trial(trialSet=self,metadata=trial)


class Trial:

    _trialSet = None
    _metadata = None

    @property
    def experiment(self):
        return self._trialSet.experiment

    @property
    def client(self):
        return self._trialSet.experiment.client


    @property
    def key(self):
        return self._metadata['key']

    @property
    def id(self):
        return self._metadata['id']

    @property
    def name(self):
        return self._metadata['name']

    @property
    def trialSetKey(self):
        return self._metadata['trialSetKey']

    @property
    def created(self):
        return self._metadata['created']

    @property
    def status(self):
        return self._metadata['status']

    @property
    def cloneFrom(self):
        return self._metadata['cloneFrom']

    @property
    def numberOfDevices(self):
        return self._metadata['numberOfDevices']

    @property
    def state(self):
        return self._metadata['state']

    def properties(self,name : str = None):
        if name is None:
            return self._properties
        else:
            return self._properties[name]


    @property
    def designEntities(self):
        entities = pandas.DataFrame(self._metadata['entities']).set_index('key')
        dfList = []
        for deviceKey in entities.index:
            deviceType = self._experiment.getDeviceType(deviceTypeKey=entities.loc[deviceKey]['typeKey'])
            properties = pandas.DataFrame(self._metadata['entities']).set_index('key').loc[deviceKey]['properties']
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
        if not self._metadata['deployedEntities']:
            return pandas.DataFrame()
        else:
            deployedEntities = pandas.DataFrame(self._metadata['deployedEntities']).set_index('key')
            dfList = []
            for deviceKey in deployedEntities.index:
                deviceType = self._experiment.getDeviceType(deviceTypeKey=deployedEntities.loc[deviceKey]['typeKey'])
                properties = pandas.DataFrame(self._metadata['deployedEntities']).set_index('key').loc[deviceKey]['properties']
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

    def __getitem__(self, item):
        return self._properties.loc[item].val

    def __init__(self, trialSet: TrialSet, metadata : dict):
        """
        Trial object contains information on a specific trial

        :param experiment: The experiment object
        :param trialSet: The trial set object
        :param desc: A dictionary with information on the trial
        :param client: GraphQL client
        """
        self._trialSet = trialSet
        self._metadata = metadata
        propertiesPandas = pandas.DataFrame(metadata['properties']).set_index('key')

        properties = propertiesPandas.merge(trialSet.properties, left_index=True, right_index=True)[['val', 'type', 'label', 'description']]\
                                     .set_index("label")

        self._properties = dict([(key, data['val']) for key, data in properties.T.to_dict().items()])


class DeviceType:
    _experiment = None
    _metadata = None

    _devicesDict = None

    @property
    def experiment(self):
        return self._experiment

    @property
    def client(self):
        return self.experiment.client

    @property
    def key(self):
        return self._metadata['key']

    @property
    def id(self):
        return self._metadata['id']

    @property
    def name(self):
        return self._metadata['name']

    @property
    def numberOfDevices(self):
        return self._metadata['numberOfDevices']

    @property
    def state(self):
        return self._metadata['state']

    @property
    def properties(self):
        if 'properties' in self._metadata:
            ret = pandas.DataFrame(self._metadata['properties']).set_index('key')
        else:
            ret = pandas.DataFrame()

        return ret


    def devices(self,name:str = None):
        if name is None:
            return self._devicesDict.keys()
        else:
            return self._devicesDict[name]


    def __getitem__(self, item):
        return self._devicesDict[item]

    def __init__(self, experiment: Experiment, metadata: dict):
        """
        DeviceType object contains information on a specific device type

        :param experiment: The experiment object
        :param metadata: dict
                The metadata of the device type (the properties and ect).
        """
        self._experiment = experiment
        self._metadata = metadata
        self._devicesDict = dict()
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
        ''' % (self.experiment.id, self.key)
        result = self.client.execute(gql(query))['devices']

        for device in result:
            self._devicesDict[device['name']] = Device(deviceType=self,metadata=device)



class Device:

    _deviceType = None
    _metadata = None

    @property
    def deviceType(self):
        return self._deviceType

    @property
    def experiment(self):
        return self.deviceType.experiment

    @property
    def client(self):
        return self.experiment.client

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
    

    def properties(self,item : str = None):
        if item is None:
            return self._properties
        else:
            return self._properties[item]

    def toJSON(self):
        ret = dict(self._properties)
        ret.update(self._metadata)
        del ret['properties']

        return ret


    def __init__(self, deviceType: DeviceType, metadata:dict):
        """

        :param deviceType: DeviceType
                The device type

        :param metadata : dict
                The metadata of the
        """
        self._deviceType = deviceType
        self._metadata = metadata
        propertiesPandas = pandas.DataFrame(metadata['properties']).set_index('key')

        properties = propertiesPandas.merge(deviceType.properties, left_index=True, right_index=True)[['val', 'type', 'label', 'description']]\
                                     .set_index("label")

        self._properties = dict([(key, data['val']) for key, data in properties.T.to_dict().items()])