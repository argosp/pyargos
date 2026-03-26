"""
Factory classes for loading experiments from different data sources.

This module provides two factories:

- ``fileExperimentFactory`` -- loads experiments from local files (JSON or ZIP).
- ``webExperimentFactory`` -- fetches experiments from an ArgosWEB server via GraphQL.

Both factories return ``Experiment`` (or subclass) objects that provide a
unified interface to the experiment data.
"""

import glob
try:
    from gql import gql, Client
    from gql.transport.aiohttp import AIOHTTPTransport
except:
    print("qgl is not installed")

import pandas
from argos.experimentSetup.dataObjects import webExperiment,Experiment,ExperimentZipFile
import os
from argos.utils.jsonutils import loadJSON
from argos.utils.logging import get_logger as argos_get_logger

class fileExperimentFactory:
    """
    Factory that loads experiment data from the local filesystem.

    Scans the experiment directory's ``runtimeExperimentData/`` folder for
    either a ``.zip`` file or an ``experiment.json`` file, and returns the
    appropriate Experiment object.

    Parameters
    ----------
    experimentPath : str, optional
        Path to the experiment root directory. Defaults to the current
        working directory if not specified.

    Examples
    --------
    >>> factory = fileExperimentFactory("/path/to/experiment")
    >>> experiment = factory.getExperiment()
    >>> print(experiment.name)
    """

    basePath = None

    def __init__(self, experimentPath=None):
        """
        Initialize the file experiment factory.

        Parameters
        ----------
        experimentPath : str, optional
            Path to the experiment root directory. If None, uses the
            current working directory.
        """
        self.basePath = os.getcwd() if experimentPath is None else experimentPath
        self.logger = argos_get_logger(self)

    def getExperiment(self):
        """
        Load the experiment from the filesystem.

        Searches ``[experimentPath]/runtimeExperimentData`` for experiment data.
        If a ``.zip`` file is found, returns an ``ExperimentZipFile``.
        Otherwise, attempts to load ``experiment.json`` and returns an ``Experiment``.

        Returns
        -------
        Experiment or ExperimentZipFile
            The loaded experiment object.

        Raises
        ------
        ValueError
            If neither a ZIP file nor ``experiment.json`` can be found in the
            experiment data directory.
        """
        experimentAbsPath = os.path.abspath(os.path.join(self.basePath,"runtimeExperimentData"))

        # Scan the directory to check if there is a .zip file.
        zipped = False

        zipfileList = [fle for fle in glob.glob(os.path.join(experimentAbsPath,"*.zip"))]
        if len(zipfileList) == 0:
            self.logger.info(f"Cannot find zip files in the {experimentAbsPath}, trying to load the experiment.json file")
            datafile = os.path.join(experimentAbsPath, "experiment.json")
            if not os.path.isfile(datafile):
                experimentDict = loadJSON(datafile)
            else:
                err = f"cannot find experiment.json in the directory {os.path.join(experimentAbsPath)}"
                self.logger.error(err)
                raise ValueError(err)
        else:
            zipped = True
            self.logger.info(f"Found zip files: {zipfileList}. Taking the first: {zipfileList[0]}")
            experimentDict = zipfileList[0]

        if zipped:
            ret =  ExperimentZipFile(setupFileOrData=experimentDict)
        else:
            ret =  Experiment(setupFileOrData=experimentDict)

        self.logger.info("------------- End ----------")
        return ret

    def __getitem__(self, item):
        """
        Load an experiment by path using dictionary-style access.

        Parameters
        ----------
        item : str
            The experiment path.

        Returns
        -------
        Experiment or ExperimentZipFile
            The loaded experiment object.
        """
        return self.getExperiment(experimentPath=item)


class webExperimentFactory:
    """
    Factory that fetches experiment data from an ArgosWEB server via GraphQL.

    Connects to the server's GraphQL endpoint and provides methods to list,
    describe, and fully load experiments.

    Parameters
    ----------
    url : str
        The base URL of the ArgosWEB server (e.g., ``"http://localhost:3000"``).
    token : str
        The authorization token for the server. Use an empty string for
        unauthenticated access.

    Examples
    --------
    >>> factory = webExperimentFactory("http://argos-server:3000", "my-token")
    >>> experiment = factory.getExperiment("MyExperiment")
    >>> print(factory.listExperimentsNames())
    """

    _client = None
    _url = None

    @property
    def url(self):
        """
        The base URL of the ArgosWEB server.

        Returns
        -------
        str
            The server URL.
        """
        return self._url

    @property
    def client(self):
        """
        The GraphQL client used for server communication.

        Returns
        -------
        Client
            The GQL client instance.
        """
        return self._client

    def __init__(self, url: str, token: str):
        """
        Initialize the web experiment factory.

        Parameters
        ----------
        url : str
            The base URL of the ArgosWEB server.
        token : str
            The authorization token. Use an empty string for unauthenticated access.
        """

        graphqlUrl = f"{url}/graphql"

        headers = None if token == '' else dict(authorization=token)
        transport = AIOHTTPTransport(url=graphqlUrl, headers=headers)
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

        self._url = url


    def getExperimentMetadata(self,experimentName):
        """
        Fetch the full metadata for an experiment from the server.

        Queries the GraphQL API to retrieve entity types, entities, trial sets,
        and trials with all their properties and relationships.

        Parameters
        ----------
        experimentName : str
            The name of the experiment to fetch.

        Returns
        -------
        dict
            A dictionary containing the full experiment metadata with keys
            ``experimentsWithData``, ``entitiesTypes``, and ``trialSets``.
        """
        experimentDesc = self.getExperimentDescriptor(experimentName)

        ## Get the entities types
        query = '''
         {
             entitiesTypes(experimentId: "%s"){
                 key
                 name
                 numberOfEntities
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
        entitiesTypes = self._client.execute(gql(query))



        for entityType in entitiesTypes['entitiesTypes']:
            query = '''
            {
                entities(experimentId: "%s", entitiesTypeKey: "%s"){
                    key
                    name
                    entitiesTypeKey
                    state
                    properties{
                        val
                        key
                    }
                }
            }
            ''' % (experimentDesc['project']['id'], entityType['key'])
            result = self.client.execute(gql(query))

            entityType.update(result)

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
                    numberOfEntities
                    state
                    properties{
                        val
                        key
                    }
                    entities{
                        entitiesTypeKey
                        properties{
                            val
                            key
                        }
                        key
                        containsEntities
                    }
                    deployedEntities{
                        entitiesTypeKey
                        properties{
                            val
                            key
                        }
                        key
                        containsEntities
                    }
                }
            }
            ''' % (experimentDesc['project']['id'], trialset['key'])

            result = self.client.execute(gql(query))
            trialset.update(result)


        ret = dict(experimentsWithData=experimentDesc)
        ret.update(trialsets)
        ret.update(entitiesTypes)
        return ret

    def getExperiment(self,experimentName):
        """
        Load a full experiment from the server.

        Fetches the experiment metadata via GraphQL and returns a
        ``webExperiment`` object with the data populated.

        Parameters
        ----------
        experimentName : str
            The name of the experiment to load.

        Returns
        -------
        webExperiment
            The loaded experiment object.
        """
        experimentDict = self.getExperimentMetadata(experimentName)
        experimentDict['experimentsWithData']['url'] = self.url
        return webExperiment(setupFileOrData=experimentDict)



    def getExperimentsDescriptionsList(self):
        """
        List all experiments on the server with their metadata.

        Queries the GraphQL API for all experiments and returns their
        descriptors including name, description, dates, and map definitions.

        Returns
        -------
        list[dict]
            A list of experiment descriptor dicts, each containing:

            - ``name`` : experiment name
            - ``description`` : experiment description
            - ``begin``, ``end`` : experiment date range
            - ``numberOfTrials`` : trial count
            - ``project.id`` : internal project ID
            - ``maps`` : list of image map definitions with coordinates
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
        Get all experiment descriptions as a Pandas DataFrame.

        Returns
        -------
        pandas.DataFrame
            A flattened DataFrame of all experiments on the server with
            their metadata.
        """
        return pandas.json_normalize(self.getExperimentsDescriptionsList())


    def getExperimentDescriptor(self,experimentName):
        """
        Get the descriptor for a specific experiment by name.

        Parameters
        ----------
        experimentName : str
            The name of the experiment.

        Returns
        -------
        dict
            The experiment descriptor containing ``name``, ``description``,
            ``begin``, ``end``, ``numberOfTrials``, ``project.id``, and ``maps``.

        Raises
        ------
        IndexError
            If no experiment with the given name is found on the server.
        """
        descs = self.getExperimentsDescriptionsList()

        return [x for x in descs if x['name']==experimentName][0]


    def listExperimentsNames(self):
        """
        List the names of all experiments on the server.

        Returns
        -------
        list[str]
            A list of experiment name strings.
        """
        return [x['name'] for x in self.listExperimentsDescriptions()]

    def __getitem__(self, item):
        """
        Load an experiment by name using dictionary-style access.

        Parameters
        ----------
        item : str
            The experiment name.

        Returns
        -------
        webExperiment
            The loaded experiment object.
        """
        return self.getExperiment(experimentName=item)

    def keys(self):
        """
        Return the names of all experiments on the server.

        Returns
        -------
        list[str]
            A list of experiment name strings.
        """
        return self.listExperiments()['name']
