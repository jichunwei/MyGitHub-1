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

# Testbed: specify the name and details required
tb_cfg = {'name':'AP-Single-STA',
             'tbtype': TestbedType.objects.get(name = 'AP_Single_Station'),
             'location':'QA-Lab',
             'owner':'ruckusauto@s3solutions.com.vn',
             'resultdist':'ruckusauto@s3solutions.com.vn',
             "config":"{'VF7811':{'ip_addr':'192.168.1.21','username':'super','password':'sp-admin','ftpsvr':{'ip_addr':'192.168.1.20','protocol':'FTP','username':'anonymous','password':'anonymous','rootpath':'c:\\\\tftpboot'}},'sta_ip_addr':'192.168.1.20'}"}


print "Adding AP testbed %s " % tb_cfg['name']
try:
    tbt = Testbed.objects.get(name = tb_cfg['name'])
    print "Testbed '%s' is already in database." % tb_cfg['name']
except ObjectDoesNotExist:
    print "Testbed '%s' is not found in database; adding...\n" % tb_cfg['name']        
    tb = Testbed(**tb_cfg)
    tb.save()
  
    
# BuildStream: specify the name
bsname_list = ['VF7811_5.3.0.0_production']

for bsname in bsname_list:
    print "Adding buildstream %s " % bsname
    try:
        tbt = BuildStream.objects.get(name = bsname)
        print "BuidStream '%s' is already in database." % bsname
    except ObjectDoesNotExist:
        print "BuidlStream '%s' is not found in database; adding...\n" % bsname
        bs = BuildStream(name = bsname, prefix = bsname.split('_')[1])
        bs.save()

# TestSuite: specify the name and test cases in it
tsname = 'AssocPing'
def get_default_params():
    default_test_params = {'ip': '192.168.0.252',
                   'active_ap':'00:13:92:02:0A:08',
                   'target_station':'192.168.1.20',
                   'wlan_cfg': {'username': '',
                                'ssid': 'RAT-%s' % time.strftime("%H%M%S"),
                                'ras_secret': '',
                                'ras_port': '',
                                'key_string': '',
                                'key_index': '',
                                'auth': 'open',
                                'ras_addr': '',
                                'use_radius': False,
                                'encryption': 'none',
                                'password': '',
                                'wlan_if': 'wlan0',
                                'wpa_ver': '',
                                'sta_wpa_ver': '',
                                'sta_auth': 'open',
                                'sta_encryption': 'none', },
                                'timeout': 180}
    return default_test_params
# end get_default_params


print "Adding TestSuite %s " % tsname
try:
    ts = TestSuite.objects.get(name = tsname)
    print "TestSuite '%s' is already in database." % tsname
except ObjectDoesNotExist:
    print "TestSuite '%s' is not found in database; adding...\n" % tsname
    ts = TestSuite(name = tsname)
    ts.save()
print "Adding TestCase to TestSuite %s " % tsname

# default test_params for none encryption
auth_list = ['open', 'shared', 'PSK', 'EAP']
encryption_list = ['WEP-64', 'WEP-128', 'Auto']
wpa_ver_list = ['WPA', 'WPA2']
tcs = []
test_id = 1        
TestCase(suite = ts, test_name = tsname, seq = test_id, test_params = str(get_default_params()),
         common_name = 'AssocPing 1(AP %s): Auth(Open) Encryption(None)' % get_default_params()['active_ap']).save() 
test_id = test_id + 1
for auth in auth_list:
    if auth in auth_list[0:2]:
        for encryption in encryption_list[0:3]:
            for key_index in [1, 2, 3, 4]:          
                test_params = get_default_params()      
                test_params['wlan_cfg']['key_index'] = str(key_index)
                test_params['wlan_cfg']['auth'] = auth
                test_params['wlan_cfg']['encryption'] = encryption                
                test_params['wlan_cfg']['sta_auth'] = auth
                test_params['wlan_cfg']['sta_encryption'] = encryption

                if encryption == 'Auto':
                    pass
                else:
                    test_params['wlan_cfg']['key_string'] = utils.make_random_string({'WEP-64':10, 'WEP-128':26}[encryption], "hex")
                    common_name = "AssocPing %d (AP %s): Auth(%s) Encryption(%s) Key Index(%d)" % (test_id, get_default_params()['active_ap'], auth, encryption, key_index)                            
                    TestCase(suite = ts, test_name = tsname, seq = test_id, test_params = str(test_params), common_name = common_name).save()
                    test_id = test_id + 1
    else:        
        for encryption in encryption_list[2:]:
            if encryption == 'Auto':
                pass
            else:
                for wpa_ver in wpa_ver_list:
                    test_params = get_default_params()
                    test_params['wlan_cfg']['auth'] = auth
                    test_params['wlan_cfg']['encryption'] = encryption                
                    test_params['wlan_cfg']['sta_auth'] = auth
                    test_params['wlan_cfg']['sta_encryption'] = encryption

                    test_params['wlan_cfg']['wpa_ver'] = wpa_ver
                    test_params['wlan_cfg']['sta_wpa_ver'] = wpa_ver
                    if wpa_ver == 'Auto':
                        pass
                    else:
                        test_params['wlan_cfg']['key_string'] = utils.make_random_string(random.randint(8, 63), "hex")
                        if auth == auth_list[3]:
                            test_params['wlan_cfg']['ras_secret'] = '1234567890'
                            test_params['wlan_cfg']['ras_port'] = '1812'
                            test_params['wlan_cfg']['ras_addr'] = '192.168.0.20'
                            test_params['wlan_cfg']['use_radius'] = True
                            test_params['wlan_cfg']['use_onex'] = True
                            test_params['wlan_cfg']['username'] = 'rat_user'
                            test_params['wlan_cfg']['password'] = 'rat_user'   

                        common_name = "AssocPing %d (AP %s): Auth(%s) Encryption(%s) %s" % (test_id, get_default_params()['active_ap'], auth, encryption, wpa_ver)                                
                        TestCase(suite = ts, test_name = tsname, seq = test_id, test_params = str(test_params), common_name = common_name).save()
                        test_id = test_id + 1         

# AutotestConfig: must be added to test the newly added test suite with a specific build stream
tb_comp = TestbedComponent(name = "VF7811")
for i in range(len(bsname_list)):    
    lastbuildnum = {'VF7811_5.3.0.0_production':47}[bsname_list[i]]
                    
    at = AutotestConfig(testbed = Testbed.objects.get(name = tb_cfg['name']),
                        build_stream = BuildStream.objects.get(name = bsname_list[i]),
                        lastbuildnum = lastbuildnum, DUT = TestbedComponent.objects.get(name = "VF7811"),
                        order = i)
    at.save()
    at.suites.add(TestSuite.objects.get(name = tsname))

