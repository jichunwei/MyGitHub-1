'''
Title: Get_Sta_OS_and_Hostname_via_DHCP_WLAN_Shift

Test purpose: Verify if ZD can get station OS type and hostname information correctly after moving the wlan from current AP to another.
    
Expect result: Station OS type and hostname obtained by ZD should be matched with the actual information on station.
    
Steps:
1) Initiate configuration on ZD and station
2) Config all APs radio - Enable WLAN service
3) Create two wlan groups
4) Configure a standard wlan
5) Assign the wlan to wlan group_1
6) Assign AP_01 to wlan group_1
7) Associate the station to the wlan
8) Get wifi address of the station
9) Verify station wifi ip address in expected subnet
10) Verify the station OS type information on ZD
11) Verify the station host name information on ZD
12) Assign AP_02 to wlan group_2
13) Assign the wlan to wlan group_2
12) Remove the wlan out of wlan group_1
14) Get wifi address of the station
15) Verify station wifi ip address in expected subnet
16) Verify the station OS type information on ZD
17) Verify the station host name information on ZD
18) Clean configuration on ZD and station

Created on 2012-9-6
@author: sean.chen@ruckuswireless.com
'''

import sys
import time
#import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    radio_mode = cfg['radio_mode']
    sta_tag = 'sta-%s' % radio_mode
    target_sta_ip = cfg['target_station']
    
    wg_cfg_01 = cfg['wg_cfg_01']
    wg_cfg_02 = cfg['wg_cfg_02']

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wireless station'
    test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WLANs on station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Enable WLAN service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP_01'
    test_cfgs.append(({'active_ap': 'AP_01',
                       'ap_tag': 'AP_01'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP_02'
    test_cfgs.append(({'active_ap': 'AP_02',
                       'ap_tag': 'AP_02'}, test_name, common_name, 0, False))

#---TestCase---------------------------------------------------------------------------------------
    test_case_name_list = ['Client Fingerprinting on, option82 off', 
                           'Client Fingerprinting on, option82 on',]
    
    for test_case_name in test_case_name_list:
        
        test_combo_case_name = "[%s]" % test_case_name
        
        test_name = 'CB_ZD_Create_New_WlanGroup'
        common_name = "%sCreate wlan group_1: %s" % (test_combo_case_name, wg_cfg_01['name']) 
        test_cfgs.append(({'wgs_cfg': wg_cfg_01}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Create_New_WlanGroup'
        common_name = "%sCreate wlan group_2: %s" % (test_combo_case_name, wg_cfg_02['name']) 
        test_cfgs.append(({'wgs_cfg': wg_cfg_02}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sConfigure a wlan on ZD' % test_combo_case_name
        
        wlan_cfg = {}
        wlan_cfg.update(cfg['wlan_cfg'])
        
        if test_combo_case_name == '[Client Fingerprinting on, option82 off]':
            wlan_cfg.update({'fingerprinting': True, 'option82': False})
            
        elif test_combo_case_name == '[Client Fingerprinting on, option82 on]':
            wlan_cfg.update({'fingerprinting': True, 'option82': True})
        
        test_params = {'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': False}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
        common_name = '%sAssign the wlan to wlan group %s' % (test_combo_case_name, wg_cfg_01['name'])
        test_params = {'wlangroup_name': wg_cfg_01['name'], 'wlan_name_list': [wlan_cfg['ssid']]}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = '%sAssign AP_01 to wlan group %s' % (test_combo_case_name, wg_cfg_01['name'])
        test_params = {'active_ap': 'AP_01', 
                       'wlan_group_name': wg_cfg_01['name'], 
                       'radio_mode': radio_mode}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP_01' % (test_combo_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': 'AP_01'}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station to the wlan' % (test_combo_case_name,)
        test_cfgs.append(({'wlan_cfg': wlan_cfg,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet wifi address of the station' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False)) 
        
        test_name = 'CB_Station_Verify_Expected_Subnet'
        common_name = '%sVerify station wifi ip address in expected subnet' % (test_combo_case_name,)
        expected_subnet = cfg['expected_subnet']
        expected_sub_mask = cfg['expected_sub_mask']
        test_cfgs.append(({'sta_tag': sta_tag,
                           'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                          test_name, common_name, 2, False))

        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP' % (test_combo_case_name,)
        target_ip_addr = cfg['switch_ip_addr']
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify the station information on ZD' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': 'AP_01',
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg,
                           'radio_mode': radio_mode,
                           },
                           test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
        common_name = '%sVerify the station information on AP_01' % (test_combo_case_name,)
        test_cfgs.append(({'ssid': wlan_cfg['ssid'],
                           'ap_tag': 'AP_01',
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_OS_Type_Info'
        common_name = '%sVerify the station OS type information on ZD' % (test_combo_case_name,)
        test_params = {'sta_tag': sta_tag, 'sta_ip_addr':target_sta_ip, 'expect_get_sta_os': True,}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_Host_Name_Info'
        common_name = '%sVerify the station host name information on ZD' % (test_combo_case_name,)
        test_params = {'sta_tag': sta_tag, 'sta_ip_addr':target_sta_ip, 'expect_get_sta_hn': True,}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = '%sAssign AP_02 to wlan group %s' % (test_combo_case_name, wg_cfg_02['name'])
        test_params = {'active_ap': 'AP_02', 
                       'wlan_group_name': wg_cfg_02['name'], 
                       'radio_mode': radio_mode}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
        common_name = '%sAssign the wlan to wlan group %s' % (test_combo_case_name, wg_cfg_02['name'])
        test_params = {'wlangroup_name': wg_cfg_02['name'], 'wlan_name_list': [wlan_cfg['ssid']]}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
        common_name = '%sRemove the wlan from wlan group %s' % (test_combo_case_name, wg_cfg_01['name'])
        test_params = {'wgs_cfg': wg_cfg_01, 'wlan_list': [wlan_cfg['ssid']]}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP_02' % (test_combo_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': 'AP_02'}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet wifi address of the station again' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False)) 
        
        test_name = 'CB_Station_Verify_Expected_Subnet'
        common_name = '%sVerify station wifi ip address in expected subnet again' % (test_combo_case_name,)
        expected_subnet = cfg['expected_subnet']
        expected_sub_mask = cfg['expected_sub_mask']
        test_cfgs.append(({'sta_tag': sta_tag,
                           'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                          test_name, common_name, 2, False))

        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP again' % (test_combo_case_name,)
        target_ip_addr = cfg['switch_ip_addr']
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify the station information on ZD again' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': 'AP_02',
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg,
                           'radio_mode': radio_mode,
                           },
                           test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
        common_name = '%sVerify the station information on AP_02' % (test_combo_case_name,)
        test_cfgs.append(({'ssid': wlan_cfg['ssid'],
                           'ap_tag': 'AP_02',
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_OS_Type_Info'
        common_name = '%sVerify the station OS type information on ZD again' % (test_combo_case_name,)
        test_params = {'sta_tag': sta_tag, 'sta_ip_addr':target_sta_ip, 'expect_get_sta_os': True}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_Host_Name_Info'
        common_name = '%sVerify the station host name information on ZD again' % (test_combo_case_name,)
        test_params = {'sta_tag': sta_tag, 'sta_ip_addr':target_sta_ip, 'expect_get_sta_hn': True}
        test_cfgs.append((test_params, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Remove_All_Wlan_Groups'
        common_name = '%sSet AP and wlan group to default status after case' % (test_combo_case_name,)
        test_cfgs.append(({'wlan_name_list': [wlan_cfg['ssid']]}, test_name, common_name, 2, True))
        
#---TestCase End-----------------------------------------------------------------------------------
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove the WLAN on station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
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
            wlan_name = "wlan0"
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid = wlan_cfg['ssid'])

        elif radio in ['na']:
            MAXIMUM_WLAN = 8
            wlan_name = "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid = wlan_cfg['ssid'])

    return expect_wlan_info

def create_test_suite(**kwargs):
    ts_cfg = dict(
        interactive_mode = True,
        station = (0, "g"),
        targetap = False,
        testsuite_name = "",
    )
    ts_cfg.update(kwargs)

    tb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)
   
    switch_ip_addr = testsuite.getTestbedSwitchIp(tbcfg)

    sta_ip_list = tbcfg['sta_ip_list']

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()

    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
    
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg = {'ssid': ssid, 
                'type': 'standard',
                'auth': 'open', 
                'encryption': 'none', 
                'sta_auth': 'open', 
                'sta_encryption': 'none',
                'option82':None,
                'fingerprinting':None,
                }
    wg_cfg_01 = {'name': 'wg_01_%s' % time.strftime("%H%M%S"),
                 'description': 'WLAN group_1 for AP shift',
                 'vlan_override': False,
                 'wlan_member': {},
                }
    wg_cfg_02 = {'name': 'wg_02_%s' % time.strftime("%H%M%S"),
                 'description': 'WLAN group_2 for AP shift',
                 'vlan_override': False,
                 'wlan_member': {},
                }
    tcfg = {
            'switch_ip_addr': switch_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'wlan_cfg': wlan_cfg,
            'wg_cfg_01': wg_cfg_01,
            'wg_cfg_02': wg_cfg_02,
            'expected_sub_mask': '255.255.255.0',
            'expected_subnet': utils.get_network_address(ras_ip_addr, '255.255.255.0'),
            'username': 'local.user',
            'password': 'local.user',
            }

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'WLAN Shift - Get Sta OS and Hostname via DHCP - Basic'

    ts = testsuite.get_testsuite(
        ts_name, 'Verify ZD obtaining station OS type and hostname via DHCP after moving the wlan from current AP to another.',
        interactive_mode = ts_cfg["interactive_mode"],
        combotest = True,
    )

    check_max_length(test_cfgs)
    check_validation(test_cfgs)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

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

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    