from .tb_api_client.swagger_client import Asset, ApiException, EntityId, Device,  EntityRelation, EntityId
import json
tojson = lambda x: json.loads(str(x).replace("None", "'None'").replace("'", '"').replace("True", "true").replace("False", "false"))

class AbstractProxy(object):
    _entityData = None

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


    def setAttribute(self, attributes,scope="SERVER_SCOPE"):
        """
            Update the device attributes.

        :param attributes: a dictionary of attributes to update.
        :param scope: can be with "SERVER_SCOPE" or "SHARED_SCOPE".
        :return:
        """
        self._swagger.deviceApi.tca.save_entity_attributesV2(self.type, self.id, scope, attributes)

    def getAttribute(self,name):
        raise NotImplementedError("TODO")

    def publishTelemetry(self,**kwargs):
        raise NotImplementedError("TODO")


    def __setitem__(self, key, value):
        """
            Setting a SERVER_SCOPE attribute.

        :param key:
        :param value:
        :return:
        """
        self.setAttribute(key,value,scope="SERVER_SCOPE")

    def __getitem__(self, item):
        return self.getAttribute(item)


class DeviceProxy(AbstractProxy):
    """
        A proxy of the device in the TB server.

        can be initialized in 2 ways:

            1. A list of key-value.
            2. by device name gets the device data from the server.

    """

    def __init__(self, deviceName, swagger,home, **kwargs):
        super().__init__(deviceName, swagger,home, **kwargs)


class AssetProxy(AbstractProxy):

    def __init__(self, deviceData, controller, **kwargs):
        super().__init__(deviceData, controller, **kwargs)



    def addRelation(self,entity):
        if isinstance(entity,DeviceProxy):
            pass
        else:
            # this is asset.
            pass