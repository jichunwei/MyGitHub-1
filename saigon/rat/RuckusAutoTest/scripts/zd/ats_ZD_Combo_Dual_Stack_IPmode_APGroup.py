"""
Verify different configuration (positive and negative) of Dual stack IP mode in AP group
    
    expect result: All steps should result properly.
    
    How to:
        1) Remove all WLANs
        2) Set factory default
        3) Create active AP
        4) Configuration test when AP in one AP group
        5) Configuration test when AP switch between two AP groups
        6) Negative test
        7) Backup and restore: Full
        8) Backup and restore: Fail-over,
        9) Backup and restore: Policy

Created on 2012-10-18
@author: kevin.tan
"""

import os
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as constant

def define_test_cfg(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'clean environment by setting ZD to factory default'
    test_cfgs.append(({},test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    # Different Configuration
    test_name = 'CB_ZD_Dualstack_IPmode_APgroup_Config'
    common_name = '[Configuration in One AP group] Dual-stack IP mode in AP group'
    test_cfgs.append(({'ap_tag': ap_tag,}, test_name, common_name, 1, False))

    test_case_name = "[Configuration between two AP groups]"
    apgrp_a_name = 'AP_Group_A'
    argrp_a_ipmode = '3' #dual stack

    apgrp_b_name = 'AP_Group_B'
    argrp_b_ipmode = '1' #IPv4

    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = '%sRemove all new created AP group in the beginning' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_Create_AP_Group'
    common_name = '%sCreate AP group A' % test_case_name
    test_cfgs.append(({'name':apgrp_a_name, 
                       'description': '%s_Description' % apgrp_a_name,
                       'ip_mode': argrp_a_ipmode, },test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_AP_Group'
    common_name = '%sCreate AP group B' % test_case_name
    test_cfgs.append(({'name':apgrp_b_name, 
                       'description': '%s_Description' % apgrp_b_name,
                       'ip_mode': argrp_b_ipmode, },test_name, common_name, 2, False))

    ap_ipmode = '*'#Use parent, override group config disabled
    test_name = 'CB_ZD_Config_AP_IPmode'
    common_name = '%sConfig IP mode of active AP to Use Parent' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': ap_ipmode}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from default to group A when AP use parent' % test_case_name
    test_cfgs.append(({'src_ap_group': 'System Default',
                       'move_to_ap_group':apgrp_a_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode when AP in group A and AP use parent' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_a_name, 'ip_mode': ap_ipmode, 'ip_version': argrp_a_ipmode}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group A to B when AP use parent' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_a_name,
                       'move_to_ap_group':apgrp_b_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode when AP in group B when AP use parent' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_b_name, 'ip_mode': ap_ipmode, 'ip_version': argrp_b_ipmode}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group B to default when AP use parent' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_b_name,
                       'move_to_ap_group':'System Default', 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))
    
    ap_ipmode = '1' #IPv4
    test_name = 'CB_ZD_Config_AP_IPmode'
    common_name = '%sConfig IP mode of active AP to IPv4' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': ap_ipmode}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from default to group A when AP use IPv4' % test_case_name
    test_cfgs.append(({'src_ap_group': 'System Default',
                       'move_to_ap_group':apgrp_a_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode when AP in group A and AP use IPv4' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_a_name, 'ip_mode': ap_ipmode,}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group A to B when AP use IPv4' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_a_name,
                       'move_to_ap_group':apgrp_b_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode when AP in group B and AP use IPv4' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_b_name, 'ip_mode': ap_ipmode,}, test_name, common_name, 2, False))
    
    # Negative test
    test_name = 'CB_ZD_Dualstack_IPmode_APgroup_Negative_Test'
    common_name = '[Negative test] Dual-stack IP mode in AP group'
    test_params = {'ap_tag': ap_tag,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    # Backup and restore
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove all new created AP groups in the beginning'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    newapgrp = 'AP_Group_BackupRestore'
    argrp_ipmode = '3' #dual-stack

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = 'Create AP group for backup restore'
    test_cfgs.append(({'name':newapgrp, 
                       'description': '%s_Description' % newapgrp,
                       'ip_mode': argrp_ipmode, },test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_IPmode'
    ap_ipmode = '1' #IPv4
    ap_ipmode_default = '*' #Use parent, override group config disabled
    common_name = 'Config IP mode of active AP'
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp, 'ip_mode': ap_ipmode}, test_name, common_name, 0, False))
    
    #### Full Backup ###
    test_case_name = "[Full Backup Restore]"
    save_to = constant.save_to
    test_name = 'CB_ZD_Backup'
    common_name = '%sBackup System' % (test_case_name,)
    test_cfgs.append(({'save_to':save_to},test_name, common_name, 1, False)) 
    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = '%sRemove all new created AP group' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Config_AP_IPmode'
    common_name = '%sConfig IP mode of active AP' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': ap_ipmode_default}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the backup file' % (test_case_name,)
    test_cfgs.append(({'restore_type':'restore_everything'},test_name, common_name,2,False)) 
    
    test_name = 'CB_ZD_Verify_AP_Group_Info'
    common_name = '%sVerify AP Group info is restored to ZD' % (test_case_name,)
    test_cfgs.append(({'ap_group': newapgrp, 'ip_mode': argrp_ipmode,}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode is restored to ZD' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp, 'ip_mode': ap_ipmode,}, test_name, common_name, 2, False))
    
    #### Failover Backup ###
    test_case_name = "[Failover Backup Restore]"
    test_name = 'CB_ZD_Change_System_Name'
    common_name = '%sChange System Name to ruckus-before-backup' % (test_case_name,)
    test_cfgs.append(({'system_name':'ruckus-before-backup'},test_name,common_name, 1, False))

    test_name = 'CB_ZD_Backup'
    common_name = '%sBackup System' % (test_case_name,)
    test_cfgs.append(({'save_to':save_to},test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Change_System_Name'
    common_name = '%sChange System Name to original Ruckus' % (test_case_name,)
    test_cfgs.append(({'system_name':'Ruckus'},test_name,common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = '%sRemove all new created AP group' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Config_AP_IPmode'
    common_name = '%sConfig IP mode of active AP' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': ap_ipmode_default}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the backup file' % (test_case_name,)
    test_cfgs.append(({'restore_type':'restore_everything_except_ip'},test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_AP_Group_Info'
    common_name = '%sVerify AP Group info is restored to ZD' % (test_case_name,)
    test_cfgs.append(({'ap_group': newapgrp, 'ip_mode': argrp_ipmode, }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode is restored to ZD' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp, 'ip_mode': ap_ipmode,}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_System_Name'
    common_name = '%sVerify System Name can not be restored to ZD' % (test_case_name,)
    test_cfgs.append(({'before_system_name':'ruckus-before-backup','system_name_change':False},test_name, common_name, 2, False))
    
    #### Policy Backup ###
    test_case_name = "[Policy Backup Restore]"
    test_name = 'CB_ZD_Change_System_Name'
    common_name = '%sChange System Name to ruckus-before-backup' % (test_case_name,)
    test_cfgs.append(({'system_name':'ruckus-before-backup'},test_name,common_name, 1, False))

    test_name = 'CB_ZD_Backup'
    common_name = '%sBackup System' % (test_case_name,)
    test_cfgs.append(({'save_to':save_to},test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Change_System_Name'
    common_name = '%sChange System Name to original Ruckus' % (test_case_name,)
    test_cfgs.append(({'system_name':'Ruckus'},test_name,common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = '%sRemove all new created AP group' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Config_AP_IPmode'
    common_name = '%sConfig IP mode of active AP' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': ap_ipmode_default}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Restore'
    common_name = '%sRestore the backup file' % (test_case_name,)
    test_cfgs.append(({'restore_type':'restore_basic_config'},test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Verify_AP_Group_Info'
    common_name = '%sVerify AP Group info can not be restored to ZD' % (test_case_name,)
    test_cfgs.append(({'ap_group': newapgrp, 'is_exist': False,}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_IPmode'
    common_name = '%sVerify AP IP mode can not be restored to ZD' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': 'System Default', 'ip_mode': ap_ipmode_default,}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_System_Name'
    common_name = '%sVerify System Name can not be restored to ZD' % (test_case_name,)
    test_cfgs.append(({'before_system_name':'ruckus-before-backup','system_name_change':False},test_name, common_name, 2, False))

    #clear configuration    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove all new created AP group at last'
    test_cfgs.append(({}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_Config_AP_IPmode'
    ap_ipmode_modified = '*' #UseParent configuration
    common_name = 'Config IP mode of active AP to parent at last'
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': ap_ipmode_modified}, test_name, common_name, 0, False))
    
    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
  
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap_list':active_ap_list,
            'all_ap_mac_list': all_ap_mac_list,
            }
    
    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Dual stack IP mode in AP group"

    ts = testsuite.get_testsuite(ts_name, "Dual stack IP mode in AP group" , combotest=True)

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
