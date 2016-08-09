"""
Verify Radius enhancement disconnect message with WLAN type Hotspot
    
    Verify disconnect messages with different attributes:
        a. Calling_Station_Id: the client's mac address 
        b. User_Name: the client's username
        c. Acct_Session_Id: the client's accounting session id

    expect result: All steps should result properly.
    
    How to:
	Preparation:

	01) Remove all the WLANs from ZD
	02) Remove all Hotspot Profiles from ZD
	03) Remove all AAA servers from ZD
	04) Create Radius authentication server
	05) Create Radius Accounting server
	06) Create target station
	07) Remove all WlANs from station
	08) Delete station mac as user_name and password in radius server
	09) Config All APs Radio - Disable WLAN Service
	10) Create active AP
	11) Config active AP Radio ng - Enable WLAN Service

	Test Process:

	01) Create a Hotspot profile
        02) Create WLAN on ZD
        03) Add station mac as user_name and password in radius server
	04) Associate the station to the WLAN
	05) Get WiFi address of the station
	06) Verify client information authorized status in ZD
	07) Verify station pings to the server successfully
	08) Remove all the events from ZD
	09) Send message and check the output
	10) Check the disconnect event on ZD
        11) Remove all WlANs from station,phrase 1
        12) Associate the station to the WLAN again
        13) Get WiFi address of the station again
        14) Remove all active clients from ZD again
        15) Verify client information Authorized status in ZD 
        16) Verify station pings to the server successfully again
        17) Remove all the events from ZD again
        18) Send message and check the output again
        19) Check the disconnect event on ZD again
        20) Delete station mac as user_name and password in radius server
        21) Remove all WlANs from station,phrase 2
        22) Remove all the WLANs from ZD
        23) Remove all Hotspot Profiles from ZD

	Clean up:

	01) Remove all the WLANs from ZD for the next test
	02) Remove all Hotspot Profiles from ZD for the next test
	03) Remove all AAA servers from ZD for the next test
	04) Restart radius server for the next test
	05) Config All APs Radio - Enable WLAN Service
	06) Remove all WlANs from station for the next test

    
Created on 2013-06
@author: chen.tao@odc-ruckuswireless.com
"""

import sys
import time
import random
import copy
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils


#@author: Tanshixiong @since 2015-04-21 zf-12546
def _define_wlan_cfg_hotspot(hs_name='',auth='open', wpa_ver = '', encryption = 'none', 
                             key_index = '1', key_string = '',sta_auth = '', sta_wpa_ver = '', sta_encryption = '',mac_addr_format = '',):
    wlan_cfg = dict(auth = auth,wpa_ver = wpa_ver,encryption = encryption,key_index = key_index,
                    key_string = key_string,sta_auth = sta_auth,
                    sta_wpa_ver = sta_wpa_ver,sta_encryption = sta_encryption,mac_addr_format = mac_addr_format)
    wlan_cfg['ssid'] = 'Radius_Enhancement_DM_HS_MAC'
    wlan_cfg['type'] = 'hotspot'
    wlan_cfg['hotspot_profile'] = hs_name
	
    return wlan_cfg

def define_test_cfg(cfg,wlan_cfg_param):

    test_cfgs = []

    hotspot_cfg = cfg['hotspot_cfg']  
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
    
    mac_bypass_password = 'ras.123.bypass'
   
###the config to build each testcase
#@author:yuyanan @since:2014-7-31 optimize:get ap mac from active_ap_tag
#@author: chen.tao since 2014-09-29, do not care station dis-associates from which AP
#do not write down ZD IP here, get it dynamically from tb components
    cfg_dict = dict(sta_tag = sta_tag,sta_radio_mode = sta_radio_mode,hs_cfg = hotspot_cfg,
                    ap_tag = ap_tag,target_ping_ip_addr = target_ip_addr,
                    shared_secret = shared_secret,wlan_cfg_param=wlan_cfg_param)

###			        
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

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    del_user = [(sta_tag,sta_tag,True,None),(sta_tag,sta_tag,True,'dot1'),
                (sta_tag,mac_bypass_password,True,None),(sta_tag,mac_bypass_password,True,'dot1')]
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = 'Delete station mac as user_name and password in radius server'
    test_cfgs.append(({'del_user': del_user}, test_name, common_name, 2, True))
        
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

#'enable_mac_auth':'',
#'mac_bypass_password':'',
#'mac_bypass_format':'',

#testcase 1

    test_case_name = '[MAC_AS_Username_And_Password_default_format]' 
    cfg_dict1 = copy.deepcopy(cfg_dict)
    cfg_dict1['hs_cfg']['enable_mac_auth'] = True
    cfg_dict1['hs_cfg']['mac_bypass_format'] = None
    cfg_dict1['hs_cfg']['mac_bypass_password'] = None
    cfg_dict1['choice'] = 'by_user_name'
    cfg_dict1['dot1'] = False
    add_user = [(sta_tag,sta_tag,True,None)]
    #@author: Tanshixiong @since 2015-04-21 zf-12546
    length= len(cfg_dict1['wlan_cfg_param'])
    cfg_dict1['lct'] = []
    i = 0
    while i < length:
        cfg_dict1['lct'].append(cfg_dict1['wlan_cfg_param'][i])
        i = i + 1
    mac_addr_format = ''
    cfg_dict1['lct'].append(mac_addr_format)
    test_cfgs.extend(test_process(test_case_name,cfg_dict1,add_user))

#testcase 2    

    test_case_name = '[MAC_AS_Username_And_Password_802.1x_format]' 
    cfg_dict2 = copy.deepcopy(cfg_dict)
    cfg_dict2['hs_cfg']['enable_mac_auth'] = True
    cfg_dict2['hs_cfg']['mac_bypass_format'] = True
    cfg_dict2['hs_cfg']['mac_bypass_password'] = None
    cfg_dict2['choice'] = 'by_user_name_dot1'
    cfg_dict2['dot1'] = True
    add_user = [(sta_tag,sta_tag,True,'dot1')]
    #@author: Tanshixiong @since 2015-04-21 zf-12546
    length= len(cfg_dict2['wlan_cfg_param'])
    cfg_dict2['lct'] = []
    i = 0
    while i < length:
        cfg_dict2['lct'].append(cfg_dict2['wlan_cfg_param'][i])
        i = i + 1
    mac_addr_format='AA-BB-CC-DD-EE-FF'
    cfg_dict2['lct'].append(mac_addr_format)    
    test_cfgs.extend(test_process(test_case_name,cfg_dict2,add_user))    
    	

#testcase 3

    test_case_name = '[MAC_AS_Username_802.1x_format]'
    cfg_dict3 = copy.deepcopy(cfg_dict)
    cfg_dict3['hs_cfg']['enable_mac_auth'] = True
    cfg_dict3['hs_cfg']['mac_bypass_format'] = True
    cfg_dict3['hs_cfg']['mac_bypass_password'] = mac_bypass_password
    cfg_dict3['choice'] = 'by_user_name_dot1'
    cfg_dict3['dot1'] = True
    add_user = [(sta_tag,mac_bypass_password,True,'dot1')]	
    #@author: Tanshixiong @since 2015-04-21 zf-12546
    length= len(cfg_dict3['wlan_cfg_param'])
    cfg_dict3['lct'] = []
    i = 0
    while i < length:
        cfg_dict3['lct'].append(cfg_dict3['wlan_cfg_param'][i])
        i = i + 1
    mac_addr_format='AA-BB-CC-DD-EE-FF'
    cfg_dict3['lct'].append(mac_addr_format)    
    test_cfgs.extend(test_process(test_case_name,cfg_dict3,add_user))

#testcase 4    

    test_case_name = '[MAC_AS_Username_default_format]' 
    cfg_dict4 = copy.deepcopy(cfg_dict)
    cfg_dict4['hs_cfg']['enable_mac_auth'] = True
    cfg_dict4['hs_cfg']['mac_bypass_format'] = None
    cfg_dict4['hs_cfg']['mac_bypass_password'] = mac_bypass_password
    cfg_dict4['choice'] = 'by_user_name'
    cfg_dict4['dot1'] = False
    add_user = [(sta_tag,mac_bypass_password,True,None)]
    #@author: Tanshixiong @since 2015-04-21 zf-12546	
    length= len(cfg_dict4['wlan_cfg_param'])
    cfg_dict4['lct'] = []
    i = 0
    while i < length:
        cfg_dict4['lct'].append(cfg_dict3['wlan_cfg_param'][i])
        i = i + 1
    mac_addr_format=''
    cfg_dict4['lct'].append(mac_addr_format)  
    test_cfgs.extend(test_process(test_case_name,cfg_dict4,add_user))     

#clean_up                       
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

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

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station for the next test'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))
    
    return test_cfgs

def test_process(test_case_name,cfg_dict,add_user):
    tcs_cfgs=[]

    hs_cfg = cfg_dict['hs_cfg']

    sta_tag = cfg_dict['sta_tag']
    sta_radio_mode = cfg_dict['sta_radio_mode']
    ap_tag = cfg_dict['ap_tag']
    target_ping_ip_addr = cfg_dict['target_ping_ip_addr']
    shared_secret = cfg_dict['shared_secret']
    #@author: Tanshixiong @since 2015-04-21 zf-12546
    wlan_cfg_param = cfg_dict['lct']
    choice = cfg_dict['choice']
    dot1 = cfg_dict['dot1']
    wlan_cfg = _define_wlan_cfg_hotspot(hs_cfg['name'],wlan_cfg_param[0], wlan_cfg_param[1], 
                                        wlan_cfg_param[2], wlan_cfg_param[3], wlan_cfg_param[4], 
                                        wlan_cfg_param[5], wlan_cfg_param[6], wlan_cfg_param[7],wlan_cfg_param[8])  
   
    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = '%sCreate a Hotspot profile'% (test_case_name)
    tcs_cfgs.append(({'hotspot_profiles_list':[hs_cfg]}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate WLAN on ZD'% (test_case_name)
    tcs_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                      }, test_name, common_name, 2, False))

    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '%sAdd station mac as user_name and password in radius server'% (test_case_name)
    tcs_cfgs.append(({'add_user': add_user}, test_name, common_name, 2, False))                      
        
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN'% (test_case_name)
    tcs_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

#    test_name = 'CB_ZD_Remove_All_Active_Clients'
#    common_name = '%s Remove all active clients from ZD' % (test_case_name)
#    tcs_cfgs.append(({}, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD' % (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username':'mac.bypass',},
                       test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify station pings to the server successfully'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ping_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sRemove all the events from ZD'% (test_case_name)
    tcs_cfgs.append(({}, test_name, common_name, 2, False))
       
    test_name = 'CB_Server_Send_Disconnect_Message'
    common_name = '%sSend message and check the output' % (test_case_name)
    tcs_cfgs.append(({
                   'shared_secret':shared_secret,
                   'choice':'by_sta_mac',
                   'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Check_Event_Disconnect_Message'
    common_name = '%sCheck the disconnect event on ZD'% (test_case_name)
    tcs_cfgs.append(({'event':'MSG_client_del_by_admin','sta_tag': sta_tag,'wlan':wlan_cfg['ssid'],
                      'dot1':dot1,}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station,phrase 1'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot' 
    common_name = '%sreboot zd' % (test_case_name)
    tcs_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN again'% (test_case_name)
    tcs_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station again'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

#    test_name = 'CB_ZD_Remove_All_Active_Clients'
#    common_name = '%s Remove all active clients from ZD again' % (test_case_name)
#    tcs_cfgs.append(({}, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD again' % (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username':'mac.bypass',},
                       test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify station pings to the server successfully again'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target':target_ping_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sRemove all the events from ZD again'% (test_case_name)
    tcs_cfgs.append(({}, test_name, common_name, 2, False))
       
    test_name = 'CB_Server_Send_Disconnect_Message'
    common_name = '%sSend message and check the output again' % (test_case_name)
    tcs_cfgs.append(({
                   'shared_secret':shared_secret,
                   'choice':choice,
                   'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Check_Event_Disconnect_Message'
    common_name = '%sCheck the disconnect event on ZD again'% (test_case_name)
    tcs_cfgs.append(({'event':'MSG_client_del_by_admin','sta_tag': sta_tag,'wlan':wlan_cfg['ssid'],
                      'dot1':dot1}, test_name, common_name, 2, False))
                       
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '%sDelete station mac as user_name and password in radius server'% (test_case_name)
    tcs_cfgs.append(({'del_user': add_user}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station,phrase 2'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs from ZD'% (test_case_name)
    tcs_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = '%sRemove all Hotspot Profiles from ZD'% (test_case_name)
    tcs_cfgs.append(({}, test_name, common_name, 2, True))
    
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
    target_ping_ip_addr = server_ip_addr
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
            'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                            'name': 'hs_radius_acct',
                            'auth_svr': ras_name,
                            'acct_svr': ras_acct_name,
                            'idle_timeout': None,
                            },
            'target_ping_ip_addr': target_ping_ip_addr,
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
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
        ts_name = "Radius Enhancemen DM - Hotspot - MAC"

    ts = testsuite.get_testsuite(ts_name, "Radius Enhancemen DM - Hotspot - MAC" , combotest=True)

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
