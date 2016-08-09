"""
Script to add new testbed or testsuite to database.
First it automatically add all the testbed types in to
the database. Do not change this part of the code.

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
import time
import random
import re

#
# setup django environment
#
from django.core.management import setup_environ

os.chdir("../../..")
sys.path.insert(0, os.getcwd())

import settings
setup_environ(settings)

# import RAT models
from RuckusAutoTest.models import TestbedType, TestbedComponent, BuildStream, Testbed, TestCase, TestSuite, AutotestConfig
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
                tbt = TestbedType.objects.get(name = name)
                print "TestbedType '%s' is already in database." % name
            except ObjectDoesNotExist:
                print "TestbedType '%s' is not found in database; adding...\n" % name
                TestbedType(name = name, description = obj.__doc__).save()

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
                tbt = TestbedComponent.objects.get(name = name)
                print "TestbedComponent '%s' is already in database." % name
            except ObjectDoesNotExist:
                print "TestbedComponent '%s' is not found in database; adding...\n" % name                
                if obj.__doc__:                    
                    TestbedComponent(name = name, description = obj.__doc__).save()
                else:
                    TestbedComponent(name = name, description = 'component').save()

add_all_testbedcomponent_types()

# Testbed: specify the name and details required
tb_name = raw_input("Testbed name: ")
tb_location = raw_input("Testbed location: ")
tb_owner = raw_input("Testbed owner: ")
sta_ip_list = raw_input("Station IP list (separated by spaces): ")
ap_list_str = raw_input("AP list in format 'name':'MAC' (separated by comma): ")
ap_dict = eval("{%s}" % ap_list_str)
ap_mac_list = []
ap_name_list = []
for name, mac in ap_dict.iteritems():
    ap_name_list.append(name)
    ap_mac_list.append(mac)
    
zd_config = "{'ZD':{'browser_type':'firefox', 'ip_addr':'192.168.0.2', 'username':'admin', 'password':'admin'}"
sta_config = "'sta_conf':{'username':'lab', 'password':'lab4man1', 'tool_ip_addr':'192.168.1.10', 'tool_folder':'common$'}"
tb_config = "%s, 'ap_mac_list': %s,'sta_ip_list':%s, %s}" % (zd_config, ap_mac_list, sta_ip_list.split(), sta_config)
testbed = {'name':tb_name,
           'tbtype': TestbedType.objects.get(name = 'ZD_Stations'),
           'location':tb_location,
           'owner':tb_owner,
           'resultdist':tb_owner,
           'config':tb_config}

print "Adding ZD_Stations testbed %s " % testbed['name']
try:
    tb = Testbed.objects.get(name = testbed['name'])
    print "Testbed '%s' is already in database." % testbed['name']
except ObjectDoesNotExist:
    print "Testbed '%s' is not found in database; adding...\n" % testbed['name']
    tb = Testbed(**testbed)
    tb.save()

# Please add new build streams that are available in K2 to the list below
def_bs_list = ["ZD1000_3.0.0_production", "ZD1000_6.0.0_beta_production",
               "ZD1000_6.0.0_production", "ZD1000_7.0.0.0_production", "FD1000_mainline"]
for bsname in def_bs_list:
    while True:
        answer = raw_input("Do you want to add build stream %s (yes/no)[enter=yes]? " % bsname)
        if not answer or answer.lower() == "yes":
            print "Adding buildstream %s " % bsname
            try:
                bs = BuildStream.objects.get(name = bsname)
                print "BuidStream '%s' is already in database." % bsname
            except ObjectDoesNotExist:
                print "BuildStream '%s' is not found in database; adding...\n" % bsname
                bs = BuildStream(name = bsname, prefix = bsname.split('_')[1])
                bs.save()
            break
        elif answer.lower() == "no":
            break

# This function return the default security settings for a test case
def get_default_params(target_sta, act_ap):
    default_test_params = {'ip': '192.168.0.252',
                           'target_station': '%s' % target_sta,
                           'active_ap': '%s' % act_ap,
                           'wlan_cfg': {'username': '',
                                        'ssid': 'RAT_ZD_%s' % time.strftime("%H%M%S"),
                                        'ras_secret': '',
                                        'ras_port': '',
                                        'key_string': '',
                                        'key_index': '',
                                        'auth': 'open',
                                        'ras_addr': '',
                                        'use_radius': False,
                                        'encryption': 'none',
                                        'password': '',
                                        'wpa_ver': '',
                                        'sta_wpa_ver': '',
                                        'sta_auth': 'open',
                                        'sta_encryption': 'none'},
                                        'timeout': 180}
    return default_test_params

# Add test suites
ts_list = list()
for ap_info in ap_name_list:
    for sta_info in sta_ip_list.split():
        # end get_default_params
        tsname = "AssocPing_%s_%s" % (sta_info.split('.')[3], ap_info.upper())
        print "Adding TestSuite %s " % tsname
        try:
            ts = TestSuite.objects.get(name = tsname)
            print "TestSuite '%s' is already in database." % tsname

        except ObjectDoesNotExist:
            print "TestSuite '%s' is not found in database; adding...\n" % tsname
            ts = TestSuite(name = tsname)
            ts.save()
            ts_list.append(tsname)

#Add test cases to testsuites
ts_all = TestSuite.objects.all()
for ts in ts_all:
    tcase_per_ts = 0

    print "Adding test cases to TestSuite %s " % ts.name
    obj = re.search("_([0-9\.]+)_", ts.name)
    if not obj: continue
    target_station = '192.168.1.' + obj.group(1)
    obj = re.search("_([A-Z0-9]+)$", ts.name)
    if not obj: continue
    active_ap_name = obj.group(1)
    active_ap_mac = ap_dict[active_ap_name]

    # default test_params for none encryption
    auth_list = ['open', 'shared', 'PSK', 'EAP']
    encryption_list = ['WEP-64', 'WEP-128', 'TKIP', 'AES']
    wpa_ver_list = ['WPA', 'WPA2']
    use_radius_list = [True, False]
    test_id = 1
    TestCase(suite = ts, test_name = "AssocPing", seq = tcase_per_ts, test_params = str(get_default_params(target_station, active_ap_mac)),
             common_name = 'AssocPing 1: Auth(Open) Encryption(None) Station %s AP %s' % (target_station, active_ap_mac)).save()
    test_id = test_id + 1
    tcase_per_ts = tcase_per_ts + 1
    for auth in auth_list:
        if auth in auth_list[0:2]:
            for encryption in encryption_list[0:2]:
                for key_index in [1, 2, 3, 4]:
                    test_params = get_default_params(target_station, active_ap_mac)
                    test_params['wlan_cfg']['key_index'] = str(key_index)
                    test_params['wlan_cfg']['auth'] = auth
                    test_params['wlan_cfg']['encryption'] = encryption
                    test_params['wlan_cfg']['sta_auth'] = auth
                    test_params['wlan_cfg']['sta_encryption'] = encryption

                    test_params['wlan_cfg']['key_string'] = utils.make_random_string({'WEP-64':10, 'WEP-128':26}[encryption], "hex")
                    common_name = "AssocPing %d: Auth(%s) Encryption(%s) Key Index(%d) Station %s AP %s" % (test_id, auth, encryption, key_index, target_station, active_ap_mac)
                    TestCase(suite = ts, test_name = "AssocPing", seq = tcase_per_ts, test_params = str(test_params), common_name = common_name).save()
                    test_id = test_id + 1
                    tcase_per_ts = tcase_per_ts + 1

        elif auth == auth_list[2]:
            for encryption in encryption_list[2:]:
                for wpa_ver in wpa_ver_list:
                    test_params = get_default_params(target_station, active_ap_mac)
                    test_params['wlan_cfg']['auth'] = auth
                    test_params['wlan_cfg']['encryption'] = encryption
                    test_params['wlan_cfg']['sta_auth'] = auth
                    test_params['wlan_cfg']['sta_encryption'] = encryption

                    test_params['wlan_cfg']['wpa_ver'] = wpa_ver
                    test_params['wlan_cfg']['sta_wpa_ver'] = wpa_ver
                    test_params['wlan_cfg']['key_string'] = utils.make_random_string(random.randint(8, 63), "hex")
                    common_name = "AssocPing %d: Auth(%s) Encryption(%s) %s Station %s AP %s" % (test_id, auth, encryption, wpa_ver, target_station, active_ap_mac)
                    TestCase(suite = ts, test_name = "AssocPing", seq = tcase_per_ts, test_params = str(test_params), common_name = common_name).save()
                    test_id = test_id + 1
                    tcase_per_ts = tcase_per_ts + 1
        else:
            for encryption in encryption_list[0:2]:
                for use_radius in use_radius_list:
                    test_params = get_default_params(target_station, active_ap_mac)
                    test_params['wlan_cfg']['auth'] = auth
                    test_params['wlan_cfg']['encryption'] = encryption
                    test_params['wlan_cfg']['sta_auth'] = auth
                    test_params['wlan_cfg']['sta_encryption'] = encryption
                    test_params['wlan_cfg']['username'] = 'rat_user'
                    test_params['wlan_cfg']['password'] = 'rat_user'
                    if use_radius:
                        test_params['wlan_cfg']['ras_secret'] = '1234567890'
                        test_params['wlan_cfg']['ras_port'] = '1812'
                        test_params['wlan_cfg']['ras_addr'] = '192.168.0.252'
                        test_params['wlan_cfg']['use_radius'] = True
                    else:
                        test_params['wlan_cfg']['use_radius'] = False
                    common_name = "AssocPing %d: Auth(%s) Encryption(%s) Station %s AP %s" % (test_id, auth, encryption, target_station, active_ap_mac)
                    TestCase(suite = ts, test_name = "AssocPing", seq = tcase_per_ts, test_params = str(test_params), common_name = common_name).save()
                    test_id = test_id + 1
                    tcase_per_ts = tcase_per_ts + 1

            for encryption in encryption_list[2:]:
                for wpa_ver in wpa_ver_list:
                    for use_radius in use_radius_list:
                        test_params = get_default_params(target_station, active_ap_mac)
                        test_params['wlan_cfg']['auth'] = auth
                        test_params['wlan_cfg']['encryption'] = encryption
                        test_params['wlan_cfg']['sta_auth'] = auth
                        test_params['wlan_cfg']['sta_encryption'] = encryption
                        test_params['wlan_cfg']['username'] = 'rat_user'
                        test_params['wlan_cfg']['password'] = 'rat_user'
                        test_params['wlan_cfg']['wpa_ver'] = wpa_ver
                        test_params['wlan_cfg']['sta_wpa_ver'] = wpa_ver
                        if use_radius:
                            test_params['wlan_cfg']['ras_secret'] = '1234567890'
                            test_params['wlan_cfg']['ras_port'] = '1812'
                            test_params['wlan_cfg']['ras_addr'] = '192.168.0.252'
                            test_params['wlan_cfg']['use_radius'] = True
                        else:
                            test_params['wlan_cfg']['use_radius'] = False
                        common_name = "AssocPing %d: Auth(%s) Encryption(%s) %s Station %s AP %s" % (test_id, auth, encryption, wpa_ver, target_station, active_ap_mac)
                        TestCase(suite = ts, test_name = "AssocPing", seq = tcase_per_ts, test_params = str(test_params), common_name = common_name).save()
                        test_id = test_id + 1
                        tcase_per_ts = tcase_per_ts + 1

# Add AutoTestConfigs
order_num = 0
for bs in BuildStream.objects.all():
    at = AutotestConfig(testbed = tb, build_stream = bs, order = order_num)
    at.save()
    order_num = order_num + 1
    for ts in TestSuite.objects.all():
        at.suites.add(ts)

