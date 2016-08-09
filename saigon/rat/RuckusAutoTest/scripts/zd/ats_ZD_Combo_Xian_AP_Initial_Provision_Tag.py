"""
Verify AP initial provision tag function works well or not when AP join ZD at the first time.
    
    expect result: All steps should result properly.
    
    How to:
        1)  Set ZD factory default
        2)  Create active AP
        3)  Create AP group A(name length is max 32), B and C
        4)  Verify AP IPT is System Default
        5)  Change AP IPT to AP group A
        6)  Verify AP IPT is group A
        7)  Change AP IPT to an invalid AP group D(name length more than max 32)
        8)  Verify AP IPT is still group A
        9)  Remove AP from GUI and clear all events
        10) Wait for AP to rejoin ZD in AP group A and event 'AP[xx:xx:xx:xx:xx:xx] is assigned to [apgrp-A]' is shown
        11) Change AP IPT to AP group B
        12) Reboot AP and wait for rejoin ZD in AP group A and event shown (Since it's not the first time that AP joins ZD)
        13) Move AP from group A to B and Verify AP IPT is group B
        14) Remove AP from GUI and clear all events
        15) Wait for AP to rejoin ZD in AP group B and event 'AP[xx:xx:xx:xx:xx:xx] is assigned to [apgrp-B]' is shown
        16) Change AP IPT to AP group B to C and Verify AP IPT is group C
        17) Change AP IPT back to AP group B, reboot ZD and Wait for AP to rejoin ZD in AP group C and no event shown
        18) Set factory default
        19) Wait for AP to rejoin ZD in system default AP group and event 'AP[xx:xx:xx:xx:xx:xx] initial provisioning [apgr-C] is undefined; 
           AP assigned to system default group' is shown
        20) Move AP to System Default group
        21) Change AP IPT to an inexistent AP group E
        22) Remove AP from GUI and clear all events
        23) Wait for AP to rejoin ZD in AP group C and event 'AP[xx:xx:xx:xx:xx:xx] initial provisioning [apgr-E] is undefined; 
           AP assigned to system default group' is shown
        24) Move AP to group A
        25) Change AP IPT to an inexistent AP group E
        26) Remove AP from GUI and clear all events
        27) Wait for AP to rejoin ZD in AP group C and event 'AP[xx:xx:xx:xx:xx:xx] initial provisioning [apgr-E] is undefined; 
           AP assigned to system default group' is shown

Created on 2012-11-06
@author: kevin.tan
"""

import os
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'clean environment by setting ZD to factory default'
    test_cfgs.append(({},test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap_list'][0],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    apgrp_default       = 'System Default'
    apgrp_a_name        = '12345678901234567890123456789012' # Maximum name length is 32
    apgrp_a_plus_name   = 'K'+apgrp_a_name
    apgrp_b_name        = 'AP_Group_B'
    apgrp_c_name        = 'AP_Group_C'
    apgrp_d_name        = 'AP_Group_Inexistent'

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = 'Create AP group A with maximum name length'
    test_cfgs.append(({'name':apgrp_a_name, 
                       'description': '%s_Description' % apgrp_a_name,},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_AP_Group'
    common_name = 'Create AP group B'
    test_cfgs.append(({'name':apgrp_b_name, 
                       'description': '%s_Description' % apgrp_b_name,},test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = 'Create AP group C'
    test_cfgs.append(({'name':apgrp_c_name, 
                       'description': '%s_Description' % apgrp_c_name,},test_name, common_name, 0, False))
    
    test_case_name = "[IPT AP group name existent]"

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is System Default' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_default,},test_name, common_name, 1, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from System Default to group A' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_a_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is group A' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_a_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from System Default to invalid group that name length more than max' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_a_plus_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is still in group A after setting invalid name' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_a_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining group A and event is shown' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_a_name, 'event_log': 'positive',},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from group A to B' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_b_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot_AP'
    common_name = '%sReboot active AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is still in group A after AP reboot' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_a_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group A to B' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_a_name,
                       'move_to_ap_group':apgrp_b_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is group B after move AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_b_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI after move AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events after move AP' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining group B and event is shown after move AP' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_b_name, 'event_log': 'positive',},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is group B after rejoin' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_b_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group B to C' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_b_name,
                       'move_to_ap_group':apgrp_c_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is group C' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_c_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from group C to B' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_b_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events before ZD reboot' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot'
    common_name = '%sReboot ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP still join group C and no event is shown' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_c_name, 'event_log': 'none'},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is still group C after ZD reboot' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_c_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sSet ZD factory default' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, True))  

    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and negative event is shown' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_log': 'negative', 'original_ap_group': apgrp_c_name},test_name, common_name, 2, True))

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sVerify AP IPT is System Default after setting ZD factory' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'get',
                       'ipt': apgrp_default,},test_name, common_name, 2, True))

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = '%sCreate AP group A with maximum name length after setting ZD factory' % test_case_name
    test_cfgs.append(({'name':apgrp_a_name, 
                       'description': '%s_Description' % apgrp_a_name,},test_name, common_name, 2, True))

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = '%sCreate AP group B after setting ZD factory' % test_case_name
    test_cfgs.append(({'name':apgrp_b_name, 
                       'description': '%s_Description' % apgrp_b_name,},test_name, common_name, 2, True))

    test_name = 'CB_ZD_Create_AP_Group'
    common_name = '%sCreate AP group C after setting ZD factory' % test_case_name
    test_cfgs.append(({'name':apgrp_c_name, 
                       'description': '%s_Description' % apgrp_c_name,},test_name, common_name, 2, True))


    test_case_name = "[IPT AP group name inexistent]"

    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from System Default to inexistent group D' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_d_name,},test_name, common_name, 1, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining System Default group and negative event is shown' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_log': 'negative', 'original_ap_group': apgrp_d_name},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group System Default to A' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_default,
                       'move_to_ap_group':apgrp_a_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from group A to inexistent group D' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_d_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI after move AP to group A' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events after move AP to group A' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining default group and negative event after move AP to group A' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_log': 'negative', 'original_ap_group': apgrp_d_name},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Move_AP_Group_Member'
    common_name = '%sMove AP from group System Default to B' % test_case_name
    test_cfgs.append(({'src_ap_group': apgrp_default,
                       'move_to_ap_group': apgrp_b_name, 
                       'ap_tag': ap_tag,},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Initial_Provision_Tag'
    common_name = '%sChange AP IPT from group B to inexistent group D' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 
                       'operation': 'set',
                       'ipt': apgrp_d_name,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Delete_APs'
    common_name = '%sRemove approval AP from ZD GUI after move AP to group B' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all ZD events after move AP to group B' % test_case_name
    test_cfgs.append(({},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '%sVerify AP joining default group and event after move AP to group B' % test_case_name
    test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': apgrp_default, 'event_log': 'negative', 'original_ap_group': apgrp_d_name},test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove all new created AP groups at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
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
        ts_name = "AP initial provision tag"

    ts = testsuite.get_testsuite(ts_name, "AP initial provision tag" , combotest=True)

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
