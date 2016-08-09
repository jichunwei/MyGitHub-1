'''
author: serena.tan@ruckuswireless.com

Description: This suite is used to test the WLAN service enable/disable.

'''


import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


MAXIMUM_WLAN = 8
MAXIMUM_WLAN_MESH = 6
RADIO_MAP = {'bg': '2g',
             'ng': '2g',
             'na': '5g'}


def define_wlan_cfgs(enable_mesh):
    config_wlan_list = []
    config_wlan_list.append(dict(ssid = "service-config-%s" % time.strftime("%H%M%S"),
                            auth = 'open', encryption = 'none'))
    #@author: Liang Aihua,@since: 2014-11-17,@change: Remove WPA/TKIP which is not supported any more.
    config_wlan_list.append(dict(ssid = config_wlan_list[0]['ssid'],
                                 auth = 'EAP', wpa_ver = "WPA2", encryption = "AES",
                                 key_index = "" , key_string = ""))
    #config_wlan_list.append(dict(ssid = config_wlan_list[0]['ssid'],
    #                             auth = 'EAP', wpa_ver = "WPA", encryption = "TKIP",
    #                             key_index = "" , key_string = ""))
    
    
    return dict(config_wlan_list = config_wlan_list)

def define_wlan_service_cfgs(radio_mode_list, test_type):
    '''
    wlan_service_cfg = {'ng'/'bg': True/False,
                        'na': True/False,
                        }
    '''
    wlan_service_cfg_list = []
    
    if test_type == "priority":
        if len(radio_mode_list) == 1:
            wlan_service_cfg_list.append({radio_mode_list[0]: False})
    
        elif len(radio_mode_list) == 2:
            wlan_service_cfg_list.append({radio_mode_list[0]: False, radio_mode_list[1]: False})
            wlan_service_cfg_list.append({radio_mode_list[0]: True, radio_mode_list[1]: False})
            wlan_service_cfg_list.append({radio_mode_list[0]: False, radio_mode_list[1]: True})
    
    elif test_type == "basic":
        if len(radio_mode_list) == 1:
            wlan_service_cfg_list.append({radio_mode_list[0]: True})
            wlan_service_cfg_list.append({radio_mode_list[0]: False})
    
        elif len(radio_mode_list) == 2:
            wlan_service_cfg_list.append({radio_mode_list[0]: True, radio_mode_list[1]: True})
            wlan_service_cfg_list.append({radio_mode_list[0]: False, radio_mode_list[1]: False})
        
    return wlan_service_cfg_list


def define_expect_wlan_info_in_ap(tcfg, wlan_service_cfg, test_type):
    expect_wlan_info = dict()
    for radio in tcfg['radio_mode']:
        status = 'up' if wlan_service_cfg[radio] else 'down'
        if radio in ['bg', 'ng']:
            wlan_cfg_list = tcfg['wlan_cfgs']['%s_wlan_list_2g' % test_type]
            for i in range(len(wlan_cfg_list)):
                wlan_name = "wlan%d" % i
                expect_wlan_info[wlan_name] = {}
                expect_wlan_info[wlan_name]['status'] = status
                expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid = wlan_cfg_list[i]['ssid'])
        
        elif radio in ['na']:
            wlan_cfg_list = tcfg['wlan_cfgs']['%s_wlan_list_5g' % test_type]
            for i in range(len(wlan_cfg_list)):
                wlan_name = "wlan%d" % (MAXIMUM_WLAN_MESH + i + 2) if tcfg['enable_mesh'] else "wlan%d" % (MAXIMUM_WLAN + i)
                expect_wlan_info[wlan_name] = {}
                expect_wlan_info[wlan_name]['status'] = status
                expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid = wlan_cfg_list[i]['ssid'])

    return expect_wlan_info

def define_com_name(tcfg, wlan_service_cfg, test_type, ap_type = ""):
    radio_status_list = []
    i = 0
    for radio in tcfg['radio_mode']:
        status = "On" if wlan_service_cfg[radio] else "Off"
        if radio in ['ng', 'bg']:
            radio_status_list.append("2.4G %s" % status)
        
        elif radio in ['na']:
            radio_status_list.append("5G %s" % status)
        
        i += 1
    
    radio_str = "/".join(radio_status_list) if len(radio_status_list) > 1 else radio_status_list[0]
    if test_type == "priority":
        com_name = "[Wlan Service %s While Schedule On]" % radio_str
           
    elif ap_type:
        com_name = "[Wlan Service %s - %s]" % (radio_str, ap_type)
        
    else:
        com_name = "[Wlan Service %s]" % radio_str
    
    return com_name

def define_config_test_cfg(tcfg):
    _test_cfgs = []
    wlan_cfg_list = tcfg['wlan_cfgs']['config_wlan_list']
    
    radio_config = {}
    for radio in tcfg['radio_mode']:
        radio_config[radio] = {'wlan_service': False}
   
    test_name = 'CB_ZD_Config_AP'
    common_name = 'Disable all wlan service in the root AP' if tcfg['enable_mesh'] else \
                  'Disable all wlan service in the active AP'
    _test_cfgs.append(({'ap_tag': tcfg['root_ap'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, False))
    #_test_cfgs.append(({'ap_mac': tcfg['rap_mac_addr'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[Add WLAN While WLAN Service Disabled] Create a wlan'
    _test_cfgs.append(({'wlan_cfg_list': [wlan_cfg_list[0]]}, test_name, common_name, 1, False))
    
    expect_wlan_info = dict()
    for radio in tcfg['radio_mode']:
        status = 'up' if radio_config[radio]['wlan_service'] else 'down'
        if radio in ['bg', 'ng']:
            expect_wlan_info['wlan0'] = {}
            expect_wlan_info['wlan0']['status'] = status
            expect_wlan_info['wlan0']['encryption_cfg'] = wlan_cfg_list[0]
        
        elif radio in ['na']:
            wlan_name = "wlan%d" % (MAXIMUM_WLAN_MESH + 2) if tcfg['enable_mesh'] else "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = wlan_cfg_list[0]
                
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '[Add WLAN While WLAN Service Disabled] Verify wlan info in the AP'
    _test_cfgs.append(({'ap_tag': 'root_ap', 'expect_wlan_info': expect_wlan_info}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[Configure WLAN While WLAN Service Disabled] Configure the existing wlan'
    _test_cfgs.append(({'wlan_cfg_list': [wlan_cfg_list[1]]}, test_name, common_name, 2, False))
    
    new_expect_wlan_info = deepcopy(expect_wlan_info)
    for wlan_name in new_expect_wlan_info:
        new_expect_wlan_info[wlan_name]['encryption_cfg'] = wlan_cfg_list[1]
        
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '[Configure WLAN While WLAN Service Disabled] Verify wlan info in the AP'
    _test_cfgs.append(({'ap_tag': 'root_ap', 'expect_wlan_info': new_expect_wlan_info}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[Delete WLAN While WLAN Service Disabled] Delete the existing wlan from ZD'
    _test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '[Delete WLAN While WLAN Service Disabled] Verify wlan info in the AP'
    _test_cfgs.append(({'ap_tag': 'root_ap', 'expect_wlan_info': None}, test_name, common_name, 2, False))
    
    return _test_cfgs


def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Find the active root AP' if tcfg['enable_mesh'] else 'Find the active AP'
    test_cfgs.append(({'ap_tag': 'root_ap', 'active_ap': tcfg['root_ap']}, test_name, common_name, 0, False))

    if tcfg['enable_mesh']:
        test_name = 'CB_ZD_Create_Active_AP'
        common_name = 'Find the active mesh AP'
        test_cfgs.append(({'ap_tag': 'mesh_ap', 'active_ap': tcfg['mesh_ap']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Find_Station'
    common_name = 'Find target station'
    test_cfgs.append(({'target_station': tcfg['target_sta']}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_cfgs.extend(define_config_test_cfg(tcfg))

    radio_config = {}
    for radio in tcfg['radio_mode']:
        radio_config[radio] = {'wlan_service': True}
   
    test_name = 'CB_ZD_Config_AP'
    common_name = 'Enable all wlan service in the root AP after test' if tcfg['enable_mesh'] else \
                  'Enable all wlan service in the active AP after test'
    #@author: liang aihua,@since: 2015-5-19,@change: remove ap mac from ats file.
    test_cfgs.append(({'ap_tag': tcfg['root_ap'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, True))
    #test_cfgs.append(({'ap_mac': tcfg['rap_mac_addr'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, True))
    
    if tcfg['enable_mesh']:
        test_name = 'CB_ZD_Config_AP'
        common_name = 'Enable all wlan service in the mesh AP after test'
        #@author: liang aihua,@since: 2015-5-19,@change: remove ap mac from ats file.
        test_cfgs.append(({'ap_tag': tcfg['mesh_ap'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, True))
        #test_cfgs.append(({'ap_mac': tcfg['map_mac_addr'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, True))

    return test_cfgs


def _get_atctive_ap(input_msg, ap_sym_dict):   
    while True:
        active_ap = raw_input(input_msg)
        if active_ap not in ap_sym_dict:
            print "AP[%s] doesn't exist." % active_ap
        
        else:
            break
    
    return active_ap
    
    
def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 enable_mesh = False,
                 root_ap = '',
                 mesh_ap = '',
                 target_sta = '',
                 ts_name = '',
                )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta = testsuite.getTargetStation(sta_ip_list)
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs['interactive_mode']:
        mesh = raw_input("Mesh Enabled? (y/n): ")
        enable_mesh = True if mesh.lower() == 'y' else False
        if not ap_sym_dict:
            print "No AP in this testbed!"
            return
        
        testsuite.showApSymList(ap_sym_dict)
        if enable_mesh:
            root_ap = _get_atctive_ap("Choose an active root AP: ", ap_sym_dict)
            mesh_ap = _get_atctive_ap("Choose an active mesh AP: ", ap_sym_dict)
        
        else:
            root_ap = _get_atctive_ap("Choose an active AP: ", ap_sym_dict)
            
    else:
        root_ap = attrs['root_ap']
        enable_mesh = attrs['enable_mesh']
        target_sta = attrs['target_sta']
        mesh_ap = attrs['mesh_ap']
        
    ap_model = ap_sym_dict[root_ap]['model']
    radio_mode = lib_Constant.get_radio_mode_by_ap_model(ap_model)
    
    wlan_cfgs = define_wlan_cfgs(enable_mesh)
    tcfg = dict(enable_mesh = enable_mesh,
                root_ap = root_ap,
                rap_mac_addr = ap_sym_dict[root_ap]['mac'],
                radio_mode = radio_mode,
                target_sta = target_sta,
                wlan_cfgs = wlan_cfgs,
                )
    
    if enable_mesh:
        tcfg['mesh_ap'] = mesh_ap
        tcfg['map_mac_addr'] = ap_sym_dict[mesh_ap]['mac']
        
    test_cfgs = define_test_cfg(tcfg)

    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    elif enable_mesh:
        #@author: Liang Aihua,@since: 2014-12-17,@change: remove ap model from ts.
        if len(radio_mode)== 1:
            ts_name = "Mesh - Wlan Service Configuration Test - Single Band"
        else:
            ts_name = "Mesh - Wlan Service Configuration Test - Dual Band"
        #ts_name = "Mesh - Wlan Service Enable and Disable - %s" % ap_model

    else:
        if len(radio_mode)== 1:
            ts_name = "Wlan Service Configuration Test - Single Band"
        else:
            ts_name = "Wlan Service Configuration Test - Dual Band"
        #ts_name = "Wlan Service Enable and Disable - %s" % ap_model

    ts = testsuite.get_testsuite(ts_name,
                                 "Verify WLAN service enable and disable",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
    
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
    
    '''
Created on 2014-12-18

@author: lab
'''
