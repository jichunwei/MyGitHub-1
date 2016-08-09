'''
Created on Oct 10, 2014

@author: lab
'''
import copy
import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg):
    test_cfgs = []
    default_lldp_cfg = {'state':'enable',
                        'interval':'30',
                        'holdtime':'120',
                        'enable_ports':'active_port',
                        'mgmt':'enable'}

################## Start ####################################

    ap_tag = 'AP_01'
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':tcfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Set_All_AP_LLDP'
    common_name = 'Disable all ap lldp'
    test_cfgs.append(({
                       'lldp_cfg': {'state': 'disable','disable_ports': 'all'}
                     }, test_name, common_name, 0, False))

    test_name = 'CB_Switch_Set_LLDP'
    common_name = 'Enable LLDP in Switch'
    test_cfgs.append(({'state':'enable','mgmt_ip':'192.168.0.253'}, test_name, common_name, 0, False))

################## Test Case 1 ####################################

    case_name = '[restart_lldp]'

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable and disable ap lldp repeatedly'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'robust_test':True
                     }, test_name, common_name, 1, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable ap lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': default_lldp_cfg,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

################## Test Case 2 ####################################   
    case_name = '[reboot_ap]'

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable ap lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': default_lldp_cfg,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Reboot_All_AP'
    common_name = '%sReboot all AP' % case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sVerify AP status changed to connected' %case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected'}, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP after reboot'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch after reboot'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

################## Test Case 3 ####################################

    case_name = '[reset_ap]'   
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable ap lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': default_lldp_cfg,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_AP_Set_Factory_Default'
    common_name = '%sSet AP to factory default' % case_name
    test_params = {'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sVerify AP status changed to connected' %case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected'}, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP after reset'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch after reset'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

################## Test Case 4 ####################################

    case_name = '[reboot_zd]'

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable ap lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': default_lldp_cfg,
                     }, test_name, common_name, 1, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%sReboot zd from zdcli'% case_name
    test_cfgs.append(( {'timeout':10*60}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sVerify AP status changed to connected' %case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected'}, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP after zd reboot'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch after zd reboot'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

################## Clean UP ####################################

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = 'Setting state to disabled'
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 0, True))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = 'Verify ap lldp state is disabled'
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 0, True))

    test_name = 'CB_Switch_Set_LLDP'
    common_name = 'Disable LLDP in Switch'
    test_cfgs.append(({'state':'disable'}, test_name, common_name, 0, True))
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
        ts_name = "LLDP_Robust_Test"

    ts = testsuite.get_testsuite(ts_name, "LLDP_Robust_Test" , combotest=True)

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