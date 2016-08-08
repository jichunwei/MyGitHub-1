'''
Test cases coverage:
    + Hotspot authentication with IAS
    + Hotspot authentication with freeradius
    + Hotspot authentication with AD
    
Created on 2011-7-14
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

#define an ID generator
def gen():
    k = 0
    while True:
        k += 1
        yield k
        
ID_GEN = gen().next


def build_tcs(target_station, target_station_radio, active_ap):
    '''
    + Hotspot authentication with IAS
    + Hotspot authentication with freeradius
    + Hotspot authentication with AD    
    '''    
    svr_list = [{
                    'server_name': 'AD',
                    'server_addr': '192.168.0.250',
                    'server_port': '389',
                    'win_domain_name': 'rat.ruckuswireless.com',  
                    'auth_info': {'username': 'ad.user', 'password': 'ad.user',}, 
                    'tcid': '[Hotspot authentication with AD]'                 
                },                                     
                {
                    'server_name': 'IAS',
                    'server_addr': '192.168.0.250',
                    'radius_auth_secret': '1234567890',
                    'server_port': '18120',
                    'auth_info': {'username': 'rad.cisco.user', 'password': 'rad.cisco.user'},
                    'tcid': '[Hotspot authentication with IAS]'
                },                
                {
                    'server_name': 'freeradius',
                    'server_addr': '192.168.0.252',
                    'radius_auth_secret': '1234567890',
                    'server_port': '1812',
                    'auth_info': {'username': 'rad.cisco.user', 'password': 'rad.cisco.user',},
                    'tcid' : '[Hotspot authentication with freeradius]'
                },                        
                ] 
    
    
    open_wlan = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test')
    
    def_test_params = {'target_station': target_station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
            
    
    test_cfgs = []
    
    test_cfgs.extend(clean_steps(LEVEL = 0))
        
    
    test_cfgs.append(({'hotspot_profiles_list': [deepcopy(def_test_params['hotspot_cfg'])]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot',
                      0, 
                      False,                      
                      ))
    
    test_cfgs.append(({'wlan_cfg_list':[open_wlan]},
                      'CB_ZD_Create_Wlan',
                      'Create wlan',
                      0, 
                      False,
                      ))
    
    
    test_cfgs.append(({}, 
                     'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group', 
                     'Remove all wlans out of default', 
                     0, 
                     False,
                     ))
    
       
    test_cfgs.append(({'wlangroups_map':{'wg_1':open_wlan['ssid'],                                         
                                        }}, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLANGroup and WLAN in pair', 
                      0, 
                      False))
    

    param_cfg = dict(active_ap = active_ap)
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Find_Active_AP', 
                      'Create an Active AP', 
                      0, 
                      False))
    
    test_cfgs.append(({'ap_tag': 'tap', 
                       'active_ap': active_ap}, 
                      'CB_ZD_Create_Active_AP', 
                      'Get the active AP', 
                      1, 
                      False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       1, 
                       False))
             
    
    for svr in svr_list:
        auth_info = svr.pop('auth_info')
        tcid = svr.pop('tcid')
        test_cfgs.append((dict(auth_ser_cfg_list = [svr]),
                      'CB_ZD_Create_Authentication_Server',
                      'Create aaa server %s' % svr['server_name'],
                      1,
                      False,
                      ))
        h_cfg = deepcopy(def_test_params['hotspot_cfg'])
        h_cfg['auth_svr'] = svr['server_name']
        test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      'Update hotspot profile',
                      1,
                      False,
                      )) 
        
        test_cfgs.extend(encode_tcid(tcid, station_steps(active_ap, 
                                               target_station, 
                                               target_station_radio, 
                                               open_wlan, 
                                               'wg_1', 
                                               auth_info)))    
           
    test_cfgs.extend(clean_steps(LEVEL = 1))
                
    
    return test_cfgs
    
def clean_steps(LEVEL = 0):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup ENV', 
            LEVEL, 
            False),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup ENV', 
            LEVEL, 
            False),            
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles', 
            LEVEL, 
            False),            
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers',
             LEVEL,
             False)
            ]
    
def station_steps(active_ap, sta, radio, wlan, wg, auth_info):
    test_cfgs = []
    test_cfgs.extend(station_a_steps(active_ap, sta, radio, wlan, wg))
    test_cfgs.extend(station_c_steps(auth_info))    
    test_cfgs.extend(station_p_steps(active_ap, radio, wlan, auth_info))
    return test_cfgs

    
def station_a_steps(active_ap, sta, radio, wlan, wg):
    test_cfgs = []
    param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = wg, 
                     radio_mode = radio)    
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Associate AP with radio %s to %s' % (radio, wg), 
                      1, 
                      False))        
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': wlan}, 
                      'CB_ZD_Associate_Station_1', 
                      'Associate the station', 
                      1, 
                      False))    

    
    test_cfgs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get wifi address', 
                      1, 
                      False))
    
    test_cfgs.append(({'sta_tag': 'sta_1'},
                      'CB_Station_CaptivePortal_Start_Browser',
                      'Open authentication web page',
                      1,
                      False,
                      ))
     
    param_cfg = {'wlan_cfg':wlan, 
                 'chk_empty':False, 
                 'status':'Unauthorized',
                 'chk_radio':False,
                 'radio_mode':radio,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                 
                 }
    test_cfgs.append((param_cfg,                        
                      'CB_ZD_Verify_Station_Info_V2',
                      'Verify the station before hotspot auth', 
                      2, 
                      False)) 
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'disallowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       'The station ping a target IP', 
                       2, 
                       False))
        
    return test_cfgs 

def station_c_steps(auth_info):
    test_cfgs = []
    param_cfgs = {'sta_tag':'sta_1'}
    param_cfgs.update(auth_info)
    test_cfgs.append((param_cfgs, 
                      'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                      'Perform Hotspot authentication', 
                      1, 
                      False)) 
    return test_cfgs

def station_p_steps(active_ap, radio, wlan, auth_info):
    test_cfgs = []
    param_cfg = {'wlan_cfg':wlan, 
                 'chk_empty':False, 
                 'status':'Authorized',
                 'chk_radio':False,
                 'radio_mode':radio,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                                  
                 'username':auth_info['username']}  
      
    test_cfgs.append((param_cfg,                        
                      'CB_ZD_Verify_Station_Info_V2',
                      'Verify the station after hotspot auth', 
                      2,
                      False))
    
    test_cfgs.append(({'sta_tag':'sta_1'},
                     'CB_Station_CaptivePortal_Download_File',
                     'Download files from server',
                     2,
                     False
                     ))  
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                     'condition': 'allowed',
                     'target': '172.126.0.252',},
                     'CB_ZD_Client_Ping_Dest', 
                     'The station ping a target IP', 
                     2, 
                     False))
    
    test_cfgs.append(({'sta_tag':'sta_1'},
                      'CB_Station_CaptivePortal_Quit_Browser',
                      'Close Authentication browser',
                      1,
                      False,
                      ))
    
    param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = 'Default', 
                     radio_mode = radio)           
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Associate AP with radio %s to %s' % (radio, 'Default'), 
                      1, 
                      False))    
    return test_cfgs    

def encode_tcid(tcid, test_cfgs):
    #append test cases identifier.
    if tcid:
        test_cfgs_copy = []
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:            
            common_name = '%s%s' % (tcid, common_name)
            test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup)) 
        return test_cfgs_copy
        
    return test_cfgs  

def decorate_common_name(test_cfgs):
    test_cfgs_copy = []
    
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
                            
        common_name = _get_common_name(common_name)
        test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup))
                    
    return test_cfgs_copy    
 

def _get_common_name(common_name):
    b_index = common_name.find('[')
    e_index = common_name.find(']')
    if b_index >=0 and e_index > b_index:        
        return '[%s]%s.%s'% (common_name[b_index+1:e_index], ID_GEN(), common_name[e_index+1:])
    else:
        return '%s.%s' % (ID_GEN(), common_name) 
    

def create_test_suite(**kwargs):
    STA_INDEX = 0
    STA_RADIO_INDEX = 1
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "Palo Alto WISPr AAA Servers - 11g",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:        
        target_sta = sta_ip_list[attrs["station"][STA_INDEX]]
        target_sta_radio = attrs["station"][STA_RADIO_INDEX]
        
        
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break
    if not active_ap:
        raise Exception('Have not found valid AP model')                
        

    ap_model = ap_sym_dict[active_ap]['model']
    
    if attrs["interactive_mode"]:
        ts_name = "Palo Alto WISPr AAA Servers  - 11%s, %s" % (target_sta_radio, ap_model)        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "Palo Alto WISPr AAA Servers  - 11%s, %s" % (target_sta_radio, ap_model), 
                                 combotest=True)
                
    test_cfgs = build_tcs(target_sta, target_sta_radio, active_ap)
    test_cfgs = decorate_common_name(test_cfgs)
    
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
