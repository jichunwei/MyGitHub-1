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

    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial test environment of test, call 2 ZD up'
    test_cfgs.append(({'zd1_ip_addr':cfg['zd1']['ip_addr'], 'zd2_ip_addr':cfg['zd2']['ip_addr'],
                       'share_secret':cfg['zd1']['share_secret']},
                       test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name,0,False))
        
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = "Get the Active ZD"
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_SR_Get_Standby_ZD'
    common_name = "Get the Standby ZD"
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = 'get ap number connected with zd'
    param_cfg = dict(timeout = 120, chk_gui = False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
         
    for index in range(1, cnt + 1):
        
        test_case_name='[Scaling SR Failover Test]'        
        
        test_name = 'CB_ZD_SR_Failover'
        common_name = '%sFailover ZD try #(%d)' % (test_case_name,index)
        param_cfg = dict()
        test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
        test_name = 'CB_Scaling_Verify_APs_Num'
        common_name = '%sCheck all of APs are connected including RuckusAP and SIMAP#(%d)' %  (test_case_name,index)
        param_cfg = dict(timeout = cfg['timeout'], aps_num = 500)
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
    test_name = 'CB_ZD_SR_Clear_Up'
    common_name = "Clear up the Smart Redundancy test environment"
    test_cfgs.append(({},test_name, common_name,0,False)) 
        
    return test_cfgs

def create_test_parameters(tbcfg, attrs, cfg):
    cfg['cnt'] = 100
    cfg['timeout'] = 1800
#   cfg['wait_for'] = 60 * 10

    cfg['zd1'] = {'ip_addr':'192.168.0.2',
                  'share_secret':'testing'
                  }
    cfg['zd2'] = {'ip_addr':'192.168.0.3',
                  'share_secret':'testing'
                  }    

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
    ts_name = 'Managed 500 Aps - With Failover.'
    ts = testsuite.get_testsuite(ts_name, 'Force Failover every 10 minutes via WebUI for 24 hours.', combotest=True)
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
    