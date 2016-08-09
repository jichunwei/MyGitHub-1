"""
Author: Louis Lou
Email: louis.lou@ruckuswireless.com
"""

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(cfg):
    test_cfgs = []
    
    aaa_config_list = cfg['aaa_config_list']
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '2.Create the authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':aaa_config_list}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_L2_ACLs'
    common_name = '3.Create 2 L2 ACLs via GUI'
    param_cfg = dict(num_of_acl_entries = 2,num_of_mac = 1)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_L3_ACLs'
    common_name = '4.Create 2 L3 ACLs via GUI'
    param_cfg = dict(num_of_acls = 2,num_of_rules = 1)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlans_Config'
    common_name = 'Init WLANs configurations'
    test_cfgs.append(({'auth_server':aaa_config_list[0]['server_name'],
                       'acct_server':aaa_config_list[1]['server_name']},
                      test_name, common_name, 0, False))

    test_case_name = '[Create Wlans]'
    
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = '%sCreate 28 wlans on ZD via CLI' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Get_All_Wlan'
    common_name = '%sGet ZD All Wlans Info via CLI' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_All_Wlan_Info_Between_Set_Get'
    common_name = '%sVerify All Wlans Info Between CLI Set and CLI Get' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_All_Wlans_Info'
    common_name = '%sGet All Wlans Info via GUI' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_All_Wlan_Info_Between_CLISet_GUIGet'
    common_name = '%sVerify All Wlans Info Between CLI Set and GUI Get' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_case_name = '[Edit Wlans]'
    
    test_name = 'CB_ZD_CLI_Edit_Wlan'
    common_name = '%sSelect one wlan form wlan list, edit it' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
    common_name = '%sGet ZD Wlans Info via CLI' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get'
    common_name = '%sVerify Wlans Info Between CLI Set and CLI Get' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Wlans_Info'
    common_name = '%sGet All Wlans Info via GUI' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_CLISet_GUIGet'
    common_name = '%sVerify Wlans Info Between CLI Get and GUI Get' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_case_name = '[Delete Wlans Configuration]'
    
    test_name = 'CB_ZD_CLI_Remove_Wlan_Configuration'
    common_name = '%sEdit the wlan - Remove the configuration' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
    common_name = '%sGet the Wlan configuration via ZD CLI' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_No_Wlan_Configuration'
    common_name = '%sVerify there is no configuration' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_case_name = '[Delete All Wlans]'
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sDelete all wlans' % test_case_name
    test_cfgs.append(( {}, test_name, common_name, 0, True))
    
    #Clean up.
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans on ZD'
    test_cfgs.append(( {}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, True))
            
    return test_cfgs

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)    
    ras_cfg = dict(server_addr = ras_ip_addr,
               server_port = '1812',
               server_name = 'rat-radius',
               radius_auth_secret = '1234567890'
               )
    acc_cfg = dict(server_addr = ras_ip_addr,
               server_port = '1812',
               server_name = 'rat-accounting',
               radius_acct_secret = '1234567890')
    aaa_config_list = [ras_cfg,acc_cfg]
    
    tcfg = {'aaa_config_list': aaa_config_list,}
    
    ts_name = 'ZD CLI WLAN Configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs Wlan Configuration: CLI Set, GUI Get', combotest=True)
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
    createTestSuite(**_dict)
    