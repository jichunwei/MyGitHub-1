'''
Title: Proxy ARP for per WLAN Basic - Packet Inspection Filter

Test purpose: Verify Proxy ARP basic mechanism for per wlan in PIF
    
Expect result: Proxy ARP status for per wlan is as expected
    
TestCase steps:
1) Create two wlans with proxy arp off (by GUI);
2) Check the proxy arp status of the two wlans;
3) Set the proxy arp of wlan1 on (by CLI)
4) Check the proxy arp status of the two wlans again. 
    
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
    test_case_name = 'Proxy ARP on_off base on wlan interface'
    test_combo_case_name = "[%s]" % (test_case_name)
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate wlan1 on ZD' % (test_combo_case_name)
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    ssid_1 = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid_1, 'do_proxy_arp': False, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg], 'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify wlan1 on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate wlan2 on ZD' % (test_combo_case_name)
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid_2 = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid_2, 'do_proxy_arp': False, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg], 'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify wlan2 on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify all wlans proxy arp info on AP' % (test_combo_case_name)
    test_params = {'ap_tag': ap1_tag, 'bridge': 'br0', 'expected_status': 'n'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sEnable Proxy ARP in wlan1 by ZD CLI' % (test_combo_case_name)
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    wlan_cfg.update({'ssid': ssid_1, 'name': ssid_1, 'do_proxy_arp': True})
    test_cfgs.append(({'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify wlan1 proxy arp info on AP' % (test_combo_case_name)
    test_params = {'ap_tag': ap1_tag, 
                   'bridge': 'br0', 
                   'wlan_name_list': ['wlan0'], 
                   'waiting_time': 10, 
                   'expected_status': 'p'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify wlan2 proxy arp info on AP' % (test_combo_case_name)
    test_params = {'ap_tag': ap1_tag, 
                   'bridge': 'br0', 
                   'wlan_name_list': ['wlan1'],
                   'expected_status': 'n'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD after case: %s' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 0, False))

#---TestCases End--------------------------------------------------------------------------------
    return test_cfgs

def _define_expect_wlan_info_in_ap(tcfg, wlan_cfg):
    if type(tcfg['radio_mode']) == list:
        radio_mode_list = tcfg['radio_mode']

    else:
        radio_mode_list = [tcfg['radio_mode']]

    expect_wlan_info = dict()
    for radio in radio_mode_list:
        status = 'up'
        if radio in ['bg', 'ng']:
            radio_mode_key = '24g'
        elif radio in ['na']:
            radio_mode_key = '5g'
        expect_wlan_info.update({radio_mode_key: {'wlan_tag1': {}}})
        expect_wlan_info[radio_mode_key]['wlan_tag1']['status'] = status
        expect_wlan_info[radio_mode_key]['wlan_tag1']['encryption_cfg'] = dict(ssid = wlan_cfg['ssid'])

    return expect_wlan_info

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

    tcfg = {'radio_mode': ['ng', 'na'],
            'active_ap1':'AP_01',
            'wlan_cfg': wlan_cfg}

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'Proxy ARP for per WLAN Basic - Packet Inspection Filter'

    ts = testsuite.get_testsuite(
        ts_name, 'Verify Proxy ARP for per WLAN basic in Packet Inspection Filter.',
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
    