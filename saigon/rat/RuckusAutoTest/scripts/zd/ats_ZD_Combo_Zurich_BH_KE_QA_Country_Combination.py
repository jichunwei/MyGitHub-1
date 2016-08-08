"""
Topos:
    ZD ---- SW --- AP )))) Station

Test Scenarios:    
    1) Attribute test:
        * Channel Range
        * Channelization-20, 40
        * Channel        
Created on 2013-05-7
@author: cwang@ruckuswireless.com
"""

import sys
import time
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant    

def _build_attribute_test(active_ap):
    def generate_ids():
        return (("[BH Channel Range | Channelization | Channel]",'BH', 'Bahrain'),
                 
                ("[KE Channel Range | Channelization | Channel]",'KE', 'Kenya'),
                             
                ("[QA Channel Range | Channelization | Channel]",'QA', 'Qatar'),)
    
    tcs = []
    ap_tag = active_ap['ap_tag']
    tcs.append(({'active_ap':ap_tag,
               'ap_tag': ap_tag}, 
               'CB_ZD_Create_Active_AP', 
               'Create active AP', 
               0, 
               False))
    
    ids = generate_ids()
    for tcid, cc, ccalias in ids:
        tcs.append(({'cc':cc,
                     'ccalias':ccalias
                     },
                    'CB_ZD_CLI_Set_AP_CountryCode',
                    '%sSet AP Country Code' % tcid,
                    1,
                    False
                    ))
        tcs.append(({'cc':cc,
                     'ccalias':ccalias
                     },
                    'CB_ZD_CLI_Test_AP_CountryCode',
                    '%sTest AP Country Code' % tcid,
                    2,
                    False
                    ))
        tcs.append(({'cc':'US',
                     'ccalias':'United States'
                     },
                    'CB_ZD_CLI_Set_AP_CountryCode',
                    '%sSet back AP Country Code to default' % tcid,
                    0,
                    True
                    ))
    
    return tcs
    

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
  
def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Zurich BH KE QA CountryCode - Combination",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
       
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    apcfg_list = []    
    for ap_tag in ap_sym_dict:
        ap = {}
        ap['ap_tag'] = ap_tag
        ap['mac'] = ap_sym_dict[ap_tag]['mac']
        ap['model'] = ap_sym_dict[ap_tag]['model']        
        if lib_Constant.is_ap_support_dual_band(ap['model']):                    
            apcfg_list.append(ap)
    
    if not apcfg_list:
        raise Exception("Haven't find any dualband AP in your testbed.")
    
    ts_name_list = [('Zurich BH KE QA CountryCode - Combination', _build_attribute_test),                                                                            
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(apcfg_list[0])
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
    
def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
