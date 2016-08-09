'''
Created on 2010-9-21

@author: cwang@ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    
    test_case_name='[remove License]'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP' % test_case_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Licenses'
    common_name = '%sRemove all licenses.'% test_case_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP(ZD3200)'% test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 200, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_case_name='[inc License]'
    test_name = 'CB_ZD_Import_License'
    common_name = '%sImport license inc license(50)'% test_case_name
    param_cfg = dict(file_path = cfg['license_file_1'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP(200+50)'% test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 250, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_case_name='[replacement License]'
    test_name = 'CB_ZD_Import_License'
    common_name = '%sImport license replacement license(250)'% test_case_name
    param_cfg = dict(file_path = cfg['license_file_2'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP(250+50)'% test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 300, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_case_name='[inc License again]'
    test_name = 'CB_ZD_Import_License'
    common_name = '%sImport inc license (200)'% test_case_name
    param_cfg = dict(file_path = cfg['license_file_3'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP(300+200)'% test_case_name
    param_cfg = dict(timeout = cfg['timeout'], aps_num = 500, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    return test_cfgs

def define_test_params(tbcfg):
    cfg = {}
    cfg['timeout'] = 1800 * 3
    file_path = "D:\\license\\"
    cfg['license_file_1'] = '%sinc50ap3k_SN1234.lic' % file_path
    cfg['license_file_2'] = '%s250ap3k_SN1234.lic' % file_path
    cfg['license_file_3'] = '%sinc200ap3k_SN1234.lic' % file_path
    return cfg

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ts_name = r'TCID 45.04 ZD3200-License'
    ts = testsuite.get_testsuite(ts_name, 'ZD3200-License Testing', combotest=True)
    cfg = define_test_params(tbcfg)
    test_cfgs = define_test_cfg(cfg)

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
    _dict['tbtype'] = 'ZD_Scaling'
    createTestSuite(**_dict)