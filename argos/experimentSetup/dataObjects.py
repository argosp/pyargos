import zipfile
import os
import json
import pandas
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import warnings

from argos.experimentSetup.fillContained import fill_properties_by_contained
from ..utils.jsonutils import loadJSON
from ..utils.logging import get_logger as argos_get_logger

import numpy


def testNan(x):
    try:
        return numpy.isnan(x)
    except Exception:

        return False


class Experiment:
    """
        Interface to the WEB experiment object.

    """

    _setupFileNameOrData = None  # experiment description holds its name, descrition and ect.
    _experimentSetup = None

    _trialSetsDict = None  # A dictionary of the trial sets.
    _entitiesTypesDict = None  # A dictionary of the devices types.

    _client = None  # The client of the connection to the WEB.

    _imagesMap = None

    def refresh(self):
        """
            Loads the experiment setup and rebuilds all the trial sets and entity types.
        """

        self._experimentSetup = loadJSON(self._setupFileNameOrData)
        self._initTrialSets()
        self._initEntitiesTypes()

    @property
    def setup(self):
        return self._experimentSetup

    @property
    def url(self):
        return self.setup['experimentsWithData']['url']

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self.setup['name']

    @property
    def description(self):
        return self.setup['description']

    @property
    def trialSet(self):
        return self._trialSetsDict

    @property
    def entityType(self):
        return self._entitiesTypesDict

    @property
    def entityTypeTable(self):
        entityTypeList = []
        for entityTypeName, entityTypeData in self.entityType.items():
            entityTypeList.append(entityTypeData.propertiesTable.assign(entityType=entityTypeName))

        return pandas.concat(entityTypeList, ignore_index=True)

    @property
    def entitiesTable(self):
        entityTypeList = []
        for entityTypeName, entityTypeData in self.entityType.items():
            for entityTypeDataName, entityData in entityTypeData.items():
                entityTypeList.append(entityData.propertiesTable.assign(entityType=entityTypeName,entityName=entityData.name))

        return pandas.concat(entityTypeList, ignore_index=True)

    @property
    def trialsTableAllSets(self):
        tableList = []
        for trialSetName in self.trialSet:
            tableList.append(self.trialsTable(trialSetName).assign(trialSet=trialSetName))
        return pandas.concat(tableList)


    def trialsTable(self, trialsetName):
        return self.trialSet[trialsetName].trialsTable

    def __init__(self, setupFileOrData):
        """
        Experiment object contains information on a specific experiment

        Parameters
        -----------

        setupFileOrData: str,dict

            - A file name that contains a dictionary with all the information on the experiment, that was downloaded from
              argosWEB (using the download metadata).
            - dict that includes all the data.


        """
        self.logger = argos_get_logger(self)
        self._trialSetsDict = dict()
        self._entitiesTypesDict = dict()

        self._setupFileNameOrData = setupFileOrData
        self.refresh()

        self.logger.execution("Loading images")
        self._init_ImageMaps()

    def _init_ImageMaps(self):
        ## Initializing the images map
        self._imagesMap = dict()
        if 'experimentsWithData' in self.setup:
            for imgs in self.setup['experimentsWithData']['maps']:
                imgName = imgs['imageName']
                imageFullURL = f"{self.url}/{imgs['imageUrl']}"
                imgs['imageURL'] = imageFullURL

                self._imagesMap[imgName] = imgs

    @property
    def imageMap(self):
        return self._imagesMap

    def getImageURL(self, imageName: str):
        return self._imagesMap[imageName]['imageURL']

    def getImageJSMappingFunction(self, imageName: str):
        """
            Return the javascript mapping function that maps the
            coordindates of the image to from the coordinates to 0..1 coordinats

            Used in thingsboard dashboards. Therefore the inputs to the function are
            (origXpos,origYpos).


        Parameters
        ----------
        imageName: str
                The name of the image


        Returns
        -------
            A string with the mapping function (in javascript).

        """
        metadata = self.getImageMetadata(imageName)

        xdim = metadata['right'] - metadata['left']
        ydim = metadata['upper'] - metadata['lower']

        Xconvert = f"image_x = (origXPos - ({metadata['left']}))/{xdim};"
        Yconvert = f"image_y = (({metadata['upper']})-origYPos)/{ydim};"

        return_string = "return {x: image_x, y: image_y};"

        return "\n".join([Xconvert, Yconvert, return_string])

    def getImageMetadata(self, imageName: str):
        return self._imagesMap[imageName]

    def _initTrialSets(self):

        for trialset in self.setup['trialSets']:
            self._trialSetsDict[trialset['name']] = TrialSet(experiment=self, metadata=trialset)

    def _initEntitiesTypes(self):
        for entityType in self.setup['entityTypes']:
            self._entitiesTypesDict[entityType['name']] = EntityType(experiment=self, metadata=entityType)

    def toJSON(self):
        """
            Create a single JSON with the data of the experiment.


        :return:
        """
        ret = dict()

        entityTypeMap = dict()
        for entityName, entityType in self.entityType.items():
            entityTypeMap[entityName] = entityType.toJSON()

        trialMap = dict()
        for trialName, trialData in self.trialSet.items():
            trialMap[trialName] = trialData.toJSON()

        ret['entityType'] = entityTypeMap
        ret['trialSet'] = trialMap

        expr = dict()

        for field in ['maps', 'begin', 'end', 'description']:
            expr[field] = self._setupFileNameOrData['experimentsWithData'][field]

        ret['experiment'] = expr
        return ret

    def getExperimentEntities(self):
        """
            Returns the list of all the entities

        :return: dict
            Return a list of the entities.
        """
        retList = []

        for entitytypeName, entityTypeObj in self.entityType.items():
            for entityName, entityData in entityTypeObj.items():
                retList.append(dict(entityName=entityName, entityTypeName=entityData.entityType.name))

        return retList

    def getEntitiesTypeByID(self, entityTypeID):

        ret = None
        for entityTypeName, entityTypeData in self.entityType.items():
            if entityTypeID == entityTypeData.keyID:
                ret = entityTypeData
                break

        return ret

    def getImage(self, imageName: str):
        imgUrl = os.path.join(self.setup['experimentsWithData']['url'], "images", f"{imageName}.png")
        # maybe we can skip the open(...), didn't want to risk it
        try:
            with open(imgUrl) as imageFile:
                img = plt.imread(imageFile)
        except UnicodeDecodeError:
            img = plt.imread(imgUrl)
        return img


class ExperimentZipFile(Experiment):

    def __init__(self, setupFileOrData):
        super().__init__(setupFileOrData=setupFileOrData)

    def getImage(self, imageName: str):

        imageurl = self._imagesMap[imageName]['filename']

        try:
            # For compliance with the old version.
            with zipfile.ZipFile(self._setupFileNameOrData) as archive:
                imageFile = archive.open(os.path.join("images", imageurl))
        except KeyError:
            # This is the new version
            with zipfile.ZipFile(self._setupFileNameOrData) as archive:
                imageFile = archive.open(os.path.join("images", imageName+".png"))

        img = plt.imread(imageFile)
        imageFile.close()
        return img

    def refresh(self):
        """
            Loads the experiment setup and rebuilds all the trial sets and entity types.
        """
        self.logger.execution("------- Start ----")
        self.logger.debug(f"Loading file {self._setupFileNameOrData}")

        with zipfile.ZipFile(self._setupFileNameOrData) as archive:
            experimentDict = loadJSON("\n".join([x.decode() for x in archive.open("data.json").readlines()]))

        fileVersion = experimentDict.get("version", "1.0.0.").replace(".", "_")
        self.logger.debug(f"Got file version {fileVersion}")

        experimentDict = getattr(self, f"_fix_json_version_{fileVersion}")(experimentDict)

        self.logger.execution("Experiemnt dict")
        self._experimentSetup = experimentDict

        self.logger.execution("Init trial sets")
        self._initTrialSets()

        self.logger.execution("Init entity type")
        self._initEntitiesTypes()

    def _init_ImageMaps(self):
        ## Initializing the images map
        #with zipfile.ZipFile(self._setupFileNameOrData) as archive:
        #    experimentDict = loadJSON("\n".join([x.decode() for x in archive.open("data.json").readlines()]))
        experimentDict = self.setup

        self._imagesMap = dict()
        for imgs in experimentDict.get('maps',[]):
            imgName = imgs['name']
            self._imagesMap[imgName] = imgs

    def _fix_json_version_1_0_0_(self, jsonFile):
        return jsonFile

    def _fix_json_version_2_0_0_(self, jsonFile):

        oldFormat = dict(experiment=jsonFile['experiment'],
                         entityTypes=jsonFile['entityTypes'],
                         trialSets=jsonFile['trialSets'])

        for trialSet in oldFormat['trialSets']:
            trialSet['trials'] = []
            currentKey = trialSet['key']
            for trial in jsonFile['trials']:
                if trial['trialSetKey'] == currentKey:
                    trialSet['trials'].append(trial)

        for entityType in oldFormat['entityTypes']:
            entityType['entities'] = []
            currentKey = entityType['key']
            for entity in jsonFile['entities']:
                if entity['entitiesTypeKey'] == currentKey:
                    entityType['entities'].append(entity)

        return oldFormat

    def _fix_json_version_3_0_0(self, jsonFile):
        oldFormat = dict(experiment={'name': jsonFile['name'],
                                     'description': jsonFile.get('description', ''),
                                     'version': jsonFile['version'],
                                     'startDate': jsonFile['startDate'],
                                     'endDate': jsonFile['endDate']},
                         entityTypes=jsonFile.get('deviceTypes', []),
                         trialSets=jsonFile.get('trialTypes', []),
                         maps = jsonFile.get("imageStandalone",[]),
                         shapes=jsonFile.get("shapes",[]),
                         )

        for entityType in oldFormat['entityTypes']:
            entityType['entities'] = []
            for device in entityType.get('devices', []):
                entityType['entities'].append(device)

        for trialSet in oldFormat['trialSets']:
            for trial in trialSet.get('trials', []):
                if 'properties' not in trial.keys():
                    trial['properties'] = []
                if 'state' not in trial.keys():
                    trial['state'] = None

                trial['entities'] = trial.get('devicesOnTrial', [])

        return oldFormat


class webExperiment(Experiment):

    def getImage(self, imageName: str):
        imgUrl = self.getImageURL(imageName)
        response = requests.get(imgUrl)

        if response.status_code != 200:
            raise ValueError(f"Image {imageName} not found on the server.")

        imageFile = BytesIO(response.content)
        return plt.imread(imageFile)


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
    def name(self):
        return self._metadata['name']

    @property
    def description(self):
        return self._metadata['description']

    @property
    def numberOfTrials(self):
        return len(self._metadata)

    @property
    def propertiesTable(self):
        return pandas.DataFrame(self.properties)

    @property
    def properties(self):
        return self._metadata['attributeTypes']

    def toJSON(self):
        ret = dict()
        ret['name'] = self.name
        ret['properties'] = self.properties

        trialsJSON = {}
        for trialName, trialData in self.items():
            trialsJSON[trialName] = trialData.toJSON()

        ret['trials'] = trialsJSON

        return ret

    @property
    def trials(self):
        return self.toJSON()['trials']

    @property
    def trialsTable(self):
        return pandas.DataFrame(self.toJSON()['trials']).T

    def __init__(self, experiment: Experiment, metadata: dict):
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

        for trial in self._metadata.get('trials', []):
            self[trial['name']] = Trial(trialSet=self, metadata=trial)


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
    def name(self):
        return self._metadata['name']

    @property
    def created(self):
        return self._metadata['created']


    @property
    def cloneFrom(self):
        return self._metadata['cloneFrom']

    @property
    def numberOfEntities(self):
        return len(self._metadata)

    @property
    def properties(self):

        propDict = {}
        propList = self._metadata['attributes'] if 'attributes' in self._metadata else self._metadata['properties']

        for prop in propList:
            propDict[prop['name']] = prop['value']

        return propDict

    @property
    def trialSet(self):
        return self._trialSet

    @property
    def propertiesTable(self):
        return pandas.DataFrame(self.properties,index=[0])

    def __init__(self, trialSet: TrialSet, metadata: dict):
        """
        Trial object contains information on a specific trial

        Parameters
        ----------

        experiment: The experiment object
        trialSet: The trial set object
        desc: A dictionary with information on the trial
        """
        self._trialSet = trialSet
        self._metadata = metadata
        if len(metadata.get('properties', [])):
            propertiesPandas = pandas.DataFrame(metadata['properties']).set_index('key')

            properties = propertiesPandas.merge(trialSet.propertiesTable, left_index=True, right_index=True)[
                ['val', 'type', 'label', 'description']]
            getParser = lambda x: getattr(self, f"_parseProperty_{x.replace('-', '_')}")

            #       this wont work well for location property in the trial because it has 2 fields.
            #       we have to get the list, and the change all the lists with size 1 to the object itself (like we do now)
            #       and leave all the lists with size 2 as is.

            parsedValuesList = []
            for key, data in properties.T.to_dict().items():
                parsed_data = getParser(data['type'])(data, data)
                if len(parsed_data[1]) > 0:
                    val = parsed_data[1][0]
                else:
                    val = None
                parsedValuesList.append((data['label'], val))

            self._properties = dict(parsedValuesList)
        else:
            self._properties = dict()

    def toJSON(self):
        val = self.properties
        val['name'] = self.name
        return val

    def __str__(self):
        return json.dumps(self.toJSON())

    def __repr__(self):
        return json.dumps(dict(name=self.name))

    def _parseProperty_location(self, property, propertyMetadata):
        """
            Parse the location property.

            Returns 3 values: location name, latitude and longitude.
            The column names are at this order.

        :param property:
                property
        :param propertyMetadata:
                The data that describes the property.

        :return: list,list
            Returns list of column names and list of values.
        """
        try:
            if isinstance(property['val'], dict):
                locationDict = property['val']
            else:
                locationDict = json.loads(property['val'])

            locationName = locationDict['name']
            coords = locationDict['coordinates']
            if isinstance(coords, str):
                coords = eval(coords)

            latitude = float(coords[0])
            longitude = float(coords[1])
            data = [locationName, latitude, longitude]
            columns = ['locationName', 'latitude', 'longitude']
        except KeyError:
            # data = [None] * 3
            data = []
            columns = []
        except TypeError:
            # data = [None] * 3
            data = []
            columns = []

        return columns, data

    def _parseProperty_text(self, property, propertyMetadata):
        """
            Parse the text property.

            Returns 2 values: location name, latitude and longitude.
        :param property:
        :param propertyMetadata:

        :return: list,list
            Returns list of column names and list of values.
        """
        propertyLabel = propertyMetadata['label']
        data = [property['val']]
        columns = [propertyLabel]

        return columns, data

    def _parseProperty_textArea(self, property, propertyMetadata):
        """
            Parse the text property.

            Returns 2 values: location name, latitude and longitude.
        :param property:
        :param propertyMetadata:

        :return: list,list
            Returns list of column names and list of values.
        """
        propertyLabel = propertyMetadata['label']

        data = [property['val']]
        columns = [propertyLabel]

        return columns, data

    def _parseProperty_boolean(self, property, propertyMetadata):
        """
            Parse the text property.

            Returns 2 values: location name, latitude and longitude.
        :param property:
        :param propertyMetadata:

        :return: list,list
            Returns list of column names and list of values.
        """
        propertyLabel = propertyMetadata['label']
        data = [property['val'].lower() in ['true','yes','1']]
        columns = [propertyLabel]

        return columns, data

    def _parseProperty_number(self, property, propertyMetadata):
        """
            Parse the text property.

            Returns 2 values: location name, latitude and longitude.
        :param property:
        :param propertyMetadata:

        :return: list,list
            Returns list of column names and list of values.
        """
        try:
            propertyLabel = propertyMetadata['label']
            flt = property['val']
            if flt is None:
                data = [None]
            else:
                data = [float(property['val'])]
            columns = [propertyLabel]
        except ValueError:
            # print(f"\tCannot convert to float property {propertyLabel}. Got value '{property['val']}'")
            data = []
            columns = []

        return columns, data

    def _parseProperty_datetime_local(self, property, propertyMetadata):
        """
            Parse the text property.

            Returns 2 values: location name, latitude and longitude.
        :param property:
        :param propertyMetadata:

        :return: list,list
            Returns list of column names and list of values.
        """
        propertyLabel = propertyMetadata['label']
        localdata = pandas.to_datetime(property['val'], utc=False)
        if localdata is None:
            data = [None]
        else:
            data = [localdata.tz_localize("israel")]
        columns = [propertyLabel]

        return columns, data

    def _parseProperty_selectList(self, property, propertyMetadata):
        propertyLabel = propertyMetadata['label']
        data = [property['val']]
        columns = [propertyLabel]

        return columns, data

    def _composeEntityProperties(self, entityType, properties):
        """
            Just resolves the properties names.
            If it is location, split into 3 coordinates.
        :param properties:
        :return:
        """
        data = []
        columns = []
        for property in properties:
            propertyKey = property['key']
            propertyMetadata = entityType.propertiesTable.loc[propertyKey]
            propertyType = propertyMetadata['type']

            prop_type_handler = getattr(self, f"_parseProperty_{propertyType}")

            pcolumns, pdata = prop_type_handler(property, propertyMetadata)
            columns += pcolumns
            data += pdata

        entity_trial_properties = pandas.DataFrame(data=[data], columns=columns, index=[0])
        return entity_trial_properties

    def _composeProperties(self, entities):
        if 'entitiesTypeKey' in entities.columns:
            fullData = self.experiment._entitiesTableFull.set_index("key").join(entities, rsuffix="_r",
                                                                                how="inner").reset_index()

            dfList = []
            for indx, (entitykey, entitydata) in enumerate(fullData.iterrows()):
                properties = entitydata['properties']
                entityType = self.experiment.getEntitiesTypeByID(entityTypeID=entitydata.entitiesTypeKey)

                entity_trial_properties = self._composeEntityProperties(entityType, properties)

                entityProperties = entityType[entitydata['name']].propertiesTable.copy()
                entity_total_properties = entity_trial_properties.join(entityProperties,
                                                                       how='left',
                                                                       rsuffix='_prop')  # .assign(trialSet = self.trialSet.name,

                dfList.append(entity_total_properties)
            new_df = pandas.concat(dfList, sort=False, ignore_index=True).drop(columns=["key", "entitiesTypeKey"])
        else:
            new_df = pandas.DataFrame(entities)

        return new_df

    @property
    def entities(self):
        ret = self.entitiesTable
        if ret.empty:
            return dict()
        else:
            datadict = ret.set_index("deviceItemName").T.to_dict()
            resultProperties = dict()
            for entityName, entityData in datadict.items():
                resultProperties[entityName] = dict(
                    [(propName, propData) for propName, propData in entityData.items() if not testNan(propData)])
            return resultProperties


    @property
    def entitiesTable(self):
        filled_entities = fill_properties_by_contained(self._trialSet.experiment.entityType, self._metadata['entities'])
        if len(filled_entities) == 0:
            entities = pandas.DataFrame()
        elif 'key' in filled_entities[0].keys():
            entities = pandas.DataFrame(filled_entities).set_index('key')
        else:
            entities = pandas.DataFrame(filled_entities)
        return self._composeProperties(entities)

    def _prepareEntitiesMetadata(self, metadata):

        retList = []
        for entityData in metadata:
            for propData in entityData['properties']:
                properties = pandas.DataFrame(propData, index=[0])
                itm = pandas.DataFrame(properties).assign(entitiesTypeKey=entityData['entitiesTypeKey'],
                                                          containsEntities=entityData['containsEntities'])
                retList.append(itm)

        return pandas.concat(retList, ignore_index=True)


################################### Depreacted part of trial

    @property
    def deployEntitiesTable(self):
        warnings.warn("deployEntitiesTable is deprecated. Use entitiesTable", DeprecationWarning, stacklevel=2)
        return self.entitiesTable

    @property
    def designEntities(self):
        warnings.warn("designEntities is deprecated. Use entities", DeprecationWarning, stacklevel=2)
        return self.entities

    @property
    def designEntitiesTable(self):
        warnings.warn("designEntitiesTable is deprecated. Use entitiesTable", DeprecationWarning, stacklevel=2)
        return self.entitiesTable

    @property
    def deployEntities(self):
        warnings.warn("deployEntities is deprecated. Use entitiesTable", DeprecationWarning, stacklevel=2)
        return self.entities

##################################################################


class EntityType(dict):
    _experiment = None
    _metadata = None


    def __init__(self, experiment: Experiment, metadata: dict):
        """
        EntityType object contains information on a specific entity type

        :param experiment: The experiment object
        :param metadata: dict
                The metadata of the entity type (the properties and ect).
        """
        self._experiment = experiment
        self._metadata = metadata

        self._initEntities()

    def _initEntities(self):
        for entity in self._metadata.get('entities', []):
            self[entity['name']] = Entity(entityType=self, metadata=entity)

    @property
    def experiment(self):
        return self._experiment

    @property
    def client(self):
        return self.experiment.client

    @property
    def name(self):
        return self._metadata['name']

    @property
    def numberOfEntities(self):
        return len(self)

    @property
    def propertiesTable(self):
        return pandas.DataFrame(self.properties)

    @property
    def properties(self):
        return self._metadata['attributeTypes']

    def toJSON(self):
        ret = dict()
        ret['name'] = self.name
        ret['properties'] = self.properties

        entityJSON = {}
        for entityName, entityData in self.items():
            entityJSON[entityName] = entityData.toJSON()

        ret['entities'] = entityJSON

        return ret


    @property
    def entitiesTable(self):
        retList = []
        for entityName, entityData in self.items():
            trialProps = entityData.propertiesTable.assign(entityName=entityName).reset_index(drop=True)
            retList.append(trialProps)
        return pandas.concat(retList).set_index("entityName")

    @property
    def entitiesAllProperties(self):
        retList = []
        for entityName, entityData in self.items():
            trialProps = entityData.allPropertiesTable.assign(entityName=entityName).reset_index(drop=True)
            retList.append(trialProps)
        return pandas.concat(retList).set_index(["entityName","trialName"])


class Entity:
    _entityType = None
    _metadata = None

    def __init__(self, entityType: EntityType, metadata: dict):
        """

        :param entityType: EntityType
                The entity type

        :param metadata : dict
                The metadata of the
        """
        self._entityType = entityType
        self._metadata = metadata

        self._properties = []
        for attr in self._entityType._metadata['attributeTypes']:
            if attr.get("scope","") == 'Constant':
                self._properties.append(dict(name=attr['name'],value=attr['defaultValue'],scope="Constant"))

        for attr in metadata.get('attributes',[]):
            self._properties.append(dict(name=attr['name'], value=attr['value'],scope="Device"))


    @property
    def entityType(self):
        return self._entityType.name

    @property
    def experiment(self):
        return self._entityType.experiment

    @property
    def name(self):
        return self._metadata['name']

    @property
    def properties(self):
        return {prop['name'] : prop['value'] for prop in self._properties}

    @property
    def propertiesList(self):
        return self._properties

    @property
    def allProperties(self):
        trialsetdict = dict() #$self.propertiesList
        for trialsSetsName in self.experiment.trialSet.keys():
            trialsetdict[trialsSetsName] = dict()
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                ddp = trialsetdict[trialsSetsName].setdefault(trialName, dict())
                ddp[trialName] = self.trialProperties(trialsSetsName, trialName)

        return trialsetdict

    @property
    def allPropertiesList(self):
        trialsetlist = self.propertiesList
        for trialsSetsName in self.experiment.trialSet.keys():
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                deploy = self.trialProperties(trialsSetsName, trialName)
                deploy['trialSetName'] = trialsSetsName
                deploy['trialName'] = trialName
                deploy['scope'] = 'trial'
                trialsetlist.append(deploy)

        return trialsetlist

    def toJSON(self):
        ret = dict()
        ret['name'] = self.name
        ret['entityType'] = self.entityType.name
        ret['trialProperties'] = self.allPropertiesList
        return ret

    def __str__(self):
        return json.dumps(self.toJSON())

    def __repr__(self):
        ret = dict(name=self.name, properties=self.propertiesList)
        return json.dumps(ret)


    @property
    def allPropertiesTable(self):
        constantProperties = self.propertiesTable
        with pandas.option_context('future.no_silent_downcasting', True):
            ret = self.allTrialPropertiesTable.join(constantProperties).ffill().infer_objects(copy=False)
        return ret

    @property
    def propertiesTable(self):
        return pandas.DataFrame(self.propertiesList)

    @property
    def allTrialPropertiesTable(self):
        retList = []
        for trialsSetsName in self.experiment.trialSet.keys():
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                trProp = self.trialProperties(trialsSetsName, trialName)
                trProp['trialSetName'] =trialsSetsName
                trProp['trialName'] = trialName
                retList.append(trProp)

        return pandas.DataFrame(retList)


    @property
    def allTrialProperties(self):
        trialsetdict = dict()

        for trialsSetsName in self.experiment.trialSet.keys():
            trialsetdict[trialsSetsName] = dict()
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                trialsetdict[trialsSetsName][trialName] = self.trialProperties(trialsSetsName, trialName)

        return trialsetdict

    def trialProperties(self, trialSetName, trialName):
        properties = self.experiment.trialSet[trialSetName][trialName].entities
        ret = properties.get(self.name, dict())
        return ret

    #################################### Deprecated entity interface ##################################

    def trial(self, trialSet, trialName, state):
        """
            Gets the properties of the trial useng the state

        Parameters
        -----------
        trialSet:  str
            The trialset name
        trialName: str
            The trial name
        state: str
            'design' or 'deploy'

        Returns
        -------
             dict
        """
        warnings.warn("trial is deprecated. Use trialProperties", DeprecationWarning, stacklevel=2)
        return getattr(self, f"trial{state.title()}")(trialSet, trialName)

    @property
    def designProperties(self):
        warnings.warn("designProperties is deprecated. Use allTriealProperties", DeprecationWarning, stacklevel=2)
        return self.propertiesList

    @property
    def deployProperties(self):
        warnings.warn("deployProperties is deprecated. Use allTriealProperties", DeprecationWarning, stacklevel=2)
        return self.propertiesList

    def trialDesign(self, trialSet, trialName):
        warnings.warn("trialDesign is deprecated. Use trialProperties", DeprecationWarning, stacklevel=2)
        return self.trialDeploy(trialSet, trialName)

    def trialDeploy(self, trialSet, trialName):
        warnings.warn("trialDeploy is deprecated. Use trialProperties", DeprecationWarning, stacklevel=2)
        properties = self.experiment.trialSet[trialSet][trialName].deployEntities
        ret = properties.get(self.name, dict())

        return ret


####################################################################################################
