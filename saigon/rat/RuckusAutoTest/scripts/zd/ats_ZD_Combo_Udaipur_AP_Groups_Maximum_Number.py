'''
Test cases coverage:
ZD-2900:ZD supports maximum AP group number
   To verify ZD supports following number of 
   groups by difference platform list below:
    1. ZD1000: 32
    2. ZD1100: 32
    3. ZD3000: 256
    4. ZD5000: 512         

The FS will be updated.
In current design, users can delete the AP which has not been defined to the System Default AP group.
    
Created on 2011-11-07
@author: cwang@ruckuswireless.com
'''

import sys
from copy import deepcopy
import time
import random

import libZD_TestSuite as testsuite

from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const


def create_tcs(mode="ZD3000"):
    cfg = {'ZD1000':32,
           'ZD1100':32,
           'ZD3000':256,
           'ZD5000':512
           }
    tcs = []    
    tcs.append(({}, 
                'CB_ZD_Remove_All_AP_Groups', 
                'Clean All AP Groups',
                0,
                False))
    
    tcs.append(({'number':cfg[mode]},
                'CB_ZD_AP_Group_Maximum_Testing',
                '[Maximum AP Groups]Maximum AP Group numbers',
                0,
                False,
                ))    
    
    tcs.append(({}, 
                'CB_ZD_Remove_All_AP_Groups', 
                'Remove All AP Groups',
                0,
                False))
        
    return tcs
    

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "AP Group Combination-Maximum number",
                 )
    attrs.update(kwargs)
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
                
        
    if attrs["interactive_mode"]:
        ts_name = "AP Group Combination-Maximum number"        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "AP Group Combination-Maximum number",
                                 combotest=True)
    
    prompt = '''
    Please Input the ZD mode index:
        1) ZD3000
        2) ZD5000
        3) ZD1100
        4) ZD1000
    For example: 1-->ZD3000 and this is by default.
    '''
    model_index = int(raw_input(prompt))
    if model_index not in range(1, 5):
        model_index = 1  
        
    cfg = {1:'ZD3000',
           2:'ZD5000',
           3:'ZD1100',
           4:'ZD1000'
           }
    print "ZD mode:%s" % cfg[model_index]           
    test_cfgs = create_tcs(cfg[model_index])    
    
    test_order = 1
    test_added = 0
    
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params,
                                  test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % \
        (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % \
    (test_added, ts.name)          


if __name__ == "__main__":    
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
