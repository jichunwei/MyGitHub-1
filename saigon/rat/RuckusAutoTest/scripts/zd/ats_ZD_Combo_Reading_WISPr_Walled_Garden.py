'''
Test cases coverage:
    + Walled Garden function
    + Maximum Walled Garden entries
    
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
    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    
    open_wlan = dict(ssid = "RAT-Open-None-%s" % time.strftime("%H%M%S"),
                     auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test')
    
    def_test_params = {'target_station': target_station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'https://192.168.0.250/slogin.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
        
    test_cfgs = []

    test_cfgs.append(({'sta_tag': 'sta_1', 'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the target station', 
                       0, 
                       False))
     
    test_cfgs.append(({'ap_tag': 'tap', 'active_ap': active_ap}, 
                      'CB_ZD_Create_Active_AP', 
                      'Get the active AP', 
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
    
    test_cfgs.append(({'username': 'local.username',
                       'password': 'local.password'},
                      'CB_ZD_Create_Local_User',
                      'Create a local user',
                      0, 
                      False,
                      ))
        
    test_cfgs.append(({'wlan_cfg_list': [open_wlan]},
                      'CB_ZD_Create_Wlan',
                      'Create a hotspot wlan',
                      0, 
                      False,
                      ))
    
    test_cfgs.append(({}, 
                     'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group', 
                     'Remove all wlans out of Default wlan group', 
                     0, 
                     False,
                     ))
    
    test_cfgs.append(({'wlangroups_map': {'wg_1': open_wlan['ssid'], 
                                          }}, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLAN Group and WLAN in pair', 
                      0, 
                      False))

    for item in [{"[Walled Garden function]": walled_garden_entries[:3]},
                 {"[Maximum Walled Garden entries]": walled_garden_entries}]:    
        tcid = item.keys()[0]
        entries = item.values()[0]
        h_cfg = deepcopy(def_test_params['hotspot_cfg'])
        h_cfg.update({'walled_garden_list': entries})
        test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                          'CB_ZD_Edit_Hotspot_Profiles',
                          '%sUpdate existing hotspot profile' % tcid,
                          1,
                          False,
                          ))  
        
        test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, 
                                                           target_station, 
                                                           target_station_radio, 
                                                           open_wlan,
                                                           'wg_1')))
        
        test_cfgs.append(({'walled_garden_list': entries,
                           'sta_tag': 'sta_1'
                           },
                         'CB_ZD_Hotspot_Walled_Garden_Ping',
                         '%sPing walled garden addresses before hotspot auth' % tcid,
                         2, 
                         False
                         ))      
        
        auth_info = deepcopy(def_test_params['auth_info'])
        test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))
                
        test_cfgs.append(({'wlan_cfg': open_wlan,
                          'hotspot_cfg': h_cfg,
                          'ap_tag': 'tap'},
                         'CB_ZD_Hotspot_Walled_Garden',
                         '%sVerify walled garden in ZD and AP shell after auth' % tcid,
                         2, 
                         False
                         ))
        test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, 
                                                           target_station_radio, 
                                                           open_wlan, 
                                                           auth_info)))
    
    test_cfgs.extend(clean_steps(Clean_up=True))                        
        
    return test_cfgs


def clean_steps(LEVEL = 0, Clean_up=False):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups to cleanup', 
            LEVEL, 
            Clean_up),   
                       
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs to cleanup', 
            LEVEL, 
            Clean_up),   
                     
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles to cleanup', 
            LEVEL, 
            Clean_up),
                        
            ({},
             'CB_ZD_Remove_All_Users',
             'Remove all users to cleanup',
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
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'disallowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       'Station ping target IP before hotspot auth', 
                       2, 
                       False))        
     
    param_cfg = {'wlan_cfg': wlan, 
                 'chk_empty': False, 
                 'status': 'Unauthorized',
                 'chk_radio': False,
                 'radio_mode': radio,
                 'sta_tag': 'sta_1',
                 'ap_tag': 'tap',                 
                 }
    test_cfgs.append((param_cfg,                        
                      'CB_ZD_Verify_Station_Info_V2',
                      'Verify station info before hotspot auth', 
                      2, 
                      False)) 
        
    return test_cfgs 


def station_c_steps(auth_info):
    test_cfgs = []
    param_cfgs = {'sta_tag': 'sta_1'}
    param_cfgs.update(auth_info)
    test_cfgs.append((param_cfgs, 
                      'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                      'Perform hotspot authentication', 
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
                      'Verify station info on ZD after hotspot auth', 
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
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       'Station ping a target IP after hotspot auth', 
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
        
        ts_name = "Reading WISPr Walled Garden - %s" % target_sta_radio    
        #ts_name = "Reading WISPr Walled Garden - %s%s - %s" % (active_ap_model, active_ap_role, target_sta_radio)

    ts = testsuite.get_testsuite(ts_name, 
                                 'Verify Reading WISPr Walled Garden',
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
