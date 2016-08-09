'''
Created on May 13, 2014

@author: yinwenling
'''
import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all Users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all Wlans from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA Servers from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = 'Remove all DPSK'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = 'Delete Radius Users'
    test_cfgs.append(({'del_user':cfg['server_user_list']}, test_name, common_name, 0, False))
       
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create AAA Servers'
    test_cfgs.append(({'server_cfg_list':cfg['server_cfg_list']}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = 'Create Standard Usage + Open wlans'
    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list']}, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = 'Create roles'
    test_cfgs.append(({'role_cfg_list':cfg['roles_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Multi_Users'
    common_name = 'Create Users'
    test_cfgs.append(({'user_cfg_list':cfg['user_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = 'Create Radius Users'
    test_cfgs.append(({'add_user':cfg['server_user_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service on active zd'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
    
    ap_tag = "AP_02"
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable AP WLAN service in ZD CLI'  
    test_cfgs.append(({'cfg_type': 'config','ap_tag': ap_tag,'ap_cfg': {'radio': cfg['radio_mode'], 'wlan_service': True}}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station']}, test_name, common_name, 0, False))
    
    tc_combo_name = "Verify Role-base Access Control With "
        
    for wlan_name in cfg['wlan_name_list']:
        selected_role_number = random.randrange(0,4)
        selected_role_number = 3
        selected_role_name = cfg['roles_cfg'][selected_role_number]['role_name']
        selected_role_cfg =  cfg['roles_cfg'][selected_role_number]
        
        cb_step = 1
        index = cfg['wlan_name_list'].index(wlan_name)
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 1, False))
        cb_step += 1
        
        if selected_role_name == "role_policy_ostype":
            cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,selected_role_cfg,'none',True)
            
            test_name = 'CB_ZD_Verify_Station_Info'
            common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': cfg['expected_station_info_dict']["role_policy_ostype_deny"]}, test_name, common_name, 2, False))
            cb_step += 1
        
            test_name = 'CB_ZD_CLI_Configure_Roles' 
            selected_role_cfg_copy = deepcopy(selected_role_cfg)          
            selected_role_cfg_copy["specify_os_type"] = cfg['os_type_list']
            common_name = '[%s%s]%s.%s Config os type allow windows in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,selected_role_name)
            test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
            cb_step += 1
            
            test_name = 'CB_ZD_Remove_Wlan_From_Station'
            common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
            cb_step += 1
            
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,selected_role_cfg)
        
        if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict'][selected_role_name])
            expected_station_info_copy['vlan'] = "1"
        else:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict'][selected_role_name])
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1 
        
        if selected_role_name == 'role_policy_rate':
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate uplink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append((cfg['expect_zing_para_up'], test_name, common_name, 2, False))
            cb_step += 1
            
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate downlink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append((cfg['expect_zing_para_down'], test_name, common_name, 2, False))
            cb_step += 1                              
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
        cb_step += 1
        
        tmp_wlan_list = deepcopy(cfg['wlan_name_list'])
        selected_role_cfg_copy = deepcopy(selected_role_cfg)
        selected_role_cfg_copy["specify_os_type"] = cfg['os_type_list']
        selected_role_cfg_copy['allow_all_wlans'] = False
        tmp_wlan_list.remove(wlan_name)
        selected_role_cfg_copy['specify_wlan_list'] = tmp_wlan_list
        test_name = 'CB_ZD_CLI_Configure_Roles'
        common_name = '[%s%s]%s.%s Disable wlan %s in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,wlan_name,selected_role_name)
        test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
        cb_step += 1
        
        if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
            cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,selected_role_cfg,"false",False,True)
        else:
            cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,selected_role_cfg,"true",False,True)
                
        if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["Default"])
            expected_station_info_copy['role'] = ""
        else:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["Default"])
        
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1
        
        if selected_role_name == 'role_policy_rate':
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate uplink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append((cfg['expect_zing_para_up_default'], test_name, common_name, 2, False))
            cb_step += 1
            
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate downlink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append((cfg['expect_zing_para_down_default'], test_name, common_name, 2, False))
            cb_step += 1
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_CLI_Configure_Roles'
        selected_role_cfg_copy = deepcopy(selected_role_cfg)
        selected_role_cfg_copy["specify_os_type"] = cfg['os_type_list']
        selected_role_cfg_copy['allow_all_wlans'] = True
        common_name = '[%s%s]%s.%s Enable wlan %s in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,wlan_name,selected_role_name)
        test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
        cb_step += 1
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,selected_role_cfg)
        
        if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict'][selected_role_name])
            expected_station_info_copy['vlan'] = "1"
        else:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict'][selected_role_name])
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1
        
        if selected_role_name == 'role_policy_rate':
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate uplink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append((cfg['expect_zing_para_up'], test_name, common_name, 2, False))
            cb_step += 1
            
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate downlink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
            test_cfgs.append((cfg['expect_zing_para_down'], test_name, common_name, 2, False))
            cb_step += 1
            
        if selected_role_name == "role_policy_ostype":
            test_name = 'CB_ZD_CLI_Configure_Roles'         
            common_name = '[%s%s]%s.%s Config os type allow windows in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,selected_role_name)
            test_cfgs.append(({'role_cfg_list': [selected_role_cfg]}, test_name, common_name, 2, False))
            cb_step += 1
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
        cb_step += 1
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,"role_policy_all",cfg['roles_cfg'][4],"none",True)
        
        if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
            expected_station_info_copy['vlan'] = "1"
            expected_station_info_copy['role'] = ''
        else:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
            
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_CLI_Configure_Roles'
        selected_role_cfg_copy = deepcopy(cfg['roles_cfg'][4])
        selected_role_cfg_copy["specify_os_type"] = cfg['os_type_list']
        common_name = '[%s%s]%s.%s Config os type allow windows in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,"role_policy_all")
        test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
        cb_step += 1
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,"role_policy_all",cfg['roles_cfg'][4])        
        
        if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
            expected_station_info_copy['vlan'] = "1"
        else:
            expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
        
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_Zing_Traffic_Station_LinuxPC'
        common_name = '[%s%s]%s.%s Verify rate uplink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append((cfg['expect_zing_para_up'], test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_Zing_Traffic_Station_LinuxPC'
        common_name = '[%s%s]%s.%s Verify rate downlink limiting' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append((cfg['expect_zing_para_down'], test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_CLI_Configure_Roles'         
        common_name = '[%s%s]%s.%s Config os type allow windows in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,"role_policy_all")
        test_cfgs.append(({'role_cfg_list': [cfg['roles_cfg'][4]]}, test_name, common_name, 2, False))
        cb_step += 1
        
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = 'Cleanup - Delete Radius Users'
    test_cfgs.append(({'del_user':cfg['server_user_list']}, test_name, common_name, 0, True))
    
        
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Cleanup - Remove all Users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Cleanup - Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Cleanup - Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Cleanup - Remove all Wlans from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Cleanup - Remove all AAA Servers from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = 'Cleanup - Remove all DPSK'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    return test_cfgs

def _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,role_name,role_cfg,flag = "true",authdeny = False,disable_flag = False):           
    if cfg['wlan_cfg_list'][index].get("enable_dpsk") and cfg['wlan_cfg_list'][index].get("enable_dpsk").lower()== "true":
        dpsk_conf = deepcopy(cfg['dpsk_conf'])
        dpsk_conf['wlan'] = wlan_name
        if cfg['wlan_cfg_list'][index].get("mobile_friendly"):
            dpsk_conf['mobile_friendly'] = True
        if disable_flag == False:
            dpsk_conf['role'] = role_name
        if disable_flag == False and role_cfg.has_key("vlan_policy"):
            dpsk_conf['vlan'] = role_cfg["vlan_policy"]
            
        test_name = 'CB_ZD_Generate_DPSK'
        common_name = '[%s%s]%s.%s Get the Dynamic PSK' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'dpsk_conf': dpsk_conf,"check_webui":False,"check_cli":False}, test_name, common_name, 2, False))
        cb_step += 1
        
        if authdeny == True:
            test_name = 'CB_Station_Association_WLAN_With_DPSK'
            common_name = '[%s%s]%s.%s STA connect to the wlan with %s' % (tc_combo_name,wlan_name,(index + 1),cb_step,role_name)
            test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': wlan_name,'auth_deny' : True}, test_name, common_name, 2, False))
            cb_step += 1
        else:
            test_name = 'CB_Station_Association_WLAN_With_DPSK'
            common_name = '[%s%s]%s.%s STA connect to the wlan with %s' % (tc_combo_name,wlan_name,(index + 1),cb_step,role_name)
            test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': wlan_name}, test_name, common_name, 2, False))
            cb_step += 1
                                   
    else:
        test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
        common_name = '[%s%s]%s.%s STA connect to the wlan with %s' % (tc_combo_name,wlan_name,(index + 1),cb_step,role_name)
        test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': wlan_name}, test_name, common_name, 2, False))
        cb_step += 1
        
    if cfg['wlan_cfg_list'][index].get("web_auth") and cfg['wlan_cfg_list'][index].get("web_auth") == True:
#        test_name = 'CB_Station_CaptivePortal_Start_Browser'
#        common_name = '[%s%s]%s.%s Create the browser object of the station' % (tc_combo_name,wlan_name,(index + 1),cb_step)
#        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
#        cb_step += 1

        web_auth_params = deepcopy(cfg['user_to_role_dict'][role_name])
        web_auth_params["sta_tag"]='sta1'
        web_auth_params['start_browser_before_auth'] = True
        web_auth_params['close_browser_after_auth'] = True
        test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
        common_name = '[%s%s]%s.%s STA perform Web Auth' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append((web_auth_params, test_name, common_name, 2, False))
        cb_step += 1
    
    if flag == "true":        
        test_name = 'CB_Station_Ping_Dest_Is_Allowed'
        common_name = '[%s%s]%s.%s the station ping a target ip is allowed' % (tc_combo_name,wlan_name,(index + 1),cb_step,)
        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
        cb_step += 1
    elif flag == 'none':
        pass
    else:
        test_name = 'CB_Station_Ping_Dest_Is_Denied'
        common_name = '[%s%s]%s.%s the station ping a target ip is denied' % (tc_combo_name,wlan_name,(index + 1),cb_step,)
        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))   
        cb_step += 1     
    return cb_step,test_cfgs

def define_test_parameters():
    cfg = {}
    """
        expect_zing_para
    """
    cfg["rate_limit"] = '0.10mbps'
    cfg['expect_zing_para_up'] = {'sta_tag': 'sta1',
                                  'rate_limit': cfg["rate_limit"],
                                  'margin_of_error': 0.2,
                                  'link_type': 'up'}
    cfg['expect_zing_para_down'] = {'sta_tag': 'sta1',
                                  'rate_limit': cfg["rate_limit"],
                                  'margin_of_error': 0.2,
                                  'link_type': 'down'}
    cfg['expect_zing_para_up_default'] = {'sta_tag': 'sta1',
                                  'rate_limit': '0.30mbps',
                                  'margin_of_error': 0.2,
                                  'link_type': 'up'}
    cfg['expect_zing_para_down_default'] = {'sta_tag': 'sta1',
                                  'rate_limit': '0.30mbps',
                                  'margin_of_error': 0.2,
                                  'link_type': 'down'}
    
    """
        server_cfg_list
    """
    aaa_ad_server = {
        'server_name': 'ACTIVE_DIRECTORY',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'example.net',
        'type'       :'ad'
    }
    
    aaa_ldap_server = {
        'server_name': 'LDAP',
        'server_addr':'192.168.0.252',
        'server_port':'389',
        'admin_domain_name': 'cn=Manager,dc=example,dc=net',
        'admin_password': 'lab4man1',
        'type'       :'ldap'
    }
    
    aaa_radius_server = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.252',
        'radius_secret': '1234567890',
        'server_port': '1812',
        'type'       :'radius-auth'
    }
    
    cfg['server_cfg_list'] = [aaa_ad_server,
                           aaa_ldap_server,
                           aaa_radius_server]
    
    """
       wlan_cfg_list
    """    
    standard_open_wpa2_zeroit_dpsk = {
             "name" : "sd_open_wpa2_zeroit_dpsk",
             "ssid" : "sd_open_wpa2_zeroit_dpsk",
             "type" : "standard-usage",
             "auth" : "PSK",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "zero_it" : "True",
             "enable_dpsk" : "True",
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    auth_server = ["local","ACTIVE_DIRECTORY","LDAP","RADIUS"]
    
    standard_open_wpa2_auth_server = auth_server[random.randrange(0,4)]
    standard_open_wpa2_webauth = {
             "name" : "sd_open_wpa2_webauth",
             "ssid" : "sd_open_wpa2_webauth",
             "type" : "standard-usage",
             "auth" : "PSK",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "web_auth" : True, 
             "auth_server" : standard_open_wpa2_auth_server,
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    standard_open_wpa2_zeroit_dpsk_webauth = {
             "name" : "sd_open_wpa2_zeroit_dpsk_webauth",
             "ssid" : "sd_open_wpa2_zeroit_dpsk_webauth",
             "type" : "standard-usage",
             "auth" : "PSK",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             #"web_auth" : True, 
             #"auth_server" : standard_open_wpa2_zeroit_dpsk_auth_server,
             "zero_it" : "True",
             "enable_dpsk" : "True",
             "enable_rbac" : "True",
             "mobile_friendly":True,
             "dvlan" : "True"}
    
    standard_open_wpamixed_auth_server = auth_server[random.randrange(0,4)]
    standard_open_wpamixed_webauth = {
             "name" : "sd_open_wpamixed_webauth",
             "ssid" : "sd_open_wpamixed_webauth",
             "type" : "standard-usage",
             "auth" : "PSK",
             "wpa_ver" : "WPA_Mixed",
             "encryption" : "AES",
             "key_string" : "12345678",
             "sta_wpa_ver" : "WPA2",
             "sta_encryption" : "AES",
#             "algorithm" : "aes",
#             "passphrase" : "1qaz2wsx",
             "web_auth" : True, 
             "auth_server" : standard_open_wpamixed_auth_server,
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    standard_open_none_auth_server = auth_server[random.randrange(0,4)]
    standard_open_none_webauth = {
             "name" : "sd_open_none_webauth",
             "ssid" : "sd_open_none_webauth",
             "type" : "standard-usage",
             "auth" : "open",
             "encryption" : "none",
             "web_auth" : True, 
             "auth_server" : standard_open_none_auth_server,
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    cfg['wlan_cfg_list'] = [standard_open_wpa2_zeroit_dpsk,
                            standard_open_wpa2_webauth,
                            standard_open_wpa2_zeroit_dpsk_webauth,
                            standard_open_wpamixed_webauth,
                            standard_open_none_webauth]
    cfg['wlan_name_list'] = ['sd_open_wpa2_zeroit_dpsk',
                             'sd_open_wpa2_webauth',
                             'sd_open_wpa2_zeroit_dpsk_webauth',
                             'sd_open_wpamixed_webauth',
                             'sd_open_none_webauth']
    
    """
        roles parameters
    """
    cfg["rate_limit"] = "0.10mbps"
    vlan_in_role_policy_vlan = "10"
    cfg["os_type_list"] = ["Windows",'others','android','blackberry','apple ios','mac os','linux','voip','gaming','printers']
    default_role = {"role_name":"Default",
                    "enable_rbac":True,
                    "rate_limit_uplink":"0.30mbps",
                    "rate_limit_downlink":"0.30mbps"}
    
    role_policy_vlan = {"role_name":"role_policy_vlan",
                        "enable_rbac" : True,
                        "allow_all_wlans":True,
                        "group_attr":"role_policy_vlan",
                        "vlan_policy":vlan_in_role_policy_vlan}
    
    os_type_list = deepcopy(cfg["os_type_list"])
    os_type_list.remove("Windows")   
    role_policy_ostype = {"role_name":"role_policy_ostype",
                          "enable_rbac" : True,
                          "allow_all_wlans":True,
                          "group_attr":"role_policy_ostype",
                          "specify_os_type":os_type_list} 
    
    role_policy_rate = {"role_name":"role_policy_rate",
                        "enable_rbac" : True,
                        "allow_all_wlans":True,
                        "group_attr":"role_policy_rate",
                        "rate_limit_uplink":cfg["rate_limit"],
                        "rate_limit_downlink":cfg["rate_limit"]}
    
    role_policy_all = {"role_name":"role_policy_all",
                        "enable_rbac" : True,
                        "group_attr":"role_policy_all",
                        "allow_all_wlans":True,
                        "vlan_policy":vlan_in_role_policy_vlan,
                        "specify_os_type":os_type_list,
                        "rate_limit_uplink":cfg["rate_limit"],
                        "rate_limit_downlink":cfg["rate_limit"]}
    
    role_policy_empty = {"role_name":"role_policy_empty",
                         "group_attr":"role_policy_empty",
                         "allow_all_wlans":True,
                         "enable_rbac" : True}
    
    cfg['roles_cfg'] = [role_policy_vlan,
                        role_policy_ostype,
                        role_policy_rate,
                        role_policy_empty,
                        role_policy_all,
                        default_role]
    cfg['roles_name_list'] = ["role_policy_vlan",
                              "role_policy_ostype",
                              "role_policy_rate",
                              "role_policy_empty"]
    
    """
        user_cfg_list
    """
    password = "1234567"
    user_role_policy_vlan = {'username': 'user_role_policy_vlan',
                             'fullname' : 'user_role_policy_vlan',
                             'password': password,
                             'role':'role_policy_vlan'}
    user_role_policy_ostype = {'username': 'user_role_policy_ostype',
                               'fullname' : 'user_role_policy_ostype', 
                               'password': password,
                               'role':'role_policy_ostype'}
    user_role_policy_rate = {'username': 'user_role_policy_rate', 
                             'fullname' : 'user_role_policy_rate',
                             'password': password,
                             'role':'role_policy_rate'}
    user_role_policy_all = {'username': 'user_role_policy_all', 
                            'fullname' : 'user_role_policy_all',
                            'password': password,
                            'role':'role_policy_all'}
    user_role_policy_empty = {'username': 'user_role_policy_empty',
                              'fullname' : 'user_role_policy_empty', 
                              'password': password,
                              'role':'role_policy_empty'}
    
    cfg['user_cfg_list'] = [user_role_policy_vlan,
                            user_role_policy_ostype,
                            user_role_policy_rate,
                            user_role_policy_all,
                            user_role_policy_empty]   
    
    """
        dpsk_conf
    """
    cfg['dpsk_conf'] = {'wlan' : None,
                        'number_of_dpsk' : 1,
                        'role' :None,
                        'vlan':""}
    
    """
        expected_station_info
    """
    sta_with_role_vlan = {'role':'role_policy_vlan',
                          'vlan':vlan_in_role_policy_vlan,
                          'status':u'Authorized'}
    sta_with_role_none = {'role':'Default',
                          'vlan':"1",
                          'status':u'Authorized'}
    sta_with_role_all = {'role':'role_policy_all',
                         'vlan':vlan_in_role_policy_vlan,
                         'status':u'Authorized'}
    sta_with_role_os_type = {'role':'role_policy_ostype',
                             'vlan':"1",
                             'status':u'Authorized'}
    sta_with_role_os_type_deny = {'role':'role_policy_ostype',
                                  'vlan':"1",
                                  'status':u'Authorized(Deny)'}
    sta_with_role_rate = {'role':'role_policy_rate',
                          'vlan':"1",
                          'status':u'Authorized'}
    sta_with_role_empty = {'role':'role_policy_empty',
                          'vlan':"1",
                          'status':u'Authorized'}
    cfg['expected_station_info_dict'] = {"role_policy_vlan" : sta_with_role_vlan,
                                         "role_policy_ostype":sta_with_role_os_type,
                                         "role_policy_ostype_deny" : sta_with_role_os_type_deny,
                                         "role_policy_rate":sta_with_role_rate,
                                         "role_policy_empty":sta_with_role_empty,
                                         "role_policy_all":sta_with_role_all,
                                         "Default": sta_with_role_none}
    
    
    """
        web_auth_user_list
    """
    local_user1 = {"username":"user_role_policy_vlan",
                   "password":"1234567",
                   "sta_tag":"sta1"}
    local_user2 = {"username":"user_role_policy_ostype",
                   "password":"1234567",
                   "sta_tag":"sta1"}
    local_user3 = {"username":"user_role_policy_rate",
                   "password":"1234567",
                   "sta_tag":"sta1"}
    local_user4 = {"username":"user_role_policy_empty",
                   "password":"1234567",
                   "sta_tag":"sta1"}
    local_user5 = {"username":"user_role_policy_all",
                   "password":"1234567",
                   "sta_tag":"sta1"}    
    
    user_list = [local_user1,local_user2,local_user3,local_user4,local_user5]
    cfg['user_to_role_dict'] = {}
    for role in cfg['roles_cfg']:
        if role["role_name"] == "Default":
            continue
        index = cfg['roles_cfg'].index(role)
        cfg['user_to_role_dict'].update({role["role_name"]:user_list[index]})
        
    """
        cfg['server_user_list']
    """
    cfg['sta_tag'] = "sta1"
    password = "1234567"
    user_role_policy_vlan = ('user_role_policy_vlan',password,False,"",None,"role_policy_vlan")
    user_role_policy_ostype = ('user_role_policy_ostype',password,False,"",None,"role_policy_ostype")
    user_role_policy_rate = ('user_role_policy_rate',password,False,"",None,"role_policy_rate")
    user_role_policy_all = ('user_role_policy_all',password,False,"",None,"role_policy_all")
    user_role_policy_empty = ('user_role_policy_empty',password,False,"",None,"role_policy_empty")   
    cfg['server_user_list'] = [user_role_policy_vlan,
                            user_role_policy_ostype,
                            user_role_policy_rate,
                            user_role_policy_all,
                            user_role_policy_empty]   
    return cfg

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]
            
    if active_ap_list != []:
        tc_dict = {'target_station':'%s' % target_sta,
                'active_ap_list': active_ap_list,
                'all_ap_mac_list': all_ap_mac_list,
                'radio_mode': target_sta_radio,
                'ap_default_vlan': '0',
                'active_ap':active_ap
                }
                  
    tcfg = define_test_parameters()
    tcfg.update(tc_dict)
    
    ts_name = 'ZD - Role Based Access Control - Stand + Open'
    ts = testsuite.get_testsuite(ts_name, 'Verify Role Based Access Control', combotest=True)
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
    