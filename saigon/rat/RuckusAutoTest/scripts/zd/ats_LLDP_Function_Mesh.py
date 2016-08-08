"""
Created on Oct 15, 2014

@author: chen.tao@odc-ruckuswireless.com
"""
import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []

    default_lldp_cfg = {'state':'enable',
                        'interval':'30',
                        'holdtime':'120',
                        'enable_ports':['1','2','3','4','5'],
                        'mgmt':'enable'}

################## Start ####################################
    #@author: Tan added
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to clear configuration'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = 'Enable mesh in ZD'
    test_cfgs.append(({'for_upgrade_test': False},test_name, common_name, 0, False))
    

    test_name = 'CB_ZD_CLI_Set_All_AP_LLDP'
    common_name = 'Disable all ap lldp'
    test_cfgs.append(({
                       'lldp_cfg': {'state': 'disable','disable_ports': 'all'}
                     }, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create Root AP'
    test_cfgs.append(({'active_ap':cfg['active_ap1'],
                       'ap_tag': 'AP_01'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create Mesh AP'
    test_cfgs.append(({'active_ap':cfg['active_ap2'],
                       'ap_tag': 'AP_02'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create eMesh AP'
    test_cfgs.append(({'active_ap':cfg['active_ap3'],
                       'ap_tag': 'AP_03'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Setting up emesh topo'
    test_cfgs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_02',
                       'emesh_ap': ['AP_03'],
                       'test_option': 'form_emesh_mesh_acl'}, test_name, common_name, 0, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = 'Verify root ap lldp state is disabled'
    test_cfgs.append(({'ap_tag': 'AP_01',
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 0, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = 'Verify mesh ap lldp state is disabled'
    test_cfgs.append(({'ap_tag': 'AP_01',
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 0, False))

    test_name = 'CB_AP_Verify_LLDP_Config'
    common_name = 'Verify emesh ap lldp state is disabled'
    test_cfgs.append(({'ap_tag': 'AP_01',
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 0, False))

    test_name = 'CB_Switch_Set_LLDP'
    common_name = 'Enable LLDP in Switch'
    test_cfgs.append(({'state':'enable','mgmt_ip':'192.168.0.253'}, test_name, common_name, 0, False))

    group_name = "System Default"

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = 'Enable lldp in AP group'
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': default_lldp_cfg,
                     }, test_name, common_name, 0, False))

################## Test Case 1 ####################################

    case_name = '[lldp_in_root_ap]'
    ap_tag = 'AP_01'

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet root ap to use group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True}
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
    common_name = '%sSet root ap to disable lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state': 'disable'}
                     }, test_name, common_name, 2, True))    

################## Test Case 2 ####################################

    case_name = '[lldp_in_mesh_ap]'
    ap_tag = 'AP_02'

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet mesh ap to use group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True}
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
    common_name = '%sSet mesh ap to disable lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state': 'disable'}
                     }, test_name, common_name, 2, True))   

################## Test Case 3 ####################################

    case_name = '[lldp_in_emesh_ap]'
    ap_tag = 'AP_03'

    test_name = 'CB_ZD_CLI_Set_AP_LLDP'
    common_name = '%sSet emesh ap to use group lldp config'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'use_group_settings': True}
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
    common_name = '%sSet emesh ap to disable lldp'%case_name
    test_cfgs.append(({'ap_tag': ap_tag,
                       'lldp_cfg': {'state': 'disable'}
                     }, test_name, common_name, 2, True))   

################## Clean UP ####################################

    test_name = 'CB_ZD_CLI_Set_AP_Group_LLDP'
    common_name = 'Disable lldp in AP group'
    test_cfgs.append(({'name': group_name,
                       'lldp_cfg': {'state':'disable'},
                     }, test_name, common_name, 0, True))

    test_name = 'CB_Switch_Set_LLDP'
    common_name = 'Disable LLDP in Switch'
    test_cfgs.append(({'state':'disable'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = 'Reconnect all active APs as Root'
    test_params = {'ap_list': ['AP_01', 'AP_02','AP_03'],
                       'test_option': 'reconnect_as_root'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    #@author: Tan added
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'ZD set Factory to disable mesh'
    test_cfgs.append(({},test_name, common_name, 0, False))

    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_duplicated_common_name(test_cfgs):
    common_name_list = []
    duplicate_flag = False
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if common_name in common_name_list:
            duplicate_flag = False
            print '####################'
            print common_name
            print '####################'
        else:
            common_name_list.append(common_name)
    return duplicate_flag

def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)

    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    if ts_cfg["interactive_mode"]:
        print 'Please select three APs.'
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
    if len(active_ap_list) < 2:
        raise Exception("Need three active APs:%s" % active_ap_list)

    active_ap1 = active_ap_list[0]  
    active_ap2 = active_ap_list[1]
    active_ap3 = active_ap_list[2]

    tcfg = {
            'active_ap1':active_ap1,
            'active_ap2':active_ap2,
            'active_ap3':active_ap3,
            'all_ap_mac_list': all_ap_mac_list,
            }

    test_cfgs = define_test_cfg(tcfg)   

    check_max_length(test_cfgs)
    check_duplicated_common_name(test_cfgs)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "LLDP_Function_Mesh_and_eMesh"

    ts = testsuite.get_testsuite(ts_name, "LLDP_Function_Mesh_and_eMesh", combotest=True)

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
