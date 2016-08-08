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
tb_cfg = {'name':'AP-Multi-STAs',
             'tbtype': TestbedType.objects.get(name = 'AP_Stations'),
             'location':'QA-Lab',
             'owner':'ruckusauto@s3solutions.com.vn',
             'resultdist':'ruckusauto@s3solutions.com.vn',
             "config":"{'ZF2925':{'ip_addr':'192.168.0.250'},'ZF7942':{'ip_addr':'192.168.0.240'},'ap_conf':{'username':'super','password':'sp-admin','ftpsvr':{'ip_addr':'192.168.0.21','protocol':'FTP','username':'anonymous','password':'anonymous','rootpath':'c:\\\\tftpboot'}},'sta_ip_list':['192.168.1.31','192.168.1.32'],'sta_conf':{'username':'lab', 'password':'lab4man1', 'tool_ip_addr':'192.168.1.10','tool_folder':'common$'}}"}


print "Adding AP testbed %s " % tb_cfg['name']
try:
    tbt = Testbed.objects.get(name = tb_cfg['name'])
    print "Testbed '%s' is already in database." % tb_cfg['name']
except ObjectDoesNotExist:
    print "Testbed '%s' is not found in database; adding...\n" % tb_cfg['name']        
    tb = Testbed(**tb_cfg)
    tb.save()
  
    
# BuildStream: specify the name
#bsname_list = ['AP2825_4.2.0_production','ZF2925_5.0.0_production','ZF2925_6.0.0.0_production','ZF2925_6.0.0.0_beta_production']
bsname_list = ['ZF2925_6.0.0.0_production', 'ZF7942_6.0.0.0_production']

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

def get_default_params(active_ap, target_sta):
    default_test_params = {'ip': '192.168.0.252',
                   'active_ap':active_ap,
                   'target_station':target_sta,
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
ap_list = ["00:1d:2e:0f:b5:e8", "00:1f:41:12:93:00"]
sta_ip_list = []
sta_ip_list = ["192.168.1.31", "192.168.1.32"] 

auth_list = ['open', 'shared', 'PSK', 'EAP']
encryption_list = ['WEP-64', 'WEP-128', 'Auto', 'TKIP', 'AES']
wpa_ver_list = ['WPA', 'WPA2']
tcname = 'AssocPing'

for active_ap in ap_list:   
    # default test_params for none encryption
    tcs = []
    test_id = 1
    for sta_ip in sta_ip_list:
        tsname = 'AssocPing (AP: %s - STA %s)' % ({"00:1d:2e:0f:b5:e8":"ZF2925", "00:1f:41:12:93:00":"ZF7942"}[active_ap], sta_ip)
        print "Adding TestSuite %s " % tsname
        try:
            ts = TestSuite.objects.get(name = tsname)
            print "TestSuite '%s' is already in database." % tsname
        except ObjectDoesNotExist:
            print "TestSuite '%s' is not found in database; adding...\n" % tsname
            ts = TestSuite(name = tsname, description = "")
            ts.save()
        print "Adding TestCase to TestSuite %s " % tsname
        
        TestCase(suite = ts, test_name = tcname, seq = test_id, test_params = str(get_default_params(active_ap, sta_ip)),
                 common_name = 'AssocPing 1(AP %s - STA %s): Auth(Open) Encryption(None)' % (active_ap, sta_ip)).save() 
        test_id = test_id + 1
        for auth in auth_list:
            if auth in auth_list[0:2]:
                for encryption in encryption_list[0:3]:
                    for key_index in [1, 2, 3, 4]:          
                        test_params = get_default_params(active_ap, sta_ip)      
                        test_params['wlan_cfg']['key_index'] = str(key_index)
                        test_params['wlan_cfg']['auth'] = auth
                        test_params['wlan_cfg']['encryption'] = encryption                
                        test_params['wlan_cfg']['sta_auth'] = auth
                        test_params['wlan_cfg']['sta_encryption'] = encryption
        
                        if encryption == 'Auto':
                            pass
                        else:
                            test_params['wlan_cfg']['key_string'] = utils.make_random_string({'WEP-64':10, 'WEP-128':26}[encryption], "hex")
                            common_name = "AssocPing %d (AP %s - STA %s): Auth(%s) Encryption(%s) Key Index(%d)" % (test_id, active_ap, sta_ip, auth, encryption, key_index)                                                        
                            TestCase(suite = ts, test_name = tcname, seq = test_id, test_params = str(test_params), common_name = common_name).save()
                            test_id = test_id + 1
            else:        
                for encryption in encryption_list[2:]:
                    if encryption == 'Auto':
                        pass
                    else:
                        for wpa_ver in wpa_ver_list:
                            test_params = get_default_params(active_ap, sta_ip)
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
                                    test_params['wlan_cfg']['ras_addr'] = '192.168.0.252'
                                    test_params['wlan_cfg']['use_radius'] = True
                                    test_params['wlan_cfg']['use_onex'] = True
                                    test_params['wlan_cfg']['username'] = 'rat_user'
                                    test_params['wlan_cfg']['password'] = 'rat_user'   
        
                                common_name = "AssocPing %d (AP %s - STA %s): Auth(%s) Encryption(%s) %s" % (test_id, active_ap, sta_ip, auth, encryption, wpa_ver)                                                                
                                TestCase(suite = ts, test_name = tcname, seq = test_id, test_params = str(test_params), common_name = common_name).save()
                                test_id = test_id + 1         

# AutotestConfig: must be added to test the newly added test suite with a specific build stream    
for i in range(len(bsname_list)): 
    lastbuildnum = {'ZF2925_6.0.0.0_production':120, 'ZF7942_6.0.0.0_production':35}[bsname_list[i]]
    dut = {'ZF2925_6.0.0.0_production':'ZF2925', 'ZF7942_6.0.0.0_production':'ZF7942'}[bsname_list[i]]    
    at = AutotestConfig(testbed = Testbed.objects.get(name = tb_cfg['name']),
                        build_stream = BuildStream.objects.get(name = bsname_list[i]),
                        lastbuildnum = lastbuildnum, DUT = TestbedComponent.objects.get(name = dut),
                        order = i)

    at.save()
    for sta_ip in sta_ip_list:
        tsname = 'AssocPing (AP: %s - STA %s)' % (dut, sta_ip)
        at.suites.add(TestSuite.objects.get(name = tsname))

