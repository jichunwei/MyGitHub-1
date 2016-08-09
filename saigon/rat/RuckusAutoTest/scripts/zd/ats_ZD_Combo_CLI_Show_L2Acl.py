'''
Description:
    Show L2 ACL information on ZD CLI, verify the information on ZD GUI.
    By Louis
    louis.lou@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration():
    test_cfgs = []
    ex_id = "[L2ACL Configure from GUI, Check from CLI]"
    test_name = 'CB_ZD_Remove_All_L2_ACLs'
    common_name = '%s1.Clean all L2 ACLs from ZD WebUI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
   
    test_name = 'CB_ZD_CLI_Show_L2_ACLs_All'
    common_name = '%s2.Show all the L2 ACLs in CLI' % ex_id
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
      
    test_name = 'CB_ZD_CLI_Verify_No_L2_ACLs'
    common_name = '%s3.Verify there is no L2 ACL in CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_ZD_Create_L2_ACLs'
    common_name = '%s4.Create 2 L2 ACLs via GUI' % ex_id
    param_cfg = dict(num_of_acl_entries = 2,num_of_mac = 1)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Show_L2_ACLs_All'
    common_name = '%s5.Show all the L2 ACLs in CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_CLI_Verify_L2_ACLs_All'
    common_name = '%s6.Verify there is no L2 ACL in CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Verify_L2_ACLs_Name'
    common_name = '%s7.Show and verify L2 ACL Name in CLI' % ex_id
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    return test_cfgs
        

def create_test_suite(**kwargs):
    ts_name = 'TCID: Show L2 ACL'
    ts = testsuite.get_testsuite(ts_name, 'Show L2 ACL in CLI', combotest=True)
    
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
    