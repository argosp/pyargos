import os
import json
import pandas
import pyargos.thingsboard as tb


class Experiment(object):

    _experimentPath = None
    _experimentDataJSON = None
    _home = None

    @property
    def trialsPath(self):
        return os.path.join(self._experimentPath, 'experimentData', 'trials')

    def __init__(self, configJsonPath):
        """
            Initialize home.
            read the experiment JSON.

        """
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


    def getTrialJSON(self, trialName):
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
            try:
                with open(os.path.join(self.trialsPath, 'design', '%s.json' % trialName), 'r') as trialJSON:
                    trialJson = json.load(trialJSON)
            except FileNotFoundError:
                raise FileNotFoundError('A trial named "%s" does not exist' % trialName)
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
                trialJSON = self.getTrialJSON(trialName)

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
                    trialJSON = self.getTrialJSON(trialName)

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
        Return a pandas with the definition of all the trials.

        The pandas columns are:

        trialName, entityType, entityName, type, attributeName, attributeValue

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
        for i in range(len(columnNames)):
            trialsDict[columnNames] = []
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
                        for i in range(len(columnNames)):
                            trialsDict[i].append(valuesList[i])
                        # trialsDict[columnNames[0]].append(trialName)
                        # trialsDict[columnNames[1]].append(trialState)
                        # trialsDict[columnNames[2]].append(entityJSON['entityType'])
                        # trialsDict[columnNames[3]].append(entityJSON['Name'])
                        # trialsDict[columnNames[4]].append(entityJSON['Type'])
                        # trialsDict[columnNames[5]].append(attributeName)
                        # trialsDict[columnNames[6]].append(attributeValue)
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
        trialJSON = self.getTrialJSON(trialName)
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
