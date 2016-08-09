'''
Title: Combination Basic - Packet Inspection Filter

Test purpose: Verify PIF in the combination with other modules
    
Expect result: The features in PIF can work well in the cooperative work with other modules
    
TestCase steps:
1) Initiate environment;
2) Enable Mesh and ABF;
3) Enable PIF rate limit and set the rate value;
4) Create wlan1 with Proxy ARP on;
5) Create wlan2 with Proxy ARP off;
6) Create wlan3 with tunnel on;
7) Backup the configuration;
8) Set ZD to factory default;
9) Restore the backup configuration;
10) Check PIF rate limit status;
11) Check PIF service status of the three wlans.
    
Created on 2012-11-22
@author: sean.chen@ruckuswireless.com
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    
    ap1_tag = 'ap1'
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Initiate environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap1'],
                       'ap_tag': ap1_tag}, test_name, common_name, 0, False))
    
#---TestCase_1-----------------------------------------------------------------------------------    
    test_case_name = 'Configuration save and restore'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = '%sEnable Mesh' % (test_combo_case_name,)
    test_cfgs.append(({'mesh_ap_mac_list': []}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_ABF'
    common_name = '%sEnable ABF' % (test_combo_case_name,)
    test_cfgs.append(({'do_abf': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sConfigure PIF rate limit' % test_combo_case_name
    test_params = {'expected_status': True, 
                   'expected_rate_limit': 1000, 
                   'expect_config_done': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate wlan1 on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate wlan2 on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': False, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate wlan3 on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_tunnel': True})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Backup'
    common_name = '%sBackup the configuration' % (test_combo_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sSet ZD to factory default status' % (test_combo_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the configuration' % (test_combo_case_name,)
    test_params = {'restore_type': 'restore_everything_except_ip'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck PIF rate limit' % test_combo_case_name 
    test_params = {'expected_status': True, 
                   'expected_rate_limit': 1000, 
                   'check_only': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify wlan1 PIF service status on AP' % (test_combo_case_name,)
    test_params = {'ap_tag': ap1_tag, 
                   'bridge': 'br0', 
                   'wlan_name_list': ['wlan0'], 
                   'expected_status': 'p'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify wlan2 PIF service status on AP' % (test_combo_case_name,)
    test_params = {'ap_tag': ap1_tag, 
                   'bridge': 'br0', 
                   'wlan_name_list': ['wlan1'], 
                   'expected_status': 'd'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify wlan3 PIF service status on AP' % (test_combo_case_name,)
    test_params = {'ap_tag': ap1_tag, 
                   'bridge': 'br6', 
                   'wlan_name_list': ['wlan2'], 
                   'expected_status': 'n'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD after case: %s' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = 'Disable PIF rate limit after case: %s' % (test_case_name) 
    test_cfgs.append(({'expected_status': False, 'expect_config_done': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_ABF'
    common_name = 'Disable ABF after case: %s' % (test_case_name)
    test_cfgs.append(({'do_abf': False}, test_name, common_name, 0, False))

#---TestCases End--------------------------------------------------------------------------------
    return test_cfgs

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station = (0, "g"),
                  targetap = False,
                  testsuite_name = "")
    ts_cfg.update(kwargs)

    wlan_cfg = {'ssid': 'standard_wlan_for_test', 
                'type': 'standard',
                'auth': 'open', 
                'encryption': 'none', 
                'sta_auth': 'open', 
                'sta_encryption': 'none',
                'do_proxy_arp': None,
                'do_tunnel': None,
                }

    tcfg = {'radio_mode': ['ng'],
            'active_ap1':'AP_01',
            'wlan_cfg': wlan_cfg}

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'Combination Basic - Packet Inspection Filter'

    ts = testsuite.get_testsuite(
        ts_name, 'Combination basic test in Packet Inspection Filter.',
        interactive_mode = ts_cfg["interactive_mode"],
        combotest = True)

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
    create_test_suite(**_dict)
    