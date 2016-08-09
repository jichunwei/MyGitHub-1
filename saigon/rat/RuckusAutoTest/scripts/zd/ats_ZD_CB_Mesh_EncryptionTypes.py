"""
Mesh with different encryption types and AP is in default wlan group

    Verify Mesh works well for different encryption types wlan.
    Encryption type coverage:
        encryption_type_list = [
            'Open None',                                 
            'Open WPA TKIP',
            'Open WPA AES',
            'Open WPA Auto', -> 2 cases
            'Open WPA2 TKIP',
            'Open WPA2 AES',                             
            'Open WPA2 Auto', -> 2 cases                 
            'Open WPA-Mixed TKIP', -> 2 cases
            'Open WPA-Mixed AES', -> 2 cases             
            'Open WPA-Mixed Auto', -> 4 cases            
            'Open WEP-64',                               
            'Open WEP-128',                              
            'Shared WEP-64',
            'Shared WEP-128',
            'EAP None',                                  
            'EAP WPA TKIP',
            'EAP WPA AES',
            'EAP WPA Auto', -> 2 cases
            'EAP WPA2 TKIP',                             
            'EAP WPA2 AES',                              
            'EAP WPA2 Auto', -> 2 cases                  
            'EAP WPA-Mixed TKIP', -> 2 cases    
            'EAP WPA-Mixed AES', -> 2 cases              
            'EAP WPA-Mixed Auto', -> 4 cases             
            'EAP WEP-64',                                
            'EAP WEP-128',                               
        ]
    The total combination is 26.

    The Encryption Algorithm: Auto means:
    -  Select "Auto" on the ZD
    -  Test station encryption with TKIP
    -  Test station encryption with AES

    The Encryption Method: WPA-Mixed means:
    -  Select "WPA-Mixed" on the ZD
    -  Test station encryption with WPA
    -  Test station encryption with WPA2

    The final number of cases is 40.


    expect result: All steps should result properly.

    How to:
        1) Disable all AP's wlan service
        2) Enable active AP's wlan service based on radio
        4) Create a wlan and make sure it is in default wlan group
        5) Station associate the wlan
        6) Get station wifi address and verify it is in expected subnet
        6) Verify station information in ZD, status is unauthorized
        7) Verify station can't ping target ip
        7) Perform web authentication in Station
        8) Verify station information in ZD, status is authorized
        9) Verify station can ping target ip
        10) Verify station can download a file from server
        11) Verify station information in AP side

Created on 2011-08-01
@author: cherry.cheng@ruckuswireless.com

Added Mesh and expanded to cover 26 cases of Encryption Types
@since: 2011-09-09
@author: phan.nguyen@ruckuswireless.com
"""

import sys
import time
import re
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

encryption_type_list = [
    'Open None',
#    'Open WPA TKIP',
#    'Open WPA AES',
#    'Open WPA Auto',
#    'Open WPA2 TKIP',
    'Open WPA2 AES',
    'Open WPA2 Auto',
#    'Open WPA-Mixed TKIP',
    'Open WPA-Mixed AES',
    'Open WPA-Mixed Auto',
    'Open WEP-64',
    'Open WEP-128',
#    'Shared WEP-64',
#    'Shared WEP-128',
    'EAP None',
#    'EAP WPA TKIP',
#    'EAP WPA AES',
#    'EAP WPA Auto',
#    'EAP WPA2 TKIP',
    'EAP WPA2 AES',
    'EAP WPA2 Auto',
#    'EAP WPA-Mixed TKIP',
    'EAP WPA-Mixed AES',
    'EAP WPA-Mixed Auto',
    'EAP WEP-64',
    'EAP WEP-128',
]

def _get_wlan_cfg(ssid, wlan_params):
    wlan_cfg = dict(
        ssid = ssid,
    )
    wlan_cfg.update(wlan_params)

    return wlan_cfg


def _define_wlan_cfg(ssid, ras_name, encryption_type_list):
    wlan_cfgs = []

    for encryption_type in encryption_type_list:
        if encryption_type in ['Open None']:
            wlan_params = dict(
                auth = "open", encryption = "none",
                sta_auth = "open", sta_encryption = "none",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WEP-64']:
            wlan_params = dict(
                auth = "open", encryption = "WEP-64",
                key_index = "1" ,
                key_string = utils.make_random_string(10, "hex"),
                sta_auth = "open",
                sta_encryption = "WEP-64",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WEP-128']:
            wlan_params = dict(
                auth = "open", encryption = "WEP-128",
                auth_svr = ras_name,
                key_index = "1" ,
                key_string = utils.make_random_string(26, "hex"),
                sta_auth = "open",
                sta_encryption = "WEP-128",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Shared WEP-64']:
            wlan_params = dict(
                auth = "shared", encryption = "WEP-64",
                key_index = "1" ,
                key_string = utils.make_random_string(10, "hex"),
                sta_auth = "shared", sta_encryption = "WEP-64",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Shared WEP-128']:
            wlan_params = dict(
                auth = "shared", encryption = "WEP-128",
                auth_svr = ras_name,
                key_index = "1" ,
                key_string = utils.make_random_string(26, "hex"),
                sta_auth = "shared", sta_encryption = "WEP-128",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))



        if encryption_type in ['Open WPA TKIP']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WPA AES']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                auth_svr = ras_name,
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WPA Auto']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA", encryption = "Auto",
                auth_svr = ras_name,
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))



        if encryption_type in ['Open WPA2 TKIP']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WPA2 AES']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                auth_svr = ras_name,
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WPA2 Auto']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA2", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA2", encryption = "Auto",
                auth_svr = ras_name,
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))



        if encryption_type in ['Open WPA-Mixed TKIP']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WPA-Mixed AES']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "AES",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "AES",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['Open WPA-Mixed Auto']:
            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))



        if encryption_type in ['EAP WPA TKIP']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WPA AES']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WPA Auto']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))



        if encryption_type in ['EAP WPA2 TKIP']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WPA2 AES']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WPA2 Auto']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA2", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA2", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))



        if encryption_type in ['EAP WPA-Mixed TKIP']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WPA-Mixed AES']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "AES",
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "AES",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WPA-Mixed Auto']:
            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "Auto",
                key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

            wlan_params = dict(
                auth = "EAP", wpa_ver = "WPA_Mixed", encryption = "Auto",
                sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WEP-64']:
            wlan_params = dict(
                auth = "EAP", encryption = "WEP-64",
                key_index = "1" ,
                key_string = "",
                sta_auth = "EAP",
                sta_encryption = "WEP-64",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

        if encryption_type in ['EAP WEP-128']:
            wlan_params = dict(
                auth = "EAP", encryption = "WEP-128",
                key_index = "1" ,
                key_string = "",
                sta_auth = "EAP",
                sta_encryption = "WEP-128",
                username = "ras.eap.user", password = "ras.eap.user",
                auth_svr = ras_name,
            )
            wlan_cfgs.append(_get_wlan_cfg(ssid, deepcopy(wlan_params)))

    return wlan_cfgs


def define_test_cfg(cfg):
    test_cfgs = []

    ras_cfg = cfg['ras_cfg']
    target_ip_addr = ras_cfg['server_addr']
    username = cfg['username']
    password = cfg['password']
    radio_mode = cfg['radio_mode']

    sta_tag = 'sta-%s' % radio_mode
    browser_tag = 'browser-%s' % radio_mode
    ap_tag = 'ap'

    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD and disable switch port connectet to ap %s,let it become mesh ap'% cfg['mesh_ap']
    test_cfgs.append(({'mesh_ap_list':cfg['mesh_ap'],
                       'for_upgrade_test':False},test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create Local User for Authentication'
    test_cfgs.append(({'username': username, 'password': password},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag': browser_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    wg_name = 'Default'
    wg_cfg = dict(name = wg_name, description = None,
                  ap_rp = {radio_mode: {'wlangroups': wg_name}},)
    test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    test_cfgs.append(({'wgs_cfg': wg_cfg,
                       'ap_tag': ap_tag, },
                  test_name, common_name, 0, False))

    wlans_cfg_list = cfg['wlan_cfg_list']
    unique_id = 0
    for wlan_cfg in wlans_cfg_list:
        unique_id += 1
        test_cfgs.extend(_define_test_case_cfg(cfg, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, unique_id))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag': browser_tag}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({},test_name, common_name, 0, True))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, True)) 

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


def _define_test_case_cfg(
        cfg, target_ip_addr, wlan_cfg,
        sta_tag, browser_tag, ap_tag, unique_id = 1
    ):
    '''
    '''
    test_cfgs = []

    new_wlan_cfg = deepcopy(wlan_cfg)

    radio_mode = cfg['radio_mode']
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    username = cfg['username']
    password = cfg['password']

    auth = new_wlan_cfg.get('auth')
    encryption = new_wlan_cfg.get('encryption')
    wpa_ver = new_wlan_cfg.get('wpa_ver')
    key_index = new_wlan_cfg.get('key_index')

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'

    wlan_encrypt = []
    wlan_encrypt.append(auth)

    if wpa_ver:
        wlan_encrypt.append(wpa_ver)

    wlan_encrypt.append(encryption)

    if key_index:
        wlan_encrypt.append(key_index)

    ssid_base = "_".join(wlan_encrypt)
    ssid = "%s-%05d" % (ssid_base, random.randrange(1, 99999))
    new_wlan_cfg['ssid'] = ssid

    wlan_encrypt.append("STA")
    wlan_encrypt.append(new_wlan_cfg['sta_auth'])

    if wpa_ver:
        wlan_encrypt.append(new_wlan_cfg['sta_wpa_ver'])

    wlan_encrypt.append(new_wlan_cfg['sta_encryption'])

    test_case_name = '[%s.%s]' % (unique_id, "_".join(wlan_encrypt), )

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, new_wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg': new_wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information in ZD' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode': sta_radio_mode,
                       'username': username},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = '%sVerify download file from server' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag': browser_tag,
                       #'validation_url': "http://%s/authenticated/" % target_ip_addr,
                       }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name,)
    test_cfgs.append(({'ssid': new_wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group'
    common_name = '%sRemove wlan %s from default wlan group' % (test_case_name, new_wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_name_list': [new_wlan_cfg['ssid']]}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLAN from ZD %s' % (test_case_name, new_wlan_cfg['ssid'])
    test_cfgs.append(({}, test_name, common_name, 2, True))

    return test_cfgs


def get_selected_input(depot = [], prompt = ""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select an option. Type q|x or all to exit or get all: "

    selection = []
    i = 0
    while True:
        what = raw_input(prompt + '%s/%s: ' % (i + 1, len(depot)))
        if re.match(r'^(q|x)', what):
            return selection

        elif re.match(r'^(all)', what):
            return depot

        else:
            try:
                val = depot[int(what)]

            except:
                val = ""

            if val:
                selection.append(val)

    return selection


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

    username = 'ras.local.user'
    password = 'ras.local.user'
    expected_sub_mask = '255.255.255.0'

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()

    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap = None
    mesh_ap = []
    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios'] 
        if not target_sta_radio in ap_support_radio_list:
            continue
        
        ret = testsuite.getApTargetType(ap_sym_name, ap_info, ts_cfg["interactive_mode"])
        desired_ap = raw_input("Is this AP under test (y/n)?: ").lower() == "y"
        
        if desired_ap and 'ROOT'.lower() in ret.lower():
            active_ap = ap_sym_name
        
        if desired_ap and 'MESH'.lower() in ret.lower():
            mesh_ap.append(ap_sym_name)
            ap_type_role = ret
        
    if len(mesh_ap) == 0 :
        raise Exception("there is no mesh ap")
        return

    encryption_type = get_selected_input(encryption_type_list)

    ssid = ""
    ras_name = 'ruckus-radius-%s' % (time.strftime("%H%M%S"),)

    wlan_cfg_list = _define_wlan_cfg(ssid, ras_name, encryption_type)

    tcfg = {
        'ras_cfg': {
            'server_addr': ras_ip_addr,
            'server_port' : '1812',
            'server_name' : ras_name,
            'radius_auth_secret': '1234567890',
        },
        'target_station':'%s' % target_sta,
        'active_ap':'%s' % active_ap,
        'mesh_ap': mesh_ap,
        'all_ap_mac_list': all_ap_mac_list,
        'radio_mode': target_sta_radio,
        'wlan_cfg_list': wlan_cfg_list,
        'expected_sub_mask': expected_sub_mask,
        'expected_subnet': utils.get_network_address(ras_ip_addr, expected_sub_mask),
        'username': username,
        'password': password,
    }

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = "MeshEncryptionTypes - 11%s %s" % (target_sta_radio, ap_type_role)

    ts = testsuite.get_testsuite(
        ts_name, 'MeshEncryptionTypes',
        interactive_mode = ts_cfg["interactive_mode"],
        combotest = True,
    )

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

