from pyargos import ApiException, Device

import json

tojson = lambda x: json.loads(
    str(x).replace("None", "'None'").replace("'", '"').replace("True", "true").replace("False", "false"))


class AbstractProxy(object):
    _DeviceType = None

    @property
    def deviceType(self):
        return self._DeviceType

    def __init__(self, deviceName,controller,**kwargs):
        """
            Initializes a new proxy device.

            if kwargs is empty:
                Load the device id from the TB server.



        :param deviceName:
        :param controller:
        :param kwargs:
        """
        self.deviceName = deviceName

    def getCredentials(self):
        """
                Get the credentials of the device.
        :return:  str
        """
        try:
            retval = self.controller.dca.get_device_credentials_by_device_id_using_get(self.deviceid)
            return retval.credentials_id
        except ApiException as e:
            return []

    @property
    def deviceId(self):
        return self.deviceid

    def setAttribute(self, attributes,scope="SERVER_SCOPE"):
        """
            Update the device attributes.

        :param attributes: a dictionary of attributes to update.
        :param scope: can be with "SERVER_SCOPE" or "SHARED_SCOPE".
        :return:
        """
        self.controller.tca.save_entity_attributesV2(self.deviceType, self.deviceid, scope, attributes)

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

    def __init__(self, deviceName, controller, **kwargs):
        super().__init__(deviceName, controller, **kwargs)
        self._DeviceType = "DEVICE"


        ## All the logic of the creation.

        # try:
        #     data, resp, header = self.deviceControllerApi.get_tenant_device_using_get_with_http_info(deviceName)
        #     print('Device {} added to TB'.format(deviceName))
        #     self.deviceid = data.id._id
        # except ApiException as e:
        #     if '404' in str(e):
        #         if deviceType == '':
        #             raise "Can't add device name {}".format(deviceName)
        #         else:
        #             newdevice = Device(name = deviceName, type = self.deviceType)
        #             self.deviceControllerApi.save_device_using_post(newdevice)
        #             data, resp, header = self.deviceControllerApi.get_tenant_device_using_get_with_http_info(deviceName)
        #             self.deviceid = data.id._id
        #             print("{} added to TB...".format(deviceName))
        #             return



class AssetProxy(AbstractProxy):

    def __init__(self, deviceName, controller, **kwargs):
        super().__init__(deviceName, controller, **kwargs)
        self._DeviceType = "DEVICE"


    def addRelation(self,entity):
        if isinstance(entity,DeviceProxy):
            pass
        else:
            # this is asset.
