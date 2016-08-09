'''
Test cases coverage:
    + Hotspot with encryption WEP
    + Hotspot with encryption WPA2-AES
    + Wrong authentication using invalid username - local database
    + Wrong authentication using invalid password - local database
    + ZD Session Timeout disabled with Session Timeout enabled on Radius server
    + ZD Session Timeout enabled with Session Timeout enabled on Radius server
    + ZD Session Timeout enabled with Session Timeout disabled on Radius server
    + Start page ridirect to a URL
    + Start page ridirect to the original URL
    + UAM Redirected HTTP login/logout URLs
    + UAM Redirected HTTPS login/logout URLs
    + Relogin within Idle Timeout threshold with Idle Timeout enabled on Radius server - disabled on ZD
    + Relogin within Idle Timeout threshold with Idle Timeout enabled on Radius server - enabled on ZD
    + Relogin within Idle Timeout threshold with Idle Timeout disabled on Radius server - enabled on ZD
    + Relogin beyond Idle Timeout threshold with Idle Timeout enabled on Radius server - disabled on ZD
    + Relogin beyond Idle Timeout threshold with Idle Timeout enabled on Radius server - enabled on ZD
    + Relogin beyond Idle Timeout threshold with Idle Timeout disabled on Radius server - enabled on ZD
    + Accounting server with extra attributes
    + Accounting server update frequency
    
    
Created on 2011-8-10
@author: Administrator
'''
import sys
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

#define an ID generator
def gen():
    k = 0
    while True:
        k += 1
        yield k
        
ID_GEN = gen().next

def build_basic_ts(target_station, target_station_radio, active_ap):
    test_cfgs = []
        
#    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    
    open_wlan = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test',)
    wep_cfg = dict(ssid='RAT-OPEN-WEP-128',
                   type = 'hotspot',
                   auth="open", wpa_ver="", encryption="WEP-128",
                   key_index="1" , key_string=utils.make_random_string(26,"hex"),
                   hotspot_profile = 'wispr_test',
                   )
    wpa_cfg = dict(ssid='RAT-PSK-WPA2-AES',
                   type = 'hotspot',
                   auth="PSK", wpa_ver="WPA2", encryption="AES",
                   key_string=utils.make_random_string(random.randint(8,63),"hex"),
                   hotspot_profile = 'wispr_test',
                   )
        
    def_test_params = {'target_station': target_station, 'target_ip': '172.16.10.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
        
            
    test_cfgs.extend(clean_steps())  
    
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
                      0, 
                      False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       0, 
                       False))                
    
    test_cfgs.append(({'hotspot_profiles_list': [deepcopy(def_test_params['hotspot_cfg'])]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot',
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
    
        
    test_cfgs.append(({'wlan_cfg_list':[open_wlan, wep_cfg, wpa_cfg]},
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
                                         'wg_2':wep_cfg['ssid'],
                                         'wg_3':wpa_cfg['ssid']
                                        }}, 
                      'CB_ZD_Create_WLANGroups_with_WLANs', 
                      'Create WLANGroup and WLAN in pair', 
                      0, 
                      False))
    

    
    tcid = "[Hotspot with encryption WEP]"
    EXEC_LEVEL = 1
    test_cfgs.extend(encode_tcid(tcid,
                                 station_steps(active_ap, 
                                               target_station, 
                                               target_station_radio, 
                                               wep_cfg, 
                                               'wg_2', 
                                               deepcopy(def_test_params['auth_info']),
                                               EXEC_LEVEL)))
    
    
    
    
    tcid = "[Hotspot with encryption WPA2-AES]"
    test_cfgs.extend(encode_tcid(tcid, 
                                 station_steps(active_ap, 
                                               target_station, 
                                               target_station_radio, 
                                               wpa_cfg, 
                                               'wg_3', 
                                               deepcopy(def_test_params['auth_info']),
                                               EXEC_LEVEL)))
    
    
    tcid = "[Start page ridirect to a URL]"
    h_cfg = deepcopy(def_test_params['hotspot_cfg'])
    h_cfg.update({'start_page': 'http://www.ruckuswireless.com'})
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))  
    test_cfgs.extend(encode_tcid(tcid, station_steps(active_ap, 
                                               target_station, 
                                               target_station_radio, 
                                               open_wlan, 
                                               'wg_1', 
                                               deepcopy(def_test_params['auth_info'])))) 
    
    tcid = "[UAM Redirected HTTP login/logout URLs]"
    h_cfg = deepcopy(def_test_params['hotspot_cfg'])
    h_cfg.update({'logout_page': 'http://192.168.0.250/logout.html'})
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))  
    test_cfgs.extend(encode_tcid(tcid, station_steps(active_ap, 
                                               target_station, 
                                               target_station_radio, 
                                               open_wlan, 
                                               'wg_1', 
                                               deepcopy(def_test_params['auth_info']))))   
    
    tcid = "[UAM Redirected HTTPS login/logout URLs]"
    
    h_cfg = deepcopy(def_test_params['hotspot_cfg'])
    h_cfg.update({'logout_page': 'http://192.168.0.250/slogout.html'})
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))  
    test_cfgs.extend(encode_tcid(tcid, station_steps(active_ap, 
                                               target_station, 
                                               target_station_radio, 
                                               open_wlan, 
                                               'wg_1', 
                                               deepcopy(def_test_params['auth_info'])))) 
       
        
    
    tcid = "[Wrong authentication using invalid username/password - local database]"  
    h_cfg = deepcopy(def_test_params['hotspot_cfg'])    
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))      
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, 
                                     target_station, 
                                     target_station_radio, 
                                     open_wlan, 
                                     'wg_1')))            
    
    
    test_cfgs.append(({'sta_tag':'sta_1',
                       'username':'invalid.username',
                       'password':'local.password',
                       'negative_test':True
                       },
                       'CB_Station_CaptivePortal_Perform_HotspotAuth_With_Invalid_Account', 
                       '%sPerform Hotspot authentication' % tcid, 
                       2, 
                       False                       
                      ))
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'disallowed',
                       'target_ip': '172.16.10.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       '%sThe station ping a target IP' % tcid, 
                       2, 
                       False))
    
#    test_cfgs.append(({'sta_tag':'sta_1'},
#              'CB_Station_CaptivePortal_Quit_Browser',
#              'Close Authentication browser',
#              1,
#              False,
#              ))       
#    
    
    tcid = "[Wrong authentication using invalid username/password - local database]" 
    test_cfgs.append(({'sta_tag':'sta_1',
                       'username':'local.username',
                       'password':'invalid.password',
                       'negative_test':True
                       },
                       'CB_Station_CaptivePortal_Perform_HotspotAuth_With_Invalid_Account', 
                       '%sPerform Hotspot authentication' % tcid, 
                       2, 
                       False                       
                      ))
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'disallowed',
                       'target_ip': '172.16.10.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       '%sThe station ping a target IP' % tcid, 
                       2, 
                       False))

    test_cfgs.append(({'sta_tag':'sta_1'},
              'CB_Station_CaptivePortal_Quit_Browser',
              '%sClose Authentication browser' %tcid,
              2,
              True,
              ))
    
    test_cfgs.extend(clean_steps(Clean_up = True))   
    
    
    return test_cfgs

def build_session_timeout_ts(target_station, target_station_radio, active_ap):
    test_cfgs = []
        
#    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    
    open_wlan = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test',)    
        
    def_test_params = {'target_station': target_station, 'target_ip': '172.16.10.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
        
            
    test_cfgs.extend(clean_steps())  
    
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
                      0, 
                      False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       0, 
                       False))                
    
    test_cfgs.append(({'hotspot_profiles_list': [deepcopy(def_test_params['hotspot_cfg'])]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot',
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
    

    
    tcid = "[Session timeout ZD disable, radius enable]"
    svr = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.250',
        'radius_auth_secret': '1234567890',
        'server_port': '18120',
        'username': 'rad.timeout.user', 
        'password': 'rad.timeout.user',
        'session_timeout':'2',
    }     
    
    test_cfgs.append((dict(auth_ser_cfg_list = [svr]),
                      'CB_ZD_Create_Authentication_Server',
                      'Create aaa servers',
                      0,
                      False,
                      ))
    hotspot_cfg = deepcopy(def_test_params['hotspot_cfg'])
    hotspot_cfg.update({'auth_svr':svr['server_name']})
    hotspot_cfg.update({'session_timeout':'5'})
    
    test_cfgs.append((dict(hotspot_profiles_list = [hotspot_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))
      
    auth_info = {'username': 'rad.timeout.user', 'password': 'rad.timeout.user',}
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, target_station,
                                                        target_station_radio, open_wlan, 'wg_1')))
    test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))
      
    test_cfgs.append((dict(hotspot_cfg = hotspot_cfg,
                           wlan_cfg = open_wlan,
                           auth_info = svr,
                           sta_tag = 'sta_1',
                           target_ip = '172.16.10.252',                            
                           ),
                       'CB_ZD_Hotspot_Session_Timeout',
                       '%sSession timeout test' % tcid,
                       2,
                       False,
                      ))    
        
    test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, target_station_radio, 
                                                       open_wlan, auth_info, chk=False)))
    
    tcid = '[Session timeout ZD enable, radius enable]'
    h_cfg = deepcopy(hotspot_cfg)
    h_cfg.update({'session_timeout':'2'})
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))
    
    auth_info = {'username': 'rad.timeout.user', 'password': 'rad.timeout.user',}
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, target_station,
                                                        target_station_radio, open_wlan, 'wg_1')))
    test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))
    
    test_cfgs.append((dict(hotspot_cfg = h_cfg,
                           wlan_cfg = open_wlan,
                           auth_info = deepcopy(svr),
                           sta_tag = 'sta_1',
                           target_ip = '172.16.10.252',                            
                           ),
                       'CB_ZD_Hotspot_Session_Timeout',
                       '%sSession timeout test' % tcid,
                       2,
                       False,
                      )) 
    
    test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, target_station_radio, 
                                                       open_wlan, auth_info, chk=False)))
     
    
    tcid = '[Session timeout ZD enable, radius disable]'
    h_cfg = deepcopy(hotspot_cfg)
    h_cfg.update({'session_timeout':'2'})
    h_cfg.update({'auth_svr':'Local Database'})
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))
    
    auth_info = deepcopy(def_test_params['auth_info'])
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, target_station,
                                                        target_station_radio, open_wlan, 'wg_1')))
    test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))
        
    #param = deepcopy(svr)
    #param.pop('session_timeout')
    #param.update({'username': 'rad.cisco.user', 'password': 'rad.cisco.user'})    
    test_cfgs.append((dict(hotspot_cfg = h_cfg,
                           wlan_cfg = open_wlan,
                           auth_info = auth_info,
                           sta_tag = 'sta_1',
                           target_ip = '172.16.10.252',                            
                           ),
                       'CB_ZD_Hotspot_Session_Timeout',
                       '%sSession timeout test' % tcid,
                       2,
                       False,
                      ))   
    
    test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, target_station_radio, 
                                                       open_wlan, auth_info, chk=False)))
    
    test_cfgs.extend(clean_steps(Clean_up = True))   
    
    
    return test_cfgs

def build_idle_timeout_ts(target_station, target_station_radio, active_ap):
    test_cfgs = []
        
#    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    
    open_wlan = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test',)
        
    def_test_params = {'target_station': target_station, 'target_ip': '172.16.10.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
        
            
    test_cfgs.extend(clean_steps(LEVEL = 0))  
    
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
                      0, 
                      False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       0, 
                       False))                
    
    test_cfgs.append(({'hotspot_profiles_list': [deepcopy(def_test_params['hotspot_cfg'])]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot',
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
    #@author: liang aihua,@since: 2015-2-4,@change: IAS grace period don't take effect, so use RADIUS Server's  
    svr = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.252',
        'radius_auth_secret': '123456789',
        'server_port': '1812',        
    }  
    #svr = {
    #    'server_name': 'RADIUS',
    #    'server_addr': '192.168.0.250',
    #    'radius_auth_secret': '1234567890',
    #    'server_port': '18120',        
    #}     
    
    test_cfgs.append((dict(auth_ser_cfg_list = [svr]),
                      'CB_ZD_Create_Authentication_Server',
                      'Create aaa servers',
                      0,
                      False,
                      ))
    hotspot_cfg = deepcopy(def_test_params['hotspot_cfg'])
    hotspot_cfg.update({'auth_svr':svr['server_name']})
    
    tcid = '[Relogin within idle timeout zd disable, radius enable]'        
    h_cfg = deepcopy(hotspot_cfg)  
       
    auth_info = deepcopy(def_test_params['auth_info'])
    auth_info.update({'username': 'idle.timeout.user', 
                      'password': 'idle.timeout.user',                                      
                      'idle_timeout':'10'})    
    test_cfgs.extend(idle_steps(tcid, open_wlan, h_cfg, auth_info, timer_expired = True, 
                                e_p = True, active_ap = active_ap, radio = target_station_radio, 
                                wg = 'wg_1', sta = target_station))   
   
    
    tcid = '[Relogin within session timeout ZD enable, radius enable]'        
    h_cfg = deepcopy(hotspot_cfg)  
    h_cfg.update({'idle_timeout':'5'})   
    auth_info = deepcopy(def_test_params['auth_info'])
    auth_info.update({'username': 'idle.timeout.user', 
                      'password': 'idle.timeout.user',                                      
                      'idle_timeout':'10'})    
    test_cfgs.extend(idle_steps(tcid, open_wlan, h_cfg, auth_info, timer_expired = True, 
                                e_p = True, active_ap = active_ap, radio = target_station_radio, 
                                wg = 'wg_1', sta = target_station))
        
    
    tcid = '[Relogin within idle session timeout ZD enable, radius disable]'        
    h_cfg = deepcopy(hotspot_cfg)         
    h_cfg.update({'idle_timeout':'5'}) 
    h_cfg.update({'auth_svr':'Local Database'})   
    auth_info = deepcopy(def_test_params['auth_info'])
    #auth_info.update({'username': 'rad.cisco.user', 
    #                  'password': 'rad.cisco.user',})    
    test_cfgs.extend(idle_steps(tcid, open_wlan, h_cfg, auth_info, timer_expired = True, 
                                e_p = True, active_ap = active_ap, radio = target_station_radio, 
                                wg = 'wg_1', sta = target_station))
    
    
    tcid = '[Relogin beyond Idle Timeout zd disable, radius enable]'        
    h_cfg = deepcopy(hotspot_cfg)     
    auth_info = deepcopy(def_test_params['auth_info'])
    auth_info.update({'username': 'idle.timeout.user', 
                      'password': 'idle.timeout.user',                                      
                      'idle_timeout':'10'
                      })    
    test_cfgs.extend(idle_steps(tcid, open_wlan, h_cfg, auth_info, timer_expired = False, 
                                e_p = True, active_ap = active_ap, radio = target_station_radio, 
                                wg = 'wg_1', sta = target_station))
    
    tcid = '[Relogin beyond Idle Timeout zd enable, radius enable]'
    h_cfg = deepcopy(hotspot_cfg) 
    h_cfg.update({'idle_timeout':'5'})
    auth_info = deepcopy(def_test_params['auth_info'])
    auth_info.update({'username': 'idle.timeout.user', 
                      'password': 'idle.timeout.user',
                      })     
    test_cfgs.extend(idle_steps(tcid, open_wlan, h_cfg, auth_info, timer_expired = False, 
                                e_p = True, active_ap = active_ap, radio = target_station_radio, 
                                wg = 'wg_1', sta = target_station))
    
    tcid = '[Relogin beyond Idle Timeout zd enable, radius disable]'
    h_cfg = deepcopy(hotspot_cfg) 
    h_cfg.update({'idle_timeout':'5'})  
    h_cfg.update({'auth_svr':'Local Database'})  
   
    auth_info = deepcopy(def_test_params['auth_info'])
    #auth_info.update({'username': 'idle.timeout.user', 
    #                  'password': 'idle.timeout.user',
    #                  })
    
    test_cfgs.extend(idle_steps(tcid, open_wlan, h_cfg, auth_info, timer_expired = False, 
                                e_p = True, active_ap = active_ap, radio = target_station_radio, 
                                wg = 'wg_1', sta = target_station))    
    
    test_cfgs.extend(clean_steps(Clean_up = True))   
    
    return test_cfgs
    

def build_adv_ts(target_station, target_station_radio, active_ap):
    test_cfgs = []
        
#    walled_garden_entries = ["www.example.net", "172.21.0.252", "172.22.0.0/16", "172.23.0.252:8888", "172.23.0.252"]
    
    open_wlan = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                     type = 'hotspot',
                     hotspot_profile = 'wispr_test',)
        
    def_test_params = {'target_station': target_station, 'target_ip': '172.16.10.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'wispr_test'},
                       'auth_info': {'username': 'local.username', 'password': 'local.password'}}
        
            
    test_cfgs.extend(clean_steps())  
    
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
                      0, 
                      False))      
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       0, 
                       False))                
    
    test_cfgs.append(({'hotspot_profiles_list': [deepcopy(def_test_params['hotspot_cfg'])]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot',
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
    
    tcid = '[Accounting server with extra attributes]'

    svr_2 = {
        'server_name': 'RADIUS_2',
        'server_addr': '192.168.0.252',
        'radius_auth_secret': '1234567890',
        'server_port': '1812',                
        }   
     
    svr_3 = {
        'server_name': 'RADIUS Accounting',
        'server_addr': '192.168.0.252',
        'radius_acct_secret': '1234567890',
        'server_port': '1813'
        }
    
    test_cfgs.append((dict(auth_ser_cfg_list = [svr_2, svr_3]),
                      'CB_ZD_Create_Authentication_Server',
                      'Create aaa servers',
                      0,
                      False,
                      ))
    
    h_cfg = deepcopy(def_test_params['hotspot_cfg'])
    h_cfg.update({'auth_svr':svr_2['server_name'],
                  'acct_svr':svr_3['server_name'],
                  'radius_location_id': 'organization=ruckus-wireless-inc',
                  'radius_location_name': '880_west_maude_ave_sunnyvale_ca_94085'})
    
    
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))    
    
    auth_info = {'username': 'rad.cisco.user', 'password': 'rad.cisco.user'}
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, target_station,
                                                        target_station_radio, open_wlan, 'wg_1')))
    test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))    
    
        
    test_cfgs.append(({'hotspot_cfg':h_cfg},
                      'CB_ZD_Hotspot_RadiusAccouting',
                      '%sVerify RADIUS Accounting info' % tcid,
                      2, 
                      False
                      ))
    
    test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, target_station_radio, 
                                                       open_wlan, auth_info)))
    
    tcid = '[Accounting server update frequency]'
    h_cfg = deepcopy(def_test_params['hotspot_cfg'])    
    h_cfg.update({'interim_update_interval': '2',
                  'auth_svr':svr_2['server_name'],
                  'acct_svr':svr_3['server_name']})
        
    test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                      'CB_ZD_Edit_Hotspot_Profiles',
                      '%sUpdate hotspot profile' %tcid,
                      1,
                      False,
                      ))
    
    auth_info = {'username': 'rad.cisco.user', 'password': 'rad.cisco.user'}
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, target_station,
                                                        target_station_radio, open_wlan, 'wg_1')))
    test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))    
        
    test_cfgs.append(({'hotspot_cfg':h_cfg},
                      'CB_ZD_Hotspot_RadiusAccouting',
                      '%sVerify RADIUS Accounting info' % tcid,
                      2, 
                      False
                      ))
    
    #test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))
    test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, target_station_radio, 
                                                       open_wlan, auth_info)))
    
    test_cfgs.extend(clean_steps(Clean_up = True))   

    
    return test_cfgs


def clean_steps(LEVEL = 0, Clean_up = False):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup ENV', 
            LEVEL, 
            Clean_up),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup ENV', 
            LEVEL, 
            Clean_up),            
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles', 
            LEVEL, 
            Clean_up),            
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers',
             LEVEL,
             Clean_up)
            ]
    
def idle_steps(tcid, wlan, h_cfg, auth_info, 
               timer_expired = True, e_p = True, 
               active_ap = None, radio = None, wg = None, sta = None):
    test_cfgs = []
    if e_p:
        test_cfgs.append((dict(hotspot_profiles_list = [h_cfg]),
                          'CB_ZD_Edit_Hotspot_Profiles',
                          '%sUpdate hotspot profile' %tcid,
                          1,
                          False,
                          ))
    test_cfgs.extend(encode_tcid(tcid, station_a_steps(active_ap, sta, radio, wlan, wg)))
    test_cfgs.extend(encode_tcid(tcid, station_c_steps(auth_info)))    
    
    test_params = {'hotspot_cfg':h_cfg,
                   'auth_info':auth_info,
                   'ap_tag':'tap',
                   'sta_tag': 'sta_1',
                   'wlan_cfg': wlan,
                   'target_ip': '172.16.10.252',                   
                   }        
    test_params.update({'relogin_before_timer_expired': timer_expired})
    test_cfgs.append((test_params, 
                      'CB_ZD_Hotspot_Idle_Timeout',
                      '%sRelogin within Idle Timeout threshold' % tcid,
                      2, 
                      False, 
                      )) 
    test_cfgs.extend(encode_tcid(tcid, station_p_steps(active_ap, radio, wlan, auth_info, chk=False)))
               
    
    return test_cfgs

def station_steps(active_ap, sta, radio, wlan, wg, auth_info, EXEC_LEVEL =2):
    test_cfgs = []
    test_cfgs.extend(station_a_steps(active_ap, sta, radio, wlan, wg, EXEC_LEVEL))
    test_cfgs.extend(station_c_steps(auth_info))
    test_cfgs.extend(station_p_steps(active_ap, radio, wlan, auth_info))
    return test_cfgs
   

def station_a_steps(active_ap, sta, radio, wlan, wg, EXEC_LEVEL=2):
    test_cfgs = []
    param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = wg, 
                     radio_mode = radio)    
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Associate AP with radio %s to %s' % (radio, wg), 
                      EXEC_LEVEL, 
                      False))
             
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': wlan}, 
                      'CB_ZD_Associate_Station_1', 
                      'Associate the station', 
                      2, 
                      False))    

    
    test_cfgs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get wifi address', 
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
                      'Verify the station before hotspot auth', 
                      2, 
                      False)) 

#    test_cfgs.append(({'sta_tag': 'sta_1',
#                       'condition': 'disallowed',
#                       'target_ip': '172.16.10.252',},
#                       'CB_ZD_Client_Ping_Dest', 
#                       'The station ping a target IP', 
#                       2, 
#                       False))    

        
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

def station_p_steps(active_ap, radio, wlan, auth_info, chk = True):
    test_cfgs = []
    if chk:
        param_cfg = {'wlan_cfg':wlan, 
                     'chk_empty':False, 
                     'status':'Authorized',
                     'chk_radio':False,
                     'radio_mode':radio,
                     'sta_tag':'sta_1',
                     'ap_tag':'tap',                                  
                     'username':auth_info['username'],
                     'check_status_timeout': 10 * 1000
                     }  
      
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
        
#        test_cfgs.append(({'sta_tag': 'sta_1',
#                 'condition': 'allowed',
#                 'target': '172.16.10.252',},
#                 'CB_ZD_Client_Ping_Dest', 
#                 'The station ping a target IP', 
#                 2, 
#                 False))        
      
    param_cfg = dict(active_ap = active_ap,
                     wlan_group_name = 'Default', 
                     radio_mode = radio)           
    test_cfgs.append((param_cfg, 
                      'CB_ZD_Assign_AP_To_Wlan_Groups', 
                      'Associate AP with radio %s to %s' % (radio, 'Default'), 
                      2, 
                      True))
    
    test_cfgs.append(({'sta_tag':'sta_1'},
              'CB_Station_CaptivePortal_Quit_Browser',
              'Close Authentication browser',
              2,
              True,
              ))       
     
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
                 testsuite_name = "Palo Alto WISPr Basic function - 11g",
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
        ts_name = "Palo Alto WISPr Basic function - 11%s" % (target_sta_radio)        
    else:
        ts_name = attrs["testsuite_name"]
    
    ts_name_list = [('Palo Alto WISPr Basic', build_basic_ts),
                    ('Palo Alto WISPr Session Timeout', build_session_timeout_ts),
                    ('Palo Alto WISPr Idle Timeout', build_idle_timeout_ts),
                    ('Palo Alto WISPr Attribute', build_adv_ts),
                    ]
    for ts_name, fn in ts_name_list:
        #ts = testsuite.get_testsuite("%s - 11%s, %s" % (ts_name, target_sta_radio, ap_model), 
        #                             "%s - 11%s, %s" % (ts_name, target_sta_radio, ap_model), 
        #                             combotest=True)
        ts = testsuite.get_testsuite("%s - 11%s" % (ts_name, target_sta_radio), 
                                     "%s - 11%s" % (ts_name, target_sta_radio), 
                                     combotest=True)
                    
        test_cfgs = fn(target_sta, target_sta_radio, active_ap)
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
          
