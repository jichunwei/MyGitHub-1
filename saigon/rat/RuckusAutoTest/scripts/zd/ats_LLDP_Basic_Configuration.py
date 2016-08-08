'''
Created on Oct 8, 2014

@author: chen.tao
'''

import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []

    ap_tag = 'AP_01'
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':tcfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

################## Test Case 1 ####################################

    #lldp interval
    case_name = '[set_ap_lldp_interval]'
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp interval to 0 should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '0'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp interval to 301 should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '301'},
                       'negative':True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp interval to 20 should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '20'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp interval is 20'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '20'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp interval to default value 30'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '30'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp interval is 30'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '30'},
                     }, test_name, common_name, 2, True))

################## Test Case 2 ####################################

    #lldp holdtime
    case_name = '[Set_ap_lldp_holdtime]'
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp holdtime to 59 should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '59'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp holdtime to 1201 should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '1201'},
                       'negative':True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp holdtime to 130 should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '130'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp holdtime is 130'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '130'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp holdtime to default value 120'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '120'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp holdtime is 120'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '120'},
                     }, test_name, common_name, 2, True))

################## Test Case 3 ####################################

    #holdtime > interval
    case_name = '[AP_interval_bigger_than_holdtime]'
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting interval bigger than holdtime should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval':'61','holdtime': '60'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting ap lldp interval and holdtime to default value'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '30','holdtime': '120'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp interval and holdtime are using default value'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '30','holdtime': '120'},
                     }, test_name, common_name, 2, True))

################## Test Case 4 ####################################

    #lldp interface
    case_name = '[Set_ap_lldp_port]'
    
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sDisable lldp in an invalid port should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'disable_ports':['6']},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable lldp in an invalid port should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'enable_ports':['6']},
                       'negative':True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sDisable lldp in port 0 should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'disable_ports':['0']},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify lldp is disabled on port 0'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'disable_ports':['0']},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable lldp in port 0 should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'enable_ports':['0']},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify lldp is enabled on port 0'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'enable_ports':['0']},
                     }, test_name, common_name, 2, True))

################## Test Case 5 ####################################

    #mgmt
    case_name = '[Set_ap_lldp_mgmt]'
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting mgmt to True should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'True'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting mgmt to disabled should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp mgmt is disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting mgmt to enabled should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp mgmt is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'enable'},
                     }, test_name, common_name, 2, True))

################## Test Case 6 ####################################

    #state
    case_name = '[Set_ap_lldp_state]'
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting state to True should fail'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'True'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting state to disabled should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting state to enabled should succeed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, True))

################## Test Case 7 ####################################

    #ap group lldp interval
    case_name = '[set_ap_group_lldp_interval]'
    group_name = "System Default"
    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp interval to 0 should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'interval': '0'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp interval to 301 should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'interval': '301'},
                       'negative':True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet AP to use AP group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp interval to 20 should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'interval': '20'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp interval is 20'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '20'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp interval to default value 30'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'interval': '30'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp interval is 30'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '30'},
                     }, test_name, common_name, 2, True))

################## Test Case 8 ####################################

    #ap group lldp  holdtime
    case_name = '[Set_ap_group_lldp_holdtime]'
    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp holdtime to 59 should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'holdtime': '59'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp holdtime to 1201 should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'holdtime': '1201'},
                       'negative':True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet AP to use AP group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp holdtime to 130 should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'holdtime': '130'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp holdtime is 130'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '130'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp holdtime to default value 120'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'holdtime': '120'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp holdtime is 120'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'holdtime': '120'},
                     }, test_name, common_name, 2, True))

################## Test Case 9 ####################################

    #ap group lldp holdtime > interval
    case_name = '[AP_Group_interval_bigger_than_holdtime]'
    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting interval bigger than holdtime should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'interval':'61','holdtime': '60'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet AP to use AP group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting ap group lldp interval and holdtime to default value'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'interval': '30','holdtime': '120'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp interval and holdtime are using default value'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'interval': '30','holdtime': '120'},
                     }, test_name, common_name, 2, True))

################## Test Case 10 ####################################

    #ap group lldp  interface
    case_name = '[Set_ap_group_lldp_port]'

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sDisable lldp in an invalid port should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'disable_ports':['6']},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sEnable lldp in an invalid port should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'enable_ports':['6']},
                       'negative':True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet AP to use AP group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sDisable lldp in port 0 should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'disable_ports':['0']},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify lldp is disabled on port 0'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'disable_ports':['0']},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sEnable lldp in port 0 should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'enable_ports':['0']},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify lldp is enabled on port 0'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'enable_ports':['0']},
                     }, test_name, common_name, 2, True))

################## Test Case 11 ####################################

    #ap group lldp mgmt
    case_name = '[Set_ap_group_lldp_mgmt]'
    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting mgmt to True should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'mgmt':'True'},
                       'negative':True,
                     }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet AP to use AP group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting mgmt to disabled should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'mgmt':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp mgmt is disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting mgmt to enabled should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'mgmt':'enable'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp mgmt is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'enable'},
                     }, test_name, common_name, 2, True))

################## Test Case 12 ####################################

    #ap group lldp state
    case_name = '[Set_ap_group_lldp_state]'
    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting state to True should fail'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'state':'True'},
                       'negative':True,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet AP to use AP group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting state to disabled should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = '%sSetting state to enabled should succeed'%case_name
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, True))
    return test_cfgs

def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]

    tcfg = {
            'active_ap':active_ap
            }
    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "LLDP_Basic_Configuration"

    ts = testsuite.get_testsuite(ts_name, "LLDP_Basic_Configuration" , combotest=True)

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