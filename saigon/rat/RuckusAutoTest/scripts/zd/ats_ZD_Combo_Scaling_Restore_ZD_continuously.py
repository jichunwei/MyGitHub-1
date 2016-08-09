'''
Description:
    restore ZD to full config and empty config continuously
    just to reccur a bug
    
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration(cfg):
    test_cfgs = []
    pre_name = 'continuous restore'       

    for i in range(1,6*24*2):            
        test_name = 'CB_ZD_Restore'
        common_name = '[%s]:Restore ZD to full configurations %d' % (pre_name,i)
        param_cfg = dict(restore_file_path = cfg['full_config_path'])
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
        test_name = 'CB_ZD_Sleep'
        common_name = '[%s]:wait for a while after restore to full cfg %d' % (pre_name,i)
        param_cfg = dict(restore_file_path = cfg['full_config_path'])
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Restore'
        common_name = '[%s]:Restore ZD to empty configurations %d' % (pre_name,i)
        param_cfg = dict(restore_file_path = cfg['empty_config_path'])
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
        test_name = 'CB_ZD_Sleep'
        common_name = '[%s]:wait for a while  after restore to empty cfg %d' % (pre_name,i)
        param_cfg = dict(restore_file_path = cfg['full_config_path'])
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
            
    return test_cfgs

def create_test_parameters(tbcfg, attrs, cfg):

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else:
        ts_name = "continuously restore"
    
    cfg['testsuite_name'] = ts_name

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
    ts_name = 'continuously restore'
    ts = testsuite.get_testsuite(ts_name, 'continuously restore', combotest=True)
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
    