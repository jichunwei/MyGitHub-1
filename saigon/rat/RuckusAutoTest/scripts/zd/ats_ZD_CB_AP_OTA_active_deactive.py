'''
Created on May 13, 2014

@author: yinwenling
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    
    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = 'Configure ZD Access Point Policies'
    test_cfgs.append(({'auto_approve':False}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Remove_AP'
    common_name = 'Remove AP from zd ap list'
    test_cfgs.append(({'ap_mac_list':cfg['all_ap_mac_list']}, test_name, common_name, 0, False))
    
    ap1_tag = "AP_01"
    ap2_tag = 'AP_02'
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP_01'
    test_cfgs.append(({'active_ap': ap1_tag,
                       'ap_tag': ap1_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP_02'
    test_cfgs.append(({'active_ap': ap2_tag,
                       'ap_tag': ap2_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_AP_SHELL_Get_Config_Wlan_Psk'
    common_name = 'Get Psk for the AP2 via AP1.'
    test_cfgs.append(({'ap_tag':ap1_tag,'get_psk_ap':ap2_tag}, test_name, common_name, 0, False))
           
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station']}, test_name, common_name, 0, False))
    
    tc_combo_name = "Verify deactive/active config-wlan via wired port"
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]1.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.2 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'wait_time':10,'force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.3 Disable config-wlan in cli via wired port' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'set state wlan102 down','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.4 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'check_wlan_exist':True,'is_negative':True,'sta_tag': 'sta1', 'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.5 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.6 Enable config-wlan in cli via wired port' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'set state wlan102 up','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.7 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'up','force_ssh':True}, test_name, common_name, 2, False))
    
    #ap2_config_wlan = "island-%s" % ap2_mac.replace('-','').replace(':','')[6:].upper()
    #cfg['wlan_cfg']['name'] = ap2_config_wlan
    #cfg['wlan_cfg']['ssid'] = ap2_config_wlan
    #test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    #common_name = '[%s]1.8 STA connect to the wlan.' % tc_combo_name
    #test_cfgs.append(({'sta_tag': 'sta1',"auth_deny":True, 'config_wlan_ap':ap2_tag, 'wlan_ssid': ap2_config_wlan,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
         
    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.9 Disable config-wlan in shell' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'wrad_cli goto -','force_ssh':True,'cmd_pmt':'shell','expect_value':'current state=-'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.10 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'check_wlan_exist':True,'is_negative':True,'config_wlan_ap':ap2_tag,'sta_tag': 'sta1','wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]1.11 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]1.12 Enable config-wlan in shell' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'cmd_text':'wrad_cli goto P','force_ssh':True,'cmd_pmt':'shell','expect_value':'current state=P'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.13 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True,'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
         
    tc_combo_name = "Verify deactive config-wlan after OTA-Conf-Reboot"
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]2.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]2.2 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True, 'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
         
    test_name = 'CB_Station_AP_Exec_Command'
    common_name = '[%s]2.3 Create and enable a service wlan through CLI via config-wlan' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','ap_cfg':{'cmd_text' : "set ssid wlan0 new_test_ssid_898",'ip_addr':'169.254.1.1', 'port' : 22,'username' : 'super','password' : 'sp-admin'}}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]2.4 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'up','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Reboot_All_AP'
    common_name = '[%s]2.5 Reboot AP' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]2.6 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'check_wlan_exist':True,'is_negative':True,'config_wlan_ap':ap2_tag,'sta_tag': 'sta1','wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]2.7 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))
    
    tc_combo_name = "Verify deactive config-wlan after OTA-Conf-Disconnect"
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]3.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]3.2 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True,'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_AP_Exec_Command'
    common_name = '[%s]3.3 Set AP2 an director ip via cli on station' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','ap_cfg':{'cmd_text' : "set director ip 192.18.0.2",'ip_addr':'169.254.1.1', 'port' : 22,'username' : 'super','password' : 'sp-admin'}}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]3.4 Check the config-wlan status(up)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'up','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]3.5 Disconnect from config-wlan' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]3.6 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))
    
    tc_combo_name = "Verify deactive config-wlan after Non-OTA-Conf"
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]4.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_CLI_Exec_Cmd'
    common_name = '[%s]4.2 Set director ip via wired port' % tc_combo_name
    test_cfgs.append(({'cmd_text' : "set director ip 192.18.0.2",'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_CLI_Check_Wlan_Status'
    common_name = '[%s]4.3 Check the config-wlan status(down)' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'expect_status':'down','force_ssh':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = 'Cleanup - Configure ZD Access Point Policies'
    test_cfgs.append(({'auto_approve':True}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = 'Cleanup - Set AP2 default factory.'
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Wait_AP_Connect'
    common_name = 'Cleanup -  Check AP2 join ZD.'
    test_cfgs.append(({'ap_tag': ap2_tag}, test_name, common_name, 0, True))
    return test_cfgs

def define_test_parameters():
    cfg = {}
    
    
    """
       wlan_cfg_list
    """    
    cfg['wlan_cfg'] = {
             "name" : '',
             "ssid" : '',
             "type" : "standard-usage",
             "auth" : "PSK",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : ''}
    
    
    
    """
        expected_station_info
    """
    cfg['expected_station_info'] = {'status':u'Authorized'}


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
                'active_ap':active_ap
                }
                  
    tcfg = define_test_parameters()
    tcfg.update(tc_dict)
    
    ts_name = 'AP OTA - Active Deactive Config-Wlan'
    ts = testsuite.get_testsuite(ts_name, 'Verify AP OTA', combotest=True)
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
    