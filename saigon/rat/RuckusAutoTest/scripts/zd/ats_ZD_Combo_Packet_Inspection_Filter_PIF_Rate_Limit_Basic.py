'''
Title: PIF Rate Limit Basic - Packet Inspection Filter

Test purpose: Verify PIF rate limit basic in PIF
    
Expect result: PIF rate limit default status and configuration mechanism is as expected
    
TestCase_1 steps:
1) Restore to factory default;
2) Check PIF rate limit default status.

TestCase_2 steps:
Configure PIF rate limit as the following values and check the configuration:
1) minimum
2) maximum
3) a random between minimum and maximum
4) empty
5) minimum - 1 
6) maximum + 1 
    
Created on 2012-11-21
@author: sean.chen@ruckuswireless.com
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg():
    test_cfgs = []
    
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'Initiate environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))

#---TestCase_1-----------------------------------------------------------------------------------    
    test_case_name = 'Default status check'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck PIF rate limit default status' % test_combo_case_name 
    test_cfgs.append(({'check_only': True, 'expected_status': False}, test_name, common_name, 1, False))
    
#---TestCase_2---------------------------------------------------------------------------------------
    test_combo_case_name = "[Configure minimum]"
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck rate limit minimum can be set' % test_combo_case_name 
    test_params = {'expected_status': True, 
                   'expected_rate_limit': 0, 
                   'expect_config_done': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_combo_case_name = "[Configure maximum]"
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck rate limit maximum can be set' % test_combo_case_name 
    test_params = {'expected_status': True, 
                   'expected_rate_limit': 3000, 
                   'expect_config_done': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_combo_case_name = "[Configure random value]"
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck random in the rate limit range can be set' % test_combo_case_name
    test_params = {'expected_status': True, 
                   'do_random': True, 
                   'random_range': (1,2999), 
                   'expect_config_done': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_combo_case_name = "[Configure empty value]"
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck empty rate limit can not be set' % test_combo_case_name 
    test_params = {'expected_status': True, 
                   'expected_rate_limit': '', 
                   'expect_config_done': False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_combo_case_name = "[Configure below minimum]"
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck rate limit minimum below can not be set' % test_combo_case_name 
    test_params = {'expected_status': True, 
                   'expected_rate_limit': -1, 
                   'expect_config_done': False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_combo_case_name = "[Configure above maximum]"
    test_name = 'CB_ZD_Config_PIF_Rate_Limit'
    common_name = '%sCheck rate limit maximum above can not be set' % test_combo_case_name 
    test_params = {'expected_status': True, 
                   'expected_rate_limit': 3001, 
                   'expect_config_done': False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
#---TestCases End--------------------------------------------------------------------------------
    return test_cfgs

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station = (0, "g"),
                  targetap = False,
                  testsuite_name = "")
    ts_cfg.update(kwargs)
    
    test_cfgs = define_test_cfg()

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'PIF Rate Limit Basic - Packet Inspection Filter'

    ts = testsuite.get_testsuite(
        ts_name, 'Verify PIF rate limit basic configuration.',
        interactive_mode = ts_cfg["interactive_mode"],
        combotest = True)

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
    