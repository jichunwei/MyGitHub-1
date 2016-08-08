"""
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


import sys
import time
from copy import deepcopy
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


GP_RANGE = (1, 144000)


def verify_gp_in_wlan(tcid, wlan_cfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sConfigure grace period in GUI' % tcid
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_Grace_Period_In_WLAN'
    common_name = '%sVerify grace period in CLI' % tcid
    test_cfgs.append(({'gui_wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    return test_cfgs


def verify_gp_in_profile(tcid, hotspot_cfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = '%sConfigure grace period in GUI' % tcid
    test_cfgs.append(({'hotspot_profiles_list': [hotspot_cfg]}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_Grace_Period_In_Hotspot'
    common_name = '%sVerify grace period in CLI' % tcid
    test_cfgs.append(({'gui_hotspot_cfg': hotspot_cfg}, 
                      test_name, common_name, 2, False))
    
    return test_cfgs


def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Profiles'
    common_name = 'Remove all hotspot profiles'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    tcid = "[Enable grace period in web auth WLAN]"
    wlan_cfg = deepcopy(tcfg['web_auth_wlan_cfg'])
    wlan_cfg['ssid'] = "web-gp-enable-%s" % time.strftime("%H%M%S")
    wlan_cfg['do_grace_period'] = True
    wlan_cfg['grace_period'] = random.randint(GP_RANGE[0], GP_RANGE[1])
    test_cfgs.extend(verify_gp_in_wlan(tcid, wlan_cfg))
    
    tcid = "[Disable grace period in web auth WLAN]"
    wlan_cfg = deepcopy(tcfg['web_auth_wlan_cfg'])
    wlan_cfg['ssid'] = "web-gp-disable-%s" % time.strftime("%H%M%S")
    wlan_cfg['do_grace_period'] = False
    test_cfgs.extend(verify_gp_in_wlan(tcid, wlan_cfg))
    
    tcid = "[Enable grace period in guest access WLAN]"
    wlan_cfg = deepcopy(tcfg['guest_access_wlan_cfg'])
    wlan_cfg['ssid'] = "guest-gp-enable-%s" % time.strftime("%H%M%S")
    wlan_cfg['do_grace_period'] = True
    wlan_cfg['grace_period'] = random.randint(GP_RANGE[0], GP_RANGE[1])
    test_cfgs.extend(verify_gp_in_wlan(tcid, wlan_cfg))

    tcid = "[Disable grace period in guest access WLAN]"
    wlan_cfg = deepcopy(tcfg['guest_access_wlan_cfg'])
    wlan_cfg['ssid'] = "guest-gp-disable-%s" % time.strftime("%H%M%S")
    wlan_cfg['do_grace_period'] = False
    test_cfgs.extend(verify_gp_in_wlan(tcid, wlan_cfg))
    
    tcid = "[Enable grace period in hotspot profile]"
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = "wispr-gp-enable-%s" % time.strftime("%H%M%S")
    hotspot_cfg['idle_timeout'] = random.randint(GP_RANGE[0], GP_RANGE[1])
    test_cfgs.extend(verify_gp_in_profile(tcid, hotspot_cfg))
    
    tcid = "[Disable grace period in hotspot profile]"
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = "wispr-gp-disable-%s" % time.strftime("%H%M%S")
    hotspot_cfg['idle_timeout'] = None
    test_cfgs.extend(verify_gp_in_profile(tcid, hotspot_cfg))
    
    
    test_name = 'CB_ZD_Remove_All_Profiles'
    common_name = 'Remove all hotspot profiles to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)

    testsuite.getTestbed2(**kwargs)
    
    web_auth_wlan_cfg = {
        'ssid': "",
        'auth': "open", 
        'encryption': "none",
        'do_webauth': True,
        }

    guest_access_wlan_cfg = {
        'ssid': "",
        'type': "guest",
        'auth': "open", 
        'encryption': "none",
        }
    
    hotspot_cfg = {
        'name': "",
        'login_page': "https://192.168.0.250/slogin.html",
        }

    tcfg = {'web_auth_wlan_cfg': web_auth_wlan_cfg,
            'guest_access_wlan_cfg': guest_access_wlan_cfg,
            'hotspot_cfg': hotspot_cfg,
            }
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "ZD CLI - Show Grace Period" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the Grace Period information shown in ZD CLI is correct" ,
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
    