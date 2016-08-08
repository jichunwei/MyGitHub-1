'''
Created on May 28, 2014

@author: yinwenling
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []

    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD before test'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs on ZD1'
    test_cfgs.append(({'zdcli_tag':'zdcli1'}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs on ZD2'
    test_cfgs.append(({'zdcli_tag':'zdcli2'}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA Servers from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({'zd1':'zd1','zd2':'zd2'},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create AAA Servers'
    test_cfgs.append(({'server_cfg_list':cfg['server_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = 'Create  Wlans'
    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list'],'zd_tag': 'active_zd'}, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = 'Create roles'
    test_cfgs.append(({'role_cfg_list':cfg['roles_cfg'],'zd_tag': 'active_zd'}, test_name, common_name, 0, False))
       
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service on active zd'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
    
    ap_tag = "aptag"
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
    
    tc_combo_name = "Verify Role-Base Access Control with SR"
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[%s]1.1 disconnect client' % (tc_combo_name)
    test_cfgs.append(({'target_station': 0}, test_name, common_name, 1, False)) 
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '[%s]1.2 Delete users from Radius Server' % (tc_combo_name)
    test_cfgs.append(({'del_user': [cfg['user_role_all']]}, test_name, common_name, 2, False))
    
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '[%s]1.3 Add users to Radius Server' % (tc_combo_name)
    test_cfgs.append(({'add_user': [cfg['user_role_all']]}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.4 STA connect to the wlan with role_policy_all' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': "default_wlan"}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]1.4 Verify Station Info' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': cfg['expected_station_info_dict']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]1.5 Remove all WlANs from station' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Failover'
    common_name = '[%s]1.6 Failover the active ZD' % (tc_combo_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.7 STA connect to the wlan with role_policy_all' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': "default_wlan"}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]1.8 Verify Station Info' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': cfg['expected_station_info_dict']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]1.9 Remove all WlANs from station' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Failover'
    common_name = '[%s]1.10 Failover the active ZD' % (tc_combo_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.10 STA connect to the wlan with role_policy_all' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': "default_wlan"}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]1.11 Verify Station Info' % (tc_combo_name)
    test_cfgs.append(({'sta_tag': 'sta1','expected_station_info': cfg['expected_station_info_dict']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Cleanup - Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown', 'zd_tag': 'active_zd'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Cleanup - Remove all AAA Servers from ZD'
    test_cfgs.append(({'zd_tag': 'active_zd'}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Cleanup - Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Cleanup - Remove all Wlans from ZD'
    test_cfgs.append(({'zd_tag': 'active_zd'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Cleanup - Disable Smart Redundancy on both ZD after test'
    test_cfgs.append(({},test_name, common_name, 0, True))
    
    return test_cfgs

def define_test_parameters():
    cfg = {}  
    cfg['sta_tag'] = 'sta1'
    """
        cfg['target_station']
    """ 
    cfg['target_station'] = "192.168.1.11"
    
    """
        cfg['user_role_all']
    """
    cfg['user_role_all'] = (cfg['sta_tag'],cfg['sta_tag'],True,"","","role_policy_all")
    
    """
        cfg['server_cfg_list']
    """
    cfg['server_cfg_list'] = [{'server_name': 'RADIUS',
                               'server_addr': '192.168.0.252',
                               'radius_secret': '1234567890',
                               'server_port': '1812',
                               'type'       :'radius-auth'}]
    
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
    
    cfg['wlan_cfg_list'] = [default_wlan]

    """
        roles parameters
    """
    cfg["rate_limit"] = "0.10mbps"
    cfg["os_type_list"] = ['Windows','others','android','blackberry','apple ios','mac os','linux','voip','gaming','printers']
    role_policy_all = {"role_name":"role_policy_all",
                       "group_attr" : "role_policy_all",
                        "enable_rbac" : True,
                        "vlan_policy": "10",
                        "allow_all_wlans":True,
                        "specify_os_type":cfg["os_type_list"],
                        "rate_limit_uplink":cfg["rate_limit"],
                        "rate_limit_downlink":cfg["rate_limit"]}
    
    cfg['roles_cfg'] = [role_policy_all] 
    
    """
        expected_station_info
    """
    cfg['expected_station_info_dict'] = {'role':'role_policy_all',
                                         'vlan':"10",
                                         'status':u'Authorized',
                                         'wlan':'default_wlan'}       
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
                'radio_mode': target_sta_radio,
                'ap_default_vlan': '0',
                'active_ap':active_ap
                }  
                  
    tcfg = define_test_parameters()
    tcfg.update(tc_dict)
    
    ts_name = 'ZD - Role Based Access Control - SR'
    ts = testsuite.get_testsuite(ts_name, 'Verify Role-base Access Control With SR', combotest=True)
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
    