"""
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn 
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def pairs(lst):
    n = len(lst)
    for i in range(n):
        yield lst[i],lst[(i+1)%n]

def define_test_cfg(cfg):
    test_cfgs = []
    
    if cfg['rate_limit']: 
        test_name = 'CB_ZD_Set_RateLimit_On_L3Switch'
        common_name = 'Change rate limit on switch to %s' % cfg['rate_limit']
        test_cfgs.append(({'rate_limit': cfg['rate_limit']}, test_name, common_name, 0, False))  
    
    # Testing speedflex between AP and Zone Director 
    for ap in cfg['active_ap_list']: 
        test_name = 'CB_ZD_Speedflex_On_MultiHop_MeshAP'
        common_name = 'Run Speedflex between AP [%s - %s] and Zone Director' % (cfg['ap_sym_dict'][ap]['model'], 
                                                                                cfg['ap_sym_dict'][ap]['status']) 
        test_cfgs.append(({'active_ap_list': [ap], 'rate_limit': cfg['rate_limit']}, test_name, common_name, 0, False))   

    # Testing speedflex between 2 APs
    if len(cfg['active_ap_list']) >= 2: 
        for pair in pairs(cfg['active_ap_list']): 
            test_name = 'CB_ZD_Speedflex_On_MultiHop_MeshAP'
            common_name = 'Run Speedflex between AP [%s - %s] and AP [%s - %s]' % (cfg['ap_sym_dict'][pair[0]]['model'], 
                                                                                   cfg['ap_sym_dict'][pair[0]]['status'],
                                                                                   cfg['ap_sym_dict'][pair[1]]['model'], 
                                                                                   cfg['ap_sym_dict'][pair[1]]['status'])
            test_cfgs.append(({'active_ap_list': list(pair), 'rate_limit': cfg['rate_limit']}, test_name, common_name, 0, False))   

    if cfg['rate_limit']: 
        test_name = 'CB_ZD_Set_RateLimit_On_L3Switch'
        common_name = 'Remove rate limit on Switch'
        test_cfgs.append(({'rate_limit': 100}, test_name, common_name, 0, False))  
            
    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        rate_limit = raw_input("Test with rate limit: (Enter number 1-100 or Press Enter to skip rate limit testing)")
        if rate_limit.strip() != "": 
            rate_limit = int(rate_limit)
        else: 
            rate_limit = 0 
    else:
        active_ap_list = sorted(ap_sym_dict.keys())
        
    # filter active APs which support speedflex test
    tcfg = {
        'active_ap_list': [],
        'ap_sym_dict': ap_sym_dict,
        'rate_limit': rate_limit,
    }
    for ap in active_ap_list: 
        if ap_sym_dict[ap]['model'] in const._ap_speedflex_supported: 
            tcfg['active_ap_list'].append(ap)
    test_cfgs = define_test_cfg(tcfg)
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "Speedflex on Multi-hop Mesh AP"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify running with multi-hop on Mesh AP",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
    test_order = 1
    test_added = 0
    if tcfg['active_ap_list']:
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
                test_order += 1
           
                print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
                
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    else: 
        print "None of Active APs are support speedflex" 

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
    