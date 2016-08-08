'''
1. Verify Force DHCP Configuration and diagnostic tool
2. Entrance test for Force DHCP in WLAN configuration
3. Verify Station with invalid IP, Station should disassociate from WLAN.
   3.1 Verify after time out for 4 times, zd block station for 30 seconds
4. Verify Station with valid IP, Station can connect the web.
5. Verify Station with valid IP but lease time expires, Station should disassociate from WLAN.

Created on 2013-5-13
@author: Guo.Can@odc-ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = {"name" : "RAT-Open-None-Force-DHCP",
            "ssid" : "RAT-Open-None-Force-DHCP",
            "auth" : "open",
            "encryption" : "none",
            "force_dhcp" : True,
            "force_dhcp_timeout" : 30
            }
ip_cfg = {"static_cfg" : dict(source = 'Static', addr = '192.168.0.231', mask = '255.255.255.0', gateway = '192.168.0.253'),
          "dhcp_cfg" : dict(source = 'dhcp', addr = '', mask = '', gateway = '')
          }
dhcp_lease_time_cfg = {"new_lease_time" : 120}

def build_tcs(target_station, all_aps_mac_list, ap_radio, active_ap):  #, active_ap_mac): #@ZJ ZF-12016
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
                 'ap_tag': active_ap},   #'active_ap'  #@ZJ ZF-12016                                
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
    
   
    tcs.append(({'ap_tag': active_ap,  #'active_ap' #@ZJ ZF-12016               
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
    
    tcs.append(({}, 
                 'CB_Server_Get_DHCP_Lease_Time', 
                  'Get DHCP lease time', 
                  0, 
                  False))

    tc_name = '[Configuration and diagnostic tool]'
    tcs.extend(build_stcs_config(wlan_cfg, tc_name))

    tcs.append(({'wlan_conf':wlan_cfg},
                'CB_ZD_CLI_Create_Wlan',
                'Create WLAN from CLI',
                0,
                False)) 
    
    tc_name = '[Entrance test for Force DHCP in WLAN configuration]'
    tcs.extend(build_stcs_Entrance(wlan_cfg, tc_name,active_ap))
    
    tc_name = '[Station with invalid IP]'
    tcs.extend(build_stcs_invalid(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, active_ap))

    tc_name = '[DOS attack test]'
    tcs.extend(build_stcs_attack(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, active_ap))    

    tc_name = '[Station with valid IP]'
    tcs.extend(build_stcs_valid(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, ap_radio, active_ap))
 
    tc_name = '[Station with valid IP but lease time expires]'
    tcs.extend(build_stcs_valid_time_expire(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, active_ap))

    tcs.append(({'lease_time': '',
                 'is_clearup': True}, 
                 'CB_Server_Config_DHCP_Lease_Time', 
                  'Change DHCP lease time to initial', 
                  0, 
                  True))  
           
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

def build_stcs_config(wlan_cfg, tc_name):
    tcs = []
    
    invalid_timeout = ['','a','-10','4','65535'] 
    tcs.append(({'invalid_timeout_list':invalid_timeout,
                 'wlan_cfg':wlan_cfg},
                'CB_ZD_Set_Force_DHCP_Invalid_Values',
                '%sConfig invalid timeout value for Force DHCP on GUI' % tc_name,
                1,
                False
                ))
    
    invalid_timeout = ['!','5.0','0','121']
    tcs.append(({'invalid_timeout_list':invalid_timeout,
                 'wlan_cfg':wlan_cfg},
                'CB_ZD_CLI_Set_Force_DHCP_Invalid_Values',
                '%sConfig invalid timeout value for Force DHCP on CLI' % tc_name,
                1,
                False
                ))
    
    return tcs
def build_stcs_Entrance(wlan_cfg, tc_name,active_ap):
    tcs = []

    tcs.append(({'wlan_cfg':wlan_cfg},
                'CB_ZD_Verify_Force_DHCP_GUI_CLI_Get',
                '%sVerify Force DHCP CLI set and GUI get'% tc_name,
                1,
                False))
     
    tcs.append(({'wlan_cfg':wlan_cfg,
                 'ap_tag': active_ap}, #@ZJ 20140318 ZF-12016 
                'CB_AP_CLI_Verify_Force_DHCP',
                '%sVerify Force DHCP on AP'% tc_name,
                2,
                False))  
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False)) 
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed' % tc_name, 
                  2, 
                  False))
    return tcs

def build_stcs_invalid(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, active_ap):
    tcs = []

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  1, 
                  False)) 
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed' % tc_name, 
                  2, 
                  False))
        
    tcs.append(({},
                'CB_ZD_Clear_Event',
                '%sClear all events'% tc_name,
                1,
                False
                ))
    
    tcs.append(({'ip_cfg' : ip_cfg['static_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static'% tc_name,
                1,
                False
                ))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied' % tc_name, 
                  2, 
                  False))
    
    wait_time = int(wlan_cfg['force_dhcp_timeout'])
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds' % (tc_name, wait_time), 
                  2, 
                  False)) 
       
    tcs.append(({'ap_tag': active_ap, #'ap_mac': active_ap_mac, #@ZJ 20140318 ZF-12016 
                 'wlan_cfg': wlan_cfg,
                 'dhcp_lease_time' : '',
                 'event_type': 'timeout',
                 'sta_tag' : 'sta_1'}, 
                 'CB_ZD_Verify_Force_DHCP_Events', 
                  '%sVerify Force DHCP events' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
        
    return tcs

def build_stcs_attack(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, active_ap):
    tcs = []
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  1, 
                  False)) 
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed' % tc_name, 
                  2, 
                  False))
        
    tcs.append(({},
                'CB_ZD_Clear_Event',
                '%sClear all events'% tc_name,
                1,
                False
                ))
    
    tcs.append(({'ip_cfg' : ip_cfg['static_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static'% tc_name,
                1,
                False
                ))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied' % tc_name, 
                  2, 
                  False))
           
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_ZD_Associate_Station_1', 
                  '%sAssociate the station 2 times' % tc_name, 
                  2, 
                  False))  
    
    wait_time = int(wlan_cfg['force_dhcp_timeout'])
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds for 3 times' % (tc_name, wait_time), 
                  2, 
                  False))  

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_ZD_Associate_Station_1', 
                  '%sAssociate the station 3 times' % tc_name, 
                  2, 
                  False))

    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds for 4 times' % (tc_name, wait_time), 
                  2, 
                  False))
        
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_ZD_Associate_Station_1', 
                  '%sAssociate the station 4 times' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ap_tag': active_ap, #'ap_mac': active_ap_mac, #@ZJ 20140318 ZF-12016 
                 'wlan_cfg': wlan_cfg,
                 'dhcp_lease_time' : '',
                 'event_type': 'block'},
                 'CB_ZD_Verify_Force_DHCP_Events', 
                  '%sVerify Force DHCP events' % tc_name, 
                  2, 
                  False))    
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
    return tcs

def build_stcs_valid(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, ap_radio,active_ap):
    tcs = []

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({},
                'CB_ZD_Clear_Event',
                '%sClear all events'% tc_name,
                2,
                False))

    tcs.append(({'ip_cfg' : '',
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static'% tc_name,
                2,
                False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after change IP to Static equal DHCP' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'ap_tag' : active_ap, #'active_ap' #@ZJ ZF-12016 
                 'status': 'Authorized',
                 'wlan_cfg': wlan_cfg,
                 'radio_mode': ap_radio
                 }, 
                 'CB_ZD_Verify_Station_Info', 
                  '%sVerify Station info in ZD' % tc_name, 
                  2, 
                  False))
   
    tcs.append(({'sta_tag': 'sta_1',
                  'max_lease_time': '',
                  'check_time' : '',
                  'time_range': 100}, 
                 'CB_ZD_CLI_Verify_DHCP_Lease_Time', 
                  '%sVerify DHCP lease time on ZD' % tc_name, 
                  2, 
                  False))    

    tcs.append(({'wlan_cfg': wlan_cfg,
                  'sta_tag': 'sta_1',
                  'ap_tag' : active_ap , #'active_ap' #@ZJ ZF-12016 
                  'check_time' : '',
                  'time_range': 200}, 
                 'CB_AP_CLI_Verify_DHCP_Lease_Time', 
                  '%sVerify DHCP lease time on AP' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
    return tcs

def build_stcs_valid_time_expire(wlan_cfg, ip_cfg, dhcp_lease_time_cfg, tc_name, active_ap):
    tcs = []
    tcs.append(({'lease_time': dhcp_lease_time_cfg['new_lease_time']}, 
                 'CB_Server_Config_DHCP_Lease_Time', 
                  '%sChange DHCP lease time' % tc_name, 
                  1, 
                  False)) 

    tcs.append(({},
                'CB_ZD_Clear_Event',
                '%sClear all events'% tc_name,
                2,
                False))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed' % tc_name, 
                  2, 
                  False))

    tcs.append(({'ip_cfg' : '',
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static'% tc_name,
                2,
                False))
    
    wait_time = int(dhcp_lease_time_cfg['new_lease_time']) + int(wlan_cfg['force_dhcp_timeout'])
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds' % (tc_name, wait_time), 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied' % tc_name, 
                  1, 
                  False))
      
    tcs.append(({'ap_tag': active_ap, #'ap_mac': active_ap_mac, #@ZJ 20140318 ZF-12016 
                 'wlan_cfg': wlan_cfg,
                 'dhcp_lease_time' : 0,
                 'event_type': 'timeout'}, 
                 'CB_ZD_Verify_Force_DHCP_Events', 
                  '%sVerify Force DHCP events' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1',
                 'renew_ip' : False},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg,
                 'wlan_ssid': wlan_cfg['ssid']}, 
                 'CB_ZD_Associate_Station_1', 
                  '%sAssociate the station after set dhcp when lease time is 0' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after set dhcp when lease time is 0' % tc_name, 
                  2, 
                  False))    
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Force DHCP Basic"
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
#            active_ap_mac = ap_info['mac']     
            break
          
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Force DHCP Basic", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta_ip_addr, all_aps_mac_list, target_sta_radio, active_ap) #, active_ap_mac) #@ZJ ZF-12016

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
    