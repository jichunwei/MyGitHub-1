"""
Verify Radius enhancement disconnect message with WLAN type WISPr
    
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
	05) Create target station
	06) Remove all WlANs from station
	07) Config All APs Radio - Disable WLAN Service
	08) Create active AP
	09) Config active AP Radio ng - Enable WLAN Service
	10) Create WLAN on ZD


	Test Process:

        Repeat test process to test valid/invalid Calling_Station_Id/User_Name/Acct_Session_Id

	01) Associate the station to the WLAN
	02) Get WiFi address of the station
	03) Verify client information authorized status in ZD
	04) Verify station pings to the server successfully
	05) Remove all the events from ZD
	06) Send message and check the output
	07) Check the disconnect event on ZD
	08) Remove all WlANs from station


	Clean up:

	01) Remove all the WLANs from ZD for the next test
	02) Remove all AAA servers from ZD for the next test
	03) Restart radius server for the next test
	04) Config All APs Radio - Enable WLAN Service
	05) Remove all WlANs from station for the next test

    
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

def _define_wlan_cfg(auth_svr = '', acct_svr = '',rad_user='',auth='EAP', wpa_ver = 'WPA', encryption = 'TKIP', 
                     sta_auth = 'EAP', sta_wpa_ver = 'WPA', sta_encryption = 'TKIP',):
    wlan_cfg = dict(auth = auth,wpa_ver = wpa_ver,encryption = encryption,sta_auth = sta_auth,
                    sta_wpa_ver = sta_wpa_ver,sta_encryption = sta_encryption)
    wlan_cfg['ssid'] = 'Radius_Enhancement_DM_EAP'
    wlan_cfg['type'] = 'standard'
    wlan_cfg['auth_svr'] = auth_svr
    wlan_cfg['acct_svr'] = acct_svr
   
    wlan_cfg['username'] = rad_user
    wlan_cfg['password'] = rad_user
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

    rad_user = cfg['rad_user']

    
    wlan_cfg = _define_wlan_cfg(ras_cfg['server_name'],ras_acct_cfg['server_name'], rad_user, wlan_cfg_param[0], 
                                wlan_cfg_param[1],wlan_cfg_param[2], wlan_cfg_param[3], wlan_cfg_param[4], 
                                wlan_cfg_param[5]) 


###the config to build each testcase
#@author:yuyanan @since:2014-7-31 optimize:get ap mac from get active_ap_tag
#@author: chen.tao since 2014-09-29, do not care station dis-associates from which AP
#do not write down ZD IP here, get it dynamically from tb components
    cfg_dict = dict(sta_tag = sta_tag,rad_user = cfg['rad_user'],sta_radio_mode = sta_radio_mode,
                    ap_tag = ap_tag,wlan_cfg = wlan_cfg,target_ping_ip_addr = target_ip_addr,
                    shared_secret = shared_secret)
###
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
    test_case_name = '[Invalid_Calling_Station_Id]' 
    choice = 'by_invalid_sta_mac'
    is_negative = True
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))

#testcase 4                       
    test_case_name = '[Invalid_User_Name]' 
    choice = 'by_invalid_user_name'
    is_negative = True
    test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))                    
                       
#clean_up                       
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Restart_Service'
    common_name = 'Restart radius server'
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

def test_process(test_case_name,choice,is_negative,cfg_dict):

    sta_tag = cfg_dict['sta_tag']
    rad_user = cfg_dict['rad_user']
    sta_radio_mode = cfg_dict['sta_radio_mode']
    ap_tag = cfg_dict['ap_tag']
    wlan_cfg = cfg_dict['wlan_cfg']
    target_ping_ip_addr = cfg_dict['target_ping_ip_addr']
    shared_secret = cfg_dict['shared_secret']

    tcs_cfgs = []

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the WLAN'% (test_case_name)
    tcs_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of the station'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information Authorized status in ZD'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': rad_user,},
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
                   'choice':choice,
                   'sta_tag': sta_tag,
                   'user_name':rad_user,
                   'is_negative':is_negative}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Check_Event_Disconnect_Message'
    common_name = '%sCheck the disconnect event on ZD'% (test_case_name)
    tcs_cfgs.append(({'event':'MSG_client_del_by_admin','user':rad_user,'wlan':wlan_cfg['ssid'],
                      'is_negative':is_negative}, test_name, common_name, 2, False))
                                 
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all WlANs from station'% (test_case_name)
    tcs_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
  
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
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': expected_subnet,
            }
 
    #######<auth>  <wpa_ver> <encryption> <sta_auth> <sta_wpa_ver> <sta_encryption>###### 
    list = [('EAP', 'WPA', 'TKIP','EAP', 'WPA', 'TKIP'),#1
           ('EAP', 'WPA', 'AES','EAP', 'WPA', 'AES'), #2
           ('EAP', 'WPA', 'Auto','EAP', 'WPA', 'TKIP'), #3
           ('EAP', 'WPA', 'Auto','EAP', 'WPA', 'AES'), #4
           ('EAP', 'WPA2', 'TKIP','EAP', 'WPA2', 'TKIP'),#5
           ('EAP', 'WPA2', 'AES','EAP', 'WPA2', 'AES'),#6
           ('EAP', 'WPA2', 'Auto','EAP', 'WPA2', 'TKIP'), #7
           ('EAP', 'WPA2', 'Auto','EAP', 'WPA2', 'AES'), #8
           ('EAP', 'WPA_Mixed', 'TKIP','EAP', 'WPA', 'TKIP'),  #9
           ('EAP', 'WPA_Mixed', 'TKIP','EAP', 'WPA2', 'TKIP'),  #10
           ('EAP', 'WPA_Mixed', 'AES','EAP', 'WPA', 'AES'),  #11
           ('EAP', 'WPA_Mixed', 'AES','EAP', 'WPA2', 'AES'),  #12
           ('EAP', 'WPA_Mixed', 'Auto','EAP', 'WPA', 'TKIP'), #13
           ('EAP', 'WPA_Mixed', 'Auto','EAP', 'WPA', 'AES'), #14
           ('EAP', 'WPA_Mixed', 'Auto','EAP', 'WPA2', 'TKIP'), #15
           ('EAP', 'WPA_Mixed', 'Auto','EAP', 'WPA2', 'AES'), #16
           ('EAP', '', 'WEP-64', 'EAP', '', 'WEP-64'),#17
           ('EAP', '', 'WEP-128','EAP', '', 'WEP-128'),#18
            ]

    select_option = raw_input("\n\
    1.  WPA+TKIP\n\
    2.  WPA+AES\n\
    3.  WPA+AUTO,       station WPA+TKIP\n\
    4.  WPA+AUTO,       station WPA+AES\n\
    5.  WPA2+TKIP\n\
    6.  WPA2+AES\n\
    7.  WPA2+AUTO,      station WPA2+TKIP\n\
    8.  WPA2+AUTO,      station WPA2+AES\n\
    9. WPA_Mixed+TKIP, station WPA+TKIP\n\
    10. WPA_Mixed+TKIP, station WPA2+TKIP\n\
    11. WPA_Mixed+AES,  station WPA+AES\n\
    12. WPA_Mixed+AES,  station WPA2+AES\n\
    13. WPA_Mixed+AUTO, station WPA+TKIP\n\
    14. WPA_Mixed+AUTO, station WPA+AES\n\
    15. WPA_Mixed+AUTO, station WPA2+TKIP\n\
    16. WPA_Mixed+AUTO, station WPA2+AES\n\
    17. WEP-64\n\
    18. WEP-128\n\n\
    Select encryption type of Autonomous WLAN[1-18, default is 1 <WPA+TKIP>]: ")
    
    
    
    if not select_option or int(select_option) not in range(1,20):
        select_option = 1      
          
    test_cfgs = define_test_cfg(tcfg, list[int(select_option)-1])   

    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Radius Enhancemen DM - Standard - EAP"

    ts = testsuite.get_testsuite(ts_name, "Radius Enhancemen DM - Standard - EAP" , combotest=True)

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
