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