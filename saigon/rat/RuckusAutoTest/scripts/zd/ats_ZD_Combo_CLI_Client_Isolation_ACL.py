"""
Access control(4 tcs)

    enable whitelist, L2 ACL set deny entry
    enable whitelist, L2 ACL set allow entry
    enable whitelist,L3/4 acl set deny all by default and set allow entry
    enable whitelist,L3/4 acl set allow all by default and set deny entry
    
Created on 2013-7-29
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-ACL-1",
            "ssid" : "Rqa-auto-RAT-CI-ACL-1",
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

l2_acl_cfg = {'acl_name':'l2_acl_for_client_isolation',
              'policy':'allow',
            'mac_entries':[],} 

rules = [{'rule_order': '3',
          'rule_type' : 'deny',
          'rule_destination_addr': '192.168.0.0/16',
          'rule_destination_port': 'Any',
          'rule_protocol': 1,
          }]
                             
l3_acl_cfg = {'acl_name':'l3_acl_for_client_isolation',
              'rule_conf_list':rules,
              'policy': 'allow',}

dvcpcy_for_windows_os = {'name': 'Policy for Window OS', 'mode': 'deny', 
                         'rules': [{'name': '1', 'os_type': 'Windows', 'type': 'allow',  
                                    'uplink': '10', 'downlink': '9'}]}

def build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2):
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

    tcs.append(({}, 
                'CB_ZD_Remove_All_L2_ACLs', 
                'Remove all L2 ACLs', 
                0, 
                False))
    
    tcs.append(({}, 
                'CB_ZD_Remove_All_L3_ACLs', 
                'Remove all L3 ACLs', 
                0, 
                False))

    tcs.append(({}, 
                'CB_ZD_CLI_Delete_Device_Policy', 
                'Remove all device policy', 
                0, 
                False))
  
    tcs.append(({'active_ap': active_ap1,
                 'ap_tag':'AP_01'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP 1',
                0,
                False))

    tcs.append(({'active_ap': active_ap2,
                 'ap_tag':'AP_02'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP 2',
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
    
    test_list = _generate_test_cfg()

    for test_case in test_list:
        tcs.extend(build_stcs_main(test_case))

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
                'CB_ZD_Remove_All_L2_ACLs', 
                'Remove all L2 ACLs for cleanup ENV', 
                0, 
                True))
    
    tcs.append(({}, 
                'CB_ZD_Remove_All_L3_ACLs', 
                'Remove all L3 ACLs for cleanup ENV', 
                0, 
                True))  

    tcs.append(({}, 
                'CB_ZD_CLI_Delete_Device_Policy', 
                'Remove all device policy for cleanup ENV', 
                0, 
                True)) 
            
    return tcs

def _generate_test_cfg():
    test_cfg = []

    test_cfg.append(({'tc_name' : '[Per AP, L2 ACL, deny]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False,
                  'l2_acl_cfg' : {'policy':'deny',
                                  'mac_entries':[],},
                  'ping_switch' : True,
                  }))

    test_cfg.append(({'tc_name' : '[Per AP, L2 ACL, allow]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True,
                  'l2_acl_cfg' : {'policy':'allow',
                                  'mac_entries':[],},
                  'ping_switch' : True,
                  }))

    test_cfg.append(({'tc_name' : '[With whitelist,L2 ACL, allow]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False,
                  'l2_acl_cfg' : {'policy':'allow',
                                  'mac_entries':[],},
                  'ping_switch' : True,
                  }))


    test_cfg.append(({'tc_name' : '[Per AP, L3 ACL, allow all, allow]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True,
                  'l3_acl_cfg' : {'policy':'allow',
                                  'rule_type': 'allow',},
                  'ping_switch' : True,
                  }))

    test_cfg.append(({'tc_name' : '[Per AP, L3 ACL, allow all, deny]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False,
                  'l3_acl_cfg' : {'policy':'allow',
                                  'rule_type': 'deny',},
                  'ping_switch' : False,
                  }))

    test_cfg.append(({'tc_name' : '[With whitelist, L3 ACL, allow]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False,
                  'l3_acl_cfg' : {'policy':'allow',
                                  'rule_type': 'allow',},
                  'ping_switch' : True,
                  }))

    test_cfg.append(({'tc_name' : '[With device policy, allow one]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False,
                  'dvcpcy_cfg' : {'mode':'deny',
                                  'type': 'allow',},
                  'ping_switch' : True,
                  }))

    test_cfg.append(({'tc_name' : '[With device policy, deny one]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False,
                  'dvcpcy_cfg' : {'mode':'allow',
                                  'type': 'deny',},
                  'ping_switch' : False,
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
    
    if wlan1.get('white_list'):    
        tcs.append(({'white_list_name':wlan1.get('white_list'),
                      'rule_no':'1',
                      'rule_type': wlan1.get('rule_type'),
                      'value_type':'switch',
                      'ip_tag': default_ip['switch']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list for gateway from CLI' % tc_name,
                    1,
                    False))

        tcs.append(({'white_list_name':wlan1.get('white_list'),
                      'rule_no':'2',
                      'rule_type': wlan1.get('rule_type'),
                      'value_type':'server',
                      'ip_tag': default_ip['server'],
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list for dhcp from CLI' % tc_name,
                    2,
                    False))
        
    wlan1_default_cfg = deepcopy(wlan1_cfg)
    wlan1_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                              'isolation_across_ap': wlan1.get('isolation_across_ap'),
                              'white_list' : wlan1.get('white_list'),
                              'tunnel_mode': wlan1.get('tunnel_mode'),
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
         
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan1_default_cfg,
                 'wlan_ssid': wlan1_default_cfg['ssid'],
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
                 'wlan_cfg': wlan1_default_cfg,
                 'wlan_ssid': wlan1_default_cfg['ssid'],
                 'ap_tag': AP2}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan' % tc_name, 
                  2, 
                  False))
    
    #config ACL
    if test_case.get('l2_acl_cfg'):
        l2_acl = deepcopy(l2_acl_cfg)
        l2_acl.update({'policy':test_case['l2_acl_cfg']['policy'],
                      'mac_entries':test_case['l2_acl_cfg']['mac_entries'],})
       
        tcs.append(({'l2acl_conf_list':[l2_acl],
                     'sta_tag' : 'sta_2'}, 
                     'CB_ZD_CLI_Create_L2_ACLs', 
                      '%sCreate L2 ACL of Station 2' % tc_name, 
                      2, 
                      False))
        
        if test_case['l2_acl_cfg']['policy'] == 'allow':
            tcs.append(({'l2acl_conf_list':[l2_acl],
                         'sta_tag' : 'sta_1'}, 
                         'CB_ZD_CLI_Create_L2_ACLs', 
                          '%sCreate L2 ACL of Station 1' % tc_name, 
                          2, 
                          False))            
        
        wlan1_new_cfg = deepcopy(wlan1_default_cfg)
        wlan1_new_cfg.update({'l2acl': l2_acl_cfg['acl_name'],})
            
    elif test_case.get('l3_acl_cfg'): 
        l3_acl = deepcopy(l3_acl_cfg)
        l3_acl['policy'] = test_case['l3_acl_cfg']['policy']        
        l3_acl['rule_conf_list'][0]['rule_type'] = test_case['l3_acl_cfg']['rule_type']
       
        tcs.append(({'l3acl_conf_list':[l3_acl]}, 
                     'CB_ZD_CLI_Create_L3_ACLs', 
                      '%sCreate L3 ACL' % tc_name, 
                      2, 
                      False))
        wlan1_new_cfg = deepcopy(wlan1_default_cfg)
        wlan1_new_cfg.update({'l3acl': l3_acl_cfg['acl_name'],})

    elif test_case.get('dvcpcy_cfg'): 
        dvcpcy_cfg = deepcopy(dvcpcy_for_windows_os)
        dvcpcy_cfg['mode'] = test_case['dvcpcy_cfg']['mode']        
        dvcpcy_cfg['rules'][0]['type'] = test_case['dvcpcy_cfg']['type']
           
        tcs.append(({'device_policy_list':[dvcpcy_cfg]}, 
                     'CB_ZD_CLI_Configure_Device_Policy', 
                      '%sCreate device policy for Windows OS' % tc_name, 
                      2, 
                      False))
        wlan1_new_cfg = deepcopy(wlan1_default_cfg)
        wlan1_new_cfg.update({'dvcpcy_name': dvcpcy_for_windows_os['name'],})
    
    tcs.append(({'wlan_conf':wlan1_new_cfg},
                'CB_ZD_CLI_Create_Wlan',
                '%sChange WLAN bind ACL from CLI' % tc_name,
                2,
                False))
    
    if wlan1.get('white_list'):
        rule_conf = {}
        rule_conf['2'] = {}      
        tcs.append(({'white_list_name':wlan1.get('white_list'),
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
    
    if test_case.get('ping_switch'):
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': default_ip['switch']}, 
                     'CB_Station_Ping_Dest_Is_Allowed', 
                      '%sStation Ping Gateway is Allowed after configure ACL' % tc_name, 
                      2, 
                      False))    
    else:
        tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch'],
                 'clean_arp_before_ping': True,}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Gateway is Denied after configure ACL' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
                2, 
                True)) 
    
    tcs.append(({'white_list_name':wlan1.get('white_list')}, 
                'CB_ZD_CLI_Delete_White_List', 
                '%sDelete white list 1' % tc_name, 
                2, 
                True))
    
    if test_case.get('l2_acl_cfg'):
        tcs.append(({}, 
                    'CB_ZD_Remove_All_L2_ACLs', 
                    '%sRemove all L2 ACLs' % tc_name, 
                    2, 
                    True))
        
    elif test_case.get('l3_acl_cfg'):
        tcs.append(({}, 
                    'CB_ZD_Remove_All_L3_ACLs', 
                    '%sRemove all L3 ACLs' % tc_name, 
                    2, 
                    True)) 
    
    elif test_case.get('dvcpcy_cfg'): 
        tcs.append(({}, 
                    'CB_ZD_CLI_Delete_Device_Policy', 
                    '%sRemove all device policy' % tc_name, 
                    2, 
                    True))     

    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation with ACL"
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
    if len(active_ap_list) < 2:
        raise Exception("Need two active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    active_ap2 = active_ap_list[1]
        
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with ACL", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2)

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
    