from .tb_api_client.swagger_client import Asset, EntityId, Device,  EntityRelation, EntityId
from .tb_api_client.swagger_client.rest import ApiException

import json

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

    def __str__(self):
        return str(self._entityData)

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


    def setAttributes(self, attributes,scope="SERVER_SCOPE"):
        """
            Update the device attributes.

        :param attributes: a dictionary of attributes to update.
        :param scope: can be with "SERVER_SCOPE" or "SHARED_SCOPE".
        :return:
        """
        self._swagger.telemetryApi.save_entity_attributes_v2_using_post(self.entityType, self.id, scope, request=attributes)

<<<<<<< HEAD
    def getAttributes(self):
=======
    def getAttributes(self, keys=None):
>>>>>>> checkRESTTB
        """
            Get all the attributes of the device.
        :param keys: string of the attributes key. i.e: 'T,id,longitude'
        :return:
            A dict with the parameters.
        """
        #data,_,_ = self._swagger.telemetryApi.get_attributes_using_get(self.entityType, self.id)
<<<<<<< HEAD
        data,_,_ = self._swagger.telemetryApi.get_attributes_using_get_with_http_info(self.entityType, self.id)
        print(data)
=======
>>>>>>> checkRESTTB

        param = {}
        if keys is not None:
            param['keys'] = keys

        data,_,_ = self._swagger.telemetryApi.get_attributes_using_get_with_http_info(self.entityType, self.id,_preload_content=False, **param)
        #print(data.data.to_dict())
        attrDict = {}
        for attr in json.loads(data.data):
            attrDict[attr['key']] = attr['value']

        return attrDict


    def delAttributes(self,attributeName,scope="SERVER_SCOPE"):
        self._swagger.telemetryApi.delete_entity_attributes_using_delete1_with_http_info(self.entityType, self.id,scope=scope,keys=attributeName)

    def __setitem__(self, key, value):
        """
            Setting a SERVER_SCOPE attribute.

        :param key:
        :param value:
        :return:
        """
        self.setAttributes({key:value},scope="SERVER_SCOPE")

    def addRelation(self,entity):
        from_id = EntityId(entity_type=self.entityType, id=self.id)
        to_id = EntityId(entity_type=entity.entityType, id=entity.id)
        new_relation = EntityRelation(_from=from_id, to=to_id, type='Contains', type_group='COMMON')
        self._swagger.entityRelationApi.save_relation_using_post(new_relation)


    def getRelations(self):
        return self._swagger.entityRelationApi.find_by_from_using_get1_with_http_info(self.id,self.entityType)

    def delRelations(self):
        relations = self.getRelations()[0]
        for relation in relations:
            relationDict = relation.to_dict()
            self._swagger.entityRelationApi.delete_relation_using_delete_with_http_info(relationDict['_from']['id'],
                                                                                        relationDict['_from']['entity_type'],
                                                                                        relationDict['type'],
                                                                                        relationDict['to']['id'],
                                                                                        relationDict['to']['entity_type'])


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

    def __init__(self, deviceData, swagger, home, **kwargs):
        super().__init__(deviceData, swagger, home, **kwargs)
        self._entityType = "ASSET"

