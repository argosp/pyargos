import os
import json
import requests

from argos.thingsboard.tbEntitiesProxy import tbEntityHome
from .tb_api_client.swagger_client import ApiClient, Configuration
from .tb_api_client.swagger_client import DeviceControllerApi, AssetControllerApi, EntityRelationControllerApi, AlarmControllerApi
from .tb_api_client.swagger_client import TelemetryControllerApi

tojson = lambda x: json.loads(
    str(x).replace("None", "'None'").replace("'", '"').replace("True", "true").replace("False", "false"))


class tbHome(object):
    """
        The main home of the Thingsboard (TB or tb) objects.

        This class acts as better interface to the swagger wrapped classes (in tb_ap_client).

        It holds the Home objects of all the devices and assets
        (for now, later we will extend it to all the other objects in the TB server like rules and dashboards).

    """

    ##########
    #
    #  TB objects API.
    #
    _deviceHome = None
    _assetHome = None

    _swaggerAPI = None

    def __del__(self):
        del self._swaggerAPI
        del self._deviceHome
        del self._assetHome

    def __init__(self, connectdata=None):
        self._swaggerAPI = swaggerAPI(connectdata=connectdata)
        self._deviceHome = tbEntityHome(self._swaggerAPI, "device")
        self._assetHome = tbEntityHome(self._swaggerAPI, "asset")

    @property
    def swaggerAPI(self):
        return self._swaggerAPI

    @property
    def deviceHome(self):
        return self._deviceHome

    @property
    def assetHome(self):
        return self._assetHome

    def executeAction(self,actionJson):
        """
            Executes the required action.

              Currently, there are 2 action:

*   Add entity (device/asset):
    --------------------------

    {
        "action" : "addEntity",
        "entityType"   : "device|asset",
        "name"   : <name>,
        "type"   : <the type>
    }
    prints error if the entity exists and type != stored type.

*    Update attributes (currently update only server scope).
     -------------------------------------------------------
     {
        "action" : "updateAttributes",
        "entityType"   : "device|asset",
        "name"      : <name>,
        "attributes" : {
                <name>  : <value>
        }

     }

*    Set relationships
    --------------------------------------------------------
    {
        "action" : "addRelation",
        "entityType"   : "device|asset",
        "name"      : <name>,
        "containedin": {
            "entityType"   : "device|asset",
            "name"      : <name>,
        }
    }


    :param actionJson:
                The JSON to execute.
    :return:
        """
        getattr(self,"execute_%s"% actionJson['action'])(actionJson)

    def execute_addEntity(self,action):
        home = getattr(self,"%sHome"% action['entityType'])
        home.createProxy(action['name'],action['type'])

    def execute_updateAttributes(self,action):
        entityHome = getattr(self, "%sHome" % action['entityType'])
        entity = entityHome[action['name']]
        entity.setAttribute(action["attributes"])

    def execute_addRelation(self,action):
        toentityHome  = getattr(self, "%sHome" % action['entityType'])
        toentity      = toentityHome[action['name']]

        fromentityHome = getattr(self, "%sHome" % action["containedin"]['entityType'])
        fromentity     = fromentityHome[action["containedin"]['name']]

        fromentity.addRelation(toentity)


class swaggerAPI(object):
    """
        Holds and initializes all the swagger api.

        Connecting to the data base is done with the following structure:

         .. code-block:: json

        "login" : [<login name>,<pwd>],
        "server" : {
                "ip" : <ip>,
                "port" : <port>
        }

    """

    ##########
    #
    #   Swagger API - these will be used internally.
    #
    _api_client = None
    _AssetApi = None
    _DeviceApi = None
    _EntityRelationApi = None
    _TelemetryApi = None


    _token = None

    @property
    def token(self):
        return self._token
    
    @property
    def assetApi(self):
        return self._AssetApi

    @property
    def deviceApi(self):
        return self._DeviceApi

    @property
    def entityRelationApi(self):
        return self._EntityRelationApi

    @property
    def telemetryApi(self):
        return self._TelemetryApi

    @property
    def alarmApi(self):
        return self._AlarmApi

    def getApi(self,entityType):
        return getattr(self,"_%sApi"% entityType.title())

    def __init__(self, connectdata=None):
        """
            Initializes the swagger API

        :param connectdata:
            if connectdata is str -> read the file.
            if connectdata is None -> read the file from .pyargos/config.
            if connectdata is dictionary use it as is.

            dictionary/json structure:

            .. code-block:: json

                "login" : [<login name>,<pwd>],
                "server" : {
                        "ip" : <ip>,
                        "port" : <port>
                }

        """
        self._api_client = self._getApiClient(connectdata)
        self._AssetApi = AssetControllerApi(api_client=self._api_client)
        self._DeviceApi = DeviceControllerApi(api_client=self._api_client)
        self._EntityRelationApi = EntityRelationControllerApi(api_client=self._api_client)
        self._TelemetryApi = TelemetryControllerApi(self._api_client)
        self._AlarmApi = AlarmControllerApi(api_client=self._api_client)

    def _getApiClient(self, connectdata=None):
        """
            Gets the JWT key from the TB server and initializes an api client.

            if conf is str -> read the file.
            if conf is None -> read the file from .pyargos/config.
            if conf is dictionary use it as is.

            dictionary/json structure:

            .. code-block:: json

                "login" : {
                        "username" : <user name>,
                        "password" : <password>
                },
                "server" : {
                        "ip" : <ip>,
                        "port" : <port>
                }

            :return: api_client
        """
        if connectdata is None:
            configpath = os.path.join(os.path.expanduser("~"), ".pyargos", 'config.json')
            # load the config file.
            with open(configpath, "r") as cnfFile:
                connectdata = json.load(cnfFile)

        login = str(connectdata["login"]).replace("'", '"')  # make it a proper json.

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        token_response = requests.post('http://{ip}:{port}/api/auth/login'.format(**connectdata['server']), data=login,
                                       headers=headers)
        token = json.loads(token_response.text)

        self._token = token


        # set up the api-client.
        api_client_config = Configuration()
        api_client_config.host = '{ip}:{port}'.format(**connectdata['server'])
        api_client_config.api_key['X-Authorization'] = 'Bearer %s' % token['token']
        api_client = ApiClient(api_client_config)

        return api_client


