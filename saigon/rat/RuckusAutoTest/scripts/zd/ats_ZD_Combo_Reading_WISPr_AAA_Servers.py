'''
Test cases coverage:
    + Hotspot authentication with IAS
    + Hotspot authentication with freeradius
    + Hotspot authentication with AD
    
Created on 2011-9-2
@author: serena.tan@ruckuswireless.com
'''


import sys
from copy import deepcopy
import re
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


def build_tcs(target_station, target_station_radio, active_ap):    
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
                    'auth_info': {'username': 'rad.cisco.user', 'password': 'rad.cisco.user'},
                    'tcid' : '[Hotspot authentication with freeradius]'
                },                        
                ] 
    
    open_wlan = dict(ssid = "RAT-Open-None-%s" % time.strftime("%H%M%S"), 
                     auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test')
    
    def_test_params = {'target_station': target_station, 
                       'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'https://192.168.0.250/slogin.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
            
    test_cfgs = []

    test_cfgs.append(({'ap_tag': 'tap', 
                       'active_ap': active_ap}, 
                       'CB_ZD_Create_Active_AP', 
                       'Get the active AP', 
                       0, 
                       False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       0, 
                       False))
    
    test_cfgs.append(({},
                       'CB_ZD_Remove_All_Config', 
                       'Remove all configuration from ZD', 
                       0, 
                       False))
    
    test_cfgs.append(({'hotspot_profiles_list': [deepcopy(def_test_params['hotspot_cfg'])]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot profile',
                      0, 
                      False,                      
                      ))
    
    test_cfgs.append(({'wlan_cfg_list':[open_wlan]},
                      'CB_ZD_Create_Wlan',
                      'Create a wlan',
                      0, 
                      False,
                      ))
    
    test_cfgs.append(({}, 
                     'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group', 
                     'Remove all wlans from Default wlan group', 
                     0, 
                     False,
                     ))
       
    test_cfgs.append(({'wlangroups_map':{'wg_1':open_wlan['ssid'],                                         
                                        }}, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLAN Group and WLAN in pair', 
                      0, 
                      False))
    
    for svr in svr_list:
        auth_info = svr.pop('auth_info')
        tcid = svr.pop('tcid')
        test_cfgs.append((dict(auth_ser_cfg_list = [svr]),
                      'CB_ZD_Create_Authentication_Server',
                      '%sCreate server %s' % (tcid, svr['server_name']),
                      1,
                      False,
                      ))
        
        h_cfg = deepcopy(def_test_params['hotspot_cfg'])
        h_cfg['auth_svr'] = svr['server_name']
        test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                          'CB_ZD_Edit_Hotspot_Profiles',
                          '%sUpdate hotspot profile' % tcid,
                           2,
                           False,
                           )) 
        
        test_cfgs.extend(encode_tcid(tcid, station_steps(active_ap,
                                                         target_station,
                                                         target_station_radio, 
                                                         open_wlan,
                                                         'wg_1', 
                                                         auth_info)))    
           
    test_cfgs.extend(clean_steps(Clean_up = True))
    
    return test_cfgs
    
    
def clean_steps(LEVEL = 0, Clean_up = False):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup', 
            LEVEL, 
            Clean_up),              
            
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup', 
            LEVEL, 
            Clean_up),    
                    
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles for cleanup', 
            LEVEL, 
            Clean_up),  
                      
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers for cleanup',
             LEVEL,
             Clean_up)
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
                      'Assign AP radio %s to %s' % (radio, wg), 
                      2, 
                      False))        
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': wlan}, 
                      'CB_ZD_Associate_Station_1', 
                      'Associate the station', 
                      2, 
                      False))    

    test_cfgs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get station wifi address', 
                      2, 
                      False))
    
    test_cfgs.append(({'sta_tag': 'sta_1'},
                      'CB_Station_CaptivePortal_Start_Browser',
                      'Open authentication web page',
                      2,
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
                      'Verify station info before hotspot auth', 
                      2, 
                      False)) 
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'disallowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       'Station ping target IP before hotspot auth', 
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
                      2, 
                      False)) 
    return test_cfgs


def station_p_steps(active_ap, radio, wlan, auth_info):
    test_cfgs = []
    param_cfg = {'wlan_cfg': wlan, 
                 'chk_empty': False, 
                 'status': 'Authorized',
                 'chk_radio': False,
                 'radio_mode': radio,
                 'sta_tag': 'sta_1',
                 'ap_tag': 'tap',                                  
                 'username': auth_info['username']}  
      
    test_cfgs.append((param_cfg,                        
                      'CB_ZD_Verify_Station_Info_V2',
                      'Verify station info after hotspot auth', 
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
                     'Station ping target IP after hotspot auth', 
                     2, 
                     False))
    
    test_cfgs.append(({'sta_tag':'sta_1'},
                      'CB_Station_CaptivePortal_Quit_Browser',
                      'Close Authentication browser',
                      2,
                      True,
                      ))
    
    param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = 'Default', 
                     radio_mode = radio)           
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Assign AP radio %s to Default wlan group' % radio, 
                      2, 
                      True))    
    
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
    

def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_station = (0, "ng"),
                 ts_name = ""
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an active AP: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            
            else:
                break
            
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio() 
        
    else:
        active_ap = attrs["active_ap"]
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if target_sta_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, target_sta_radio)
        return

    test_cfgs = build_tcs(sta_ip_addr, target_sta_radio, active_ap)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        active_ap_status = ap_sym_dict[active_ap]['status']
        active_ap_role = ''
        res = re.search('Connected \((.+)\)', active_ap_status, re.I)
        if res:
            active_ap_role = ' - %s' % res.group(1).split(' ')[0]
            
        ts_name = "Reading WISPr AAA Servers - %s" % target_sta_radio
        #ts_name = "Reading WISPr AAA Servers - %s%s - %s" % (active_ap_model, active_ap_role, target_sta_radio)

    ts = testsuite.get_testsuite(ts_name, 
                                 'Verify Reading WISPr with AAA servers',
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest = True)
                
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
