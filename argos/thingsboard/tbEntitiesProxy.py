from argos.thingsboard.tb_api_client.swagger_client import Asset, Device
from argos.thingsboard.tb_api_client.swagger_client.rest import ApiException
from .tb_api_client.swagger_client import Asset, EntityId, Device,  EntityRelation, EntityId
from .tb_api_client.swagger_client.rest import ApiException

from ..noSQLdask import CassandraBag

import pandas
import json

class AbstractProxy:
    """
        Abstract Proxy.

        Implements the setting and getting of the attributes.

    """
    _entityData = None
    _entityType = None # DEVICE or ASSET

    _swagger = None
    _home    = None

    _AlarmsData = None

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

    def getAttributes(self, keys=None):
        """
            Get all the attributes of the device.
        :param keys: string of the attributes key. i.e: 'T,id,longitude'
        :return:
            A dict with the parameters.
        """
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

    def getAlarms(self, limit=10000):
        if self._AlarmsData is None:
            data = self._swagger.alarmApi.get_alarms_using_get_with_http_info(entity_type=self.entityType, entity_id=self.id, limit=limit, fetch_originator=True)[0].to_dict()['data']
            data = pandas.DataFrame(data)
            self._AlarmsData = data
        else:
            data = self._AlarmsData

        return data


class DeviceProxy(AbstractProxy):
    """
        A proxy of the device in the TB server.
    """

    _telemetry = None

    def __init__(self, deviceData, swagger, home, **kwargs):
        super().__init__(deviceData, swagger, home, **kwargs)
        self._entityType = "DEVICE"
        self._telemetry  = {}

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

    def getTelemetry(self, start_time, end_time, partitions=10, IP='127.0.0.1', db_name='thingsboard', set_name='ts_kv_cf'):

        if (start_time,end_time) in self._telemetry:
            df = self._telemetry[(start_time,end_time)]
        else:
            cdb = CassandraBag(deviceID=self.id, IP=IP, db_name=db_name, set_name=set_name)
            bg = cdb.bag(start_time, end_time, partitions)
            meta = {'ts': int, 'key': str, 'dbl_v': float}
            bgDataFrame = bg.to_dataframe(meta=meta)
            df = bgDataFrame.compute().pivot_table(index='ts', columns='key', values='dbl_v')
            df.index = [pandas.Timestamp.fromtimestamp(x / 1000.0) for x in df.index]
            self._telemetry[(start_time,end_time)] = df

        return df


class AssetProxy(AbstractProxy):

    def __init__(self, deviceData, swagger, home, **kwargs):
        super().__init__(deviceData, swagger, home, **kwargs)
        self._entityType = "ASSET"


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
        ret = None
        try:
            getFunc = getattr(self._entityApi, "get_tenant_%s_using_get_with_http_info" % self._entityType)
            data, _, _ = getFunc(entityName)
            ret = data.to_dict()
        except ApiException as e:
            if json.loads(e.body)['errorCode'] != 32:
                raise e

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
            del self[entityName]
        except ApiException as e:
            pass

    def getAllEntitiesName(self, limit=10000):
        ret = None
        try:
            getFunc = getattr(self._entityApi, "get_tenant_%ss_using_get_with_http_info" % self._entityType)
            data, _, _ = getFunc(limit)
            ret = data.to_dict()['data']
            #ret = list(map(lambda x: x['name'], ret))
            ret = [x['name'] for x in ret]
        except ApiException as e:
            if json.loads(e.body)['errorCode'] != 32:
                raise e

        return ret

    def getAllEntitiesNameByType(self, type, limit=10000):
        ret = None
        try:
            getFunc = getattr(self._entityApi, "get_tenant_%ss_using_get_with_http_info" % self._entityType)
            data, _, _ = getFunc(limit)
            ret = data.to_dict()['data']
            ret = [x['name'] for x in ret if x['type']==type]
        except ApiException as e:
            if json.loads(e.body)['errorCode'] != 32:
                raise e

        return ret

    def deleteAllEntities(self):
        entitiesName = self.getAllEntitiesName(limit=10000)
        for entityName in entitiesName:
            self.delete(entityName)

    def __getitem__(self, item):
        if item not in self:
            ret = self.createProxy(item)
        else:
            ret = self.get(item)
        return ret