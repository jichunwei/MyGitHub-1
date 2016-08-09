"""
Verify Autonomous WLAN Max Clients supported.
Note that when AP disconnected and connected again, clients will be forced to disconnect from Autonomous WLAN first.
Reason:
Due the to implementation of AP manager in AP side, which is not able to aware the differences between the current active configurations 
and configuration updates from ZoneDirector, all WLAN services will be removed first when APs re-join ZoneDirector once it is reachable. 
This behavior will cause all connected wireless stations to be disconnected.

    expect result: All steps should result properly.
    
    How to:
        1) Create an Autonomous wlan, encryption type is selected value(open-none, WPA/WP2 AES/TKIP, WEP, etc.)
        2) Set max clients number to 2 in WLAN or AP group AP model configuration
        3) Verify client 1 can connect to the WLAN with Authorized status, and can ping target server successfully.
        4) Verify client 2 can connect to the WLAN with Authorized status, and can ping target server successfully.
        5) Disconnect client 1 and 2
        6) Set max clients number to only 1 in WLAN or AP group AP model configuration
        7) Verify client 1 can connect to the WLAN with Authorized status, and can ping target server successfully.
        8) Verify client 2 assoicate to the WLAN failed with warning event.
        9) Set max clients number to 2 in WLAN or AP group AP model configuration
        10) Verify client 1 can connect to the WLAN with Authorized status, and can ping target server successfully.
        11) Verify client 2 can connect to the WLAN with Authorized status, and can ping target server successfully.
        12) Add an invalid route is ZD 'Static Route' table and wait AP disconnected
        13) Set max clients number to only 1 in WLAN or AP group AP model configuration
        14) Delete the invalid route is ZD 'Static Route' table and wait AP reconnected
        15) Verify only one client can connect to the WLAN with Authorized status, and can ping target server successfully. 
            The other is refused to access it with warning event.
        16) Remove the WLAN and set mac clients number to default in AP group AP model table

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

def _define_wlan_cfg(auth='open', wpa_ver = '', encryption = 'none', key_index = '1', key_string = '', 
                     sta_auth = '', sta_wpa_ver = '', sta_encryption = '', 
                     vlan_id = ''):
    wlan_cfg = dict(ssid='autonomous-auto-test', auth=auth, wpa_ver=wpa_ver, encryption=encryption, key_index=key_index, key_string=key_string,
                    sta_auth=sta_auth, sta_wpa_ver=sta_wpa_ver, sta_encryption=sta_encryption)
    
    wlan_cfg['type'] = 'autonomous'

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

    sta_tag1 = 'sta1%s' % radio_mode
    sta_tag2 = 'sta2%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station 1'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station_1'],
                       'sta_tag': sta_tag1}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station 2'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station_2'],
                       'sta_tag': sta_tag2}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station 1'
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station 2'
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 0, False))

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

    wlan_cfg = _define_wlan_cfg(wlan_cfg_param[0], wlan_cfg_param[1], wlan_cfg_param[2], wlan_cfg_param[3], wlan_cfg_param[4],\
                                wlan_cfg_param[5], wlan_cfg_param[6], wlan_cfg_param[7], cfg['vlan_id'])

    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create WLAN on ZD'
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg], 
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 0, False))


########################################## case 1 ############################################################
    test_case_name = "[Configure in WLAN, equal to max clients]"

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sSet WLAN max clients number to 2' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '2'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 1 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 1 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 1 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 2 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 2 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 2 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sRecover WLAN max clients number to default' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '100'}, test_name, common_name, 2, True))

########################################## case 2 ############################################################
    test_case_name = "[Configure in WLAN, exceed max clients]"

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sSet WLAN max clients number to only 1' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '1'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 1 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 1 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 1 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all event' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 2 to the WLAN should failed' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg, 'is_negative':True, 'failed_event':'max_client_exceed',
                       'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sRecover WLAN max clients number to deafult' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '100'}, test_name, common_name, 2, True))

########################################## case 3 ############################################################
    test_case_name = "[Configure in AP group, equal to max clients]"

    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sSet max client number in AP group to 2' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'grp_name':'System Default','set_type':'Value', 'number': '2'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 1 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 1 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 1 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 2 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 2 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 2 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sRecover max client number in AP group to default' % (test_case_name)
    test_cfgs.append(({'grp_name':'System Default','set_type':'Max'}, test_name, common_name, 2, True))

########################################## case 4 ############################################################
    test_case_name = "[Configure in AP group, exceed max clients]"

    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sSet max client number in AP group to only 1' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'grp_name':'System Default','set_type':'Value', 'number': '1'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 1 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 1 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 1 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all event' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 2 to the WLAN should failed' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg, 'is_negative':True, 'failed_event':'max_client_exceed',
                       'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sRecover max client number in AP group to default' % (test_case_name)
    test_cfgs.append(({'grp_name':'System Default','set_type':'Max'}, test_name, common_name, 2, True))

########################################## case 5 ############################################################
    test_case_name = "[WLAN config, AP disconnected then connected]"

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sSet WLAN max clients number to 2' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '2'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 1 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 1 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 1 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 2 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 2 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 2 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure an invalid route to AP' % (test_case_name)
    test_cfgs.append(({'operation': 'add',
                        'parameter': None, 'ap_tag': ap_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sWait active AP status changed to disconnected' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'disconnected'}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlans'
    common_name = '%sCheck WLAN is still available in AP CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag,  
                       'num_of_ssids':1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sSet WLAN max clients number to 1' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete all static routes' % (test_case_name)
    test_cfgs.append(({'operation': 'delete all'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all event' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sWait active AP status changed back to connected' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected',
                       'ap_cfg': {'radio': radio_mode, 'wlan_service': True},}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Max_Clients_Info'
    common_name = '%sVerify only one client is permitted to access, the other is refused' % (test_case_name)
    test_cfgs.append(({'sta_tag_list': [sta_tag1,sta_tag2], 'ap_tag': ap_tag, 'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sRecover WLAN max clients number to default' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '100'}, test_name, common_name, 2, True))

########################################## case 6 ############################################################
    test_case_name = "[AP group config, AP disconnected then connected]"

    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sSet max client number in AP group to 2' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'grp_name':'System Default','set_type':'Value', 'number': '2'}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 1 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 1 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 1 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag1,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station 2 to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client 2 information Authorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client 2 can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag2,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sConfigure an invalid route to AP' % (test_case_name)
    test_cfgs.append(({'operation': 'add',
                        'parameter': None, 'ap_tag': ap_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sWait active AP status changed to disconnected' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'disconnected'}, test_name, common_name, 2, False))

    test_name = 'CB_AP_CLI_Check_Wlans'
    common_name = '%sCheck WLAN is still available in AP CLI' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag,  
                       'num_of_ssids':1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Wlan_Max_Clients_Number'
    common_name = '%sSet WLAN max clients number to 1' % (test_case_name)
    test_cfgs.append(({'wlan_name':wlan_cfg['ssid'],
                       'number': '1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Config_Static_Route'
    common_name = '%sDelete all static routes' % (test_case_name)
    test_cfgs.append(({'operation': 'delete all'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all event' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sWait active AP status changed back to connected' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected',
                       'ap_cfg': {'radio': radio_mode, 'wlan_service': True},}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Max_Clients_Info'
    common_name = '%sVerify only one client is permitted to access, the other is refused' % (test_case_name)
    test_cfgs.append(({'sta_tag_list': [sta_tag1, sta_tag2], 'ap_tag': ap_tag, 'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 1' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag1}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station 2' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag2}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Set_AP_Model_Max_Clients_Number' 
    common_name = '%sRecover max client number in AP group to default' % (test_case_name)
    test_cfgs.append(({'grp_name':'System Default','set_type':'Max'}, test_name, common_name, 2, True))

    #Recover test environment
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD at last'
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
    
    expected_sub_mask = '255.255.255.0'
    
    if ts_cfg["interactive_mode"]:
        target_sta1 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 1: ")
        target_sta2 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 2: ")
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta1 = sta_ip_list[ts_cfg["station"][0]]
        target_sta2 = sta_ip_list[ts_cfg["station"][1]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    server_ip_addr  = testsuite.getTestbedServerIp(tbcfg)
    target_ping_ip_addr = '172.16.10.252'

    expected_subnet = utils.get_network_address(server_ip_addr, expected_sub_mask)

    tcfg = {
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station_1':'%s' % target_sta1,
            'target_station_2':'%s' % target_sta2,
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
        ts_name = "Autonomous WLAN Max Clients"

    ts = testsuite.get_testsuite(ts_name, ("Autonomous WLAN Max Clients"), combotest=True)

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
