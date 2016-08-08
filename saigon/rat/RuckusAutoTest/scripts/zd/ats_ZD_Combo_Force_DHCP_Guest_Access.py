'''
1. Create Wlan with Guest Access and enable Force DHCP
2. Verify station can authenticate and ping success if the station with static ip equal to DHCP ip

Created on 2013-5-13
@author: Guo.Can@odc-ruckuswireless.com
'''

import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = {"name" : "RAT-Open-None-Force-DHCP",
            "ssid" : "RAT-Open-None-Force-DHCP",
            'type': 'guest',
            'do_tunnel': False,
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
test_params = dict(server_cfg_list = [dict(server_name = 'radius_server', type = 'radius-auth', backup = False, 
                                        server_addr = '192.168.0.252', server_port = '1812', radius_secret = '1234567890')])

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

    tcs.append((test_params, 
                'CB_ZD_CLI_Configure_AAA_Servers', 
                'Creates AAA Server via CLI', 
                0, 
                False))  
    
    tc_name = "[Force DHCP with Guest Access]"
    tcs.extend(build_stcs_guest_access(target_station, tc_name))
           
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

    tcs.append(({'server_name_list': [test_params['server_cfg_list'][0]['server_name']]},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove AAA server',
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

def build_stcs_guest_access(target_station, tc_name):
    tcs = []    
    target_url = 'http://172.16.10.252/'
    dest_ip = '172.16.10.252'
    username = 'ras.local.user'
    password = 'ras.local.user'
    guest_policy = {'Auth/TOU/No Redirection': {'generate_guestpass_cfg': dict(type = "single",
                                                                               guest_fullname = "Guest-Auth",
                                                                               duration = "5",
                                                                               duration_unit = "Days",
                                                                               key = "",
                                                                               wlan = wlan_cfg['ssid'],
                                                                               remarks = "",
                                                                               is_shared = "YES",
                                                                               auth_ser = '',
                                                                               username = username,
                                                                               password = password),
                                                },
                    }
         
    guest_access_conf = {'authentication_server': 'radius_server',                 
                      'terms_of_use': 'Enabled',
                      'terms': 'Test set term of use by CLI'}

    tcs.append(({'guest_access_conf': guest_access_conf}, 
                   'CB_ZD_CLI_Configure_Guest_Access', 
                   '%sSet guest access authentication server' % tc_name, 
                   2, 
                   False))
    
    #create wlan
    tcs.append(({'wlan_conf':wlan_cfg},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN from CLI' % tc_name,
                2,
                False))

    tcs.append(( guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg'],
                'CB_ZD_Generate_Guest_Pass',
                '%sGenerate the guestpass by the guest user' % tc_name,
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
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'check_status_timeout': 10000}, 
             'CB_ZD_Station_Verify_Client_Unauthorized', 
              '%sVerify the station info which is unauthorized via GUI' % tc_name, 
              2, 
              False))

    tcs.append(({'sta_tag' : 'sta_1',
                 'dest_ip': dest_ip}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied' % tc_name, 
                  2, 
                  False))
    
    #Perform Guest Auth
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_CaptivePortal_Start_Browser', 
                  "%sCreate the station's browser object" % tc_name, 
                  2, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1',
                   'no_auth': False, 
                   'use_tou': True,
                   'target_url': target_url, 
                   'redirect_url': '',
                   }, 
                'CB_Station_CaptivePortal_Perform_GuestAuth', 
                '%sPerform guest authentication' % tc_name, 
                2, 
                False))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_CaptivePortal_Quit_Browser', 
                  "%sClosed the station's browser object" % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'username': guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg']['guest_fullname'],
                 'check_status_timeout': 10000}, 
             'CB_ZD_Station_Verify_Client_Authorized', 
              '%sVerify the station info which is authorized via GUI' % tc_name, 
              2, 
              False))
      
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': dest_ip}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing station is allowed after authentication' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg' : '',
             'sta_tag' : 'sta_1'},
            'CB_Station_Config_Static_Wifi_Addr',
            '%sSet Station IP to static equal dhcp ip'% tc_name,
            2,
            False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': dest_ip}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after change IP to Static equal DHCP' % tc_name, 
                  2, 
                  False))

    tcs.append(({'ip_cfg' : ip_cfg['static_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static not equal dhcp ip'% tc_name,
                2,
                False
                ))
    
    tcs.append(({'sta_tag' : 'sta_1',
                 'dest_ip': dest_ip}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied if ip not equal dhcp ip' % tc_name, 
                  2, 
                  False))
    #Clear up
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))

    guest_access_conf = {'authentication_server': 'Local Database',                 
                      'terms_of_use': 'Disabled'}
    
    tcs.append(({'guest_access_conf': guest_access_conf},
                'CB_ZD_CLI_Configure_Guest_Access',
                '%sCleanup Guest Access'% tc_name,
                2,
                True))

    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Force DHCP with Guest Access"
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
                                 "Force DHCP with Guest Access", 
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
    