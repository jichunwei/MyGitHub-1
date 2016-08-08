"""
Verify Radius accounting Interim update procedure like Cisco
     Different Acct-Interim interval, such as 1 minute, 2 minutes, 0, etc.
     There're two ways to configure the value, one is on ZD GUI WLAN, the other is on Radius user file, and Radius user prior to ZD GUI WLAN.
        a. 1 min in WLAN configuration, client has no radius attribution
        b. 1 min in WLAN configuration, client has radius attribution value 0 min
        c. 1 min in WLAN configuration, client has radius attribution 2 min

        d. 0 min in WLAN configuration, client has no radius attribution
        e. 0 min in WLAN configuration, client has radius attribution 0 min
        f. 0 min in WLAN configuration, client has radius attribution 1 min
     
    expect result: All steps should result properly.
    
    How to:
        1) Disable all AP's wlan service
        2) Enable active AP's wlan service based on radio
        3) Create Radius authentication server
        4) Create Radius Accounting server
        5) Create Hotspot profile, enable Radius Accounting, and select Radius server as authentication database
        6) Create a WISPr wlan with created Hotspot profile
        7) Station associate the wlan
        8) Get station wifi address
        9) Verify station information in ZD, status is unauthorized
        10) Perform Hotspot authentication, and verify station information in ZD, status is authorized
        11) Verify radius accounting start message and parameters(User-Name, NAS-ID type, NAS-Identify, ...)
        12) Verify radius accounting interim update message and parameters(User-Name, NAS-ID type, NAS-Identify, ...) after 1 minute
        13) Client disconnects from the WLAN
        14) Verify radius accounting stop message and parameters(User-Name, NAS-ID type, NAS-Identify, ...)
        15) Modify radius accounting interim update value in WLAN config, and use different radius subscriber to perform web authentication
        16) Repeat step 7)-14)
    
Created on 2012-0918
@author: kevin.tan
"""

import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

check_wlan_timeout  = 5
wlan_interim_update = '1'      #minute: Radius accounting interim update interval

#client radius user configuration
radius_user ={'1': 'ras.interim.1min', '2':'ras.interim.2min', '0':'ras.interim.0min', 'none':'ras.interim.none'}

def _define_wlan_cfg_hotspot(hs_name='', rad_user='', do_tunnel=False, vlan_id=''):
    wlan_cfg = dict(ssid='ras-acct-cisco-interim-update', auth="open", encryption="none")
    
    wlan_cfg['type'] = 'hotspot'
    wlan_cfg['hotspot_profile'] = hs_name

    wlan_cfg['username']        = rad_user
    wlan_cfg['password']        = rad_user

    if do_tunnel:
        wlan_cfg['do_tunnel'] = do_tunnel
    
    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id #In 9.4 LCS version, default vlan_id is 1, but other versions have null default vlan_id
    
    return wlan_cfg

def define_test_cfg(cfg):
    test_cfgs = []
    
    ras_cfg = cfg['ras_cfg']
    ras_acct_cfg = cfg['ras_acct_cfg']
    hs_cfg = cfg['hotspot_cfg']

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
    acct_authentic = 'Radius'
    nas_id_type='wlan-bssid'
    
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
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius Accounting server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_acct_cfg]}, test_name, common_name, 0, False))

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
    test_params = {'cfg_type': 'init'}
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

    test_name = 'CB_ZD_Start_Radius_Server_Nohup'
    common_name = 'Start radius server in the background by nohup option'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    rad_user = radius_user['none']
    wlan_cfg = _define_wlan_cfg_hotspot(hs_cfg['name'], rad_user, do_tunnel, vlan_id)

    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create WLAN on ZD'
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                       'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 0, False))
        
    #WLAN hotspot config 1 min, radius config none, no interim update parameter in response message
    test_case_name = '[Radius Acct Hotspot %smin, %s]' % (wlan_interim_update, rad_user)

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
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
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Start Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Start',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Interim Update Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Interim-Update',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       'acct_session_time': int(wlan_interim_update)*60,
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for user %s' % (test_case_name, rad_user)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Stop Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Stop',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))

    #WLAN hotspot config 1min, radius config 0min
    interval = '0'
    rad_user = radius_user[interval]
    test_case_name = '[Radius Acct Hotspot %smin, %s]' % (wlan_interim_update, rad_user)

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
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
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Start Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Start',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Interim Update Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Interim-Update',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       'acct_session_time': int(wlan_interim_update)*60,
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for user %s' % (test_case_name, rad_user)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Stop Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Stop',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))

    #WLAN hotspot config 1min, radius config 2min
    interval = '2'
    rad_user = radius_user[interval]
    test_case_name = '[Radius Acct Hotspot %smin, %s]' % (wlan_interim_update, rad_user)

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
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
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Start Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Start',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Interim Update Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Interim-Update',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       'acct_session_time': int(interval)*60,
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for user %s' % (test_case_name, rad_user)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Stop Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Stop',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))

    #Edit hotspot profile from 1 min to 0 min
    new_hs_cfg = deepcopy(hs_cfg)
    new_hs_cfg['interim_update_interval'] = '0'

    test_name = 'CB_ZD_Edit_Hotspot_Profiles'
    common_name = 'Edit Hotspot profile to new interim update interval %s min' % (new_hs_cfg['interim_update_interval'])
    test_cfgs.append(({'hotspot_profiles_list':[new_hs_cfg]}, test_name, common_name, 0, False))

    #WLAN hotspot config 0 min, radius config none, no interim update parameter in response message
    rad_user = radius_user['none']
    test_case_name = '[Radius Acct Hotspot %smin, %s]' % (new_hs_cfg['interim_update_interval'], rad_user)

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
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
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Start Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Start',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Interim Update Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'log_display': False,
                       'acct_status_type': 'Interim-Update',
                       'acct_session_time': 120,
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for user %s' % (test_case_name, rad_user)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Stop Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Stop',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))

    #WLAN hotspot config 0min, radius config 0min
    interval = '0'
    rad_user = radius_user[interval]
    test_case_name = '[Radius Acct Hotspot %smin, %s]' % (new_hs_cfg['interim_update_interval'], rad_user)

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
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
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Start Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Start',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Interim Update Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'log_display': False,
                       'acct_status_type': 'Interim-Update',
                       'acct_session_time': 120,
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for user %s' % (test_case_name, rad_user)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Stop Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Stop',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))

    #WLAN hotspot config 0min, radius config 1min
    interval = '1'
    rad_user = radius_user[interval]
    test_case_name = '[Radius Acct Hotspot %smin, %s]' % (new_hs_cfg['interim_update_interval'], rad_user)

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
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
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Start Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Start',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Interim Update Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Interim-Update',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       'acct_session_time': int(interval)*60,
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan from station for user %s' % (test_case_name, rad_user)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Radius_Acct_Message'
    common_name = '%sVerify Radius Accounting Stop Message' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,
                       'acct_status_type': 'Stop',
                       'acct_authentic': acct_authentic,
                       'acct_user_name': rad_user,
                       'acct_nas_id_type': nas_id_type,
                       },
                       test_name, common_name, 2, False))

    #Clear Environment at last
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove the wlan from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Restart_Service'
    common_name = 'Restart radius server'
    test_cfgs.append(({'service':'radiusd'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))

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

    ras_name = 'radius-%s' % (time.strftime("%H%M%S"),)
    ras_acct_name = 'radius-acct-%s' % (time.strftime("%H%M%S"),)

    tcfg = {'ras_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1812',
                    'server_name' : ras_name,
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': 'chap',
                    },
            'ras_acct_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1813',
                    'server_name' : ras_acct_name,
                    'radius_acct_secret': '1234567890',
                    },
            'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                            'name': 'hs_radius_acct',
                            'auth_svr': ras_name,
                            'acct_svr': ras_acct_name,
                            'interim_update_interval': wlan_interim_update,
                            'idle_timeout': None,
                            },
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
            'do_tunnel': False,
            'do_grace_period': False,
            'grace_period': '',
            'vlan_id': '',
            }
    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Radius Accounting like Cisco - Interim Update"

    ts = testsuite.get_testsuite(ts_name, "Radius Accounting like Cisco - Interim Update" , combotest=True)

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