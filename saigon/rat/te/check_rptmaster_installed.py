"""
This module check whether all required packages that support for Master Report are
installed correctly.
"""


import traceback
import os
os.chdir('..')
import sys
sys.path.append(os.getcwd())

from django.core.management import setup_environ
import settings
setup_environ(settings)



def check_simple_json():
    try:
        import simplejson
    except:
        print 'Simplejson package is not installed. Please install it.'
        return
    print 'Simplejson package is installed successfully'


def check_django_json_rpc():
    try:
        from jsonrpc import jsonrpc_method
    except Exception:
        print 'Django-json-rpc package is not installed. Please install it. Trace back: %s' % traceback.format_exc()
        return
    print 'Django-json-rpc package is installed successfully'


def get_django_version():
    try:
        import django
        print 'You are running Django version %s' % str(django.VERSION)
    except Exception:
        print 'Cant import Django. Please check PYTHONPATH. Trace back: %s' % traceback.format_exc()
        return

if __name__ == "__main__":
    check_simple_json()
    check_django_json_rpc()
    get_django_version()
