"""
eMesh(3 tcs)

    Enable mesh
    [Guest Access wlan, root and emesh]sta1 connect to RootAP, sta2 connect to eMeshAP
    [Guest Access wlan, root and emesh]sta1,sta2 can not ping gw
    [Guest Access wlan, root and emesh]sta1 can ping sta2
    [Guest Access wlan, root and emesh]bind MAC only entry to wlan
    [Guest Access wlan, root and emesh]sta1 can ping PC, sta2 can ping PC
    [Webauth wlan, mesh and emesh]sta1 connect to MeshAP, sta2 connect to eMeshAP
    [Webauth wlan, mesh and emesh]sta1,sta2 can not ping gw
    [Webauth wlan, mesh and emesh]sta1 can ping sta2
    [Webauth wlan, mesh and emesh]bind IP and MAC entry to wlan
    [Dvlan wlan, emesh and emesh]sta1 can ping PC, sta2 can ping PC
    [Dvlan wlan, emesh and emesh]sta1 connect to eMeshAP, sta2 connect to eMeshAP
    [Dvlan wlan, emesh and emesh]sta1,sta2 can not ping gw
    [Dvlan wlan, emesh and emesh]sta1 can ping sta2
    [Dvlan wlan, emesh and emesh]bind MAC only entry to wlan
    [Dvlan wlan, emesh and emesh]sta1 can ping PC, sta2 can ping PC

Tips: RootAP---------------MeshAP--------------2 eMeshAP

if enable DVLAN, we need tag switch port of eMeshAP to support vlan of station,like vlan 10.

But in our testbed, we use 1 switch, if we tag eMeshAP port, it just go through the emesh port to server.

So for now, we can use tunnel mode instead.
    
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
ras_user_cfg = {'username': 'finance.user', 'password': 'finance.user', 'vlan': '10'}
test_params = dict(server_cfg_list = [dict(server_name = 'radius_server', type = 'radius-auth', backup = False, 
                                        server_addr = '192.168.0.252', server_port = '1812', radius_secret = '1234567890')])

target_url = 'http://172.16.10.252/'
dest_ip = '172.16.10.252'
username = 'ras.local.user'
password = 'ras.local.user'
guest_policy = {'Auth/TOU/No Redirection': {'generate_guestpass_cfg': dict(type = "single",
                                                                           guest_fullname = "Guest-Auth",
                                                                           duration = "5",
                                                                           duration_unit = "Days",
                                                                           key = "",
                                                                           wlan = ci_wlan1_cfg['ssid'],
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

def build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2, active_ap3, active_ap4):
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

    tcs.append(({'active_ap': active_ap4,
                 'ap_tag':'AP_04'},                                       
                'CB_ZD_Create_Active_AP',
                'Create Mesh AP_04',
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
                       'emesh_ap': ['AP_03','AP_04'],
                       'test_option': 'form_emesh_mesh_acl'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Setting up Mesh AP AP_02, eMesh AP AP_03,AP_04', 
                   0, 
                   False))

    tcs.append((test_params, 
                'CB_ZD_CLI_Configure_AAA_Servers', 
                'Creates AAA Server via CLI', 
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
    
    test_list = _generate_test_cfg()

    for test_case in test_list:
        tcs.extend(build_stcs_main(test_case))
        
    tcs.append(({'name': local_user_cfg['username']}, 
                   'CB_ZD_CLI_Delete_User', 
                   'Delete local user for cleanup ENV', 
                   0, 
                   True))

    tcs.append(({'server_name_list': [test_params['server_cfg_list'][0]['server_name']]},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove AAA server',
                0,
                True))
        
    tcs.append(({'ap_list': ['AP_01', 'AP_02', 'AP_03', 'AP_04'],
                       'test_option': 'reconnect_as_root'}, 
                   'CB_ZD_Mesh_Provisioning', 
                   'Reconnect all active APs as Root', 
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

def _generate_test_cfg():
    test_cfg = []

    test_cfg.append(({'tc_name' : '[Guest Access wlan, root and emesh, MAC only]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_03',
                  'AP2_radio' : '802.11g/n',
                  'ping_result': False,
                  'type': 'guest',
                  }))

    test_cfg.append(({'tc_name' : '[Webauth wlan, mesh and emesh, IP and MAC]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'AP1' : 'AP_02',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_03',
                  'AP2_radio' : '802.11g/n',
                  'ping_result': False,
                  'type': 'Webauth'
                  }))

    test_cfg.append(({'tc_name' : '[DVLAN wlan, emesh and emesh, MAC only]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                              'tunnel_mode' : True,
                            },
                  'AP1' : 'AP_03',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_04',
                  'AP2_radio' : '802.11g/n',
                  'ping_result': False,
                  'type': 'DVLAN'
                  }))

    return test_cfg
    
def build_stcs_main(test_case):
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
    type = test_case.get('type')
    
    if type == 'guest':
        tcs.append(({'guest_access_conf': guest_access_conf}, 
                       'CB_ZD_CLI_Configure_Guest_Access', 
                       '%sSet guest access authentication server' % tc_name, 
                       1, 
                       False))
        
        guest_restrict_conf = {'order': '2',
         '2':{'destination_address': '192.168.0.0/16', 
              'type': 'Allow',
              'order':'1'}
        }
        tcs.append(({'guest_restrict_conf': guest_restrict_conf}, 
                       'CB_ZD_CLI_Configure_Guest_Restrict_Access', 
                       '%sConfigure restricted subnet access' % tc_name, 
                       2, 
                       False))     
    
    if white_list:  
        rule_type = wlan1.get('rule_type')
        new_ip = deepcopy(default_ip)
        if type == 'DVLAN':
            new_ip.update({'switch': '192.168.10.253',
                            'server': '192.168.10.252',
                            })

        tcs.append(({'white_list_name':white_list,
                      'rule_no':'1',
                      'rule_type': rule_type,
                      'value_type':'switch',
                      'ip_tag': new_ip['switch']
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

        tcs.append(({'white_list_name':white_list,
                      'rule_no':'3',
                      'rule_type': rule_type,
                      'value_type':'server',
                      'ip_tag': new_ip['server']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule of white list 1 for server from CLI' % tc_name,
                    2,
                    False))  
    
    wlan1_default_cfg = deepcopy(wlan1_cfg)
    
    if type == 'guest':
        wlan1_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                                  'isolation_across_ap': wlan1.get('isolation_across_ap'),
                                  'white_list' : wlan1.get('white_list'),
                                  'tunnel_mode': wlan1.get('tunnel_mode'),
                                  'vlan_id': wlan1.get('vlan_id'),
                                  'type': 'guest',
                                  })
    elif type == 'Webauth':
        wlan1_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                                  'isolation_across_ap': wlan1.get('isolation_across_ap'),
                                  'white_list' : wlan1.get('white_list'),
                                  'tunnel_mode': wlan1.get('tunnel_mode'),
                                  'vlan_id': wlan1.get('vlan_id'),
                                  'web_auth' : True,
                                  'auth_server' : 'local',
                                  })
    elif type == 'DVLAN':
        wlan1_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                                  'isolation_across_ap': wlan1.get('isolation_across_ap'),
                                  'white_list' : wlan1.get('white_list'),
                                  'tunnel_mode': wlan1.get('tunnel_mode'),
                                  'vlan_id': wlan1.get('vlan_id'),
                                    'auth': "dot1x-eap",
                                    'encryption': 'AES',
                                    'algorithm' : 'AES',
                                    'wpa_ver': 'WPA2',
                                    'sta_encryption' : "AES",
                                    'sta_auth' : 'EAP',
                                    'auth_server': test_params['server_cfg_list'][0]['server_name'],
                                    'username': ras_user_cfg['username'],
                                    'password': ras_user_cfg['password'],
                                    'key_string': '',
                                    'ras_addr' : test_params['server_cfg_list'][0]['server_addr'],
                                    'ras_port' : test_params['server_cfg_list'][0]['server_port'],
                                    'ras_secret' : test_params['server_cfg_list'][0]['radius_secret'], 
                                    'use_radius' : True,
                                    'dvlan': True,
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
            
    tcs.append(({'wlan_cfg':wlan1_default_cfg,
                 'ap_tag':AP1,
                 'ap_radio': AP1_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 1' % tc_name,
                2,
                False
                ))
    
    get_cfg = deepcopy(wlan1_default_cfg)
    if type == 'DVLAN':
        #The CLI parameters are different between association, so we need to convert it
        if get_cfg['auth'] == "dot1x-eap":
            get_cfg['auth'] = get_cfg['sta_auth']
            get_cfg['encryption'] = get_cfg['sta_encryption']
            if get_cfg.has_key('wpa_ver') and get_cfg['wpa_ver'] == 'WPA-Mixed':
                get_cfg['wpa_ver'] = 'WPA'
             
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': get_cfg,
                 'wlan_ssid': get_cfg['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 1 to wlan' % tc_name, 
                  2, 
                  False))   

    tcs.append(({'wlan_cfg':wlan1_default_cfg,
                 'ap_tag':AP2,
                 'ap_radio': AP2_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 2' % tc_name,
                2,
                False
                )) 
    
    tcs.append(({'sta_tag': 'sta_2', 
                 'wlan_cfg': get_cfg,
                 'wlan_ssid': get_cfg['ssid'],
                 'ap_tag': AP2}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan' % tc_name, 
                  2, 
                  False))
    
    if white_list and not type == 'DVLAN':
        tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation 1 Ping Linux Server is Denied before authentication' % tc_name, 
                  2, 
                  False))

    #Perform Auth
    if type == 'guest':
        tcs.append(( guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg'],
                    'CB_ZD_Generate_Guest_Pass',
                    '%sGenerate the guestpass 1 by the guest user' % tc_name,
                    2,
                    False))
        
        tcs.append(({'sta_tag': 'sta_1',
                       'no_auth': False, 
                       'use_tou': True,
                       'target_url': target_url,
                       'start_browser_before_auth': True,
                       'close_browser_after_auth': True
                       }, 
                    'CB_Station_CaptivePortal_Perform_GuestAuth', 
                    '%sStation 1 perform guest authentication' % tc_name, 
                    2, 
                    False))

        tcs.append(( guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg'],
                    'CB_ZD_Generate_Guest_Pass',
                    '%sGenerate the guestpass 2 by the guest user' % tc_name,
                    2,
                    False))
        
        tcs.append(({'sta_tag': 'sta_2',
                       'no_auth': False, 
                       'use_tou': True,
                       'target_url': target_url,
                       'start_browser_before_auth': True,
                       'close_browser_after_auth': True
                       }, 
                    'CB_Station_CaptivePortal_Perform_GuestAuth', 
                    '%sStation 2 perform guest authentication' % tc_name, 
                    2, 
                    False))
    elif type == 'Webauth':                
        tcs.append(({'sta_tag': 'sta_1',
                 'username':local_user_cfg['username'], 
                 'password':local_user_cfg['password']}, 
                 'CB_ZD_Station_Perform_Web_Auth', 
                  "%sStation 1 Do web auth" % tc_name, 
                  2, 
                  False))

        tcs.append(({'sta_tag': 'sta_2',
                 'username':local_user_cfg['username'], 
                 'password':local_user_cfg['password']}, 
                 'CB_ZD_Station_Perform_Web_Auth', 
                  "%sStation 2 Do web auth" % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Gateway is Allowed after auth' % tc_name, 
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
    
    if type == 'guest':
        guest_access_clear_conf = {'authentication_server': 'Local Database',                 
                          'terms_of_use': 'Disabled',
                          'redirection': 'To the URL that the user intends to visit',}
        
        tcs.append(({'guest_access_conf': guest_access_clear_conf},
                    'CB_ZD_CLI_Configure_Guest_Access',
                    '%sCleanup Guest Access' % tc_name,
                    2,
                    True))
    
        guest_restrict_conf = {'order': '1'}
        tcs.append(({'guest_restrict_conf': guest_restrict_conf,
                     'cleanup': True,}, 
                       'CB_ZD_CLI_Configure_Guest_Restrict_Access', 
                       '%sConfigure restricted subnet access to default' % tc_name, 
                       2, 
                       True))

    wlan_list = []
    wlan_list.append(wlan1_default_cfg['ssid'])

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

    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation with eMesh"
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
    
    ap_sym_dict = tbcfg['ap_sym_dict']
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    if len(active_ap_list) < 4:
        raise Exception("Need Four active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0] 
    active_ap2 = active_ap_list[1]
    active_ap3 = active_ap_list[2]
    active_ap4 = active_ap_list[3]
        
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with eMesh", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2, active_ap3, active_ap4)

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
    