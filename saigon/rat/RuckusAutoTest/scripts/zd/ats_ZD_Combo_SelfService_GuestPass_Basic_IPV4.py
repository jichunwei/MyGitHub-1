"""
Verify self-service guest pass basic function under ipv4 only.

    Pre-condition:
       AP joins ZD
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) create guest service enable self service
        2) create guest wlan with guest service
        3) case1:[self service update mobile]
        4) case2:[self service update name]
        5) case3:[update invalid name and invalid mobile]
        6) case4:[self service sponsor number] #needs firefox version 36.0.1
        7) case5:[self service with tunnel and tac]
        8) case6:[self service with invalid guest pass]
        9) case7:[self service with enable session time]
        10) case8:[reboot and restore]
        
    ps:
    
Created on 2015-2-9
@author: Yu.yanan@odc-ruckuswireless.com
"""

import sys
from random import randint
import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as CONST
from copy import deepcopy
from RuckusAutoTest.common import lib_Constant as constant


def define_test_cfg(cfg):
 
    test_cfgs = [] 
    idx = 0
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target client'
    test_cfgs.append(({'sta_ip_addr':cfg['target_sta_1'],'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from client'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Remove all GuestService from ZDCLI'
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan' 
    common_name = 'create guest wlan with self service'
    test_cfgs.append(({'wlan_conf':cfg['guest_wlan_cfg']}, test_name, common_name, 0, False))

    
    #****************************************case (1) update mobile ***************************************************
    idx +=1
    step = 0
    tc_common_name = "self service update mobile"
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key with name and default mobile' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1',}, test_name, common_name, 2, False))
    
    
    update_mobile_cfg = {'sta_tag':'sta_1',
                        'clear_mobile':True,
                        'user_register_infor':{'username':'test.user','email':'test.user@163.com','countrycode':'+010','mobile':'13011223344'}
                        }
    test_name = 'CB_Station_SelfService_Update_Contact'
    step += 1
    common_name = '[%s]%s.%s sta update mobile' % (tc_common_name, idx, step)
    test_cfgs.append((update_mobile_cfg, test_name, common_name, 2, False))
 
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    
    #****************************************case (2) update name ***************************************************
    
    idx +=1
    step = 0
    tc_common_name = "self service update name"
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key with name' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1','clear_mobile':True,}, test_name, common_name, 2, False))
    
    update_name_cfg = {'sta_tag':'sta_1','user_register_infor':{'username':'my.user','email':'test.user@163.com','countrycode':'','mobile':''}}
    test_name = 'CB_Station_SelfService_Update_Contact'
    step += 1
    common_name = '[%s]%s.%s sta only update name ' % (tc_common_name, idx, step)
    test_cfgs.append((update_name_cfg, test_name, common_name, 2, False))
        
    update_name_mobile_cfg = {'sta_tag':'sta_1',             
                              'user_register_infor':{'username':'new.user','email':'test.user@163.com','countrycode':'+010','mobile':'111111111111111111111111111111'}
                              }
    test_name = 'CB_Station_SelfService_Update_Contact'
    step += 1
    common_name = '[%s]%s.%s sta update name and mobile ' % (tc_common_name, idx, step)
    test_cfgs.append((update_name_mobile_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    #**************************(3) update invalid name and invalid mobile**********************************************************
    
    idx +=1
    step = 0
    tc_common_name = "self service update invalid name and invalid mobile"
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key with name' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1','clear_mobile':True,}, test_name, common_name, 2, False))
    
    update_name_cfg = {'sta_tag':'sta_1','condition_allow':False,'user_register_infor':{'username':'invalid.name.&^*','email':'test.user@163.com','countrycode':'','mobile':''}}
    test_name = 'CB_Station_SelfService_Update_Contact'
    step += 1
    common_name = '[%s]%s.%s sta only update invalid name ' % (tc_common_name, idx, step)
    test_cfgs.append((update_name_cfg, test_name, common_name, 2, False))
        
    update_name_mobile_cfg = {'sta_tag':'sta_1', 
                              'condition_allow':False,            
                              'user_register_infor':{'username':'new.user','email':'test.user@163.com','countrycode':'+010','mobile':'133ruckus'}
                              }
    test_name = 'CB_Station_SelfService_Update_Contact'
    step += 1
    common_name = '[%s]%s.%s sta only update invalid mobile ' % (tc_common_name, idx, step)
    test_cfgs.append((update_name_mobile_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    

    #*************************(3)sponsor max number*********************************************************************
    idx +=1
    step = 0
    tc_common_name = "self service sponsor number"
        
    guest_access_conf_enable_sponsor = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_enable_sponsor.update({'self_service_registration':{'status':'Enabled',                                                           
                                                                          'notification_method':'Mobile',
                                                                          'sponsor_approval':{
                                                                                              'status':'Enabled',
                                                                                              'sponsor_auth_server': 'Local Database', 
                                                                                              'sponsor_number': '5'}}})
                                                               
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s edit guest_service with sponsor maxnumber'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':guest_access_conf_enable_sponsor}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key ' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1','condition_allow':False}, test_name, common_name, 2, False))
    
    
    guest_access_conf_disable_sponsor = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_disable_sponsor.update({'self_service_registration':{'status':'Enabled',                                                           
                                                                           'sponsor_approval':{'status':'Disabled',} }})                                                    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s edit guest_service with disable sponsor'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':guest_access_conf_disable_sponsor}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    
    
    #************************(4) tunnel and Terms_and_conditon************************************************************************************
    
    idx +=1
    step = 0
    tc_common_name = "self service with tunnel and terms_and_condition"
    
    guest_wlan_cfg_tunnel = deepcopy(cfg['guest_wlan_cfg'])
    guest_wlan_cfg_tunnel.update({'tunnel_mode':True})
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s edit wlan with enable tunnel' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':guest_wlan_cfg_tunnel}, test_name, common_name, 1, False))
    
    
    guest_access_conf_tou = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_tou.update({'self_service_registration':{'status':'Enabled',                                                          
                                                               'terms_and_conditions': 'this is test',}})  
       
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s edit guest_service with enable terms_and_condition'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':guest_access_conf_tou}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': guest_wlan_cfg_tunnel}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1','use_tac':True,'tac_text':'this is test'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform authorize with key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1',} , test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': guest_wlan_cfg_tunnel,'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

    guest_wlan_cfg_disable_tunnel = deepcopy(cfg['guest_wlan_cfg'])
    guest_wlan_cfg_disable_tunnel.update({'tunnel_mode':False})
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s edit wlan with disable tunnel' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':guest_wlan_cfg_disable_tunnel}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    #*****************************case (5) invalid key ***************************************************
    
    tc_common_name = "self service with invalid guest pass"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
      
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform auth with invalid key' % (tc_common_name, idx, step)
    test_cfgs.append(( {'sta_tag':'sta_1','guest_pass':'INVALID','condition_allow':False}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','guest_name':'test.user','use_guestpass_auth':True,'wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Unauthorized',}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can not ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','condition': 'disallowed'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    #****************************************case(6) session time ***************************************************  
    
    tc_common_name = "self service with enable session time"
    idx +=1
    step = 0
    
    guest_access_conf_session = deepcopy(cfg['guest_access_conf'])
    guest_access_conf_session.update({'self_service_registration':{'status':'Enabled',
                                                                   're-auth_time': '5 mins', }})                                                               
                    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s edit guest_service with enable session time'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':guest_access_conf_session}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1'}, test_name, common_name, 2, False))
   
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform authorize with key' % (tc_common_name, idx, step)
    test_cfgs.append(( {'sta_tag':'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Authorized',}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'condition': 'allowed'}, test_name, common_name, 2, False))

    #after session time
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd after session time' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'check_status_timeout':'300','guest_name':'test.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Unauthorized'}, test_name, common_name, 2, False))
  
    # can not ping
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can not ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'condition': 'disallowed'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s edit guest_service with disable session time'% (tc_common_name, idx, step)
    test_cfgs.append(({'guest_access_conf':cfg['guest_access_conf']}, test_name, common_name, 2, True))
    
    
    #*******************************case (7) reboot and restore ******************************************************
    
    tc_common_name = "reboot and restore"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','expected_failed': True,'wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform authorize with key'% (tc_common_name, idx, step)
    test_cfgs.append(( {'sta_tag':'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Authorized',}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'condition': 'allowed'}, test_name, common_name, 2, False))
    
    test_params = {'sta_tag': 'sta_1', 
                   'test_policy': 'guest access',
                   'guest_name': 'test.user',
                   'use_guestpass_auth': True,
                   'wlan_cfg': cfg['guest_wlan_cfg'],
                   'status': 'Authorized'}
    
    test_name = 'CB_ZD_Delete_Active_Client'
    step += 1
    common_name = "[%s]%s.%s delete the station from the zone currently active clients" % (tc_common_name, idx, step)
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Backup'
    common_name = '[%s]%s.%s backup zd configuration'% (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':cfg['guest_wlan_cfg'],'save_to':constant.save_to}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    step += 1
    common_name = '[%s]%s.%s Reboot ZD from CLI'% (tc_common_name, idx, step)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 2, False)) 

    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform auth with key' % (tc_common_name, idx, step)
    test_cfgs.append(( {'sta_tag':'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Authorized',}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

    
    test_name = 'CB_ZD_Delete_Active_Client'
    step += 1
    common_name = "[%s]%s.%s delete the station from the zone currently active clients" % (tc_common_name, idx, step)
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = '[%s]%s.%s Remove all GuestService from ZDCLI' % (tc_common_name, idx, step)
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 2, False))
         
    test_name = 'CB_ZD_Restore'
    step += 1
    common_name = '[%s]%s.%s zd restore configuration' % (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform authorize with key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Authorized',}, test_name, common_name, 2, False))
  
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','condition': 'allowed'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
 
    #****************************************clean up**************************************************
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove the WLAN from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
     
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Remove GuestService from ZDCLI'
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 0, True))
    

    return test_cfgs

def gen_random_int():
    return randint(1,10000)
    
    
def define_test_parameters(tbcfg):
    
    random_num = gen_random_int()
    guest_wlan_name = 'guest_wlan'+str(random_num)
   
    guest_access_conf = {
                         'self_service_registration':{'status':'Enabled',}                                
                        }
    
        
    guest_wlan_cfg = { 
                       'name' :guest_wlan_name,
                       'ssid': guest_wlan_name,
                       'auth': 'open',
                       'encryption' : 'none',     
                       'type':'guest-access',
                       'guest_access_service':guest_access_conf,
                       }
    
    self_service_cfg={
                        'expected_data': 'It works!', 
                        'target_url': CONST.TARGET_IPV4_URL, 
                        'no_auth': False,  
                        'redirect_url': '', 
                        'guest_auth_cfg': {'use_tou': False}, 
                        'user_register_infor':{'username':'test.user','email':'test.user@163.com','countrycode':'','mobile':''},
                        'generate_guestpass':False,
                        'update_contact_detail':False,
                        'check_update_contact_detail':False,
                        'start_browser_before_auth': True,
                        'close_browser_after_auth': True,
                        'use_tou': False,
                        'sta_tag': 'sta_1',
                        'clear_mobile':False,
                    }
        
    tcfg = {'guest_access_conf':guest_access_conf,
            'guest_wlan_cfg':guest_wlan_cfg,
            'self_service_cfg':self_service_cfg
            }
    
    return tcfg
    

    
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    
    if ts_cfg["interactive_mode"]:
        target_sta_1 = testsuite.getTargetStation(sta_ip_list, "this feature needs 1 station,Pick first station: ")
        if len(sta_ip_list)< 1:
            print "Sorry,this ats needs 1 station at least.please check your testbed"
            return
    else:
        target_sta_1 = sta_ip_list[ts_cfg["station"][0]]
    
  
    tcfg = {'target_sta_1':target_sta_1,}
            
    
    ts_name = 'Selfservice Guest Pass Basic Function under Ipv4'
    ts = testsuite.get_testsuite(ts_name, 'Verify Selfservice Guest Pass Basic Function under Ipv4', combotest=True)
    
    dcfg = define_test_parameters(tbcfg)
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