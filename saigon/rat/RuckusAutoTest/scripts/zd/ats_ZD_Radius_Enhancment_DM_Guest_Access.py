"""
Verify Radius enhancement disconnect message with WLAN type Guest Access
    
    Verify disconnect messages with different attributes:
        a. Calling_Station_Id: the client's mac address 
        b. User_Name: the client's username
        c. Acct_Session_Id: the client's accounting session id

    expect result: All steps should result properly.
    
    How to:
	Preparation:

	01) Remove all the WLANs from ZD
	02) Remove all AAA servers from ZD
	03) Create Radius authentication server
	04) Create Radius Accounting server
	05) Restart radius server
	06) Set the guest access policy
	07) Create target station
	08) Remove all WlANs from station
	09) Start browser in station
	10) Config All APs Radio - Disable WLAN Service
	11) Create active AP
	12) Config active AP Radio ng - Enable WLAN Service
	13) Create WLAN on ZD
        14) Generate a guest pass automatically
	15) Associate the station to the WLAN
	16) Get WiFi address of the station
	17) Verify client information Unauthorized status in ZD
	18) Verify station pinging to the server fails

	Test Process:

        Repeat test process to test valid/invalid Calling_Station_Id/User_Name/Acct_Session_Id

	01) Perform guest authentication in station
	02) Verify client information Authorized status in ZD
	03) Verify station pings to the server successfully
	04) Remove all the events from ZD
	05) Send message and check the output
	06) Verify client status on zd
	07) Check the disconnect event on ZD
	08) Verify station ping to the server
	09) Remove all WlANs from station
	10) Associate the station to the WLAN
	11) Get WiFi address of the station
	12) Verify client information Unauthorized status in ZD

	Clean up:

	01) Remove all the WLANs from ZD for the next test
	02) Select authentication server to original value
	03) Remove all AAA servers from ZD for the next test
	04) Restart radius server for the next test
	05) Config All APs Radio - Enable WLAN Service
	06) Quit browser in Station for the next test
	a07) Remove all WlANs from station for the next test

    
Created on 2013-06
@author: chen.tao@odc-ruckuswireless.com
"""


import sys
import time
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def _define_wlan_cfg_guestpass(acct_svr = '',auth='open', wpa_ver = '', encryption = 'none', 
                             key_index = '1', key_string = '',sta_auth = '', sta_wpa_ver = '', sta_encryption = '',):
    wlan_cfg = dict(auth = auth,wpa_ver = wpa_ver,encryption = encryption,key_index = key_index,
                    key_string = key_string,sta_auth = sta_auth,
                    sta_wpa_ver = sta_wpa_ver,sta_encryption = sta_encryption)
    wlan_cfg['ssid'] = 'Radius_Enhancement_DM_Guest_Acc'
    wlan_cfg['type'] = 'guest'
    wlan_cfg['acct_svr'] = acct_svr
    
    return wlan_cfg

def define_test_cfg(cfg,wlan_cfg_param):
    test_cfgs = []

    ras_cfg = cfg['ras_cfg']  
    ras_acct_cfg = cfg['ras_acct_cfg']

    target_ip_addr = cfg['target_ping_ip_addr']
    radio_mode = cfg['radio_mode']

    shared_secret = cfg['ras_cfg']['radius_auth_secret']   

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode

    rad_user = cfg['rad_user']

    browser_tag = 'browser%s' % radio_mode
   
    target_url = cfg['target_url']
    guest_name = 'Radius_Acct_Guest'
    use_guestpass_auth= True
    use_tou = False
    redirect_url = ''
    restricted_subnet_list = cfg['restricted_subnet_list']
    wlan_cfg = _define_wlan_cfg_guestpass(ras_acct_cfg['server_name'],  wlan_cfg_param[0], wlan_cfg_param[1], 
                                        wlan_cfg_param[2], wlan_cfg_param[3], wlan_cfg_param[4], 
                                        wlan_cfg_param[5], wlan_cfg_param[6], wlan_cfg_param[7])
                                        
    cfg_dict = dict(sta_tag = sta_tag,rad_user = cfg['rad_user'],sta_radio_mode = sta_radio_mode,
                    ap_tag = ap_tag,wlan_cfg = wlan_cfg,target_ping_ip_addr = target_ip_addr,
                    shared_secret = shared_secret,browser_tag = browser_tag,target_url = target_url,
                    guest_name = guest_name,use_guestpass_auth=use_guestpass_auth,
                    use_tou= use_tou,redirect_url = redirect_url)
                       
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
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

    test_name = 'CB_ZD_Restart_Service'
    common_name = 'Restart radius server'
    test_cfgs.append(({'service':'radiusd'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = 'Set the guest access policy'
    test_params = {'use_guestpass_auth': use_guestpass_auth,
                   'use_tou': use_tou,
                   'redirect_url': redirect_url}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_Guest_Restricted_Subnet_Access'
    common_name = 'Remove all restrict subnet records'
    test_params = {'restricted_subnet_list': []}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

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
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create WLAN on ZD'
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                      }, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = 'Generate a guest pass automatically' 
    test_params = {'username': rad_user, 
                   'password': rad_user,
                   'auth_ser': ras_cfg['server_name'], 
                   'wlan': wlan_cfg['ssid'],
                   'guest_fullname': guest_name}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = 'Associate the station to the WLAN'
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = 'Get WiFi address of the station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = 'Verify client information Unauthorized status in ZD'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = 'Verify station pinging to the server fails'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'disallowed',
                       'target': cfg['target_ping_ip_addr']}, test_name, common_name, 0, False))
    
     
#    disconnect_event = 'User[%s] disconnected by admin from WLAN[%s] at AP[%s]'%(rad_user,wlan_cfg['ssid'],cfg['active_ap_mac'])
                       
#testcase 1


    test_case_name = '[Calling_Station_Id]' 
    choice = 'by_sta_mac'
    is_negative = False
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))


#testcase 2    
                       
    test_case_name = '[User_Name]' 
    choice = 'by_user_name'
    is_negative = False
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))       
#testcase 3
    test_case_name = '[Acct_Session_Id]' 
    choice = 'by_session_id'
    is_negative = False
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))                      

#testcase 4
    test_case_name = '[Invalid_Calling_Station_Id]' 
    choice = 'by_invalid_sta_mac'
    is_negative = True
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))

#testcase 5
                       
    test_case_name = '[Invalid_User_Name]' 
    choice = 'by_invalid_user_name'
    is_negative = True
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))    

#testcase 6
    test_case_name = '[Invalid_Acct_Session_Id]' 
    choice = 'by_invalid_session_id'
    is_negative = True
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))                             

#clean_up                       
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_GuestPassGen_Select_Auth_Server'
    common_name = 'Select authentication server to original value'
    test_cfgs.append(({'guestpassgen_auth_serv':'Local Database'}, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_Set_Guest_Restricted_Subnet_Access'
    common_name = 'Recover all restrict subnet records for the next test'
    test_params = {'restricted_subnet_list': restricted_subnet_list}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Restart_Service'
    common_name = 'Restart radius server for the next test'
    test_cfgs.append(({'service':'radiusd'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station for the next test'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station for the next test'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))
    
    return test_cfgs

def test_process(test_case_name,choice,is_negative,cfg_dict):

    sta_tag = cfg_dict['sta_tag']
    browser_tag = cfg_dict['browser_tag']
    rad_user = cfg_dict['rad_user']
    sta_radio_mode = cfg_dict['sta_radio_mode']
    ap_tag = cfg_dict['ap_tag']
    wlan_cfg = cfg_dict['wlan_cfg']
    target_ping_ip_addr = cfg_dict['target_ping_ip_addr']
    shared_secret = cfg_dict['shared_secret']
    target_url = cfg_dict['target_url']
    guest_name = cfg_dict['guest_name']
    use_guestpass_auth= cfg_dict['use_guestpass_auth']
    use_tou = cfg_dict['use_tou']
    redirect_url = cfg_dict['redirect_url']

    if is_negative:
        condition = 'allowed'
        status = 'Authorized'
    else:
        condition = 'disallowed'
        status = 'Unauthorized'	

    tcs_cfgs = []
    exec_level = 1
    if choice == 'by_session_id':
        test_name = 'CB_ZD_Start_Radius_Server_Nohup'
        common_name = '%sStart radius server in the background by nohup option'% (test_case_name)
        tcs_cfgs.append(({}, test_name, common_name, exec_level, False))
        exec_level = 2
    
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%sPerform guest authentication in station" % (test_case_name)
    test_params = {'sta_tag': sta_tag, 
                   'browser_tag': browser_tag,
                   'use_tou': use_tou, 
                   'redirect_url': redirect_url,
                   'target_url': target_url,
                   'no_auth': not use_guestpass_auth}
    tcs_cfgs.append((test_params, test_name, common_name, exec_level, False))
                       
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'guest_name': guest_name,
                       'use_guestpass_auth': use_guestpass_auth,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify station pings to the server successfully'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ping_ip_addr}, test_name, common_name, 2, False))
                       
    if choice == 'by_session_id':     
        test_name = 'CB_Server_Get_Radius_Accounting_Parameters'
        common_name = '%sGet radius accounting parameters from the server'% (test_case_name)
        tcs_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sRemove all the events from ZD'% (test_case_name)
    tcs_cfgs.append(({}, test_name, common_name, 2, False))
      
    test_name = 'CB_Server_Send_Disconnect_Message'
    common_name = '%sSend message and check the output' % (test_case_name)
    tcs_cfgs.append(({
                   'shared_secret':shared_secret,
                   'choice':choice,
                   'sta_tag': sta_tag,
                   'user_name':guest_name,
                   'is_negative':is_negative}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client status on zd'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': status,
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'guest_name': guest_name,
                       'use_guestpass_auth': use_guestpass_auth,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Check_Event_Disconnect_Message'
    common_name = '%sCheck the disconnect event on ZD'% (test_case_name)
    tcs_cfgs.append(({'event':'MSG_client_del_by_admin','user':guest_name,'wlan':wlan_cfg['ssid'],
                      'is_negative':is_negative}, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify station ping to the server'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'condition': condition,
                       'target': target_ping_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN'% (test_case_name)
    tcs_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
                       
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Unauthorized status in ZD'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, True))                       
    return tcs_cfgs

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

    active_ap = active_ap_list[0]

    server_ip_addr  = testsuite.getTestbedServerIp(tbcfg)
    target_ping_ip_addr = '172.16.10.252'
    expected_subnet = utils.get_network_address(server_ip_addr, expected_sub_mask)

    ras_name = 'radius-%s' % (time.strftime("%H%M%S"),)
    ras_acct_name = 'radius-acct-%s' % (time.strftime("%H%M%S"),)

    tcfg = {'ras_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1812',
                    'server_name' : ras_name,
                    'radius_auth_secret': '1234567890',
                    'radius_auth_method': 'chap',
                    'secondary_server_addr':'192.168.0.152',
                    'secondary_server_port':'1812',
                    'secondary_radius_auth_secret':'1234567890',
                    },
            'ras_acct_cfg': {'server_addr': server_ip_addr,
                    'server_port' : '1813',
                    'server_name' : ras_acct_name,
                    'radius_acct_secret': '1234567890',
                    'secondary_server_addr':'192.168.0.152',
                    'secondary_server_port':'1813',
                    'secondary_acct_secret':'1234567890',
                    },
            'rad_user': 'ras.eap.user',
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_url': 'http://172.16.10.252/',
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            'restricted_subnet_list':[r'10.0.0.0/8',r'172.16.0.0/12',r'192.168.0.0/16']
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
        ts_name = "Radius Enhancemen DM - Guest_Access"

    ts = testsuite.get_testsuite(ts_name, "Radius Enhancemen DM - Guest_Access" , combotest=True)

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
