'''
1. Create Wlan with Hotspot and enable Force DHCP
2. Verify station can authenticate and ping success if the station with static ip equal to DHCP ip

Created on 2013-5-13
@author: Guo.Can@odc-ruckuswireless.com
'''

import sys
import libZD_TestSuite as testsuite
from copy import deepcopy
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = {"name" : "RAT-Open-None-Force-DHCP",
            "ssid" : "RAT-Open-None-Force-DHCP",
            'type': 'hotspot',
            'hotspot_profile' : '',
            "auth" : "open",
            "encryption" : "none",
            "force_dhcp" : True,
            "force_dhcp_timeout" : 30,
            }
ip_cfg = {"static_cfg" : dict(source = 'Static', addr = '192.168.0.231', mask = '255.255.255.0', gateway = '192.168.0.253'),
          "dhcp_cfg" : dict(source = 'dhcp', addr = '', mask = '', gateway = '')}
local_user_cfg = {'username': 'local_user', 'password': 'local_user',}
hotspot_cfg = {
    'name': 'hotspot-force-dhcp',
    'login_page': 'http://192.168.0.250/login.html',
    'idle_timeout': None,
    'auth_svr': 'Local Database',
    }

def build_tcs(target_station, all_aps_mac_list, ap_radio, active_ap, active_ap_mac):
    tcs = [] 
    #@ZJ ZF-10187 Disable dhcp relay setting on l3 switch**************************************************
    target_vlan = ['301']
    tcs.append(({'dhcp_relay_conf': {'enable': False,
                                    'vlans': target_vlan}}, 
                'CB_L3Switch_Configure_DHCP_Relay', 
                'Modify the configuration on L3 switch: disable DHCP Relay', 
                0, 
                False))  
           
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Remove All WLAN Groups',
                0,
                False))
                  
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
  
    tcs.append(({'active_ap': active_ap,
                 'ap_tag':'active_ap'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP',
                0,
                False))
    
    tcs.append(({'cfg_type': 'init', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Config All APs Radio - Disable WLAN Service', 
                 0, 
                 False))
    
   
    tcs.append(({'ap_tag': 'active_ap',                      
                 'cfg_type': 'config',
                 'ap_cfg': {'wlan_service': True, 'radio': ap_radio}},
                 'CB_ZD_Config_AP_Radio',
                 'Config active AP Radio %s - Enable WLAN Service' % ap_radio,
                 0, 
                 False))    

    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': target_station}, 
                   'CB_ZD_Create_Station', 
                   'Create the station', 
                   0, 
                   False))
    
    tc_name = "[Force DHCP with Hotspot]"
    tcs.extend(build_stcs_hotspot(target_station, tc_name))
           
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Clean All WLAN Groups',
                0,
                True))  
                  
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                True))
    
    tcs.append(({'cfg_type': 'teardown', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Restore all WLAN Services', 
                 0, 
                 True))
    #**********************************************************
    tcs.append(({'dhcp_relay_conf': {'enable': True,
                                    'vlans': target_vlan}}, 
                'CB_L3Switch_Configure_DHCP_Relay', 
                'Restoring the configuration on switch: enable DHCP Relay', 
                0, 
                True))
            
    return tcs

def build_stcs_hotspot(target_station, tc_name):
    tcs = []    
    
    #create user
    tcs.append(({'username': local_user_cfg['username'], 
                'password': local_user_cfg['password']}, 
                   'CB_ZD_Create_Local_User', 
                   '%sCreate local user' % tc_name, 
                   1, 
                   False))
    
    #create hotspot
    def_hotspot_params = {'target_station': target_station, 'target_ip': '172.16.10.252',
                       'hotspot_cfg': hotspot_cfg,
                       'auth_info': {'username': local_user_cfg['username'], 
                                     'password': local_user_cfg['password']}
                          }
    
    tcs.append(({'hotspot_profiles_list': [deepcopy(def_hotspot_params['hotspot_cfg'])]},
                'CB_ZD_Create_Hotspot_Profiles',
                '%sCreate a hotspot' % tc_name,
                2, 
                False,                      
                ))
    
    #create wlan
    default_wlan = deepcopy(wlan_cfg)
    default_wlan['hotspot_profile'] = hotspot_cfg['name']
    tcs.append(({'wlan_conf':default_wlan},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN from CLI' % tc_name,
                2,
                False))
    
    #Station associate
    tcs.append(({'sta_tag': 'sta_1', 
             'wlan_cfg': wlan_cfg,
             'wlan_ssid': wlan_cfg['ssid']}, 
             'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
              '%sAssociate the station' % tc_name, 
              2, 
              False))
    
    tcs.append(({'sta_tag': "sta_1",
            #'sta_ins_attr': target_station,
            'username': local_user_cfg['username'],
            'password': local_user_cfg['password'],
            'start_browser_before_auth': True,
            'close_browser_after_auth': True
             }, 
             'CB_Station_CaptivePortal_Perform_HotspotAuth', 
              '%sDo hotspot authentication' % tc_name, 
              2, 
              False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing station' % tc_name, 
                  2, 
                  False))

    tcs.append(({'ip_cfg' : ip_cfg['static_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static not equal dhcp ip'% tc_name,
                2,
                False
                ))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP after change ip not equal dhcp ip'% tc_name,
                2,
                True))
    
    tcs.append(({'ip_cfg' : '',
             'sta_tag' : 'sta_1'},
            'CB_Station_Config_Static_Wifi_Addr',
            '%sSet Station IP to static equal dhcp ip'% tc_name,
            2,
            False))
    
    #@author: Jane.Guo @since: 2013-6-19 add a step to do authentication if station is dis-associate
    tcs.append(({'sta_tag': "sta_1",
            #'sta_ins_attr': target_station,
            'username': local_user_cfg['username'],
            'password': local_user_cfg['password'],
            'start_browser_before_auth': True,
            'close_browser_after_auth': True
             }, 
             'CB_Station_CaptivePortal_Perform_HotspotAuth', 
              '%sDo hotspot authentication after change ip' % tc_name, 
              2, 
              False))    
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after change IP to Static equal DHCP' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Force DHCP with hotspot"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
            
    ts_name = attrs['testsuite_name']
    sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
    target_sta_radio = testsuite.get_target_sta_radio()
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            active_ap_mac = ap_info['mac']           
            break
          
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Force DHCP with hotspot", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta_ip_addr, all_aps_mac_list, target_sta_radio, active_ap, active_ap_mac)

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
    