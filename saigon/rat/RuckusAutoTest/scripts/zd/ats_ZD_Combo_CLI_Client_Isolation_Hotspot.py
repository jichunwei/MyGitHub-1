"""
Hotspot(8 tcs)

    Client isolation enable and whitelist is none
    bind whitelist to hotspot wlan(MAC only)
    bind whitelist to hotspot wlan(IP and MAC entry)
    redirect unauthenticated user to login page
    redirect authenticated user to start page
    enable walled garden
    enable Restricted subnet access
    different subnet
    
Created on 2013-7-25
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Hotspot-1",
            "ssid" : "Rqa-auto-RAT-CI-Hotspot-1",
            'type': 'hotspot',
            'hotspot_profile' : '',
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

local_user_cfg = {'username': 'local_user', 'password': 'local_user','role':'Default'}
hotspot_cfg = {
    'name': 'hotspot-Client-Isolation',
    'login_page': 'http://192.168.0.250/login.html',
    'idle_timeout': None,
    'auth_svr': 'Local Database',
    }

def build_tcs(sta1_ip_addr, active_ap1, win2k3_mac):
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
  
    tcs.append(({'active_ap': active_ap1,
                 'ap_tag':'AP_01'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP 1',
                0,
                False))

    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': sta1_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 1', 
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
        tcs.extend(build_stcs_hotspot(test_case, win2k3_mac))

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
            
    return tcs


def _generate_test_cfg():
    test_cfg = []

    test_cfg.append(({'tc_name' : '[Client Isolation Disable]',
                      'white_list' : '',
                      'isolation_per_ap' : False,
                      }))
        
    test_cfg.append(({'tc_name' : '[Client Isolation Per AP]',
                      'white_list' : '',
                      'isolation_per_ap' : True,
                      }))
    
    test_cfg.append(({'tc_name' : '[MAC only]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MAC',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      }))

    test_cfg.append(({'tc_name' : '[MAC and IP]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MACandIP',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      }))
    
    test_cfg.append(({'tc_name' : '[Different subnet]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MACandIP',
                      'vlan_id' : 10,
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      'gateway_ip' : '192.168.10.253',
                      }))
    
    test_cfg.append(({'tc_name' : '[Unauthenticated user]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MAC',
                      'username' : 'un-user',
                      'password' :'un-user',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      }))
    
    test_cfg.append(({'tc_name' : '[Enable walled garden]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MACandIP',
                      'username' : 'un-user',
                      'password' :'un-user',
                      'enable_walled_garden': True,
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      })) 
    
    test_cfg.append(({'tc_name' : '[Enable restricted subnet]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MAC',
                      'enable_restricted_subnet' : True,
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      }))

    return test_cfg

def build_stcs_hotspot(test_case, win2k3_mac):
    tcs = []

    tc_name = test_case['tc_name']
    white_list = test_case.get('white_list')

    hotspot_new_cfg = deepcopy(hotspot_cfg)
    hotspot_new_cfg.update({'white_list' : white_list,
                        'isolation_per_ap' : test_case.get('isolation_per_ap'),
                        'isolation_across_ap' : test_case.get('isolation_across_ap'),
                              })
    
    default_wlan = deepcopy(ci_wlan1_cfg)
    default_wlan.update({'tunnel_mode': test_case.get('tunnel_mode'),
                        'vlan_id': test_case.get('vlan_id'),
                        'hotspot_profile' : hotspot_new_cfg['name'],
                              })
    
    if white_list:
        rule_type = test_case.get('rule_type')
        if test_case.get('gateway_ip'):
            gateway_ip = test_case.get('gateway_ip')
        else:
            gateway_ip = default_ip['switch']
        tcs.append(({'white_list_name':white_list,
                      'rule_no':'1',
                      'rule_type': rule_type,
                      'value_type':'switch',
                      'ip_tag': gateway_ip,
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
                      'ip_tag': default_ip['server'],
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list for dhcp from CLI' % tc_name,
                    2,
                    False))

    tcs.append(({'hotspot_conf':hotspot_new_cfg}, 
                   'CB_ZD_CLI_Configure_Hotspot', 
                   '%sConfigure Hotspot from CLI' % tc_name, 
                   1, 
                   False))
    
    tcs.append(({'wlan_conf':default_wlan},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN from CLI' % tc_name,
                2,
                False))

    tcs.append(({},
                'CB_ZDCLI_Get_Wlan_By_SSID',
                '%sGet ZD WLAN Info via CLI' % tc_name,
                2,
                False))

    tcs.append(({},
                'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                '%sVerify Wlan Info Between CLI Set and CLI Get' % tc_name,
                2,
                False))
    
    #Station associate
    tcs.append(({'sta_tag': 'sta_1', 
             'wlan_cfg': default_wlan,
             'wlan_ssid': default_wlan['ssid']}, 
             'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
              '%sAssociate the station' % tc_name, 
              2, 
              False))

    if white_list:
        rule_conf = {}
        rule_conf['4'] = {}      
        tcs.append(({'white_list_name':white_list,
                      'rule_conf':rule_conf,
                      },
                    'CB_ZD_CLI_Delete_Rules_White_List',
                    '%sDelete dhcp server rule from  White list from CLI' % tc_name,
                    2,
                    False))
        
        tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server'],
                 'clean_arp_before_ping': True,}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied before authentication' % tc_name, 
                  2, 
                  False))
    
    if test_case.get('username'):
        username = test_case.get('username')
        password = test_case.get('password')
        expected_data = "Wireless Internet Service"
        ping_result = False
        
        tcs.append(({'sta_tag': "sta_1",
                'username': username,
                'password': password,
                'expected_data':expected_data,
                'start_browser_before_auth': True,
                'close_browser_after_auth': True,
                'negative_test': True,
                 }, 
                 'CB_Station_CaptivePortal_Perform_HotspotAuth_With_Invalid_Account', 
                  '%sDo hotspot authentication' % tc_name, 
                  2, 
                  False))
        
    else:
        username = local_user_cfg['username']
        password = local_user_cfg['password']
        expected_data = "It works!"
        ping_result = True
        
        tcs.append(({'sta_tag': "sta_1",
                'username': username,
                'password': password,
                'expected_data':expected_data,
                'start_browser_before_auth': True,
                'close_browser_after_auth': True,
                 }, 
                 'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                  '%sDo hotspot authentication' % tc_name, 
                  2, 
                  False))
        
    if white_list and not test_case.get('vlan_id'):
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation Ping Linux Server is Denied after auth before add entry' % tc_name, 
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
    
    if ping_result:
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Allowed', 
                      '%sStation Ping Linux Server is Allowed' % tc_name, 
                      2, 
                      False))
    else:
        tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied' % tc_name, 
                  2, 
                  False))
    
    if test_case.get('enable_walled_garden'):
        h_cfg = deepcopy(hotspot_new_cfg)
        h_cfg.update({'walled_garden_list': [default_ip['server']]})
        tcs.append(({'hotspot_conf':h_cfg}, 
                   'CB_ZD_CLI_Configure_Hotspot', 
                   '%sConfigure Walled Garden' % tc_name, 
                   2, 
                   False))
        
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Allowed', 
                      '%sStation Ping Linux Server is Allowed after enable walled garden' % tc_name, 
                      2, 
                      False))    
    
    des_ip = str(default_ip['server']) + '/24'
    restrict_cfg = {'order': '1',
    'destination_address': des_ip,
    'type': 'Deny',
    }
    
    if test_case.get('enable_restricted_subnet'):
        tcs.append(({'hotspot_name': hotspot_new_cfg['name'],
                     'hotspot_restrict_access_conf':restrict_cfg,
                     'hotspot_cfg': hotspot_new_cfg}, 
                 'CB_ZD_CLI_Configure_Hotspot_Restrict_Access', 
                  '%sConfigure Restrict access' % tc_name, 
                  2, 
                  False))
              
        tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied after configure restrict access' % tc_name, 
                  2, 
                  False))

    tcs.append(({}, 
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
        tcs.append(({'white_list_name':white_list}, 
                    'CB_ZD_CLI_Delete_White_List', 
                    '%sDelete white list' % tc_name, 
                    2, 
                    True))  
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation with Hotspot"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
        
    ts_name = attrs['testsuite_name']
    sta1_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the first wireless station: ")
    
    if not sta1_ip_addr:
        raise Exception("Get station fail, sta1: %s" % (sta1_ip_addr))

    ap_sym_dict = tbcfg['ap_sym_dict']
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    if len(active_ap_list) < 1:
        raise Exception("Need one active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    
    win2k3_mac = str(raw_input("Please input the mac address of win2k3 server[like 50:A7:33:10:B9:60]"))
    if not win2k3_mac:
        raise Exception("Get the mac address of win2k3 server fail")
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with Hotspot", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, active_ap1, win2k3_mac)

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
    