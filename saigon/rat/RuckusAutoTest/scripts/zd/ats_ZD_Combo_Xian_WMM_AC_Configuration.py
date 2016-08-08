'''
Doc@https://jira-wiki.ruckuswireless.com/display/Team/Spectralink+Admission+Control
Topology:
    Zone Director----- L3 Switch --------AP

                        |

        DHCP/Radius Server/Win2003 web portal server

Created on 2012-10-31
@author: cwang@ruckuswireless.com
'''

from copy import deepcopy
import time
import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = dict(ssid = "rat-wlan-ac-%s" % (time.strftime("%H%M%S")),
                auth = "open",                 
                encryption = "none",                 
                ac = True,) 

gui_cfg_map = [({'ac':'10'},'[10% airtime usage limit]'),
               ({'ac':'70'},'[70% airtime usage limit]'),
               ({'ac':'40'},'[40% airtime usage limit]'),
               ]

ap_group_cfg_map = [({'ac':'10'},'[AP Group-10% airtime usage limit]'),
                    ({'ac':'70'},'[AP Group-70% airtime usage limit]'),
                    ({'ac':'30'},'[AP Group-30% airtime usage limit]'),
                    ]

cli_cfg_map = [({'ac':'10'},'[CLI-10% airtime usage limit]'),
               ({'ac':'70'},'[CLI-70% airtime usage limit]'),
               ({'ac':'60'},'[CLI-60% airtime usage limit]'),
               ]

def _setup_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_Remove_All_Wlans',
                'Remove all WLANs.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_AP_Groups',
                'Remove all AP Groups.',
                0,
                False
                ))
    return tcs

def _teardown_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_Remove_All_Wlans',
                'Clean up all WLANs.',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_AP_Groups',
                'Clean up all AP Groups.',
                0,
                True
                ))
    return tcs

def build_gui_tcs(ap_tag, radio):
    tcs = []
    tcs.extend(_setup_tcs())
    
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_Create_Wlans',
                'Create WLANs',
                0,
                False
                ))
    
    for _cfg, tcid in gui_cfg_map:
        ap_cfg = {'radio_config':{'%s'%radio: _cfg,'override_parent': True,}}
        tcs.append(({'ap_cfg':ap_cfg, 'ap_tag':ap_tag},
                    'CB_ZD_Config_AP',
                    '%sConfigure AP' % tcid,
                    1,
                    False
                    ))    
        tcs.append(({'ap_tag':ap_tag},
                    'CB_ZD_Get_AP_Cfg',
                    '%sGet AP Configuration' % tcid,
                    2,
                    False
                    ))
        
        tcs.append(({'ap_cfg':ap_cfg},
                    'CB_ZD_Verify_AP_Cfg',
                    '%sVerify AP Configuration' % tcid,
                    2,
                    False
                    ))
            
    tcs.extend(_teardown_tcs())
    return tcs


def build_cli_tcs(ap_tag, radio):
    tcs = []
    tcs.extend(_setup_tcs())
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_CLI_Create_Wlans',
                'Create a WLAN',
                0,
                False
                ))
    for radio_cfg, tcid in cli_cfg_map:
        ap_cfg = {'ap_tag':ap_tag,
                  'radio_%s'%radio:radio_cfg
                 }
        tcs.append(({'ap_cfg':ap_cfg, 'ap_tag':ap_tag},
                    'CB_ZD_CLI_Configure_AP',
                    '%sConfigure AP' % tcid,
                    1,
                    False
                    )) 
        
        tcs.append(({'ap_tag':ap_tag},
                    'CB_ZD_CLI_Get_AP_Config',
                    '%sGet AP Info' % tcid,
                    2,
                    False
                    ))
        
        tcs.append(({'ap_cfg':ap_cfg},
                    'CB_ZD_CLI_Verify_AP_Config',
                    '%sVerify AP Info' % tcid,
                    2,
                    False
                    ))
    
    tcs.extend(_teardown_tcs())
    
    return tcs

def build_ap_group(ap_tag, radio):
    tcs = []
    for cfg, tcid in ap_group_cfg_map:
        if radio in "ng":
            radio = "gn"
            
        tcs.append(({'name':'mytest',
                     'description':'mytest',
                     radio:cfg, 
                     'replace': True,
                     },
                    'CB_ZD_Create_AP_Group',
                    '%sCreate AP Group' % tcid,
                    1,
                    False
                    ))
#        tcs.append(({'name':'mytest'},
#                    'CB_ZD_CLI_Get_AP_Group',
#                    '%sGet AP Group' % tcid,
#                    2,
#                    False
#                    ))
#        tcs.append(({},
#                    'CB_ZD_CLI_Verify_AP_Group',
#                    '%sVerify AP Group' % tcid,
#                    2,
#                    False
#                    ))
        
        tcs.append(({'name':'mytest'},
                    'CB_ZD_Remove_AP_Group',
                    '%sRemove AP Group' % tcid,
                    2,
                    True
                    ))
    
    return tcs


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Xian-WMM-AC Configuration",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
        
    if attrs["interactive_mode"]:        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:        
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
       
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    ap_mac_addr = None
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            ap_mac_addr = ap_info.get('mac')            
            break
        
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
        
    ts_name_list = [('Xian WMM-AC AP Configuration-GUI', build_gui_tcs),                                        
                    ('Xian WMM-AC AP Configuration-CLI', build_cli_tcs),
                    ('Xian WMM-AC AP Group Configuration', build_ap_group),
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(active_ap, target_sta_radio)
    
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

