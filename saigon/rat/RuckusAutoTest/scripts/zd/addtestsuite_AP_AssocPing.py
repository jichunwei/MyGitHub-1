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
import time
import random

#
# setup django environment
#
from django.core.management import setup_environ

os.chdir("../../../")
sys.path.append(os.getcwd())
from RuckusAutoTest.common import Ratutils as utils
import settings
setup_environ(settings)

# import RAT models
import libZD_TestSuite as testsuite
from RuckusAutoTest.models import Testbed, TestbedType, TestSuite 
from RuckusAutoTest.testbeds import *
from RuckusAutoTest.tests.zd import *

from django.core.exceptions import ObjectDoesNotExist

# Testbed: specify the name and details required
tb_name = raw_input("Testbed name: ")
try:
    tb = Testbed.objects.get(name = tb_name)
except ObjectDoesNotExist:
    tb_location = raw_input("Testbed location: ")
    tb_owner = raw_input("Testbed owner (email address): ")
    ap_list = raw_input("AP list in format ap_type:ip_address (separated by spaces): ")
    ftp_svr_cfg = {'ip_addr':'192.168.0.21',
                   'protocol':'FTP',
                   'username':'anonymous',
                   'password':'anonymous',
                   'rootpath':'c:\\\\tftpboot'}    
    ap_conf = {'username':'super', 'password':'sp-admin', 'ftpsvr': ftp_svr_cfg}
    print "Select your test bed type: "
    print "1 - 'AP_Stations'"
    print "2 - 'AP_Single_Station' (use this test bed if your test engine PC has wireless adaptor and running Windows)\n" 
    tbt_id = raw_input("Pick a testbed type in the list above [1]: ")
    if not tbt_id or int(tbt_id) == 1:
        tbt = TestbedType.objects.get(name = 'AP_Stations')
        sta_ip_list = raw_input("Station IP list (separated by spaces): ")    
        config = {'ap_conf':ap_conf, 'sta_ip_list':sta_ip_list.split()}        
    elif int(tbt_id) == 2:
        tbt = TestbedType.objects.get(name = 'AP_Single_Station')
        sta_ip_list = raw_input("Station IP address: ")    
        config = {'ap_conf':ap_conf, 'sta_ip_addr':sta_ip_list.split()}
    else:
        raise Exception("Testbed type entered is not in the list")

    for ap in ap_list.split():
        ap_model = ap.split(":")[0]
        ap_ip_addr = ap.split(":")[1]
        config[ap_model.upper()] = {'ip_addr':ap_ip_addr}
        
    # Testbed: specify the name and details required    
    testbed = {'name':tb_name, 'tbtype': tbt,
               'location':tb_location, 'owner':tb_owner, 'resultdist':tb_owner, 'config':str(config)}
    tb = Testbed(**testbed)
    tb.save()     

# TestSuite: specify the name and test cases in it
def get_default_params(active_ap, target_sta, dest_ip_addr):
    default_test_params = {'ip': dest_ip_addr,
                   'active_ap':active_ap,
                   'target_station':target_sta,
                   'wlan_cfg': {'username': '', 'ssid': 'RAT-%s' % time.strftime("%H%M%S"),
                                'ras_secret': '', 'ras_port': '', 'key_string': '', 'key_index': '', 'auth': 'open',
                                'ras_addr': '', 'use_radius': False, 'encryption': 'none',
                                'password': '', 'wlan_if': 'wlan0', 'wpa_ver': '', 'sta_wpa_ver': '',
                                'sta_auth': 'open', 'sta_encryption': 'none', }, 'timeout': 180}
    return default_test_params
# end get_default_params
auth_list = ['open', 'shared', 'PSK', 'EAP']
encryption_list = ['WEP-64', 'WEP-128', 'Auto', 'TKIP', 'AES']
wpa_ver_list = ['WPA', 'WPA2']
tcname = 'AssocPing'

# get config from testbed to generate AssocPing test cases
tb_config = eval(tb.config)
if tb_config.has_key('sta_ip_list'):
    sta_ip_list = tb_config['sta_ip_list']
    del tb_config['sta_ip_list']
elif tb_config.has_key('sta_ip_addr'):
    sta_ip_list = tb_config['sta_ip_addr']
    del tb_config['sta_ip_addr']
    
    
del tb_config['ap_conf']

for ap in tb_config.keys():   
    
    active_ap = raw_input("MAC Address of AP %s - %s (using format XX:XX:XX:XX:XX:XX) : " 
                          % (ap, tb_config[ap]['ip_addr']))
    print "Authentication supported by %s: " % ap
    support_auth_list = []
    for auth in auth_list:
        input = raw_input("Does %s support authentication %s? [y]/n: " % (ap, auth))
        if not input or input.upper() == 'Y' or input.upper() == "YES":
            support_auth_list.append(auth)
            
    print "Encryption supported by %s: " % ap        
    support_encrypt_list = []
    for encrypt in encryption_list:
        input = raw_input("Does %s support encryption %s? [y]/n: " % (ap, encrypt))
        if not input or input.upper() == 'Y' or input.upper() == "YES":        
            support_encrypt_list.append(encrypt)  
    
    
    # default test_params for none encryption
    tcs = []
    test_order = 1
    test_added = 0
    
    ip_list = []
    for i in range(len(sta_ip_list)):
        ip_list.append("(%d) - %s" % (i, sta_ip_list[i]))
    print "Station IP list:"
    print "; ".join(ip_list)
    id = raw_input("Pick an IP in the list above: ")
    sta_ip = sta_ip_list[int(id)]   
    
    dest_ip_addr = raw_input("Destination IP address used in ping test[192.168.0.252]: ")
    if dest_ip_addr == "":
        dest_ip_addr = "192.168.0.252"
    
    tsname = 'AssocPing'
    print "Adding TestSuite %s " % tsname
    try:
        ts = TestSuite.objects.get(name = tsname)
        print "TestSuite '%s' is already in database." % tsname
    except ObjectDoesNotExist:
        print "TestSuite '%s' is not found in database; adding...\n" % tsname
        ts = TestSuite(name = tsname, description = "")
        ts.save()
    print "Adding TestCase to TestSuite %s " % tsname
    if 'open' in support_auth_list:
        common_name = 'AP_ASSOCPING_%04d' % test_order
        test_params = str(get_default_params(active_ap, sta_ip, dest_ip_addr))    
        if testsuite.addTestCase(ts, tcname, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        
        test_order = test_order + 1
    for auth in auth_list:
        if auth in auth_list[0:2]:
            if auth in support_auth_list:
                for encryption in encryption_list[0:3]:
                    if encryption in support_encrypt_list:
                        for key_index in [1, 2, 3, 4]:          
                            test_params = get_default_params(active_ap, sta_ip, dest_ip_addr)      
                            test_params['wlan_cfg']['key_index'] = str(key_index)
                            test_params['wlan_cfg']['auth'] = auth
                            test_params['wlan_cfg']['encryption'] = encryption                
                            test_params['wlan_cfg']['sta_auth'] = auth
                            test_params['wlan_cfg']['sta_encryption'] = encryption
            
                            if encryption == 'Auto':
                                pass
                            else:
                                test_params['wlan_cfg']['key_string'] = utils.make_random_string({'WEP-64':10,
                                                                                          'WEP-128':26}[encryption], "hex")
                                common_name = 'AP_ASSOCPING_%04d' % test_order 
                                if testsuite.addTestCase(ts, tcname, common_name, test_params, test_order) > 0:
                                    test_added += 1
                                test_order += 1
                                
        elif auth in support_auth_list:        
            for encryption in encryption_list[2:]:
                if encryption in support_encrypt_list:
                    if encryption == 'Auto':
                        pass
                    else:
                        for wpa_ver in wpa_ver_list:
                            test_params = get_default_params(active_ap, sta_ip, dest_ip_addr)
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
        
                                common_name = 'AP_ASSOCPING_%04d' % test_order
                                if testsuite.addTestCase(ts, tcname, common_name, test_params, test_order) > 0:
                                    test_added += 1
                                test_order += 1      
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

