'''
Created on May 28, 2014

@author: yinwenling
'''

import sys
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
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = 'Delete users to Radius Server'
    test_cfgs.append(({'del_user': [cfg['user_vlan_override'],cfg['user_role_all']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_Device_Policy'
    common_name = 'Set Access Control Device Access Policy'
    test_cfgs.append(({'device_policy_list': cfg['device_policy_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create AAA Servers'
    test_cfgs.append(({'server_cfg_list':cfg['server_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = 'Create Default Wlans'
    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list']}, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = 'Create roles'
    test_cfgs.append(({'role_cfg_list':cfg['roles_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Multi_Users'
    common_name = 'Create Users'
    test_cfgs.append(({'user_cfg_list':cfg['user_cfg_list']}, test_name, common_name, 0, False))
    
#    test_name = 'CB_ZD_CLI_Create_Radius_User'
#    common_name = 'Create Web Users'
#    test_cfgs.append(({'user_cfg_list':cfg['user_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service on active zd'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
    
    ap_tag = "AP_02"
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable AP[%s] WLAN service in ZD CLI' % cfg['active_ap']
    test_cfgs.append(({'cfg_type': 'config','ap_tag': ap_tag,'ap_cfg': {'radio': cfg['radio_mode'], 'wlan_service': True}}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': cfg['sta_tag'], 'sta_ip_addr': cfg['target_station']}, test_name, common_name, 0, False))
    
    tc_combo_name = "Verify Role-Base Access Control With "
    cb_step = 1
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,"default_wlan",1,cb_step)
    test_cfgs.append(({'target_station': 0}, test_name, common_name, 1, False))
    cb_step += 1  
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '[%s%s]%s.%s Delete users to Radius Server' % (tc_combo_name,"default_wlan",1,cb_step)
    test_cfgs.append(({'del_user': [cfg['user_vlan_override'],cfg['user_role_all']]}, test_name, common_name, 2, False))
    cb_step += 1
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '[%s%s]%s.%s Add users to Radius Server' % (tc_combo_name,"default_wlan",1,cb_step)
    test_cfgs.append(({'add_user': [cfg['user_vlan_override']]}, test_name, common_name, 2, False))
    cb_step += 1
    
    cb_step,test_cfgs  = _verify_sta_association_wlan("default_wlan",1,cfg,test_cfgs,tc_combo_name,cb_step,"role_vlan_override")
    
    expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_vlan_override"])
    expected_station_info_copy["wlan"] = "default_wlan"
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,"default_wlan",1,cb_step)
    test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
    cb_step += 1 
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '[%s%s]%s.%s Delete users to Radius Server' % (tc_combo_name,"default_wlan",1,cb_step)
    test_cfgs.append(({'del_user': [cfg['user_vlan_override']]}, test_name, common_name, 2, False))
    cb_step += 1
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '[%s%s]%s.%s Add users to Radius Server' % (tc_combo_name,"default_wlan",1,cb_step)
    test_cfgs.append(({'add_user': [cfg['user_role_all']]}, test_name, common_name, 2, False))
    cb_step += 1
        
    for wlan_name in cfg['wlan_name_list']:
        if wlan_name == "default_wlan":
            continue
        
        cb_step = 1
        index = cfg['wlan_name_list'].index(wlan_name) + 1
        
        test_name = 'CB_Server_Add_And_Delete_Radius_Users'
        common_name = '[%s%s]%s.%s Delete users to Radius Server' % (tc_combo_name,wlan_name,index,cb_step)
        test_cfgs.append(({'del_user': [cfg['user_role_all']]}, test_name, common_name, 1, False))
        cb_step += 1
        
        test_name = 'CB_Server_Add_And_Delete_Radius_Users'
        common_name = '[%s%s]%s.%s Add users to Radius Server' % (tc_combo_name,wlan_name,index,cb_step)
        test_cfgs.append(({'add_user': [cfg['user_role_all']]}, test_name, common_name, 2, False))
        cb_step += 1
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = '[%s%s]%s.%s disconnect client' % (tc_combo_name,wlan_name,index,cb_step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 2, False))
        cb_step += 1
            
        cb_step,test_cfgs  = _verify_sta_association_wlan(wlan_name,index,cfg,test_cfgs,tc_combo_name,cb_step,"role_policy_all")
        
        expected_station_info_copy = deepcopy(cfg['expected_station_info_dict']["role_policy_all"])
        expected_station_info_copy['wlan'] = wlan_name
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = '[%s%s]%s.%s Verify Station Info' % (tc_combo_name,wlan_name,index,cb_step)
        test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': expected_station_info_copy}, test_name, common_name, 2, False))
        cb_step += 1 
        
        if wlan_name == 'rate_wlan':
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate uplink limiting' % (tc_combo_name,wlan_name,index,cb_step)
            test_cfgs.append((cfg['expect_zing_para_up'], test_name, common_name, 2, False))
            cb_step += 1
            
            test_name = 'CB_Zing_Traffic_Station_LinuxPC'
            common_name = '[%s%s]%s.%s Verify rate downlink limiting' % (tc_combo_name,wlan_name,index,cb_step)
            test_cfgs.append((cfg['expect_zing_para_down'], test_name, common_name, 2, False))
            cb_step += 1                              
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = 'Cleanup - Delete users to Radius Server'
    test_cfgs.append(({'del_user': [cfg['user_vlan_override'],cfg['user_role_all']]}, test_name, common_name, 0, True))
   
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Cleanup - Remove all Users from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Cleanup - Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
        
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
    common_name = '[%s%s]%s.%s Associate station1 to the WLAN'% (tc_combo_name,wlan_name,index,cb_step)
    test_cfgs.append(({'sta_tag': 'sta1','wlan_ssid': wlan_name}, test_name, common_name, 2, False))                      
    cb_step += 1
    
    if cfg['wlan_cfg_list'][index - 1].get("web_auth") and cfg['wlan_cfg_list'][0].get("web_auth") == True:
        web_auth_params = deepcopy(cfg['user_to_role_dict'][role_name])
        web_auth_params["sta_tag"]='sta1'
        web_auth_params['start_browser_before_auth'] = True
        web_auth_params['close_browser_after_auth'] = True
        test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
        common_name = '[%s%s]%s.%s STA perform Web Auth' % (tc_combo_name,wlan_name,index,cb_step)
        test_cfgs.append((web_auth_params, test_name, common_name, 2, False))
        cb_step += 1
    
    if flag == "true":        
        test_name = 'CB_Station_Ping_Dest_Is_Allowed'
        common_name = '[%s%s]%s.%s the station ping a target ip is allowed' % (tc_combo_name,wlan_name,index,cb_step,)
        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
        cb_step += 1
    else:
        test_name = 'CB_Station_Ping_Dest_Is_Denied'
        common_name = '[%s%s]%s.%s the station ping a target ip is denied' % (tc_combo_name,wlan_name,index,cb_step,)
        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))   
        cb_step += 1     
    return cb_step,test_cfgs

def define_test_parameters(target_sta):
    cfg = {}
    cfg['sta_tag'] = 'sta1'
    """
        expect_zing_para
    """
    cfg["rate_limit"] = '0.10mbps'
    cfg['expect_zing_para_up'] = {'sta_tag': cfg['sta_tag'],
                                  'rate_limit': cfg["rate_limit"],
                                  'margin_of_error': 0.2,
                                  'link_type': 'up'}
    cfg['expect_zing_para_down'] = {'sta_tag': cfg['sta_tag'],
                                  'rate_limit': cfg["rate_limit"],
                                  'margin_of_error': 0.2,
                                  'link_type': 'down'}
    
    """
        cfg['server_cfg_list']
    """
    cfg['server_cfg_list'] = [{'server_name': 'RADIUS',
                               'server_addr': '192.168.0.252',
                               'radius_secret': '1234567890',
                               'server_port': '1812',
                               'type'       :'radius-auth'}]
    
    """
        cfg['device_policy_list']
    """
    cfg['device_policy_list'] = [{'name':"Windows_allow",
                                  'mode':"deny"}]
    
    """
        cfg['user_vlan_override']
    """
    cfg['user_vlan_override'] = (cfg['sta_tag'],cfg['sta_tag'],True,"","0010","role_vlan_override",False)
    cfg['user_role_all'] = (cfg['sta_tag'],cfg['sta_tag'],True,"","0010","role_policy_all",False)
    
    """
       wlan_cfg_list
    """    
    default_wlan = {
             "name" : "default_wlan",
             "ssid" : "default_wlan",
             "type" : "standard-usage",
             "auth" : "mac",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "auth_server" : "RADIUS",
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    vlan_wlan = {
             "name" : "vlan_wlan",
             "ssid" : "vlan_wlan",
             "type" : "standard-usage",
             "auth" : "mac",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "auth_server" : "RADIUS",
             "vlan" : "10",
             "enable_rbac" : "True"}
    
    dvc_wlan = {
             "name" : "dvc_wlan",
             "ssid" : "dvc_wlan",
             "type" : "standard-usage",
             "auth" : "mac",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "auth_server" : "RADIUS",
             "dvcpcy_name" : "Windows_allow",
             "enable_rbac" : "True",
             "dvlan" : "True"}
    rate_wlan = {
             "name" : "rate_wlan",
             "ssid" : "rate_wlan",
             "type" : "standard-usage",
             "auth" : "mac",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "auth_server" : "RADIUS",
             "rate_limit_uplink":"0.30mbps",
             "rate_limit_downlink":"0.30mbps",
             "enable_rbac" : "True",
             "dvlan" : "True"}
    
    cfg['wlan_cfg_list'] = [default_wlan,
                            vlan_wlan,
                            dvc_wlan,
                            rate_wlan]
    cfg['wlan_name_list'] = ['default_wlan',
                             'vlan_wlan',
                             'dvc_wlan',
                             'rate_wlan']
    
    """
        roles parameters
    """
    cfg["rate_limit"] = "0.10mbps"
    role_vlan_override = {"role_name":"role_vlan_override",
                          "enable_rbac" : True,
                          "vlan_policy": "20",
                          "allow_all_wlans":True,
                          "group_attr":"role_vlan_override"}
    role_policy_all = {"role_name":"role_policy_all",
                       "group_attr" : "role_policy_all",
                        "enable_rbac" : True,
                        "vlan_policy": "20",
                        "allow_all_wlans":True,
                        "rate_limit_uplink":cfg["rate_limit"],
                        "rate_limit_downlink":cfg["rate_limit"]}
    
    cfg['roles_cfg'] = [role_vlan_override,role_policy_all]
    
    """
        user_cfg_list
    """
    password = "1234567"
    user_vlan_override = {'username': 'user_vlan_override',
                          'fullname' : 'user_vlan_override',
                          'password': password,
                          'role':'role_vlan_override'}
    user_role_policy_all = {'username': 'user_role_policy_all', 
                            'fullname' : 'user_role_policy_all',
                            'password': password,
                            'role':'role_policy_all'}
    cfg['aaa_user'] = user_vlan_override
    cfg['user_cfg_list'] = [user_role_policy_all]   
    
    """
        expected_station_info
    """
    sta_with_role_vlan = {'role':'role_vlan_override',
                          'vlan':"20",
                          'status':u'Authorized'}
    sta_with_role_all = {'role':'role_policy_all',
                         'vlan':"20",
                         'status':u'Authorized'}
    cfg['expected_station_info_dict'] = {"role_vlan_override" : sta_with_role_vlan,
                                         "role_policy_all":sta_with_role_all}
    
    
    """
        web_auth_user_list
    """
    local_user1 = {"username":"user_role_policy_all",
                   "password":"1234567",
                   "sta_tag":"sta1"}    
    local_user2 = {"username":"user_vlan_override",
                   "password":"1234567",
                   "sta_tag":"sta1"}
    cfg['user_to_role_dict'] = {role_policy_all["role_name"]: local_user1,
                                role_vlan_override['role_name']:local_user2}
        
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
                  
    tcfg = define_test_parameters(target_sta)
    tcfg.update(tc_dict)
    
    ts_name = 'ZD - Role Based Access Control - Role Policy Priority'
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
    