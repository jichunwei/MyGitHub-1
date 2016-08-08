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
    basic_wlan_list_2g = []
    basic_wlan_list_5g = []
    num = MAXIMUM_WLAN_MESH if enable_mesh else MAXIMUM_WLAN
    for i in range(num):
        basic_wlan_list_2g.append(dict(ssid = "service-basic-2g-%s-%d" % (time.strftime("%H%M%S"), i),
                                       auth = 'open', encryption = 'none'))
        basic_wlan_list_5g.append(dict(ssid = "service-basic-5g-%s-%d" % (time.strftime("%H%M%S"), i),
                                       auth = 'open', encryption = 'none'))
    
    config_wlan_list = []
    config_wlan_list.append(dict(ssid = "service-config-%s" % time.strftime("%H%M%S"),
                            auth = 'open', encryption = 'none'))
    config_wlan_list.append(dict(ssid = config_wlan_list[0]['ssid'],
                                 auth = 'EAP', wpa_ver = "WPA", encryption = "TKIP",
                                 key_index = "" , key_string = ""))
    
    priority_wlan_list_2g = []
    priority_wlan_list_5g = []
    priority_wlan_list_2g.append(dict(ssid = "service-priority-2g-%s" % time.strftime("%H%M%S"),
                                      auth = 'open', encryption = 'none'))
    priority_wlan_list_5g.append(dict(ssid = "service-priority-5g-%s" % time.strftime("%H%M%S"),
                                      auth = 'open', encryption = 'none'))
    
    return dict(basic_wlan_list_2g = basic_wlan_list_2g,
                basic_wlan_list_5g = basic_wlan_list_5g,
                config_wlan_list = config_wlan_list,
                priority_wlan_list_2g = priority_wlan_list_2g,
                priority_wlan_list_5g = priority_wlan_list_5g
                )


def wlan_group_cfgs(wlan_cfgs):
    basic_wlan_members_2g = {}
    basic_wlan_members_5g = {}
    for wlan in wlan_cfgs['basic_wlan_list_2g']:
        basic_wlan_members_2g[wlan['ssid']] = {}
        
    for wlan in wlan_cfgs['basic_wlan_list_5g']:
        basic_wlan_members_5g[wlan['ssid']] = {}
        
    priority_wlan_members_2g = {wlan_cfgs['priority_wlan_list_2g'][0]['ssid']: {}}
    priority_wlan_members_5g = {wlan_cfgs['priority_wlan_list_5g'][0]['ssid']: {}}
    
    basic_group_cfg_2g = dict(name = 'service-basic-group-2g', description = '', 
                              vlan_override = False, wlan_member = basic_wlan_members_2g)
    
    basic_group_cfg_5g = dict(name = 'service-basic-group-5g', description = '', 
                              vlan_override = False, wlan_member = basic_wlan_members_5g)
    
    priority_group_cfg_2g = dict(name = 'service-priority-group-2g', description = '', 
                                 vlan_override = False, wlan_member = priority_wlan_members_2g)
    
    priority_group_cfg_5g = dict(name = 'service-priority-group-5g', description = '', 
                                 vlan_override = False, wlan_member = priority_wlan_members_5g)
    
    return dict(basic_group_cfg_2g = basic_group_cfg_2g,
                basic_group_cfg_5g = basic_group_cfg_5g,
                priority_group_cfg_2g = priority_group_cfg_2g,
                priority_group_cfg_5g = priority_group_cfg_5g
                )


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


def define_prim_test_cfg(tcfg, wlan_service_cfg, com_name, test_type, ap_type = ""):
    _test_cfgs = []
    radio_config = {}
    for radio in wlan_service_cfg:
        radio_config[radio] = {'wlan_service': wlan_service_cfg[radio]}
    
    if ap_type == "MAP":
        ap_mac_addr = tcfg['map_mac_addr']
        ap_tag = 'mesh_ap'
        push_cfg_time = 120
    
    else:
        ap_mac_addr = tcfg['rap_mac_addr']
        ap_tag = 'root_ap'
        push_cfg_time = 60
        
    test_name = 'CB_ZD_Config_AP'
    common_name = '%s Configure AP' % com_name
    _test_cfgs.append(({'ap_mac': ap_mac_addr, 'ap_cfg': {'radio_config': radio_config}, 'push_cfg_time': push_cfg_time}, 
                       test_name, common_name, 2, False))
    
    expect_wlan_info = define_expect_wlan_info_in_ap(tcfg, wlan_service_cfg, test_type)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%s Verify wlan info in AP' % com_name
    _test_cfgs.append(({'ap_tag': ap_tag, 'expect_wlan_info': expect_wlan_info}, test_name, common_name, 2, False))
    
    allow_wlan_cfg_list = []
    deny_wlan_cfg_list = []
    for radio in tcfg['radio_mode']:
        if wlan_service_cfg[radio]:
            allow_wlan_cfg_list.extend(tcfg['wlan_cfgs']['%s_wlan_list_%s' % (test_type, RADIO_MAP[radio])])
        
        else:
            deny_wlan_cfg_list.extend(tcfg['wlan_cfgs']['%s_wlan_list_%s' % (test_type, RADIO_MAP[radio])])
                       
    if allow_wlan_cfg_list:
        test_name = 'CB_ZD_Associate_Test'
        common_name = '%s Associate station with wlans which service enabled' % com_name
        _test_cfgs.append(({'wlan_cfg_list': allow_wlan_cfg_list}, test_name, common_name, 2, False))
    
    if deny_wlan_cfg_list:
        deny_ssid_list = [wlan['ssid'] for wlan in deny_wlan_cfg_list]
        test_name = 'CB_ZD_Verify_Wlans_Not_In_The_Air'
        common_name = '%s verify wlans which service disabled not in the air' % com_name
        _test_cfgs.append(({'ssid_list': deny_ssid_list}, test_name, common_name, 2, False))
    
    return _test_cfgs


def define_sub_test_cfg(tcfg, test_type, wgs_cfg, ap_type = ""):
    _test_cfgs = []
    
    if ap_type == 'MAP':
        test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
        common_name = "Assign created wlan groups to the mesh AP for %s test" % test_type
        _test_cfgs.append(({"wgs_cfg": wgs_cfg, "ap_tag": 'mesh_ap'},
                           test_name, common_name, 0, False))
    
    else:
        test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
        common_name = "Assign created wlan groups to the root AP for %s test" % test_type if tcfg['enable_mesh'] else \
                      "Assign created wlan groups to the active AP for %s test" % test_type
        _test_cfgs.append(({"wgs_cfg": wgs_cfg, "ap_tag": 'root_ap'},
                           test_name, common_name, 0, False))
    
    wlan_service_cfg_list = define_wlan_service_cfgs(tcfg['radio_mode'], test_type)
    for wlan_service_cfg in wlan_service_cfg_list:
        com_name = define_com_name(tcfg, wlan_service_cfg, test_type, ap_type)
        _test_cfgs.extend(define_prim_test_cfg(tcfg, wlan_service_cfg, com_name, test_type, ap_type))
    
    ap_rp = dict()
    for radio in tcfg['radio_mode']:
        ap_rp[radio] = {'wlangroups': 'Default'}
        
    if ap_type == 'MAP':
        test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
        common_name = "Assign the mesh AP to Default wlan group after %s test" % test_type
        _test_cfgs.append(({"wgs_cfg": {'name': 'Default', 'ap_rp': ap_rp, 'description': ''}, "ap_tag": 'mesh_ap'},
                            test_name, common_name, 0, False))
    
    else:
        test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
        common_name = "Assign the root AP to Default wlan group after %s test" % test_type if tcfg['enable_mesh'] else \
                      "Assign the active AP to Default wlan group after %s test" % test_type
        _test_cfgs.append(({"wgs_cfg": {'name': 'Default', 'ap_rp': ap_rp, 'description': ''}, "ap_tag": 'root_ap'},
                            test_name, common_name, 0, False))
    
    return _test_cfgs


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
        
        
def define_other_test_cfg(tcfg, test_type):
    _test_cfgs = []
    
    wlan_cfg_list = []
    for radio in tcfg['radio_mode']:
        wlan_cfg_list_name = '%s_wlan_list_%s' % (test_type, RADIO_MAP[radio])
        wlan_cfg_list.extend(tcfg['wlan_cfgs'][wlan_cfg_list_name])
    
    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create %d wlans for %s test' % (len(wlan_cfg_list), test_type)
    _test_cfgs.append(({'wlan_cfg_list': wlan_cfg_list, 'pause': 5}, test_name, common_name, 0, False))
    
    if test_type == "priority":
        for radio in tcfg['radio_mode']:
            wlan_cfg = tcfg['wlan_cfgs']['priority_wlan_list_%s' % RADIO_MAP[radio]][0]
            test_name = 'CB_ZD_Schedule_WLAN_Service'
            common_name = "Set radio '%s' wlan schedule to always on for %s test" % (radio, test_type)
            _test_cfgs.append(({'on': True, 'wlan_cfg': wlan_cfg}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group'
    common_name = 'Remove all wlans from default wlan group for %s test'  % test_type
    _test_cfgs.append(({}, test_name, common_name, 0, False))
    
    wgs_cfg = {"name": [], "ap_rp": {}, 'description': ''}
    for radio in tcfg['radio_mode']:
        group_key = "%s_group_cfg_%s" % (test_type, RADIO_MAP[radio])
        test_name = 'CB_ZD_Create_New_WlanGroup'
        common_name = "Create a wlan group for radio '%s' for %s test" % (radio, test_type)
        _test_cfgs.append(({'wgs_cfg': tcfg['wlan_groups'][group_key]}, test_name, common_name, 0, False))
        
        name = tcfg['wlan_groups'][group_key]['name']
        wgs_cfg["ap_rp"][radio] = {'wlangroups': name}
        if name not in wgs_cfg["name"]:
            wgs_cfg["name"].append(name)
    
    if test_type == "basic" and tcfg['enable_mesh']:
        _test_cfgs.extend(define_sub_test_cfg(tcfg, test_type, wgs_cfg, "RAP"))
        _test_cfgs.extend(define_sub_test_cfg(tcfg, test_type, wgs_cfg, "MAP"))
        
    else:
        _test_cfgs.extend(define_sub_test_cfg(tcfg, test_type, wgs_cfg))
        
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all wlan group from ZD after %s test' % test_type
    _test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlan from ZD after %s test' % test_type
    _test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return _test_cfgs


def define_config_test_cfg(tcfg):
    _test_cfgs = []
    wlan_cfg_list = tcfg['wlan_cfgs']['config_wlan_list']
    
    radio_config = {}
    for radio in tcfg['radio_mode']:
        radio_config[radio] = {'wlan_service': False}
   
    test_name = 'CB_ZD_Config_AP'
    common_name = 'Disable all wlan service in the root AP for configure test' if tcfg['enable_mesh'] else \
                  'Disable all wlan service in the active AP for configure test'
    _test_cfgs.append(({'ap_mac': tcfg['rap_mac_addr'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, False))
    
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
    _test_cfgs.append(({'wlan_cfg_list': [wlan_cfg_list[1]]}, test_name, common_name, 1, False))
    
    new_expect_wlan_info = deepcopy(expect_wlan_info)
    for wlan_name in new_expect_wlan_info:
        new_expect_wlan_info[wlan_name]['encryption_cfg'] = wlan_cfg_list[1]
        
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '[Configure WLAN While WLAN Service Disabled] Verify wlan info in the AP'
    _test_cfgs.append(({'ap_tag': 'root_ap', 'expect_wlan_info': new_expect_wlan_info}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[Delete WLAN While WLAN Service Disabled] Delete the existing wlan from ZD'
    _test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '[Delete WLAN While WLAN Service Disabled] Verify wlan info in the AP'
    _test_cfgs.append(({'ap_tag': 'root_ap', 'expect_wlan_info': None}, test_name, common_name, 1, False))
    
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

    test_cfgs.extend(define_other_test_cfg(tcfg, "basic"))
    test_cfgs.extend(define_other_test_cfg(tcfg, "priority"))
    test_cfgs.extend(define_config_test_cfg(tcfg))

    radio_config = {}
    for radio in tcfg['radio_mode']:
        radio_config[radio] = {'wlan_service': True}
   
    test_name = 'CB_ZD_Config_AP'
    common_name = 'Enable all wlan service in the root AP after test' if tcfg['enable_mesh'] else \
                  'Enable all wlan service in the active AP after test'
    test_cfgs.append(({'ap_mac': tcfg['rap_mac_addr'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, False))
    
    if tcfg['enable_mesh']:
        test_name = 'CB_ZD_Config_AP'
        common_name = 'Enable all wlan service in the mesh AP after test'
        test_cfgs.append(({'ap_mac': tcfg['map_mac_addr'], 'ap_cfg': {'radio_config': radio_config}}, test_name, common_name, 0, False))

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
    wlan_groups = wlan_group_cfgs(wlan_cfgs)
    tcfg = dict(enable_mesh = enable_mesh,
                root_ap = root_ap,
                rap_mac_addr = ap_sym_dict[root_ap]['mac'],
                radio_mode = radio_mode,
                target_sta = target_sta,
                wlan_cfgs = wlan_cfgs,
                wlan_groups = wlan_groups
                )
    
    if enable_mesh:
        tcfg['mesh_ap'] = mesh_ap
        tcfg['map_mac_addr'] = ap_sym_dict[mesh_ap]['mac']
        
    test_cfgs = define_test_cfg(tcfg)

    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    elif enable_mesh:
        ts_name = "Mesh - Wlan Service Enable and Disable - %s" % ap_model

    else:
        ts_name = "Wlan Service Enable and Disable - %s" % ap_model

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
    
    