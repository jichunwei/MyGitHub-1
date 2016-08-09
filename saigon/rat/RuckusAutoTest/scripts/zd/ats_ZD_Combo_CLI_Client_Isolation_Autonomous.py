"""
AutonomousWLAN(2 tcs)

    before ap disconnect to ZD, bind whitelist
    after ap disconnect to ZD, bind whitelist
    
Created on 2013-8-5
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

default_ip = {'switch' : '192.168.0.253',
              'server' : '192.168.0.252',
              }

whitelist_conf = {'name':'White-Basic-1',
                  'description':'White-Basic-1'
                      }

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Autonomous-1",
            "ssid" : "Rqa-auto-RAT-CI-Autonomous-1",
            "auth" : "open",
            "encryption" : "none",
            'type' : 'autonomous',
            }


def build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1):
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

    tcs.append(({'sta_tag': 'sta_2', 
                   'sta_ip_addr': sta2_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 2', 
                   0, 
                   False))
    
    tcs.append(({'recovery_enabled': False}, 
                'CB_ZD_Config_AP_Auto_Recovery', 
                'Config AP recovery option disabled', 
                0, 
                False))
    
    test_list = _generate_test_cfg()

    for test_case in test_list:
        tcs.extend(build_stcs_main(test_case))
    
    
    tcs.append(({'recovery_enabled': True}, 
                'CB_ZD_Config_AP_Auto_Recovery', 
                'Config AP recovery option enabled', 
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
        
    test_cfg.append(({'tc_name' : '[Before AP disconnect, Client Isolation Per AP]',
                      'white_list' : '',
                      'isolation_per_ap' : True,
                      'ping_result' : False,
                      'test_type' : 'before'
                      }))
    
    test_cfg.append(({'tc_name' : '[Before AP disconnect, MAC only]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MAC',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      'ping_result' : False,
                      'test_type' : 'before'
                      }))

    test_cfg.append(({'tc_name' : '[After AP disconnect, MAC and IP]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MACandIP',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      'ping_result' : True,
                      'test_type' : 'after'
                      }))

    return test_cfg

def build_stcs_main(test_case):
    tcs = []

    tc_name = test_case['tc_name']
    white_list = test_case.get('white_list')
    ping_result = test_case['ping_result']
    AP1 = 'AP_01'
    test_type = test_case['test_type']

    default_wlan = deepcopy(ci_wlan1_cfg)
    
    if test_type == 'before':
        default_wlan.update({'white_list' : white_list,
                            'isolation_per_ap' : test_case.get('isolation_per_ap'),
                            'isolation_across_ap' : test_case.get('isolation_across_ap'),
                                  })
        if white_list:
            rule_type = test_case.get('rule_type')
            tcs.append(({'white_list_name':white_list,
                          'rule_no':'1',
                          'rule_type': rule_type,
                          'value_type':'switch',
                          'ip_tag': default_ip['switch'],
                          },
                        'CB_ZD_CLI_Edit_White_List_Special',
                        '%sCreate White list for gateway from CLI' % tc_name,
                        1,
                        False))

            tcs.append(({'white_list_name':white_list,
                          'rule_no':'2',
                          'rule_type': rule_type,
                          'value_type':'server',
                          'ip_tag': default_ip['server'],
                          },
                        'CB_ZD_CLI_Edit_White_List_Special',
                        '%sCreate White list for dhcp from CLI' % tc_name,
                        2,
                        False))

        tcs.append(({'wlan_conf':default_wlan},
                    'CB_ZD_CLI_Create_Wlan',
                    '%sCreate WLAN from CLI' % tc_name,
                    1,
                    False))
        
    elif test_type == 'after':
        new_wlan = deepcopy(default_wlan)
        new_wlan.update({'white_list' : '',
                            'isolation_per_ap' : False,
                            'isolation_across_ap' : False,
                                  })        
        
        tcs.append(({'wlan_conf':new_wlan},
                    'CB_ZD_CLI_Create_Wlan',
                    '%sCreate WLAN from CLI' % tc_name,
                    1,
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

    tcs.append(({'wlan_cfg':default_wlan,
                 'ap_tag':AP1,
                 'ap_radio': '802.11g/n'},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 1' % tc_name,
                2,
                False
                ))

    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': default_wlan,
                 'wlan_ssid': default_wlan['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 1 to wlan' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'sta_tag': 'sta_2', 
                 'wlan_cfg': default_wlan,
                 'wlan_ssid': default_wlan['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan' % tc_name, 
                  2, 
                  False))
    
    if white_list and test_type == 'before':
        rule_conf = {}
        rule_conf['2'] = {}      
        tcs.append(({'white_list_name':white_list,
                      'rule_conf':rule_conf,
                      },
                    'CB_ZD_CLI_Delete_Rules_White_List',
                    '%sDelete dhcp server rule from  White list from CLI' % tc_name,
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
                 'clean_arp_before_ping': True,
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Gateway is Allowed after auth' % tc_name, 
                  2, 
                  False))
        
    if white_list and test_type == 'before':
        tcs.append(({'sta_tag': 'sta_1',
                     'clean_arp_before_ping': True,
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation Ping Linux Server is Denied after auth before add entry' % tc_name, 
                      2, 
                      False))

        tcs.append(({'white_list_name':white_list,
                      'rule_no':'2',
                      'rule_type': rule_type,
                      'value_type':'server',
                      'ip_tag': default_ip['server']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule for server from CLI' % tc_name,
                    2,
                    False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'clean_arp_before_ping': True,
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed after auth' % tc_name, 
                  2, 
                  False))    
    
    #------------------------
    tcs.append(({'operation': 'add',
                'parameter': None, 'ap_tag': AP1}, 
                 'CB_ZD_Config_Static_Route', 
                  '%sConfigure an invalid route to AP' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'ap_tag': AP1, 'expected_status':'disconnected'}, 
                 'CB_ZD_Wait_AP_Status', 
                  '%sWait active AP status changed to disconnected' % tc_name, 
                  2, 
                  False))
    
    if test_type == 'after':
        default_wlan.update({'white_list' : white_list,
                            'isolation_per_ap' : test_case.get('isolation_per_ap'),
                            'isolation_across_ap' : test_case.get('isolation_across_ap'),
                                  })
        if white_list:
            rule_type = test_case.get('rule_type')
            tcs.append(({'white_list_name':white_list,
                          'rule_no':'1',
                          'rule_type': rule_type,
                          'value_type':'switch',
                          'ip_tag': default_ip['switch'],
                          },
                        'CB_ZD_CLI_Edit_White_List_Special',
                        '%sCreate White list for gateway from CLI after AP disconnect' % tc_name,
                        2,
                        False))
    
        tcs.append(({'wlan_conf':default_wlan},
                    'CB_ZD_CLI_Create_Wlan',
                    '%sChange WLAN enable Client Isolation from CLI' % tc_name,
                    2,
                    False))
    
        tcs.append(({},
                    'CB_ZDCLI_Get_Wlan_By_SSID',
                    '%sGet ZD WLAN Info via CLI after enable Client Isolation' % tc_name,
                    2,
                    False))
    
        tcs.append(({},
                    'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                    '%sVerify Wlan Info Between CLI Set and CLI Get after enable Client Isolation' % tc_name,
                    2,
                    False))       
 
    tcs.append(({'sta_tag': 'sta_1',
                 'clean_arp_before_ping': True,
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed after AP disconnect' % tc_name, 
                  2, 
                  False))    
    
    tcs.append(({'src_sta_tag': 'sta_1',
                 'dst_sta_tag': 'sta_2',
                 'condition': condition,
                 'clean_arp_before_ping': True},
                 'CB_ZD_Client_Ping_Another', 
                  '%sStation Ping Another Station is %s after AP disconnect' % (tc_name,condition), 
                  2,
                  False))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': default_wlan,
                 'wlan_ssid': default_wlan['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 1 to wlan after AP disconnect' % tc_name, 
                  2, 
                  False)) 

    tcs.append(({'sta_tag': 'sta_2', 
                 'wlan_cfg': default_wlan,
                 'wlan_ssid': default_wlan['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan after AP disconnect' % tc_name, 
                  2, 
                  False))    

    tcs.append(({'sta_tag': 'sta_1',
                 'clean_arp_before_ping': True,
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed after associate again' % tc_name, 
                  2, 
                  False))    
    
    tcs.append(({'src_sta_tag': 'sta_1',
                 'dst_sta_tag': 'sta_2',
                 'condition': condition,
                 'clean_arp_before_ping': True},
                 'CB_ZD_Client_Ping_Another', 
                  '%sStation Ping Another Station is %s after associate again' % (tc_name,condition), 
                  2,
                  False))
       
    tcs.append(({'operation': 'delete all'}, 
                 'CB_ZD_Config_Static_Route', 
                  '%sDelete all static routes at last' % tc_name, 
                  2, 
                  True))

    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
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
    attrs = dict(testsuite_name = "Client Isolation with Autonomous"
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
    if len(active_ap_list) < 1:
        raise Exception("Need one active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with Autonomous", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1)

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
    