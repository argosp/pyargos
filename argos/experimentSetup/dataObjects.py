import os
import json
import pandas
import requests
from io import BytesIO
import matplotlib.pyplot as plt

class Experiment:
    """
        Interface to the WEB experiment object.

    """

    _experimentDescription = None            # experiment description holds its name, descrition and ect.

    _trialSetsDict = None   # A dictionary of the trial sets.
    _entitiesTypesDict = None # A dictionary of the devices types.

    _client = None          # The client of the connection to the WEB.

    _imagesMap = None

    @property
    def experimentDescription(self):
        return self._experimentDescription

    @property
    def url(self):
        return self._experimentDescription['experimentsWithData']['url']

    @property
    def client(self):
        return self._client

    @property
    def id(self):
        ## DO NOT USE the self._experimentDescription['id']. It is not useful here.
        return self._experimentDescription['project']['id']

    @property
    def name(self):
        return self._experimentDescription['name']

    @property
    def description(self):
        return self._experimentDescription['description']


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
                for entityTypeDataName,entityData in entityTypeData.items():
                    entityTypeList.append(pandas.DataFrame(entityData.properties,index=[0]).assign(entityType=entityTypeName))

            return pandas.concat(entityTypeList,ignore_index=True)



    def __init__(self, experimentDescription: dict):
        """
        Experiment object contains information on a specific experiment

        Parameters
        -----------

        experimentDescription: dict

            A dictionary with all the information on the experiment

            obtained from JSON or from

        """

        self._trialSetsDict = dict()
        self._entitiesTypesDict = dict()

        self._experimentDescription = experimentDescription


        self._initTrialSets()
        self._initEntitiesTypes()

        ## Initializing the images map
        self._imagesMap = dict()

        for imgs in self._experimentDescription['experimentsWithData']['maps']:
            imgName = imgs['imageName']
            imageFullURL = f"{self.url}/{imgs['imageUrl']}"
            imgs['imageURL'] = imageFullURL

            self._imagesMap[imgName] = imgs


    @property
    def imageMap(self):
        return self._imagesMap

    def getImageURL(self,imageName : str):
        return self._imagesMap[imageName]['imageURL']



    def getImageJSMappingFunction(self,imageName: str):
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

        return "\n".join([Xconvert,Yconvert,return_string])

    def getImageMetadata(self,imageName : str):
        return self._imagesMap[imageName]


    def _initTrialSets(self):

        for trialset in self.experimentDescription['trialSets']:
            self._trialSetsDict[trialset['name']] = TrialSet(experiment=self, metadata=trialset)

    def _initEntitiesTypes(self):

        for entityType in self.experimentDescription['entitiesTypes']:
            self._entitiesTypesDict[entityType['name']] = EntityType(experiment=self, metadata = entityType)


    def toJSON(self):
        """
            Create a single JSON with the data of the experiment.


        :return:
        """
        ret = dict()

        entityTypeMap = dict()
        for entityName,entityType in self.entityType.items():
            entityTypeMap[entityName] = entityType.toJSON()

        trialMap = dict()
        for trialName,trialData in self.trialSet.items():
            trialMap[trialName] = trialData.toJSON()

        ret['entityType'] = entityTypeMap
        ret['trialSet'] = trialMap

        expr = dict()

        for field in ['maps','begin','end','description']:
            expr[field] = self._experimentDescription['experimentsWithData'][field]

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
        os.makedirs(toDirectory,exist_ok=True)
        imgDir = os.path.join(toDirectory, "images")
        js = self.experimentDescription

        with open(os.path.join(toDirectory,"experiment.json"),"w") as metadataJson:
            metadataJson.writelines(json.dumps(js))

        os.makedirs(imgDir,exist_ok=True)

        for imgName in self.imageMap.keys():
            img = self.getImage(imgName)
            plt.imsave(os.path.join(imgDir,f"{imgName}.png"),img)


    def getExperimentEntities(self):
        """
            Returns the list of all the entities

        :return: dict
            Return a list of the entities.
        """
        retList = []

        for entitytypeName, entityTypeObj in self._entitiesTypesDict.items():
            for entityName, entityData in entityTypeObj.items():
                retList.append(dict(entityName=entityName, entityTypeName=entityData.entityType.name))

        return retList


    def getEntitiesTypeByID(self, entityTypeID):

        ret = None
        for entityTypeName,entityTypeData in self.entityType.items():
            if entityTypeID == entityTypeData.keyID:
                ret = entityTypeData
                break

        return ret




class fileExperiment(Experiment):

    def getImage(self,imageName:str):


        imgUrl = os.path.join(self.experimentDescription['experimentWithData']['url'],imageName)


        with open(imgUrl) as imageFile:
            img = plt.imread(imageFile)
        return img


class webExperiment(Experiment):

    def getImage(self,imageName:str):
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
            trialProps = trialData.propertiesTable.assign(trialName=trialName,key=trialData.key)
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

        for trial in self._metadata['trials']:
            self[trial['name']] = Trial(trialSet=self,metadata=trial)


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
    def numberOfEntities(self):
        return self._metadata['numberOfEntities']

    @property
    def state(self):
        return self._metadata['state']

    @property
    def properties(self):
            return self._properties

    @property
    def trialSet(self):
        return self._trialSet


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


    def _composeProperties(self,entities):
        fullData = self.experiment.entityTypeTable.set_index("key").join(entities)
        dfList = []
        for entitykey,entitydata in fullData.iterrows():

            properties = entitydata['properties']
            entityType = self.experiment.getEntitiesTypeByID(entityTypeID=entities.loc[entitykey]['typeKey'])

            data = []
            columns = []
            for property in properties:
                propertyKey = property['key']
                propertyLabel = entityType.propertiesTable.loc[propertyKey]['label']
                propertyType = entityType.propertiesTable.loc[propertyKey]['type']
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


            entity_trial_properties = pandas.DataFrame(data=[data], columns=columns, index=[0])
            entityProperties = entityType[entitydata['name']].propertiesTable.copy()
            entity_total_properties = entity_trial_properties.join(entityProperties,how='left')#.assign(trialSet = self.trialSet.name,
                                                                                               #        trial = self.name)
            dfList.append(entity_total_properties)
        new_df = pandas.concat(dfList, sort=False,ignore_index=True)

        return new_df



    @property
    def designEntities(self):
        ret = self.designEntitiesTable
        if ret.empty:
            return dict()
        else:
            return ret.set_index("entityName").T.to_dict()


    @property
    def deployEntities(self):
        ret = self.deployEntitiesTable
        if ret.empty:
            return dict()
        else:
            return ret.set_index("entityName").T.to_dict()

    @property
    def designEntitiesTable(self):
        entities = pandas.DataFrame(self._metadata['entities']).set_index('key')

        return self._composeProperties(entities)

    @property
    def deployEntitiesTable(self):
        if not self._metadata['deployedEntities']:
            return pandas.DataFrame()
        else:
            entities = pandas.DataFrame(self._metadata['deployedEntities']).set_index('key')
            return self._composeProperties(entities)


    def __getitem__(self, item):
        return self._properties.loc[item].val


class EntityType(dict):
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
    def numberOfEntities(self):
        return self._metadata['numberOfEntities']

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

        entityJSON = {}
        for entityName, entityData in self.items():
            entityJSON[entityName] = entityData.toJSON()

        ret['entities'] = entityJSON

        return ret

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

        for entity in self._metadata['entities']:
            self[entity['name']] = Entity(entityType=self, metadata=entity)

    @property
    def entities(self):
        retList = []
        for entityName, entityData in self.items():
            trialProps = entityData.propertiesTable.assign(entityName=entityName, key=entityData.key)
            retList.append(trialProps)
        return pandas.concat(retList, ignore_index=True)


class Entity:
    _entityType = None
    _metadata = None

    @property
    def entityType(self):
        return self._entityType

    @property
    def experiment(self):
        return self.entityType.experiment

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
    def entityTypeKey(self):
        return self._metadata['entitiesTypeKey']

    @property
    def properties(self):

        ret = dict(self._properties)

        ret['key'] = self.key
        ret['entitiesTypeKey'] = self._metadata['entitiesTypeKey']
        ret['name'] = self.name
        ret['entityType'] = self.entityType.name

        return ret

    @property
    def allProperties(self):
        trialsetdict = dict()

        for trialsSetsName in self.experiment.trialSet.keys():
            trialsetdict[trialsSetsName] = dict()
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                ddp = trialsetdict[trialsSetsName].setdefault(trialName, dict())

                ddp['design'] = self.trialDesign(trialsSetsName, trialName)
                ddp['deploy'] = self.trialDeploy(trialsSetsName, trialName)

        return trialsetdict

    @property
    def allPropertiesList(self):

        trialsetlist = []

        for trialsSetsName in self.experiment.trialSet.keys():
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                design = self.trialDesign(trialsSetsName, trialName)
                deploy = self.trialDeploy(trialsSetsName, trialName)

                design['trialSetName'] = trialsSetsName
                design['trialName'] = trialName
                design['state'] = 'design'

                deploy['trialSetName'] = trialsSetsName
                deploy['trialName'] = trialName
                deploy['state'] = 'deploy'

                trialsetlist.append(design)
                trialsetlist.append(deploy)

        return trialsetlist

    @property
    def allPropertiesTable(self):
        return pandas.DataFrame(self.allPropertiesList)

    @property
    def propertiesTable(self):
        val = pandas.DataFrame(self.properties, index=[0])
        val = val.assign(entityName=self.name)
        return val

    def toJSON(self):
        ret = dict()
        ret['properties'] = dict(self._properties)
        ret['name'] = self.name
        ret['entityType'] = self.entityType.name
        ret['trialProperties'] = self.allPropertiesList
        return ret

    def __str__(self):
        return json.dumps(self.toJSON())

    def __repr__(self):
        props = self.properties
        props['name'] = self.name
        return json.dumps(props)

    @property
    def designProperties(self):

        trialsetdict = dict()

        for trialsSetsName in self.experiment.trialSet.keys():
            trialsetdict[trialsSetsName] = dict()
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                trialsetdict[trialsSetsName][trialName] = self.trialDesign(trialsSetsName, trialName)

        return trialsetdict

    @property
    def deployProperties(self):
        trialsetdict = dict()

        for trialsSetsName in self.experiment.trialSet.keys():
            trialsetdict[trialsSetsName] = dict()
            for trialName in self.experiment.trialSet[trialsSetsName].keys():
                trialsetdict[trialsSetsName][trialName] = self.trialDeploy(trialsSetsName, trialName)

        return trialsetdict

    def trialDesign(self, trialSet, trialName):
        properties = self.experiment.trialSet[trialSet][trialName].designEntities
        ret = properties.get(self.name, dict())

        for fld in ['key', 'name', 'entityType', 'entityTypeKey']:
            if fld in ret:
                del ret[fld]

        return ret

    def trialDeploy(self, trialSet, trialName):
        properties = self.experiment.trialSet[trialSet][trialName].deployEntities
        ret = properties.get(self.name, dict())

        for fld in ['key', 'name', 'entityType', 'entityTypeKey']:
            if fld in ret:
                del ret[fld]

        return ret

    def trial(self, trialSet, trialName,state):
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

        return getattr(self,f"trial{state.title()}")(trialSet,trialName)


    def __init__(self, entityType: EntityType, metadata: dict):
        """

        :param entityType: EntityType
                The entity type

        :param metadata : dict
                The metadata of the
        """
        self._entityType = entityType
        self._metadata = metadata
        propertiesPandas = pandas.DataFrame(metadata['properties']).set_index('key')

        properties = propertiesPandas.merge(entityType.propertiesTable.query("trialField==False"), left_index=True,
                                            right_index=True)[['val', 'type', 'label', 'description']] \
            .set_index("label")

        self._properties = dict([(key, data['val']) for key, data in properties.T.to_dict().items()])


