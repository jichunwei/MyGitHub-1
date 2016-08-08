"""
Verify WISPr MAC authentication bypass procedure (O2 required feature)
    
    expect result: All steps should result properly.
    
    How to:
        1) Disable all AP's wlan service
        2) Enable active AP's wlan service based on radio
        3) Create Radius authentication server
        4) Create Hospot profile, enable MAC authentication, ZD sends username and password to radius server in default format of 0010a42319c0(for example)
        5) Create a WISPr wlan with created Hotspot profile
        6) Station associate the wlan
        7) Get station wifi address
        8) Verify station information in ZD, status is unauthorized
        9) Verify radius access request message parameters(User-Name is MAC address: 00-10-A4-23-19-C0, response message is failure result
        10) Perform Hotspot authentication, and verify station information in ZD, status is authorized, Auth-Method shown on ZD active clients page is 'WEB'
        11) Verify radius access request message parameters(User-Name is radius user name 'ras.local.user'), response message is successful result
        12) Edit radius users file in Linux '/etc/raddb/' directory, add username/password 00-10-A4-23-19-C0
        13) Client disconnects from the WLAN
        14) Station associate the wlan again
        15) Perform Hotspot authentication, and verify station information in ZD, status is authorized, Auth-Method shown on ZD active clients page is 'MAC'
        16) Verify radius access request message parameters(User-Name is MAC address: 00-10-A4-23-19-C0, response message is successful result
        17) Remove the wlan
        18) Edit Hospot profile, ZD sends username and password to radius server in 802.1X format of 00-10-A4-23-19-C0
        19) Repeat step 5)-17)
        18) Edit Hospot profile, user user-defined string '12-34-56-78-90-11' as authentication password.
        19) Repeat step 5)-17)

Created on 2012-11-28
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
rad_user = 'ras.local.user'
auth_method = 'pap'

wispr_list = [{'wlan_ssid': 'mac-bypass-wispr-1', 'format': None,     'password': None,             'hs_cfg_linux': {}, 'hs_cfg_win': {}}, 
              {'wlan_ssid': 'mac-bypass-wispr-2', 'format': None,     'password': 'ras.mac.bypass', 'hs_cfg_linux': {}, 'hs_cfg_win': {}},
              {'wlan_ssid': 'mac-bypass-wispr-3', 'format': '802.1X', 'password': None,             'hs_cfg_linux': {}, 'hs_cfg_win': {}},
              {'wlan_ssid': 'mac-bypass-wispr-4', 'format': '802.1X', 'password': 'ras.mac.bypass', 'hs_cfg_linux': {}, 'hs_cfg_win': {}}]
#@author: TSX #@since: zf-12923
#add parameter "mac_addr_format"
def _define_wlan_cfg_hotspot(hs_name='', auth='open', wpa_ver = '', encryption='none', key_index='1', key_string='', 
                             sta_auth = '', sta_wpa_ver = '', sta_encryption = '', 
                             rad_user='', do_tunnel=False, vlan_id='',mac_addr_format = '',):
    wlan_cfg = dict(ssid='ras-mac-bypass-wispr', auth=auth, wpa_ver=wpa_ver, encryption=encryption, key_index=key_index, key_string=key_string,
                    sta_auth=sta_auth, sta_wpa_ver=sta_wpa_ver, sta_encryption=sta_encryption, mac_addr_format = mac_addr_format)
    
    wlan_cfg['type'] = 'hotspot'
    wlan_cfg['hotspot_profile'] = hs_name

    wlan_cfg['username']        = rad_user
    wlan_cfg['password']        = rad_user

    if do_tunnel:
        wlan_cfg['do_tunnel'] = do_tunnel
    
    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id #In 9.4 LCS version, default vlan_id is 1, but other versions have null default vlan_id
    
    return wlan_cfg

def define_test_cfg(cfg, wlan_cfg):
    test_cfgs = []
    
    ras_cfg = cfg['ras_cfg']
    ras_cfg_win = cfg['ras_cfg_win']
    hs_cfg = cfg['hotspot_cfg']
    
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    target_ip_addr = cfg['target_ping_ip_addr']

    radio_mode = cfg['radio_mode']
    do_tunnel = cfg['do_tunnel']
    vlan_id  = cfg['vlan_id']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'

    do_grace_period = cfg['do_grace_period']
    grace_period = cfg['grace_period']
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius PAP authentication server of Linux'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius PAP authentication server of Win2003'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg_win]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = 'Create a Hotspot profile'
    test_cfgs.append(({'hotspot_profiles_list':[hs_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
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

    wlan_cfg1 = deepcopy(wlan_cfg)
    wlan_cfg2 = deepcopy(wlan_cfg)
    wlan_cfg3 = deepcopy(wlan_cfg)
    wlan_cfg4 = deepcopy(wlan_cfg)

    wlan_cfg_list = [wlan_cfg1, wlan_cfg2, wlan_cfg3, wlan_cfg4]
    for j in range(0,4):
        wlan_cfg_list[j]['ssid'] = wispr_list[j]['wlan_ssid'] 

    idx=-1
    for wispr in wispr_list:
        idx=idx+1
        test_case_name = '[mac-auth bypass, format %s, password %s]' % (wispr['format'], wispr['password'])

        if wispr['format'] is None:
            access_user_type = 'mac-lower'
        else:
            access_user_type = 'mac-upper-connecter'
            #@author: TSX,#@since: zf-12923; add parameter "mac_addr_format"
            wlan_cfg_list[idx]['mac_addr_format'] = 'AA-BB-CC-DD-EE-FF'

        if wispr['password'] is not None:
            mac_password = wispr['password']
        else:
            mac_password = ''
    
        wispr['hs_cfg_win'] = deepcopy(hs_cfg)
        wispr['hs_cfg_win']['auth_svr'] = ras_cfg_win['server_name']
        wispr['hs_cfg_win']['mac_bypass_format']   = wispr['format']
        wispr['hs_cfg_win']['mac_bypass_password'] = wispr['password']

        wispr['hs_cfg_linux'] = deepcopy(wispr['hs_cfg_win'])
        
        test_name = 'CB_ZD_Edit_Hotspot_Profiles'
        common_name = '%sEdit Hotspot profile for new mac format and server' % (test_case_name)
        test_cfgs.append(({'hotspot_profiles_list':[wispr['hs_cfg_win']]}, test_name, common_name, 1, False))
            
        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sCreate WLAN on ZD' % (test_case_name)
        test_cfgs.append(({'wlan_cfg_list':[wlan_cfg_list[idx]],
                           'enable_wlan_on_default_wlan_group': True,
                           'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station to the WLAN' % (test_case_name)
        test_cfgs.append(({'wlan_cfg': wlan_cfg_list[idx],
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet WiFi address of the station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Verify_Expected_Subnet'
        common_name = '%sVerify station wifi ipaddr in expected subnet' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                          test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Unauthorized',
                           'wlan_cfg': wlan_cfg_list[idx],
                           'radio_mode':sta_radio_mode,},
                           test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client should not ping a target IP' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'disallowed',
                           'target': target_ip_addr},
                          test_name, common_name, 2, False))
    
        test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
        common_name = '%sPerform Hotspot authentication for client' % (test_case_name)
        test_cfgs.append(({'sta_tag':sta_tag, 
                           'browser_tag': browser_tag,
                           'username': rad_user, 
                           'password': rad_user,},
                           test_name, common_name, 2, False)) 
    
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify client information Authorized status in ZD' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg_list[idx],
                           'radio_mode':sta_radio_mode,
                           'username': rad_user,},
                           test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

        wispr['hs_cfg_linux']['auth_svr'] = ras_cfg['server_name']
        
        test_name = 'CB_ZD_Edit_Hotspot_Profiles'
        common_name = '%sEdit Hotspot profile for new linux radius server' % (test_case_name)
        test_cfgs.append(({'hotspot_profiles_list':[wispr['hs_cfg_linux']]}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Start_Radius_Server_Nohup'
        common_name = '%sStart radius server in the background by nohup option' % (test_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Associate_Station_1'
        common_name = '%sAssociate the station to the WLAN again' % (test_case_name)
        test_cfgs.append(({'wlan_cfg': wlan_cfg_list[idx],
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        common_name = '%sGet WiFi address of the station again' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Verify_Expected_Subnet'
        common_name = '%sVerify station wifi ipaddr in expected subnet again' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                          test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        common_name = '%sVerify client information Authorized status in ZD again' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'status': 'Authorized',
                           'wlan_cfg': wlan_cfg_list[idx],
                           'radio_mode':sta_radio_mode,
                           'username': 'mac.bypass',}, 
                           test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        common_name = '%sVerify client can ping a target IP again' % (test_case_name,)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'condition': 'allowed',
                           'target': target_ip_addr}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Radius_Access_Request'
        common_name = '%sVerify Radius Access Request Accept Message again' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'wlan_cfg': wlan_cfg_list[idx],
                           'radio_mode':radio_mode,
                           'auth_method': auth_method,
                           'user_type': access_user_type,
                           'user_name': '',
                           'password': mac_password,
                           'auth_result': 'Access-Accept'
                           },
                           test_name, common_name, 2, False))
    
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station again' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = '%sRemove the wlan from ZD' % (test_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Restart_Service'
    common_name = 'Restart radius server'
    test_cfgs.append(({'service':'radiusd'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))

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

    target_ping_ip_addr = server_ip_addr
    expected_subnet = utils.get_network_address(server_ip_addr, expected_sub_mask)

    ras_name = 'radius-linux-%s' % (time.strftime("%H%M%S"),)
    ras_win_name = 'radius-win-%s' % (time.strftime("%H%M%S"),)

    tcfg = {'ras_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1812',
                    'server_name' : ras_name,
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': auth_method,
                    },
            'ras_cfg_win': {'server_addr': '192.168.0.250',
                    'server_port' : '18120',
                    'server_name' : ras_win_name,
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': auth_method,
                    },                    
            'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                            'name': 'hs_radius_mac_bypass',
                            'auth_svr': ras_win_name,
                            'idle_timeout': None,
                            'enable_mac_auth': True,
                            'mac_bypass_format': None,
                            'mac_bypass_password': None,
                            },
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
            'do_tunnel': False,
            'do_grace_period': False,
            'grace_period': '',
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
    Select encryption type of Autonomous WLAN[1-19]: ")
    
    if not select_option or int(select_option) not in range(1,20):
        print "Failed: Selected value should be integer between 1 and %s!" % len(list)
        return

    member = int(select_option)-1
    wlan_cfg = _define_wlan_cfg_hotspot(tcfg['hotspot_cfg']['name'], list[member][0], list[member][1], list[member][2], list[member][3], list[member][4],
                                        list[member][5], list[member][6],list[member][7],
                                        rad_user, False, tcfg['vlan_id'])

    test_cfgs = define_test_cfg(tcfg, wlan_cfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        index = int(select_option)
        if index == 1:
            ts_name = "WISPr MAC auth bypass %s %s" % (wlan_cfg['auth'], wlan_cfg['encryption'])
        elif index in [2,3,6,7]:
            ts_name = "WISPr MAC auth bypass %s %s %s" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'], wlan_cfg['encryption'])
        elif index in [4,5,8,9]:
            ts_name = "WISPr MAC auth bypass %s %s %s sta %s" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_encryption'])
        elif index in [10,11,12,13]:
            ts_name = "WISPr MAC auth bypass %s %s %s sta %s" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'])
        elif index in [14,15,16,17]:
            ts_name = "WISPr MAC auth bypass %s %s %s sta %s %s" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('_', ''), wlan_cfg['encryption'], wlan_cfg['sta_wpa_ver'], 
                                                                    wlan_cfg['sta_encryption'])
        elif index in [18,19]:
            ts_name = "WISPr MAC auth bypass %s %s" % (wlan_cfg['auth'], wlan_cfg['encryption'])
        else:
            pass
        

    ts = testsuite.get_testsuite(ts_name, ("WISPr MAC auth bypass %s %s %s" % (wlan_cfg['auth'], wlan_cfg['wpa_ver'].replace('-',''), wlan_cfg['encryption'])), combotest=True)

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
