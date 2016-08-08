"""
Verify per client rate limit configuration integrated with WebAuth wlan rate limiting option on root and mesh AP

    Verify rate limit configuration in AP shell and wlan, 
    - Shaper value is correct in mesh AP
    - Send zing traffic, and rate of 50% is between the range [>min_rate, <=allowed_rate]
       min_rate=default is 0
       allowed_rate= rate_limit_mbps * (1.0 + margin_of_error), margin_of_error is 0.2 by default
    - Rate limit range is from 0.10mbps to 20.00mbps step is 0.25mbps excpet value 0.10mbps-0.25mpbs.
    - Coverage: uplink and downlink rate limit is same, uplink     
    
    expect result: All steps should result properly.
    
    How to:
        1) Disable all AP's wlan service
        2) Enable active AP's wlan service based on radio   
        4) Create a wlan and make sure it is in default wlan group
        5) Station associate the WIPSr wlan
        6) Get station wifi address and verify it is in expected subnet
        7) Verify station information in ZD, status is unauthorized
        8) Verify station cannot ping target ip
        9) Perform web authentication, and verify station information in ZD, status is authorized
        10) Verify station can ping target ip
        11) Verify station information in AP side
        12) Verify uplink shaper value in AP side
        13) Verify downlink shaper value in AP side
        14) Verify uplink zing traffic [From linux PC to wireless station]
        15) Verify downlink zing traffic [From wireless station to linux PC]
        16) Verify per client rate limiting in AP shell before WLAN edit in AP
        17) Edit wlan to another rate limiting option
        18) Edit hotspot profile with grace period enabled.
        19) Perform web authentication
        20) Test station reconnecting procedure within grace period time
        21) Verify per client rate limiting in AP shell within grace period time, it should not change.
        22) Test station reconnecting procedure beyond grace period time
        23) Perform web authentication
        24) Verify per client rate limiting in AP shell beyond grace period time, it should not change.
        25) Edit hotspot profile to orginal value without grace period option
        26) Repeat step 4)-25) for all rate limit configuration.
    
Created on 2011-04-25
@author: kevin.tan@ruckuswireless.com
"""

import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

check_wlan_timeout = 5

#WLAN option 1
wlan_cfg_up1   = '10.75mbps'
wlan_cfg_down1 = '9.25mbps'

#WLAN option 2
wlan_cfg_up2   = 'Disabled'
wlan_cfg_down2 = 'Disabled'

#WLAN option for editing WLAN
wlan_cfg_up_edit   = '5.75mbps'
wlan_cfg_down_edit = '8.25mbps'

wlan_cfg_up_edit_str   = '5750kbps'
wlan_cfg_down_edit_str = '8250kbps'

#client radius user configuration
radius_user_cfg =['ras.0kbps', 'ras.36kbps', 
                  'ras.ul.10733.dl.19788kbps', 'ras.30mbps',
                  'ras.20mbps','ras.ul.750.dl.5000kbps']

def _def_expected_rate_limit_cfg_list():
    '''
    uplink and downlink rate limit is between 0.10mbps - 20.00mbps.
    '''
    expected_rate_cfg_list = []

    #uplink 10.75mbps, downlink 9.25mbps in WLAN configuration
    expected_rate_cfg_list.append(dict(uplink_rate_limit = "10.75mbps", downlink_rate_limit = "9.25mbps", margin_of_error = 0.2,
                                       uplink_str_in_ap  = "10750kbps", downlink_str_in_ap  = "9250kbps"))    
    expected_rate_cfg_list.append(dict(uplink_rate_limit = "0.10mbps", downlink_rate_limit = "0.10mbps", margin_of_error = 0.2,
                                       uplink_str_in_ap  = "100kbps",  downlink_str_in_ap  = "100kbps"))

    expected_rate_cfg_list.append(dict(uplink_rate_limit = "10.75mbps", downlink_rate_limit = "20.00mbps", margin_of_error = 0.2,
                                       uplink_str_in_ap  = "10750kbps", downlink_str_in_ap  = "20000kbps"))
    expected_rate_cfg_list.append(dict(uplink_rate_limit = "20.00mbps", downlink_rate_limit = "20.00mbps", margin_of_error = 0.2,
                                       uplink_str_in_ap  = "20000kbps", downlink_str_in_ap  = "20000kbps"))

    #uplink and downlink are both no limiting in WLAN configuration
    expected_rate_cfg_list.append(dict(uplink_rate_limit = "20.00mbps", downlink_rate_limit = "20.00mbps", margin_of_error = 0.2,
                                       uplink_str_in_ap  = "20000kbps", downlink_str_in_ap  = "20000kbps"))
    expected_rate_cfg_list.append(dict(uplink_rate_limit = "0.75mbps", downlink_rate_limit = "5.00mbps", margin_of_error = 0.2,
                                       uplink_str_in_ap  = "750kbps", downlink_str_in_ap  = "5000kbps"))

    return expected_rate_cfg_list    

def _define_wlan_cfg(uplink_rate_limit, downlink_rate_limit, auth_svr = '', do_tunnel=False, vlan_id='',do_grace_period=False, grace_period='2'):
    wlan_cfg = dict(ssid='rate-limit-test', auth="open", encryption="none")
    
    wlan_cfg['uplink_rate_limit'] = uplink_rate_limit
    wlan_cfg['downlink_rate_limit'] = downlink_rate_limit
    
    wlan_cfg['do_webauth'] = True
    if auth_svr:
        wlan_cfg['auth_svr'] = auth_svr

    if do_tunnel:
        wlan_cfg['do_tunnel'] = do_tunnel
    
    if vlan_id:
        wlan_cfg['vlan_id'] = vlan_id #In 9.4 LCS version, default vlan_id is 1, but other versions have null default vlan_id
    
    wlan_cfg['do_grace_period'] = do_grace_period
    if do_grace_period:
        wlan_cfg['grace_period'] = grace_period

    return wlan_cfg

def define_test_cfg(cfg):
    test_cfgs = []
    
    ras_cfg = cfg['ras_cfg']

    target_ip_addr = cfg['target_ping_ip_addr']
    radio_mode = cfg['radio_mode']
    do_tunnel = cfg['do_tunnel']
    vlan_id  = cfg['vlan_id']

    do_grace_period = cfg['do_grace_period']
    grace_period = cfg['grace_period']
    
    expected_list = _def_expected_rate_limit_cfg_list()
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag1 = 'ap%s1' % radio_mode
    ap_tag2 = 'ap%s2' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    #Station    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))
    #AP config
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag1}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag1,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    j=0
    for rate_cfg in expected_list:
        j = j+1
        
        if j < 4:
            #WLAN rate_limiting_option: uplink 10.25mbps, downlink 9.75mbps 
            wlan_rate_option_up = wlan_cfg_up1
            wlan_rate_option_down = wlan_cfg_down1

            ap_tag = ap_tag1 # Verify AP info and test AP on AP1
        else:
            #WLAN rate_limiting_option: both uplink & downlink no limiting 
            wlan_rate_option_up = wlan_cfg_up2
            wlan_rate_option_down = wlan_cfg_down2

            ap_tag = ap_tag2 # Verify AP info and test AP on AP2

        expected_uplink = rate_cfg['uplink_rate_limit']
        expected_downlink = rate_cfg['downlink_rate_limit']
        
        expected_ul_str = rate_cfg['uplink_str_in_ap']
        expected_dl_str = rate_cfg['downlink_str_in_ap']

        margin_of_error = rate_cfg['margin_of_error']

        if j==4:
            test_name = 'CB_ZD_Config_AP_Radio'
            common_name = 'Config active AP 1 Radio %s - Disable WLAN Service' % (radio_mode)
            test_params = {'cfg_type': 'config',
                           'ap_tag': ap_tag1,
                           'ap_cfg': {'radio': radio_mode, 'wlan_service': False},
                   }
            test_cfgs.append((test_params, test_name, common_name, 0, False))
            
            test_name = 'CB_ZD_Create_Active_AP'
            common_name = 'Create active AP 2'
            test_cfgs.append(({'active_ap':cfg['active_ap_list'][1],
                               'ap_tag': ap_tag2}, test_name, common_name, 0, False))
            
            test_name = 'CB_ZD_Config_AP_Radio'
            common_name = 'Config active AP 2 Radio %s - Enable WLAN Service' % (radio_mode)
            test_params = {'cfg_type': 'config',
                           'ap_tag': ap_tag2,
                           'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
            test_cfgs.append((test_params, test_name, common_name, 0, False))

        # WLAN configuration
        wlan_cfg = _define_wlan_cfg(wlan_rate_option_up, wlan_rate_option_down, ras_cfg['server_name'], do_tunnel, vlan_id, do_grace_period, grace_period)
        
        test_case_name = '[WLAN Up=%s-Down=%s, Radius %s]' % (wlan_rate_option_up, wlan_rate_option_down, radius_user_cfg[j-1])
    
        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sCreate WLAN on ZD' % (test_case_name,)
        test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                           'enable_wlan_on_default_wlan_group': True,
                           'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 1, False))
            
        expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP' % (test_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': ap_tag}, test_name, common_name, 2, False))
        
        test_cfgs.extend(_define_sta_before_auth_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag))

        test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
        common_name = '%sPerform Web authentication for client' % (test_case_name)
        test_cfgs.append(({'sta_tag':sta_tag, 
                           'browser_tag': browser_tag,
                           'username': radius_user_cfg[j-1], 
                           'password': radius_user_cfg[j-1]},  
                           test_name, common_name, 2, False)) 

        test_cfgs.extend(_define_sta_after_auth_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, radius_user_cfg[j-1]))

        test_name = 'CB_ZD_Verify_AP_Shaper'
        common_name = '%sVerify uplink shaper in AP' % (test_case_name)
        test_cfgs.append(({'rate_limit': wlan_rate_option_up,
                           'link_type': 'up',
                           'ap_tag': ap_tag,
                           'ssid': wlan_cfg['ssid']}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Shaper'
        common_name = '%sVerify downlink shaper in AP' % (test_case_name)
        test_cfgs.append(({'rate_limit': wlan_rate_option_down,
                           'link_type': 'down',
                           'ap_tag': ap_tag,
                           'ssid': wlan_cfg['ssid']}, test_name, common_name, 2, False))

        test_name = 'CB_Zing_Traffic_Station_LinuxPC'
        common_name = '%sSend downlink zap traffic and verify traffic rate' % (test_case_name)
        test_cfgs.append(({'rate_limit': expected_downlink,
                           'margin_of_error': margin_of_error,
                           'link_type': 'down',
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_Zing_Traffic_Station_LinuxPC'
        common_name = '%sSend uplink zing traffic and verify traffic rate' % (test_case_name)
        test_cfgs.append(({'rate_limit': expected_uplink,
                           'margin_of_error': margin_of_error,
                           'link_type': 'up',
                           'sta_tag': sta_tag,
                           'ssid': wlan_cfg['ssid']}, test_name, common_name, 2, False))


        test_name = 'CB_ZD_Verify_AP_PerClient_RateLimit'
        common_name = '%sVerify per client rate limiting before WLAN edit in AP' % (test_case_name)
        test_cfgs.append(({'ap_tag': ap_tag,
                           'ssid': wlan_cfg['ssid'],
                           'sta_tag': sta_tag,
                           'client_ul_rate':expected_ul_str,
                           'client_dl_rate':expected_dl_str,
                           },
                           test_name, common_name, 2, False))

        # WLAN configuration
        edit_wlan_cfg = _define_wlan_cfg(wlan_cfg_up_edit, wlan_cfg_down_edit)

        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sEdit WLAN on ZD' % (test_case_name,)
        test_cfgs.append(({'wlan_cfg_list':[edit_wlan_cfg],
                           'check_wlan_timeout': check_wlan_timeout}, test_name, common_name, 2, False))

        #If radius user rate limit value is set to 0 ,client should follow ZD GUI rate limiting setting.
        if j == 1:
            expected_ul_str = wlan_cfg_up_edit_str
            expected_dl_str = wlan_cfg_down_edit_str

        # Grace Period Integration
        if do_grace_period:
            new_wlan_cfg = deepcopy(edit_wlan_cfg)
            new_wlan_cfg['do_grace_period'] = do_grace_period
            new_wlan_cfg['grace_period'] = grace_period
            
            test_name = 'CB_ZD_Create_Wlan'
            common_name = '%sEdit WLAN with grace period enabled' % (test_case_name,)
            test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg]}, test_name, common_name, 2, False))

            test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
            common_name = '%sPerform Web Authentication after editing WLAN for client' % (test_case_name)
            test_cfgs.append(({'sta_tag':sta_tag, 
                               'browser_tag': browser_tag,
                               'username': radius_user_cfg[j-1], 
                               'password': radius_user_cfg[j-1]},  
                               test_name, common_name, 2, False)) 

            test_name = 'CB_ZD_Test_Grace_Period'
            common_name = "%sTest station reconnect within grace period time" % (test_case_name)
            test_params = {'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'grace_period': grace_period,
                           'reconnect_within_gp': True,
                           'no_need_auth': True,
                           'wlan_cfg': wlan_cfg,
                           'username': radius_user_cfg[j-1],
                           'radio_mode': radio_mode,
                           'target_ip': target_ip_addr,
                           }
            test_cfgs.append((test_params, test_name, common_name, 2, False))

            test_name = 'CB_ZD_Verify_AP_PerClient_RateLimit'
            common_name = '%sVerify client rate limit reconnect within grace period' % (test_case_name)
            test_cfgs.append(({'ap_tag': ap_tag,
                               'ssid': wlan_cfg['ssid'],
                               'sta_tag': sta_tag,
                               'client_ul_rate':expected_ul_str,
                               'client_dl_rate':expected_dl_str,
                               },
                               test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_Test_Grace_Period'
            common_name = "%sReTest station reconnect beyond grace period time" % (test_case_name)
            test_params = {'sta_tag': sta_tag,
                           'ap_tag': ap_tag,
                           'grace_period': grace_period,
                           'reconnect_within_gp': False,
                           'no_need_auth': False,
                           'wlan_cfg': wlan_cfg,
                           'username': radius_user_cfg[j-1],
                           'radio_mode': radio_mode,
                           'target_ip': target_ip_addr,
                           }
            test_cfgs.append((test_params, test_name, common_name, 2, False))

            test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
            common_name = '%sPerform Hotspot auth for client reconnect beyond grace period' % (test_case_name)
            test_cfgs.append(({'sta_tag':sta_tag, 
                               'browser_tag': browser_tag,
                               'username': radius_user_cfg[j-1], 
                               'password': radius_user_cfg[j-1]},  
                               test_name, common_name, 2, False)) 

            test_name = 'CB_ZD_Verify_AP_PerClient_RateLimit'
            common_name = '%sVerify client rate limit reconnect beyond grace period' % (test_case_name)
            test_cfgs.append(({'ap_tag': ap_tag,
                               'ssid': wlan_cfg['ssid'],
                               'sta_tag': sta_tag,
                               'client_ul_rate':expected_ul_str,
                               'client_dl_rate':expected_dl_str,
                               },
                               test_name, common_name, 2, False))

        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = '%sRemove the wlan from ZD' % (test_case_name)
        test_cfgs.append(({}, test_name, common_name, 2, True))


    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))
    
    #@author:yuyanan @since:2014-8-15 optimize:add test step: remove aaa server
    test_name = 'CB_ZD_CLI_Delete_AAA_Servers'
    common_name = 'Remove all AAA servers'
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
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])
        elif radio in ['na']:
            MAXIMUM_WLAN = 8
            wlan_name = "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])

    return expect_wlan_info

def _define_sta_before_auth_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_wpa_auto=False):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    ssid = wlan_cfg['ssid']
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information before auth in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client cannot ping a target IP before auth' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'disallowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
    
    return test_cfgs

def _define_sta_after_auth_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, username, is_wpa_auto=False):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    ssid = wlan_cfg['ssid']
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information after auth in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username':username},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP after auth' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name)
    test_cfgs.append(({'ssid': wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    return test_cfgs

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
    
    enable_tunnel = ''
    enable_vlan = True
    auth_method_option = ''

    target_sta_radio = 'ng'
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")

        enable_tunnel = raw_input("Is tunnel mode enabled? [y/n]: ").lower() == "y"
        auth_method_option = raw_input("Select Radius Auth Method: [y(PAP)/n(CHAP)]: ").lower() == "y"

        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
            
    if enable_tunnel:
        do_tunnel = True
    else:
        do_tunnel = False

    if auth_method_option:
        radius_auth_method = 'pap'
    else:
        radius_auth_method = 'chap'

    server_ip_addr  = testsuite.getTestbedServerIp(tbcfg)

    target_ping_ip_addr = server_ip_addr
    expected_subnet = utils.get_network_address(server_ip_addr, expected_sub_mask)
    vlan_id = ''

    if enable_vlan:
        target_ping_ip_addr = '20.0.2.252'
        expected_subnet = '20.0.2.0'
        vlan_id = 2

    ras_name = 'ruckus-radius-%s' % (time.strftime("%H%M%S"),)

    tcfg = {'ras_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1812',
                    'server_name' : ras_name,
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': radius_auth_method,
                    },
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
            'do_tunnel': do_tunnel,
            'do_grace_period': True,
            'grace_period': '2',
            'vlan_id': vlan_id,
            }
    
    test_cfgs = define_test_cfg(tcfg)
    
    tmp_radius_auth_method = ""
    tmp_enable_tunnel = ""

    if not auth_method_option:
        tmp_radius_auth_method = " - CHAP" 
    else:
        tmp_radius_auth_method = " - PAP"

    if enable_tunnel:
        tmp_enable_tunnel = " - Tunnel" 

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "PerClient Rate Limiting%s - WebAuth%s" % (tmp_radius_auth_method, tmp_enable_tunnel)


    ts = testsuite.get_testsuite(ts_name, "Verify PerClient rate limit" , combotest=True)

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
