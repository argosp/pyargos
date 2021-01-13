import os
import json
import pandas
from . import thingsboard as tb
from .argosWeb import GQLDataLayer
from typing import Union


class AbstractExperiment(object):

    def setup(self, **kwargs):
        raise NotImplementedError

    def loadTrial(self, **kwargs):
        raise NotImplementedError

    def dumpTrial(self,**kwargs):
        raise NotImplementedError

class ExperimentJSON(AbstractExperiment):

    _experimentPath = None
    _experimentDataJSON = None
    _home = None

    @property
    def trialsPath(self):
        return os.path.join(self._experimentPath, 'experimentData', 'trials')

    @property
    def home(self):
        return self._home

    def __init__(self, configJsonPath):
        """
            Initialize home.
            read the experiment JSON.

        """
        try:
            JSON = json.loads(configJsonPath)
        except json.JSONDecodeError:
            with open(configJsonPath, 'r') as jsonFile:
                JSON = json.load(jsonFile)

        self._experimentPath = JSON['experimentPath']

        if os.path.exists(os.path.join(self._experimentPath, 'experimentData', 'ExperimentData.json')):
            with open(os.path.join(self._experimentPath, 'experimentData', 'ExperimentData.json'), 'r') as experimentDataJSON:
                self._experimentDataJSON = json.load(experimentDataJSON)
            self._home = tb.tbHome(JSON['connection'])
        else:
            raise EnvironmentError('Current directory is not an experiment directory')


    def _getWindows(self,type):
        """
        Return the windows of the type.

        if does not exist, return empty list.

        :param type:
        :return:
        """
        return self._experimentDataJSON['properties']['calculationWindows'][type]


    def setup(self):
        """
        Loads all the devices with the ids to the TB.

        that is, prepare an experiment.

        and save the trial template to the directory in the json.

        make sure the trials direcotry is git repository  (check if .git exists).

        :return:
        """
        trialTemplate = {}
        trialTemplate['properties'] = self._experimentDataJSON['properties']
        trialTemplate['Entities'] = []
        for entitiesCreation in self._experimentDataJSON['Entities']:
            entityType = entitiesCreation['entityType']
            for entityNum in range(entitiesCreation['Number']):
                if entitiesCreation['Number'] == 1:
                    entityName = entitiesCreation['nameFormat']
                    id = None
                else:
                    id = entityNum + 1
                    entityName = entitiesCreation['nameFormat'].format(id=id)
                entityHome = getattr(self._home, "%sHome" % (entitiesCreation['entityType'].lower()))
                entityHome.createProxy(entityName, entitiesCreation['Type'])
                windowEntitiesNames = []
                try:
                    for window in trialTemplate['properties']['calculationWindows'][entitiesCreation['Type']]:
                        windowEntityName = self._getWindowEntityName(entityName, window)
                        windowEntityType = 'calculated_%s' % entitiesCreation['Type']
                        entityHome.createProxy(windowEntityName, windowEntityType)
                        windowEntitiesNames.append(['DEVICE', windowEntityName])
                        trialTemplate['Entities'].append({'Name': windowEntityName,
                                                          'entityType': entityType,
                                                          'Type': windowEntityType,
                                                          'attributes': {'longitude': 0, 'latitude': 0, 'id': id},
                                                          'contains': []})
                except KeyError:
                    pass
                trialTemplate['Entities'].append({'Name': entityName,
                                                  'entityType': entityType,
                                                  'Type': entitiesCreation['Type'],
                                                  'attributes': {'longitude': 0, 'latitude': 0, 'id': id},
                                                  'contains': windowEntitiesNames})
        os.makedirs(os.path.join(self.trialsPath), exist_ok=True)
        with open(os.path.join(self.trialsPath , 'trialTemplate.json'), 'w') as trialTemplateJSON:
            json.dump(trialTemplate, trialTemplateJSON, indent=4, sort_keys=True)


    def _getWindowEntityName(self,entityName,window):
        """
        creates the name of the device with the window.

        i.e. [devicename]_[window in seconds]s
        :param entityName:
        :param window:
        :return:
        """
        return '%s_%ds' % (entityName, window)


    def getTrialList(self):
        """
        Return the list of trials. actually the list of file names. without the extension

        trial directory is given in the JSON

        :return:
            A pandas series. | list
        """
        return [x.split('.')[0] for x in os.listdir(os.path.join(self.trialsPath, 'design'))]


    def getTrialJSON_from_execution(self, trialName):
        """
            Load and return the JSON of the trial
        :param trialName: The name of the trial
        :param trialType: 'design' / 'execution'
        :return:
        """
        if os.path.exists(os.path.join(self.trialsPath, 'execution', '%s.json' % trialName)):
            with open(os.path.join(self.trialsPath, 'execution', '%s.json' % trialName), 'r') as trialJSON:
                trialJson = json.load(trialJSON)
        else:
            # try:
            #     with open(os.path.join(self.trialsPath, 'design', '%s.json' % trialName), 'r') as trialJSON:
            #         trialJson = json.load(trialJSON)
            # except FileNotFoundError:
            #     raise FileNotFoundError('A trial named "%s" does not exist' % trialName)
            trialJson = self.getTrialJSON_from_design(trialName)
            with open(os.path.join(self.trialsPath, 'execution', '%s.json' % trialName), 'w') as trialJSON:
                json.dump(trialJson, trialJSON, indent=4, sort_keys=True)
        return trialJson

    def getTrialJSON_from_design(self, trialName):
        try:
            with open(os.path.join(self.trialsPath, 'design', '%s.json' % trialName), 'r') as trialJSON:
                trialJson = json.load(trialJSON)
        except FileNotFoundError:
            raise FileNotFoundError('A trial named "%s" does not exist' % trialName)
        return trialJson

    def getContainedEntities(self, trialName, entityType, entityName, trialState='execution'):
        if trialState == 'execution':
            trialJson = self.getTrialJSON_from_execution(trialName)
        else:
            trialJson = self.getTrialJSON_from_design(trialName)
        containedEntities = pandas.DataFrame(columns=['entityType', 'entityName'])
        for entityJson in trialJson['Entities']:
            if entityJson['Name']==entityName and entityJson['entityType']==entityType:
                for containedEntity in entityJson['contains']:
                    containedEntities = containedEntities.append({'entityType':containedEntity[0], 'entityName':containedEntity[1]}, ignore_index=True)
                break

        return containedEntities

    def setAttributesInTrial(self, trialName, entityType, entityName, attrMap, updateLevel=None, trialJSON=None):
        """
            Also updates the JSON of the trial
            Set the attribute for the required entity and all the entities it contains.

        :param entityType:
        :param entityName:
        :param attrMap:
        :param updateLevel: how much recursive steps to update
        :return:
        """
        if updateLevel is None:
            if trialJSON is None:
                trialJSON = self.getTrialJSON_from_execution(trialName)

            for i, entityJSON in enumerate(trialJSON['Entities']):
                if entityJSON['Name']==entityName and entityJSON['entityType']==entityType:
                    break

            trialJSON['Entities'][i]['attributes'].update(attrMap)
            # entityTypeHome = getattr(self._home, '%sHome' % entityType.lower())
            # entityProxy = entityTypeHome.createProxy(entityName)
            # entityProxy.setAttributes(attrMap)
            if not entityJSON['contains']:
                path = os.path.join(self.trialsPath, 'execution', '%s.json' % trialName)
                with open(path, 'w') as trialFile:
                    json.dump(trialJSON, trialFile, indent=4, sort_keys=True)
                os.chdir(os.path.join(self._experimentPath, 'experimentData'))
                os.system('git commit -a -m "Attributes of %s: %s, have been updated in trial: %s. Attributes: %s"' % (entityType, entityName, trialName, attrMap))
            else:
                for contatinedEntity in entityJSON['contains']:
                    self.setAttributesInTrial(trialName, contatinedEntity[0], contatinedEntity[1], attrMap, trialJSON=trialJSON)
        else:
            if updateLevel < 0:
                path = os.path.join(self.trialsPath, 'execution', '%s.json' % trialName)
                with open(path, 'w') as trialFile:
                    json.dump(trialJSON, trialFile, indent=4, sort_keys=True)
                os.chdir(os.path.join(self._experimentPath, 'experimentData'))
                os.system('git commit -a -m "Attributes of %s: %s, have been updated in trial: %s. Attributes: %s"' % (entityType, entityName, trialName, attrMap))
            else:
                if trialJSON is None:
                    trialJSON = self.getTrialJSON_from_execution(trialName)

                for i, entityJSON in enumerate(trialJSON['Entities']):
                    if entityJSON['Name'] == entityName and entityJSON['entityType'] == entityType:
                        break

                trialJSON['Entities'][i]['attributes'].update(attrMap)
                # entityTypeHome = getattr(self._home, '%sHome' % entityType.lower())
                # entityProxy = entityTypeHome.createProxy(entityName)
                # entityProxy.setAttributes(attrMap)
                if not entityJSON['contains']:
                    path = os.path.join(self.trialsPath, 'execution', '%s.json' % trialName)
                    with open(path, 'w') as trialFile:
                        json.dump(trialJSON, trialFile, indent=4, sort_keys=True)
                    os.chdir(os.path.join(self._experimentPath, 'experimentData'))
                    os.system('git commit -a -m "Attributes of %s: %s, have been updated in trial: %s. Attributes: %s"' % (entityType, entityName, trialName, attrMap))
                else:
                    for contatinedEntity in entityJSON['contains']:
                        self.setAttributesInTrial(trialJSON, contatinedEntity[0], contatinedEntity[1], attrMap,
                                                 updateLevel=updateLevel - 1, trialJSON=trialJSON)


    def getTrialsEntities(self):
        """
        Return a pandas with the definition of all entities of all trials.

        The pandas columns are:

        trialName, trialState, entityType, entityName, Type, attributeName, attributeValue

        :return: a pandas.
        """

        trialStates = ['design', 'execution']
        columnNames = ['trialName', 'trialState', 'entityType', 'entityName', 'Type', 'attributeName', 'attributeValue']
        # trialsDict = {'Trial Name': [],
        #               'Trial State': [],
        #               'Attribute Name': [],
        #               'Attribute Value': []
        #               }
        trialsDict = {}
        for columnName in columnNames:
            trialsDict[columnName] = []
        for trialName in self.getTrialList():
            for trialState in trialStates:
                #print(os.path.join(self.trialsPath, trialState, '%s.json' % trialName))
                with open(os.path.join(self.trialsPath, trialState, '%s.json' % trialName), 'r') as trialFile:
                    trialJSON = json.load(trialFile)
                for entityJSON in trialJSON['Entities']:
                    for attributeName, attributeValue in entityJSON['attributes'].items():
                        # trialsDict['Trial Name'].append(trialName)
                        # trialsDict['Trial State'].append(trialState)
                        # trialsDict['Attribute Name'].append(attributeName)
                        # trialsDict['Attribute Value'].append(attributeValue)
                        valuesList = [trialName, trialState, entityJSON['entityType'], entityJSON['Name'], entityJSON['Type'], attributeName, attributeValue]
                        for i, columnName in enumerate(columnNames):
                            trialsDict[columnName].append(valuesList[i])
                        # trialsDict[columnNames[0]].append(trialName)
                        # trialsDict[columnNames[1]].append(trialState)
                        # trialsDict[columnNames[2]].append(entityJSON['entityType'])
                        # trialsDict[columnNames[3]].append(entityJSON['Name'])
                        # trialsDict[columnNames[4]].append(entityJSON['Type'])
                        # trialsDict[columnNames[5]].append(attributeName)
                        # trialsDict[columnNames[6]].append(attributeValue)
        return pandas.DataFrame(trialsDict)

    def getTrials(self):
        """
        Return a pandas with the definition of all trials.
        :return: a pandas.
        """
        trialStates = ['design', 'execution']
        columnNames = ['trialName', 'trialState', 'propertyName', 'propertyValue']
        trialsDict = {}
        for columnName in columnNames:
            trialsDict[columnName] = []
        for trialName in self.getTrialList():
            for trialState in trialStates:
                with open(os.path.join(self.trialsPath, trialState, '%s.json' % trialName), 'r') as trialFile:
                    trialJSON = json.load(trialFile)
                flag = True
                for propertyName, propertyValue in trialJSON['properties'].items():
                    if type(propertyValue) is not dict:
                        flag = False
                        valuesList = [trialName, trialState, propertyName, propertyValue]
                        for i, columnName in enumerate(columnNames):
                            trialsDict[columnName].append(valuesList[i])
                if flag:
                    valuesList = [trialName, trialState, None, None]
                    for i, columnName in enumerate(columnNames):
                        trialsDict[columnName].append(valuesList[i])

        return pandas.DataFrame(trialsDict)

    def loadTrial(self, trialName):
        """
        Loads the trial to the TB server.

        Loads the JSON from the disk and then load the
        entities to the server.

        commits the changes to git.

        :param name:
        :return:
        """
        trialJSON = self.getTrialJSON_from_execution(trialName)
        for entityJSON in trialJSON['Entities']:
            entityTypeHome = getattr(self._home, '%sHome' % entityJSON['entityType'].lower())
            entityProxy = entityTypeHome.createProxy(entityJSON['Name'])
            self._setEntityForTrialInTB(entityProxy, entityJSON)
            # try:
            #     for window in self.getWindows(entityJSON["Type"]):
            #         windowEntityJSON = entityJSON.copy()
            #         windowEntityJSON['Type'] = 'calculated_%s' % entityJSON['Type']
            #         windowEntityJSON['Name'] = self._getWindowEntityName(entityJSON['Name'], window)
            #         windowEntityProxy = entityTypeHome.createProxy(windowEntityJSON['Name'])
            #         self._setEntityForTrialInTB(windowEntityProxy, windowEntityJSON)
            # except KeyError:
            #     pass


    def loadTrialFromDesign(self, trialName):
        """
        Loads the trial to the TB server.

        Loads the JSON from the disk and then load the
        entities to the server.

        commits the changes to git.

        :param name:
        :return:
        """
        trialJSON = self.getTrialJSON_from_design(trialName)

        for entityJSON in trialJSON['Entities']:
            entityTypeHome = getattr(self._home, '%sHome' % entityJSON['entityType'].lower())
            entityProxy = entityTypeHome.createProxy(entityJSON['Name'])
            self._setEntityForTrialInTB(entityProxy, entityJSON)
            try:
                for window in self._getWindows(entityJSON["Type"]):
                    windowEntityJSON = entityJSON.copy()
                    windowEntityJSON['Type'] = 'calculated_%s' % entityJSON['Type']
                    windowEntityJSON['Name'] = self._getWindowEntityName(entityJSON['Name'], window)
                    windowEntityProxy = entityTypeHome.createProxy(windowEntityJSON['Name'])
                    self._setEntityForTrialInTB(windowEntityProxy, windowEntityJSON)
            except KeyError:
                pass


    def _setEntityForTrialInTB(self, entityProxy, JSON):
        self._prepareEntity(entityProxy, JSON)
        self._loadEntity(entityProxy, JSON)


    def _loadEntity(self, entityProxy ,JSON):
        if JSON['attributes']:
            entityProxy.setAttributes(JSON['attributes'])
        for containedEntity in JSON['contains']:
            containedEntityHome = getattr(self._home, "%sHome" % (containedEntity[0].lower()))
            containedEntityProxy = containedEntityHome.createProxy(containedEntity[1])
            entityProxy.addRelation(containedEntityProxy)
        # try:
        #     entityTypeHome = getattr(self._home, '%sHome' % JSON['entityType'].lower())
        #     for window in self.getWindows(JSON["Type"]):
        #         windowEntityName = self._getWindowEntityName(JSON['Name'], window)
        #         windowEntityProxy = entityTypeHome.createProxy(windowEntityName)
        #         entityProxy.addRelation(windowEntityProxy)
        # except KeyError:
        #     pass


    def _prepareEntity(self, entityProxy, JSON):
        """
            Delete relations and attributes (that are in the JSON).

        :param entityName:
        :return:
        """
        entityProxy.delRelations()
        for attributeKey, attributeValue in JSON['attributes'].items():
            entityProxy.delAttributes(attributeKey)


class ExperimentGQL(AbstractExperiment):
    """
        Gets the experiment configuration from the
        argosWeb server using graphQL.

    """

    _expConf = None
    _gqlDL = None
    _tbh = None
    _windowsDict = None

    @property
    def experimentName(self):
        return self._expConf['name']
    
    @property
    def tbHome(self):

        if self._tbh is None:
            tb_config = self._expConf['thingsboard']
            self._tbh = tb.tbHome(tb_config)


        return self._tbh

    @property
    def gqDL(self):
        return self._gqlDL

    @property
    def experiment(self):
        return self.gqDL.getExperimentByName(self.experimentName)

    def __init__(self, expConf: Union[str, dict]):
        """

        :param expConf: The experiment configuration
        """

        if type(expConf) is str:
            with open(expConf, 'r') as myFile:
                expConf = json.load(myFile)
        self._expConf = expConf

        gql_config = expConf['graphql']
        self._gqlDL = GQLDataLayer(url=gql_config['url'], token=gql_config['token'])


        self._windowsDict = {deviceType: list(self._expConf['kafka']['consumers'][deviceType]['processes'].keys()) for deviceType in self._expConf['kafka']['consumers'].keys()}

    def setup(self):
        devices = self._gqlDL.getExperimentDevices(experimentName=self.experimentName)
        for deviceDict in devices:
            deviceName = deviceDict['deviceName']
            deviceType = deviceDict['deviceTypeName']
            windows = self._windowsDict[deviceType]
            self.tbHome.deviceHome.createProxy(deviceName, deviceType)
            for window in windows:
                windowDeviceName = f'{deviceName}_{window}s'
                windowDeviceType = f'calculated_{deviceType}'
                self.tbHome.deviceHome.createProxy(windowDeviceName, windowDeviceType)

    def createTrialDevicesThingsboard(self, trialSetName: str, trialName: str, trialType: str = 'deploy'):

        devices = self.glDL.getThingsboardTrialLoadConf(self.experimentName, trialSetName, trialName, trialType)
        for deviceDict in devices:
            windows = self._windowsDict[deviceDict['deviceTypeName']]
            deviceProxy = self.tbHome.deviceHome.createProxy(deviceDict['deviceName'])
            for attributeKey, attributeValue in deviceDict['attributes'].items():
                deviceProxy.delAttributes(attributeKey)
                deviceProxy.setAttributes(deviceDict['attributes'])
                for window in windows:
                    windowDeviceName = f'{deviceDict["deviceName"]}_{window}s'
                    windowDeviceProxy = self.tbHome.deviceHome.createProxy(windowDeviceName)
                    windowDeviceProxy.delAttributes(attributeKey)
                    windowDeviceProxy.setAttributes(deviceDict['attributes'])

    def loadTrialDesignToTBF(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'design')

    def loadTrialDeployToTBF(self, trialSetName: str, trialName: str):
        self.loadTrial(trialSetName, trialName, 'deploy')


    def dumpExperimentDevices(self,experimentName):
        """
            Writes the devices and the properties to a file.

        :return:
            None
        """
        devices = self.experiment.devices[['deviceTypeName', 'deviceName']]
        devicesJSON = [devices.loc[key].to_dict() for key in devices.index]


        with open(f"{experimentName}.json", 'w') as outputFile:
            outputFile.write(json.dumps(devicesJSON, indent=4, sort_keys=True))

