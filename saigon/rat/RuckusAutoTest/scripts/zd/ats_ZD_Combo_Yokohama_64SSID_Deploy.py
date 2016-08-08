"""
Suite including 64SSIDs basic test cases, 
ZF2942, ZF7962 required.
2 Clients required.
"""
from copy import deepcopy
import time
import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

def _build_tcs(apcfg_list):
    """
    +Create more 32 SSIDs
    +Create wlan-groups Default, test1, test2, test3:
        Default assign 26 SSIDS
        test1 assign 8 SSIDs
        test2 assign 26 SSIDs
        test3 assign 26 SSIDs
    +AP assign Default WLAN Group on Radio 2.4/5.0G:
        Verify 26 SSIDs can deploy to Radio 2.4/5G
    +AP assign test1 WLAN Group on Radio 2.4/5.0G:
        Verify 8 SSIDs can deploy to Radio 2.4/5G
        Verify other SSIDs status are DONE.
    +AP assign test2 WLAN Group on Radio 2.4/5.0G:
        Verify 26 SSIDs can deploy to Radio 2.4/5G
    +AP assign Default WLAN Group back to Radio 2.4/5G:
        Verify 26 SSIDs can deploy to Radio 2.4/5G
    +Clean up WLAN Groups
    +Clean up WLANs 
    +Check all of SSIDs status are DOWN
    """
    wlans = [dict(ssid = "RAT-Open-None-%d" % i, name= "RAT-Open-None-%d" % i,
                   auth = "open", encryption = "none") for i in range(32)]
    
    def generate_wlan_groups(wlans):
        group = {'wg_name':'test1', 'wlan_member':{}}
        for wlan in wlans[:8]:
            group['wlan_member'].update({wlan['ssid']:{}})
        
        group2 = {'wg_name':'test2', 'wlan_member':{}}
        for wlan in wlans[:27]:
            group2['wlan_member'].update({wlan['ssid']:{}})
        
        group3 = {'wg_name':'test3', 'wlan_member':{}}
        for wlan in wlans[:27]:
            group3['wlan_member'].update({wlan['ssid']:{}})
        
        return [group, group2, group3]
    
    tcs = []
    for ap in apcfg_list:
        model = ap['model']
        if lib_Constant.is_ap_support_11n(model):
            cfg = {'mac_addr': '%s' % ap['mac'],      
                   'radio_ng': {'wlangroups': 'Default'},
                   'radio_na': {'wlangroups': 'Default'},
                   }
        else:
            cfg = {'mac_addr': '%s' % ap['mac'],      
                   'radio_ng': {'wlangroups': 'Default'},                   
                   }
        tcs.append(({'ap_cfg':cfg},
                    'CB_ZD_CLI_Configure_AP',
                    'Set AP %s WLAN Group to Default' % ap['mac'],
                    0,
                    False
                    ))
    
        tcs.append(({'active_ap':ap['mac'],
                     'ap_tag': ap['ap_tag']
                     },
                    'CB_ZD_Create_Active_AP',
                    'Create Active AP %s' % ap['ap_tag'],
                    0,
                    False
                    ))
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_All_WLAN_Groups',
                'Remove all WLAN Groups',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Remove all Wlans',
                0,
                False
                ))
    
    tcs.append(({'wlan_cfg_list':wlans},
                'CB_ZD_CLI_Create_Wlans',
                'Create WLANs',
                0,
                False
                ))
    
    tcs.append(({'wlan_group_cfg_list':generate_wlan_groups(wlans)},
                'CB_ZD_CLI_Create_WLAN_Groups',
                'Create WLAN Groups',
                0,
                False
                ))
    
    def _generate(apcfg_list, tcid, num_of_ssids, wlan_group):    
        tcs = []
        for ap in apcfg_list:
            model = ap['model']
            if lib_Constant.is_ap_support_11n(model):
                cfg = {'mac_addr': '%s' % ap['mac'],      
                       'radio_ng': {'wlangroups': '%s' % wlan_group},
                       'radio_na': {'wlangroups': '%s' % wlan_group},
                       }
            else:
                cfg = {'mac_addr': '%s' % ap['mac'],      
                       'radio_ng': {'wlangroups': '%s' % wlan_group},                   
                       }
                
            tcs.append(({'ap_cfg':cfg},
                        'CB_ZD_CLI_Configure_AP',
                        '%sSet AP %s WLAN Group to test1' % (tcid, ap['mac']),
                        0,
                        False
                        ))
            
        
        for ap in apcfg_list:
            model = ap['model']    
            maxinum_of_ssids = lib_Constant.get_maxinum_of_ssids_by_model(model)            
            if lib_Constant.is_ap_support_dual_band(model):    
                num_of_ssids = maxinum_of_ssids if num_of_ssids *2 > maxinum_of_ssids else num_of_ssids * 2
                cfg = {'ap_tag':ap['ap_tag'],
                       'num_of_ssids':num_of_ssids
                       }
            else:
                num_of_ssids = maxinum_of_ssids if num_of_ssids > maxinum_of_ssids else num_of_ssids
                cfg = {'ap_tag':ap['ap_tag'],
                       'num_of_ssids':num_of_ssids
                       }
                
            tcs.append((cfg,
                        'CB_AP_CLI_Check_Wlans',
                        '%sVerify AP Configuration' % tcid,
                        2,
                        False
                        ))
        return tcs
    
    tcid = '[AP assign Default WLAN Group on Radio 2.4/5.0G]'
    tcs.extend(_generate(apcfg_list, tcid, 27, 'Default'))
    
    tcid = '[AP assign WLAN Group with 8 WLANs on Radio 2.4/5.0G]'
    tcs.extend(_generate(apcfg_list, tcid, 8, 'test1'))
    
    tcid = '[AP assign WLAN Group with 26 WLANs on Radio 2.4/5.0G]'
    tcs.extend(_generate(apcfg_list, tcid, 27, 'test2'))
    
    
    tcid = '[AP Move WLAN Group with 26 WLANs on Radio 2.4/5.0G]'
    tcs.extend(_generate(apcfg_list, tcid, 27, 'test3'))
    
    
    tcid = '[AP Move WLAN Group with Default on Radio 2.4/5.0G]'
    tcs.extend(_generate(apcfg_list, tcid, 27, 'Default'))
    
    for ap in apcfg_list:
        model = ap['model']
        if lib_Constant.is_ap_support_11n(model):
            cfg = {'mac_addr': '%s' % ap['mac'],      
                   'radio_ng': {'wlangroups': 'Default'},
                   'radio_na': {'wlangroups': 'Default'},
                   }
        else:
            cfg = {'mac_addr': '%s' % ap['mac'],      
                   'radio_ng': {'wlangroups': 'Default'},                   
                   }
        tcs.append(({'ap_cfg':cfg},
                    'CB_ZD_CLI_Configure_AP',
                    'Restore AP %s WLAN Group to Default' % ap['mac'],
                    0,
                    True
                    ))
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_All_WLAN_Groups',
                'Cleanup all WLAN Groups',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Cleanup all Wlans',
                0,
                True
                ))
    
    return tcs



def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Yokohama-64 SSIDs Deploy",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
       
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    apcfg_list = []
    models = [] 
    for ap_tag in ap_sym_dict:
        ap = {}
        ap['ap_tag'] = ap_tag
        ap['mac'] = ap_sym_dict[ap_tag]['mac']
        ap['model'] = ap_sym_dict[ap_tag]['model']
        if ap['model'] not in models:
            apcfg_list.append(ap)
            models.append(ap['model'])
    
    ts_name_list = [('Yokohama-64 SSIDs Deploy', _build_tcs),                                                                            
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(apcfg_list)
    
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
    
