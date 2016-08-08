'''
Test cases coverage:
    ZD-2902:Compare AP group priority for <AP model>
    To verify the the priority of AP group is per AP > 
    new AP group > System Default AP group as following:
        1. 2.4G Radio settings
        2. Port settings 

    
    
    Steps:
        + Create a WLAN        
        + Pick-up AP and check configurations from AP CLI about the AP setting
            Checking items(2.4G, 5G):
                - channel "cmd: get channel wlan0/wlan8"
                - Channelization "cmd: get cwmode wlan0/wlan8"
                - Port Base VLAN "cmd: get interface"
        + Create a WLAN Group
        + Assign WLAN Group to AP
        + Create AP Group
        + Assign WLAN Group to AP Group
        + Assign AP Group to AP
        + Check AP Group setting if overwrite AP setting
        + Update AP setting, Check if use the AP-Based setting other then AP Group
        + Remove AP Group
        + Check if AP setting restore back to self-AP configuration.        
        
    
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


def create_tcs(ap_list):
    tcs = []    
    tcs.append(({},
                'CB_ZD_Remove_All_Wlan_Groups',
                'Clean All WLAN Groups',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Wlans',
                'Clean All WLANs',
                0,
                False
                ))
    
    
    tcs.append(({}, 
                'CB_ZD_Remove_All_AP_Groups', 
                'Clean All AP Groups',
                0,
                False))
    
    wlan_cfg = dict(ssid = "RAT-Open-None", 
                    auth = "open", 
                    encryption = "none")
    
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_Create_Wlans',
                'Create WLANs %s' % wlan_cfg['ssid'],
                0,
                False
                ))
    
    wlan_group_name = 'WLAN_Group_Test'
    tcs.append(({'wgs_cfg':{'name':wlan_group_name,
                            'description':wlan_group_name}
                 },
                'CB_ZD_Create_Wlan_Group',
                'Create WLAN Group %s' 
                % (wlan_group_name),
                0,
                False
                ))
    
    tcs.append(({'wlangroup_name':wlan_group_name,
                 'wlan_name_list': [wlan_cfg['ssid']]},
                'CB_ZD_Assign_Wlan_To_Wlangroup',
                'Assign Wlan %s to WLAN Group %s' 
                % (wlan_cfg['ssid'], wlan_group_name),
                0,
                False
                ))
    #@authon: Tanshixiong @since: 20150310 zf-12293
    for (ap_tag, ap_model) in ap_list:   
        tcs.append(({'ap_tag':ap_tag,'ap_model':ap_model},
                    'CB_ZD_AP_Group_Priority_Testing',
                    '[AP Group Priority Comparison-%s]Comparison to Priority'
                     % ap_tag,
                    1,
                    False
                    ))   
        
        tcs.append(({},
                    'CB_ZD_Remove_All_AP_Groups',
                    'Remove All AP Groups-%s' % ap_tag,
                    0,
                    False
                    ))       
    tcs.append(({},
                'CB_ZD_Remove_All_Wlan_Groups',
                'Remove All WLAN Groups',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Wlans',
                'Remove All WLANs',
                0,
                False
                ))
        
    return tcs
    

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "AP Group Combination-Priority Comparison",
                 )
    attrs.update(kwargs)
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ap_dict =tbcfg['ap_sym_dict']
    ap_list = []
    model_list = []
    aps = ap_dict.values()
    #@author: Tanshixiong @since 20150310 zf-12293
    ap_tag = ap_dict.keys()
    for tag in ap_tag:
        if ap_dict[tag]['model'] in model_list:
            continue
        else:
            ap_list.append((tag, ap_dict[tag]['model']))
            model_list.append(ap_dict[tag]['model'])
              
    if attrs["interactive_mode"]:
        ts_name = "AP Group Combination-Priority Comparison"        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "AP Group Combination-Priority Comparison",
                                 combotest=True)
                
    test_cfgs = create_tcs(ap_list)    
    
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
