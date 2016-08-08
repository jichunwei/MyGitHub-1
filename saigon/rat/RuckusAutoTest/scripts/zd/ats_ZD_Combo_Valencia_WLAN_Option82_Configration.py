'''
1) Verify default setting of dhcp option82 from ZD WebUI and CLI.
2) Verify commands to enable/disable dhcp option82 from ZDCLI.
3) Verify dhcp option82 could be enabled/disabled via ZD WebUI properly.
4) Verify dhcp option82 is matching between CLI and WebUI.
5) Verify dhcp option82 is not lost after ZD reboot.

Created on 2012-2-15
@author: cwang@ruckuswireless.com
'''


import time
import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = {"name" : "RAT-Open-None-Option82-Testing",
            "ssid" : "RAT-Open-None-Option82-Testing",
            "auth" : "open",
            "encryption" : "none",
            "option82":None,
            }

def build_tcs():
    tcs = []    
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Remove All WLAN Groups',
                0,
                False))
    
                  
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
    
    default_cfg = deepcopy(wlan_cfg)
    tcs.append(({'wlan_cfg_list':[default_cfg]},
                'CB_ZD_Create_Wlan',
                'Create WLAN from GUI',
                1,
                False
                ))
    
    tcs.append(({'wlan_name': default_cfg['name']},
                'CB_ZD_Get_Wlans_Info',
                '[Default Option82 Setting]Get WLAN info from ZD GUI',
                2,
                False
                ))
    
    tcs.append(({'ssid':default_cfg['name']},
                'CB_ZDCLI_Get_Wlan',
                '[Default Option82 Setting]Get WLAN info from ZD CLI',
                2,
                False
                )
               )
    
    tcs.append(({'wlan_cfg':default_cfg},
                'CB_ZD_ZDCLI_Verify_Wlan_Option82',
                '[Default Option82 Setting]Verify Option82 info between GUI and CLI',
                2,
                False
                ))
    
    
    cli_enable_cfg = deepcopy(wlan_cfg)
    cli_enable_cfg['option82'] = True
    tcs.append(({'wlan_cfg':cli_enable_cfg},
                'CB_ZD_CLI_Configure_WLAN',
                '[Enable Option82 Setting in CLI]enable dhcp option82 from CLI',
                1,
                False
                ))
    
    
    tcs.append(({'wlan_name': cli_enable_cfg['name']},
                'CB_ZD_Get_Wlans_Info',
                '[Enable Option82 Setting in CLI]get wlans info from GUI',
                2,
                False
                ))
    
    tcs.append(({'ssid':cli_enable_cfg['name']},
                'CB_ZDCLI_Get_Wlan',
                '[Enable Option82 Setting in CLI]Get WLAN info from ZD CLI',
                2,
                False
                )
               )
    
    tcs.append(({'wlan_cfg':cli_enable_cfg},
                'CB_ZD_ZDCLI_Verify_Wlan_Option82',
                '[Enable Option82 Setting in CLI]verify wlans info from GUI and CLI',
                2,
                False
                ))
    
    
    cli_disable_cfg = deepcopy(wlan_cfg)
    cli_disable_cfg['option82'] = False
    tcs.append(({'wlan_cfg':cli_disable_cfg},
                'CB_ZD_CLI_Configure_WLAN',
                '[Disable Option82 Setting in CLI]disable dhcp option82 from CLI',
                1,
                False
                ))
    
    tcs.append(({'wlan_name': cli_disable_cfg['name']},
                'CB_ZD_Get_Wlans_Info',
                '[Disable Option82 Setting in CLI]get wlans info from GUI',
                2,
                False
                ))
    
    tcs.append(({'ssid':cli_disable_cfg['name']},
                'CB_ZDCLI_Get_Wlan',
                '[Disable Option82 Setting in CLI]Get WLAN info from ZD CLI',
                2,
                False
                )
               )
    
    tcs.append(({'wlan_cfg':cli_disable_cfg},
                'CB_ZD_ZDCLI_Verify_Wlan_Option82',
                '[Disable Option82 Setting in CLI]verify wlans info from GUI and CLI',
                2,
                False
                ))
    
    
    
    gui_enable_cfg = deepcopy(wlan_cfg)
    gui_enable_cfg['option82'] = True 
    tcs.append(({'wlan_cfg_list':[gui_enable_cfg]},
                'CB_ZD_Create_Wlan',
                '[Enable Option82 Setting in GUI]enable dhcp option82 from GUI',
                1,
                False
                ))
    
    
    tcs.append(({'wlan_name': gui_enable_cfg['name']},
                'CB_ZD_Get_Wlans_Info',
                '[Enable Option82 Setting in GUI]get wlans info from GUI',
                2,
                False
                ))
    
    tcs.append(({'ssid':gui_enable_cfg['name']},
                'CB_ZDCLI_Get_Wlan',
                '[Enable Option82 Setting in GUI]Get WLAN info from ZD CLI',
                2,
                False
                )
               )
    
    tcs.append(({'wlan_cfg':gui_enable_cfg},
                'CB_ZD_ZDCLI_Verify_Wlan_Option82',
                '[Enable Option82 Setting in GUI]verify wlans info from GUI and CLI',
                2,
                False
                ))
    
    
    gui_disable_cfg = deepcopy(wlan_cfg)
    gui_disable_cfg['option82'] = False 
    tcs.append(({'wlan_cfg_list': [gui_disable_cfg]},
                'CB_ZD_Create_Wlan',
                '[Disable Option82 Setting in GUI]disable dhcp option82 from GUI',
                1,
                False
                ))
    
    
    tcs.append(({'wlan_name': gui_disable_cfg['name']},
                'CB_ZD_Get_Wlans_Info',
                '[Disable Option82 Setting in GUI]get wlans info from GUI',
                2,
                False
                ))
    
    
    tcs.append(({'ssid':gui_disable_cfg['name']},
                'CB_ZDCLI_Get_Wlan',
                '[Disable Option82 Setting in GUI]Get WLAN info from ZD CLI',
                2,
                False
                )
               )
    
    
    tcs.append(({'wlan_cfg':gui_disable_cfg},
                'CB_ZD_ZDCLI_Verify_Wlan_Option82',
                '[Disable Option82 Setting in GUI]verify wlans info from GUI and CLI',
                2,
                False
                ))    
    
    rwlan_cfg = deepcopy(wlan_cfg)
    rwlan_cfg['option82'] = True 
    tcs.append(({'wlan_cfg': rwlan_cfg},
                'CB_ZD_CLI_Configure_WLAN',
                '[Reboot and Check Option82 Setting]enable dhcp option82 from CLI',
                1,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Reboot',
                '[Reboot and Check Option82 Setting]ZD reboot',
                1,
                False
                ))
    
    tcs.append(({'wlan_name': rwlan_cfg['name']},
                'CB_ZD_Get_Wlans_Info',
                '[Reboot and Check Option82 Setting]get wlans info from GUI',
                2,
                False
                ))
    
    
    tcs.append(({'ssid':rwlan_cfg['name']},
                'CB_ZDCLI_Get_Wlan',
                '[Reboot and Check Option82 Setting]Get WLAN info from ZD CLI',
                2,
                False
                )
               )
    
    
    tcs.append(({'wlan_cfg':rwlan_cfg},
                'CB_ZD_ZDCLI_Verify_Wlan_Option82',
                '[Reboot and Check Option82 Setting]verify wlans info from GUI and CLI',
                2,
                False
                ))   
        
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Clean All WLAN Groups',
                0,
                False))
    
                  
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                False))    
    
        
    return tcs


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Valencia DHCP option82 configuration",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
       
    if attrs["interactive_mode"]:
        ts_name = "Valencia DHCP option82 configuration"        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "Valencia DHCP option82 configuration", 
                                 combotest=True)
                
    test_cfgs = build_tcs()

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
    create_test_suite(**_dict)
    