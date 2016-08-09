"""
HW Acceleration for LWAPP tunnel encryption
    
    expect result: All steps should result properly.
    
    How to:
        1)  Clean ZD environment
        2)  Create active AP
        3)  Verify ZD crypto information
        4)  Verify active AP crypto information
        5)  Enable HW Acceleration option on ZD service page
        6)  Create an open-none WLAN with tunnel enabled
        7)  Client associates to WLAN and ping from client to target Linux server
        8)  Verify active AP interrupts information
        9)  Disable HW Acceleration option on ZD service page
        10) Clean ZD environment

Created on 2012-12-25
@author: kevin.tan
"""

import os
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

check_wlan_timeout = 5

def define_test_cfg(cfg):
    test_cfgs = []
    
    ap_model = cfg['ap_model']
    ap_tag = 'ap_bandswitch'

    radio_mode = cfg['radio_mode']
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    sta_tag = 'sta%s' % radio_mode
    target_ip_addr = cfg['target_ip_addr']
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    ####################### TEST CASE I ###############################
    test_case_name = "[Verify ZD crypto info]"
    
    test_name = 'CB_ZD_Verify_HW_Acceleration'
    common_name = '%sVerify ZD crypto information' % (test_case_name)
    test_cfgs.append(({'device': 'ZD5K', 'ap_tag': ap_tag, 'type': 'check_crypto'}, test_name, common_name, 1, False))

    ####################### TEST CASE II ###############################
    test_case_name = "[Verify AP crypto info]"
    test_name = 'CB_ZD_Verify_HW_Acceleration'
    common_name = '%sVerify AP crypto information' % (test_case_name)
    test_cfgs.append(({'device': 'AP', 'ap_tag': ap_tag, 'type': 'check_crypto'}, test_name, common_name, 1, False))

    ####################### TEST CASE III ###############################
    test_case_name = "[Verify AP interrupts info]"
    wlan_cfg = dict(ssid='HW-Acceleration-LWAPP-tunnel', auth="open", encryption="none", do_tunnel=True)

    test_name = 'CB_ZD_Set_HW_Acceleration_Option'
    common_name = '%sEnable HW Acceleration option on ZD service page' % (test_case_name)
    test_cfgs.append(({'operation': 'enable'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate WLAN with tunnel enabled' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_HW_Acceleration'
    common_name = '%sVerify ZD interupts information' % (test_case_name)
    test_cfgs.append(({'device': 'AP', 'ap_tag': ap_tag, 'type': 'check_interrupts'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    ####################### TEST CASE end ###############################
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Set_HW_Acceleration_Option'
    common_name = 'Disable HW Acceleration option on ZD service page'
    test_cfgs.append(({'operation': 'disable'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove the wlan from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
  
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    model = ''
    while(True):
        if ts_cfg["interactive_mode"]:
            target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
            target_sta_radio = testsuite.get_target_sta_radio()
            active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        else:
            target_sta = sta_ip_list[ts_cfg["station"][0]]
            target_sta_radio = ts_cfg["station"][1]
            if kwargs["targetap"]:
                active_ap_list = sorted(ap_sym_dict.keys())

        model = ap_sym_dict[active_ap_list[0]]['model'].lower() 
        if  model == 'zf7982' or model == 'zf7782' or model == 'zf7782-s':
            break
    
        print("Appointed AP doesn't support HW Acceleration for LWAPP tunnel encryption(should among zf7982, zf7782, zf7782-s), select is again:\n\n\n")

    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'ap_model': model,
            'target_ip_addr': '172.16.10.252',
            }
    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "HW Acceleration for LWAPP tunnel encryption for %s" % (model)

    ts = testsuite.get_testsuite(ts_name, "HW Acceleration for LWAPP tunnel encryption" , combotest=True)

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
