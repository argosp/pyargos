import os
import json
import requests
from .tb_api_client.swagger_client import ApiClient, Configuration
from .tb_api_client.swagger_client import Asset, ApiException, EntityId, Device, EntityRelation, EntityId
from .tb_api_client.swagger_client import DeviceControllerApi, AssetControllerApi, EntityRelationControllerApi
from .tb_api_client.swagger_client.apis.telementry_controller_api import TelemetryControllerApi

from .tbEntitiesProxy import DeviceProxy, AssetProxy

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

    def __init__(self, connectdata=None):
        self._swaggerAPI = swaggerAPI(connectdata=connectdata)
        self._deviceHome = tbEntityHome(self._swaggerAPI, "device")
        self._assetHome = tbEntityHome(self._swaggerAPI, "asset")

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

        # set up the api-client.
        api_client_config = Configuration()
        api_client_config.host = '{ip}:{port}'.format(**connectdata['server'])
        api_client_config.api_key['X-Authorization'] = 'Bearer %s' % token['token']
        api_client = ApiClient(api_client_config)

        return api_client


class tbEntityHome(dict):
    """
        This class manages the creation, removal and retrieving of an entity (ASSET or DEVICE for now) from the server.
        The design pattern is a thin proxy. so that the proxy does not cache. Thincker clients can be
        implemented in the future if necessary.

        Inherits from a dictionary and holds the current instances of the entity proxy.
    """
    _swagger = None

    _entityType = None
    _entityApi = None
    _entityProxy = None

    def __init__(self, iswaggerApi, entityType):
        """
            Initializes the Home.

        :param iswaggerApi:
                the swagger wrapper with all the api initialized and after authentication with the server.
        :param entityType:
                asset or device.
        """
        proxyClass = {"asset": AssetProxy, "device": DeviceProxy}
        objClass = {"asset": Asset, "device": Device}

        self._entityType = entityType.lower()
        self._swagger = iswaggerApi
        self._entityApi = iswaggerApi.getApi(self._entityType)
        self._entityProxy = proxyClass[self._entityType]
        self._entityObj = objClass[self._entityType]

    def createProxy(self, entityName, entityType=None):
        """
            Creates a proxy entity.

            Call modes:

            createProxy(entityName = "NewDevice")

                    Create a proxy for the entity NewDevice.
                    if does not exist raise exception.

            createProxy(entityName = "NewDevice",entityType="blah")
                    Create a proxy for the entity NewDevice.
                    if does not exist - create.
                    if exists and type mismatch the entityType - raise exception.

            :return returns the proxy object of the entity according to the home type.
        """

        entityData = self.getEntity(entityName)

        if entityType is None:
            # kwargs is not emtpy.
            if entityData is not None:
                newEntityProxy = self._entityProxy(entityData, swagger=self._swagger, home=self)
            else:
                raise ValueError("Device %s does not exist" % entityName)

        else:
            if entityData is None:
                newentity = self._entityObj(name=entityName, type=entityType)
                saveFunc = getattr(self._entityApi, "save_%s_using_post" % self._entityType)
                saveFunc(newentity)
                newEntityProxy = self._entityProxy(self.getEntity(entityName), swagger=self._swagger, home=self)
            else:
                if entityData["type"] != entityType:
                    raise ValueError(
                        "Cannot create Proxy. The type of %s mismatch. The device type in Thingsboard is %s while requested type is %s " % (
                        entityName, entityData["type"], entityType))
                newEntityProxy = self._entityProxy(entityData, swagger=self._swagger, home=self)

        self[entityName] = newEntityProxy
        return newEntityProxy



    def getEntity(self, entityName):
        """
            Gets the device data from the TB server.


        :param entityName: The name of the device.

        :return:
                return a dict:

                .. code-block:: json

                {
                 'additional_info': <..>,
                 'created_time': <timestamp>,
                 'customer_id': {'id': <str> },
                 'id': {'id': <str>},
                 'name': <str>,
                 'tenant_id': {'id': <str>},
                 'type': <str>
                }

                if device exists, False otherwise.
        """
        entityfuncmapping = {"asset":"assets"}
        ret = None
        if self._entityType =="device":
            try:
                entitytype = entityfuncmapping.get(self._entityType, self._entityType)
                getFunc = getattr(self._entityApi, "get_tenant_%s_using_get_with_http_info" % entitytype)
                data, _, _ = getFunc(entityName)
                ret = tojson(data)
            except ApiException as e:
                if json.loads(e.body)['errorCode'] != 32:
                    raise e
        else:
            # This is an ugly workaround since the tb_api_client is old.
            # TODO: Lior, if you know how to generate a new one from the existing API it would
            #       make life simpler...
            data,_,_ = self._entityApi.get_tenant_assets_using_get_with_http_info(100)
            assetlist = tojson(data)['data']
            ret = [x for x in assetlist if x['name'] ==entityName]
            ret = ret[0] if len(ret)>0 else None

        return ret

    def exists(self, entityName):
        """
            Checks if the device exists in the TB server.

        :param entityName: The name of the device.

        :return: True if device exists, false otherwise.
        """
        return False if self.get(entityName) is None else True

    def delete(self, entityName):
        try:

            deleteFunc = getattr(self._entityApi, "delete_%s_using_delete" % self._entityType)
            deleteFunc(self[entityName].id)
        except ApiException as e:
            pass

    def __getitem__(self, item):
        if item not in self:
            ret = self.createProxy(item)
        else:
            ret = self.get(item)
        return ret
