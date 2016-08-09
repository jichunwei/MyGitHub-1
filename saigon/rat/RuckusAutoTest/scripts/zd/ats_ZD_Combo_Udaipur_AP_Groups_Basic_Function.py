'''
Test cases coverage:
    ZD-2894:Default AP group
        To verify Default AP group behavior list below:
            1. Default AP group name can't be changed.
            2. Administrators can't delete the Default AP group by WebGUI.
            3. ZD allows administrators to clone the Default AP group configuration 
            settings to the new AP group.
            
    ZD-2895:Create/Delete new AP group
        To verify create new AP group behavior list below:
            1. ZD allows administrators to create new AP group by WebGUI or CLI.
            2. Administrators define parent group works, i.e., 
            If the configuration is set as "Use Global configuration", 
            its configuration will follow its parent group.
            3. ZD allows administrators to delete AP group by WebGUI.
            
    ZD-2896:Select APs to join AP group
        To verify APs join to the AP group behavior list below:
            1. All new join AP will be assgined to the Default 
            AP group automatically.
            2. The APs can be selected to join the specify AP group.
            3. An AP can only be in one group at a time.
            4. Select APs table has filter function to help 
            administrators to choose APs more quickly.
            5. Move APs to other AP group works.
    
    ZD-2897:Delete AP
        When an AP has not been defined to "Default" group, 
        it can't be deleted directly. A pop-up warning message 
        will show on the web UI to ask customer to move the AP to 
        "Default" group before deleting the AP.
            

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


def create_tcs():
    tcs = []    
    tcs.append(({}, 
                'CB_ZD_Remove_All_AP_Groups', 
                'Remove All AP Groups',
                0,
                False))
    
    tcs.append(({},
                'CB_ZD_AP_Group_System_Default_Testing',
                '[Default AP group]testing',
                1,
                False
                ))
    
    tcs.append(({'name':'AP_Group_1',
                     'description':'AP_Group_1',
                     'an': {'channel': '36',
                           'channelization': '20',
                           'mode': 'Auto',
                           'power': 'Full',
                           'wlangroups': 'Default'},
                     'bgn': {'channel': '11',
                            'channelization': '40',
                            'mode': 'N/AC-only',
                            'power': '-1dB',
                            'wlangroups': 'Default'},                                            
                },
                'CB_ZD_Create_AP_Group',
                '[Create AP Group]Create action',
                0,
                False
                ))
    
    tcs.append(({'clone_name':'AP_Group_1',
                 'new_name':'AP_Group_1_Clone'
                 },
                'CB_ZD_Clone_AP_Group',
                '[Clone AP Group]Clone action',
                1,
                False,
                ))        
    
    tcs.append(({'ap_group_name':'AP_Group_1'},
                'CB_ZD_Join_AP_Group_Testing',
                '[AP join to AP group]Select APs to join AP group',
                1,
                False
                ))
    
    tcs.append(({'ap_group_name':'AP_Group_1',
                 'move_to_group_name':'AP_Group_Move',
                 },
                'CB_ZD_Move_AP_Group_Testing',
                '[Move APs to other AP group works]Select APs to move other AP group',
                1,
                False
                ))
    
    tcs.append(({'name':'AP_Group_1'},
                'CB_ZD_Remove_AP_Group',
                '[Remove AP Group]Remove action',
                1,
                False
                ))
    
    tcs.append(({}, 
                'CB_ZD_Remove_All_AP_Groups', 
                'Remove All AP Groups',
                0,
                False))
    
    tcs.append(({},
                'CB_ZD_Re_Join_Default_AP_Group',
                '[AP re-join to default AP group]Delete all AP groups',
                1,
                False
                ))
    return tcs
    

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "AP Group Basic Function",
                 )
    attrs.update(kwargs)
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
                
        
    if attrs["interactive_mode"]:
        ts_name = "AP Group Basic Function"        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "AP Group Basic Function",
                                 combotest=True)
                
    test_cfgs = create_tcs()    
    
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
