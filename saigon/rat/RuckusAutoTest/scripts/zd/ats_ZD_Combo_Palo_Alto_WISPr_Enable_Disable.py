'''
Created on 2011-7-25
@author: Administrator
'''

import sys
import time
import copy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

BROWSER_STARTED = False

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
        
        EXEC_LEVEL = 1     
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
        global  BROWSER_STARTED
        if not BROWSER_STARTED:
            test_cfgs.append(({'sta_tag': sta_tag},
                              'CB_Station_CaptivePortal_Start_Browser',
                              'Open authentication web page',
                              EXEC_LEVEL,
                              False,
                              ))
            BROWSER_STARTED = True           
    
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
        EXEC_LEVEL = 1  
        param_cfg = dict(active_ap = active_ap,
                         wlan_group_name = wlan_group_name, 
                         radio_mode = radio)    
        return[(param_cfg, 
                'CB_ZD_Assign_AP_To_Wlan_Groups', 
                'Associate AP with radio: %s to Default' % (radio), 
                EXEC_LEVEL, 
                False)]
    
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
        EXEC_LEVEL = 1       
        test_cfgs = []
        
        active_ap = param_dict['active_ap']
        radio = param_dict['radio']
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        wlan_group_name = param_dict['wlan_group_name']
        target_station = param_dict['target_station']
        target_ip = param_dict['target_ip']
        sta_tag = param_dict['sta_tag']
        ap_tag = param_dict['ap_tag']
        tcid = param_dict['tcid']
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
                          tcid = tcid, 
                          chk_radio = chk_radio, 
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_hotspot_station(**kwargs))
            
        elif auth_type == TestStepBuilder.WEBAUTH:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL,
                          wlan_cfg = wlan_cfg,
                          sta_tag = sta_tag,
                          ap_tag = ap_tag,
                          tcid = tcid,
                          chk_radio = chk_radio,
                          radio = radio,
                          )
            test_cfgs.extend(TestStepBuilder._build_webauth_station(**kargs))
            
        elif auth_type == TestStepBuilder.GUESTAUTH:
            kwargs = dict(EXEC_LEVEL = EXEC_LEVEL,
                          wlan_cfg = wlan_cfg,
                          guest_cfg = guest_cfg,
                          sta_tag = sta_tag,
                          tcid = tcid,
                          chk_radio = chk_radio,
                          radio = radio)
            test_cfgs.extend(TestStepBuilder._build_guestauth_station(**kwargs))
            
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
        EXEC_LEVEL = 1
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
                 'target': target_ip,
                 'ping_timeout_ms': 10 * 1000
                 },
                 'CB_ZD_Client_Ping_Dest', 
                 'The station ping a target IP', 
                 EXEC_LEVEL + 1, 
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
                      'tcid':None,
                     }
        param_dict.update(kwargs)        
        EXEC_LEVEL = 1       
        test_cfgs = []
        
        active_ap = param_dict['active_ap']
        radios = param_dict['radios']
        wlan_cfg = copy.deepcopy(param_dict['wlan_cfg'])
        wlan_group_name = param_dict['wlan_group_name']
        target_station = param_dict['target_station']
        target_ip = param_dict['target_ip']
        sta_tag = param_dict['sta_tag']
        ap_tag = param_dict['ap_tag']
        tcid = param_dict['tcid']
        chk_radio = param_dict['chk_radio']
        
        hotspot_cfg = copy.deepcopy(param_dict['hotspot_cfg'])
        webauth_cfg = copy.deepcopy(param_dict['webauth_cfg'])
        guest_cfg = copy.deepcopy(param_dict['guest_cfg'])
                     
          
        for radio in radios: 
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
                          EXEC_LEVEL + 1, 
                          False))
        if tcid:
            return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
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
                          EXEC_LEVEL + 1, 
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
                          EXEC_LEVEL + 1, 
                          False))
        
        test_cfgs.append(({'sta_tag':sta_tag},
                         'CB_Station_CaptivePortal_Download_File',
                         'Download files from server',
                         EXEC_LEVEL + 1,
                         False
                         ))        
         
        if tcid:
            return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
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
                          EXEC_LEVEL + 1, 
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
                          EXEC_LEVEL + 1, 
                          False))
        
        if tcid:
            return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
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
                          EXEC_LEVEL + 1, 
                          False)) 
            
        
        param_cfgs = {'sta_tag':sta_tag}
        for k, v in guest_cfg.items():
            param_cfgs[k] = v
                
        test_cfgs.append((param_cfgs, 
                          'CB_Client_CaptivePortal_GuestAuth', 
                          'Perform Guest authentication', 
                          EXEC_LEVEL, 
                          False)) 
        
        
        username = webauth_cfg['auth_info']['username']
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
                          EXEC_LEVEL + 1, 
                          False))
        
        
    
        if tcid:
            return TestStepBuilder._encode_tcid(tcid, test_cfgs)
            
        return test_cfgs  

#----------------------    Test step builder END      ---------------#




OPEN_NONE_INDEX  = 0
def define_wlans():
    wlan_cfg_list = []
    # Open-None
    wlan_cfg_list.append(dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", web_auth = None))
    
    return wlan_cfg_list


def define_test_params(target_station):
    cfg = dict()
    cfg['target_station'] = target_station
    cfg['target_ip'] = '172.126.0.252'
    cfg['hotspot_cfg'] = {'login_page': 'http://192.168.0.250/login.html', 
                          'name': 'A Sampe Hotspot Profile'}
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


def build_sta_hot_cfg(test_params, server_name='local_server'):
    return dict(hotspot_profile_name = test_params['hotspot_cfg']['name'],
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
    
    tcid = '[Test Hotspot disable in WLAN]'    
    param_cfg = dict(hotspot_profiles_list = [test_params['hotspot_cfg']])
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_Hotspot_Profiles', 
                      '%sCreate Hotspot service' % tcid, 
                      EXEC_LEVEL, 
                      False))
    
    test_cfgs.extend(TestStepBuilder.build_create_wlans_step(EXEC_LEVEL, wlans))
    test_cfgs.extend(TestStepBuilder.build_uncheck_wlans_in_default_wg_step())
     
    wlans_copy = copy.deepcopy(wlans)     
    OPEN_WLANGROUP = 'open_none_wlangroup_1'    
    param_cfg = dict(wlangroups_map = {OPEN_WLANGROUP:wlans_copy[OPEN_NONE_INDEX]['ssid']})
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLANGroup and WLAN in pair', 
                      EXEC_LEVEL, 
                      False))
    
    #Disable Hotspot on a WLAN.
    param_dict = {'active_ap':active_ap,
                  'wlan_cfg':wlans_copy[OPEN_NONE_INDEX],
                  'wlan_group_name':OPEN_WLANGROUP,
                  'target_station':target_station,
                  'target_ip':test_params['target_ip'],
                  'radios':[target_station_radio],
                  'chk_radio':False,
                  'sta_tag':'sta_1',
                  'ap_tag':'tap',
                  'hotspot_cfg':None,
                  'tcid':tcid,
                 }    
    test_cfgs.extend(TestStepBuilder.build_station_all_steps(TestStepBuilder.NORMAL, **param_dict))         
    
    
    wlan_copy2 = copy.deepcopy(wlans)
    #Update WLAN to support hotspot.
    test_name = 'CB_ZD_Create_Wlan'
    hotspot_cfg = build_sta_hot_cfg(test_params, server_name='local_server')
    common_name = 'Modify WLAN{%s} with hotspot file{%s}' % (wlan_copy2[OPEN_NONE_INDEX]['ssid'], 
                                                            hotspot_cfg['hotspot_profile_name'])
    wlan_copy2[OPEN_NONE_INDEX]['hotspot_profile'] = hotspot_cfg['hotspot_profile_name']  
    wlan_copy2[OPEN_NONE_INDEX]['type'] = 'hotspot'
    param_cfg = dict(wlan_cfg_list = [wlan_copy2[OPEN_NONE_INDEX]])
    test_cfgs.append((param_cfg, test_name, common_name, EXEC_LEVEL, False))
    
    
    tcid = '[Test Hotspot enable in WLAN]'    
    #Enable Hotspot on a WLAN.
    param_dict = {'active_ap':active_ap,
                  'wlan_cfg':wlan_copy2[OPEN_NONE_INDEX],
                  'wlan_group_name':OPEN_WLANGROUP,
                  'target_station':target_station,
                  'target_ip':test_params['target_ip'],
                  'radios':[target_station_radio],
                  'chk_radio':False,
                  'sta_tag':'sta_1',
                  'ap_tag':'tap',
                  'hotspot_cfg':hotspot_cfg,
                  'tcid':tcid,
                }            
    test_cfgs.extend(TestStepBuilder.build_station_all_steps(TestStepBuilder.HOTSPOT, **param_dict))
    

    if BROWSER_STARTED:
        test_cfgs.append(({'sta_tag':'sta_1'},
                      'CB_Station_CaptivePortal_Quit_Browser',
                      'Close Authentication browser',
                      False,
                      1,
                      ))    
    
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
                 testsuite_name = "Palo Alto WISPr Enable and Disable - 11g",
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
        ts_name = "Palo Alto WISPr Enable and Disable - 11%s, %s" % (target_sta_radio, ap_model)        
    else:
        ts_name = attrs["testsuite_name"]

    ts = testsuite.get_testsuite(ts_name, 
                                 "Palo Alto WISPr Enable and Disable - 11%s, %s" % (target_sta_radio, ap_model), 
                                 combotest=True)
                
    test_cfgs = build_test_cases(target_sta, target_sta_radio, active_ap)
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
          
