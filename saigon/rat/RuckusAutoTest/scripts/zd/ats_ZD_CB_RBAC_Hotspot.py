'''
Created on Jun 3, 2014

@author: yinwenling
'''

import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode'] 

    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all Users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all Hotspot Profiles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all Wlans from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    common_name = 'Set guest access authentication server'
    test_cfgs.append(({'hotspot_conf': cfg['hotspot_conf']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = 'Create Hotspot Wlans'
    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list']}, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = 'Create roles'
    test_cfgs.append(({'role_cfg_list':cfg['roles_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Multi_Users'
    common_name = 'Create Users'
    test_cfgs.append(({'user_cfg_list':cfg['user_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service on active zd'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable AP[%s] WLAN service in ZD CLI' % cfg['active_ap']
    test_cfgs.append(({'cfg_type': 'config','ap_tag': ap_tag,'ap_cfg': {'radio': cfg['radio_mode'], 'wlan_service': True}}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station']}, test_name, common_name, 0, False))
    
    tc_combo_name = "Verify Role-base access control with "
        
    for wlan_name in cfg['wlan_name_list']:
        selected_role_number = random.randrange(0,4)
        selected_role_number = 3
        selected_role_name = cfg['roles_cfg'][selected_role_number]['role_name']
        selected_role_cfg =  deepcopy(cfg['roles_cfg'][selected_role_number])
        cb_step = 1
        index = cfg['wlan_name_list'].index(wlan_name)
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 1, False))
        cb_step += 1
        
        if selected_role_name == "role_policy_ostype":
            cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,"none")
            
            test_name = 'CB_ZD_CLI_Configure_Roles'
            selected_role_cfg_copy = deepcopy(selected_role_cfg)
            selected_role_cfg_copy["specify_os_type"] = cfg['os_type_list']
            common_name = '[%s%s]%s.%s Config os type allow windows in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,selected_role_name)
            test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
            cb_step += 1
            
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name)
        
        expected_station_info_copy = deepcopy(cfg['expected_station_info_dict'][selected_role_name])
        expected_station_info_copy['wlan'] = wlan_name
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
        
        tmp_enable_wlan_list = deepcopy(cfg['wlan_name_list'])
        tmp_enable_wlan_list.remove(wlan_name)
        selected_role_cfg_copy = deepcopy(selected_role_cfg)
        selected_role_cfg_copy['specify_wlan_list'] = tmp_enable_wlan_list
        selected_role_cfg_copy['allow_all_wlans'] = False
        test_name = 'CB_ZD_CLI_Configure_Roles'
        common_name = '[%s%s]%s.%s Disable wlan %s in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,wlan_name,selected_role_name)
        test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
        cb_step += 1
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name,"none")
        
        expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["Default"])
        expected_station_info_copy['wlan'] = wlan_name
        expected_station_info_copy['status'] = 'Unauthorized'
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
        
        selected_role_cfg_copy = deepcopy(selected_role_cfg)
        selected_role_cfg_copy['specify_wlan_list'] = cfg['wlan_name_list']
        test_name = 'CB_ZD_CLI_Configure_Roles'
        common_name = '[%s%s]%s.%s Enable wlan %s in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,wlan_name,selected_role_name)
        test_cfgs.append(({'role_cfg_list': [selected_role_cfg_copy]}, test_name, common_name, 2, False))
        cb_step += 1
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,selected_role_name)
        
        expected_station_info_copy = deepcopy(cfg['expected_station_info_dict'][selected_role_name])
        expected_station_info_copy['wlan'] = wlan_name
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
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,"role_policy_all","none")
        
        expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
        expected_station_info_copy['wlan'] = wlan_name
        expected_station_info_copy['status'] = "Unauthorized"
        expected_station_info_copy['role'] = ""
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_CLI_Configure_Roles'
        cfg['roles_cfg'][4]["specify_os_type"] = cfg['os_type_list']
        common_name = '[%s%s]%s.%s Config os type allow windows in %s ' % (tc_combo_name,wlan_name,(index + 1),cb_step,selected_role_name)
        test_cfgs.append(({'role_cfg_list': [cfg['roles_cfg'][3]]}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
        cb_step += 1
        
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,"role_policy_all")        
        
        expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
        expected_station_info_copy['wlan'] = wlan_name        
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
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Cleanup - Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Cleanup - Remove all Users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Cleanup - Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Cleanup - Remove all Wlans from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Cleanup - Remove all AAA Servers from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    return test_cfgs

def _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,role_name,flag = "true"):
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s%s]%s.%s STA connect to the wlan with %s' % (tc_combo_name,wlan_name,(index + 1),cb_step,role_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': wlan_name}, test_name, common_name, 2, False))
    cb_step += 1
    
    if flag == "true" or flag == True:
        hotspot_auth_copy = deepcopy(cfg['hotspot_auth'])
        hotspot_auth_copy['username'] = cfg['user_to_role_dict'][role_name]['username']
        hotspot_auth_copy['password'] = cfg['user_to_role_dict'][role_name]['password']
        hotspot_auth_copy['start_browser_before_auth'] = True
        hotspot_auth_copy['close_browser_after_auth'] = True
        test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
        common_name = '[%s%s]%s.%s STA perform hotspot authentication' % (tc_combo_name,wlan_name,(index + 1),cb_step)
        test_cfgs.append((hotspot_auth_copy, test_name, common_name, 2, False))
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
    
    """
       wlan_cfg_list
    """    
    hotspot_wpa2 = {
             "name" : "hotspot_wpa2",
             "ssid" : "hotspot_wpa2",
             "type" : "hotspot",
             "auth" : "PSK",
             'hotspot_name':'rbac_hotspot',
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    hotspot_wpamixed = {
             "name" : "hotspot_wpamixed",
             "ssid" : "hotspot_wpamixed",
             "type" : "hotspot",
             'hotspot_name':'rbac_hotspot',
             "auth" : "PSK",
             "wpa_ver" : "WPA_Mixed",
             "sta_wpa_ver" : "WPA2",
             "sta_encryption" : "AES",
             "encryption" : "AES",
             "key_string" : "12345678",
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    hotspot_none = {
             "name" : "hotspot_none",
             "ssid" : "hotspot_none",
             "type" : "hotspot",
             "auth" : "open",
             "encryption" : "none",
             'hotspot_name':'rbac_hotspot',
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    cfg['wlan_cfg_list'] = [hotspot_wpa2,
                            hotspot_wpamixed,
                            hotspot_none]
    cfg['wlan_name_list'] = ['hotspot_wpa2',
                             'hotspot_wpamixed',
                             'hotspot_none']
    
    """
        roles parameters
    """
    cfg["rate_limit"] = "0.10mbps"
    vlan_in_role_policy_vlan = "10"
    cfg["os_type_list"] = ['Windows','windows mobile','others','android','blackberry','apple ios','mac os','linux','voip','gaming','printers']
    role_policy_vlan = {"role_name":"role_policy_vlan",
                        "enable_rbac" : True,
                        "allow_all_wlans":True,
                        "vlan_policy":"vlan_in_role_policy_vlan"}
    
    os_type_list = deepcopy(cfg["os_type_list"])
    os_type_list.remove("Windows")   
    role_policy_ostype = {"role_name":"role_policy_ostype",
                          "enable_rbac" : True,
                          "allow_all_wlans":True,
                          "specify_os_type":os_type_list} 
    
    role_policy_rate = {"role_name":"role_policy_rate",
                        "enable_rbac" : True,
                        "allow_all_wlans":True,
                        "rate_limit_uplink":cfg["rate_limit"],
                        "rate_limit_downlink":cfg["rate_limit"]}
    
    os_type_list = deepcopy(cfg["os_type_list"])
    os_type_list.remove("Windows")
    role_policy_all = {"role_name":"role_policy_all",
                        "enable_rbac" : True,
                        "allow_all_wlans":True,
                        "vlan_policy":vlan_in_role_policy_vlan,
                        "specify_os_type":os_type_list,
                        "rate_limit_uplink":cfg["rate_limit"],
                        "rate_limit_downlink":cfg["rate_limit"]}
    
    role_policy_empty = {"role_name":"role_policy_empty",
                         "enable_rbac" : True,
                         "allow_all_wlans":True,}
    role_policy_default = {"role_name":"Default",
                           "enable_rbac":True,
                           "guest_pass_gen" : True,
                           "rate_limit_uplink":"0.30mbps",
                           "rate_limit_downlink":"0.30mbps"}
    
    cfg['roles_cfg'] = [role_policy_vlan,
                    role_policy_ostype,
                    role_policy_rate,
                    role_policy_empty,
                    role_policy_all,
                    role_policy_default]
    
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
                            user_role_policy_empty,
                            user_role_policy_all]   
    
    """
    cfg['hotspot_conf']
    """
    cfg['hotspot_conf'] = {'login_page': 'http://192.168.0.250/login.html',
                           'name': 'rbac_hotspot',
                           #'auth_svr': 'Local Database',
                           'idle_timeout': None}
    
    """
        expected_station_info
    """
    sta_with_role_vlan = {'role':'role_policy_vlan',
                          'vlan':"1",
                          'status':u'Authorized'}
    sta_with_role_none = {'vlan':"1",
                          'status':u'Authorized'}
    sta_with_role_all = {'role':'role_policy_all',
                         'vlan':"1",
                         'status':u'Authorized'}
    sta_with_role_os_type = {'role':'role_policy_ostype',
                             'vlan':"1",
                             'status':u'Authorized'}
    sta_with_role_rate = {'role':'role_policy_rate',
                          'vlan':"1",
                          'status':u'Authorized'}
    sta_with_role_empty = {'role':'role_policy_empty',
                          'vlan':"1",
                          'status':u'Authorized'}
    cfg['expected_station_info_dict'] = {"role_policy_vlan" : sta_with_role_vlan,
                                         "role_policy_ostype":sta_with_role_os_type,
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
    local_user4 = {"username":"user_role_policy_all",
                   "password":"1234567",
                   "sta_tag":"sta1"}    
    local_user5 = {"username":"user_role_policy_empty",
                   "password":"1234567",
                   "sta_tag":"sta1"}
    user_list = [local_user1,local_user2,local_user3,local_user5,local_user4]
    cfg['user_to_role_dict'] = {}
    for role in cfg['roles_cfg']:
        if role['role_name'] == "Default":
            continue
        index = cfg['roles_cfg'].index(role)
        cfg['user_to_role_dict'].update({role["role_name"]:user_list[index]})
    
    """
        cfg['hotspot_auth']
    """ 
    cfg['hotspot_auth'] = {'sta_tag': "sta1",
                           'username': None,
                           'password': None,
                           'expected_data':"It works!",
                           'start_browser_before_auth': True,
                           'close_browser_after_auth': True}   
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
    
    ts_name = 'ZD - Role Based Access Control - Hotspot'
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
    