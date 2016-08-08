'''
Created on Oct 10, 2014

@author: lab
'''
import sys
import copy
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

    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = 'Set AP system name to RuckusAP'
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg':{ 'device_name': 'RuckusAP', }
                     }, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_CLI_Set_All_AP_LLDP'
    common_name = 'Disable all ap lldp'
    test_cfgs.append(({
                       'lldp_cfg': {'state': 'disable','disable_ports': 'all'}
                     }, test_name, common_name, 0, False))

    test_name = 'CB_Switch_Set_LLDP'
    common_name = 'Enable LLDP in Switch'
    test_cfgs.append(({'state':'enable','mgmt_ip':'192.168.0.253'}, test_name, common_name, 0, False))

################## Test Case 1 ####################################

    case_name = '[enable_disable_ap_lldp]'
    
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sDisable ap lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 1, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify AP does not exist in LLDP neighbor'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'negative': True,
                     }, test_name, common_name, 2, False))

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

    case_name = '[disable_and_enable_ap_active_port]'

    lldp_cfg = copy.deepcopy(default_lldp_cfg)
    lldp_cfg.pop('enable_ports')
    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sDisable ap lldp in active port'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'disable_ports':'active_port'},
                     }, test_name, common_name, 1, False))    

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable ap lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': lldp_cfg,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp state is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify AP does not exist in LLDP neighbor'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'negative': True,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sEnable ap lldp in active port'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'enable_ports':'active_port'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in AP'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))    

################## Test Case 3 ####################################

    case_name = '[change_ap_sys_name]'   
    
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

    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = '%sChange AP system name'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg':{ 'device_name': 'test_lldp', }
                     }, test_name, common_name, 2, False))    

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify system info is changed'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_neighbor':{'system_name':'test_lldp'}
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = '%sRecover AP system name'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg':{ 'device_name': 'RuckusAP', }
                     }, test_name, common_name, 2, True))    

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify system info is recovered'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, True))

################## Test Case 4 ####################################

    case_name = '[enable_disable_ap_mgmt]'   
    
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

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting mgmt to disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp mgmt is disabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'disable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify there is no mgmt info in Switch neighbor'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'verify_mgmt':False,
                     }, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSetting mgmt to enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = '%sVerify ap lldp mgmt is enabled'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'mgmt':'enable'},
                     }, test_name, common_name, 2, False))

    test_name = 'CB_Switch_Verify_LLDP_Neighbor'
    common_name = '%sVerify LLDP neighbor in Switch again'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                     }, test_name, common_name, 2, False))

################## Clean UP ####################################

    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = 'Set AP system name to RuckusAP after test'
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ap_cfg':{ 'device_name': 'RuckusAP', }
                     }, test_name, common_name, 0, True))  

    test_name = 'CB_ZD_CLI_Set_All_AP_LLDP'
    common_name = 'Set all ap lldp state to disabled'
    test_cfgs.append(({
                       'lldp_cfg': {'state': 'disable','disable_ports': 'all'},
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
        ts_name = "LLDP_Basic_Function"

    ts = testsuite.get_testsuite(ts_name, "LLDP_Basic_Function" , combotest=True)

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