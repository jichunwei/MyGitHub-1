'''
Title: Get_Sta_OS_and_Hostname_via_DHCP_Web_Auth

Test purpose: Verify if ZD can get station OS type and hostname information correctly with web-auth wlan.
    
Expect result: Station OS type and hostname obtained by ZD should be matched with the actual information on station.
    
Steps:
1) Remove configuration on ZD
2) Create local user for authentication
3) Config all APs radio - Disable WLAN service
4) Remove all WLANs on wireless station
5) Config active AP radio - Enable WLAN service
6) Assign active AP to default wlan group
7) Create a wlan with web auth on ZD
8) Associate the station to the wlan
9) Get wifi address of the station
10) Verify station wifi ip address in expected subnet
11) Verify the station information on ZD (Unauthenticated)
12) Verify the station OS type information on ZD
13) Verify the station host name information on ZD
14) Station perform web auth
15) Verify the station information on ZD again (Authenticated)
16) Verify the station OS type information on ZD
17) Verify the station host name information on ZD
18) Clean configuration on station
19) Clean configuration on ZD
    
Created on 2012-8-22
@author: sean.chen@ruckuswireless.com
'''

import sys
import time
#import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []

    username = cfg['username']
    password = cfg['password']
    radio_mode = cfg['radio_mode']

    sta_tag = 'sta-%s' % radio_mode
    target_sta_ip = cfg['target_station']
    ap_tag = 'ap'
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create local user for authentication'
    test_cfgs.append(({'username': username, 'password': password},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Disable WLAN service'
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wireless station'
    test_cfgs.append(({'sta_ip_addr': target_sta_ip,
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WLANs on wireless station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP radio %s - Enable WLAN service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    wg_name = 'Default'
    wg_cfg = dict(name = wg_name, description = None, ap_rp = {radio_mode: {'wlangroups': wg_name}})
    test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    test_cfgs.append(({'wgs_cfg': wg_cfg,
                       'ap_tag': ap_tag, },
                  test_name, common_name, 0, False))
    
#---TestCase---------------------------------------------------------------------------------------
    test_case_name_list = ['Client Fingerprinting on, option82 off', 
                           'Client Fingerprinting on, option82 on', 
                           'Client Fingerprinting off, option82 off', 
                           'Client Fingerprinting off, option82 on',
                           'VLAN on, Client Fingerprinting on, option82 off', 
                           'VLAN on, Client Fingerprinting on, option82 on',
                           'Tunnel on, Client Fingerprinting on, option82 off', 
                           'Tunnel on, Client Fingerprinting on, option82 on', 
                           'Tunnel on, Client Fingerprinting off, option82 off', 
                           'Tunnel on, Client Fingerprinting off, option82 on',
                           'Tunnel on, VLAN on, Client Fingerprinting on, option82 off', 
                           'Tunnel on, VLAN on, Client Fingerprinting on, option82 on',]
    for test_case_name in test_case_name_list:
        
        test_combo_case_name = "[%s]" % test_case_name
        
        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sCreate a wlan on ZD' % test_combo_case_name
        
        wlan_cfg = {}
        wlan_cfg.update(cfg['wlan_cfg'])
        
        if test_combo_case_name == '[Client Fingerprinting on, option82 off]':
            wlan_cfg.update({'fingerprinting': True, 'option82': False})
            
        elif test_combo_case_name == '[Client Fingerprinting on, option82 on]':
            wlan_cfg.update({'fingerprinting': True, 'option82': True})
            
        elif test_combo_case_name == '[Client Fingerprinting off, option82 off]':
            wlan_cfg.update({'fingerprinting': False, 'option82': False})
            
        elif test_combo_case_name == '[Client Fingerprinting off, option82 on]':
            wlan_cfg.update({'fingerprinting': False, 'option82': True})
            
        elif test_combo_case_name == '[VLAN on, Client Fingerprinting on, option82 off]':
            wlan_cfg.update({'vlan_id': '2', 'fingerprinting': True, 'option82': False})
            
        elif test_combo_case_name == '[VLAN on, Client Fingerprinting on, option82 on]':
            wlan_cfg.update({'vlan_id': '2', 'fingerprinting': True, 'option82': True})
            
        ### Tunnel on------------------------------------------------------------------------------        
        elif test_combo_case_name == '[Tunnel on, Client Fingerprinting on, option82 off]':
            wlan_cfg.update({'do_tunnel': True, 'fingerprinting': True, 'option82': False})
            
        elif test_combo_case_name == '[Tunnel on, Client Fingerprinting on, option82 on]':
            wlan_cfg.update({'do_tunnel': True, 'fingerprinting': True, 'option82': True})
            
        elif test_combo_case_name == '[Tunnel on, Client Fingerprinting off, option82 off]':
            wlan_cfg.update({'do_tunnel': True, 'fingerprinting': False, 'option82': False})
            
        elif test_combo_case_name == '[Tunnel on, Client Fingerprinting off, option82 on]':
            wlan_cfg.update({'do_tunnel': True, 'fingerprinting': False, 'option82': True})
            
        elif test_combo_case_name == '[Tunnel on, VLAN on, Client Fingerprinting on, option82 off]':
            wlan_cfg.update({'do_tunnel': True, 'vlan_id': '2', 'fingerprinting': True, 'option82': False})
            
        elif test_combo_case_name == '[Tunnel on, VLAN on, Client Fingerprinting on, option82 on]':
            wlan_cfg.update({'do_tunnel': True, 'vlan_id': '2', 'fingerprinting': True, 'option82': True})
        
        test_params = {'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True}
        test_cfgs.append((test_params, test_name, common_name, 1, False))
    
        expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP' % (test_combo_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
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
        if test_combo_case_name in ['[VLAN on, Client Fingerprinting on, option82 off]', 
                              '[VLAN on, Client Fingerprinting on, option82 on]',
                              '[Tunnel on, VLAN on, Client Fingerprinting on, option82 off]',
                              '[Tunnel on, VLAN on, Client Fingerprinting on, option82 on]']:
            expected_subnet = '20.0.2.0'
        test_cfgs.append(({'sta_tag': sta_tag,
                           'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                          test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify the station information on ZD' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Unauthorized',
                           'wlan_cfg': wlan_cfg,
                           'radio_mode': radio_mode,
                           'username': username},
                           test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
        common_name = '%sVerify the station information on AP' % (test_combo_case_name,)
        test_cfgs.append(({'ssid': wlan_cfg['ssid'],
                           'ap_tag': ap_tag,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify if client can ping a target IP' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'disallowed',
                           'target': '172.16.10.252'}, test_name, common_name, 2, False))
    
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_OS_Type_Info'
        common_name = '%sVerify the station OS type information on ZD' % (test_combo_case_name,)
        if test_combo_case_name in ['[Client Fingerprinting off, option82 off]', 
                           '[Client Fingerprinting off, option82 on]',
                           '[Tunnel on, Client Fingerprinting off, option82 off]', 
                           '[Tunnel on, Client Fingerprinting off, option82 on]',]:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_os': False, 
                           }
        else:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_os': True, 
                           }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_Host_Name_Info'
        common_name = '%sVerify the station host name information on ZD' % (test_combo_case_name,)
        if test_combo_case_name in ['[Client Fingerprinting off, option82 off]', 
                           '[Client Fingerprinting off, option82 on]',
                           '[Tunnel on, Client Fingerprinting off, option82 off]', 
                           '[Tunnel on, Client Fingerprinting off, option82 on]',]:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_hn': False, 
                           }
        else:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_hn': True, 
                           }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
        test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
        common_name = '%sStation perform web auth' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'username': username,
                           'password': password,
                           'start_browser_before_auth': True,
                           'close_browser_after_auth': True,
                           }, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify the station information on ZD again' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg,
                           'radio_mode': radio_mode,
                           'username': username},
                           test_name, common_name, 2, False))

        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify if client can ping a target IP again' % (test_combo_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': '172.16.10.252'}, test_name, common_name, 2, False))

    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_OS_Type_Info'
        common_name = '%sVerify the station OS type information on ZD again' % (test_combo_case_name,)
        if test_combo_case_name in ['[Client Fingerprinting off, option82 off]', 
                           '[Client Fingerprinting off, option82 on]',
                           '[Tunnel on, Client Fingerprinting off, option82 off]', 
                           '[Tunnel on, Client Fingerprinting off, option82 on]',]:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_os': False, 
                           }
        else:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_os': True, 
                           }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    ### new added tests script.
        test_name = 'CB_ZD_Verify_Station_Host_Name_Info'
        common_name = '%sVerify the station host name information on ZD again' % (test_combo_case_name,)
        if test_combo_case_name in ['[Client Fingerprinting off, option82 off]', 
                           '[Client Fingerprinting off, option82 on]',
                           '[Tunnel on, Client Fingerprinting off, option82 off]', 
                           '[Tunnel on, Client Fingerprinting off, option82 on]',]:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_hn': False, 
                           }
        else:
            test_params = {'sta_tag': sta_tag,
                           'sta_ip_addr': target_sta_ip,
                           'expect_get_sta_hn': True, 
                           }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan on station after case' % (test_combo_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
        
        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, True))

#---TestCase End-----------------------------------------------------------------------------------

    test_name = 'CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group'
    common_name = 'Remove the wlan from default wlan group'
    test_cfgs.append(({'wlan_name_list': [wlan_cfg['ssid']]}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Enable WLAN service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users on ZD'
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

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)
     
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()

    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            desired_ap = raw_input("Is %s under test (y/n)?: " % (active_ap)).lower() == "y"
            if desired_ap:
                break
    
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg = {'ssid': ssid, 
                'type': 'standard',
                'auth': 'open', 
                'encryption': 'none', 
                'sta_auth': 'open', 
                'sta_encryption': 'none',
                'do_webauth': True, 
                'auth_svr': 'Local Database',
                'vlan_id':None,
                'do_tunnel': None,
                'option82':None,
                'fingerprinting':None,
                  }

    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':'%s' % active_ap,
            'wlan_cfg': wlan_cfg,
            'expected_sub_mask': '255.255.255.0',
            'expected_subnet': utils.get_network_address(ras_ip_addr, '255.255.255.0'),
            'username': 'local.user',
            'password': 'local.user',
           }

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'Web Auth - Get Sta OS and Hostname via DHCP - Basic'

    ts = testsuite.get_testsuite(
        ts_name, 'Verify ZD obtaining station OS type and hostname via DHCP with Web Auth WLAN.',
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
    