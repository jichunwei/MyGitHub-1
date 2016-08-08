'''
Description: 
    Show AP information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration():
    test_cfgs = []
    
    ex_id = "[AP info Configure from GUI, Check from CLI]"
    test_name = 'CB_ZD_Config_AP_Info'
    common_name = '%s1.Configure the APs information via GUI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
   
    test_name = 'CB_ZD_CLI_Show_AP_All'
    common_name = '%s2.Show ap all in CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Get_All_AP_Info'
    common_name = '%s3.Get All AP Information' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
      
    test_name = 'CB_ZD_CLI_Verify_AP_Info_All'
    common_name = '%s4.Verify all ap info in CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_CLI_Show_And_Verify_AP_Devname'
    common_name = '%s5.Show and Verify ZD CLI: show ap devname $name' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
    test_name = 'CB_ZD_CLI_Show_And_Verify_AP_Mac'
    common_name = '%s6.Show and Verify ZD CLI: show ap mac $mac' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
    return test_cfgs


def create_test_suite(**kwargs):
    ts_name = 'TCID: x-Show AP information in CLI'
    ts = testsuite.get_testsuite(ts_name, 'Show AP information in CLI', combotest=True)
    
    test_cfgs = define_test_configuration()

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
    