# swagger-client
For instructions how to authorize requests please visit <a href='http://thingsboard.io/docs/reference/rest-api/'>REST API documentation page</a>.

This Python package is automatically generated by the [Swagger Codegen](https://github.com/swagger-api/swagger-codegen) project:

- API version: 2.0
- Package version: 1.0.0
- Build package: io.swagger.codegen.languages.PythonClientCodegen
For more information, please visit [http://thingsboard.io](http://thingsboard.io)

## Requirements.

Python 2.7 and 3.4+

## Installation & Usage
### pip install

If the python package is hosted on Github, you can install directly from Github

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import swagger_client 
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import swagger_client
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: X-Authorization
swagger_client.configuration.api_key['X-Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['X-Authorization'] = 'Bearer'
# create an instance of the API class
api_instance = swagger_client.AdminControllerApi()

try:
    # checkUpdates
    api_response = api_instance.check_updates_using_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AdminControllerApi->check_updates_using_get: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://127.0.0.1:8080*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AdminControllerApi* | [**check_updates_using_get**](docs/AdminControllerApi.md#check_updates_using_get) | **GET** /api/admin/updates | checkUpdates
*AdminControllerApi* | [**get_admin_settings_using_get**](docs/AdminControllerApi.md#get_admin_settings_using_get) | **GET** /api/admin/settings/{key} | getAdminSettings
*AdminControllerApi* | [**save_admin_settings_using_post**](docs/AdminControllerApi.md#save_admin_settings_using_post) | **POST** /api/admin/settings | saveAdminSettings
*AdminControllerApi* | [**send_test_mail_using_post**](docs/AdminControllerApi.md#send_test_mail_using_post) | **POST** /api/admin/settings/testMail | sendTestMail
*AlarmControllerApi* | [**ack_alarm_using_post**](docs/AlarmControllerApi.md#ack_alarm_using_post) | **POST** /api/alarm/{alarmId}/ack | ackAlarm
*AlarmControllerApi* | [**clear_alarm_using_post**](docs/AlarmControllerApi.md#clear_alarm_using_post) | **POST** /api/alarm/{alarmId}/clear | clearAlarm
*AlarmControllerApi* | [**delete_alarm_using_delete**](docs/AlarmControllerApi.md#delete_alarm_using_delete) | **DELETE** /api/alarm/{alarmId} | deleteAlarm
*AlarmControllerApi* | [**get_alarm_by_id_using_get**](docs/AlarmControllerApi.md#get_alarm_by_id_using_get) | **GET** /api/alarm/{alarmId} | getAlarmById
*AlarmControllerApi* | [**get_alarm_info_by_id_using_get**](docs/AlarmControllerApi.md#get_alarm_info_by_id_using_get) | **GET** /api/alarm/info/{alarmId} | getAlarmInfoById
*AlarmControllerApi* | [**get_alarms_using_get**](docs/AlarmControllerApi.md#get_alarms_using_get) | **GET** /api/alarm/{entityType}/{entityId}{?searchStatus,status,limit,startTime,endTime,ascOrder,offset,fetchOriginator} | getAlarms
*AlarmControllerApi* | [**get_highest_alarm_severity_using_get**](docs/AlarmControllerApi.md#get_highest_alarm_severity_using_get) | **GET** /api/alarm/highestSeverity/{entityType}/{entityId}{?searchStatus,status} | getHighestAlarmSeverity
*AlarmControllerApi* | [**save_alarm_using_post**](docs/AlarmControllerApi.md#save_alarm_using_post) | **POST** /api/alarm | saveAlarm
*AssetControllerApi* | [**assign_asset_to_customer_using_post**](docs/AssetControllerApi.md#assign_asset_to_customer_using_post) | **POST** /api/customer/{customerId}/asset/{assetId} | assignAssetToCustomer
*AssetControllerApi* | [**assign_asset_to_public_customer_using_post**](docs/AssetControllerApi.md#assign_asset_to_public_customer_using_post) | **POST** /api/customer/public/asset/{assetId} | assignAssetToPublicCustomer
*AssetControllerApi* | [**delete_asset_using_delete**](docs/AssetControllerApi.md#delete_asset_using_delete) | **DELETE** /api/asset/{assetId} | deleteAsset
*AssetControllerApi* | [**find_by_query_using_post**](docs/AssetControllerApi.md#find_by_query_using_post) | **POST** /api/assets | findByQuery
*AssetControllerApi* | [**get_asset_by_id_using_get**](docs/AssetControllerApi.md#get_asset_by_id_using_get) | **GET** /api/asset/{assetId} | getAssetById
*AssetControllerApi* | [**get_asset_types_using_get**](docs/AssetControllerApi.md#get_asset_types_using_get) | **GET** /api/asset/types | getAssetTypes
*AssetControllerApi* | [**get_assets_by_ids_using_get**](docs/AssetControllerApi.md#get_assets_by_ids_using_get) | **GET** /api/assets{?assetIds} | getAssetsByIds
*AssetControllerApi* | [**get_customer_assets_using_get**](docs/AssetControllerApi.md#get_customer_assets_using_get) | **GET** /api/customer/{customerId}/assets{?type,textSearch,idOffset,textOffset,limit} | getCustomerAssets
*AssetControllerApi* | [**get_tenant_asset_using_get**](docs/AssetControllerApi.md#get_tenant_asset_using_get) | **GET** /api/tenant/assets{?assetName} | getTenantAsset
*AssetControllerApi* | [**get_tenant_assets_using_get**](docs/AssetControllerApi.md#get_tenant_assets_using_get) | **GET** /api/tenant/assets{?type,textSearch,idOffset,textOffset,limit} | getTenantAssets
*AssetControllerApi* | [**save_asset_using_post**](docs/AssetControllerApi.md#save_asset_using_post) | **POST** /api/asset | saveAsset
*AssetControllerApi* | [**unassign_asset_from_customer_using_delete**](docs/AssetControllerApi.md#unassign_asset_from_customer_using_delete) | **DELETE** /api/customer/asset/{assetId} | unassignAssetFromCustomer
*AuditLogControllerApi* | [**get_audit_logs_by_customer_id_using_get**](docs/AuditLogControllerApi.md#get_audit_logs_by_customer_id_using_get) | **GET** /api/audit/logs/customer/{customerId}{?startTime,endTime,ascOrder,offset,limit} | getAuditLogsByCustomerId
*AuditLogControllerApi* | [**get_audit_logs_by_entity_id_using_get**](docs/AuditLogControllerApi.md#get_audit_logs_by_entity_id_using_get) | **GET** /api/audit/logs/entity/{entityType}/{entityId}{?startTime,endTime,ascOrder,offset,limit} | getAuditLogsByEntityId
*AuditLogControllerApi* | [**get_audit_logs_by_user_id_using_get**](docs/AuditLogControllerApi.md#get_audit_logs_by_user_id_using_get) | **GET** /api/audit/logs/user/{userId}{?startTime,endTime,ascOrder,offset,limit} | getAuditLogsByUserId
*AuditLogControllerApi* | [**get_audit_logs_using_get**](docs/AuditLogControllerApi.md#get_audit_logs_using_get) | **GET** /api/audit/logs{?startTime,endTime,ascOrder,offset,limit} | getAuditLogs
*AuthControllerApi* | [**activate_user_using_post**](docs/AuthControllerApi.md#activate_user_using_post) | **POST** /api/noauth/activate | activateUser
*AuthControllerApi* | [**change_password_using_post**](docs/AuthControllerApi.md#change_password_using_post) | **POST** /api/auth/changePassword | changePassword
*AuthControllerApi* | [**check_activate_token_using_get**](docs/AuthControllerApi.md#check_activate_token_using_get) | **GET** /api/noauth/activate{?activateToken} | checkActivateToken
*AuthControllerApi* | [**check_reset_token_using_get**](docs/AuthControllerApi.md#check_reset_token_using_get) | **GET** /api/noauth/resetPassword{?resetToken} | checkResetToken
*AuthControllerApi* | [**get_user_using_get**](docs/AuthControllerApi.md#get_user_using_get) | **GET** /api/auth/user | getUser
*AuthControllerApi* | [**request_reset_password_by_email_using_post**](docs/AuthControllerApi.md#request_reset_password_by_email_using_post) | **POST** /api/noauth/resetPasswordByEmail | requestResetPasswordByEmail
*AuthControllerApi* | [**reset_password_using_post**](docs/AuthControllerApi.md#reset_password_using_post) | **POST** /api/noauth/resetPassword | resetPassword
*ComponentDescriptorControllerApi* | [**get_component_descriptor_by_clazz_using_get**](docs/ComponentDescriptorControllerApi.md#get_component_descriptor_by_clazz_using_get) | **GET** /api/component/{componentDescriptorClazz} | getComponentDescriptorByClazz
*ComponentDescriptorControllerApi* | [**get_component_descriptors_by_type_using_get**](docs/ComponentDescriptorControllerApi.md#get_component_descriptors_by_type_using_get) | **GET** /api/components/{componentType} | getComponentDescriptorsByType
*ComponentDescriptorControllerApi* | [**get_component_descriptors_by_types_using_get**](docs/ComponentDescriptorControllerApi.md#get_component_descriptors_by_types_using_get) | **GET** /api/components{?componentTypes} | getComponentDescriptorsByTypes
*CustomerControllerApi* | [**delete_customer_using_delete**](docs/CustomerControllerApi.md#delete_customer_using_delete) | **DELETE** /api/customer/{customerId} | deleteCustomer
*CustomerControllerApi* | [**get_customer_by_id_using_get**](docs/CustomerControllerApi.md#get_customer_by_id_using_get) | **GET** /api/customer/{customerId} | getCustomerById
*CustomerControllerApi* | [**get_customer_title_by_id_using_get**](docs/CustomerControllerApi.md#get_customer_title_by_id_using_get) | **GET** /api/customer/{customerId}/title | getCustomerTitleById
*CustomerControllerApi* | [**get_customers_using_get**](docs/CustomerControllerApi.md#get_customers_using_get) | **GET** /api/customers{?textSearch,idOffset,textOffset,limit} | getCustomers
*CustomerControllerApi* | [**get_short_customer_info_by_id_using_get**](docs/CustomerControllerApi.md#get_short_customer_info_by_id_using_get) | **GET** /api/customer/{customerId}/shortInfo | getShortCustomerInfoById
*CustomerControllerApi* | [**get_tenant_customer_using_get**](docs/CustomerControllerApi.md#get_tenant_customer_using_get) | **GET** /api/tenant/customers{?customerTitle} | getTenantCustomer
*CustomerControllerApi* | [**save_customer_using_post**](docs/CustomerControllerApi.md#save_customer_using_post) | **POST** /api/customer | saveCustomer
*DashboardControllerApi* | [**add_dashboard_customers_using_post**](docs/DashboardControllerApi.md#add_dashboard_customers_using_post) | **POST** /api/dashboard/{dashboardId}/customers/add | addDashboardCustomers
*DashboardControllerApi* | [**assign_dashboard_to_customer_using_post**](docs/DashboardControllerApi.md#assign_dashboard_to_customer_using_post) | **POST** /api/customer/{customerId}/dashboard/{dashboardId} | assignDashboardToCustomer
*DashboardControllerApi* | [**assign_dashboard_to_public_customer_using_post**](docs/DashboardControllerApi.md#assign_dashboard_to_public_customer_using_post) | **POST** /api/customer/public/dashboard/{dashboardId} | assignDashboardToPublicCustomer
*DashboardControllerApi* | [**delete_dashboard_using_delete**](docs/DashboardControllerApi.md#delete_dashboard_using_delete) | **DELETE** /api/dashboard/{dashboardId} | deleteDashboard
*DashboardControllerApi* | [**get_customer_dashboards_using_get**](docs/DashboardControllerApi.md#get_customer_dashboards_using_get) | **GET** /api/customer/{customerId}/dashboards{?startTime,endTime,ascOrder,offset,limit} | getCustomerDashboards
*DashboardControllerApi* | [**get_dashboard_by_id_using_get**](docs/DashboardControllerApi.md#get_dashboard_by_id_using_get) | **GET** /api/dashboard/{dashboardId} | getDashboardById
*DashboardControllerApi* | [**get_dashboard_info_by_id_using_get**](docs/DashboardControllerApi.md#get_dashboard_info_by_id_using_get) | **GET** /api/dashboard/info/{dashboardId} | getDashboardInfoById
*DashboardControllerApi* | [**get_max_datapoints_limit_using_get**](docs/DashboardControllerApi.md#get_max_datapoints_limit_using_get) | **GET** /api/dashboard/maxDatapointsLimit | getMaxDatapointsLimit
*DashboardControllerApi* | [**get_server_time_using_get**](docs/DashboardControllerApi.md#get_server_time_using_get) | **GET** /api/dashboard/serverTime | getServerTime
*DashboardControllerApi* | [**get_tenant_dashboards_using_get**](docs/DashboardControllerApi.md#get_tenant_dashboards_using_get) | **GET** /api/tenant/dashboards{?textSearch,idOffset,textOffset,limit} | getTenantDashboards
*DashboardControllerApi* | [**get_tenant_dashboards_using_get1**](docs/DashboardControllerApi.md#get_tenant_dashboards_using_get1) | **GET** /api/tenant/{tenantId}/dashboards{?textSearch,idOffset,textOffset,limit} | getTenantDashboards
*DashboardControllerApi* | [**remove_dashboard_customers_using_post**](docs/DashboardControllerApi.md#remove_dashboard_customers_using_post) | **POST** /api/dashboard/{dashboardId}/customers/remove | removeDashboardCustomers
*DashboardControllerApi* | [**save_dashboard_using_post**](docs/DashboardControllerApi.md#save_dashboard_using_post) | **POST** /api/dashboard | saveDashboard
*DashboardControllerApi* | [**unassign_dashboard_from_customer_using_delete**](docs/DashboardControllerApi.md#unassign_dashboard_from_customer_using_delete) | **DELETE** /api/customer/{customerId}/dashboard/{dashboardId} | unassignDashboardFromCustomer
*DashboardControllerApi* | [**unassign_dashboard_from_public_customer_using_delete**](docs/DashboardControllerApi.md#unassign_dashboard_from_public_customer_using_delete) | **DELETE** /api/customer/public/dashboard/{dashboardId} | unassignDashboardFromPublicCustomer
*DashboardControllerApi* | [**update_dashboard_customers_using_post**](docs/DashboardControllerApi.md#update_dashboard_customers_using_post) | **POST** /api/dashboard/{dashboardId}/customers | updateDashboardCustomers
*DeviceApiControllerApi* | [**get_device_attributes_using_get**](docs/DeviceApiControllerApi.md#get_device_attributes_using_get) | **GET** /api/v1/{deviceToken}/attributes{?clientKeys,sharedKeys} | getDeviceAttributes
*DeviceApiControllerApi* | [**post_device_attributes_using_post**](docs/DeviceApiControllerApi.md#post_device_attributes_using_post) | **POST** /api/v1/{deviceToken}/attributes | postDeviceAttributes
*DeviceApiControllerApi* | [**post_rpc_request_using_post**](docs/DeviceApiControllerApi.md#post_rpc_request_using_post) | **POST** /api/v1/{deviceToken}/rpc | postRpcRequest
*DeviceApiControllerApi* | [**post_telemetry_using_post**](docs/DeviceApiControllerApi.md#post_telemetry_using_post) | **POST** /api/v1/{deviceToken}/telemetry | postTelemetry
*DeviceApiControllerApi* | [**reply_to_command_using_post**](docs/DeviceApiControllerApi.md#reply_to_command_using_post) | **POST** /api/v1/{deviceToken}/rpc/{requestId} | replyToCommand
*DeviceApiControllerApi* | [**subscribe_to_attributes_using_get**](docs/DeviceApiControllerApi.md#subscribe_to_attributes_using_get) | **GET** /api/v1/{deviceToken}/attributes/updates{?timeout} | subscribeToAttributes
*DeviceApiControllerApi* | [**subscribe_to_commands_using_get**](docs/DeviceApiControllerApi.md#subscribe_to_commands_using_get) | **GET** /api/v1/{deviceToken}/rpc{?timeout} | subscribeToCommands
*DeviceControllerApi* | [**assign_device_to_customer_using_post**](docs/DeviceControllerApi.md#assign_device_to_customer_using_post) | **POST** /api/customer/{customerId}/device/{deviceId} | assignDeviceToCustomer
*DeviceControllerApi* | [**assign_device_to_public_customer_using_post**](docs/DeviceControllerApi.md#assign_device_to_public_customer_using_post) | **POST** /api/customer/public/device/{deviceId} | assignDeviceToPublicCustomer
*DeviceControllerApi* | [**delete_device_using_delete**](docs/DeviceControllerApi.md#delete_device_using_delete) | **DELETE** /api/device/{deviceId} | deleteDevice
*DeviceControllerApi* | [**find_by_query_using_post1**](docs/DeviceControllerApi.md#find_by_query_using_post1) | **POST** /api/devices | findByQuery
*DeviceControllerApi* | [**get_customer_devices_using_get**](docs/DeviceControllerApi.md#get_customer_devices_using_get) | **GET** /api/customer/{customerId}/devices{?type,textSearch,idOffset,textOffset,limit} | getCustomerDevices
*DeviceControllerApi* | [**get_device_by_id_using_get**](docs/DeviceControllerApi.md#get_device_by_id_using_get) | **GET** /api/device/{deviceId} | getDeviceById
*DeviceControllerApi* | [**get_device_credentials_by_device_id_using_get**](docs/DeviceControllerApi.md#get_device_credentials_by_device_id_using_get) | **GET** /api/device/{deviceId}/credentials | getDeviceCredentialsByDeviceId
*DeviceControllerApi* | [**get_device_types_using_get**](docs/DeviceControllerApi.md#get_device_types_using_get) | **GET** /api/device/types | getDeviceTypes
*DeviceControllerApi* | [**get_devices_by_ids_using_get**](docs/DeviceControllerApi.md#get_devices_by_ids_using_get) | **GET** /api/devices{?deviceIds} | getDevicesByIds
*DeviceControllerApi* | [**get_tenant_device_using_get**](docs/DeviceControllerApi.md#get_tenant_device_using_get) | **GET** /api/tenant/devices{?deviceName} | getTenantDevice
*DeviceControllerApi* | [**get_tenant_devices_using_get**](docs/DeviceControllerApi.md#get_tenant_devices_using_get) | **GET** /api/tenant/devices{?type,textSearch,idOffset,textOffset,limit} | getTenantDevices
*DeviceControllerApi* | [**save_device_credentials_using_post**](docs/DeviceControllerApi.md#save_device_credentials_using_post) | **POST** /api/device/credentials | saveDeviceCredentials
*DeviceControllerApi* | [**save_device_using_post**](docs/DeviceControllerApi.md#save_device_using_post) | **POST** /api/device | saveDevice
*DeviceControllerApi* | [**unassign_device_from_customer_using_delete**](docs/DeviceControllerApi.md#unassign_device_from_customer_using_delete) | **DELETE** /api/customer/device/{deviceId} | unassignDeviceFromCustomer
*EntityRelationControllerApi* | [**delete_relation_using_delete**](docs/EntityRelationControllerApi.md#delete_relation_using_delete) | **DELETE** /api/relation{?relationTypeGroup,fromId,fromType,relationType,toId,toType} | deleteRelation
*EntityRelationControllerApi* | [**delete_relations_using_delete**](docs/EntityRelationControllerApi.md#delete_relations_using_delete) | **DELETE** /api/relations{?entityId,entityType,id,type} | deleteRelations
*EntityRelationControllerApi* | [**find_by_from_using_get**](docs/EntityRelationControllerApi.md#find_by_from_using_get) | **GET** /api/relations{?relationTypeGroup,fromId,fromType,relationType} | findByFrom
*EntityRelationControllerApi* | [**find_by_from_using_get1**](docs/EntityRelationControllerApi.md#find_by_from_using_get1) | **GET** /api/relations{?relationTypeGroup,fromId,fromType} | findByFrom
*EntityRelationControllerApi* | [**find_by_query_using_post2**](docs/EntityRelationControllerApi.md#find_by_query_using_post2) | **POST** /api/relations | findByQuery
*EntityRelationControllerApi* | [**find_by_to_using_get**](docs/EntityRelationControllerApi.md#find_by_to_using_get) | **GET** /api/relations{?relationTypeGroup,toId,toType,relationType} | findByTo
*EntityRelationControllerApi* | [**find_by_to_using_get1**](docs/EntityRelationControllerApi.md#find_by_to_using_get1) | **GET** /api/relations{?relationTypeGroup,toId,toType} | findByTo
*EntityRelationControllerApi* | [**find_info_by_from_using_get**](docs/EntityRelationControllerApi.md#find_info_by_from_using_get) | **GET** /api/relations/info{?relationTypeGroup,fromId,fromType} | findInfoByFrom
*EntityRelationControllerApi* | [**find_info_by_query_using_post**](docs/EntityRelationControllerApi.md#find_info_by_query_using_post) | **POST** /api/relations/info | findInfoByQuery
*EntityRelationControllerApi* | [**find_info_by_to_using_get**](docs/EntityRelationControllerApi.md#find_info_by_to_using_get) | **GET** /api/relations/info{?relationTypeGroup,toId,toType} | findInfoByTo
*EntityRelationControllerApi* | [**get_relation_using_get**](docs/EntityRelationControllerApi.md#get_relation_using_get) | **GET** /api/relation{?relationTypeGroup,fromId,fromType,relationType,toId,toType} | getRelation
*EntityRelationControllerApi* | [**save_relation_using_post**](docs/EntityRelationControllerApi.md#save_relation_using_post) | **POST** /api/relation | saveRelation
*EntityViewControllerApi* | [**assign_entity_view_to_customer_using_post**](docs/EntityViewControllerApi.md#assign_entity_view_to_customer_using_post) | **POST** /api/customer/{customerId}/entityView/{entityViewId} | assignEntityViewToCustomer
*EntityViewControllerApi* | [**assign_entity_view_to_public_customer_using_post**](docs/EntityViewControllerApi.md#assign_entity_view_to_public_customer_using_post) | **POST** /api/customer/public/entityView/{entityViewId} | assignEntityViewToPublicCustomer
*EntityViewControllerApi* | [**delete_entity_view_using_delete**](docs/EntityViewControllerApi.md#delete_entity_view_using_delete) | **DELETE** /api/entityView/{entityViewId} | deleteEntityView
*EntityViewControllerApi* | [**find_by_query_using_post3**](docs/EntityViewControllerApi.md#find_by_query_using_post3) | **POST** /api/entityViews | findByQuery
*EntityViewControllerApi* | [**get_customer_entity_views_using_get**](docs/EntityViewControllerApi.md#get_customer_entity_views_using_get) | **GET** /api/customer/{customerId}/entityViews{?type,textSearch,idOffset,textOffset,limit} | getCustomerEntityViews
*EntityViewControllerApi* | [**get_entity_view_by_id_using_get**](docs/EntityViewControllerApi.md#get_entity_view_by_id_using_get) | **GET** /api/entityView/{entityViewId} | getEntityViewById
*EntityViewControllerApi* | [**get_entity_view_types_using_get**](docs/EntityViewControllerApi.md#get_entity_view_types_using_get) | **GET** /api/entityView/types | getEntityViewTypes
*EntityViewControllerApi* | [**get_tenant_entity_view_using_get**](docs/EntityViewControllerApi.md#get_tenant_entity_view_using_get) | **GET** /api/tenant/entityViews{?entityViewName} | getTenantEntityView
*EntityViewControllerApi* | [**get_tenant_entity_views_using_get**](docs/EntityViewControllerApi.md#get_tenant_entity_views_using_get) | **GET** /api/tenant/entityViews{?type,textSearch,idOffset,textOffset,limit} | getTenantEntityViews
*EntityViewControllerApi* | [**save_entity_view_using_post**](docs/EntityViewControllerApi.md#save_entity_view_using_post) | **POST** /api/entityView | saveEntityView
*EntityViewControllerApi* | [**unassign_entity_view_from_customer_using_delete**](docs/EntityViewControllerApi.md#unassign_entity_view_from_customer_using_delete) | **DELETE** /api/customer/entityView/{entityViewId} | unassignEntityViewFromCustomer
*EventControllerApi* | [**get_events_using_get**](docs/EventControllerApi.md#get_events_using_get) | **GET** /api/events/{entityType}/{entityId}/{eventType}{?tenantId,limit,startTime,endTime,ascOrder,offset} | getEvents
*EventControllerApi* | [**get_events_using_get1**](docs/EventControllerApi.md#get_events_using_get1) | **GET** /api/events/{entityType}/{entityId}{?tenantId,limit,startTime,endTime,ascOrder,offset} | getEvents
*RpcControllerApi* | [**handle_one_way_device_rpc_request_using_post**](docs/RpcControllerApi.md#handle_one_way_device_rpc_request_using_post) | **POST** /api/plugins/rpc/oneway/{deviceId} | handleOneWayDeviceRPCRequest
*RpcControllerApi* | [**handle_two_way_device_rpc_request_using_post**](docs/RpcControllerApi.md#handle_two_way_device_rpc_request_using_post) | **POST** /api/plugins/rpc/twoway/{deviceId} | handleTwoWayDeviceRPCRequest
*RuleChainControllerApi* | [**delete_rule_chain_using_delete**](docs/RuleChainControllerApi.md#delete_rule_chain_using_delete) | **DELETE** /api/ruleChain/{ruleChainId} | deleteRuleChain
*RuleChainControllerApi* | [**get_latest_rule_node_debug_input_using_get**](docs/RuleChainControllerApi.md#get_latest_rule_node_debug_input_using_get) | **GET** /api/ruleNode/{ruleNodeId}/debugIn | getLatestRuleNodeDebugInput
*RuleChainControllerApi* | [**get_rule_chain_by_id_using_get**](docs/RuleChainControllerApi.md#get_rule_chain_by_id_using_get) | **GET** /api/ruleChain/{ruleChainId} | getRuleChainById
*RuleChainControllerApi* | [**get_rule_chain_meta_data_using_get**](docs/RuleChainControllerApi.md#get_rule_chain_meta_data_using_get) | **GET** /api/ruleChain/{ruleChainId}/metadata | getRuleChainMetaData
*RuleChainControllerApi* | [**get_rule_chains_using_get**](docs/RuleChainControllerApi.md#get_rule_chains_using_get) | **GET** /api/ruleChains{?textSearch,idOffset,textOffset,limit} | getRuleChains
*RuleChainControllerApi* | [**save_rule_chain_meta_data_using_post**](docs/RuleChainControllerApi.md#save_rule_chain_meta_data_using_post) | **POST** /api/ruleChain/metadata | saveRuleChainMetaData
*RuleChainControllerApi* | [**save_rule_chain_using_post**](docs/RuleChainControllerApi.md#save_rule_chain_using_post) | **POST** /api/ruleChain | saveRuleChain
*RuleChainControllerApi* | [**set_root_rule_chain_using_post**](docs/RuleChainControllerApi.md#set_root_rule_chain_using_post) | **POST** /api/ruleChain/{ruleChainId}/root | setRootRuleChain
*RuleChainControllerApi* | [**test_script_using_post**](docs/RuleChainControllerApi.md#test_script_using_post) | **POST** /api/ruleChain/testScript | testScript
*TelemetryControllerApi* | [**delete_entity_attributes_using_delete**](docs/TelemetryControllerApi.md#delete_entity_attributes_using_delete) | **DELETE** /api/plugins/telemetry/{deviceId}/{scope}{?keys} | deleteEntityAttributes
*TelemetryControllerApi* | [**delete_entity_attributes_using_delete1**](docs/TelemetryControllerApi.md#delete_entity_attributes_using_delete1) | **DELETE** /api/plugins/telemetry/{entityType}/{entityId}/{scope}{?keys} | deleteEntityAttributes
*TelemetryControllerApi* | [**delete_entity_timeseries_using_delete**](docs/TelemetryControllerApi.md#delete_entity_timeseries_using_delete) | **DELETE** /api/plugins/telemetry/{entityType}/{entityId}/timeseries/delete{?keys,deleteAllDataForKeys,startTs,endTs,rewriteLatestIfDeleted} | deleteEntityTimeseries
*TelemetryControllerApi* | [**get_attribute_keys_by_scope_using_get**](docs/TelemetryControllerApi.md#get_attribute_keys_by_scope_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/keys/attributes/{scope} | getAttributeKeysByScope
*TelemetryControllerApi* | [**get_attribute_keys_using_get**](docs/TelemetryControllerApi.md#get_attribute_keys_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/keys/attributes | getAttributeKeys
*TelemetryControllerApi* | [**get_attributes_by_scope_using_get**](docs/TelemetryControllerApi.md#get_attributes_by_scope_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/attributes/{scope}{?keys} | getAttributesByScope
*TelemetryControllerApi* | [**get_attributes_using_get**](docs/TelemetryControllerApi.md#get_attributes_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/attributes{?keys} | getAttributes
*TelemetryControllerApi* | [**get_latest_timeseries_using_get**](docs/TelemetryControllerApi.md#get_latest_timeseries_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/timeseries{?keys} | getLatestTimeseries
*TelemetryControllerApi* | [**get_timeseries_keys_using_get**](docs/TelemetryControllerApi.md#get_timeseries_keys_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/keys/timeseries | getTimeseriesKeys
*TelemetryControllerApi* | [**get_timeseries_using_get**](docs/TelemetryControllerApi.md#get_timeseries_using_get) | **GET** /api/plugins/telemetry/{entityType}/{entityId}/values/timeseries{?interval,limit,agg,keys,startTs,endTs} | getTimeseries
*TelemetryControllerApi* | [**save_device_attributes_using_post**](docs/TelemetryControllerApi.md#save_device_attributes_using_post) | **POST** /api/plugins/telemetry/{deviceId}/{scope} | saveDeviceAttributes
*TelemetryControllerApi* | [**save_entity_attributes_v1_using_post**](docs/TelemetryControllerApi.md#save_entity_attributes_v1_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/{scope} | saveEntityAttributesV1
*TelemetryControllerApi* | [**save_entity_attributes_v2_using_post**](docs/TelemetryControllerApi.md#save_entity_attributes_v2_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/attributes/{scope} | saveEntityAttributesV2
*TelemetryControllerApi* | [**save_entity_telemetry_using_post**](docs/TelemetryControllerApi.md#save_entity_telemetry_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/timeseries/{scope} | saveEntityTelemetry
*TelemetryControllerApi* | [**save_entity_telemetry_with_ttl_using_post**](docs/TelemetryControllerApi.md#save_entity_telemetry_with_ttl_using_post) | **POST** /api/plugins/telemetry/{entityType}/{entityId}/timeseries/{scope}/{ttl} | saveEntityTelemetryWithTTL
*TenantControllerApi* | [**delete_tenant_using_delete**](docs/TenantControllerApi.md#delete_tenant_using_delete) | **DELETE** /api/tenant/{tenantId} | deleteTenant
*TenantControllerApi* | [**get_tenant_by_id_using_get**](docs/TenantControllerApi.md#get_tenant_by_id_using_get) | **GET** /api/tenant/{tenantId} | getTenantById
*TenantControllerApi* | [**get_tenants_using_get**](docs/TenantControllerApi.md#get_tenants_using_get) | **GET** /api/tenants{?textSearch,idOffset,textOffset,limit} | getTenants
*TenantControllerApi* | [**save_tenant_using_post**](docs/TenantControllerApi.md#save_tenant_using_post) | **POST** /api/tenant | saveTenant
*UserControllerApi* | [**delete_user_using_delete**](docs/UserControllerApi.md#delete_user_using_delete) | **DELETE** /api/user/{userId} | deleteUser
*UserControllerApi* | [**get_activation_link_using_get**](docs/UserControllerApi.md#get_activation_link_using_get) | **GET** /api/user/{userId}/activationLink | getActivationLink
*UserControllerApi* | [**get_customer_users_using_get**](docs/UserControllerApi.md#get_customer_users_using_get) | **GET** /api/customer/{customerId}/users{?textSearch,idOffset,textOffset,limit} | getCustomerUsers
*UserControllerApi* | [**get_tenant_admins_using_get**](docs/UserControllerApi.md#get_tenant_admins_using_get) | **GET** /api/tenant/{tenantId}/users{?textSearch,idOffset,textOffset,limit} | getTenantAdmins
*UserControllerApi* | [**get_user_by_id_using_get**](docs/UserControllerApi.md#get_user_by_id_using_get) | **GET** /api/user/{userId} | getUserById
*UserControllerApi* | [**get_user_token_using_get**](docs/UserControllerApi.md#get_user_token_using_get) | **GET** /api/user/{userId}/token | getUserToken
*UserControllerApi* | [**is_user_token_access_enabled_using_get**](docs/UserControllerApi.md#is_user_token_access_enabled_using_get) | **GET** /api/user/tokenAccessEnabled | isUserTokenAccessEnabled
*UserControllerApi* | [**save_user_using_post**](docs/UserControllerApi.md#save_user_using_post) | **POST** /api/user{?sendActivationMail} | saveUser
*UserControllerApi* | [**send_activation_email_using_post**](docs/UserControllerApi.md#send_activation_email_using_post) | **POST** /api/user/sendActivationMail{?email} | sendActivationEmail
*WidgetTypeControllerApi* | [**delete_widget_type_using_delete**](docs/WidgetTypeControllerApi.md#delete_widget_type_using_delete) | **DELETE** /api/widgetType/{widgetTypeId} | deleteWidgetType
*WidgetTypeControllerApi* | [**get_bundle_widget_types_using_get**](docs/WidgetTypeControllerApi.md#get_bundle_widget_types_using_get) | **GET** /api/widgetTypes{?isSystem,bundleAlias} | getBundleWidgetTypes
*WidgetTypeControllerApi* | [**get_widget_type_by_id_using_get**](docs/WidgetTypeControllerApi.md#get_widget_type_by_id_using_get) | **GET** /api/widgetType/{widgetTypeId} | getWidgetTypeById
*WidgetTypeControllerApi* | [**get_widget_type_using_get**](docs/WidgetTypeControllerApi.md#get_widget_type_using_get) | **GET** /api/widgetType{?isSystem,bundleAlias,alias} | getWidgetType
*WidgetTypeControllerApi* | [**save_widget_type_using_post**](docs/WidgetTypeControllerApi.md#save_widget_type_using_post) | **POST** /api/widgetType | saveWidgetType
*WidgetsBundleControllerApi* | [**delete_widgets_bundle_using_delete**](docs/WidgetsBundleControllerApi.md#delete_widgets_bundle_using_delete) | **DELETE** /api/widgetsBundle/{widgetsBundleId} | deleteWidgetsBundle
*WidgetsBundleControllerApi* | [**get_widgets_bundle_by_id_using_get**](docs/WidgetsBundleControllerApi.md#get_widgets_bundle_by_id_using_get) | **GET** /api/widgetsBundle/{widgetsBundleId} | getWidgetsBundleById
*WidgetsBundleControllerApi* | [**get_widgets_bundles_using_get**](docs/WidgetsBundleControllerApi.md#get_widgets_bundles_using_get) | **GET** /api/widgetsBundles{?textSearch,idOffset,textOffset,limit} | getWidgetsBundles
*WidgetsBundleControllerApi* | [**get_widgets_bundles_using_get1**](docs/WidgetsBundleControllerApi.md#get_widgets_bundles_using_get1) | **GET** /api/widgetsBundles | getWidgetsBundles
*WidgetsBundleControllerApi* | [**save_widgets_bundle_using_post**](docs/WidgetsBundleControllerApi.md#save_widgets_bundle_using_post) | **POST** /api/widgetsBundle | saveWidgetsBundle


## Documentation For Models

 - [AdminSettings](docs/AdminSettings.md)
 - [AdminSettingsId](docs/AdminSettingsId.md)
 - [Alarm](docs/Alarm.md)
 - [AlarmId](docs/AlarmId.md)
 - [AlarmInfo](docs/AlarmInfo.md)
 - [Asset](docs/Asset.md)
 - [AssetId](docs/AssetId.md)
 - [AssetSearchQuery](docs/AssetSearchQuery.md)
 - [AttributesEntityView](docs/AttributesEntityView.md)
 - [AuditLog](docs/AuditLog.md)
 - [AuditLogId](docs/AuditLogId.md)
 - [ComponentDescriptor](docs/ComponentDescriptor.md)
 - [ComponentDescriptorId](docs/ComponentDescriptorId.md)
 - [Customer](docs/Customer.md)
 - [CustomerId](docs/CustomerId.md)
 - [Dashboard](docs/Dashboard.md)
 - [DashboardId](docs/DashboardId.md)
 - [DashboardInfo](docs/DashboardInfo.md)
 - [DeferredResultResponseEntity](docs/DeferredResultResponseEntity.md)
 - [Device](docs/Device.md)
 - [DeviceCredentials](docs/DeviceCredentials.md)
 - [DeviceCredentialsId](docs/DeviceCredentialsId.md)
 - [DeviceId](docs/DeviceId.md)
 - [DeviceSearchQuery](docs/DeviceSearchQuery.md)
 - [EntityId](docs/EntityId.md)
 - [EntityRelation](docs/EntityRelation.md)
 - [EntityRelationInfo](docs/EntityRelationInfo.md)
 - [EntityRelationsQuery](docs/EntityRelationsQuery.md)
 - [EntitySubtype](docs/EntitySubtype.md)
 - [EntityTypeFilter](docs/EntityTypeFilter.md)
 - [EntityView](docs/EntityView.md)
 - [EntityViewId](docs/EntityViewId.md)
 - [EntityViewSearchQuery](docs/EntityViewSearchQuery.md)
 - [Event](docs/Event.md)
 - [EventId](docs/EventId.md)
 - [NodeConnectionInfo](docs/NodeConnectionInfo.md)
 - [RelationsSearchParameters](docs/RelationsSearchParameters.md)
 - [ResponseEntity](docs/ResponseEntity.md)
 - [RuleChain](docs/RuleChain.md)
 - [RuleChainConnectionInfo](docs/RuleChainConnectionInfo.md)
 - [RuleChainId](docs/RuleChainId.md)
 - [RuleChainMetaData](docs/RuleChainMetaData.md)
 - [RuleNode](docs/RuleNode.md)
 - [RuleNodeId](docs/RuleNodeId.md)
 - [ShortCustomerInfo](docs/ShortCustomerInfo.md)
 - [TelemetryEntityView](docs/TelemetryEntityView.md)
 - [Tenant](docs/Tenant.md)
 - [TenantId](docs/TenantId.md)
 - [TextPageDataAsset](docs/TextPageDataAsset.md)
 - [TextPageDataCustomer](docs/TextPageDataCustomer.md)
 - [TextPageDataDashboardInfo](docs/TextPageDataDashboardInfo.md)
 - [TextPageDataDevice](docs/TextPageDataDevice.md)
 - [TextPageDataEntityView](docs/TextPageDataEntityView.md)
 - [TextPageDataRuleChain](docs/TextPageDataRuleChain.md)
 - [TextPageDataTenant](docs/TextPageDataTenant.md)
 - [TextPageDataUser](docs/TextPageDataUser.md)
 - [TextPageDataWidgetsBundle](docs/TextPageDataWidgetsBundle.md)
 - [TextPageLink](docs/TextPageLink.md)
 - [TimePageDataAlarmInfo](docs/TimePageDataAlarmInfo.md)
 - [TimePageDataAuditLog](docs/TimePageDataAuditLog.md)
 - [TimePageDataDashboardInfo](docs/TimePageDataDashboardInfo.md)
 - [TimePageDataEvent](docs/TimePageDataEvent.md)
 - [TimePageLink](docs/TimePageLink.md)
 - [UpdateMessage](docs/UpdateMessage.md)
 - [User](docs/User.md)
 - [UserId](docs/UserId.md)
 - [WidgetType](docs/WidgetType.md)
 - [WidgetTypeId](docs/WidgetTypeId.md)
 - [WidgetsBundle](docs/WidgetsBundle.md)
 - [WidgetsBundleId](docs/WidgetsBundleId.md)


## Documentation For Authorization


## X-Authorization

- **Type**: API key
- **API key parameter name**: X-Authorization
- **Location**: HTTP header


## Author

info@thingsboard.io
