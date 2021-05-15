from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pandas
import json

class webExperimentHome:
    """
        Manages the experiment trials from the web.

        Getting the data from the WEB:

        - The list of experiments.
        - Get the experiment Object that manages a specific experiment.

    """
    _client = None

    @property
    def client(self):
        return self._client

    def __init__(self, url: str, token: str):
        """

        url: str
            The url of the server.
        token: str
            The token to access the server.
        """
        headers = None if token=='' else dict(authorization=token)
        transport = AIOHTTPTransport(url=url, headers=headers)
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

        # experimentDict = self.listExperiments().query(f"name=='{self.experimentName}'").reset_index().iloc[0].to_dict()
        # self._experiment = Experiment(desc=experimentDict,client=self._client)


    def getExperiment(self,experimentName):
        experimentDict = self.getExperimentDescriptor(experimentName)
        return Experiment(desc=experimentDict,client=self._client)

    def getExperimentsDescriptionsList(self):
        """
            Returns a list of the experiment description as JSON (dict)

            The structure of the dict:

            * id: The id of the experiment in the server.
            * project
                            id

            * name: The name of the experiment
            * description: The description of the project
            * begin:        The beginning of the experiment
            * end:          The end of the experiment.
            * numberOfTrials: The number of trial sets that are present in the
            * maps: descirption of the maps (images) of the project
                    {
                    imageUrl
                    imageName
                    lower
                    upper
                    left
                    right
                    width
                    height
                    embedded
                    }

        Returns
        -------
            The list of experiment descriptions.

        """
        query = '''
                {
                    experimentsWithData {
                        name
                        description
                        begin
                        end
                        numberOfTrials
                        project {
                            id
                        }                        
                        maps {
                            imageUrl
                            imageName
                            lower
                            upper
                            left
                            right
                            width
                            height
                            embedded
                        }
                    }
                }
        '''
        return self._client.execute(gql(query))['experimentsWithData']

    def getExperimentsDescriptionsTable(self):
        """
            Returns the table of the
        :return:
            Return the pandas
        """
        return pandas.json_normalize(self.getExperimentsDescriptionsList())


    def getExperimentDescriptor(self,experimentName):
        """
            Returns the JSON (dict) descriptor of the requested expeiment.


        Parameters
        ----------

        experimentName: str

        Returns
        -------
            the dict that describes the experiment

            id
            name
            description
            begin
            end
            numberOfTrials
            maps {
                imageUrl
                imageName
                lower
                upper
                left
                right
                width
                height
                embedded
            }

        """
        descs = self.getExperimentsDescriptionsList()

        return [x for x in descs if x['name']==experimentName][0]


    def listExperimentsNames(self):
        """
            Lists the names of all the experiments in the server.

        Returns
        -------
            A list of experiment names.
        """
        return [x['name'] for x in self.listExperimentsDescriptions()]

    def __getitem__(self, item):
        return self.getExperiment(experimentName=item)

    def keys(self):
        """
            Return the list of experiment names.
        """
        return self.listExperiments()['name']


class Experiment:
    """
        Interface to the WEB experiment object.

    """

    _desc = None            # experiment description holds its name, descrition and ect.

    _trialSetsDict = None   # A dictionary of the trial sets.
    _deviceTypesDict = None # A dictionary of the devices types.

    _client = None          # The client of the connection to the WEB.


    @property
    def client(self):
        return self._client

    @property
    def id(self):
        ## DO NOT USE the self._desc['id']. It is not useful here.
        return self._desc['project']['id']

    @property
    def name(self):
        return self._desc['name']

    @property
    def description(self):
        return self._desc['description']


    @property
    def trialSet(self):
        return self._trialSetsDict

    @property
    def deviceType(self):
        return self._deviceTypesDict


    def __init__(self, desc: dict, client: Client):
        """
        Experiment object contains information on a specific experiment

        Parameters
        -----------

        desc: dict

            A dictionary with information on the experiment

        client: dict
            GraphQL client
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
                name
                description
                numberOfTrials
                properties{
                    key
                    type
                    label
                    description
                    required
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
                name
                numberOfDevices
                properties{
                    key
                    type
                    label
                    description
                    required
                    trialField
                    value
                }
            }
        }
        ''' % self.id
        result = self._client.execute(gql(query))['deviceTypes']

        for deviceType in result:
            self._deviceTypesDict[deviceType['name']] = DeviceType(experiment=self,metadata = deviceType)


    def toJSON(self):
        """
            Create a single JSON with the data of the experiment.


        :return:
        """
        ret = dict()

        deviceTypeMap = dict()
        for deviceName,deviceType in self.deviceType.items():
            deviceTypeMap[deviceName] = deviceType.toJSON()

        trialMap = dict()
        for trialName,trialData in self.trialSet.items():
            trialMap[trialName] = trialData.toJSON()

        ret['deviceType'] = deviceTypeMap
        ret['trialSet'] = trialMap

        expr = dict()

        for field in ['maps','begin','end','description']:
            expr[field] = self._desc[field]

        ret['experiment'] = expr
        return ret


    def pack(self,toDirectory : str):
        """
            Archive all the data of the experiment.

            Download the pictures from the


        Parameters
        ----------

        toDirectory : str
            The directory to pack the experiment to.


        Returns
        -------

        None
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


class TrialSet(dict):
    """
        Interface to the web trial set object.

    """
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
    def keyID(self):
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
    def propertiesTable(self):
        if 'properties' in self._metadata:
            ret = pandas.DataFrame(self._metadata['properties']).set_index('key')
        else:
            ret = pandas.DataFrame()

        return ret

    @property
    def properties(self):
        ret = dict()
        for prop in self._metadata['properties']:
            ret[prop['label']] = prop

        return ret

    def toJSON(self):
        ret = dict()
        ret['name'] = self.name
        ret['properties'] = self.properties

        trialsJSON = {}
        for trialName,trialData in self.items():
            trialsJSON[trialName] = trialData.toJSON()

        ret['trials'] = trialsJSON


        return ret

    @property
    def trials(self):
        retList = []
        for trialName,trialData in self.items():
            trialProps = trialData.propertiesTable
            trialProps = trialProps.assign(trialName=trialName)
            retList.append(trialProps)
        return pandas.concat(retList,ignore_index=True)

    def __init__(self, experiment: Experiment,metadata : dict):
        """
        Trial set object contains information on a specific trial set

        :param experimentId: The experiment id
        :param desc: A dictionary with information on the trial set
        :param client: GraphQL client
        """
        self._experiment = experiment
        self._metadata = metadata

        self._initTrials()

    def _initTrials(self):
        query = '''
        {
            trials(experimentId: "%s", trialSetKey: "%s"){
                key
                name
                status
                created
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
        ''' % (self._experiment.id, self.keyID)

        result = self.client.execute(gql(query))['trials']

        for trial in result:
            self[trial['name']] = Trial(trialSet=self,metadata=trial)



    def dumps(self):
        return

class Trial:
    """
        Interface to the WEB trials.

    """

    _trialSet = None
    _metadata = None


    @property
    def experiment(self):
        return self._trialSet.experiment

    @property
    def client(self):
        return self._trialSet.experiment.client

    @property
    def experiment(self):
        return self._trialSet.experiment


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

    @property
    def properties(self):
            return self._properties


    @property
    def propertiesTable(self):
        return pandas.DataFrame(self.properties,index=[0])

    def __init__(self, trialSet: TrialSet, metadata : dict):
        """
        Trial object contains information on a specific trial

        Parameters
        ----------

        experiment: The experiment object
        trialSet: The trial set object
        desc: A dictionary with information on the trial
        client: GraphQL client
        """
        self._trialSet = trialSet
        self._metadata = metadata

        propertiesPandas = pandas.DataFrame(metadata['properties']).set_index('key')

        properties = propertiesPandas.merge(trialSet.propertiesTable, left_index=True, right_index=True)[['val', 'type', 'label', 'description']]\
                                     .set_index("label")

        self._properties = dict([(key, data['val']) for key, data in properties.T.to_dict().items()])


    def toJSON(self):
        val = self.properties
        val['name'] = self.name
        val['status'] = self.status
        val['state'] = self.status
        return val

    def __str__(self):
        return json.dumps(self.toJSON())

    def __repr__(self):
        return json.dumps(dict(name=self.name,status=self.status,state=self.state))

    @property
    def designEntities(self):
        entities = pandas.DataFrame(self._metadata['entities']).set_index('key')
        dfList = []
        for deviceKey in entities.index:
            deviceType = self.experiment.getDeviceType(deviceTypeKey=entities.loc[deviceKey]['typeKey'])
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
                deviceType = self.experiment.getDeviceType(deviceTypeKey=deployedEntities.loc[deviceKey]['typeKey'])
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


class DeviceType(dict):
    _experiment = None
    _metadata = None

    @property
    def experiment(self):
        return self._experiment

    @property
    def client(self):
        return self.experiment.client

    @property
    def keyID(self):
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
    def propertiesTable(self):
        if 'properties' in self._metadata:
            ret = pandas.DataFrame(self._metadata['properties']).set_index('key')
        else:
            ret = pandas.DataFrame()

        return ret

    @property
    def properties(self):
        ret = dict()
        for prop in self._metadata['properties']:
            ret[prop['label']] = prop

        return ret

    def toJSON(self):
        ret = dict()
        ret['name'] = self.name
        ret['properties'] = self.properties

        devicesJSON = {}
        for deviceName,deviceData in self.items():
            devicesJSON[deviceName] = deviceData.toJSON()

        ret['devices'] = devicesJSON


        return ret


    def __init__(self, experiment: Experiment, metadata: dict):
        """
        DeviceType object contains information on a specific device type

        :param experiment: The experiment object
        :param metadata: dict
                The metadata of the device type (the properties and ect).
        """
        self._experiment = experiment
        self._metadata = metadata
        self._initDevices()

    def _initDevices(self):
        query = '''
        {
            devices(experimentId: "%s", deviceTypeKey: "%s"){
                key
                name
                deviceTypeKey
                state
                properties{
                    val
                    key
                }
            }
        }
        ''' % (self.experiment.id, self.keyID)
        result = self.client.execute(gql(query))['devices']

        for device in result:
            self[device['name']] = Device(deviceType=self,metadata=device)

    @property
    def devices(self):
        retList = []
        for deviceName, deviceData in self.items():
            trialProps = deviceData.propertiesTable
            trialProps = trialProps.assign(deviceName=deviceName)
            retList.append(trialProps)
        return pandas.concat(retList, ignore_index=True)


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
        return self._metadata['key']
    
    @property
    def id(self):
        return self._metadata['id']
    
    @property
    def name(self):
        return self._metadata['name']

    @property
    def deviceTypeKey(self):
        return self._metadata['deviceTypeKey']


    @property
    def properties(self):
        return self._properties

    @property
    def propertiesTable(self):
        val = pandas.DataFrame(self.properties,index=[0])
        val = val.assign(deviceName=self.name)
        return val

    def toJSON(self):
        ret = dict(self.properties)
        ret.update(self._metadata)
        del ret['properties']

        return ret

    def __str__(self):
        return json.dumps(self.toJSON())

    def __repr__(self):
        props = self.properties
        props['name'] = self.name
        return json.dumps(props)

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

        properties = propertiesPandas.merge(deviceType.propertiesTable.query("trialField==False"), left_index=True, right_index=True)[['val', 'type', 'label', 'description']]\
                                     .set_index("label")

        self._properties = dict([(key, data['val']) for key, data in properties.T.to_dict().items()])






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
