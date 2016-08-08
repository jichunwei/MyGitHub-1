# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure Guest Access:
12.1    Negative name test.
12.2    Negative password test.
12.3    Negative IP address test.

Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def defineTestConfiguration():
    test_cfgs = []

    test_name = 'CB_ZD_CLI_Negative_Name_Test'    
    common_name = 'Negative name test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Negative_Password_Test'    
    common_name = 'Negative password test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Negative_IP_Address_Test'    
    common_name = 'Negative IP address test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs
  
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts_name = 'ZD CLI - Negative Test'
    ts = testsuite.get_testsuite(ts_name, 'Negative testing with ZD CLI for name, password and IP', combotest=True)
    test_cfgs = defineTestConfiguration()

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
