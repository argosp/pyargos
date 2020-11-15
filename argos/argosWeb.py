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
        result = self._client.execute(gql(query))['experiments']
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


class Experiment:
    _desc = None
    _trialSets = None
    _trialSetsDict = dict()
    _deviceTypes = None
    _deviceTypesDict = dict()
    _devices = None
    _devicesDict = dict()

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

    def _initDevices(self):
        devicesList = []
        for deviceKey in self._deviceTypesDict:
            query = '''
            {
                devices(experimentId: "%s"){
                    key
                    id
                    name
                    deviceTypeKey
                    state
                }
            }
            ''' % self.id
            result = self._client.execute(gql(query))['devices']
            self._devices = pandas.DataFrame(result).set_index('key') if result else pandas.DataFrame()
            for key in self._devices.index:
                deviceDesc = self._devices.loc[key].to_dict()
                deviceDesc['key'] = key
                self._devicesDict[key] = dict(experiment=self, desc=deviceDesc, client=self._client)


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

    def getDevice(self, deviceTypeKey: str, deviceKey: str):
        """
        Gets a Device object of a specific device

        :param deviceKey:
        :return:
        """


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
            self._trialsDict[key] = dict(experiment=self._experiment, trialSet=self, desc=trialDesc, client=self._client)

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
        return pandas.DataFrame(self._desc['properties']).set_index('key') if self._desc['properties'] else pandas.DataFrame()

    @property
    def entities(self):
        df = pandas.DataFrame(self._desc['entities']).set_index('key') if self._desc['entities'] else pandas.DataFrame()
        return df.join(df, self._experiment.devices)

    @property
    def deployedEntities(self):
        return pandas.DataFrame(self._desc['deployedEntities']).set_index('key') if self._desc['deployedEntities'] else pandas.DataFrame()

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
        return pandas.DataFrame(self._desc['properties']) if self._desc['properties'] else pandas.DataFrame()

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
