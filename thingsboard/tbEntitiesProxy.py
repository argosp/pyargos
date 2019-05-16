from .tb_api_client.swagger_client import Asset, ApiException, EntityId, Device,  EntityRelation, EntityId
import json
tojson = lambda x: json.loads(str(x).replace("None", "'None'").replace("'", '"').replace("True", "true").replace("False", "false"))

class AbstractProxy(object):
    """
        Abstract Proxy.

        Implements the setting and getting of the attributes.

    """
    _entityData = None
    _entityType = None # DEVICE or ASSET

    _swagger = None
    _home    = None

    @property
    def deviceType(self):
        return self._DeviceType

    @property
    def id(self):
        return self._entityData["id"]["id"]

    @property
    def type(self):
        return self._entityData["type"]

    @property
    def entityType(self):
        return self._entityType

    @property
    def name(self):
        return self._entityData["name"]

    @property
    def tenant(self):
        return self._entityData["tenant"]["id"]

    @property
    def additional_info(self):
        return self._entityData["additional_info"]

    def __init__(self, entityData,swagger,home):
        """
            Initializes a new proxy device.

            if kwargs is empty:
                Load the device id from the TB server.

        :param deviceName:
        :param controller:
        :param kwargs:  list of device attributes.
        """

        self._entityData = entityData

        self._swagger = swagger
        self._home    = home


    def setAttribute(self, attributes,scope="SERVER_SCOPE"):
        """
            Update the device attributes.

        :param attributes: a dictionary of attributes to update.
        :param scope: can be with "SERVER_SCOPE" or "SHARED_SCOPE".
        :return:
        """
        self._swagger.telemetryApi.save_entity_attributesV2(self.entityType, self.id, scope, attributes)

    def getAttributes(self,scope=None):
        """
            This doesn't work right now.
            The problem is that I wrote the Telemetry controller and maybe there is a mistake there.
            we should try to call the swagger from the CLI...

            Get all the attributes of the device.
        :param scope: can be None (for all scopes) or "SERVER_SCOPE" or "SHARED_SCOPE" or "CLIENT_SCOPE"
        :return:
            A dict with the parameters.
        """
        data,_,_ = self._swagger.telemetryApi.get_attributes(self.entityType, self.id, scope)
        return data["result"]



    def __setitem__(self, key, value):
        """
            Setting a SERVER_SCOPE attribute.

        :param key:
        :param value:
        :return:
        """
        self.setAttribute({key:value},scope="SERVER_SCOPE")



class DeviceProxy(AbstractProxy):
    """
        A proxy of the device in the TB server.
    """

    def __init__(self, deviceData, swagger, home, **kwargs):
        super().__init__(deviceData, swagger, home, **kwargs)
        self._entityType = "DEVICE"

    def getCredentials(self):
        """
                Get the credentials of the device.
        :return:  str
        """
        try:
            retval = self._swagger.deviceApi.get_device_credentials_by_device_id_using_get(self.id)
            return retval.credentials_id
        except ApiException as e:
            return []


class AssetProxy(AbstractProxy):

    def __init__(self, assetData, controller, **kwargs):
        super().__init__(assetData, controller, **kwargs)
        self._entityType = "RELATION"

    def addRelation(self,entity):
        if isinstance(entity,DeviceProxy):
            pass
        else:
            # this is asset.
            pass