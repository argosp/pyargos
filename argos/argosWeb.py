from gql import gql, Client, AIOHTTPTransport
import pandas


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
        result = self._execute(query)['experiments']
        self._experiments = pandas.DataFrame(result).set_index('id') if result else pandas.DataFrame()
        for id in self._experiments.index:
            expDesc = self._experiments.loc[id].to_dict()
            expDesc['id'] = id
            self._experimentsDict[id] = dict(desc=expDesc, client=self._client)

    def getExperiment(self, experimentId: str):
        """
        Gets an Experiment object of a specific experiment

        :param experimentId: The experiment id
        :return: Experiment object
        """
        if type(self._experimentsDict[experimentId]) is dict:
            self._experimentsDict[experimentId] = Experiment(**self._experimentsDict[experimentId])
        return self._experimentsDict[experimentId]

    def getDeviceTypes(self, expName: str):
        """
        Gets the device types information

        :param expName: The experiment name
        :return: pandas.DataFrame
        """
        expId = self._getExpId(expName=expName)
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
        ''' % expId
        result = self._execute(query)['deviceTypes']
        return pandas.DataFrame(result)

    def _getDeviceTypeKey(self, expName: str, deviceType: str):
        """
        Gets the key of a specific device type

        :param expName: The experiment name
        :param deviceType: The device type
        :return: str
        """
        try:
            return self.getDeviceTypes(expName=expName).query(f"name=='{deviceType}'")['key'].values[0]
        except IndexError:
            raise NameError(f'There is not device type called "{deviceType}"')

    def getDevicesByDeviceTypeAndTrial(self, expName: str, deviceType: str, trialName: str):
        """
        Gets the devices information of a specific device type in a specific trial

        :param expName: The experiment name
        :param deviceType: The device type
        :param trialName: The trial name
        :return: pandas.DataFrame
        """
        expId = self._getExpId(expName=expName)
        deviceTypeKey = self._getDeviceTypeKey(expName=expName, deviceType=deviceType)
        query = '''
        {
            devices (experimentId:"%s", deviceTypeKey:"%s", trialKey:){
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
        ''' % (expId, deviceTypeKey)
        result = self._execute(query)['devices']
        return pandas.DataFrame(result)

    def getTrialSets(self, expName: str):
        """
        Gets the trial sets information

        :param expName: The experiment name
        :return: pandas.DataFrame
        """
        expId = self._getExpId(expName=expName)
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
        ''' % expId
        result = self._execute(query)['trialSets']
        return pandas.DataFrame(result)

    def _getTrialSetKey(self, expName: str, trialSetName: str):
        """
        Gets the key of a specific trial set

        :param expName: The experiment name
        :param trialSetName: The trial set name
        :return: str
        """
        try:
            return self.getTrialSets(expName=expName).query(f"name=='{trialSetName}'")['key'].values[0]
        except IndexError:
            raise NameError(f'There is no trial set called {trialSetName}')

    def getTrialsByTrialSet(self, expName: str, trialSetName: str):
        """
        Gets the trials information of a specific trial set

        :param expName: The experiment name
        :param trialSetName: The trial set name
        :return: pandas.DataFrame
        """
        expId = self._getExpId(expName=expName)
        trialSetKey = self._getTrialSetKey(expName=expName, trialSetName=trialSetName)
        query = '''
        {
            trials(experimentId: "%s", trialSetKey: "%s"){
                key
                id
                name
                created
                state
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
        ''' % (expId, trialSetKey)
        result = self._execute(query)['trials']
        return pandas.DataFrame(result)

    def getDevices(self, expName: str):
        """
        Gets all devices and their types

        :param expName: The experiment name
        :return: pandas.DataFrame
        """
        devicesList = []
        for deviceType in self.getDeviceTypes(expName=expName)['name'].values:
            for deviceName in self.getDevicesByDeviceType(expName=expName, deviceType=deviceType)['name'].values:
                devicesList.append(dict(deviceType=deviceType, deviceName=deviceName))
        return pandas.DataFrame(devicesList)

    def getDeviceAttributesByTrial(self, expName: str, deviceType: str, deviceName: str, trialName: str):
        """
        Gets a device attributes in a specific trial

        :param expName: The experiment name
        :param deviceType: The device type
        :param deviceName: The device name
        :param trialName: The trial name
        :return: pandas.DataFrame
        """
        deviceProperties = pandas.DataFrame(self.getDevicesByDeviceType(expName=expName, deviceType=deviceType).query(f'name=="{deviceName}"')['properties'].values[0])
        deviceProperties['label'] = deviceProperties.apply(lambda x: self._getDeviceTypeAttributeByKey(expName=expName, deviceType=deviceType, key=x['key']), axis=1)
        return deviceProperties

    def _getDeviceTypeAttributeByKey(self, expName: str, deviceType: str, key: str):
        """
        Gets the attribute key of a specific device type

        :param expName:
        :param deviceType:
        :param key:
        :return:
        """
        attributes = pandas.DataFrame(self.getDeviceTypes(expName=expName).query(f'name=="{deviceType}"')['properties'].values[0])
        return attributes.query(f'key=="{key}"')['label'].values[0]

    def getExperimentData(self, expName: str):
        """
        Gets an experiment information

        :param expName: The experiment name
        :return: pandas.DataFrame
        """
        expId = self._getExpId(expName=expName)
        query = '''
        {
            experimentData(experimentId: "%s"){
                id
                key
                name
                description
                begin
                end
                location
                numberOfTrials
                state
                status
                maps{
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
                project{
                    id
                    name
                    description
                    status
                }
            }
        }
        ''' % expId
        result = self._execute(query)['experimentData']
        return result#pandas.DataFrame(result)

    def _execute(self, query: str):
        """
        Executes query

        :param query: The query to execute
        :return: The query result
        """
        return self._client.execute(gql(query))


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
            self._trialSetsDict[key] = dict(experimentId=self.id, desc=trialSetDesc, client=self._client)

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
            self._deviceTypesDict[key] = dict(experimentId=self.id, desc=deviceTypeDesc, client=self._client)

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
                        state
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
            self._trialsDict[key] = dict(experimentId=self._experimentId, trialSetKey=self.key, desc=trialDesc, client=self._client)

    def getTrial(self, trialKey: str):
        """

        :param trialKey: Th trial key
        :return:
        """
        if type(self._trialsDict[trialKey]) is dict:
            self._trialsDict[trialKey] = Trial(**self._trialsDict[trialKey])
        return self._trialsDict.get(trialKey)


class Trial:
    _experiment = None
    _trialSet = None
    _desc = None
    _client = None
    _entities = None
    _entitiesDict = dict()
    _deployedEntities = None
    _deployedEntitiesDict = dict()

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
        return pandas.DataFrame[self._desc['properties']].set_index('key') if self._desc['properties'] else pandas.DataFrame()

    @property
    def entities(self):
        return pandas.DataFrame(self._desc['entities']).set_index('key') if self._desc['entities'] else pandas.DataFrame()

    @property
    def deployedEntities(self):
        return pandas.DataFrame(self._desc['deployedEntities']).set_index('key') if self._desc['deployedEntites'] else pandas.DataFrame()

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
    _deviceDict = dict()

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

    def __init__(self, experiment: Experiment, desc: dict, client: Client):
        """
        DeviceType object contains information on a specific device type

        :param experiment: The experiment object
        :param desc: A dictionary with information on the trial
        :param client: GraphQL server
        """
        self._experiment = experiment
        self._desc = desc
        self._client = client


class Device:
    _experiment = None
    _deviceType = None
    _trialKey = None
    _desc = None
    _client = None

    def __init__(self, experiment: str, deviceType: DeviceType, desc: dict, client: Client, trialKey: str = None):
        self._experiment = experiment
        self._deviceType = deviceType
        self._trialKey = trialKey
        self._desc = desc
        self._client = client
