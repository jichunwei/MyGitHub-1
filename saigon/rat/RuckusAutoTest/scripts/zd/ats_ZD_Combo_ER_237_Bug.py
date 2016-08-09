'''
https://jira.ruckuswireless.com/browse/ER-237
How to Test:
    -Create a WLAN with essid_name != wlan_name
    -Pick up a client to associate it.
    -Open WLAN monitor page and make sure client are shown in client list.
    
Created on 2012-11-22
@author: cwang@ruckuwireless.com
'''

from copy import deepcopy
import time
import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = dict(ssid = "rat-wlan-%s" % (time.strftime("%H%M%S")),
                name = "rat-wlan-er237",
                auth = "open",                 
                encryption = "none",                 
                )


def _setup_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_Remove_All_Wlans',
                'Remove all WLANs.',
                0,
                False
                ))

    return tcs

def _teardown_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_Remove_All_Wlans',
                'Clean up all WLANs.',
                0,
                True
                ))
        
    return tcs

def build_tcs(target_station):
    tcs = []
    tcs.extend(_setup_tcs())
    
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_Create_Wlans',
                'Create WLAN',
                0,
                False
                ))
    
    sta_tag = "sta_1"
    tcs.append(({'sta_ip_addr': target_station,
                       'sta_tag': sta_tag}, 
                       'CB_ZD_Create_Station', 
                       'Create target wireless station',
                        0, 
                        False))

    tcs.append(({'sta_tag': sta_tag}, 
                      'CB_Station_Remove_All_Wlans', 
                      'Remove all WLANs on station', 
                      0, 
                      False))
    
    tcid = "[er237]"
    _cfg = deepcopy(wlan_cfg)
    _cfg.update({'ssid':wlan_cfg['name']})
    tcs.append(({'wlan_cfg': _cfg,
                       'sta_tag': sta_tag}, 
                       'CB_ZD_Associate_Station_1', 
                       '%sAssociate the station' % tcid,
                       1,
                       False))
        
    tcs.append(({'sta_tag': sta_tag},
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      '%sGet wifi address of the station' % tcid, 
                      2,
                      False)) 
    
    tcs.append(({
            'wlan_name':wlan_cfg['ssid'],
            'sta_tag':sta_tag,
            'info':{}},
            'CB_ZD_Verify_Client_Info_In_Wlan_Detail_Page',
            '%sVerify Client Info' % tcid,
            2,
            False
            ))
    
    tcs.extend(_teardown_tcs())
    return tcs


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "ER-237 Regression",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
        
    if attrs["interactive_mode"]:        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:        
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
       
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    ap_mac_addr = None
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            ap_mac_addr = ap_info.get('mac')            
            break
        
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    
    ts_name_list = [('ER-237 Regression', build_tcs),                                                            
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(sta_ip_addr)
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
    


def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)

