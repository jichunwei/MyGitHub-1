"""
Edit Autonomous WLAN type(usage) to Standard/Guest Access/Hotspot WLAN, and verify station can access the WLAN successfully.

    expect result: All steps should result properly.
    
    How to:
	[Autonomous--->Standard]
        1) Create an Autonomous WLAN, encryption type is selected value(open-none, WPA/WP2 AES/TKIP, WEP, etc.)
        2) Station associate the WLAN
        3) Get station wifi address
        4) Verify client status is 'authorized' and client can ping target station successfully.
        5) Edit WLAN type from 'Autonomous' to 'Standard'
        6) Station associate the WLAN
        7) Get station wifi address
        8) Verify client status is 'authorized' and client can ping target station successfully.
        9) Client disconnects from the WLAN
        10) Delete WLAN

	[Autonomous--->Guest Access]
        1) Create an Autonomous WLAN, encryption type is selected value(open-none, WPA/WP2 AES/TKIP, WEP, etc.)
        2) Station associate the WLAN
        3) Get station wifi address
        4) Verify client status is 'authorized' and client can ping target station successfully.
        5) Select Local Database as authentication server, and create local user.
        6) Edit WLAN type from 'Autonomous' to 'Guest Access'
        7) Station associate the WLAN
        8) Get station wifi address
        9) Verify client status is 'unauthorized' and client can ping target station failed.
        10) Perform Guest authentication by browser with local user.
        11) Verify client status is 'authorized' and client can ping target station successfully.
        12) Client disconnects from the WLAN
        13) Delete WLAN

	[Autonomous--->Hotspot]
        1) Create an Autonomous WLAN, encryption type is selected value(open-none, WPA/WP2 AES/TKIP, WEP, etc.)
        2) Station associate the WLAN
        3) Get station wifi address
        4) Verify client status is 'authorized' and client can ping target station successfully.
        5) Create Hotspot profile selecting Local Database as authentication server, and create local user.
        6) Edit WLAN type from 'Autonomous' to 'Hotspot' with created hotspot profile.
        7) Station associate the WLAN
        8) Get station wifi address
        9) Verify client status is 'unauthorized' and client can ping target station failed.
        10) Perform Hotspot authentication by browser with local user.
        11) Verify client status is 'authorized' and client can ping target station successfully.
        12) Client disconnects from the WLAN
        13) Delete WLAN

Created on 2013-04-17
@author: kevin.tan
"""

import sys
import time
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

check_wlan_timeout = 5

def _define_wlan_cfg(type='standard', auth='open', wpa_ver = '', encryption = 'none', key_index = '1', key_string = '', 
                     sta_auth = '', sta_wpa_ver = '', sta_encryption = '', 
                     vlan_id = ''):
    wlan_cfg = dict(ssid='autonomous-type-change', auth=auth, wpa_ver=wpa_ver, encryption=encryption, key_index=key_index, key_string=key_string,
                    sta_auth=sta_auth, sta_wpa_ver=sta_wpa_ver, sta_encryption=sta_encryption)
    
    wlan_cfg['type'] = type

    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id
    
    return wlan_cfg

def define_test_cfg(cfg, wlan_cfg_param):
    test_cfgs = []
    
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    target_ip_addr = cfg['target_ping_ip_addr']

    radio_mode = cfg['radio_mode']
    vlan_id  = cfg['vlan_id']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'

    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    
    username = 'local.user'
    password = 'local.user'

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))

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

    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create Local User'
    test_params = {'username': username,
                   'password': password}
    test_cfgs.append((test_params, test_name, common_name, 0, False))


    wlan_cfg = _define_wlan_cfg('autonomous', wlan_cfg_param[0], wlan_cfg_param[1], wlan_cfg_param[2], wlan_cfg_param[3], wlan_cfg_param[4],\
                                wlan_cfg_param[5], wlan_cfg_param[6], wlan_cfg_param[7], cfg['vlan_id'])

    ########################################## case 1 ############################################################
    test_case_name = "[WLAN type change to standard]"

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate autonomous WLAN on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to autonomous WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD' % (test_case_name)
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

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    new_wlan_cfg = deepcopy(wlan_cfg)
    new_wlan_cfg['type'] = 'standard'
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sEdit WLAN type to standard on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to standard WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': new_wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station for standard WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD for standard WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP for standard WLAN' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for standard WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    ########################################## case 2 ############################################################
    test_case_name = "[WLAN type change to guest access]"

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate autonomous WLAN on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to autonomous WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD' % (test_case_name)
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

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))


    target_url = cfg['target_url']
    guest_name = 'WLAN_Change_Guest'
    use_guestpass_auth= True
    use_tou = False
    redirect_url = ''

    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = '%sSet the guest access policy' % (test_case_name)
    test_params = {'use_guestpass_auth': use_guestpass_auth,
                   'use_tou': use_tou,
                   'redirect_url': redirect_url}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    new_wlan_cfg = deepcopy(wlan_cfg)
    new_wlan_cfg['type'] = 'guest'

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sEdit WLAN type to guest on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate a guest pass automatically' % (test_case_name)
    test_params = {'username': username, 
                   'password': password,
                   'wlan': new_wlan_cfg['ssid'],
                   'guest_fullname': guest_name}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to guest WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': new_wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station for guest WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information unauthorized status in ZD for guest WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%sPerform guest authentication in station for guest WLAN" % (test_case_name)
    test_params = {'sta_tag': sta_tag, 
                   'browser_tag': browser_tag,
                   'use_tou': use_tou, 
                   'redirect_url': redirect_url,
                   'target_url': target_url,
                   'no_auth': not use_guestpass_auth}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD for guest WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'guest_name': guest_name,
                       'use_guestpass_auth': use_guestpass_auth,},
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for guest WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
    ########################################## case 3 ############################################################
    test_case_name = "[WLAN type change to hotspot]"

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate autonomous WLAN on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to autonomous WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD' % (test_case_name)
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

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    hotspot_cfg = {'login_page': 'http://192.168.0.250/login.html',
                   'name': 'hs_profile',
                   }

    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = '%sCreate a Hotspot profile' % (test_case_name)
    test_cfgs.append(({'hotspot_profiles_list':[hotspot_cfg]}, test_name, common_name, 2, False))

    new_wlan_cfg = deepcopy(wlan_cfg)
    new_wlan_cfg['type'] = 'hotspot'
    new_wlan_cfg['hotspot_profile'] = hotspot_cfg['name']

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sEdit WLAN type to hotspot on ZD' % (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to hotspot WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': new_wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station for hotspot WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD for hotspot WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client cannot ping a target IP for hotspot WLAN' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'disallowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    common_name = '%sPerform Hotspot authentication for client' % (test_case_name)
    test_cfgs.append(({'sta_tag':sta_tag, 
                       'browser_tag': browser_tag,
                       'username': username, 
                       'password': password,},
                       test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD for hotspot WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': username,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP after authorized for hotspot WLAN' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for hotspot WLAN' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    #Recover test environment
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users in ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all hotspot profiles for hotspot WLAN'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

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
    
    expected_sub_mask = '255.255.255.0'
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    server_ip_addr  = testsuite.getTestbedServerIp(tbcfg)
    target_ping_ip_addr = '172.16.10.252'

    expected_subnet = utils.get_network_address(server_ip_addr, expected_sub_mask)

    tcfg = {
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_url': 'http://172.16.10.252/',
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
            'vlan_id': '',
            }
   
    key_string_wpa      = utils.make_random_string(random.randint(8, 63), "hex")
    key_string_wpa2     = utils.make_random_string(random.randint(8, 63), "hex")
    key_string_wpa_mixed= utils.make_random_string(random.randint(8, 63), "hex")
    key_string_wep64_0  = utils.make_random_string(10, "hex"),
    key_string_wep128_0 = utils.make_random_string(26, "hex"),
    
    if type(key_string_wep64_0) == type((1,2)):
        key_string_wep64 = key_string_wep64_0[0]
    else:
        key_string_wep64 = key_string_wep64_0
    
    if type(key_string_wep128_0) == type((1,2)):
        key_string_wep128 = key_string_wep128_0[0]
    else:
        key_string_wep128 = key_string_wep128_0

    #######<auth>  <wpa_ver> <encryption> <key_index> <key_string> <sta_auth> <sta_wpa_ver> <sta_encryption>###### 
    list = [('open', '', 'none', '', '', 'open', '', 'none'),#1
           ('PSK', 'WPA', 'TKIP', '', key_string_wpa,'PSK', 'WPA', 'TKIP'),#2
           ('PSK', 'WPA', 'AES', '', key_string_wpa,'PSK', 'WPA', 'AES'), #3
           ('PSK', 'WPA', 'Auto', '', key_string_wpa,'PSK', 'WPA', 'TKIP'), #4
           ('PSK', 'WPA', 'Auto', '', key_string_wpa,'PSK', 'WPA', 'AES'), #5
           ('PSK', 'WPA2', 'TKIP', '', key_string_wpa2,'PSK', 'WPA2', 'TKIP'),#6
           ('PSK', 'WPA2', 'AES', '', key_string_wpa2,'PSK', 'WPA2', 'AES'),#7
           ('PSK', 'WPA2', 'Auto', '', key_string_wpa2, 'PSK', 'WPA2', 'TKIP'), #8
           ('PSK', 'WPA2', 'Auto', '', key_string_wpa2, 'PSK', 'WPA2', 'AES'), #9
           ('PSK', 'WPA_Mixed', 'TKIP', '', key_string_wpa_mixed, 'PSK', 'WPA', 'TKIP'),  #10
           ('PSK', 'WPA_Mixed', 'TKIP', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'TKIP'),  #11
           ('PSK', 'WPA_Mixed', 'AES', '', key_string_wpa_mixed, 'PSK', 'WPA', 'AES'),  #12
           ('PSK', 'WPA_Mixed', 'AES', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'AES'),  #13
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA', 'TKIP'), #14
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA', 'AES'), #15
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'TKIP'), #16
           ('PSK', 'WPA_Mixed', 'Auto', '', key_string_wpa_mixed, 'PSK', 'WPA2', 'AES'), #17
           ('open', '', 'WEP-64', '1', key_string_wep64, 'open', '', 'WEP-64'),#18
           ('open', '', 'WEP-128', '1', key_string_wep128, 'open', '', 'WEP-128'),#19
            ]

    select_option = raw_input("\n\
    1.  Open None\n\
    2.  WPA+TKIP\n\
    3.  WPA+AES\n\
    4.  WPA+AUTO,       station WPA+TKIP\n\
    5.  WPA+AUTO,       station WPA+AES\n\
    6.  WPA2+TKIP\n\
    7.  WPA2+AES\n\
    8.  WPA2+AUTO,      station WPA2+TKIP\n\
    9.  WPA2+AUTO,      station WPA2+AES\n\
    10. WPA_Mixed+TKIP, station WPA+TKIP\n\
    11. WPA_Mixed+TKIP, station WPA2+TKIP\n\
    12. WPA_Mixed+AES,  station WPA+AES\n\
    13. WPA_Mixed+AES,  station WPA2+AES\n\
    14. WPA_Mixed+AUTO, station WPA+TKIP\n\
    15. WPA_Mixed+AUTO, station WPA+AES\n\
    16. WPA_Mixed+AUTO, station WPA2+TKIP\n\
    17. WPA_Mixed+AUTO, station WPA2+AES\n\
    18. WEP-64\n\
    19. WEP-128\n\n\
    Select encryption type of Autonomous WLAN[1-19, default is 1 <Open None>]: ")
    
    if not select_option or int(select_option) not in range(1,20):
        select_option = 1

    test_cfgs = define_test_cfg(tcfg, list[int(select_option)-1])
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Autonomous WLAN Type Change"

    ts = testsuite.get_testsuite(ts_name, ("Autonomous WLAN Type Change"), combotest=True)

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
