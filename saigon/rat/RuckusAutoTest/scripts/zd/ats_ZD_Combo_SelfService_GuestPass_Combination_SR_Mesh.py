"""
Verify self-service guest pass combination function.

    Pre-condition:
       AP1 AP2 joins ZD1
       support SR + Mesh
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) enable SR
        2) enable mesh
        3) create active ap is mesh ap
        4) case1:[different wlan with same email]
        5) case2:[same wlan with same email]
        6) case3:[wlan with another key]
        7) case4:[change wlan encryption]
        8) case5:[change wlan with gs2]
        9) case6:[change wlan with newname]
        10)case7:[change wlan type]
        11)case8:[guestpass statistics]
        12)case9:[access duration with first use]
        13)case10:[access duration with create time]
        14)case11:[default max device]
        15)case12:[max guest service reconnect client]
        16)case13:[self service fail over]
        17)case14:[max guest pass]
        18)enable sw port connected to mesh ap
        19)disable sr via CLI on zd1
        20)disable sr via CLI on zd2
        21)make sure all ap connect active ap
        
    ps:
    
Created on 2015-2-9
@author: Yu.yanan@odc-ruckuswireless.com
"""

import sys
from random import randint
import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from copy import deepcopy

def define_test_cfg(cfg):
 
   
    test_cfgs = [] 
    idx = 0
    
    sta_tag_1 = "sta_1"
    sta_tag_2 = "sta_2"
    
    mesh_ap_tag = cfg['mesh_ap_tag']
   
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target sta_1'
    test_cfgs.append(({'sta_ip_addr':cfg['target_sta_1'],'sta_tag': sta_tag_1}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target sta_2'
    test_cfgs.append(({'sta_ip_addr':cfg['target_sta_2'],'sta_tag': sta_tag_2}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from sta_1'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from sta_2'
    test_cfgs.append(({'sta_tag': 'sta_2'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD and disable switch port connectet to %s,let it become mesh ap'% mesh_ap_tag
    test_cfgs.append(({'mesh_ap_list':[mesh_ap_tag],
                       'for_upgrade_test':False},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active mesh AP' 
    test_cfgs.append(({'active_ap': mesh_ap_tag,'ap_tag': mesh_ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Disable All WLAN Service'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
     
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable Active AP WLAN Service'
    test_cfgs.append(({'ap_tag': mesh_ap_tag, 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True, 'radio': cfg['active_radio']}}, test_name, common_name, 0, False))
 
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Remove all GuestService from ZDCLI'
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 0, False))
    
    guest_access_conf_1 = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_1.update({'name':'guest_service_test_1'})
    wlan_cfg_wlan_1 = deepcopy(cfg['guest_wlan_cfg'])
    wlan_cfg_wlan_1.update({'name':'self_service_guest_wlan_test1','ssid':'self_service_guest_wlan_test1',
                            'guest_name':'guest_service_test_1','guest_access_service':guest_access_conf_1})
    
    test_name = 'CB_ZD_CLI_Create_Wlan' 
    common_name = 'create guest wlan1 with guest_service_1'
    test_cfgs.append(({'wlan_conf':wlan_cfg_wlan_1}, test_name, common_name, 0, False))
    

    guest_access_conf_2 = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_2.update({'name':'guest_service_test_2'})
    wlan_cfg_wlan_2 = deepcopy(cfg['guest_wlan_cfg'])
    wlan_cfg_wlan_2.update({'name':'self_service_guest_wlan_test2','ssid':'self_service_guest_wlan_test2',
                            'guest_name':'guest_service_test_2','guest_access_service':guest_access_conf_2})
    
    test_name = 'CB_ZD_CLI_Create_Wlan' 
    common_name = 'create guest wlan2 with guest_service_2'
    test_cfgs.append(({'wlan_conf':wlan_cfg_wlan_2}, test_name, common_name, 0, False))
    
    param_test =[ {sta_tag_1:['WLAN1',wlan_cfg_wlan_1,'Authorized','allowed','can ping',True,1]},
                  {sta_tag_2:['WLAN2',wlan_cfg_wlan_2,'Unauthorized','disallowed','can not ping',False,2]}
                ]
    #****************************************case (1)  ***************************************************
    idx +=1
    step = 0
    tc_common_name = "different wlan with same email"
    
    for sta_info in param_test:
        
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s %s Associate client to %s' % (tc_common_name,idx, step, sta_info.keys()[0],sta_info.values()[0][0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'wlan_cfg': sta_info.values()[0][1]}, test_name, common_name, sta_info.values()[0][6], False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s %s get client wifi address' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, False))
    
    
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key with same email' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag':sta_info.keys()[0]}, test_name, common_name, 2, False))
    

        test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
        step += 1
        common_name = '[%s]%s.%s %s perform authorize with key' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag':sta_info.keys()[0]} , test_name, common_name, 2, False))
 
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        step += 1
        common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': sta_info.values()[0][1],'status': 'Authorized'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        step += 1
        common_name = '[%s]%s.%s verify %s can ping target ip' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from %s '% (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from %s '% (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, True))
    
    
    #****************************************case (2)  ***************************************************
 
    idx +=1
    step = 0
    tc_common_name = "same wlan with same email"
    num = 0
     
    for sta_info in param_test:
        
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s %s Associate client to WLAN1' % (tc_common_name,idx, step, sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'wlan_cfg':wlan_cfg_wlan_1}, test_name, common_name, sta_info.values()[0][6], False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s %s get client wifi address' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, False))
    
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key with same email' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag':sta_info.keys()[0],'condition_allow':sta_info.values()[0][5]}, test_name, common_name, 2, False))
        
        if num == 0:
            num += 1
            test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
            step += 1
            common_name = '[%s]%s.%s %s perform authorize with key' % (tc_common_name, idx, step,sta_info.keys()[0])
            test_cfgs.append(({'sta_tag':sta_info.keys()[0],'condition_allow':False}, test_name, common_name, 2, False))

            test_name = 'CB_ZD_Verify_Station_Info_V2'
            step += 1
            common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_info.keys()[0])
            test_cfgs.append(({'sta_tag': sta_info.keys()[0],'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': sta_info.values()[0][1],'status': sta_info.values()[0][2]}, test_name, common_name, 2, False))
    
            test_name = 'CB_ZD_Client_Ping_Dest'
            step += 1
            common_name = '[%s]%s.%s verify %s %s target ip' % (tc_common_name, idx, step,sta_info.keys()[0],sta_info.values()[0][4])
            test_cfgs.append(({'sta_tag': sta_info.keys()[0],'target': '172.16.10.252', 'condition': sta_info.values()[0][3]}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from %s '% (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from %s '% (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, True))
    
        
    #*************************************(3)*********************************************************************
    idx +=1
    step = 0
    tc_common_name = "wlan with another key"
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s %s associate to WLAN2' % (tc_common_name,idx, step, sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2,'wlan_cfg': wlan_cfg_wlan_2}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s %s get client wifi address' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s %s generate key2  ' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(( {'sta_tag':sta_tag_2,}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s %s Associate client to WLAN1' % (tc_common_name,idx, step, sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2,'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s %s get client wifi address' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, False))
    
  
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s %s perform authorize with key2' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag':sta_tag_2,'condition_allow':False}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2,'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': wlan_cfg_wlan_1,'status':'Unauthorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify %s can not ping target ip' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2,'target': '172.16.10.252', 'condition': 'disallowed'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, True))
    
 
    #************************(4)**(5)**(6)********************************************************************************
    
    
    guest_wlan_cfg_encryption = deepcopy(wlan_cfg_wlan_1)
    guest_wlan_cfg_encryption.update({'tunnel_mode':True,
                                      'encryption': 'AES',
                                      'sta_encryption': 'AES', 
                                      'sta_auth': 'PSK',
                                      'key_index': '', 
                                      'auth': 'PSK', 
                                      'sta_wpa_ver': 'WPA2',
                                      'key_string': 'ae04e3d049f476dbc7c3a110a54caa1fd3', 
                                      'wpa_ver': 'WPA2'})
    
    guest_wlan_cfg_gs2 = deepcopy(wlan_cfg_wlan_1)
    guest_wlan_cfg_gs2.update({'name':'self_service_guest_wlan_test1','ssid':'self_service_guest_wlan_test1','guest_name':'guest_service_test_2','guest_access_service':guest_access_conf_2})
    
    guest_wlan_cfg_updatename = deepcopy(wlan_cfg_wlan_1)
    guest_wlan_cfg_updatename.update({'name':'self_service_guest_wlan_test1','newname':'self_service_guest_wlan_newname',})
    
    guest_wlan_cfg_restorename = deepcopy(wlan_cfg_wlan_1)
    guest_wlan_cfg_restorename.update({'name':'self_service_guest_wlan_newname','newname':'self_service_guest_wlan_test1'})
    
    guest_wlan_cfg_updatename_verify = deepcopy(wlan_cfg_wlan_1)
    guest_wlan_cfg_updatename_verify.update({'ssid':'self_service_guest_wlan_newname',})
    
    param_case5 = {'change wlan encryption':[guest_wlan_cfg_encryption,'Authorized','allowed',True,'can ping',wlan_cfg_wlan_1,wlan_cfg_wlan_1],
                   'change wlan with guest_service_2':[guest_wlan_cfg_gs2,'Unauthorized','disallowed',False,'can not ping',wlan_cfg_wlan_1,wlan_cfg_wlan_1],
                   'change wlan name':[guest_wlan_cfg_updatename,'Unauthorized','disallowed',False,'can not ping',guest_wlan_cfg_updatename_verify,guest_wlan_cfg_restorename]}

    for key,value in param_case5.items():
        idx +=1
        step = 0
        tc_common_name = key
        
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate %s to WLAN1' % (tc_common_name,idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, 1, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
    
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key ' % (tc_common_name, idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag':sta_tag_1,}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_CLI_Create_Wlan'
        step += 1
        common_name = '[%s]%s.%s edit wlan ' % (tc_common_name, idx, step)
        test_cfgs.append(({'wlan_conf':value[0]}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Reassociate %s to WLAN1' % (tc_common_name,idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': value[0]}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
    

        test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
        step += 1
        common_name = '[%s]%s.%s %s perform authorize with key' % (tc_common_name, idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag':sta_tag_1,'condition_allow':value[3]}, test_name, common_name, 2, False))
      
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        step += 1
        common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag': sta_tag_1,'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': value[5],'status': value[1]}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        step += 1
        common_name = '[%s]%s.%s verify %s %s target ip' % (tc_common_name, idx, step,sta_tag_1,value[4])
        test_cfgs.append(({'sta_tag': sta_tag_1, 'condition': value[2]}, test_name, common_name, 2, False))
     
        test_name = 'CB_ZD_CLI_Create_Wlan'
        step += 1
        common_name = '[%s]%s.%s restore wlan ' % (tc_common_name, idx, step)
        test_cfgs.append(({'wlan_conf':value[6]}, test_name, common_name, 2, True))
    
        test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
        step += 1
        common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
        test_cfgs.append(({}, test_name, common_name, 2, True))
    
        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from %s'% (tc_common_name, idx, step,sta_tag_1)
        test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))
    
    #*****************************case (7)  ***************************************************
    
    tc_common_name = "change wlan type"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_CLI_Create_Users'
    step +=1
    common_name = '[%s]%s.%s Create Users' % (tc_common_name,idx, step)
    test_cfgs.append(({'name': 'test.user', 'password': 'test.user', 'number': 1}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg':wlan_cfg_wlan_1 }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key ' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':sta_tag_1,}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s %s perform authorize with key' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
         
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1,'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': wlan_cfg_wlan_1,'status': 'Authorized'}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1, 'condition': 'allowed'}, test_name, common_name, 2, False))       
       
    wlan_cfg_hotspot = deepcopy(wlan_cfg_wlan_1) 
    wlan_cfg_hotspot.update({'auth': 'open',
                             'encryption' :'none',
                             'type':'hotspot', 
                             'hotspot_service': cfg['hotspot_conf']})

    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s edit wlan with hotspot' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':wlan_cfg_hotspot}, test_name, common_name, 2, False)) 

        
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg':wlan_cfg_hotspot }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1,'original_url': 'https://172.16.10.252/', 
                       'username': 'test.user', 'close_browser_after_auth': True, 'password': 'test.user', 'start_browser_before_auth': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','username':'test.user','wlan_cfg': wlan_cfg_hotspot,'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1,'condition': 'allowed'}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_SelfService_GuestPass_Info_On_WebUI'
    step += 1
    common_name = '[%s]%s.%s check selfservice guestpass on zd ' % (tc_common_name, idx, step)
    test_cfgs.append(({'expected_webui_info':{}}, test_name, common_name, 2, False))
      

    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s restore wlan ' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':wlan_cfg_wlan_1}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    step += 1
    common_name = '[%s]%s.%s Remove  hotspot profile from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({'cleanup':True,'hotspot_conf':{'name':'Hotsport_Default'}}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))
        
    test_name = 'CB_ZD_Remove_All_Users'
    step += 1
    common_name = '[%s]%s.%s Remove all local user' % (tc_common_name,idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    #****************************************case(8)***************************************************  
    
    tc_common_name = "guest pass statistics"
    idx +=1
    step = 0
    
    for sta_info in param_test:
        
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate %s to %s' % (tc_common_name,idx, step,sta_info.keys()[0],sta_info.values()[0][0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'wlan_cfg':sta_info.values()[0][1]}, test_name, common_name, sta_info.values()[0][6], False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s  get %s wifi address' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, False))
    
        
        username = 'test_'+sta_info.keys()[0]
        email = username+'@163.com'
      
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key1 ' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''},
                                 'sta_tag':sta_info.keys()[0],}, test_name, common_name, 2, False))
  
        username = 'my_'+sta_info.keys()[0]
        email = username+'@163.com'
        
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key2 ' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''},
                                 'sta_tag':sta_info.keys()[0], }, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Verify_SelfService_GuestPass_Info_On_WebUI'
    step += 1
    common_name = '[%s]%s.%s check selfservice guestpass on zd ' % (tc_common_name, idx, step)
    test_cfgs.append(({'expected_webui_info':{'test_sta_1':['test_sta_1@163.com','self_service_guest_wlan_test1'],
                                              'my_sta_1':['my_sta_1@163.com','self_service_guest_wlan_test1'],
                                              'test_sta_2':['test_sta_2@163.com','self_service_guest_wlan_test2'],
                                              'my_sta_2':['my_sta_2@163.com','self_service_guest_wlan_test2'],     
                                              }}, test_name, common_name, 2, False))
   
    
    wlan_cfg_stand ={ 'name' :'self_service_guest_wlan_test1',
                      'ssid': 'self_service_guest_wlan_test1',
                      'type':'standard-usage', 
                      'auth': 'open',
                      'encryption' :'none',}
                       
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s edit wlan with stand' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':wlan_cfg_stand}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_SelfService_GuestPass_Info_On_WebUI'
    step += 1
    common_name = '[%s]%s.%s check selfservice guestpass on zd ' % (tc_common_name, idx, step)
    test_cfgs.append(({'expected_webui_info': {'test_sta_2':['test_sta_2@163.com','self_service_guest_wlan_test2'],
                                              'my_sta_2':['my_sta_2@163.com','self_service_guest_wlan_test2'],
                                              }}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SelfService_GuestPass_Info_On_WebUI'
    step += 1
    common_name = '[%s]%s.%s check selfservice guestpass on zd ' % (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s restore wlan ' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':wlan_cfg_wlan_1}, test_name, common_name, 2, True)) 
    
    #************************************(9)**********************************************************88
    
    tc_common_name = "access duration with first use"
    idx +=1
    step = 0
    num = 0
    
    param_duration_firstuse = [{sta_tag_1:[True,False,'expired',1]},#is_pass_expired_after_used,first_use
                               {sta_tag_2:[False,True,'valid',2],},
                               ]
    
    for sta_info in param_duration_firstuse:
        
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate %s to WLAN1' % (tc_common_name,idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, sta_info.values()[0][3], False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, False))
        
        username = 'test_'+sta_info.keys()[0]
        email = username+'@163.com'
                   
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key ' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag':sta_info.keys()[0],'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''}}, test_name, common_name, 2, False))

        test_name = 'ZD_GuestAccess_SelfService_GuestPassExpiration'
        step += 1
        common_name = '[%s]%s.%s check %s guestpass %s' % (tc_common_name, idx, step,sta_info.keys()[0],sta_info.values()[0][2])
        test_cfgs.append(({'sta_tag':sta_info.keys()[0],'wlan_cfg': wlan_cfg_wlan_1,'is_pass_expired_after_used':sta_info.values()[0][0],'first_use':sta_info.values()[0][1],
                               'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''}},test_name, common_name, 2, False))  
  
        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, True))
   
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
  
    
    #************************************(10)**********************************************************88
    
    tc_common_name = "access duration with create time"
    idx +=1
    step = 0
    num = 0
    
    guest_access_conf_create_time = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_create_time.update({'name':'guest_service_test_1','validity_period':'Effective from the creation time.'})#Effective from first use.
        
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s edit gs with create time'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':guest_access_conf_create_time}, test_name, common_name, 1, False))

    param_duration_createtime = [{sta_tag_1:[True,False,]},
                               {sta_tag_2:[False,False,]},
                               ]
    
    for sta_info in param_duration_createtime:

        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate %s to WLAN' % (tc_common_name,idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0],'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, False))
        
        username = 'test_'+sta_info.keys()[0]
        email = username+'@163.com'
            
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s %s generate key ' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''},                                
                                 'sta_tag':sta_info.keys()[0],'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''} }, test_name, common_name, 2, False))
            
        test_name = 'ZD_GuestAccess_SelfService_GuestPassExpiration'
        step += 1
        common_name = '[%s]%s.%s check %s guestpass expiration' % (tc_common_name, idx, step,sta_info.keys()[0])
        test_cfgs.append(({'sta_tag':sta_info.keys()[0],'wlan_cfg': wlan_cfg_wlan_1,'is_pass_expired_after_used':sta_info.values()[0][0],'first_use':sta_info.values()[0][1],
                            'user_register_infor':{'username':username,'email':email,'countrycode':'','mobile':''}},test_name, common_name, 2, False)) 
 
        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_info.keys()[0]}, test_name, common_name, 2, True))
        
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    guest_access_conf_first_use = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_first_use.update({'name':'guest_service_test_1','validity_period':'Effective from first use.','expire_days':'7'})
        
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s restore gs with first use'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':guest_access_conf_first_use}, test_name, common_name, 2, True))
    
    
    #*******************************case (11) max device ******************************************************
    
    tc_common_name = "default max device"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate %s to WLAN' % (tc_common_name,idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg':wlan_cfg_wlan_1 }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s %s generate key ' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag':sta_tag_1,}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s %s perform authorize with key' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
         
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': wlan_cfg_wlan_1,'status': 'Authorized'}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify %s can ping target ip' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'condition': 'allowed'}, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate %s to WLAN' % (tc_common_name,idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2,'wlan_cfg':wlan_cfg_wlan_1 }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s access %s perform authorize with key' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2,'use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': wlan_cfg_wlan_1,'status': 'Authorized'}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify %s can ping target ip' % (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag': sta_tag_2, 'condition': 'allowed'}, test_name, common_name, 2, False))  
    
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from %s '% (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag':sta_tag_1 }, test_name, common_name, 2, True))
    
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from %s'% (tc_common_name, idx, step,sta_tag_2)
    test_cfgs.append(({'sta_tag':sta_tag_2 }, test_name, common_name, 2, True))
   
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    
    #*************************************(11)************************************************

    tc_common_name = "max guest service reconnect client"
    idx +=1
    step = 0

    wlans = [dict(ssid = "self_service_guest_wlan_%d" % i, 
                  name= "self_service_guest_wlan_%d" % i,
                  auth = "open", 
                  encryption = "none",
                  type = "guest",
                  guest_name="guest_service_%d"%i,
                  guest_access_service={'name':"guest_service_%d"%i, 
                                        'terms_of_use': 'Disabled',
                                        'self_service_registration':{
                                                                     'status':'Enabled',
                                                                     'duration':'1 days',
                                                                     'share_number':'1',
                                                                     'notification_method':'Device Screen',    
                                                                     'sponsor_approval':{'status':'Disabled'},
                                                                     }
                                        }
                  ) for i in range(1,31)]
             
    test_name = 'CB_ZD_CLI_Create_Wlans' 
    step += 1
    common_name = '[%s]%s.%s create 30 guest wlan with self service '% (tc_common_name,idx, step)
    test_cfgs.append(({'wlan_cfg_list':wlans}, test_name, common_name, 0, False))
    
    for wlan_count in range(2):
        num = randint(1,25)#wlan group only support 27 wlan up status
        wlan_cfg = wlans[num-1]
        
        for reconnect_count in range(3):
            
            if wlan_count == 0 and reconnect_count == 0:#adapt to level
                test_name = 'CB_ZD_Associate_Station_1'
                step += 1
                common_name = '[%s]%s.%s Associate client to WLAN_%s' % (tc_common_name,idx, step,num)
                test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg}, test_name, common_name, 1, False))
            else:
                test_name = 'CB_ZD_Associate_Station_1'
                step += 1
                common_name = '[%s]%s.%s Associate client to WLAN_%s' % (tc_common_name,idx, step,num)
                test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
            test_name = 'CB_Station_Remove_All_Wlans'
            step += 1
            common_name = '[%s]%s.%s Disconnect client to WLAN_%s'% (tc_common_name, idx, step,num)
            test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
    
    
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate client to WLAN_%s' % (tc_common_name,idx, step,num)
        test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
        
        
        test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
        step += 1
        common_name = '[%s]%s.%s sta generate key' % (tc_common_name, idx, step)
        test_cfgs.append(({ 'sta_tag':sta_tag_1 }, test_name, common_name, 2, False))
        
        
        test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
        step += 1
        common_name = '[%s]%s.%s sta perform authoize with key' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        step += 1
        common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_tag_1,'username':'test.user','use_guestpass_auth': True,'guest_name':'test.user','wlan_cfg':wlan_cfg ,'status': 'Authorized'}, test_name, common_name, 2, False))
        
        
        test_params = {'sta_tag': sta_tag_1, 
                       'test_policy': 'guest access',
                       'guest_name': 'test.user',
                       'use_guestpass_auth': True,
                       'wlan_cfg': wlan_cfg,
                       'status': 'Authorized'}
    
        for reauthorize_count in range(3):
            test_name = 'CB_ZD_Delete_Active_Client'
            step += 1
            common_name = "[%s]%s.%s delete the station from the zone currently active clients" % (tc_common_name, idx, step)
            test_cfgs.append((test_params, test_name, common_name, 2, False))
    
            test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
            step += 1
            common_name = '[%s]%s.%s sta perform authoize with key' % (tc_common_name, idx, step)
            test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
          
        test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
        step += 1
        common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
        test_cfgs.append(({}, test_name, common_name, 2, True))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Disconnect client to WLAN'% (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))     
        
    wlan_name_list = [("self_service_guest_wlan_%d" % i) for i in range(1,31)]
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_name_list':wlan_name_list}, test_name, common_name, 2, True))

    #************************************(12)**********************************************************
    tc_common_name = "fail over"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate %s to WLAN' % (tc_common_name,idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
 
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s %s generate key' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({ 'sta_tag':sta_tag_1 }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s %s perform authoize wih key' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({ 'sta_tag':sta_tag_1 }, test_name, common_name, 2, False))
  
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'username':'test.user','use_guestpass_auth': True,'guest_name':'test.user','wlan_cfg':wlan_cfg_wlan_1 ,'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify %s can ping target ip' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_SR_Failover'
    step += 1
    common_name = '[%s]%s.%s Failover the active zd'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate %s to WLAN' % (tc_common_name,idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get %s wifi address' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
  
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s %s perform authoize with key' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag':sta_tag_1}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify %s status on zd' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'username':'test.user','use_guestpass_auth': True,'guest_name':'test.user','wlan_cfg':wlan_cfg_wlan_1 ,'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify %s can ping target ip' % (tc_common_name, idx, step,sta_tag_1)
    test_cfgs.append(({'sta_tag': sta_tag_1,'target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, True))

    
    
    #************************************(14)**********************************************************
    tc_common_name = "max guest pass"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_Remove_All_Users'
    step += 1
    common_name = '[%s]%s.%s Remove all local user' % (tc_common_name,idx, step)
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1,'wlan_cfg': wlan_cfg_wlan_1}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': sta_tag_1}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_Using_Command'
    common_name = '[%s]%s.%s sta generate max guestpass' % (tc_common_name, idx, step)
    test_cfgs.append(({ 'expect_guestpass_count':10000, }, test_name, common_name, 2, False))  
    
    #****************************************clean up**************************************************
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove the WLAN from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Remove GuestService from ZDCLI'
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable sw port connected to mesh ap'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd1'
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd2'
    test_cfgs.append(({'target_zd':'zd2'}, test_name, common_name, 0, True))
      
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD1 set Factory to clear configuration'
    test_cfgs.append(({'zd':'zd1'},test_name, common_name, 0, True))  
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD2 set Factory to clear configuration'
    test_cfgs.append(({'zd':'zd2'},test_name, common_name, 0, True))  
    
    test_name = 'CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD'
    common_name = 'Make all aps connect init active zd'
    test_cfgs.append(({'ap_num':len(cfg['all_ap_tag_list']),'from_zd':'zd2','to_zd':'zd1'}, test_name, common_name, 0, True))
    
    for ap_tag in cfg['all_ap_tag_list']:
        test_name = 'CB_ZD_CLI_Wait_AP_Connect'
        common_name = 'Make sure %s connect init active zd'%ap_tag
        test_cfgs.append(({'zd_tag':'zdcli1','ap_tag':ap_tag}, test_name, common_name, 0, True))


    return test_cfgs

def gen_random_int():
    return randint(1,10000)
    
    
def define_test_parameters():
    
    hotspot_name ='Hotsport_Default'
    servername = 'Local Database'
   
    guest_wlan_name = 'self_service_guest_wlan'
    guest_access_conf = {'terms_of_use': 'Disabled',
                         'self_service_registration':{
                                                      'status':'Enabled',
                                                      'duration':'1 days',
                                                      'share_number':'1',
                                                      'notification_method':'Device Screen',   
                                                      'sponsor_approval':{'status':'Disabled'},}}                                         
        
    guest_wlan_cfg = {'name' :guest_wlan_name,
                      'ssid': guest_wlan_name,
                      'auth': 'open',
                      'encryption' : 'none',     
                      'type':'guest',
                      'tunnel_mode':False,
                      'guest_access_service':guest_access_conf,}
    
    hotspot_conf = {'name': hotspot_name, 
                    'start_page': '', 
                    'authentication_server':servername, 
                    'accounting_server': 'Disabled', 
                    'login_page_url':'http://192.168.0.250/login.html'}
    
    tcfg = {'guest_access_conf':guest_access_conf,
            'guest_wlan_cfg':guest_wlan_cfg,
            'hotspot_conf':hotspot_conf,
            }
    
    return tcfg
    
def _select_ap(ap_sym_dict, ap_type):
    select_tips = """Possible AP roles are: RootAP, MeshAP and AP
Enter symbolic AP from above list for %s: """ % ap_type
    while (True):
        testsuite.showApSymList(ap_sym_dict)
        active_ap = raw_input(select_tips)
        
        if active_ap:
            return active_ap
    
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    
    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
     
    ap_sym_dict = tbcfg['ap_sym_dict'] 
    sta_ip_list = tbcfg['sta_ip_list']
    
    if ts_cfg["interactive_mode"]:
        target_sta_1 = testsuite.getTargetStation(sta_ip_list, "this feature needs 2 station,Pick first station: ")
        target_sta_2 = testsuite.getTargetStation(sta_ip_list, "Pick another wireless station: ")
        if len(sta_ip_list)< 2:
            print "Sorry,this ats needs 2 station at least.please check your testbed"
            return
        active_radio = testsuite.get_target_sta_radio()
    else:
        target_sta_1 = sta_ip_list[ts_cfg["station"][0]]
        target_sta_2 = sta_ip_list[ts_cfg["station"][1]]
        active_radio = 'na'
    
    all_ap_tag_list = []
    for ap_tag in ap_sym_dict:
        all_ap_tag_list.append(ap_tag)
   
    if ts_cfg["interactive_mode"]:
        root_ap_tag = _select_ap(ap_sym_dict, 'Root AP')
        mesh_ap_tag = _select_ap(ap_sym_dict, 'Mesh AP')
    

    tcfg = {'target_sta_1':target_sta_1,
            'target_sta_2':target_sta_2,
            'active_radio':active_radio,
            'all_ap_tag_list':all_ap_tag_list,
            'mesh_ap_tag':mesh_ap_tag,
            'root_ap_tag':root_ap_tag,
            }
    
    ts_name = 'Selfservice Guest Pass Combination under SR and Mesh'
    ts = testsuite.get_testsuite(ts_name, 'Verify Selfservice Guest Pass Combination Function under SR and Mesh', combotest=True)
    
    dcfg = define_test_parameters()
    tcfg.update(dcfg)
    
    test_cfgs = define_test_cfg(tcfg)
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