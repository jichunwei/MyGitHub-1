
'''
    + Multiple Hotspot profiles on differrent WLANs
    + Single Hotspot profile shared by different WLANs
Created on 2011-7-25
@author: cwang@ruckuswireless.com
'''

import sys
#import copy
#import time
import random
import copy

import libZD_TestSuite as testsuite

from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

#--------------------------   Test Step builder    ---------------#
class TestStepBuilder:
    #######################################
    #             Constant                #
    #######################################
    NORMAL = 0
    WEBAUTH = 1
    GUESTAUTH = 2
    HOTSPOT = 3
    

    #######################################
    #         Access Methods              #
    #######################################
    @classmethod
    def build_create_local_user_step(cls, EXEC_LEVEL, **user_cfg):
        user_cfg = {'username': 'local.username',
                    'password': 'local.password'
                    }
        user_cfg.update(user_cfg)
        return [(user_cfg, 
                 'CB_ZD_Create_Local_User', 
                 'Create a local user', 
                 EXEC_LEVEL, 
                 False)]
        
    
    @classmethod
    def build_create_wlans_step(cls, EXEC_LEVEL, wlans):     
        return [(dict(wlan_cfg_list = copy.deepcopy(wlans)), 
                 'CB_ZD_Create_Wlans', 
                 'Create WLANs', 
                 EXEC_LEVEL, 
                 False),
                ] 
    @classmethod
    def build_uncheck_wlans_in_default_wg_step(cls, EXEC_LEVEL = 0):
        return [({}, 
                 'CB_ZD_Remove_All_Wlans_Out_Of_Default_Wlan_Group', 
                 'Remove all wlans out of default', 
                 EXEC_LEVEL, 
                 False)
                ]
    
    @classmethod
    def build_clean_wlan_wlangroup_steps(cls, EXEC_LEVEL = 0):
           
        return [
                ({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Remove All WLAN Groups for cleanup ENV', 
                EXEC_LEVEL, False),
                  
                ({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                EXEC_LEVEL, 
                False),
                ]    
        
    @classmethod
    def build_clean_hotspot_step(cls, EXEC_LEVEL = 0):
        return [({}, 
                'CB_ZD_Remove_All_Profiles', 
                'Remove all profiles', 
                EXEC_LEVEL, 
                False)]
    
    
    @classmethod
    def build_station_pre_steps(cls, **kwargs):
        param_dict = {'active_ap':'',
                      'wlan_cfg':'',
                      'wlan_group_name':'',
                      'target_station':'',                  
                      'radio':None,
                      'sta_tag':'sta_1',
                      'ap_tag':'tap',                  
                     }
        param_dict.update(kwargs)
        active_ap = param_dict['active_ap']
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        wlan_group_name = param_dict['wlan_group_name']
        radio = param_dict['radio']
        target_station = param_dict['target_station']
        sta_tag = param_dict['sta_tag']
        ap_tag = param_dict['ap_tag']
        #tcid = param_dict['tcid']    
        
        EXEC_LEVEL = 2     
        test_cfgs = []
        
        param_cfg = dict(active_ap = active_ap)
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Find_Active_AP', 
                          'Create an Active AP', 
                          EXEC_LEVEL, 
                          False))
            
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = wlan_group_name, 
                         radio_mode = radio)
        
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Assign_AP_To_Wlan_Groups', 
                          'Associate AP with radio %s to %s' % (radio, wlan_group_name), 
                          EXEC_LEVEL, 
                          False))
     
    
        test_cfgs.append(({'sta_tag': sta_tag, 
                           'sta_ip_addr': target_station}, 
                           'CB_ZD_Create_Station', 
                           'Get the station', 
                           EXEC_LEVEL, 
                           False))
          
         
        test_cfgs.append(({'ap_tag': ap_tag, 
                           'active_ap': active_ap}, 
                          'CB_ZD_Create_Active_AP', 
                          'Get the active AP', 
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
                          'Get wifi address', 
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
        param_dict = {'radio':None,
                      'wlan_group_name':None,
                      'active_ap': None,                           
                     }
        param_dict.update(kwargs)
        radio = param_dict['radio']
        active_ap = param_dict['active_ap']
        wlan_group_name = param_dict['wlan_group_name']    
        EXEC_LEVEL = 2  
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = wlan_group_name, 
                         radio_mode = radio)    
        return[(param_cfg, 
                'CB_ZD_Assign_AP_To_Wlan_Groups', 
                'Associate AP with radio: %s to Default' % (radio), 
                EXEC_LEVEL, 
                True),
                ({'sta_tag':'sta_1'},
                  'CB_Station_CaptivePortal_Quit_Browser',
                  'Close Authentication browser',
                  EXEC_LEVEL,
                  True)                      
                ]
    
    @classmethod
    def build_station_check_steps(cls, auth_type, **kwargs):
        param_dict = {'active_ap':'',
                      'wlan_cfg':'',
                      'wlan_group_name':'',
                      'target_station':'',
                      'target_ip':'',
                      'radio':None,
                      'chk_radio':False,
                      'sta_tag':'sta_1',
                      'ap_tag':'tap',
                      'hotspot_cfg':None,
                      'webauth_cfg':None,
                      'guest_cfg':None,
                      'tcid':None,
                     }
        param_dict.update(kwargs)        
        EXEC_LEVEL = 2       
        test_cfgs = []
        
        #active_ap = param_dict['active_ap']
        radio = param_dict['radio']
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        #wlan_group_name = param_dict['wlan_group_name']
        #target_station = param_dict['target_station']
        #target_ip = param_dict['target_ip']
        sta_tag = param_dict['sta_tag']
        ap_tag = param_dict['ap_tag']
        chk_radio = param_dict['chk_radio']
        hotspot_cfg = copy.deepcopy(param_dict['hotspot_cfg'])
        webauth_cfg = copy.deepcopy(param_dict['webauth_cfg'])
        guest_cfg = copy.deepcopy(param_dict['guest_cfg'])
                
        if auth_type == TestStepBuilder.HOTSPOT:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL, 
                          wlan_cfg = wlan_cfg, 
                          hotspot_cfg = hotspot_cfg, 
                          sta_tag = sta_tag, 
                          ap_tag = ap_tag, 
                          #tcid = tcid, 
                          chk_radio = chk_radio, 
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_hotspot_station(**kwargs))
            
        elif auth_type == TestStepBuilder.WEBAUTH:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL,
                          wlan_cfg = wlan_cfg,
                          webauth_cfg = webauth_cfg, 
                          sta_tag = sta_tag,
                          ap_tag = ap_tag,
                          #tcid = tcid,
                          chk_radio = chk_radio,
                          radio = radio,
                          )
            test_cfgs.extend(TestStepBuilder._build_webauth_station(**kwargs))
            
        elif auth_type == TestStepBuilder.GUESTAUTH:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL,
                          wlan_cfg = wlan_cfg,
                          guest_cfg = guest_cfg,
                          sta_tag = sta_tag,
                          #tcid = tcid,
                          chk_radio = chk_radio,
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_guestauth_station(**kwargs))
            
        else:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL,
                          wlan_cfg = wlan_cfg,
                          sta_tag = sta_tag,
                          ap_tag = ap_tag,
                          #tcid = tcid,
                          chk_radio = chk_radio,
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_normal_station(**kwargs))
        
        return test_cfgs
        
    @classmethod
    def build_station_ping_step(cls, **kwargs):
        EXEC_LEVEL = 2
        param_dict = {'sta_tag':'sta_1',
                      'target_ip':'',
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
                 EXEC_LEVEL, 
                 False)
               ]
        
    @classmethod
    def build_station_all_steps(cls, auth_type, **kwargs):
        param_dict = {'active_ap':'',
                      'wlan_cfg':'',
                      'wlan_group_name':'',
                      'target_station':'',
                      'target_ip':'',
                      'radios':[],
                      'chk_radio':False,
                      'sta_tag':'sta_1',
                      'ap_tag':'tap',
                      'hotspot_cfg':None,
                      'webauth_cfg':None,
                      'guest_cfg':None,
                      #'tcid':None,
                     }
        param_dict.update(kwargs)        
        #EXEC_LEVEL = 2       
        test_cfgs = []
        
        #Modified by Liang Aihua on 2014-8-13
        #active_ap = param_dict['active_ap']
        #radios = param_dict['radios']
        #wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        #wlan_group_name = param_dict['wlan_group_name']
        #target_station = param_dict['target_station']
        #target_ip = param_dict['target_ip']
        #sta_tag = param_dict['sta_tag']
        #ap_tag = param_dict['ap_tag']
        #tcid = param_dict['tcid']
        #chk_radio = param_dict['chk_radio']
        
        #hotspot_cfg = copy.deepcopy(param_dict['hotspot_cfg'])
        #webauth_cfg = copy.deepcopy(param_dict['webauth_cfg'])
        #guest_cfg = copy.deepcopy(param_dict['guest_cfg'])
                     
          
        for radio in param_dict['radios']: 
            param_dict['radio'] = radio
        test_cfgs.extend(TestStepBuilder.build_station_pre_steps(**param_dict))
        test_cfgs.extend(TestStepBuilder.build_station_check_steps(auth_type, **param_dict))        
        test_cfgs.extend(TestStepBuilder.build_station_ping_step(**param_dict))
        test_cfgs.extend(TestStepBuilder.build_station_post_steps(**param_dict))
        
        return test_cfgs


    #######################################
    #         Protected Methods           #
    #######################################
    
    @classmethod
    def _encode_tcid(cls, tcid, test_cfgs):
        #append test cases identifier.
        if tcid:
            test_cfgs_copy = []
            for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
                common_name = '%s%s' % (tcid, common_name)
                test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup)) 
            return test_cfgs_copy
            
        return test_cfgs     
    
    
    @classmethod
    def _build_normal_station(cls,
                              EXEC_LEVEL = 1, 
                              wlan_cfg = None,                         
                              sta_tag = 'sta_1', 
                              ap_tag = 'tap', 
                              tcid = None,
                              chk_radio=False,
                              radio = None
                              ):
        test_cfgs = []
            
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Authorized',
                     'chk_radio':chk_radio,
                     'radio_mode':radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,}
        
        test_cfgs.append((param_cfg, 
                          'CB_ZD_Verify_Station_Info_V2', 
                          'Verify the station information on ZD', 
                          EXEC_LEVEL, 
                          False))
        #if tcid:
        #    return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
        return test_cfgs       
        
         
         
    @classmethod
    def _build_hotspot_station(cls,
                               EXEC_LEVEL = 1, 
                               wlan_cfg = None, 
                               hotspot_cfg = None, 
                               sta_tag = 'sta_1', 
                               ap_tag = 'tap',
                               tcid = None,
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
                          'Verify the station before hotspot auth', 
                          EXEC_LEVEL, 
                          False)) 
        
        
        
        param_cfgs = {'sta_tag':sta_tag}
        for k, v in hotspot_cfg['auth_info'].items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                          'Perform Hotspot authentication', 
                          EXEC_LEVEL, 
                          False)) 
        
        username = hotspot_cfg['auth_info']['username']    
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Authorized',
                     'chk_radio':chk_radio,
                     'radio_mode':radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,
                     'username':username}
        
        
                 
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify the station after hotspot auth', 
                          EXEC_LEVEL, 
                          False))
        
        test_cfgs.append(({'sta_tag':sta_tag},
             'CB_Station_CaptivePortal_Download_File',
             'Download files from server',
             EXEC_LEVEL,
             False
             ))        
         
        #if tcid:
        #    return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
        return test_cfgs       
        
    
    @classmethod
    def _build_webauth_station(cls,
                               EXEC_LEVEL = 1, 
                               wlan_cfg = None, 
                               webauth_cfg = None, 
                               sta_tag = 'sta_1', 
                               ap_tag = 'tap',
                               tcid = None,
                               chk_radio = False,
                               radio = None):
        test_cfgs = []            
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Unauthorized',
                     'chk_radio':chk_radio,
                     'radio_mode': radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,}
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify the station before web auth', 
                          EXEC_LEVEL, 
                          False)) 
        
        
        
        param_cfgs = {'sta_tag':sta_tag}
        for k, v in webauth_cfg['auth_info'].items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Client_CaptivePortal_WebAuth', 
                          'Perform Web authentication', 
                          EXEC_LEVEL, 
                          False)) 
        
        
        username = webauth_cfg['auth_info']['username']
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Authorized',
                     'chk_radio':chk_radio,
                     'radio_mode': radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,
                     'username':username}
        
        
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify the station after web auth', 
                          EXEC_LEVEL, 
                          False))
        
        test_cfgs.append(({'sta_tag':sta_tag},
                          'CB_Station_CaptivePortal_Download_File',
                          'Download files from server',
                           EXEC_LEVEL,
                           False))        
        
        #if tcid:
        #    return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
        return test_cfgs       
    
    @classmethod
    def _build_guestauth_station(cls, 
                                 EXEC_LEVEL = 1, 
                                 wlan_cfg = None, 
                                 guest_cfg = None, 
                                 sta_tag = 'sta_1', 
                                 ap_tag = 'tap',
                                 tcid = None,
                                 chk_radio = False,
                                 radio = None,
                                 ):
        test_cfgs = []            
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Unauthorized',
                     'chk_radio':chk_radio,
                     'radio_mode' : radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,}
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify the station before guest-auth', 
                          EXEC_LEVEL, 
                          False)) 
            
        
        param_cfgs = {'sta_tag':sta_tag}
        for k, v in guest_cfg.items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Client_CaptivePortal_GuestAuth', 
                          'Perform Guest authentication', 
                          EXEC_LEVEL, 
                          False)) 
        
        
        #username = guest_cfg['auth_info']['username']
        param_cfg = {'wlan_cfg':wlan_cfg, 
                     'chk_empty':False, 
                     'status':'Authorized',
                     'chk_radio':chk_radio,
                     'radio_mode' : radio,
                     'sta_tag':sta_tag,
                     'ap_tag':ap_tag,
                     }
        
        
        test_cfgs.append((param_cfg,                        
                          'CB_ZD_Verify_Station_Info_V2',
                          'Verify the station info after guest-auth', 
                          EXEC_LEVEL, 
                          False))
        
        
    
        #if tcid:
        #    return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
        return test_cfgs  

#----------------------    Test step builder END      ---------------#


OPEN_NONE_INDEX  = 0
def define_wlans():
    wlan_cfg_list = []
    # Open-None    
    wlan_cfg_list.append(dict(ssid = "RAT-Open-None", auth = "open", encryption = "none"))
    # Open-WEP64
    wlan_cfg_list.append(dict(ssid = "RAT-Open-WEP64", auth = "open", encryption = "WEP-64",
                         key_index = "1", key_string = utils.make_random_string(10, "hex")))
    # Open-WEP128
    wlan_cfg_list.append(dict(ssid = "RAT-Open-WEP128", auth = "open", encryption = "WEP-128",
                         key_index = "1", key_string = utils.make_random_string(26, "hex")))
    # WPA-PSK-TKIP
    #wlan_cfg_list.append(dict(ssid = "RAT-WPA-PSK-TKIP", auth = "PSK", wpa_ver = "WPA" , encryption = "TKIP",
    #                     key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    # WPA-PSK-AES
    #wlan_cfg_list.append(dict(ssid = "RAT-WPA-PSK-AES", auth = "PSK", wpa_ver = "WPA" , encryption = "AES",
    #                     key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    # WPA2-PSK-TKIP
    #wlan_cfg_list.append(dict(ssid = "RAT-WPA2-PSK-TKIP", auth = "PSK", wpa_ver = "WPA2" , encryption = "TKIP",
    #                     key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    # WPA2-PSK-AES
    wlan_cfg_list.append(dict(ssid = "RAT-WPA2-PSK-AES", auth = "PSK", wpa_ver = "WPA2" , encryption = "AES",
                         key_string = utils.make_random_string(random.randint(8, 63), "hex")))
        
    return wlan_cfg_list


def define_test_params(target_station):
    cfg = dict()
    cfg['target_station'] = target_station
    cfg['target_ip'] = '172.126.0.252'
    
    
    hotspot_list = [] 
    for index in range(1, 4):
        hotspot_list.append({'login_page': 'http://192.168.0.250/login.html', 
                             'name': 'A Sampe Hotspot Profile_%d' % index})
    
    cfg['hotspot_list'] = hotspot_list
    #define AAA server data.
    cfg['local_server'] = {'username': 'local.username',
                           'password': 'local.password'}
        
    return cfg


#define an ID generator
def gen():
    k = 0
    while True:
        k += 1
        yield k
        
ID_GEN = gen().next


def build_sta_hot_cfg(test_params, server_name='local_server', index = 0):
    return dict(hotspot_profile_name = test_params['hotspot_list'][index]['name'],
                auth_info = test_params[server_name],
                station_ip = test_params['target_station'])


def build_test_cases(target_station, target_station_radio, active_ap):
    EXEC_LEVEL = 0
    test_cfgs = []
    test_params = define_test_params(target_station)
    wlans = define_wlans()
    
    test_cfgs.extend(TestStepBuilder.build_clean_wlan_wlangroup_steps())
    test_cfgs.extend(TestStepBuilder.build_clean_hotspot_step())
    
    test_cfgs.extend(TestStepBuilder.build_create_local_user_step(EXEC_LEVEL, 
                                                         **test_params['local_server']))   
      
    test_cfgs.extend(TestStepBuilder.build_create_wlans_step(EXEC_LEVEL, wlans))    
    test_cfgs.extend(TestStepBuilder.build_uncheck_wlans_in_default_wg_step())
    
        
    hotspot_services = copy.deepcopy(test_params['hotspot_list'])
    param_cfg = dict(hotspot_profiles_list = hotspot_services)
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_Hotspot_Profiles', 
                      'Create Hotspot service', 
                      EXEC_LEVEL, 
                      False))
               
    #Multiple WLANs in same WIRSPr profile.        
    for wlan in copy.deepcopy(wlans)[1:]:  
        import pdb
        pdb.set_trace()
        EXEC_LEVEL = 2  
        tcid = '[Test Hotspot with wlan %s]' % wlan['ssid']        
        #Update WLAN to support hotspot.
        sta_hotspot_cfg = build_sta_hot_cfg(test_params, server_name='local_server', index=0)        
        wlan['hotspot_profile'] = sta_hotspot_cfg['hotspot_profile_name']  
        wlan['type'] = 'hotspot'        
        test_cfgs.append((dict(wlan_cfg_list = [wlan]), 
                          'CB_ZD_Create_Wlan', 
                          '%sModify WLAN with hotspot{%s}' % (tcid, (sta_hotspot_cfg['hotspot_profile_name'])), 
                          1, 
                          False))        
        
        OPEN_WLANGROUP = 'open_none_wlangroup_1'        
        test_cfgs.append((dict(wlangroups_map = {OPEN_WLANGROUP:wlan['ssid']}), 
                          'CB_ZD_Create_WLANGroups_with_WLANs', 
                          '%sCreate WLANGroup and WLAN in pair' %tcid, 
                          EXEC_LEVEL, 
                          False))    
                 
        param_dict = {'active_ap':active_ap,
                  'wlan_cfg':wlan,
                  'wlan_group_name':OPEN_WLANGROUP,
                  'target_station':target_station,
                  'target_ip':test_params['target_ip'],
                  'radios':[target_station_radio],
                  'chk_radio':False,
                  'sta_tag':'sta_1',
                  'ap_tag':'tap',
                  'hotspot_cfg':sta_hotspot_cfg,
                  'tcid':tcid,
                 }         
        test_cfgs.extend(TestStepBuilder._encode_tcid(tcid, TestStepBuilder.build_station_all_steps(TestStepBuilder.HOTSPOT, **param_dict)))
        #test_cfgs.extend(TestStepBuilder.build_station_all_steps(TestStepBuilder.HOTSPOT, **param_dict))    
    
        
                
    
    #Multiple WIRSPr profiles in same WLAN.
    cnt = 0
    wlan = wlans[OPEN_NONE_INDEX]
    
    OPEN_WLANGROUP = 'open_none_wlangroup_1'        
    test_cfgs.append((dict(wlangroups_map = {OPEN_WLANGROUP:wlan['ssid']}), 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLANGroup and WLAN in pair', 
                      0, 
                      False))    
    
    for hotspot_cfg in hotspot_services:
        tcid = '[Test Hotspot with WISPr %s]' % hotspot_cfg['name']
        EXEC_LEVEL = 2
        
        sta_hotspot_cfg = build_sta_hot_cfg(test_params, server_name='local_server', index=cnt)        
        wlan['hotspot_profile'] = sta_hotspot_cfg['hotspot_profile_name']  
        wlan['type'] = 'hotspot'        
        test_cfgs.append((dict(wlan_cfg_list = [wlan]), 
                          'CB_ZD_Create_Wlan', 
                          '%sModify WLAN with hotspot{%s}' % (tcid, (sta_hotspot_cfg['hotspot_profile_name'])), 
                          1, 
                          False))      
          
        
        param_dict = {'active_ap':active_ap,
                  'wlan_cfg':wlan,
                  'wlan_group_name':OPEN_WLANGROUP,
                  'target_station':target_station,
                  'target_ip':test_params['target_ip'],
                  'radios':[target_station_radio],
                  'chk_radio':False,
                  'sta_tag':'sta_1',
                  'ap_tag':'tap',
                  'hotspot_cfg':sta_hotspot_cfg,
                  'tcid':tcid,
                 }        
        test_cfgs.extend(TestStepBuilder._encode_tcid(tcid, TestStepBuilder.build_station_all_steps(TestStepBuilder.HOTSPOT, **param_dict)))
        
        cnt += 1  
        
    
    return test_cfgs

#Append id number to identify the test case in database.
def decorate_common_name(test_cfgs):
    test_cfgs_copy = []
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        common_name = '%s.%s' % (ID_GEN(), common_name) 
        test_cfgs_copy.append((test_params, testname, common_name, exc_level, is_cleanup))
    return test_cfgs_copy



def create_test_suite(**kwargs):
    STA_INDEX = 0
    STA_RADIO_INDEX = 1
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "Palo Alto WISPr Multiple WLANs and Profiles - 11g",
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
        #ts_name = "Palo Alto WISPr Multiple WLANs and Profiles - 11%s, %s" % (target_sta_radio, ap_model) 
        ts_name = "Palo Alto WISPr Multiple WLANs and Profiles - 11%s" % target_sta_radio      
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "Palo Alto WISPr Multiple WLANs and Profiles - 11%s, %s" % (target_sta_radio, ap_model), 
                                 combotest=True)
                
    test_cfgs = build_test_cases(target_sta, target_sta_radio, active_ap)
    #test_cfgs = decorate_common_name(test_cfgs)
    
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
          