'''
Test cases coverage:
    + Hotspot Disable in WLAN
    + Hotspot Enable in WLAN
    
Created on 2011-9-2
@author: serena.tan@ruckuswireless.com
'''


import sys
import copy
import re
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


#--------------------------   Test Step builder    ---------------#
class TestStepBuilder:
    #######################################
    #             Constant                #
    #######################################
    NORMAL = 0
    HOTSPOT = 3

    #######################################
    #         Access Methods              #
    #######################################
    @classmethod
    def build_station_pre_steps(cls, **kwargs):
        param_dict = {'active_ap': '',
                      'wlan_cfg': '',
                      'wlan_group_name': '',
                      'target_station': '',                  
                      'radio': '',
                      'sta_tag': 'sta_1',
                      'ap_tag': 'tap',
                      'tcid': ''                  
                     }
        param_dict.update(kwargs)
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        sta_tag = param_dict['sta_tag']
        
        EXEC_LEVEL = 2  
        test_cfgs = []

        param_cfg = dict(active_ap = param_dict['active_ap'],
                         wlan_group_name = param_dict['wlan_group_name'], 
                         radio_mode = param_dict['radio'])
        
        common_name = '%sAssign AP radio %s to %s'
        common_name = common_name % (param_dict['tcid'], param_cfg['radio_mode'], param_cfg['wlan_group_name'])
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Assign_AP_To_Wlan_Groups', 
                          common_name,
                          1, 
                          False))
        
        test_cfgs.append(({'sta_tag': sta_tag, 
                           'wlan_cfg': wlan_cfg}, 
                           'CB_ZD_Associate_Station_1', 
                           '%sAssociate the target station' % param_dict['tcid'], 
                           EXEC_LEVEL, 
                           False))    
    
        test_cfgs.append(({'sta_tag': sta_tag}, 
                           'CB_ZD_Get_Station_Wifi_Addr_1', 
                           '%sGet station wifi address' % param_dict['tcid'], 
                           EXEC_LEVEL, 
                           False))   
        
        return test_cfgs
    
    @classmethod
    def build_station_post_steps(cls, **kwargs):
        param_dict = {'radio': None,
                      'active_ap': None,
                      'sta_tag': None,
                      'tcid': ''                           
                     }
        param_dict.update(kwargs)
        radio = param_dict['radio']
        active_ap = param_dict['active_ap']
        test_cfgs = []
        
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = 'Default', 
                         radio_mode = radio) 
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Assign_AP_To_Wlan_Groups', 
                          '%sAssign AP radio %s to Default wlan group' % (param_dict['tcid'], radio), 
                          2, 
                          True))
 
        return test_cfgs
    
    @classmethod
    def build_station_check_steps(cls, auth_type, **kwargs):
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
                      'webauth_cfg': None,
                      'guest_cfg': None,
                      'tcid': '',
                     }
        param_dict.update(kwargs)   
             
        EXEC_LEVEL = 2       
        test_cfgs = []
        
        radio = param_dict['radio']
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        sta_tag = param_dict['sta_tag']
        ap_tag = param_dict['ap_tag']
        tcid = param_dict['tcid']
        chk_radio = param_dict['chk_radio']
        hotspot_cfg = copy.deepcopy(param_dict['hotspot_cfg'])
                
        if auth_type == TestStepBuilder.HOTSPOT:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL, 
                          wlan_cfg = wlan_cfg, 
                          hotspot_cfg = hotspot_cfg, 
                          sta_tag = sta_tag, 
                          ap_tag = ap_tag, 
                          tcid = tcid, 
                          chk_radio = chk_radio, 
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_hotspot_station(**kwargs))
            
        else:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL,
                          wlan_cfg = wlan_cfg,
                          sta_tag = sta_tag,
                          ap_tag = ap_tag,
                          tcid = tcid,
                          chk_radio = chk_radio,
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_normal_station(**kwargs))
        
        return test_cfgs
        
    @classmethod
    def build_station_ping_step(cls, **kwargs):
        param_dict = {'sta_tag': 'sta_1',
                      'target_ip': '',
                      'condition': 'allowed',  
                      'tcid': '',
                      }
        param_dict.update(kwargs)  
          
        sta_tag = param_dict['sta_tag']
        target_ip = param_dict['target_ip']
        condition = param_dict['condition']
        
        return[({'sta_tag': sta_tag,
                 'condition': condition,
                 'target': target_ip,
                 'ping_timeout_ms': 10 * 1000
                 },
                 'CB_ZD_Client_Ping_Dest', 
                 '%sThe station ping a target IP' % param_dict['tcid'], 
                 2, 
                 False)
               ]
        
    @classmethod
    def build_station_all_steps(cls, auth_type, **kwargs):
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
                      'tcid': '',
                     }
        param_dict.update(kwargs)        
        test_cfgs = []
        
        test_cfgs.extend(TestStepBuilder.build_station_pre_steps(**param_dict))
        test_cfgs.extend(TestStepBuilder.build_station_check_steps(auth_type, **param_dict))        
        test_cfgs.extend(TestStepBuilder.build_station_ping_step(**param_dict))
        test_cfgs.extend(TestStepBuilder.build_station_post_steps(**param_dict))
        
        return test_cfgs

    #######################################
    #         Protected Methods           #
    #######################################
    @classmethod
    def _build_normal_station(cls,
                              EXEC_LEVEL = 2, 
                              wlan_cfg = None,                         
                              sta_tag = 'sta_1', 
                              ap_tag = 'tap', 
                              tcid = '',
                              chk_radio=False,
                              radio = None
                              ):
        test_cfgs = []
            
        param_cfg = {'wlan_cfg': wlan_cfg, 
                     'chk_empty': False, 
                     'status': 'Authorized',
                     'chk_radio': chk_radio,
                     'radio_mode': radio,
                     'sta_tag': sta_tag,
                     'ap_tag': ap_tag}
        
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Verify_Station_Info_V2', 
                          '%sVerify the station information on ZD' % tcid, 
                          EXEC_LEVEL, 
                          False))
            
        return test_cfgs       
         
    @classmethod
    def _build_hotspot_station(cls,
                               EXEC_LEVEL = 2, 
                               wlan_cfg = None, 
                               hotspot_cfg = None, 
                               sta_tag = 'sta_1', 
                               ap_tag = 'tap',
                               tcid = '',
                               chk_radio = False,
                               radio = None):    
        test_cfgs = []            
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Unauthorized',
                     'chk_radio':chk_radio,
                     'radio_mode':radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,                 
                     }
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          '%sVerify the station before hotspot auth' % tcid, 
                          EXEC_LEVEL, 
                          False)) 

        test_cfgs.append(({'sta_tag': sta_tag},
                          'CB_Station_CaptivePortal_Start_Browser',
                          '%sOpen authentication web page' % tcid,
                          EXEC_LEVEL,
                          False,
                          ))

        param_cfgs = {'sta_tag': sta_tag}
        for k, v in hotspot_cfg['auth_info'].items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                          '%sPerform Hotspot authentication' % tcid, 
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
                          '%sVerify the station after hotspot auth' % tcid, 
                          EXEC_LEVEL, 
                          False))
        
        test_cfgs.append(({'sta_tag': sta_tag},
                          'CB_Station_CaptivePortal_Download_File',
                          '%sDownload files from server' % tcid,
                          EXEC_LEVEL,
                          False
                         ))        

        test_cfgs.append(({'sta_tag': sta_tag},
                           'CB_Station_CaptivePortal_Quit_Browser',
                           '%sClose Authentication browser' % tcid,
                           EXEC_LEVEL, 
                           False))
            
        return test_cfgs       
    

#----------------------    Test step builder END      ---------------#

OPEN_NONE_INDEX  = 0
def define_wlans():
    wlan_cfg_list = []
    wlan_cfg_list.append(dict(ssid = "RAT-Open-None-%s" % (time.strftime("%H%M%S")), 
                              auth = "open", encryption = "none", 
                              web_auth = None))
    
    return wlan_cfg_list


def define_test_params(target_station):
    cfg = dict()
    cfg['target_station'] = target_station
    cfg['target_ip'] = '172.126.0.252'
    cfg['hotspot_cfg'] = {'login_page': 'https://192.168.0.250/slogin.html', 
                          'name': 'A Sampe Hotspot Profile'}

    cfg['local_server'] = {'username': 'local.username',
                           'password': 'local.password'}
    
    return cfg


def build_sta_hot_cfg(test_params, server_name = 'local_server'):
    return dict(hotspot_profile_name = test_params['hotspot_cfg']['name'],
                auth_info = test_params[server_name],
                station_ip = test_params['target_station'])


def build_test_cases(target_station, target_station_radio, active_ap):
    test_cfgs = []
    test_params = define_test_params(target_station)
    wlans = define_wlans()
    user_cfg = {'username': 'local.username', 'password': 'local.password'}
    sta_tag = target_station
    ap_tag = active_ap
    
    test_cfgs.append(({'sta_tag': sta_tag, 'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the target station', 
                       0, 
                       False))
     
    test_cfgs.append(({'ap_tag': ap_tag, 'active_ap': active_ap}, 
                      'CB_ZD_Create_Active_AP', 
                      'Get the active AP', 
                      0, 
                      False)) 
        
    test_cfgs.append(({},
                       'CB_ZD_Remove_All_Config', 
                       'Remove all configuration from ZD', 
                       0, 
                       False))

    test_cfgs.append((user_cfg, 
                      'CB_ZD_Create_Local_User', 
                      'Create a local user', 
                      0, 
                      False))
    
    tcid = '[Test Hotspot disable in WLAN]'     
    
    param_cfg = dict(hotspot_profiles_list = [test_params['hotspot_cfg']])
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_Hotspot_Profiles', 
                      'Create a hotspot profile', 
                      0, 
                      False))

    test_cfgs.append((dict(wlan_cfg_list = copy.deepcopy(wlans)), 
                      'CB_ZD_Create_Wlans', 
                      'Create a standard wlan',
                      0, 
                      False))
        
    test_cfgs.append(({}, 
                      'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group',
                      'Remove all wlans from Default wlan group', 
                      0,
                      False))
     
    wlans_copy = copy.deepcopy(wlans)     
    OPEN_WLANGROUP = 'open_none_wlangroup_1'    
    param_cfg = dict(wlangroups_map = {OPEN_WLANGROUP: wlans_copy[OPEN_NONE_INDEX]['ssid']})
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create wlan group and wlan in pair', 
                      0, 
                      False))
    
    param_dict = {'active_ap': active_ap,
                  'wlan_cfg': wlans_copy[OPEN_NONE_INDEX],
                  'wlan_group_name': OPEN_WLANGROUP,
                  'target_station': target_station,
                  'target_ip': test_params['target_ip'],
                  'radio': target_station_radio,
                  'chk_radio': False,
                  'sta_tag': sta_tag,
                  'ap_tag': ap_tag,
                  'hotspot_cfg': None,
                  'tcid': tcid,
                 }    
    test_cfgs.extend(TestStepBuilder.build_station_all_steps(TestStepBuilder.NORMAL, **param_dict))         
    
    tcid = '[Test Hotspot enable in WLAN]'  
    
    wlan_copy2 = copy.deepcopy(wlans)
    hotspot_cfg = build_sta_hot_cfg(test_params, server_name = 'local_server')
    common_name = '%sModify existing wlan with hotspot{%s}'
    common_name = common_name % (tcid, hotspot_cfg['hotspot_profile_name'])
    wlan_copy2[OPEN_NONE_INDEX]['hotspot_profile'] = hotspot_cfg['hotspot_profile_name']  
    wlan_copy2[OPEN_NONE_INDEX]['type'] = 'hotspot'
    param_cfg = dict(wlan_cfg_list = [wlan_copy2[OPEN_NONE_INDEX]])
    test_cfgs.append((param_cfg, 'CB_ZD_Create_Wlan', common_name, 2, False))
  
    param_dict = {'active_ap': active_ap,
                  'wlan_cfg': wlan_copy2[OPEN_NONE_INDEX],
                  'wlan_group_name': OPEN_WLANGROUP,
                  'target_station': target_station,
                  'target_ip': test_params['target_ip'],
                  'radio': target_station_radio,
                  'chk_radio': False,
                  'sta_tag': sta_tag,
                  'ap_tag': ap_tag,
                  'hotspot_cfg': hotspot_cfg,
                  'tcid': tcid,
                }            
    test_cfgs.extend(TestStepBuilder.build_station_all_steps(TestStepBuilder.HOTSPOT, **param_dict))

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
            
        ts_name = "Reading WISPr Enable and Disable - %s" % (target_sta_radio)
        #ts_name = "Reading WISPr Enable and Disable - %s%s - %s" % (active_ap_model, active_ap_role, target_sta_radio)

    ts = testsuite.get_testsuite(ts_name, 
                                 'Verify Reading WISPr enable and disable',
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
    
