'''
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration(cfg):
    cnt = 100
    if cfg.has_key('cnt') and cfg['cnt']:
        cnt = cfg['cnt']
        
    test_cfgs = []    
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore ZD to full configurations'
    param_cfg = dict(restore_file_path = cfg['full_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_Scaling_Verify_APs'
    common_name = 'First time check all of APs are connected including RuckusAP and SIMAP'
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
          
         
    for index in range(1, cnt + 1):
        test_case_name='[restart all ap 100 times]'               
        test_name = 'CB_ZD_Scaling_APs_Reboot'
        common_name = '%s Restart All APs try #(%d)' % (test_case_name,index)
        param_cfg = dict()
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
            
            
        test_name = 'CB_Scaling_Waiting'
        common_name = '%s Waiting for 30 MINs try #(%d)' % (test_case_name,index)
        param_cfg = dict(timeout=cfg['wait_for'])
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))        
        
        test_name = 'CB_Scaling_Verify_APs'
        common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP try #(%d)' % (test_case_name,index)
        param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore ZD to empty configurations'
    param_cfg = dict(restore_file_path = cfg['empty_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    return test_cfgs

def create_test_parameters(tbcfg, attrs, cfg):
    cfg['cnt'] = 100        
    cfg['wait_for'] = 30
    cfg['timeout'] = 3 * 1800
    
    import os
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\full_cfg.bak" )    
    cfg['full_config_path'] = file
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\empty_cfg.bak" )    
    cfg['empty_config_path'] = file  
            

def create_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    cfg = {}
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    create_test_parameters(tbcfg, attrs, cfg)
    ts_name = 'TCID:45.04 max APs with memory leak - maximum AP rebooting '
    ts = testsuite.get_testsuite(ts_name, '500 APs with memory leak - maximum AP rebooting ', combotest=True)
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
    _dict['tbtype'] = 'ZD_Scaling'
    create_test_suite(**_dict)
    