# coding: utf-8

"""
    Thingsboard REST API

    For instructions how to authorize requests please visit <a href='http://thingsboard.io/docs/reference/rest-api/'>REST API documentation page</a>.  # noqa: E501

    OpenAPI spec version: 2.0
    Contact: info@thingsboard.io
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from  ..api_client import ApiClient


class WidgetTypeControllerApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def delete_widget_type_using_delete(self, widget_type_id, **kwargs):  # noqa: E501
        """deleteWidgetType  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.delete_widget_type_using_delete(widget_type_id, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str widget_type_id: widgetTypeId (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.delete_widget_type_using_delete_with_http_info(widget_type_id, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_widget_type_using_delete_with_http_info(widget_type_id, **kwargs)  # noqa: E501
            return data

    def delete_widget_type_using_delete_with_http_info(self, widget_type_id, **kwargs):  # noqa: E501
        """deleteWidgetType  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.delete_widget_type_using_delete_with_http_info(widget_type_id, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str widget_type_id: widgetTypeId (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['widget_type_id']  # noqa: E501
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_widget_type_using_delete" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'widget_type_id' is set
        if ('widget_type_id' not in params or
                params['widget_type_id'] is None):
            raise ValueError("Missing the required parameter `widget_type_id` when calling `delete_widget_type_using_delete`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'widget_type_id' in params:
            path_params['widgetTypeId'] = params['widget_type_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['X-Authorization']  # noqa: E501

        return self.api_client.call_api(
            '/api/widgetType/{widgetTypeId}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            asynch=params.get('async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_bundle_widget_types_using_get(self, is_system, bundle_alias, **kwargs):  # noqa: E501
        """getBundleWidgetTypes  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.get_bundle_widget_types_using_get(is_system, bundle_alias, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str is_system: isSystem (required)
        :param str bundle_alias: bundleAlias (required)
        :return: list[WidgetType]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.get_bundle_widget_types_using_get_with_http_info(is_system, bundle_alias, **kwargs)  # noqa: E501
        else:
            (data) = self.get_bundle_widget_types_using_get_with_http_info(is_system, bundle_alias, **kwargs)  # noqa: E501
            return data

    def get_bundle_widget_types_using_get_with_http_info(self, is_system, bundle_alias, **kwargs):  # noqa: E501
        """getBundleWidgetTypes  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.get_bundle_widget_types_using_get_with_http_info(is_system, bundle_alias, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str is_system: isSystem (required)
        :param str bundle_alias: bundleAlias (required)
        :return: list[WidgetType]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['is_system', 'bundle_alias']  # noqa: E501
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_bundle_widget_types_using_get" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'is_system' is set
        if ('is_system' not in params or
                params['is_system'] is None):
            raise ValueError("Missing the required parameter `is_system` when calling `get_bundle_widget_types_using_get`")  # noqa: E501
        # verify the required parameter 'bundle_alias' is set
        if ('bundle_alias' not in params or
                params['bundle_alias'] is None):
            raise ValueError("Missing the required parameter `bundle_alias` when calling `get_bundle_widget_types_using_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'is_system' in params:
            query_params.append(('isSystem', params['is_system']))  # noqa: E501
        if 'bundle_alias' in params:
            query_params.append(('bundleAlias', params['bundle_alias']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['X-Authorization']  # noqa: E501

        return self.api_client.call_api(
            '/api/widgetTypes{?isSystem,bundleAlias}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[WidgetType]',  # noqa: E501
            auth_settings=auth_settings,
            asynch=params.get('async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_widget_type_by_id_using_get(self, widget_type_id, **kwargs):  # noqa: E501
        """getWidgetTypeById  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.get_widget_type_by_id_using_get(widget_type_id, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str widget_type_id: widgetTypeId (required)
        :return: WidgetType
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.get_widget_type_by_id_using_get_with_http_info(widget_type_id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_widget_type_by_id_using_get_with_http_info(widget_type_id, **kwargs)  # noqa: E501
            return data

    def get_widget_type_by_id_using_get_with_http_info(self, widget_type_id, **kwargs):  # noqa: E501
        """getWidgetTypeById  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.get_widget_type_by_id_using_get_with_http_info(widget_type_id, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str widget_type_id: widgetTypeId (required)
        :return: WidgetType
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['widget_type_id']  # noqa: E501
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_widget_type_by_id_using_get" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'widget_type_id' is set
        if ('widget_type_id' not in params or
                params['widget_type_id'] is None):
            raise ValueError("Missing the required parameter `widget_type_id` when calling `get_widget_type_by_id_using_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'widget_type_id' in params:
            path_params['widgetTypeId'] = params['widget_type_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['X-Authorization']  # noqa: E501

        return self.api_client.call_api(
            '/api/widgetType/{widgetTypeId}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='WidgetType',  # noqa: E501
            auth_settings=auth_settings,
            asynch=params.get('async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_widget_type_using_get(self, is_system, bundle_alias, alias, **kwargs):  # noqa: E501
        """getWidgetType  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.get_widget_type_using_get(is_system, bundle_alias, alias, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str is_system: isSystem (required)
        :param str bundle_alias: bundleAlias (required)
        :param str alias: alias (required)
        :return: WidgetType
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.get_widget_type_using_get_with_http_info(is_system, bundle_alias, alias, **kwargs)  # noqa: E501
        else:
            (data) = self.get_widget_type_using_get_with_http_info(is_system, bundle_alias, alias, **kwargs)  # noqa: E501
            return data

    def get_widget_type_using_get_with_http_info(self, is_system, bundle_alias, alias, **kwargs):  # noqa: E501
        """getWidgetType  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.get_widget_type_using_get_with_http_info(is_system, bundle_alias, alias, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param str is_system: isSystem (required)
        :param str bundle_alias: bundleAlias (required)
        :param str alias: alias (required)
        :return: WidgetType
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['is_system', 'bundle_alias', 'alias']  # noqa: E501
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_widget_type_using_get" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'is_system' is set
        if ('is_system' not in params or
                params['is_system'] is None):
            raise ValueError("Missing the required parameter `is_system` when calling `get_widget_type_using_get`")  # noqa: E501
        # verify the required parameter 'bundle_alias' is set
        if ('bundle_alias' not in params or
                params['bundle_alias'] is None):
            raise ValueError("Missing the required parameter `bundle_alias` when calling `get_widget_type_using_get`")  # noqa: E501
        # verify the required parameter 'alias' is set
        if ('alias' not in params or
                params['alias'] is None):
            raise ValueError("Missing the required parameter `alias` when calling `get_widget_type_using_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'is_system' in params:
            query_params.append(('isSystem', params['is_system']))  # noqa: E501
        if 'bundle_alias' in params:
            query_params.append(('bundleAlias', params['bundle_alias']))  # noqa: E501
        if 'alias' in params:
            query_params.append(('alias', params['alias']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['X-Authorization']  # noqa: E501

        return self.api_client.call_api(
            '/api/widgetType{?isSystem,bundleAlias,alias}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='WidgetType',  # noqa: E501
            auth_settings=auth_settings,
            asynch=params.get('async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def save_widget_type_using_post(self, widget_type, **kwargs):  # noqa: E501
        """saveWidgetType  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.save_widget_type_using_post(widget_type, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param WidgetType widget_type: widgetType (required)
        :return: WidgetType
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.save_widget_type_using_post_with_http_info(widget_type, **kwargs)  # noqa: E501
        else:
            (data) = self.save_widget_type_using_post_with_http_info(widget_type, **kwargs)  # noqa: E501
            return data

    def save_widget_type_using_post_with_http_info(self, widget_type, **kwargs):  # noqa: E501
        """saveWidgetType  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass asynch=True
        >>> thread = api.save_widget_type_using_post_with_http_info(widget_type, asynch=True)
        >>> result = thread.get()

        :param async bool
        :param WidgetType widget_type: widgetType (required)
        :return: WidgetType
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['widget_type']  # noqa: E501
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method save_widget_type_using_post" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'widget_type' is set
        if ('widget_type' not in params or
                params['widget_type'] is None):
            raise ValueError("Missing the required parameter `widget_type` when calling `save_widget_type_using_post`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'widget_type' in params:
            body_params = params['widget_type']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['X-Authorization']  # noqa: E501

        return self.api_client.call_api(
            '/api/widgetType', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='WidgetType',  # noqa: E501
            auth_settings=auth_settings,
            asynch=params.get('async'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
