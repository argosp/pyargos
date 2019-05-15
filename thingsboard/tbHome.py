import os
import json
import requests
from .tb_api_client.swagger_client import ApiClient,Configuration
from .tb_api_client.swagger_client import Asset, ApiException, EntityId, Device,  EntityRelation, EntityId
from .tb_api_client.swagger_client import DeviceControllerApi, AssetControllerApi, EntityRelationControllerApi
from .tb_api_client.swagger_client.apis.telementry_controller_api import TelemetryControllerApi

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

    @property
    def deviceHome(self):
        return self._deviceHome

    @property
    def assetHome(self):
        return self._assetHome


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
    _AssetApi   = None
    _DeviceApi  = None
    _EntityRelationApi = None
    _TelemetryApi = None

    @property
    def assetApi(self):
        return self._AssetApi

    @property
    def deviceApi(self):
        return self._DeviceApi

    @property
    def enttityRelationApi(self):
        return self._EntityRelationApi

    @property
    def telemetryApi(self):
        return self._TelemetryApi


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
        self._api_client         = self._getApiClient(connectdata)
        self._AssetApi           = AssetControllerApi(api_client=self._api_client)
        self._DeviceApi          = DeviceControllerApi(api_client=self._api_client)
        self._EntityRelationApi  = EntityRelationControllerApi(api_client=self._api_client)
        self._TelemetryApi       = TelemetryControllerApi(self._api_client)


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

        #login = str(dict([(str(x[0]), str(x[1])) for x in serverAttr['login'].items()])).replace("'", '"')
        login = str(connectdata["login"]).replace("'", '"') # make it a proper json.

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        token_response = requests.post('http://{ip}:{port}/api/auth/login'.format(**connectdata['server']), data=login, headers=headers)
        token = json.loads(token_response.text)

        # set up the api-client.
        api_client_config = Configuration()
        api_client_config.host = '{ip}:{port}'.format(**connectdata['server'])
        api_client_config.api_key['X-Authorization'] = 'Bearer %s' % token['token']
        api_client = ApiClient(api_client_config)

        return api_client


class tbDeviceHome(dict):
    """
        This class manages the creation, removal and retrieving the data from the server.

        Inherits from a dictionary and holds the current instances of the
        assets in it.

        It is also a map that holds the deviceName->deviceProxy map.

    """
    _swaggerApi = None

    def __init__(self,swaggerApi):
        self._swaggerApi = swaggerApi

    def createProxy(self,deviceName,overwrite=True,**kwargs):
        """
            Creates a proxy device.

            Call modes:

            createProxy(deviceName = "NewDevice")

                    try to load deviceName from the TB server.
                    if does not exist throw exception.

            createProxy(deviceName = "NewDevice",location=32,overwrite = True)
                    Update attribute location in the device.
                    if does not exist - create (if deviceType exists else throw exception).

            createProxy(deviceName = "NewDevice",location=32,deviceType="Sonic",overwrite = False)
                    Try to create a new device and set the attributes.
                    if exists, raise exception.

            :return returns the DeviceProxy object.
        """

        # all the logic.
        newDeviceProxy = Deviceproxy(deviceName,controller=self,**kwargs)

        self[deviceName] = newDeviceProxy
        return newDeviceProxy


    def deleteDevice(self,deviceName):
        try:
            self.deviceControllerApi.delete_device_using_delete(self[deviceName].deviceId)
        except ApiException as e:
            pass



############################################################################################3
############################################################################################3
############################################################################################3
############################################################################################3
############################################################################################3
#
#
# class tbController(object):
#
#     _Assets = None
#     _Devices = None
#
#     @property
#     def Assets(self):
#         return self._Assets
#
#     @property
#     def Devices(self):
#         return self._Devices
#
#     def __init__(self, **kwargs):
#         self._Devices = {}
#         self._Assets = {}
#
#         login = '{' + '"username":"{username}", "password":"{password}"'.format(**kwargs) + '}'
#         serverCred = {'ip': kwargs['ip'], 'port': kwargs['port']}  # works
#
#         self.api_client = getApiClient({"login":login, "server": serverCred})
#         self.aca = AssetControllerApi(api_client=self.api_client)
#         self.dca = DeviceControllerApi(api_client=self.api_client)
#         self.Rel = RelationClass(self.api_client)
#         self.erc = EntityRelationControllerApi(api_client=self.api_client)
#         self.tca = TelemetryControllerApi(self.api_client)
#
#     def getDevices(self, customerid):  #works if device is assined to customer customer id must be supplied
#         """
#             doesn't work properly
#         :param customerid:
#         :return:
#         """
#         aa = self.dca.get_customer_devices_using_get(customerid, 1000)
#         return aa
#
#
#     def getTenantDevices(self, **kwargs):
#         """
#             doesn't work properly
#         :param kwargs:
#         :return:
#         """
#         # return  self.dca.getTenantDevices({'limit': '1000'})
#         return self.dca.getTenantDevices(1000)
#
#
#     def getDevice(self, devName):
#         """
#             This method returns the device instance with devName
#             params:
#                   devName : device instance to be returned
#             return values
#                 if device instance with the name devName
#                 None if devName is not exists.
#         """
#
#         for device in self.Devices:
#             if device.deviceName == devName:
#                 return device
#         return None
#
#     def getAsset(self, assetName,assetType=None):
#         """
#             This method returns the asset instance with assetName
#             params:
#                   assetName : asste name to be returned
#             return values
#                 if asset instance with the name assetName
#                 None if assetName is not exists.
#         """
#         if assetName in self.Assets:
#             return self.Assets[assetName]
#         else:
#
#
#             if assetType is None:
#                 raise ValueError("Asst %s is not found!. Must supply asset type")
#
#
#         for asset in self.Assets:
#             if asset.assetName == assetName:
#                 return asset
#         return None
#
#
#     def addDevice(self, devName, devType):
#         """
#             adding device to thingboard
#             params:
#                 devName: Device name to be add
#                 devType: device type
#             if devName exists in thingsboard this methos will do nothing
#             return value
#                 this method does not return any value
#         """
#         if devName in self.Devices:
#             dev = DeviceClass(self.dca, devName, devType, self.tca)
#             self.Devices.append(dev)
#
#     def removeDevice(self, devName):
#         """
#                 remove device from thingboard
#                 params:
#                     devName: Device name to be add
#                 if devName exists, the device will be removed from thingboard data base
#                 return value
#                     this method does not return any value
#         """
#         try:
#             self.getDevice(devName).safeDeleteDevice()
#             self.Devices.remove(devName)
#         except:
#             return
#
#
#     def addAsset(self, assetName, assetType):
#         if assetName in self.Assets:
#             asset = AssetClass(self.aca, assetName, assetType, self.tca, self.erc )
#             self.Assets.append(asset)
#
#     def removeAsset(self, assetName):
#         try:
#             self.getAsset(assetName).safeDeleteAsset()
#             self.Assets.remove(assetName)
#         except:
#             return
#
#
#     def getCredential(self, devName):
#         try:
#             self.getDevice(devName).getCredentials()
#         except:
#             return ''
#
#
#
