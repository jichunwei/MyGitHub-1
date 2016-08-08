'''
Description:
    Show Mgmt interface information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys
#import copy
import time
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils



def define_test_configuration(tbcfg):
    test_cfgs = []
    ex_id = "[Mgmt Interface configure from GUI, Check from CLI]"
    test_name = 'CB_ZD_Disable_Mgmt_Interface'
    common_name = '%s1.Disable MGMT IF via GUI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Show_Mgmt_Interface'
    common_name = '%s2.Show MGMT-IF information via CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
      
    test_name = 'CB_ZD_CLI_Verify_No_Mgmt_Interface'
    common_name = '%s3.Verify MGMT-IF status is Disabled' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Enable_Mgmt_Interface'
    common_name = '%s4.Enable MGMT Interface Info via GUI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Get_Mgmt_Interface'
    common_name = '%s5.Get MGMT Info via GUI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Show_Mgmt_Interface'
    common_name = '%s6.Show MGMT-IF information via CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_Mgmt_Interface'
    common_name = '%s7.Verify MGMT-IF information are correct' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
    return test_cfgs
        

def create_test_suite(**kwargs):
    ts_name = 'TCID: Show Mgmt Interface Information'
    ts = testsuite.get_testsuite(ts_name, 'Show Mgmt Interface Information in CLI', combotest=True)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    test_cfgs = define_test_configuration(tbcfg)

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
    