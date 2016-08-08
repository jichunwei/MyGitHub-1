"""
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
     This script is verify auto upgrade via cli for CPE.
"""

import sys
import random

import libCPE_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg, reboot_times):
    test_cfgs = []
    
    for i in range(0, reboot_times):
        test_name = 'CB_AP_Reboot'
        common_name = 'Reboot AP %04d' % random.randrange(1,9999) 
        param_cfg = {'ap_cli_cfg': tcfg['ap_cli_cfg']}
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
            
    return test_cfgs

def define_test_parameters():
    ap_cli_cfg = {'ip_addr': '192.168.0.200',
                  'username': 'super',
                  'password': 'sp-admin',
                  'telnet': True,
                  'port'    : 23,
                  'timeout' : 360,
                  }     
     
    cfg = {'ap_cli_cfg': ap_cli_cfg} 
    return cfg

def create_test_suite(**kwargs):
    tcfg = define_test_parameters()
    
    model_name = raw_input("Please input AP model:")
    reboot_times = raw_input("Please input reboot times:")
    
    if not reboot_times:
        reboot_times = 1
    if not model_name:
        model_name = ""
    
    for i in range(0, int(reboot_times)):
        ts_name = 'AP CLI - Repeat Reboot 50 times %s-%04d' % (model_name, random.randrange(1,9999))
        ts = testsuite.get_testsuite(ts_name, 'Verify reboot AP repeatly', combotest=True)
        test_cfgs = define_test_cfg(tcfg, 50)
    
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
    