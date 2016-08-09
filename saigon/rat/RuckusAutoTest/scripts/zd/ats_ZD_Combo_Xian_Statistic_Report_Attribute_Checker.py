"""
Author:cwang@ruckuswireless.com
"""

import time
import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant



def define_wlan_cfg():    
    wlan_cfg = dict(ssid = "RAT-WLAN-statistic-%s" % (time.strftime("%H%M%S")),
                    auth = "open", wpa_ver = "", encryption = "none",
                    key_index = "" , key_string = "",
                    username = "", password = "", auth_svr = "", 
                    web_auth = None, do_service_schedule=None,)    
    return wlan_cfg


def build_tcs():
    tcs = []
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_All_WLAN_Groups', 
                'Remove All WLAN Groups', 
                0, 
                False))
                  
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
    
    wlan = define_wlan_cfg()
    tcs.append(({'wlan_cfg_list':[wlan]},
                'CB_ZD_CLI_Create_Wlans',
                'Create Wlans',
                0,
                False
                ))
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Wait for 90 seconds',
                0,
                False
                ))
    
    tcid = "[ZD-28926]"
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                '%sget xml data from AP' % tcid,
                1,
                False
                ))
    
    tcs.append(({"attr":[["wlan", "tx", "pkts"],
                         ["wlan", "rx", "pkts"],
                         ["wlan", "tx", "bytes"],
                         ["wlan", "rx", "bytes"],
                         ["vap", "tx", "pkts"],
                         ["vap", "rx", "pkts"],
                         ["vap", "tx", "bytes"],
                         ["vap", "rx", "bytes"],
                         ["vap", "tx", "mgmt", "pkts"],
                         ["vap", "rx", "mgmt", "pkts"],
                         ]},
                'CB_Statistic_Attribute_Check',
                '%scheck xml attribute' % tcid,
                2,
                False
                ))
    
    
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_All_WLAN_Groups', 
                'Clean up All WLAN Groups', 
                0, 
                True))
                  
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Clean up all WLANs', 
                0, 
                True))
        
    return tcs


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Statistic Reporting-Attribute check",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
        
    ts_name_list = [("Statistic Reporting-Attribute WLAN and VAP check", build_tcs),]
        
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn()
    
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