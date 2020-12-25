# swagger_client.TelemetryControllerApi

All URIs are relative to *https://127.0.0.1:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_entity_attributes_using_delete**](TelemetryControllerApi.md#delete_entity_attributes_using_delete) | **DELETE** /api/plugins/telemetry/{deviceId}/{scope}{?keys} | deleteEntityAttributes
[**delete_entity_attributes_using_delete1**](TelemetryControllerApi.md#delete_entity_attributes_using_delete1) | **DELETE** /api/plugins/telemetry/{entityType}/{entityId}/{scope}{?keys} | deleteEntityAttributes
[**delete_entity_timeseries_using_delete**](TelemetryControllerApi.md#delete_entity_timeseries_using_delete) | **DELETE** /api/plugins/telemetry/{entityType}/{entityId}/timeseries/delete{?keys,deleteAllDataForKeys,startTs,endTs,rewriteLatestIfDeleted} | deleteEntityTimeseries
[**get_attribute_keys_by_scope_using_get**](TelemetryControllerApi.md#get_attribute_keys_by_scope_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/keys/attributes/{scope} | getAttributeKeysByScope
[**get_attribute_keys_using_get**](TelemetryControllerApi.md#get_attribute_keys_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/keys/attributes | getAttributeKeys
[**get_attributes_by_scope_using_get**](TelemetryControllerApi.md#get_attributes_by_scope_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/attributes/{scope}{?keys} | getAttributesByScope
[**get_attributes_using_get**](TelemetryControllerApi.md#get_attributes_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/attributes{?keys} | getAttributes
[**get_latest_timeseries_using_get**](TelemetryControllerApi.md#get_latest_timeseries_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/timeseries{?keys} | getLatestTimeseries
[**get_timeseries_keys_using_get**](TelemetryControllerApi.md#get_timeseries_keys_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/keys/timeseries | getTimeseriesKeys
[**get_timeseries_using_get**](TelemetryControllerApi.md#get_timeseries_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/timeseries{?interval,limit,agg,keys,startTs,endTs} | getTimeseries
[**save_device_attributes_using_post**](TelemetryControllerApi.md#save_device_attributes_using_post) | **POST** /api/plugins/telemetry/{deviceId}/{scope} | saveDeviceAttributes
[**save_entity_attributes_v1_using_post**](TelemetryControllerApi.md#save_entity_attributes_v1_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/{scope} | saveEntityAttributesV1
[**save_entity_attributes_v2_using_post**](TelemetryControllerApi.md#save_entity_attributes_v2_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/attributes/{scope} | saveEntityAttributesV2
[**save_entity_telemetry_using_post**](TelemetryControllerApi.md#save_entity_telemetry_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/timeseries/{scope} | saveEntityTelemetry
[**save_entity_telemetry_with_ttl_using_post**](TelemetryControllerApi.md#save_entity_telemetry_with_ttl_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/timeseries/{scope}/{ttl} | saveEntityTelemetryWithTTL


# **delete_entity_attributes_using_delete**
> DeferredResultResponseEntity delete_entity_attributes_using_delete(device_id, scope, keys)

deleteEntityAttributes

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
device_id = 'device_id_example' # str | deviceId
scope = 'scope_example' # str | scope
keys = 'keys_example' # str | keys

try:
    # deleteEntityAttributes
    api_response = api_instance.delete_entity_attributes_using_delete(device_id, scope, keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->delete_entity_attributes_using_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| deviceId | 
 **scope** | **str**| scope | 
 **keys** | **str**| keys | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_entity_attributes_using_delete1**
> DeferredResultResponseEntity delete_entity_attributes_using_delete1(entity_type, entity_id, scope, keys)

deleteEntityAttributes

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope
keys = 'keys_example' # str | keys

try:
    # deleteEntityAttributes
    api_response = api_instance.delete_entity_attributes_using_delete1(entity_type, entity_id, scope, keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->delete_entity_attributes_using_delete1: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 
 **keys** | **str**| keys | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_entity_timeseries_using_delete**
> DeferredResultResponseEntity delete_entity_timeseries_using_delete(entity_type, entity_id, keys, delete_all_data_for_keys=delete_all_data_for_keys, start_ts=start_ts, end_ts=end_ts, rewrite_latest_if_deleted=rewrite_latest_if_deleted)

deleteEntityTimeseries

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
keys = 'keys_example' # str | keys
delete_all_data_for_keys = false # bool | deleteAllDataForKeys (optional) (default to false)
start_ts = 789 # int | startTs (optional)
end_ts = 789 # int | endTs (optional)
rewrite_latest_if_deleted = false # bool | rewriteLatestIfDeleted (optional) (default to false)

try:
    # deleteEntityTimeseries
    api_response = api_instance.delete_entity_timeseries_using_delete(entity_type, entity_id, keys, delete_all_data_for_keys=delete_all_data_for_keys, start_ts=start_ts, end_ts=end_ts, rewrite_latest_if_deleted=rewrite_latest_if_deleted)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->delete_entity_timeseries_using_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **keys** | **str**| keys | 
 **delete_all_data_for_keys** | **bool**| deleteAllDataForKeys | [optional] [default to false]
 **start_ts** | **int**| startTs | [optional] 
 **end_ts** | **int**| endTs | [optional] 
 **rewrite_latest_if_deleted** | **bool**| rewriteLatestIfDeleted | [optional] [default to false]

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_attribute_keys_by_scope_using_get**
> DeferredResultResponseEntity get_attribute_keys_by_scope_using_get(entity_type, entity_id, scope)

getAttributeKeysByScope

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope

try:
    # getAttributeKeysByScope
    api_response = api_instance.get_attribute_keys_by_scope_using_get(entity_type, entity_id, scope)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_attribute_keys_by_scope_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_attribute_keys_using_get**
> DeferredResultResponseEntity get_attribute_keys_using_get(entity_type, entity_id)

getAttributeKeys

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId

try:
    # getAttributeKeys
    api_response = api_instance.get_attribute_keys_using_get(entity_type, entity_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_attribute_keys_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_attributes_by_scope_using_get**
> DeferredResultResponseEntity get_attributes_by_scope_using_get(entity_type, entity_id, scope, keys=keys)

getAttributesByScope

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope
keys = 'keys_example' # str | keys (optional)

try:
    # getAttributesByScope
    api_response = api_instance.get_attributes_by_scope_using_get(entity_type, entity_id, scope, keys=keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_attributes_by_scope_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 
 **keys** | **str**| keys | [optional] 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_attributes_using_get**
> DeferredResultResponseEntity get_attributes_using_get(entity_type, entity_id, keys=keys)

getAttributes

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
keys = 'keys_example' # str | keys (optional)

try:
    # getAttributes
    api_response = api_instance.get_attributes_using_get(entity_type, entity_id, keys=keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_attributes_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **keys** | **str**| keys | [optional] 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_latest_timeseries_using_get**
> DeferredResultResponseEntity get_latest_timeseries_using_get(entity_type, entity_id, keys=keys)

getLatestTimeseries

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
keys = 'keys_example' # str | keys (optional)

try:
    # getLatestTimeseries
    api_response = api_instance.get_latest_timeseries_using_get(entity_type, entity_id, keys=keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_latest_timeseries_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **keys** | **str**| keys | [optional] 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_timeseries_keys_using_get**
> DeferredResultResponseEntity get_timeseries_keys_using_get(entity_type, entity_id)

getTimeseriesKeys

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId

try:
    # getTimeseriesKeys
    api_response = api_instance.get_timeseries_keys_using_get(entity_type, entity_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_timeseries_keys_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_timeseries_using_get**
> DeferredResultResponseEntity get_timeseries_using_get(entity_type, entity_id, keys, start_ts, end_ts, interval=interval, limit=limit, agg=agg)

getTimeseries

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
keys = 'keys_example' # str | keys
start_ts = 'start_ts_example' # str | startTs
end_ts = 'end_ts_example' # str | endTs
interval = 0 # int | interval (optional) (default to 0)
limit = 100 # int | limit (optional) (default to 100)
agg = 'NONE' # str | agg (optional) (default to NONE)

try:
    # getTimeseries
    api_response = api_instance.get_timeseries_using_get(entity_type, entity_id, keys, start_ts, end_ts, interval=interval, limit=limit, agg=agg)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->get_timeseries_using_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **keys** | **str**| keys | 
 **start_ts** | **str**| startTs | 
 **end_ts** | **str**| endTs | 
 **interval** | **int**| interval | [optional] [default to 0]
 **limit** | **int**| limit | [optional] [default to 100]
 **agg** | **str**| agg | [optional] [default to NONE]

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_device_attributes_using_post**
> DeferredResultResponseEntity save_device_attributes_using_post(device_id, scope, request)

saveDeviceAttributes

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
device_id = 'device_id_example' # str | deviceId
scope = 'scope_example' # str | scope
request = 'request_example' # str | request

try:
    # saveDeviceAttributes
    api_response = api_instance.save_device_attributes_using_post(device_id, scope, request)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->save_device_attributes_using_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| deviceId | 
 **scope** | **str**| scope | 
 **request** | **str**| request | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_entity_attributes_v1_using_post**
> DeferredResultResponseEntity save_entity_attributes_v1_using_post(entity_type, entity_id, scope, request)

saveEntityAttributesV1

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope
request = 'request_example' # str | request

try:
    # saveEntityAttributesV1
    api_response = api_instance.save_entity_attributes_v1_using_post(entity_type, entity_id, scope, request)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->save_entity_attributes_v1_using_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 
 **request** | **str**| request | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_entity_attributes_v2_using_post**
> DeferredResultResponseEntity save_entity_attributes_v2_using_post(entity_type, entity_id, scope, request)

saveEntityAttributesV2

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope
request = 'request_example' # str | request

try:
    # saveEntityAttributesV2
    api_response = api_instance.save_entity_attributes_v2_using_post(entity_type, entity_id, scope, request)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->save_entity_attributes_v2_using_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 
 **request** | **str**| request | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_entity_telemetry_using_post**
> DeferredResultResponseEntity save_entity_telemetry_using_post(entity_type, entity_id, scope, request_body)

saveEntityTelemetry

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope
request_body = 'request_body_example' # str | requestBody

try:
    # saveEntityTelemetry
    api_response = api_instance.save_entity_telemetry_using_post(entity_type, entity_id, scope, request_body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->save_entity_telemetry_using_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 
 **request_body** | **str**| requestBody | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_entity_telemetry_with_ttl_using_post**
> DeferredResultResponseEntity save_entity_telemetry_with_ttl_using_post(entity_type, entity_id, scope, ttl, request_body)

saveEntityTelemetryWithTTL

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
configuration = swagger_client.Configuration()
configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.TelemetryControllerApi(swagger_client.ApiClient(configuration))
entity_type = 'entity_type_example' # str | entityType
entity_id = 'entity_id_example' # str | entityId
scope = 'scope_example' # str | scope
ttl = 789 # int | ttl
request_body = 'request_body_example' # str | requestBody

try:
    # saveEntityTelemetryWithTTL
    api_response = api_instance.save_entity_telemetry_with_ttl_using_post(entity_type, entity_id, scope, ttl, request_body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TelemetryControllerApi->save_entity_telemetry_with_ttl_using_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_type** | **str**| entityType | 
 **entity_id** | **str**| entityId | 
 **scope** | **str**| scope | 
 **ttl** | **int**| ttl | 
 **request_body** | **str**| requestBody | 

### Return type

[**DeferredResultResponseEntity**](DeferredResultResponseEntity.md)

### Authorization

[X-Authorization](../README.md#X-Authorization)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

