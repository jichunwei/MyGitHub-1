"""
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def define_wlan_cfg():
    wlan_cfgs = []    

    wlan_cfgs.append(dict(ssid = 'OPEN-WPA-DVLAN', auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "", use_radius = ""))    
    return wlan_cfgs


def define_test_cfg(active_ap):
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify the active AP'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'active_ap': active_ap}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Reconnect_AP_By_LWAPP'
    common_name = '[L3 Join] Reconnect AP to ZD as L3 mode'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'mode': 'l3',
                       }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_External_IP_Port'
    common_name = '[L3 Join] Verify the AP external IP and Port'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_ext_ip': '',
                       'expected_ext_port': '12223'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = '[AP Manual IP setting] configure AP use static IP'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'ip_cfg': {'ipv4': {'pri_dns': '192.168.0.252', 
                                            'net_mask': '255.255.255.0', 
                                            'ip_addr': '192.168.33.123', 
                                            'gateway': '192.168.33.253', 
                                            'ip_mode':'manual'}
                                  }
                       }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_External_IP_Port'
    common_name = '[AP Manual IP setting] Verify the AP external IP and Port'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_ext_ip': '',
                       'expected_ext_port': '12223'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = '[AP DHCP IP setting] configure AP use DHCP'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'ip_cfg': {'ipv4':{'ip_mode': 'dhcp'}}}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_External_IP_Port'
    common_name = '[AP DHCP IP setting] Verify the AP external IP and Port'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_ext_ip': '',
                       'expected_ext_port': '12223'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Reboot'
    common_name = '[Reboot ZD] Reboot the ZoneDirector'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '[Reboot ZD] Verify all AP reconnect to ZD'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_External_IP_Port'
    common_name = '[Reboot ZD] Verify the AP external IP and Port'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'expected_ext_ip': '',
                       'expected_ext_port': '12223'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Reconnect_AP_By_LWAPP'
    common_name = 'Cleanup by reconnect AP to ZD as L2 mode'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'mode': 'l2',
                       }, test_name, common_name, 0, False))
             
    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap = testsuite.getActiveAp(ap_sym_dict)[0]
    
    test_cfgs = define_test_cfg(active_ap)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "KDDI - AP External IP/Port"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the AP external IP and Port information on ZD WebUI",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
       
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
    