"""
Topos:
    ZD ---- SW --- AP )))) Station

Test Scenarios:
    1) Change countrycode to BH/KE/QA, make sure AP can join, station can associate.
    2) Attribute test:
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


def generate_data_plane(tcid, wlan_cfg, ap_tag, radio_mode, 
                                sta_tag='sta1',
                                target_ip_addr = '192.168.0.252'
                                ):
    tcs = []
    tcs.append(({'wlan_cfg': wlan_cfg,'sta_tag': sta_tag}, 
                'CB_ZD_Associate_Station_1', 
                '%sAssociate the station to the WLAN' % tcid, 
                2,
                False))

    tcs.append(({'sta_tag': sta_tag}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      '%sGet WiFi address of the station' % (tcid), 
                      2, 
                      False))                        
    
    tcs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':radio_mode,},
                       'CB_ZD_Verify_Station_Info_V2', 
                       '%sCheck if authorzied' % (tcid), 
                       2, 
                       False))
           
    tcs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, 
                       'CB_ZD_Client_Ping_Dest', 
                       '%sVerify client can ping a target IP' % (tcid,), 
                       2, 
                       False))
    
    return tcs

def _build_basic_test(active_ap, target_station):
    """
    1)Change countrycode to BH/KE/QA, make sure AP can join, station can associate.        
    """
    tcs = []
    
    def generate_wlan():
        cc_wlan_24 = dict(ssid = "RAT-Open-None-cc24", 
             name= "RAT-Open-None-cc24",
             auth = "open", encryption = "none",
             bgscan = True,
             )

        cc_wlan_5g = dict(ssid = "RAT-Open-None-cc5g", 
             name= "RAT-Open-None-cc5g",
             auth = "open", encryption = "none",
             bgscan = True,
             )

        cc_wlan_default = dict(ssid = "RAT-Open-None-Default", 
             name= "RAT-Open-None-Default",
             auth = "open", encryption = "none",
             bgscan = False,
             )
        return (cc_wlan_24, cc_wlan_5g, cc_wlan_default)
    
    def generate_wlan_groups(wlans):
        (cc_wlan_24, cc_wlan_5g, cc_wlan_default) = wlans
        default = {'wg_name':'test1', 'wlan_member':{cc_wlan_default['ssid']:{}}}        
                
        g24 = {'wg_name':'test2', 'wlan_member':{}}        
        g24['wlan_member'].update({cc_wlan_24['ssid']:{}})
        
        g5 = {'wg_name':'test3', 'wlan_member':{}}        
        g5['wlan_member'].update({cc_wlan_5g['ssid']:{}})
        
        return (default, g24, g5)#(default, 2.4, 5)
    
    def generate_id_list(wlan, wgs, ap_mac):            
        return (("[BH with 2.4 enable background scan]",'BH', 'Bahrain', wlan[0],'ng',
                 {'radio_ng': {'wlangroups': '%s' % wgs[1]['wg_name']}}),
                ("[BH with 5 enable background scan]",'BH', 'Bahrain',wlan[1],'na',
                 {'radio_na': {'wlangroups': '%s' % wgs[2]['wg_name']}}),
                ("[BH with 5 disable background scan]", 'BH', 'Bahrain',wlan[2],'na',
                 {'radio_na': {'wlangroups': '%s' % wgs[0]['wg_name']}}),
                #@ZJ 20140918  ZF-10099
#                ("[KE with 2.4 enable background scan]",'KE', 'Kenya', wlan[1],'ng',
                ("[KE with 2.4 enable background scan]",'KE', 'Kenya', wlan[0],'ng',
                 {'radio_ng': {'wlangroups': '%s' % wgs[1]['wg_name']}}),
                ("[KE with 5 enable background scan]",'KE', 'Kenya', wlan[1],'na',
                 {'radio_na': {'wlangroups': '%s' % wgs[2]['wg_name']}}),
                ("[KE with 5 disable background scan]",'KE', 'Kenya', wlan[2],'na',
                 {'radio_na': {'wlangroups': '%s' % wgs[0]['wg_name']}}),
                
                ("[QA with 2.4 enable background scan]",'QA', 'Qatar', wlan[0],'ng',
                 {'radio_ng': {'wlangroups': '%s' % wgs[1]['wg_name']}}
                 ),
                ("[QA with 5 enable background scan]",'QA', 'Qatar', wlan[1],'na',
                 {'radio_na': {'wlangroups': '%s' % wgs[2]['wg_name']}}
                 ),
                ("[QA with 5 disable background scan]",'QA', 'Qatar', wlan[2],'na',
                 {'radio_na': {'wlangroups': '%s' % wgs[0]['wg_name']}}
                 ),               
         )
        
    wlans = generate_wlan()
    wgs = generate_wlan_groups(wlans)
    params = generate_id_list(wlans, wgs, active_ap['mac'])
    
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
    
    tcs.append(({'wlan_group_cfg_list':wgs},
                'CB_ZD_CLI_Create_WLAN_Groups',
                'Create WLAN Groups',
                0,
                False
                ))
    
    ap_tag = active_ap['ap_tag']
    tcs.append(({'active_ap':ap_tag,
                       'ap_tag': ap_tag}, 
                       'CB_ZD_Create_Active_AP', 
                       'Create active AP', 
                       0, 
                       False))
    
    #@ZJ @since20141115 ZF-10286
    tcs.append(({'cfg_type': 'teardown',
                       'all_ap_mac_list': ''}, 
                       'CB_ZD_Config_AP_Radio', 
                       'Config All APs Radio - Enable WLAN Service', 
                       0, 
                       False))
    #@ZJ @since20141115 ZF-10286
           
    tcs.append(({'sta_ip_addr':target_station,
                       'sta_tag': 'sta1'}, 
                       'CB_ZD_Create_Station', 
                       'Create target station', 
                       0, 
                       False))
    
    for tcid, cc, ccalias, wlan_cfg, radio_mode, ap_cfg in params:
        tcs.append(({'ap_tag':active_ap['ap_tag'] ,'ap_cfg':ap_cfg},
                    'CB_ZD_CLI_Configure_AP',
                    '%sSet AP %s WLAN Group' % (tcid, active_ap['ap_tag']),#Chico, 2014-10-21, fix bug ZF-10097
                    0,
                    False
                    ))
        
        tcs.append(({'cc':cc,  
                     'ccalias':ccalias                   
                     },
                    'CB_ZD_CLI_Set_AP_CountryCode',
                    '%sSet countrycode' % tcid,
                    1,
                    False
                    ))                         
        
        tcs.extend(generate_data_plane(tcid, 
                                       wlan_cfg, 
                                       ap_tag, 
                                       radio_mode))
        
        tcs.append(({'cc':'US',
                     'ccalias':'United States',
                     },
                    'CB_ZD_CLI_Set_AP_CountryCode',
                    '%sSet back to default countrycode' % tcid,
                    0,
                    True
                    ))
        
        tcs.append(({},
                    'CB_ZD_CLI_Default_Wlan_Group_From_AP_CFG',
                    '%sDefault WLAN Group' % tcid,
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
    

def _build_attribute_test():
    pass

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
                 testsuite_name = "Zurich BH KE QA CountryCode - Basic",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        target_sta_radio = testsuite.get_target_sta_radio()
    else:        
        target_sta = sta_ip_list[ts_cfg["station"][0]]
#        target_sta_radio = ts_cfg["station"][1]
        
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
    
    ts_name_list = [('Zurich BH KE QA CountryCode - Basic', _build_basic_test),                                                                            
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(apcfg_list[0], target_sta)
    
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

