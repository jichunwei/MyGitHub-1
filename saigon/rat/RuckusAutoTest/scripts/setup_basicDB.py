"""
Run this script if you want to manually add testbed specific information
such as testbed, testsuites, testcases, and autotestconfig

This script automatically enter into database
- all testbed types
- all testbed components
- Null buildstream
- Null build
- Important Buildstreams

"""

import sys
import os
import types
import datetime
import re
#
# setup django environment
#
from django.core.management import setup_environ

os.chdir("../..")
sys.path.insert(0, os.getcwd())

import settings
setup_environ(settings)

# import RAT models
#from RuckusAutoTest.models import *
from RuckusAutoTest.models import TestbedType, TestbedComponent, BuildStream, Build
from RuckusAutoTest.testbeds import *
#from RuckusAutoTest.components import *

from django.core.exceptions import ObjectDoesNotExist

def add_all_testbed_types():
    """
    Find all RAT Testbed objects and add them to the database as TestbedTypes if they are not already there.
    Assumes/requires all modules within RuckusAutoTest.testbeds are testbed implementations.
    """
    print "\nDiscovering RuckusAutoTest.testbeds and adding them to the database:\n"
    for name, obj in sys.modules['RuckusAutoTest.testbeds'].__dict__.items():
        if name != 'sys' and type(obj) == types.ModuleType:
            try:
                tbt = TestbedType.objects.get(name = name)
                print "    TestbedType '%s' already in database.\n" % name
            except ObjectDoesNotExist:
                print "    TestbedType '%s' not found in database; adding...\n" % name
                TestbedType(name = name, description = obj.__doc__).save()


def add_all_testbedcomponent_types():
    """
    Find all RAT Testbed component objects and add them to the database as TestbedComponent if they are not already there.
    Assumes/requires all modules within RuckusAutoTest.components are testbed component implementations.
    """
    print "\nDiscovering RuckusAutoTest.components and adding them to the database:\n"
    for name, obj in sys.modules['RuckusAutoTest.components'].__dict__.items():
        if name == 'sys' or name == "lib" or name == "resources" or re.search('helper',name,re.I):
            continue
        if type(obj) == types.ModuleType:
            try:
                tbt = TestbedComponent.objects.get(name = name)
                print "    TestbedComponent '%s' is already in database.\n" % name
            except ObjectDoesNotExist:
                print "    TestbedComponent '%s' is not found in database; adding...\n" % name
                TestbedComponent(name = name, description = obj.__doc__).save()


lhotse_url = "http://lhotse/cgi-bin/build_info.pl?filename=www_%s"
k2_url = "http://k2/cgi-bin/build_info.pl?filename=www_%s"
# some buildstreams were moved to different repository,
# they are coded in list, with the 2nd element as int
lhotse_url_old="http://lhotse/cgi-bin/build_info_old.pl?filename=www_%s"
yangming_url="http://yangming.tw.video54.local:9000/buildsystem/build_list?pd_name=%s"
def get_build_prefix_url(bsname, debug = False):
    if debug:
        import pdb
        pdb.set_trace()
    if type(bsname) is list:
        repo_type = bsname[1]
        bsname=bsname[0]
        prefix=bsname.split('_')[1]
    else:
        prefix = bsname.split('_')[1]
        repo_type=False
    if re.match(r'[0-9.]+',prefix) and int(prefix.split('.')[0]) < 8:
        bld_url = k2_url % bsname
    elif repo_type == 1:
        bld_url = lhotse_url_old % bsname
    elif repo_type == 2:
        bld_url = yangming_url % bsname.replace('_','').replace('.','')
    else:
        bld_url = lhotse_url % bsname
    return (bsname, prefix, bld_url)

# BuildStream: specify the name
bsname_list = [
               'ZD1000_mainline',
               ['ZD3000_9.4.0.0_production',2],
               ['ZD3000_9.5.0.0_production',2],
               ['ZD3000_9.5.1.0_production',2],
               ['ZD3000_9.5.2.0_production',2],
               ['ZD3000_9.6.0.0_production',2],
               ['ZD3000_9.7.0.0_production',2],
               ['ZD3000_9.8.0.0_production',2],
               ['ZD3000_9.9.0.0_production',2],
               ['ZD3000_0.0.0.99_production',2],
               'ZD3000_china_mainline',
               'ZD3000_mainline',
               ]

def make_buildstream(rewrite = False):
    print "\nAdding BuildStream:\n"
    for bsname in bsname_list:
        (_bsname, _prefix, _URL) = get_build_prefix_url(bsname)
        try:
            bs = BuildStream.objects.get(name=_bsname)
            if rewrite:
                print "    BuildStream '%s' is found in database; rewriting...\n" % _bsname
                bs.prefix = _prefix
                bs.URL = _URL
                bs.save()
            else:
                print "    BuildStream '%s' is already in database." % _bsname
        except ObjectDoesNotExist:
            print "    BuildStream '%s' is not found in database; adding...\n" % _bsname
            bs = BuildStream(name=_bsname, prefix=_prefix, URL=_URL)
            bs.save()


#Must Add Null BuildStream and Null Build if don't want to upgrade SW
def add_nullstream():
    bsnull = 'Null'
    print "Adding buildstream %s " % bsnull
    try:
        tbt = BuildStream.objects.get(name = bsnull)
        print "BuidStream '%s' already in database." % bsnull
    except ObjectDoesNotExist:
        print "BuildStream '%s' not found in database; adding...\n" % bsnull
        bs = BuildStream(name = "Null", prefix = "Null")
        bs.save()

    bdnull = 'NullBuild'
    print "Adding build %s " % bdnull
    try:
        tbt = Build.objects.get(label = 'Null')
        print "Build '%s' is already in database." % bdnull
    except ObjectDoesNotExist:
        print "Build '%s' is not found in database; adding...\n" % bdnull
        bd = Build(build_stream = BuildStream.objects.get(name = bsnull),
                  number = 1,
                  builder = 'Null',
                  version = '0',
                  label = 'Null',
                  timestamp = datetime.datetime.now(),
                  URL = 'Null')
        bd.save()

def setup_basicDB(**kwargs):
    fcfg = dict(rewrite = False)
    fcfg.update(kwargs)
    add_all_testbed_types()
    add_all_testbedcomponent_types()
    make_buildstream(rewrite = fcfg['rewrite'])
    ########## To run without upgrade software: configure an Autotestconfig with Null BuildStream:
    add_nullstream()

def _Usage():
    print"""
This script creates rat.db's basic data set so regression testbed's objects can be constructed correctly.

    Note on buildstream which define the URL location to download the build packages.
    Buildstream's URL is define here and not configured by the class BuildStream any more.
    If you change k2_url and lhots_url, [or buildstream URL moved to old repository]
    you can rerun this program with KW of rewrite=True

Run Example:

    python setup_basicDB.py
    python setup_basicDB.py rewrite=True
"""

# Usage:
#
#       python setup_basicDB.py
#       python setup_basicDB.py rewrite=True
#
if __name__ == "__main__":
    from RuckusAutoTest.common import lib_KwList as kwlist
    _dict = kwlist.as_dict(sys.argv[1:])
    if _dict.has_key('h') or _dict.has_key('help'):
        _Usage()
        exit(0)
    setup_basicDB(**_dict)

