"""
Script to add new testbed or testsuite to database.
First it automatically add all the testbed types and testbed components
into the database. Do not change this part of the code.

To add a new testbed:
   Specify the testbed name and provide necessary info 
To add a new BuildStream:
   Specify the name (the k2 release build name without the leading www_)
To add a new testsuite:
   Specify the test suite name
   Specify the test cases in it with proper test parameters
Finally, AutotestConfig needs to be added to specify which
build stream to use for the test suite added.

Multiple test suites and its related Autotestconfig can be
created in this file for the same testbed. Please use different
script files for different testbeds.

The script performs check in the database to make sure no objects
of the same name is entered into the database.

"""

import sys
import os
import types
import datetime

#
# setup django environment
#
from django.core.management import setup_environ

os.chdir("../../..")
sys.path.insert(0, os.getcwd())

import settings
setup_environ(settings)

# import RAT models
from RuckusAutoTest.models import TestbedType, TestbedComponent, BuildStream, Testbed, TestCase, TestSuite, AutotestConfig, Build
from RuckusAutoTest.testbeds import *
from RuckusAutoTest.common import Ratutils as utils

from django.core.exceptions import ObjectDoesNotExist

def add_all_testbed_types():
    """
    Find all RAT Testbed objects and add them to the database as TestbedTypes if they are not already there.
    Assumes/requires all modules within RuckusAutoTest.testbeds are testbed implementations.
    """
    print "\nDiscovering RuckusAutoTest.testbeds and adding them to the database...\n"
    for name, obj in sys.modules['RuckusAutoTest.testbeds'].__dict__.items():
        if name != 'sys' and type(obj) == types.ModuleType:
            try:
                tbt = TestbedType.objects.get(name=name)
                print "TestbedType '%s' is already in database." % name
            except ObjectDoesNotExist:
                print "TestbedType '%s' is not found in database; adding...\n" % name
                TestbedType(name=name, description=obj.__doc__).save()

add_all_testbed_types()

def add_all_testbedcomponent_types():
    """
    Find all RAT Testbed component objects and add them to the database as TestbedComponent if they are not already there.
    Assumes/requires all modules within RuckusAutoTest.components are testbed component implementations.
    """
    print "\nDiscovering RuckusAutoTest.components and adding them to the database...\n"
    for name, obj in sys.modules['RuckusAutoTest.components'].__dict__.items():
        if name != 'sys' and type(obj) == types.ModuleType:
            try:
                tbt = TestbedComponent.objects.get(name=name)
                print "TestbedComponent '%s' is already in database." % name
            except ObjectDoesNotExist:
                print "TestbedComponent '%s' is not found in database; adding...\n" % name
                TestbedComponent(name=name, description=obj.__doc__).save()

add_all_testbedcomponent_types()


# Testbed: specify the name and details required
tbname = 'StandaloneAP'
print "Adding AP testbed %s " % tbname
try:
    tbt = Testbed.objects.get(name=tbname)
    print "Testbed '%s' is already in database." % tbname
except ObjectDoesNotExist:
    print "Testbed '%s' is not found in database; adding...\n" % tbname
    tb = Testbed(name=tbname,
             tbtype=TestbedType.objects.get(name='AP'),
             location='amycube',
             owner='awang@ruckuswireless.com',
             resultdist='awang@ruckuswireless.com',
             config="{'ap':{'ip_addr':'172.16.14.101','username':'super','password':'sp-admin','ftpsvr':{'ip_addr':'172.16.14.50','protocol':'TFTP','rootpath':'/tftpboot'}}}")
    tb.save()


    
# BuildStream: specify the name
bsname = 'AP2825_4.2.0_production'
print "Adding buildstream %s " % bsname
try:
    tbt = BuildStream.objects.get(name=bsname)
    print "BuidStream '%s' is already in database." % bsname
except ObjectDoesNotExist:
    print "BuidlStream '%s' is not found in database; adding...\n" % bsname
    bs = BuildStream(name="AP2825_4.2.0_production", prefix="4.2.0")
    bs.save()


# TestSuite: specify the name and test cases in it
tsname = 'APSSID'
print "Adding APSSID TestSuite %s " % tsname
try:
    tbt = TestSuite.objects.get(name=tsname)
    print "TestSuite '%s' is already in database." % tsname
except ObjectDoesNotExist:
    print "TestSuite '%s' is not found in database; adding...\n" % tsname
    ts = TestSuite(name=tsname)
    ts.save()

    print "Adding TestCase"
    test_params={'wlan_if':'wlan0'}
    TestCase(suite=ts,test_name="APSSID",seq=1,test_params=str(test_params)).save()


# AutotestConfig: must be added to test the newly added test suite with a specific build stream
at = AutotestConfig(testbed=Testbed.objects.get(name=tbname),
                    build_stream=BuildStream.objects.get(name=bsname ),
                    lastbuildnum=171,
                    order=0)
at.save()
at.suites.add(TestSuite.objects.get(name=tsname))


########## To run without upgrade software: configure an Autotestconfig with Null BuildStream:

#Must Add Null BuildStream and Null Build if don't want to upgrade SW
bsnull = 'Null'
print "Adding buildstream %s " % bsnull
try:
    tbt = BuildStream.objects.get(name=bsnull)
    print "BuidStream '%s' is already in database." % bsnull
except ObjectDoesNotExist:
    print "BuildStream '%s' is not found in database; adding...\n" % bsnull
    bs = BuildStream(name="Null", prefix="Null")
    bs.save()

bdnull = 'NullBuild'
print "Adding build %s " % bdnull
try:
    tbt = Build.objects.get(label='Null')
    print "Build '%s' is already in database." % bdnull
except ObjectDoesNotExist:
    print "Build '%s' is not found in database; adding...\n" % bdnull
    bd = Build(build_stream =  BuildStream.objects.get(name=bsnull),
                  number       = 1,
                  builder      = 'Null',
                  version      = '0',
                  label        = 'Null',
                  timestamp    = datetime.datetime.now(),
                  URL          = 'Null')
    bd.save()

atnull = AutotestConfig(testbed=Testbed.objects.get(name=tbname),
                    build_stream=BuildStream.objects.get(name=bsnull),
                    order=1)
atnull.save()
atnull.suites.add(TestSuite.objects.get(name=tsname))    
