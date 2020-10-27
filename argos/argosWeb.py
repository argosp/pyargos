from gql import gql, Client, AIOHTTPTransport
import pandas


class GQLDataLayer:
    _client = None

    def __init__(self, url: str, token: str = ''):
        """
        A data layer to get information from the graphql server

        :param url: The url of the graphql server
        :param authorization: the authorization token
        """

        headers = None if token=='' else dict(authorization=token)
        transport = AIOHTTPTransport(url=url, headers=headers)
        self._client = Client(transport=transport, fetch_schema_from_transport=True)

    def getExperiments(self):
        """
        Get the experiments information

        :return: pandas.DataFrame
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
        return pandas.DataFrame(result)

    def _getExpId(self, expName: str):
        """
        Gets the experiment id

        :param expName: The experiment name
        :return: str
        """
        return self.getExperiments().query(f"name=='{expName}'")['id'].values[0]

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
        return self.getDeviceTypes(expName=expName).query(f"name=='{deviceType}'")['key'].values[0]

    def getDevicesByDeviceType(self, expName: str, deviceType: str):
        """
        Gets the devices information of a specific device type

        :param expName: The experiment name
        :param deviceType: The device type
        :return: pandas.DataFrame
        """
        expId = self._getExpId(expName=expName)
        deviceTypeKey = self._getDeviceTypeKey(expName=expName, deviceType=deviceType)
        query = '''
        {
            devices (experimentId:"%s", deviceTypeKey:"%s"){
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
        return self.getTrialSets(expName=expName).query(f"name=='{trialSetName}'")['key'].values[0]

    def getTrialsByTrialSet(self, expName: str, trialSetName: str):
        """
        Gets the trials information of a specific trial set

        :param expName: The experiment name
        :param trialSetName: The trial set name
        :return: pandas.DataFrame()
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

    def _execute(self, query: str):
        """
        Executes query

        :param query: The query to execute
        :return: The query result
        """
        return self._client.execute(gql(query))
