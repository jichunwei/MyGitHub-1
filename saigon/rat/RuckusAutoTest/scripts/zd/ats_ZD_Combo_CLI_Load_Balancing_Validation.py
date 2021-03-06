'''
Description: 
    Show AAA Server information on ZD CLI, verify the information on ZD GUI.
    By Chris
    cwang@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def gen_id(id):
    ex_id = "[Load balancing configure from GUI, check from CLI]"
    return '%s(%d) ' % (ex_id, id)

def define_test_configuration(cfg):
    test_cfgs = []
    i = 1 
    test_name = 'CB_ZD_Set_Load_Balancing'
    common_name = '%sEnable load balancing' % gen_id(i)
    param_cfg = dict(enable = True)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1    
    test_name = 'CB_ZD_CLI_Get_Check_Load_Balancing'
    common_name = '%sChecking load balancing' % gen_id(i)
    param_cfg = dict(enable = True)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
    
    i += 1
    test_name = 'CB_ZD_Set_Load_Balancing'
    common_name = '%sDisable load balancing' % gen_id(i)
    param_cfg = dict(enable = False, r24g_expected_enable = False, r5g_expected_enable = False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1    
    test_name = 'CB_ZD_CLI_Get_Check_Load_Balancing'
    common_name = '%sChecking load balancing' % gen_id(i)
    param_cfg = dict(enable = False,r24g_expected_enable = False, r5g_expected_enable = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))     
    
    return test_cfgs


def define_test_paramter():
    cfg = {}     
    return cfg


def create_test_suite(**kwargs):
    ts_name = 'TCID: x-Show load balancing information in CLI'
    ts = testsuite.get_testsuite(ts_name, 'Show load balancing information in CLI', combotest=True)
    cfg = define_test_paramter()
    test_cfgs = define_test_configuration(cfg)

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
    