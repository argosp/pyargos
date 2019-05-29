import os
import json
import pyargos.thingsboard as tb


class Experiment(object):

    _experimentDataPath = None
    _trialPath = None

    def getWindows(self,type):
        """
        Return the windows of the type.

        if does not exist, return empty list.

        :param type:
        :return:
        """
        return self._experimentDataJSON['properties']['calculationWindows'][type]


    def __init__(self, JSON):
        """
            Initialize home.
            read the experiment JSON.

        """
        currentDirectory = os.getcwd()
        if os.path.exists(os.path.join(currentDirectory, 'experimentData', 'ExperimentData.json')):
            self._experimentDataPath = os.path.join(currentDirectory, 'experimentData')
            self._trialPath = os.path.join(self._experimentDataPath, 'trials')
            with open(os.path.join(self._experimentDataPath, 'ExperimentData.json'), 'r') as experimentDataJSON:
                self._experimentDataJSON = json.load(experimentDataJSON)
            self._home = tb.tbHome(JSON['connection'])
        else:
            raise EnvironmentError('Current directory is not an experiment directory')


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
                    entityName = entitiesCreation['Name']
                else:
                    entityName = '%s_%d' % (entitiesCreation['Name'], entityNum + 1)
                entityHome = getattr(self._home, "%sHome" % (entitiesCreation['entityType'].lower()))
                entityProxy = entityHome.createProxy(entityName, entitiesCreation['Type'])
                windowEntitiesNames = []
                try:
                    for window in trialTemplate['properties']['calculationWindows'][entitiesCreation['Type']]:
                        windowEntityName = self._getWindowEntityName(entityName, window)
                        windowEntityType = 'calculated_%s' % entitiesCreation['Type']
                        windowEntityProxy = entityHome.createProxy(windowEntityName, windowEntityType)
                        entityProxy.addRelation(windowEntityProxy)
                        windowEntitiesNames.append(windowEntityName)
                except KeyError:
                    pass
                trialTemplate['Entities'].append({'Name': entityName,
                                                  'entityType': entityType,
                                                  'Type': entitiesCreation['Type'],
                                                  'attributes': {'longitude': 0, 'latidude': 0},
                                                  'contains': windowEntitiesNames})
        with open(os.path.join(self._trialPath ,'trialTemplate.json'), 'w') as trialTemplateJSON:
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
        return [x.split('.')[0] for x in os.listdir(os.path.join(self._trialPath, 'design'))]


    def getTrialJSON(self, trialName):
        """
            Load and return the JSON of the trial
        :param trialName: The name of the trial
        :param trialType: 'design' / 'execution'
        :return:
        """
        if os.path.exists(os.path.join(self._trialPath, 'execution', '%s.json' % trialName)):
            with open(os.path.join(self._trialPath, 'execution', '%s.json' % trialName), 'r') as trialJSON:
                trialJson = json.load(trialJSON)
        else:
            try:
                with open(os.path.join(self._trialPath, 'design', '%s.json' % trialName), 'r') as trialJSON:
                    trialJson = json.load(trialJSON)
            except FileNotFoundError:
                raise FileNotFoundError('A trial named "%s" does not exist' % trialName)
            with open(os.path.join(self._trialPath, 'execution', '%s.json' % trialName), 'w') as trialJSON:
                json.dump(trialJson, trialJSON, indent=4, sort_keys=True)
        return trialJson


    def getTrialJSON_from_design(self, trialName):
        try:
            with open(os.path.join(self._trialPath, 'design', '%s.json' % trialName), 'r') as trialJSON:
                trialJson = json.load(trialJSON)
        except FileNotFoundError:
            raise FileNotFoundError('A trial named "%s" does not exist' % trialName)
        return trialJson


    def setAttributeInTrial(self, trialName, entityType, entityName, attrMap):
        """
            Also updates the JSON of the trial
            Set the attribute for the required entity and all the entities it contains.

        :param entityType:
        :param entityName:
        :param attrMap:
        :return:
        """
        pass


    def getTrial(self, trialName=None):
        """
        Return a pandas with the definition of the trial.

        The pandas columns are:

        trialName, entityType, entityName, type attributeName attributeValue

        :param trialName: if NOne, return the pandas for all trials.
        :return:
           a pandas.
        """
        pass


    def loadTrial(self, trialName):
        """
        Loads the trial to the TB server.

        Loads the JSON from the disk and then load the
        entities to the server.

        commits the changes to git.

        :param name:
        :return:
        """
        trialJSON = self.getTrialJSON(trialName)
        for entityJSON in trialJSON['Entities']:
            entityTypeHome = getattr(self._home, '%sHome' % entityJSON['entityType'].lower())
            entityProxy = entityTypeHome.createProxy(entityJSON['Name'])
            self._setEntityForTrialInTB(entityProxy, entityJSON)
            try:
                for window in self.getWindows(entityJSON["Type"]):
                    windowEntityJSON = entityJSON.copy()
                    windowEntityJSON['Type'] = 'calculated_%s' % entityJSON['Type']
                    windowEntityJSON['Name'] = self._getWindowEntityName(entityJSON['Name'], window)
                    windowEntityProxy = entityTypeHome.createProxy(windowEntityJSON['Name'])
                    self._setEntityForTrialInTB(windowEntityProxy, windowEntityJSON)
            except KeyError:
                pass

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
                for window in self.getWindows(entityJSON["Type"]):
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
