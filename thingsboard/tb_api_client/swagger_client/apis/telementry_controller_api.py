from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..api_client import ApiClient


class TelemetryControllerApi(object):
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client


    def save_entity_attributesV2(self,entityType,entityId,scope,parameters,**kwargs):
        """
            Set the attributes of the entity

        :param entityType: "ASSET" or "DEVICE"
        :param entityId: entity id
        :param scope: "SERVER_SCOPE" or "SHARED_SCOPE"
        :param parameters: a key-value map of the attributes
        :param kwargs: another method to specify parameters.
        :return:
        """

        all_params = []
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_device_attributes_using_get" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = { "entityType" : entityType,
                        "entityId"   : entityId,
                        "scope"      : scope
                      }

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = parameters

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['*/*'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['X-Authorization']

        retval = self.api_client.call_api('/api/plugins/telemetry/{entityType}/{entityId}/attributes/{scope}', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='DeferredResultResponseEntity',
                                        auth_settings=auth_settings,
                                        asynch=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)


        return retval

    def get_attributes(self,entityType,entityId,scope=None,**kwargs):
        """
            Get the entity attributes.

        :param entityType DEVICE or ASSET
        :param entityId the id of the entity.
        :param scope either NONE (for all) or "SERVER_SCOPE" or "SHARED_SCOPE" or "CLIENT_SCOPE"
        :param kwargs optional definition of he async, return http only and request timeout.
        :return:
        """

        all_params = []
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_device_by_id_using_get" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = { "entityType" : entityType,
                        "entityId"   : entityId
                       }

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = {}

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['X-Authorization']

        if scope is not None:
            path_params["scope"] = scope
            requestpath = '/api/plugins/telemetry/{entityType}/{entityId}/values/attributes/{scope}'
        else:
            requestpath = '/api/plugins/telemetry/{entityType}/{entityId}/values/attributes'

        retval = self.api_client.call_api(requestpath, 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='DeferredResultResponseEntity',
                                        auth_settings=auth_settings,
                                        asynch=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

        return retval