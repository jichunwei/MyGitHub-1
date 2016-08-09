'''
Created on May 13, 2014

@author: yinwenling
'''
import sys
from copy import deepcopy

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
           
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station']}, test_name, common_name, 0, False))
    
    test_name = 'CB_AP_SHELL_Get_Config_Wlan_Psk'
    common_name = 'Get Psk for the AP2 via AP1.'
    test_cfgs.append(({'ap_tag':ap1_tag,'get_psk_ap':ap2_tag}, test_name, common_name, 1, False))
    
    tc_combo_name = "Verify Configure AP by Config-wlan"
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = '[%s]1.1 Set AP2 default factory.' % tc_combo_name
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '[%s]1.2 STA connect to the wlan.' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','auth_deny':True, 'config_wlan_ap':ap2_tag,'wlan_cfg':cfg['wlan_cfg']}, test_name, common_name, 2, False))
                     
    cmd_text = "set messh mesh\n set meshcfg ssid Mesh-431103001644\n set meshcfg passphrase rX4tnoegeXtYx1Mi4WCVCUjaLhaJBwwaJ0oPgEzEpSDTWbCkmoqpXWWZhWrTUld\nset director ip 192.18.0.2\n"
    ap_cfg = deepcopy(cfg['ap_cfg'])
    ap_cfg['cmd_text'] = cmd_text
    test_name = 'CB_Station_AP_Exec_Command'
    common_name = '[%s]1.3 Set mesh setting which is same as on ZD' % tc_combo_name
    test_cfgs.append(({'sta_tag': 'sta1','ap_cfg':ap_cfg}, test_name, common_name, 2, False))                 
    
    test_name = 'CB_ZD_AP_Set_Factory_By_MAC'
    common_name = 'Cleanup - Set AP2 default factory.'
    test_cfgs.append(({'ap_tag':ap2_tag,'force_ssh':True}, test_name, common_name, 0, True))    
    
    test_name = 'CB_ZDCLI_Config_AP_Policy'
    common_name = 'Cleanup - Configure ZD Access Point Policies'
    test_cfgs.append(({'auto_approve':True}, test_name, common_name, 0, True))
    
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
             "key_string" : '',}
    
    '''
        ap_cfg
    '''
    cfg['ap_cfg'] = {'ip_addr':'169.254.1.1', 
                     'port' : 22, 
                     'username' : 'super', 
                     'password' : 'sp-admin',
                     'cmd_text' : ''}


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
    active_ap = active_ap_list
            
    if active_ap_list != []:
        tc_dict = {'target_station':'%s' % target_sta,
                'active_ap_list': active_ap_list,
                'all_ap_mac_list': all_ap_mac_list,
                'radio_mode': target_sta_radio,
                'active_ap':active_ap
                }
                  
    tcfg = define_test_parameters()
    tcfg.update(tc_dict)
    
    ts_name = 'AP OTA - Combination Function'
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
    