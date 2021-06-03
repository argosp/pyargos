from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pandas
from.dataObjects import webExperiment,fileExperiment
import os
import json

class fileExperimentFactory:
    """
        Loads the experiment data from the directory.
    """

    def __init__(self,**kwargs):
        pass

    def getExperiment(self,experimentPath):


        experimentAbsPath = os.path.abspath(experimentPath)

        with open(os.path.join(experimentAbsPath,"experiment.json"),"r") as confFile:
            experimentDict = json.load(confFile)

        experimentDict['experimentsWithData']['url'] = experimentAbsPath
        return fileExperiment(experimentDescription=experimentDict)

    def __getitem__(self, item):
        return self.getExperiment(experimentPath=item)



class webExperimentFactory:
    """
        Loads the experiment data from the argos web

    """

    _client = None
    _url = None

    @property
    def url(self):
        return self._url

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

        graphqlUrl = f"{url}/graphql"

        headers = None if token == '' else dict(authorization=token)
        transport = AIOHTTPTransport(url=graphqlUrl, headers=headers)
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

        self._url = url


    def getExperimentMetadata(self,experimentName):
        """
            Goes to the web server and gets all the JSONs.

        :param experimentName:
        :return:
        """
        experimentDesc = self.getExperimentDescriptor(experimentName)

        ## Get the device types
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
         ''' % experimentDesc['project']['id']
        deviceTypes = self._client.execute(gql(query))



        for deviceType in deviceTypes['deviceTypes']:
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
            ''' % (experimentDesc['project']['id'], deviceType['key'])
            result = self.client.execute(gql(query))


            deviceType.update(result)

        ## Get the trialsets
        query = """{
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
        """ % experimentDesc['project']['id']
        trialsets = self._client.execute(gql(query))


        for trialset in trialsets['trialSets']:
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
            ''' % (experimentDesc['project']['id'], trialset['key'])

            result = self.client.execute(gql(query))
            trialset.update(result)


        ret = dict(experimentsWithData=experimentDesc)
        ret.update(trialsets)
        ret.update(deviceTypes)
        return ret

    def getExperiment(self,experimentName):
        experimentDict = self.getExperimentMetadata(experimentName)
        experimentDict['experimentWithData']['url'] = self.url
        return webExperiment(experimentDescription=experimentDict)



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


