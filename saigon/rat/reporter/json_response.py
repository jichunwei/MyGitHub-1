from django.shortcuts import HttpResponse
from django.utils import simplejson as JSON
from django.core import serializers

JSON_SERIALIZER = serializers.get_serializer("json")()

###
### utilities to get json response from DB tables
###
class JsonResponse(HttpResponse):
    def __init__(self, py_dict):
        content = JSON.dumps(
            py_dict,
            indent = 3,
            ensure_ascii = False
        )
        super( JsonResponse, self ).__init__(
            content = content,
            content_type = 'application/javascript; charset=utf8'
        )
        super( JsonResponse, self ).__setitem__(
            header = 'Access-Control-Allow-Origin',
            value = '*'
        )

class JsonResponseOnQSet(HttpResponse):
    def __init__( self, queryset ):
        content = JSON_SERIALIZER.serialize(
            queryset,
            ensure_ascii = False,
            use_natural_keys = True
        )
        super( JsonResponseOnQSet, self ).__init__(
            content = content,
            content_type = 'application/javascript; charset=utf8'
        )
        super( JsonResponseOnQSet, self ).__setitem__(
            header = 'Access-Control-Allow-Origin',
            value = '*'
        )

def json_response(py_dict):
    # return with application/json preventing you from debugging in your browser?
    return HttpResponse(
        JSON.dumps(py_dict),
        content_type = 'application/javascript; charset=utf8'
        )

def json_response_on_qs(queryset):
    # return with application/json preventing you from debugging in your browser?
    return HttpResponse(
        JSON_SERIALIZER.serialize(queryset,ensure_ascii=False),
        content_type = 'application/javascript; charset=utf8'
        )
'''
Created on 2013-3-11

@author: Administrator
'''
