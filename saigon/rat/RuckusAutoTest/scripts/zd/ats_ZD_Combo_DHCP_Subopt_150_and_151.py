"""
Verify AP can insert DHCP option82 subopt into DHCP packages.

    Verify AP can insert DHCP option82 subopt into DHCP packages.
    Pre-condition:
       AP joins ZD1
       ZD1 is auto approval
    Test Data:
        
    
    expect result: All steps should result properly.
    
    How to:
        1) Remove all configuraton of ZD
        2) Disable all APs' WLAN service
        3) Disable SW DHCP relay
        4) Enable ZD DHCP relay
        5) Create AP instance and enable its WLAN service
        6) Create station.
        7) Create WLAN and enable subopt randomly
        8) Start Tshark on DHCP server and station
        9) Associate station to WLAN, and authenticate if need
        10) Verify station connection
        11) Stop Tshark on DHCP server and station
        12) Verify DHCP package on DHCP server and station
        13) Edit WLAN to disable subopt
        14) jump to step 8 to 12
        15) Enable DHCP relay on SW
        16) Disable DHCP relay on ZD
        15) Enable all APs' WLAN service
    
Created on 2014-03-03
@author: liu.anzuo@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy

import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


vlan_cfg = {}
'''
vlan_cfg = {"1":{"server_ip_addr":"192.168.0.252",
                 "if":"eth0"},
            "2":{"server_ip_addr":"192.168.10.252",
                 "if":"eth0.10"
                 },                    
            }
'''

def define_test_cfg(cfg):
    test_cfgs = []
    
    if cfg.get('access_vlan'):
        dhcp_server_ip = vlan_cfg.get(cfg.get('access_vlan')).get('server_ip_addr')
    
    test_name = 'CB_ZD_Remove_All_Config' 
    common_name = 'Remove all configurations of ZD before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
    
    test_name = 'CB_L3Switch_Configure_DHCP_Relay' 
    common_name = 'Disable DHCP relay on L3 Switch'
    test_cfgs.append(({'dhcp_relay_conf': {'enable': False,
                                           'vlans': ['301', cfg.get('access_vlan')]}}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = 'Create the ZD DHCP Relay agent'
    test_cfgs.append(({'dhcp_relay_svr_cfg': {'name': dhcp_server_ip, 
                                              'description': 'Agent for default server',
                                              'first_server': dhcp_server_ip}}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create an AAA server in ZD CLI'  
    test_cfgs.append(({'server_cfg_list': [ {'server_name':'radius_server', 
                                             'new_server_name':'radius_server', 
                                             'type':'radius-auth', 'backup':False, 
                                             'server_addr':'192.168.0.252', 
                                             'server_port':'1812', 
                                             'radius_secret':'1234567890', 
                                             'radius_auth_method':'chap',
                                             'cfg_name':'Configure RADIUS CHAP Server without Backup'}]}, test_name, common_name, 0, True))

    std_wlan_cfg = {"name" : "opt82-subopt-std-open-none",
                    "ssid" : "opt82-subopt-std-open-none",
                    "auth" : "open",
                    "encryption" : "none",
                    "vlan_id": cfg.get('access_vlan'),
                    }

    guest_access_conf = {'authentication_server': 'radius_server',
                         'authentication': 'No Authentication.',      
                         'terms_of_use': 'Enabled',
                         'terms': 'Test set term of use by CLI',
                         }
    guest_wlan_cfg =  {"name" : "opt82-subopt-guest-open-none",
                       'ssid': 'opt82-subopt-guest-open-none',
                       'auth': 'open',
                       'encryption' : 'none',     
                       'type':'guest',
                       'guest_access_service':guest_access_conf,
                       "vlan_id": cfg.get('access_vlan'),
                       }
    
    hotspot_conf = {'name': 'Hotsport_Default', 
                    'start_page': '', 
                    'authentication_server':'radius_server', 
                    'accounting_server': 'Disabled', 
                    'login_page_url':'http://192.168.0.250/login.html'}
    hotspot_wlan_cfg = {'name' : 'opt82-subopt-hotspot-open-none',
                        'ssid': 'opt82-subopt-hotspot-open-none',
                        'auth': 'open',
                        'encryption' :'none',
                        'type':'hotspot', 
                        'hotspot_service': hotspot_conf,
                        "vlan_id": cfg.get('access_vlan'),
                        }
    
    autonomous_wlan_cfg = {"name" : "opt82-subopt-autonomo-open-none",
                           "ssid" : "opt82-subopt-autonomo-open-none",
                           "auth" : "open",
                           "encryption" : "none",
                           'type' : 'autonomous',
                           "vlan_id": cfg.get('access_vlan'),
                           }

    wlan_cfgs = {'standard-wlan':std_wlan_cfg,
                 'hotspot-wlan':hotspot_wlan_cfg,
                 'guestaccess-wlan':guest_wlan_cfg,
                 'autonomous-wlan':autonomous_wlan_cfg}
    
    active_ap = cfg.get('active_ap_list')[0]
    ap_sym_name = active_ap.keys()[0]

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP %s' % ap_sym_name
    test_cfgs.append(({'active_ap': ap_sym_name,
                       'ap_tag': ap_sym_name}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_CLI_Configure_AP'
    common_name = 'Enable AP[%s] WLAN service in ZD CLI' % (ap_sym_name)
    test_cfgs.append(({'ap_cfg': {'radio_a':{'wlan_service':'Yes'},  'radio_ng':{'wlan_service':'Yes'}, 'mac_addr':''},
                       'ap_tag': ap_sym_name}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Creates the station'
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg.get('target_station')}, test_name, common_name, 0, False))
    
    tc_common_name = 'Verify DHCP Option82 subopt combine with'
    
    round = 0
    for tc_name in wlan_cfgs.keys():
        step = 0
        round += 1

        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        step += 1
        common_name = '[%s %s]%s.%s remove all wlans from the station' %  (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 0, False))

        wlan_cfg = deepcopy(wlan_cfgs.get(tc_name))
        wlan_cfg['option82'] = True
        wlan_cfg['subopt1'] = True
        wlan_cfg['subopt2'] = True
        wlan_cfg['subopt150'] = True
        wlan_cfg['subopt151'] = True
        wlan_cfg['tunnel_mode'] = True
        
        #@author: yuyanan @since: 2015-2-3 @bug: zf-11882 autonomous wlan can not enable tunnel
        if tc_name in ['autonomous-wlan']:
            wlan_cfg['tunnel_mode'] = None
        
        test_name = 'CB_ZD_CLI_Create_Wlan'
        step += 1
        common_name = '[%s %s]%s.%s Edit WLAN configuration to enable option82 subopt' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'wlan_conf':wlan_cfg}, test_name, common_name, 2, False))

        test_name = 'CB_AP_CLI_Verify_DHCP_option82_config'
        step += 1
        common_name = '[%s %s]%s.%s Check AP configuration' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'ssid':wlan_cfg.get('ssid'),
                           'ap_tag': ap_sym_name}, test_name, common_name, 2, False))

        default_cfg = wlan_cfg
        if default_cfg.has_key('vlan_id') and default_cfg['vlan_id']:        
            params = ' -i %s -f "udp port 67 or udp port 68"' % vlan_cfg[default_cfg['vlan_id']]['if']
        else:
            params = ' -i %s -f "udp port 67 or udp port 68"' % vlan_cfg[cfg.get('access_vlan')]['if']
        
        test_name = 'CB_Station_Start_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Start Tshark on client' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'params': ' -f "udp port 67 and udp port 68" -p',
                           'sta_tag': 'sta1'}, 
                          test_name, common_name, 2, False))
        
        test_name = 'CB_Server_Start_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Start Tshark on DHCP server' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'params':params}, 
                          test_name, common_name, 2, False))

        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        step += 1
        common_name = '[%s %s]%s.%s Associate client to WLAN' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                           'wlan_cfg': wlan_cfg,
                           'start_browser': False,
                           'get_sta_wifi_ip': True,
                           'verify_ip_subnet': False,
                           'is_restart_adapter':False,
                           'tshark_params': ' -f "udp port 67 and udp port 68" -p',
                           }, 
                          test_name, common_name, 2, False))
        
        if tc_name in ['hotspot-wlan']:
                test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
                step += 1
                common_name = "[%s %s]%s.%s perform hotspot auth" % (tc_common_name, tc_name, round, step)
                test_cfgs.append(({'sta_tag': 'sta1', 
                               'username': 'ras.local.user',
                               'password': 'ras.local.user',
                               'start_browser_before_auth': True,
                               'close_browser_after_auth': True}, test_name, common_name, 2, False))
        elif tc_name in ['guestaccess-wlan']:
                test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
                step += 1
                common_name = "[%s %s]%s.%s Perform guest auth" % (tc_common_name, tc_name, round, step)
                test_cfgs.append(({'sta_tag': 'sta1', 
                                  'use_tou': 'Enabled', 
                                  'redirect_url': None, 
                                  'no_auth': False,
                                  'start_browser_before_auth': True,
                                  'close_browser_after_auth': True,
                                  'guest_pass':guest_access_conf}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Connectivity'
        step += 1
        common_name = '[%s %s]%s.%s Verify client connect to WLAN' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                           'wlan_cfg': wlan_cfg,
                           'status': 'Authorized',
                           }, 
                          test_name, common_name, 2, False))
    
        test_name = 'CB_Server_Stop_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Stop Tshark on DHCP server' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({}, test_name, common_name, 2, True))

        test_name = 'CB_Station_Stop_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Stop Tshark on client' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))

        if default_cfg.has_key('vlan_id') and default_cfg['vlan_id']:        
            server_ip_addr = vlan_cfg[default_cfg['vlan_id']]['server_ip_addr']
        else:
            server_ip_addr = vlan_cfg[cfg.get('access_vlan')]['server_ip_addr']
            
        test_name = 'CB_Server_Verify_Option82'
        step += 1
        common_name = '[%s %s]%s.%s Verify package on DHCP server' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                           'option82':wlan_cfg['option82'],
                           'subopt1' :wlan_cfg['subopt1'],
                           'subopt2' :wlan_cfg['subopt2'],
                           'subopt150':wlan_cfg['subopt150'],
                           'subopt151':wlan_cfg['subopt151'],
                           'server_ip_addr': server_ip_addr,}, test_name, common_name, 2, False))

        test_name = 'CB_Station_Verify_Option82'
        step += 1
        common_name = '[%s %s]%s.%s Verify package on client' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                          'option82':wlan_cfg['option82'],
                          'src_ip_addr':server_ip_addr}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        step += 1
        common_name = '[%s %s]%s.%s remove all wlans from the station' %  (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'target_station': 0}, test_name, common_name, 0, False))
        
        wlan_cfg = deepcopy(wlan_cfgs.get(tc_name))
        wlan_cfg['option82'] = False
        wlan_cfg['subopt1'] = False
        wlan_cfg['subopt2'] = False
        wlan_cfg['subopt150'] = False
        wlan_cfg['subopt151'] = False
        test_name = 'CB_ZD_CLI_Create_Wlan'
        step += 1
        common_name = '[%s %s]%s.%s Edit WLAN configuration to disable option82 subopt' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'wlan_conf':wlan_cfg}, test_name, common_name, 2, False))
        
        test_name = 'CB_AP_CLI_Verify_DHCP_option82_config'
        step += 1
        common_name = '[%s %s]%s.%s Check AP configuration' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'ssid':wlan_cfg.get('ssid'),
                           'ap_tag': ap_sym_name}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Start_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Start Tshark on client' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'params': ' -f "udp port 67 and udp port 68" -p',
                           'sta_tag': 'sta1'}, 
                          test_name, common_name, 2, False))
        
        test_name = 'CB_Server_Start_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Start Tshark on DHCP server' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'params': params}, 
                          test_name, common_name, 2, False))
    
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        step += 1
        common_name = '[%s %s]%s.%s Associate client to WLAN' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                           'wlan_cfg': wlan_cfg,
                           'start_browser': False,
                           'get_sta_wifi_ip': True,
                           'verify_ip_subnet': False,
                           'is_restart_adapter':False,
                           'tshark_params': ' -f "udp port 67 and udp port 68" -p'
                           }, 
                          test_name, common_name, 2, False))

        if tc_name in ['hotspot-wlan']:
                test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
                step += 1
                common_name = "[%s %s]%s.%s perform hotspot auth" % (tc_common_name, tc_name, round, step)
                test_cfgs.append(({'sta_tag': 'sta1', 
                               'username': 'ras.local.user',
                               'password': 'ras.local.user',
                               'start_browser_before_auth': True,
                               'close_browser_after_auth': True}, test_name, common_name, 2, False))
        elif tc_name in ['guestaccess-wlan']:
                test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
                step += 1
                common_name = "[%s %s]%s.%s Perform guest auth" % (tc_common_name, tc_name, round, step)
                test_cfgs.append(({'sta_tag': 'sta1', 
                                  'use_tou': 'Enabled', 
                                  'redirect_url': None, 
                                  'no_auth': False,
                                  'start_browser_before_auth': True,
                                  'close_browser_after_auth': True,
                                  'guest_pass':guest_access_conf}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Connectivity'
        step += 1
        common_name = '[%s %s]%s.%s Verify client connect to WLAN' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                           'wlan_cfg': wlan_cfg,
                           'status': 'Authorized',
                           }, 
                          test_name, common_name, 2, False))

        test_name = 'CB_Server_Stop_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Stop Tshark on DHCP server' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({}, test_name, common_name, 2, True))

        test_name = 'CB_Station_Stop_Tshark'
        step += 1
        common_name = '[%s %s]%s.%s Stop Tshark on client' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))
    
        test_name = 'CB_Server_Verify_Option82'
        step += 1
        common_name = '[%s %s]%s.%s Verify package on DHCP server' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                           'option82':wlan_cfg['option82'],
                           'subopt1' :wlan_cfg['subopt1'],
                           'subopt2' :wlan_cfg['subopt2'],
                           'subopt150':wlan_cfg['subopt150'],
                           'subopt151':wlan_cfg['subopt151'],
                           'server_ip_addr': server_ip_addr,}, test_name, common_name, 2, False))

        test_name = 'CB_Station_Verify_Option82'
        step += 1
        common_name = '[%s %s]%s.%s Verify package on client' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({'sta_tag': 'sta1',
                          'option82':wlan_cfg['option82'],
                          'src_ip_addr':server_ip_addr}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Remove_Wlans'
        step += 1
        common_name = '[%s %s]%s.%s Remove WLAN configuration' % (tc_common_name, tc_name, round, step)
        test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_L3Switch_Configure_DHCP_Relay'
    common_name = 'Enable DHCP relay on L3 Switch'
    test_cfgs.append(({'dhcp_relay_conf': {'enable': True,
                                           'vlans': ['301', cfg.get('access_vlan')]}}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Delete_All_DHCP_Relay_Server'
    common_name = 'Delete the ZD DHCP Relay agent'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Delete_AAA_Servers'
    common_name = 'Delete AAA server in ZD CLI'
    test_cfgs.append(({'server_name_list':['radius_server']}, test_name, common_name, 0, True))    
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_cfgs.append(({'cfg_type': 'teardown'}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Config' 
    common_name = 'Remove all configurations of ZD after test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    zd1_gui_tag = 'zd1'
    zd1_cli_tag = 'ZDCLI1'

    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap_list = []
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap_list.append({ap_sym_name:ap_info})

    access_vlan = raw_input("Please input access vlan for wlan[default is 1]")
    if not access_vlan:
        access_vlan = 1 

    server_ip_1 = raw_input("Please input server ip addr for vlan 1[Default is 192.168.0.252]")
    if not server_ip_1:
        server_ip_1 = '192.168.0.252'
        
    server_if_1 = raw_input("Please input server interface for vlan 1[Default is eth0]")
    if not server_if_1:
        server_if_1 = 'eth0'
        
    server_ip_2 = raw_input("Please input server ip addr for vlan %s[Default is 192.168.%s.252]" % (access_vlan, access_vlan))
    if not server_ip_2:
        server_ip_2 = '192.168.%s.252' % access_vlan
        
    server_if_2 = raw_input("Please input server interface for vlan %s[Default is %s.%s]" % (access_vlan, server_if_1, access_vlan))
    if not server_if_2:
        server_if_2 = '%s.%s' % (server_if_1, access_vlan)
        
    vlan_cfg.update({"1":{"server_ip_addr": server_ip_1,
                          "if": server_if_1},
                     access_vlan:{"server_ip_addr": server_ip_2,
                          "if": server_if_2},
                     })

    if active_ap_list != []:
        tcfg = {'target_station':'%s' % target_sta,
                'active_ap_list': active_ap_list,
                'radio_mode': target_sta_radio,
                'target_ip_list': [server_ip_addr],
                'zd1_gui_tag': zd1_gui_tag,
                'zd1_cli_tag': zd1_cli_tag,
                'ap_default_vlan': '0',
                'access_vlan': access_vlan,
                }

        test_cfgs = define_test_cfg(tcfg)

        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            if access_vlan:
                ts_name = "ZD CLI - Verify DHCP Option82 subopt with AP Mgmt Vlan 11%s" % (target_sta_radio)
            else:
                ts_name = "ZD CLI - Verify DHCP Option82 subopt 11%s" % (target_sta_radio)

        ts = testsuite.get_testsuite(ts_name, "Verify DHCP Option82 subopt combine with different wlan type", combotest = True)

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
