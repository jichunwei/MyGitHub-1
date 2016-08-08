"""
Verify Smart Redundancy of Dual stack IP mode in AP group
    
    expect result: All steps should result properly.
    
    How to:
        1) Create active AP
        2) Initialize SR environment and enable SR option
        3) Remove all AP groups
        4) Create AP group A with IP mode x and group B with IP mode x
        5) Configure active AP's IP mode to 'IPv4 only'
        6) Verify IP mode of AP group A/B/default and active AP in standby ZD
        7) Remove all AP groups
        8) Change IP mode of active AP to 'dual -stack'
        9) Repeat step 4-7
        10) Change IP mode of active AP to 'use group configuration'
        11) Repeat step 4-7

Created on 2012-10-18
@author: kevin.tan
"""

import sys
import time
from copy import deepcopy
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

nn = {'1': 'IPv4 only',
      '2': 'IPv6 only',
      '3': 'Dual stack',
      '*': 'Use Parent',
      }

def define_test_cfgs(tcfg):
    test_cfgs = []

    ap_tag = tcfg['active_ap']
    sta_tag = tcfg['target_sta']
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create Active AP'
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station'
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))

    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove all new created AP groups in the beginning'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    default_apgrp = 'System Default'
    default_apgrp_ipmode = '3' #dual-stack

    newapgrp1 = 'AP_Group_DualStack_SR1'
    argrp1_ipmode = '3' #dual-stack

    newapgrp2 = 'AP_Group_DualStack_SR2'
    argrp2_ipmode = '1' #IPv4 only

    ipmode_list = ['1', '3', '*']
    for ap_ipmode in ipmode_list:
        test_case_name = "[Dual stack IP mode when AP is %s]" % nn[ap_ipmode]

        test_name = 'CB_ZD_Create_AP_Group'
        common_name = '%sCreate AP group A' % (test_case_name,)
        test_cfgs.append(({'name':newapgrp1, 
                           'description': '%s_Description' % newapgrp1,
                           'ip_mode': argrp1_ipmode, },test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Create_AP_Group'
        common_name = '%sCreate AP group B' % (test_case_name,)
        test_cfgs.append(({'name':newapgrp2, 
                           'description': '%s_Description' % newapgrp2,
                           'ip_mode': argrp2_ipmode, },test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Config_AP_IPmode'
        common_name = '%sConfig IP mode of active AP' % (test_case_name,)
        test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp1, 'ip_mode': ap_ipmode}, test_name, common_name, 2, False))
    
        #Verification AP group and AP info
        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify default AP group info when AP belongs to group A in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': default_apgrp, 'ip_mode': default_apgrp_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify AP group A info when AP belongs to group A in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': newapgrp1, 'ip_mode': argrp1_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify AP group B info when AP belongs to group A in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': newapgrp2, 'ip_mode': argrp2_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))

        if ap_ipmode == '*':
            test_name = 'CB_ZD_Verify_AP_IPmode'
            common_name = '%sVerify AP IP mode when AP belongs to group A in standby ZD' % (test_case_name,)
            test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp1, 'ip_mode': ap_ipmode, 'ip_version': argrp1_ipmode, 'zd_type': 'standby'}, \
                              test_name, common_name, 2, False))
        else:
            test_name = 'CB_ZD_Verify_AP_IPmode'
            common_name = '%sVerify AP IP mode when AP belongs to group A in standby ZD' % (test_case_name,)
            test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp1, 'ip_mode': ap_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
    
        #Verification AP group and AP info again after moving AP between AP groups
        test_name = 'CB_ZD_Move_AP_Group_Member'
        common_name = '%sMove AP from group A to group B' % test_case_name
        test_cfgs.append(({'src_ap_group': newapgrp1,
                           'move_to_ap_group':newapgrp2, 
                           'ap_tag': ap_tag,},test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify default AP group info when AP belongs to group B in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': default_apgrp, 'ip_mode': default_apgrp_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify AP group A info when AP belongs to group B in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': newapgrp1, 'ip_mode': argrp1_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify AP group B info when AP belongs to groupB in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': newapgrp2, 'ip_mode': argrp2_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
    
        if ap_ipmode == '*':
            test_name = 'CB_ZD_Verify_AP_IPmode'
            common_name = '%sVerify AP IP mode when AP belongs to group B in standby ZD' % (test_case_name,)
            test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp2, 'ip_mode': ap_ipmode, 'ip_version': argrp2_ipmode, 'zd_type': 'standby'}, \
                              test_name, common_name, 2, False))
        else:
            test_name = 'CB_ZD_Verify_AP_IPmode'
            common_name = '%sVerify AP IP mode when AP belongs to group B in standby ZD' % (test_case_name,)
            test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': newapgrp2, 'ip_mode': ap_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Move_AP_Group_Member'
        common_name = '%sMove AP from group B to default group' % test_case_name
        test_cfgs.append(({'src_ap_group': newapgrp2,
                           'move_to_ap_group': 'System Default', 
                           'ap_tag': ap_tag,},test_name, common_name, 2, False))

        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify default AP group info when AP belongs to default group in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': default_apgrp, 'ip_mode': default_apgrp_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))

        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify AP group A info when AP belongs to default group in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': newapgrp1, 'ip_mode': argrp1_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Group_Info'
        common_name = '%sVerify AP group B info when AP belongs to default group in standby ZD' % (test_case_name,)
        test_cfgs.append(({'ap_group': newapgrp2, 'ip_mode': argrp2_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
    
        if ap_ipmode == '*':
            test_name = 'CB_ZD_Verify_AP_IPmode'
            common_name = '%sVerify AP IP mode when AP belongs to default group in standby ZD' % (test_case_name,)
            test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': default_apgrp, 'ip_mode': ap_ipmode, 'ip_version': default_apgrp_ipmode, 'zd_type': 'standby'}, \
                              test_name, common_name, 2, False))
        else:
            test_name = 'CB_ZD_Verify_AP_IPmode'
            common_name = '%sVerify AP IP mode when AP belongs to default group in standby ZD' % (test_case_name,)
            test_cfgs.append(({'ap_tag': ap_tag, 'ap_group': 'System Default', 'ip_mode': ap_ipmode, 'zd_type': 'standby'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Remove_All_AP_Groups'
        common_name = '%sRemove all new created AP groups' % (test_case_name,)
        test_cfgs.append(({}, test_name, common_name, 2, True))
    
    #clear configuration    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove all AP groups at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
   
    test_name = 'CB_ZD_Config_AP_IPmode'
    common_name = 'Config IP mode of active AP to user parent at last'
    test_cfgs.append(({'ap_tag': ap_tag, 'ip_mode': '*'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD'
    test_cfgs.append(({},test_name, common_name, 0, True))
    
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
  
def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_sta = '',
                 active_radio = '',
                 ts_name = "",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an active AP: ")
            if active_ap not in ap_sym_dict.keys():
                print "AP[%s] doesn't exist." % active_ap
            else:
                break
            
        target_sta = testsuite.getTargetStation(sta_ip_list)
        active_radio = testsuite.get_target_sta_radio()
        
    else:
        active_ap = attrs["active_ap"]
        target_sta = attrs['target_sta']
        active_radio = attrs["active_radio"]

    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if active_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, active_radio)
        return
    
    tcfg = dict(active_ap = active_ap,
                active_radio = active_radio,
                target_sta = target_sta,
                target_ip = '172.16.10.252'
                )
    
    test_cfgs = define_test_cfgs(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Dual stack IP mode in AP group SR" 
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify dual stack IP mode in AP group SR",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest = True)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
    
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    