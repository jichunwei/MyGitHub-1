'''
Title: AP MTU configuration on ZD Smart Redundancy

Test purpose: Verify if AP MTU configuration can be kept with ZD SR on
    
Expect result: AP should keep the MTU configuration
    
TestCase_1 steps:
1) Enable Smart Redundancy;
2) Configure AP eth port MTU;
3) Do Failover;
4) Check the MTU configuration on AP.

Created on 2013-03-04
@author: sean.chen@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    
    ap1_tag = 'ap1'
    
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initiate test'
    test_params = {'zd1_ip_addr': '192.168.0.2',
                   'zd2_ip_addr': '192.168.0.3',
                   'share_secret': 'testing',
                   'sw_ip': '192.168.0.253'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy'
    test_cfgs.append(({'timeout': 1000}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Check_Ap_Num_From_Web'
    common_name = 'Wait for AP connect to active ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': cfg['active_ap1'],
                       'ap_tag': ap1_tag}, test_name, common_name, 0, False))
    
#---TestCase_1-----------------------------------------------------------------------------------
    test_case_name = 'Verify AP MTU configuration with ZD SR on'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP eth port MTU' % test_combo_case_name
    test_params = {'ap_tag': ap1_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'do_random': True,
                   'random_range': (1500, 9578),
                   'expect_status': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Failover'
    common_name = 'Perform ZD Failover'
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Check_Ap_Num_From_Web'
    common_name = 'Wait for AP connect to new active ZD' 
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Eth_Mtu_Setting'
    common_name = '%sCheck AP eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'retrieve_mtu': True,
                   'expect_status': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCases End--------------------------------------------------------------------------------
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = 'Restore AP default eth port MTU'
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    return test_cfgs

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  testsuite_name = '')
    ts_cfg.update(kwargs)

    tcfg = {'active_ap1':'AP_01'}

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = "AP MTU configuration on ZD SR"

    ts = testsuite.get_testsuite(
        ts_name, "Verify if AP MTU configuration can be kept with ZD SR on",
        interactive_mode = ts_cfg["interactive_mode"],
        combotest = True )
    
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

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

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    