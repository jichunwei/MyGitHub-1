"""
Mesh(4 tcs)

    Enable mesh
    setup 1 RootAP, 2 MeshAP
    client isolaiton disable
    sta1 connect to RootAP, sta2 connect to MeshAP
    sta1,sta2 can ping gw
    client isolation enable
    [standard wlan, root and mesh]sta1 connect to RootAP, sta2 connect to MeshAP
    [standard wlan, root and mesh]sta1,sta2 can not ping gw
    [standard wlan, root and mesh]sta1 can ping sta2
    [standard wlan, root and mesh]bind MAC only entry to wlan
    [standard wlan, root and mesh]sta1 can ping PC, sta2 can ping PC
    [standard wlan, root and mesh, different subnet]sta1,sta2 in different subnet
    [standard wlan, root and mesh, different subnet]sta1 can ping
    [standard wlan, root and mesh, different subnet]sta2bind MAC only entry to wlan
    [standard wlan, root and mesh, different subnet]sta1 can ping PC, sta2 can ping PC
    [Hotspot wlan, mesh and mesh]sta1 connect to MeshAP, sta2 connect to MeshAP
    [Hotspot wlan, mesh and mesh]sta1,sta2 can not ping gw
    [Hotspot wlan, mesh and mesh]sta1 can ping sta2
    [Hotspot wlan, mesh and mesh]bind IP and MAC entry to wlan
    [Hotspot wlan, mesh and mesh]sta1 can ping PC, sta2 can ping PC
    
Created on 2013-7-22
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Mesh-1",
            "ssid" : "Rqa-auto-RAT-CI-Mesh-1",
            "auth" : "open",
            "encryption" : "none",
            }

ci_wlan2_cfg = {"name" : "Rqa-auto-RAT-CI-Mesh-2",
            "ssid" : "Rqa-auto-RAT-CI-Mesh-2",
            "auth" : "open",
            "encryption" : "none",
            }

default_ip = {'switch' : '192.168.0.253',
              'server' : '192.168.0.252',
              'win2k3' : '192.168.0.250',
              }

whitelist_conf = {'name':'White-Basic-1',
                  'description':'White-Basic-1'
                      }
whitelist2_conf = {'name':'White-Basic-2',
                  'description':'White-Basic-2'
                      }

local_user_cfg = {'username': 'local_user', 'password': 'local_user','role':'Default'}
hotspot_cfg = {
    'name': 'hotspot-Client-Isolation',
    'login_page': 'http://192.168.0.250/login.html',
    'idle_timeout': None,
    'auth_svr': 'Local Database',
    }

def build_tcs(sta1_ip_addr, sta2_ip_addr, all_aps_mac_list, active_ap1, active_ap1_mac, active_ap2, active_ap2_mac, active_ap3, active_ap3_mac, win2k3_mac):
    tcs = []
                  
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Remove all WLANs', 
                0, 
                False))

    tcs.append(({}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                'Remove all white lists', 
                0, 
                False))
    
    tcs.append(({'cfg_type': "init"}, 
                'CB_ZD_Config_AP_Policy_Mgmt_VLAN', 
                'Backup AP Mgmt VLAN current settings', 
                0, 
                False))    
    
    tcs.append(({'mgmt_vlan': {'mode': "enable", 'vlan_id': '1', },
                       'cfg_type': "config",
                       }, 
                'CB_ZD_Config_AP_Policy_Mgmt_VLAN', 
                'Config AP Mgmt VLAN to 1', 
                0, 
                False))
    
    tcs.append(({'mesh_ap_mac_list':'',
                 'for_upgrade_test':False},
                'CB_ZD_Enable_Mesh', 
                'Enable mesh in ZD', 
                0, 
                False))
  
    tcs.append(({'active_ap': active_ap1,
                 'ap_tag':'AP_01'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Root AP_01',
                0,
                False))

    tcs.append(({'active_ap': active_ap2,
                 'ap_tag':'AP_02'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Mesh AP_02',
                0,
                False))

    tcs.append(({'active_ap': active_ap3,
                 'ap_tag':'AP_03'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Mesh AP_03',
                0,
                False))

    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': sta1_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 1', 
                   0, 
                   False))

    tcs.append(({'sta_tag': 'sta_2', 
                   'sta_ip_addr': sta2_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 2', 
                   0, 
                   False))
    
    tcs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_02',
                       'test_option': 'form_mesh_mesh_acl'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Setting up mesh ap AP_02', 
                   0, 
                   False))
 
    tcs.append(({'root_ap': 'AP_01',
                       'mesh_ap': 'AP_03',
                       'test_option': 'form_mesh_mesh_acl',
                       'vlan':'778' }, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Setting up mesh ap AP_03', 
                   0, 
                   False))

    tcs.append(({'name': local_user_cfg['username'], 
                 'fullname':local_user_cfg['username'],
                 'role': local_user_cfg['role'],
                'password': local_user_cfg['password']}, 
                   'CB_ZD_CLI_Create_Users', 
                   'Create local user from CLI', 
                   0, 
                   False))
    
    test_list = _generate_test_cfg_standard()

    for test_case in test_list:
        tcs.extend(build_stcs_main_standard(test_case))
        
    test_list = _generate_test_cfg_hotspot()

    for test_case in test_list:
        tcs.extend(build_stcs_main_hotspot(test_case, win2k3_mac))
        

    tcs.append(({'ap_list': ['AP_01', 'AP_02', 'AP_03'],
                       'test_option': 'reconnect_as_root'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Reconnect all active APs as Root', 
                   0, 
                   True))

    tcs.append(({'name': local_user_cfg['username']}, 
                   'CB_ZD_CLI_Delete_User', 
                   'Delete local user for cleanup ENV', 
                   0, 
                   True))
            
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                True))

    tcs.append(({}, 
                'CB_ZD_CLI_Delete_White_Lists_Batch', 
                'Remove all white lists for cleanup ENV', 
                0, 
                True))

    tcs.append(({},
                'CB_ZD_Set_Factory_Default', 
                'ZD set Factory to clear configuration', 
                0, 
                True))
    
    tcs.append(({'cfg_type': "teardown"}, 
                'CB_ZD_Config_AP_Policy_Mgmt_VLAN', 
                'Restore AP Mgmt VLAN settings', 
                0, 
                True))   
            
    return tcs

def _generate_test_cfg_hotspot():
    test_cfg = []

    test_cfg.append(({'tc_name' : '[Hotspot wlan, mesh and mesh AP, IP and MAC]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'AP1' : 'AP_02',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_03',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': False,
                  }))

    test_cfg.append(({'tc_name' : '[Hotspot wlan, root and mesh AP, MAC only, different radio]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_03',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': False,
                  }))

    return test_cfg

def _generate_test_cfg_standard():
    test_cfg = []

    test_cfg.append(({'tc_name' : '[Client Isolation disable]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : False,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : False,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': True,
                  }))

    test_cfg.append(({'tc_name' : '[Client Isolation per AP, root and mesh AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': False, #Checked with R&D:SRC guard and SPOOF guard are both disabled on Mesh Downlink interface.  
                                        #So the packet is dropped at wlan1 near the destination client (RUNI), not at mesh downlink interface.
                  }))

    test_cfg.append(({'tc_name' : '[Client Isolation per AP, same mesh AP, with tunnel]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'tunnel_mode' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'tunnel_mode' : True,
                            },
                  'AP1' : 'AP_02',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': False,
                  }))
    
    test_cfg.append(({'tc_name' : '[Standard wlan, root and mesh AP, MAC only]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': False,
                  }))

    test_cfg.append(({'tc_name' : '[Standard wlan, root and mesh AP, different subnet]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                              'vlan_id' : 10,
                              'gateway_ip' : '192.168.10.253',
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist2_conf['name'],
                              'rule_type' : 'MAC',
                              'vlan_id' : 20,
                              'gateway_ip' : '192.168.20.253',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11a/n',
                  'ping_result': True,
                  }))

    return test_cfg
    
def build_stcs_main_standard(test_case):
    tcs = []

    tc_name = test_case['tc_name']
    wlan1 = test_case['wlan1']
    wlan1_cfg = wlan1['wlan_cfg']
    wlan2 = test_case['wlan2']
    wlan2_cfg = wlan2['wlan_cfg']
    AP1 = test_case['AP1']
    AP1_radio = test_case['AP1_radio']
    AP2 = test_case['AP2']
    AP2_radio = test_case['AP2_radio']
    ping_result = test_case['ping_result']
    
    white_list = wlan1.get('white_list')
    if white_list:  
        rule_type = wlan1.get('rule_type')
        if wlan1.get('gateway_ip'):
            wlan1_gateway_ip = wlan1.get('gateway_ip')
        else:
            wlan1_gateway_ip = default_ip['switch']
        tcs.append(({'white_list_name':white_list,
                      'rule_no':'1',
                      'rule_type': rule_type,
                      'value_type':'switch',
                      'ip_tag': wlan1_gateway_ip
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list for gateway from CLI' % tc_name,
                    1,
                    False))
        
        if not wlan1.get('white_list') == wlan2.get('white_list'):
            if wlan2.get('gateway_ip'):
                wlan2_gateway_ip = wlan2.get('gateway_ip')
            else:
                wlan2_gateway_ip = default_ip['switch']            
            tcs.append(({'white_list_name':wlan2.get('white_list'),
                          'rule_no':'1',
                          'rule_type': wlan2.get('rule_type'),
                          'value_type':'switch',
                          'ip_tag': wlan2_gateway_ip
                          },
                        'CB_ZD_CLI_Edit_White_List_Special',
                        '%sCreate White list 2 for gateway from CLI' % tc_name,
                        2,
                        False))        
    
    wlan1_default_cfg = deepcopy(wlan1_cfg)
    wlan1_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                              'isolation_across_ap': wlan1.get('isolation_across_ap'),
                              'white_list' : wlan1.get('white_list'),
                              'tunnel_mode': wlan1.get('tunnel_mode'),
                              'vlan_id': wlan1.get('vlan_id'),
                              })

    tcs.append(({'wlan_conf':wlan1_default_cfg},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN 1 from CLI' % tc_name,
                1,
                False))
    
    tcs.append(({},
                'CB_ZDCLI_Get_Wlan_By_SSID',
                '%sGet ZD WLAN 1 Info via CLI' % tc_name,
                2,
                False))

    tcs.append(({},
                'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                '%sVerify Wlan 1 Info Between CLI Set and CLI Get' % tc_name,
                2,
                False))
        
    if not wlan2_cfg == wlan1_cfg:
        wlan2_default_cfg = deepcopy(wlan2_cfg)
        wlan2_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                              'isolation_across_ap': wlan1.get('isolation_across_ap'),
                              'white_list' : wlan2.get('white_list'),
                              'tunnel_mode': wlan2.get('tunnel_mode'),
                              'vlan_id': wlan2.get('vlan_id'),
                              })
        tcs.append(({'wlan_conf':wlan2_default_cfg},
                    'CB_ZD_CLI_Create_Wlan',
                    '%sCreate WLAN 2 from CLI' % tc_name,
                    2,
                    False))
        
        tcs.append(({},
                    'CB_ZDCLI_Get_Wlan_By_SSID',
                    '%sGet ZD WLAN 2 Info via CLI' % tc_name,
                    2,
                    False))
    
        tcs.append(({},
                    'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                    '%sVerify Wlan 2 Info Between CLI Set and CLI Get' % tc_name,
                    2,
                    False))
        
    else:
        wlan2_default_cfg = wlan1_default_cfg
        
    tcs.append(({'wlan_cfg':wlan1_default_cfg,
                 'ap_tag':AP1,
                 'ap_radio': AP1_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 1' % tc_name,
                2,
                False
                ))
         
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan1_default_cfg,
                 'wlan_ssid': wlan1_default_cfg['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 1 to wlan' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'wlan_cfg':wlan2_default_cfg,
                 'ap_tag':AP2,
                 'ap_radio': AP2_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 2' % tc_name,
                2,
                False
                ))   
    
    
    if "[Client Isolation per AP, root and mesh AP]" in tc_name:
        tcs.append(({'sta_tag': 'sta_2', 
                     'wlan_cfg': wlan2_default_cfg,
                     'wlan_ssid': wlan2_default_cfg['ssid'],
                     'ap_tag': AP1}, 
                     'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                      '%sAssociate the station 2 to wlan' % tc_name, 
                      2, 
                      False))
    else:
        tcs.append(({'sta_tag': 'sta_2', 
                     'wlan_cfg': wlan2_default_cfg,
                     'wlan_ssid': wlan2_default_cfg['ssid'],
                     'ap_tag': AP2}, 
                     'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                      '%sAssociate the station 2 to wlan' % tc_name, 
                      2, 
                      False))

    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 1 Ping Gateway is Allowed' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'sta_tag': 'sta_2',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 2 Ping Gateway is Allowed' % tc_name, 
                  2, 
                  False))

    if ping_result:
        condition = 'allowed'
    else:
        condition = 'disallowed'
        
    tcs.append(({'src_sta_tag': 'sta_1',
                 'dst_sta_tag': 'sta_2',
                 'condition': condition,
                 'clean_arp_before_ping': True},
                 'CB_ZD_Client_Ping_Another', 
                  '%sStation Ping Another Station is %s' % (tc_name,condition), 
                  2,
                  False)) 
    
    if white_list and not wlan1_default_cfg.get('vlan_id'):
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation 1 Ping Linux Server is Denied before add entry' % tc_name, 
                      2, 
                      False))

        tcs.append(({'sta_tag': 'sta_2',
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation 2 Ping Linux Server is Denied before add entry' % tc_name, 
                      2, 
                      False))

        tcs.append(({'white_list_name':white_list,
                      'rule_no':'2',
                      'rule_type': rule_type,
                      'value_type':'server',
                      'ip_tag': default_ip['server']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule of white list 1 for server from CLI' % tc_name,
                    2,
                    False))

        if not wlan1.get('white_list') == wlan2.get('white_list'):
            tcs.append(({'white_list_name':wlan2.get('white_list'),
                          'rule_no':'2',
                          'rule_type': wlan2.get('rule_type'),
                          'value_type':'server',
                          'ip_tag': default_ip['server']
                          },
                        'CB_ZD_CLI_Edit_White_List_Special',
                        '%sAdd rule of white list 2 for server from CLI' % tc_name,
                        2,
                        False))


    if 'different subnet' in tc_name:
        target_ip = default_ip['win2k3']
        tmp_name = "Win2003 Server"
    else:
        target_ip = default_ip['server']
        tmp_name = "Linux Server"
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': target_ip}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 1 Ping %s is Allowed' % (tc_name, tmp_name), 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_2',
                 'dest_ip': target_ip}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 2 Ping %s is Allowed' % (tc_name, tmp_name), 
                  2, 
                  False))

    wlan_list = []
    wlan_list.append(wlan1_default_cfg['ssid'])
    if not wlan2_cfg == wlan1_cfg:
        wlan_list.append(wlan2_default_cfg['ssid'])

    tcs.append(({'wlan_name_list':wlan_list}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
                2, 
                True)) 
    
    if white_list:
        tcs.append(({'white_list_name':wlan1.get('white_list')}, 
                    'CB_ZD_CLI_Delete_White_List', 
                    '%sDelete white list 1' % tc_name, 
                    2, 
                    True))
    
    if not wlan1.get('white_list') == wlan2.get('white_list'):
        tcs.append(({'white_list_name':wlan2.get('white_list')}, 
                    'CB_ZD_CLI_Delete_White_List', 
                    '%sDelete white list 2' % tc_name, 
                    2,
                    True))        

    return tcs

def build_stcs_main_hotspot(test_case, win2k3_mac):
    tcs = []

    tc_name = test_case['tc_name']
    wlan1 = test_case['wlan1']
    wlan1_cfg = wlan1['wlan_cfg']
    AP1 = test_case['AP1']
    AP1_radio = test_case['AP1_radio']
    AP2 = test_case['AP2']
    AP2_radio = test_case['AP2_radio']
    ping_result = test_case['ping_result']


    white_list = wlan1.get('white_list')

    hotspot_new_cfg = deepcopy(hotspot_cfg)
    hotspot_new_cfg.update({'white_list' : white_list,
                        'isolation_per_ap' : wlan1.get('isolation_per_ap'),
                        'isolation_across_ap' : wlan1.get('isolation_across_ap'),
                              })
    
    wlan1_default_cfg = deepcopy(wlan1_cfg)
    wlan1_default_cfg.update({'tunnel_mode': wlan1.get('tunnel_mode'),
                        'vlan_id': wlan1.get('vlan_id'),
                        'type': 'hotspot',
                        'hotspot_profile' : hotspot_new_cfg['name'],
                              })
    
    if wlan1.get('white_list'):  
        rule_type = wlan1.get('rule_type')
        if wlan1.get('gateway_ip'):
            wlan1_gateway_ip = wlan1.get('gateway_ip')
        else:
            wlan1_gateway_ip = default_ip['switch']
        tcs.append(({'white_list_name':white_list,
                      'rule_no':'1',
                      'rule_type': rule_type,
                      'value_type':'switch',
                      'ip_tag': wlan1_gateway_ip
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list for gateway from CLI' % tc_name,
                    1,
                    False))

        tcs.append(({'white_list_name':white_list,
                      'rule_no':'2',
                      'rule_type': rule_type,
                      'value_type':'zd',
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list for zd from CLI' % tc_name,
                    2,
                    False))

        if rule_type == 'MAC':
            rule_server_conf = {'3':{'mac':win2k3_mac}}
        else:
            rule_server_conf = {'3':{'mac':win2k3_mac,'ip':default_ip['win2k3']}}

        tcs.append(({'white_list_name':white_list,
                     'rule_conf': rule_server_conf,
                      },
                    'CB_ZD_CLI_Edit_White_List',
                    '%sCreate White list for win2k3 from CLI' % tc_name,
                    2,
                    False))

        tcs.append(({'white_list_name':white_list,
                      'rule_no':'4',
                      'rule_type': rule_type,
                      'value_type':'server',
                      'ip_tag': default_ip['server']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule for server from CLI' % tc_name,
                    2,
                    False)) 
    
    tcs.append(({'hotspot_conf':hotspot_new_cfg}, 
                   'CB_ZD_CLI_Configure_Hotspot', 
                   '%sConfigure Hotspot from CLI' % tc_name, 
                   1, 
                   False))    

    tcs.append(({'wlan_conf':wlan1_default_cfg},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN 1 from CLI' % tc_name,
                2,
                False))
    
    tcs.append(({},
                'CB_ZDCLI_Get_Wlan_By_SSID',
                '%sGet ZD WLAN 1 Info via CLI' % tc_name,
                2,
                False))

    tcs.append(({},
                'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                '%sVerify Wlan 1 Info Between CLI Set and CLI Get' % tc_name,
                2,
                False))
        
    tcs.append(({'wlan_cfg':wlan1_default_cfg,
                 'ap_tag':AP1,
                 'ap_radio': AP1_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 1' % tc_name,
                2,
                False
                ))
    
    if not AP1 == AP2:
        tcs.append(({'wlan_cfg':wlan1_default_cfg,
                     'ap_tag':AP2,
                     'ap_radio': AP2_radio},
                    'CB_AP_CLI_Get_BSSID',
                    '%sGet BSSID for AP 2' % tc_name,
                    2,
                    False
                    ))
         
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan1_default_cfg,
                 'wlan_ssid': wlan1_default_cfg['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 1 to wlan' % tc_name, 
                  2, 
                  False))    
    
    tcs.append(({'sta_tag': 'sta_2', 
                 'wlan_cfg': wlan1_default_cfg,
                 'wlan_ssid': wlan1_default_cfg['ssid'],
                 'ap_tag': AP2}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan' % tc_name, 
                  2, 
                  False))

    if white_list:
        tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server'],
                 'clean_arp_before_ping': True,}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied before authentication' % tc_name, 
                  2, 
                  False))

    username = local_user_cfg['username']
    password = local_user_cfg['password']
    expected_data = "It works!"
    tcs.append(({'sta_tag': "sta_1",
            'username': username,
            'password': password,
            'expected_data':expected_data,
            'start_browser_before_auth': True,
            'close_browser_after_auth': True,
             }, 
             'CB_Station_CaptivePortal_Perform_HotspotAuth', 
              '%sStation 1 do hotspot authentication' % tc_name, 
              2, 
              False))

    tcs.append(({'sta_tag': "sta_2",
            'username': username,
            'password': password,
            'expected_data':expected_data,
            'start_browser_before_auth': True,
            'close_browser_after_auth': True,
            'negative_test': True,
             }, 
             'CB_Station_CaptivePortal_Perform_HotspotAuth', 
              '%sStation 2 do hotspot authentication' % tc_name, 
              2, 
              False))

    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 1 Ping Gateway is Allowed' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'sta_tag': 'sta_2',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 2 Ping Gateway is Allowed' % tc_name, 
                  2, 
                  False)) 

    if ping_result:
        condition = 'allowed'
    else:
        condition = 'disallowed'
        
    tcs.append(({'src_sta_tag': 'sta_1',
                 'dst_sta_tag': 'sta_2',
                 'condition': condition,
                 'clean_arp_before_ping': True},
                 'CB_ZD_Client_Ping_Another', 
                  '%sStation Ping Another Station is %s' % (tc_name,condition), 
                  2,
                  False)) 

    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 1 Ping Linux Server is Allowed' % tc_name, 
                  2, 
                  False))

    tcs.append(({'sta_tag': 'sta_2',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation 2 Ping Linux Server is Allowed' % tc_name, 
                  2, 
                  False))

    wlan_list = []
    wlan_list.append(wlan1_default_cfg['ssid'])

    tcs.append(({'wlan_name_list':wlan_list}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
                2, 
                True)) 

    tcs.append(({'hotspot_conf':hotspot_new_cfg,
                 'cleanup': True}, 
                   'CB_ZD_CLI_Configure_Hotspot', 
                   '%sDelete Hotspot from CLI' % tc_name, 
                   2, 
                   True))
    
    if white_list:
        tcs.append(({'white_list_name':wlan1.get('white_list')}, 
                    'CB_ZD_CLI_Delete_White_List', 
                    '%sDelete white list 1' % tc_name, 
                    2, 
                    True))      

    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation with Mesh"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
        
    ts_name = attrs['testsuite_name']
    sta1_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the first wireless station: ")
    sta2_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the second wireless station: ")
    
    if not sta1_ip_addr or not sta2_ip_addr:
        raise Exception("Get station fail, sta1: %s, sta2: %s" % (sta1_ip_addr,sta2_ip_addr))

    if sta1_ip_addr == sta2_ip_addr:
        raise Exception("Please select different station")
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    if len(active_ap_list) < 3:
        raise Exception("Need three active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    active_ap1_mac = ap_sym_dict[active_ap1]['mac']
    
    active_ap2 = active_ap_list[1]
    active_ap2_mac = ap_sym_dict[active_ap2]['mac']

    active_ap3 = active_ap_list[2]
    active_ap3_mac = ap_sym_dict[active_ap3]['mac']

    win2k3_mac = str(raw_input("Please input the mac address of win2k3 server[like 50:A7:33:10:B9:60]"))
    if not win2k3_mac:
        raise Exception("Get the mac address of win2k3 server fail")
        
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with Mesh", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, sta2_ip_addr, all_aps_mac_list, active_ap1, active_ap1_mac, active_ap2, active_ap2_mac, active_ap3, active_ap3_mac, win2k3_mac)

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
    