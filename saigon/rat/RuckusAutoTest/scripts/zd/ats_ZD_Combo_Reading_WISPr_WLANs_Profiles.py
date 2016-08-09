'''
Test cases coverage:
    + Multiple Hotspot profiles on differrent WLANs
    + Single Hotspot profile shared by different WLANs
    
Created on 2011-9-2
@author: serena.tan@ruckuswireless.com
'''


import sys
import random
import re
import copy
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant


#--------------------------   Test Step builder    ---------------#
class TestStepBuilder:
    #######################################
    #         Access Methods              #
    #######################################
    @classmethod
    def build_station_pre_steps(cls, **kwargs):
        param_dict = {'active_ap': '',
                      'wlan_cfg': '',
                      'wlan_group_name': '',
                      'target_station': '',                  
                      'radio': None,
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',                  
                     }
        param_dict.update(kwargs)
        active_ap = param_dict['active_ap']
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        wlan_group_name = param_dict['wlan_group_name']
        radio = param_dict['radio']
        sta_tag = param_dict['sta_tag']
        
        EXEC_LEVEL = 2    
        test_cfgs = []
        
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = wlan_group_name, 
                         radio_mode = radio)
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Assign_AP_To_Wlan_Groups', 
                          'Assign AP radio %s to %s' % (radio, wlan_group_name), 
                          EXEC_LEVEL, 
                          False))
            
        test_cfgs.append(({'sta_tag': sta_tag, 
                           'wlan_cfg': wlan_cfg}, 
                          'CB_ZD_Associate_Station_1', 
                          'Associate the station', 
                          EXEC_LEVEL, 
                          False))    
        
        test_cfgs.append(({'sta_tag': sta_tag}, 
                          'CB_ZD_Get_Station_Wifi_Addr_1', 
                          'Get station wifi address', 
                          EXEC_LEVEL, 
                          False))  
        
        test_cfgs.append(({'sta_tag': sta_tag},
                          'CB_Station_CaptivePortal_Start_Browser',
                          'Open authentication web page',
                          EXEC_LEVEL,
                          False,
                          ))
    
        return test_cfgs
    
    @classmethod
    def build_station_post_steps(cls, **kwargs):
        param_dict = {'radio': None,
                      'wlan_group_name': None,
                      'active_ap': None,                           
                     }
        param_dict.update(kwargs)
        radio = param_dict['radio']
        active_ap = param_dict['active_ap']
        wlan_group_name = param_dict['wlan_group_name']    
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = wlan_group_name, 
                         radio_mode = radio) 
           
        return[({'sta_tag': 'sta_1'},
                  'CB_Station_CaptivePortal_Quit_Browser',
                  'Close authentication browser',
                  2,
                  True),
                  
                (param_cfg, 
                'CB_ZD_Assign_AP_To_Wlan_Groups', 
                'Assign AP radio %s to Default wlan group' % (radio), 
                2, 
                True)
                ]
    
    @classmethod
    def build_station_check_steps(cls, **kwargs):
        param_dict = {'active_ap': '',
                      'wlan_cfg': '',
                      'wlan_group_name': '',
                      'target_station': '',
                      'target_ip': '',
                      'radio': None,
                      'chk_radio': False,
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',
                      'hotspot_cfg': None,
                     }
        param_dict.update(kwargs) 
        test_cfgs = []
        
        kwargs = dict(wlan_cfg = copy.deepcopy(param_dict['wlan_cfg']), 
                      hotspot_cfg = copy.deepcopy(param_dict['hotspot_cfg']), 
                      sta_tag = param_dict['sta_tag'], 
                      ap_tag = param_dict['ap_tag'], 
                      chk_radio = param_dict['chk_radio'], 
                      radio = param_dict['radio'])
        test_cfgs.extend(TestStepBuilder._build_hotspot_station(**kwargs))
            
        return test_cfgs
        
    @classmethod
    def build_station_ping_step(cls, **kwargs):
        param_dict = {'sta_tag': 'sta_1',
                      'target_ip': '',
                      'condition': 'allowed',                           
                     }
        param_dict.update(kwargs)    
        sta_tag = param_dict['sta_tag']
        target_ip = param_dict['target_ip']
        condition = param_dict['condition']
        
        return[({'sta_tag': sta_tag,
                 'condition': condition,
                 'target': target_ip,},
                 'CB_ZD_Client_Ping_Dest', 
                 'The station ping a target IP', 
                 2, 
                 False)
               ]
        
    @classmethod
    def build_station_all_steps(cls, **kwargs):
        param_dict = {'active_ap': '',
                      'wlan_cfg': '',
                      'wlan_group_name': '',
                      'target_station': '',
                      'target_ip': '',
                      'radio': '',
                      'chk_radio': False,
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',
                      'hotspot_cfg': None,
                      'webauth_cfg': None,
                      'guest_cfg': None,
                     }
        param_dict.update(kwargs)        
        test_cfgs = []
        
        test_cfgs.extend(TestStepBuilder.build_station_pre_steps(**param_dict))
        test_cfgs.extend(TestStepBuilder.build_station_check_steps(**param_dict))        
        test_cfgs.extend(TestStepBuilder.build_station_ping_step(**param_dict))
        test_cfgs.extend(TestStepBuilder.build_station_post_steps(**param_dict))
        
        return test_cfgs
    

    #######################################
    #         Protected Methods           #
    #######################################
    @classmethod
    def _build_hotspot_station(cls, 
                               wlan_cfg = None, 
                               hotspot_cfg = None, 
                               sta_tag = 'sta_1', 
                               ap_tag = 'tap',
                               chk_radio = False,
                               radio = None):  
        EXEC_LEVEL = 2  
        test_cfgs = []            
        param_cfg = {'wlan_cfg': wlan_cfg, 
                     'chk_empty': False, 
                     'status': 'Unauthorized',
                     'chk_radio': chk_radio,
                     'radio_mode': radio,
                     'sta_tag': sta_tag,
                     'ap_tag': ap_tag,                 
                     }
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify station info before hotspot auth', 
                          EXEC_LEVEL, 
                          False)) 
        
        param_cfgs = {'sta_tag': sta_tag}
        for k, v in hotspot_cfg['auth_info'].items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                          'Perform hotspot authentication', 
                          EXEC_LEVEL, 
                          False)) 
        
        username = hotspot_cfg['auth_info']['username']    
        param_cfg = {'wlan_cfg': wlan_cfg, 
                     'chk_empty': False, 
                     'status': 'Authorized',
                     'chk_radio': chk_radio,
                     'radio_mode': radio,
                     'sta_tag': sta_tag,
                     'ap_tag': ap_tag,
                     'username': username}
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify station info after hotspot auth', 
                          EXEC_LEVEL, 
                          False))
        
        test_cfgs.append(({'sta_tag':sta_tag},
                          'CB_Station_CaptivePortal_Download_File',
                          'Download files from server',
                          EXEC_LEVEL,
                          False
                          ))        
         
        return test_cfgs       
    

#----------------------    Test step builder END      ---------------#


OPEN_NONE_INDEX  = 0
def define_wlans():
    wlan_cfg_list = []
    # Open-None    
    wlan_cfg_list.append(dict(ssid = "RAT-Open-None-%s" % time.strftime("%H%M%S"), 
                              auth = "open", encryption = "none"))
    # Open-WEP64
    wlan_cfg_list.append(dict(ssid = "RAT-Open-WEP64-%s" % time.strftime("%H%M%S"), 
                              auth = "open", encryption = "WEP-64",
                              key_index = "1", key_string = utils.make_random_string(10, "hex")))
    # Open-WEP128
    wlan_cfg_list.append(dict(ssid = "RAT-Open-WEP128-%s" % time.strftime("%H%M%S"), 
                              auth = "open", encryption = "WEP-128",
                              key_index = "1", key_string = utils.make_random_string(26, "hex")))
    # WPA-PSK-TKIP
    #wlan_cfg_list.append(dict(ssid = "RAT-WPA-PSK-TKIP-%s" % time.strftime("%H%M%S"), 
    #                          auth = "PSK", wpa_ver = "WPA" , encryption = "TKIP",
    #                          key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    # WPA-PSK-AES
    #wlan_cfg_list.append(dict(ssid = "RAT-WPA-PSK-AES-%s" % time.strftime("%H%M%S"), 
    #                          auth = "PSK", wpa_ver = "WPA" , encryption = "AES",
    #                          key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    # WPA2-PSK-TKIP
    #wlan_cfg_list.append(dict(ssid = "RAT-WPA2-PSK-TKIP-%s" % time.strftime("%H%M%S"), 
    #                          auth = "PSK", wpa_ver = "WPA2" , encryption = "TKIP",
    #                          key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    # WPA2-PSK-AES
    wlan_cfg_list.append(dict(ssid = "RAT-WPA2-PSK-AES-%s" % time.strftime("%H%M%S"), 
                              auth = "PSK", wpa_ver = "WPA2" , encryption = "AES",
                              key_string = utils.make_random_string(random.randint(8, 63), "hex")))
        
    return wlan_cfg_list


def encode_tcid(tcid, test_cfgs):
    #append test cases identifier.
    if tcid:
        test_cfgs_copy = []
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:            
            common_name = '%s%s' % (tcid, common_name)
            test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup)) 
            
        return test_cfgs_copy
        
    return test_cfgs  


def define_test_params(target_station):
    cfg = dict()
    cfg['target_station'] = target_station
    cfg['target_ip'] = '172.126.0.252'
    
    hotspot_list = [] 
    for index in range(1, 4):
        hotspot_list.append({'login_page': 'https://192.168.0.250/slogin.html', 
                             'name': 'A Sampe Hotspot Profile_%d' % index})
    
    cfg['hotspot_list'] = hotspot_list
    
    cfg['local_server'] = {'username': 'local.username',
                           'password': 'local.password'}
        
    return cfg


def build_sta_hot_cfg(test_params, server_name = 'local_server', index = 0):
    return dict(hotspot_profile_name = test_params['hotspot_list'][index]['name'],
                auth_info = test_params[server_name],
                station_ip = test_params['target_station'])


def build_test_cases(target_station, target_station_radio, active_ap):
    test_params = define_test_params(target_station)
    wlans = define_wlans()
    EXEC_LEVEL = 0
    test_cfgs = []

    test_cfgs.append(({'ap_tag': 'tap', 
                       'active_ap': active_ap}, 
                       'CB_ZD_Create_Active_AP', 
                       'Get the active AP', 
                       EXEC_LEVEL, 
                       False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       EXEC_LEVEL, 
                       False))
    
    test_cfgs.append(({},
                       'CB_ZD_Remove_All_Config', 
                       'Remove all configuration from ZD', 
                       EXEC_LEVEL, 
                       False))  

    user_cfg = {'username': 'local.username', 'password': 'local.password'}
    test_cfgs.append((user_cfg,
                      'CB_ZD_Create_Local_User', 
                      'Create a local user',
                      EXEC_LEVEL, 
                      False))
        
    test_cfgs.append((dict(wlan_cfg_list = copy.deepcopy(wlans)), 
                      'CB_ZD_Create_Wlans', 
                      'Create standard wlans', 
                       EXEC_LEVEL, 
                       False))
        
    test_cfgs.append(({}, 
                     'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group', 
                     'Remove all wlans from Default wlan group', 
                     EXEC_LEVEL, 
                     False,
                     ))
        
    hotspot_services = copy.deepcopy(test_params['hotspot_list'])
    param_cfg = dict(hotspot_profiles_list = hotspot_services)
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_Hotspot_Profiles', 
                      'Create hotspot profiles', 
                      EXEC_LEVEL, 
                      False))
               
    #Multiple WLANs in same WIRSPr profile.        
    for wlan in copy.deepcopy(wlans)[1:]:    
        tcid = '[Test Hotspot with wlan %s]' % wlan['ssid']        
        #Update WLAN to support hotspot.
        sta_hotspot_cfg = build_sta_hot_cfg(test_params, server_name = 'local_server', index = 0)        
        wlan['hotspot_profile'] = sta_hotspot_cfg['hotspot_profile_name']  
        wlan['type'] = 'hotspot'        
        test_cfgs.append((dict(wlan_cfg_list = [wlan]), 
                          'CB_ZD_Create_Wlan', 
                          '%sModify wlan with hotspot{%s}' % (tcid, sta_hotspot_cfg['hotspot_profile_name']), 
                          1, 
                          False))        
        
        OPEN_WLANGROUP = 'open_none_wlangroup_1'        
        test_cfgs.append((dict(wlangroups_map = {OPEN_WLANGROUP: wlan['ssid']}), 
                          'CB_ZD_Create_WLANGroups_with_WLANs', 
                          '%sCreate wlan group and wlan in pair' % tcid, 
                          2, 
                          False))    
                 
        param_dict = {'active_ap': active_ap,
                      'wlan_cfg': wlan,
                      'wlan_group_name': OPEN_WLANGROUP,
                      'target_station': target_station,
                      'target_ip': test_params['target_ip'],
                      'radio': target_station_radio,
                      'chk_radio': False,
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',
                      'hotspot_cfg': sta_hotspot_cfg,
                      }         
        test_cfgs.extend(encode_tcid(tcid, TestStepBuilder.build_station_all_steps(**param_dict)))
    
    #Multiple WIRSPr profiles in same WLAN.
    cnt = 0 
    wlan = wlans[OPEN_NONE_INDEX]
    OPEN_WLANGROUP = 'open_none_wlangroup_1'        
    test_cfgs.append((dict(wlangroups_map = {OPEN_WLANGROUP: wlan['ssid']}), 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLAN Group and WLAN in pair', 
                      0, 
                      False))
    for hotspot_cfg in hotspot_services:
        tcid = '[Test Hotspot with WISPr %s]' % hotspot_cfg['name']  
        sta_hotspot_cfg = build_sta_hot_cfg(test_params, server_name = 'local_server', index = cnt)        
        wlan['hotspot_profile'] = sta_hotspot_cfg['hotspot_profile_name']  
        wlan['type'] = 'hotspot'        
        test_cfgs.append((dict(wlan_cfg_list = [wlan]), 
                          'CB_ZD_Create_Wlan', 
                          '%sModify WLAN with hotspot{%s}' % (tcid, sta_hotspot_cfg['hotspot_profile_name']), 
                          1, 
                          False))      
        
        param_dict = {'active_ap': active_ap,
                      'wlan_cfg': wlan,
                      'wlan_group_name': OPEN_WLANGROUP,
                      'target_station': target_station,
                      'target_ip': test_params['target_ip'],
                      'radio': target_station_radio,
                      'chk_radio': False,
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',
                      'hotspot_cfg': sta_hotspot_cfg,
                     }        
        test_cfgs.extend(encode_tcid(tcid, TestStepBuilder.build_station_all_steps(**param_dict)))
        
        test_name = 'CB_ZD_Remove_All_Active_Clients'
        common_name = '%sRemove all active clients from ZD' % tcid
        test_cfgs.append(({}, test_name, common_name, 2, True)) 
        
        cnt += 1  

    test_cfgs.extend(clean_steps(Clean_up = True))
    
    return test_cfgs
    
    
def clean_steps(EXEC_LEVEL = 0, Clean_up = False):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup', 
            EXEC_LEVEL, 
            Clean_up),              
            
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup', 
            EXEC_LEVEL, 
            Clean_up),    
                    
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles for cleanup', 
            EXEC_LEVEL, 
            Clean_up),
              
            ({},
             'CB_ZD_Remove_All_Users',
             'Remove all users for cleanup',
             EXEC_LEVEL,
             Clean_up)
            ]
    
    
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

    test_cfgs = build_test_cases(sta_ip_addr, target_sta_radio, active_ap)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        active_ap_status = ap_sym_dict[active_ap]['status']
        active_ap_role = ''
        res = re.search('Connected \((.+)\)', active_ap_status, re.I)
        if res:
            active_ap_role = ' - %s' % res.group(1).split(' ')[0]
        
        ts_name = "Reading WISPr Multiple WLANs and Profiles - %s" % target_sta_radio    
        #ts_name = "Reading WISPr Multiple WLANs and Profiles - %s%s - %s" % (active_ap_model, active_ap_role, target_sta_radio)

    ts = testsuite.get_testsuite(ts_name, 
                                 'Verify Reading WISPr multiple WLANs and profiles',
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
