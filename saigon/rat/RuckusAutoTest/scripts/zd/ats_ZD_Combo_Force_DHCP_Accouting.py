'''
1. Create Wlan enable Radius accounting server
2. Verify the station with static ip equal to DHCP ip, accouting success, include start stop interim info
2. Verify the station with static ip not equal to DHCP ip, don't accouting

Created on 2013-5-13
@author: Guo.Can@odc-ruckuswireless.com
'''

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = {"name" : "RAT-Open-None-Force-DHCP",
            "ssid" : "RAT-Open-None-Force-DHCP",
            "auth" : "open",
            "encryption" : "none",
            "force_dhcp" : True,
            "force_dhcp_timeout" : 30,
            'acc_server' : '',
            'interim' : 1
            }
ip_cfg = {"static_cfg" : dict(source = 'Static', addr = '192.168.0.231', mask = '255.255.255.0', gateway = '192.168.0.253'),
          "dhcp_cfg" : dict(source = 'dhcp', addr = '', mask = '', gateway = '')
          }
vlan_cfg = {}
'''
vlan_cfg = {"1":{"server_ip_addr":"192.168.0.252",
                 "if":"eth0"},
            "2":{"server_ip_addr":"20.0.2.253",
                 "if":"eth0.2"
                 },                    
            }
'''
test_params = dict(server_cfg_list = [dict(server_name = 'radius_server_acct', type = 'radius-acct', backup = False, 
                                        server_addr = '192.168.0.252', server_port = '1813', radius_secret = '1234567890')])


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
        
    tc_name = "[Force DHCP with Accounting]"
    tcs.extend(build_stcs_acct(wlan_cfg, ip_cfg, tc_name, target_station))
 
    tunnel_cfg = deepcopy(wlan_cfg)
    tunnel_cfg['tunnel_mode'] = True
    tunnel_cfg['name'] = "RAT-Open-None-Force-DHCP-tunnel"
    tunnel_cfg['ssid'] = "RAT-Open-None-Force-DHCP-tunnel" 
    tc_name = "[Force DHCP with Accounting of tunnel wlan]"
    tcs.extend(build_stcs_acct(tunnel_cfg, ip_cfg, tc_name, target_station))
    
    tcs.append(({'cfg_type': 'teardown', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Restore all WLAN Services', 
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
    
    tcs.append(({'server_name_list': [test_params['server_cfg_list'][0]['server_name']]},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove AAA server',
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

def build_stcs_acct(wlan_cfg, ip_cfg, tc_name, target_station):
    tcs = []

    default_cfg = deepcopy(wlan_cfg)
    default_cfg['acc_server'] = test_params['server_cfg_list'][0]['server_name']
    

    acc_svr_port = test_params['server_cfg_list'][0]['server_port']
    #start capture packet
    if default_cfg.has_key('vlan_id') and default_cfg['vlan_id']:        
        params = ' -i %s -f "udp port %s"' % (vlan_cfg[default_cfg['vlan_id']]['if'], acc_svr_port)
    else:
        params = ' -i %s -f "udp port %s"' % (vlan_cfg["1"]['if'], acc_svr_port)
    
    tcs.append(({'params': params},
                'CB_Server_Start_Tshark',
                '%sStart Tshark from DHCP Server' % tc_name,
                2,
                False
                ))
               
    tcs.append(({'wlan_conf':default_cfg},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN from CLI' % tc_name,
                1,
                False))
    
    #--------------------------Valid IP
    #Station associate
    tcs.append(({'sta_tag': 'sta_1', 
             'wlan_cfg': default_cfg,
             'wlan_ssid': default_cfg['ssid']}, 
             'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
              '%sAssociate the station' % tc_name, 
              2, 
              False))
    
    tcs.append(({'ip_cfg' : '',
             'sta_tag' : 'sta_1'},
            'CB_Station_Config_Static_Wifi_Addr',
            '%sSet Station IP to static equal to DHCP'% tc_name,
            2,
            False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after change IP to Static equal DHCP' % tc_name, 
                  2, 
                  False))
    
    #ping long time
    wait_time = int(default_cfg['interim'])*60
    tcs.append(({'timeout': wait_time}, 
                 'CB_Scaling_Waiting', 
                  '%sWait time %s seconds' % (tc_name, wait_time), 
                  2, 
                  False))  
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after change IP to Static equal DHCP after a while' % tc_name, 
                  2, 
                  False))    
    #disassociate
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_ZD_Station_Disconnect_From_WLAN', 
                  '%sStation disconnect from wlan' % tc_name, 
                  2, 
                  False))    
    
    #Stop capture packet
    tcs.append(({},
                'CB_Server_Stop_Tshark',
                '%sStop Tshark from DHCP Server' % tc_name,
                2,
                False
                )) 
        
    #Verify packet
    if default_cfg.has_key('vlan_id') and default_cfg['vlan_id']:        
        server_ip_addr = vlan_cfg[default_cfg['vlan_id']]['server_ip_addr']
    else:
        server_ip_addr = vlan_cfg["1"]['server_ip_addr']
            
    tcs.append(({'check_list': {'acct-start':True,'acct-stop':True, 'acct-interim-update':True},
                'acct_svr_port' : acc_svr_port},
                'CB_Server_Verify_Accounting_Packets',
                '%sVerify package from DHCP Server' % tc_name,
                2, 
                False
                )) 
    
    #--------------------------Invalid IP   
    tcs.append(({'params': params},
                'CB_Server_Start_Tshark',
                '%sStart Tshark from DHCP Server for invalid IP' % tc_name,
                1,
                False
                ))
 
    tcs.append(({'ip_cfg' : ip_cfg['static_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static not equal to DHCP'% tc_name,
                2,
                False
                ))
    
    #associate
    tcs.append(({'sta_tag': 'sta_1', 
             'wlan_cfg': default_cfg}, 
             'CB_ZD_Associate_Station_1', 
              '%sAssociate the station with valid IP' % tc_name, 
              2, 
              False))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied after change ip to invalid' % tc_name, 
                  2, 
                  False))
    
    #Stop capture packet
    tcs.append(({},
                'CB_Server_Stop_Tshark',
                '%sStop Tshark from DHCP Server for invalid ip' % tc_name,
                2,
                False
                ))
         
    #Verify packet      
    tcs.append(({'check_list': {'acct-start':False,'acct-stop':False, 'acct-interim-update':False},
                'acct_svr_port' : acc_svr_port},
                'CB_Server_Verify_Accounting_Packets',
                '%sVerify no package from Accouting Server' % tc_name,
                2, 
                False
                ))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
     
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Force DHCP with Accounting"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    server_ip_1 = raw_input("Please input server ip addr for vlan 1[Default is 192.168.0.252]")
    if not server_ip_1:
        server_ip_1 = '192.168.0.252'
        
    server_if_1 = raw_input("Plase input server interface for vlan 1[Default is eth0]")  
    if not server_if_1:
        server_if_1 = 'eth0'
        
    server_ip_2 = raw_input("Please input server ip addr for vlan 2[Default is 20.0.2.253]")
    if not server_ip_2:
        server_ip_2 = '20.0.2.253'
        
    server_if_2 = raw_input("Plase input server interface for vlan 2[Default is %s.2]" % server_if_1)
    if not server_if_2:
        server_if_2 = '%s.2' % server_if_1
        
    vlan_cfg.update({"1":{"server_ip_addr": server_ip_1,
                          "if": server_if_1},
                     "2":{"server_ip_addr": server_ip_2,
                          "if": server_if_2},
                     })
            
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
                                 "Force DHCP with Accounting", 
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
    