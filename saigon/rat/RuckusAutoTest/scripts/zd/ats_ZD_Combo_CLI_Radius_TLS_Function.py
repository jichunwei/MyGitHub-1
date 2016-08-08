

import sys, os
import time
from copy import deepcopy
from random import randint
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as constant

#configuration on RadiusSec Server
radius_user ={'grace.period.user': 'grace.period.user', 
              'idle.timeout.user':'idle.timeout.user', 
              'session.timeout.user':'session.timeout.user',
              'role.user':'rad.cisco.user',
              'ras.local.user':'ras.local.user',
              }
radius_session_timeout = 120 #seconds
radius_grace_period = 180 #seconds
radius_idle_timeout = 120 #seconds

def define_test_cfg(cfg):
    global radius_user
    global radius_session_timeout
    global radius_grace_period
 
    test_cfgs = [] 

    radio_mode = cfg['radio_mode']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode


    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove all aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create Radius auth server enable TLS with PAP.'
    test_cfgs.append(({'server_cfg_list':[cfg['ras_cfg']]}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
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
    #****************************************case 1***************************************************
    #****************************************hotspot wlan ,session timeout***************************************************
    round = 0
    step = 0
    round += 1

    tc_common_name = "Radsec Session timeout with hotspot"
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s create hotspot wlan with TLSRadius' % (tc_common_name,round, step)
    test_cfgs.append(({'wlan_conf':cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,#'original_url': 'https://172.16.10.252/', 
                       'username': radius_user['session.timeout.user'], 'password': radius_user['session.timeout.user'],
                       'close_browser_after_auth': True,  'start_browser_before_auth': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'username':radius_user['session.timeout.user'],'status': 'Authorized',
                       'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg'],'ap_tag': ap_tag,}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Hotspot_Session_Timeout'
    step += 1
    common_name = '[%s]%s.%s Test station disconnet to ZD beyond session timeout' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'auth_info':{'username':radius_user['session.timeout.user'],
                                    'password':radius_user['session.timeout.user'],
                                    'session_timeout':'2'}, 
                       'hotspot_cfg':cfg['hotspot_with_tlsradius_conf'],'target_ip':'192.168.0.232',
                       'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'username': radius_user['session.timeout.user'], 'password': radius_user['session.timeout.user'],
                       'close_browser_after_auth': True,  'start_browser_before_auth': True}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'username':radius_user['session.timeout.user'],'status': 'Authorized',
                       'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg'],'ap_tag': ap_tag,}, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))

    #****************************************case 2 ***************************************************
    #**************************************** EAP webauth wlan , grace period , Dvlan ***************************************************    
    tc_common_name = "Radsec Grace Period with Webauth"
    round +=1
    step = 0     
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s Create wlan with webauth' % (tc_common_name, round, step)
    test_cfgs.append(({'wlan_conf':cfg['webauth_wlan_cfg']}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'wlan_cfg': cfg['webauth_wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'start_browser_before_auth': True, 'close_browser_after_auth': True ,#'target_url': 'https://172.16.10.252/',
                       'username':radius_user['grace.period.user'], 'password': radius_user['grace.period.user']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s Verify client information Authorized status in ZD' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'username':radius_user['grace.period.user'],
                       'wlan_cfg': cfg['webauth_wlan_cfg'],'status': 'Authorized','ap_tag': ap_tag,}, test_name, common_name, 2, False))

    grace_period_time = 3
    test_name = 'CB_ZD_Test_Grace_Period'
    step += 1
    common_name = "[%s]%s.%s Test station reconnect within grace period" % (tc_common_name, round, step)
    test_params = {'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'grace_period': grace_period_time,
                       'reconnect_within_gp': True,
                       'no_need_auth': True,
                       'wlan_cfg': cfg['webauth_wlan_cfg'],
                       'username': radius_user['grace.period.user'],
                       'radio_mode': radio_mode,
                       'target_ip': cfg['target_ip'],#?252 232
                       }    
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    step += 1
    common_name = "[%s]%s.%s Test station reconnect beyond grace period" % (tc_common_name, round, step)
    test_params = {'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'grace_period': grace_period_time,
                       'reconnect_within_gp': False,
                       'no_need_auth': False,
                       'wlan_cfg': cfg['webauth_wlan_cfg'],
                       'username': radius_user['grace.period.user'],
                       'radio_mode': radio_mode,
                       'target_ip': cfg['target_ip'],
                       }
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'start_browser_before_auth': True, 'close_browser_after_auth': True ,#'target_url': 'https://172.16.10.252/',
                       'username':radius_user['grace.period.user'], 'password': radius_user['grace.period.user']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s Verify client information Authorized status in ZD' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'username':radius_user['grace.period.user'],
                       'wlan_cfg': cfg['webauth_wlan_cfg'],'status': 'Authorized','ap_tag': ap_tag,}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))

    #****************************************case 3 ***************************************************
    tc_common_name = "Radsec with Admin Auth"
    round +=1
    step = 0 

    test_name = 'CB_ZD_Backup_Admin_Cfg'
    step += 1
    common_name = '[%s]%s.%sBackup the admin configuration'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    step += 1
    common_name = '[%s]%s.%s Create a role for radiusTLS test' % (tc_common_name,round, step)
    test_cfgs.append(({'role_cfg_list':cfg['role_cfg_list']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_Admin'
    step += 1
    common_name = '[%s]%s.%sConfigure administer with radsec user in ZD CLI' % (tc_common_name, round, step)
    test_cfgs.append(({'admin_cfg': cfg['admin_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login'
    step += 1
    common_name = '[%s]%s.%sLogin ZD GUI' %  (tc_common_name, round, step)
    test_cfgs.append(({'login_name':cfg['admin_cfg']['login_name'], 'login_pass': cfg['admin_cfg']['login_pass']}, 
                          test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Admin_Cfg_In_GUI'
    step += 1
    common_name = '[%s]%s.%sVerify administer with radsec user configuration in ZD GUI' %  (tc_common_name, round, step)
    test_cfgs.append(({'admin_cfg': cfg['admin_cfg']}, test_name, common_name, 2, False))
     
    test_name = 'CB_ZD_CLI_Restore_Admin'
    step += 1
    common_name = '[%s]%s.%sRestore admin to original configuration in ZD CLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))   
    
    #****************************************case 3 ***************************************************
    tc_common_name = "Radsec with Zero-IT Activation"
    round +=1
    step = 0
    
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    step += 1
    common_name = '[%s]%s.%s set TLSRadius server for zeroIT'%(tc_common_name, round, step)
    test_cfgs.append(({'zero_it_auth_serv':cfg['ras_name'] }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s create WLAN with eap' % (tc_common_name,round, step)
    test_cfgs.append(({'wlan_conf':cfg['eap_wlan_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Station_Config_Wlan_With_ZeroIT'
    step += 1
    common_name = '[%s]%s.%s station connect wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag, 'wlan_cfg':cfg['eap_wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify station status in zd' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'wlan_cfg': cfg['eap_wlan_cfg'],'status': 'Authorized','ap_tag': ap_tag,}, test_name, common_name, 2, False))    
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))      

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    step += 1
    common_name = '[%s]%s.%s set TLSRadius server for zeroIT'%(tc_common_name, round, step)
    test_cfgs.append(({'zero_it_auth_serv':"Local Database" }, test_name, common_name, 2, True))

    #****************************************case 4 ***************************************************
    tc_common_name = "Radsec with role testing factory and restore"
    round +=1
    step = 0
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    step += 1
    common_name = '[%s]%s.%s Create a role for radiusTLS test' % (tc_common_name,round, step)
    test_cfgs.append(({'role_cfg_list':cfg['role_cfg_list']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s Create wlan with hotspot' % (tc_common_name,round, step)
    test_cfgs.append(({'wlan_conf':cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Backup'
    step += 1
    common_name = '[%s]%s.%s Backup zd configuration' % (tc_common_name,round, step)
    test_cfgs.append(({'wlan_conf':cfg['hotspot_wlan_with_tlsradius_cfg'],'save_to':constant.save_to}, test_name, common_name, 2, False))
    
    
    for count in range(0,2):
    
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
        test_cfgs.append(({'sta_tag': sta_tag,'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    
        test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
        step += 1
        common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, round, step)
        test_cfgs.append(({'sta_tag': sta_tag,'original_url': 'http://172.16.10.252/', 'username': radius_user['role.user'], 
                           'close_browser_after_auth': True, 'password': radius_user['role.user'], 'start_browser_before_auth': True}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        step += 1
        common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, round, step)
        test_cfgs.append(({'sta_tag': sta_tag,'username':radius_user['role.user'],'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg'],
                           'status': 'Authorized','role':cfg['role_cfg_list'][0]['role_name'],'ap_tag': ap_tag,}, test_name, common_name, 2, False))


        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        if count == 0:
            test_name = 'CB_ZD_CLI_Reboot_ZD'
            step += 1
            common_name = '[%s]%s.%sReboot ZD from CLI'% (tc_common_name, round, step)
            test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_Factory_Default'
    step += 1
    common_name = '[%s]%s.%s zd set factory' % (tc_common_name,round, step)
    test_cfgs.append(({'relogin_zdcli':False,'sta_tag': sta_tag,'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s verify station disconnect wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'expected_failed': True,'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Restore'
    step += 1
    common_name = '[%s]%s.%s zd restore configuration' % (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    step += 1
    common_name = '[%s]%s.%s perform hotspot auth in station' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'original_url': 'http://172.16.10.252/', 'username': radius_user['role.user'], 
                'close_browser_after_auth': True, 'password': radius_user['role.user'], 'start_browser_before_auth': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'username':radius_user['role.user'],'wlan_cfg': cfg['hotspot_wlan_with_tlsradius_cfg'],
                           'status': 'Authorized','role':cfg['role_cfg_list'][0]['role_name'],'ap_tag': ap_tag,}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True)) 
              
    #****************************************case 5 ***************************************************
    tc_common_name = "Radsec cannot with invalid CA"
    round +=1
    step = 0

    test_name = 'CB_ZD_import_CA_to_ZD'
    step += 1
    common_name = '[%s]%s.%sImport an invalid CA to ZD'% (tc_common_name, round, step)
    test_cfgs.append(({'file_name':os.path.join(constant.save_to, 'invalid_ca.pem')}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Reboot_ZD'
    step += 1
    common_name = '[%s]%s.%sReboot ZD from CLI'% (tc_common_name, round, step)
    test_cfgs.append(( {}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%sCreate wlan with webauth' % (tc_common_name, round, step)
    test_cfgs.append(({'wlan_conf':cfg['webauth_wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'wlan_cfg': cfg['webauth_wlan_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'start_browser_before_auth': True, 'close_browser_after_auth': True ,
                       'target_url': 'http://172.16.10.252/','username': radius_user['ras.local.user'], 
                       'password': radius_user['ras.local.user'],'negative':True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify station disconnect wlan' % (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag,'target': '172.16.10.252', 'condition': 'disallowed'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, round, step)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))        
        
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, round, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))    
    
    test_name = 'CB_ZD_import_CA_to_ZD'
    step += 1
    common_name = '[%s]%s.%sImport trusted CA to ZD'% (tc_common_name, round, step)
    test_cfgs.append(({'file_name':os.path.join(constant.save_to, 'ca.pem')}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    step += 1
    common_name = '[%s]%s.%sReboot ZD from CLI'% (tc_common_name, round, step)
    test_cfgs.append(( {}, test_name, common_name, 2, True))
    #****************************************clean up**************************************************
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove the WLAN from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
         
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    step += 1
    common_name = 'Remove all hotspot profile from ZDCLI' ### How to all??
    test_cfgs.append(({'cleanup':True,'hotspot_conf':{'name':cfg['hotspot_name']}}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    return test_cfgs
   
def gen_random_int():
    return randint(1,10000)
    
def define_test_parameters(tbcfg):
    global radius_user    
    role_cfg_list= [{'role_name': 'radius-tls-role',
                      'description': '', 
                      'group_attr': '0123456789', 
                      'guest_pass_gen': True,  
                      'allow_all_wlans': True, 
                      'zd_admin_mode':'super',
                      'allow_zd_admin': True,
                      }]
    
    server_ip_addr  = '192.168.0.232'
    ras_name = 'TLSRadiussec-%s' % (time.strftime("%H%M%S"),)
    ras_acct_name = 'TLSRadiussec-acct-%s' % (time.strftime("%H%M%S"),)
    
    ras_cfg = {'type': 'radius-auth',
               'server_name' : ras_name,
               'server_addr': server_ip_addr,
               'server_port' : '2083',
               'radius_encryption':True,
               'radius_auth_method': 'chap',
                }
    
    rand_num = gen_random_int()
    hotspot_name = "Hotsport_Default"
    hotspot_wlan_name = 'tlsradius-hotspot-%s' % (time.strftime("%H%M%S"),)

    hotspot_with_tlsradius_conf = {'name': hotspot_name, 
                    'start_page': '', 
                    'authentication_server':ras_name, 
                    'accounting_server': 'Disabled', 
                    'login_page_url':'http://192.168.0.250/login.html'}
        
    hotspot_wlan_with_tlsradius_cfg = {'name' : hotspot_wlan_name,
                        'ssid': hotspot_wlan_name,
                        'auth': 'open',
                        'encryption' :'none',
                        'type':'hotspot', 
                        'hotspot_service': hotspot_with_tlsradius_conf,
                        }
       
       
    guest_name = 'Guest-Auth'
    guest_wlan_name = 'tlsradius-guest-%s' % (time.strftime("%H%M%S"),)   
    generate_guestpass_cfg= dict(type = "single",
                                 guest_fullname = guest_name,
                                 duration = "5",
                                 duration_unit = "Days",
                                 key = "",
                                 wlan = guest_wlan_name,
                                 remarks = "",
                                 is_shared = "YES",
                                 auth_ser = ras_name,
                                 username = radius_user['idle.timeout.user'],
                                 password = radius_user['idle.timeout.user'])                                               
                    
    guest_access_conf = {'authentication_server': ras_name,
                         'authentication': 'Use guest pass authentication.',      
                         'terms_of_use': 'Disabled'}
    
    guest_wlan_with_tlsradius_cfg =  {"name" :guest_wlan_name,
                       'ssid': guest_wlan_name,
                       'auth': 'open',
                       'encryption' : 'none',     
                       'type':'guest-access',
                       'guest_access_service':guest_access_conf,
                       }
    
    webauth_wlan_name = 'tlsradius-webauth-gp-%s' % (time.strftime("%H%M%S"),)    
    webauth_wlan_cfg = {"name" : webauth_wlan_name,
                    "ssid" : webauth_wlan_name,
                    "type" : "standard-usage",
                    "auth" : "open",
                    "encryption" : "none",
                    'web_auth':True,
                    'auth_server':ras_name,
                    'username':radius_user['grace.period.user'],
                    'password':radius_user['grace.period.user']
                    } 
    
    eap_wlan_name = 'tlsradius-eap-%s' % (time.strftime("%H%M%S"),)
    eap_username ='ras.eap.user'
    eap_wlan_cfg={"name":eap_wlan_name,
                  "ssid":eap_wlan_name,
                  "auth" : "EAP",
                  'wpa_ver':"WPA2",
                  "encryption" : "AES",
                  'auth_server':ras_name,
                  'username':eap_username,
                  'password':eap_username,
                  'sta_wpa_ver':'WPA2',
                  'sta_encryption':'AES',
                  'sta_auth':'EAP',
                  'do_zero_it':True,
                  'use_radius':True
                  }
    
    local_database = 'Local Database'    
    
    admin_cfg = dict(auth_method = 'external', 
                     auth_server = ras_name, 
                     fallback_local = True, 
                     login_name = radius_user['role.user'], 
                     login_pass = radius_user['role.user'],
                     admin_name='admin', 
                     admin_pass='admin',
                    )
    
    dcfg = {'ras_cfg':ras_cfg,
            'ras_name':ras_name,
            'hotspot_name':hotspot_name,
            'hotspot_with_tlsradius_conf':hotspot_with_tlsradius_conf,
            'hotspot_wlan_with_tlsradius_cfg':hotspot_wlan_with_tlsradius_cfg,
            'guest_wlan_with_tlsradius_cfg':guest_wlan_with_tlsradius_cfg,
            'guest_access_conf':guest_access_conf,
            'generate_guestpass_cfg':generate_guestpass_cfg,
            'guest_name':guest_name,
            'webauth_wlan_cfg':webauth_wlan_cfg,
            'local_database':local_database,
            'role_cfg_list':role_cfg_list,
            'eap_wlan_cfg':eap_wlan_cfg,
            'admin_cfg':admin_cfg,
            'target_ip':server_ip_addr,
            }
    
    return dcfg
    

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ") 
    target_sta_radio = testsuite.get_target_sta_radio()    
    active_ap = active_ap_list[0]   
    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            }    
    dcfg = define_test_parameters(tbcfg)
    tcfg.update(dcfg)
    test_cfgs = define_test_cfg(tcfg)

    ts_name = 'Radius over TLS Function test'
    ts = testsuite.get_testsuite(ts_name, 'Verify Radius over TLS Functions', combotest=True)
    
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