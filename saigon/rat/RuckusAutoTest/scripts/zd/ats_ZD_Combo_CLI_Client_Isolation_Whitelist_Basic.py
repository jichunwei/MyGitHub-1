"""
Whitelist basic(4 tcs)

    Create white list,add gateway entry
    Create wlan bind white list, verify sta1 ping gw pass
    [MAC only]Add MAC only entry, server
    [MAC only]upstream, check ip, sta1 can ping server
    [MAC only]downstream, check mac
    [MAC only]del entry, sta1 can not ping server
    [MAC only]Add MAC only entry, sta1
    [MAC only]upstream, check ip, sta1 can ping gw
    [MAC only]downstream, check mac
    [IP and MAC]Add IP and MAC entry, server
    [IP and MAC]upstream, check ip, sta1 can ping server
    [IP and MAC]downstream, check mac
    [IP and MAC]del entry, sta1 can not ping server
    [IP and MAC]Add IP and MAC entry, sta1
    [IP and MAC]upstream, check ip, sta1 can not ping gw
    [IP and MAC]downstream, check mac
    Create wlan with tunnel, repeat step 3 to 16
    
Created on 2013-7-22
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Whitelist-1",
            "ssid" : "Rqa-auto-RAT-CI-Whitelist-1",
            "auth" : "open",
            "encryption" : "none",
            }

ci_wlan2_cfg = {"name" : "Rqa-auto-RAT-CI-Whitelist-2",
            "ssid" : "Rqa-auto-RAT-CI-Whitelist-2",
            "auth" : "open",
            "encryption" : "none",
            }

default_ip = {'switch' : '192.168.0.253',
              'server' : '192.168.0.252',
              }

whitelist_conf = {'name':'White-Basic-1',
                  'description':'White-Basic-1'
                      }
whitelist2_conf = {'name':'White-Basic-2',
                  'description':'White-Basic-2'
                      }

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
            
    return tcs

def _generate_test_cfg():
    test_cfg = []
    
    test_cfg.append(({'tc_name' : '[MAC only]',
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
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  }))

    test_cfg.append(({'tc_name' : '[MAC and IP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11a/n',
                  }))

    test_cfg.append(({'tc_name' : '[MAC only, with tunnel]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MAC',
                              'tunnel_mode' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist2_conf['name'],
                              'rule_type' : 'MAC',
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  }))
    
    test_cfg.append(({'tc_name' : '[MAC and IP, with tunnel]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                              'tunnel_mode' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'isolation_across_ap' : True,
                              'white_list' : whitelist_conf['name'],
                              'rule_type' : 'MACandIP',
                              'tunnel_mode' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  }))

    return test_cfg
    
def build_stcs_main(test_case):
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
                 'ip_tag': default_ip['server']
                },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sAdd rule for dhcp server from CLI' % tc_name,
                2,
                False)) 
    
    if not wlan1.get('white_list') == wlan2.get('white_list'):
        tcs.append(({'white_list_name':wlan2.get('white_list'),
                      'rule_no':'1',
                      'rule_type': wlan2.get('rule_type'),
                      'value_type':'switch',
                      'ip_tag': default_ip['switch']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sCreate White list 2 for gateway from CLI' % tc_name,
                    2,
                    False))
        tcs.append(({'white_list_name':wlan2.get('white_list'),
                 'rule_no':'2',
                 'rule_type': wlan2.get('rule_type'),
                 'value_type':'server',
                 'ip_tag': default_ip['server']
                },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sAdd rule for dhcp server from CLI for White list 2' % tc_name,
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
        
    if not wlan2_cfg == wlan1_cfg:
        wlan2_default_cfg = deepcopy(wlan2_cfg)
        wlan2_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                              'isolation_across_ap': wlan1.get('isolation_across_ap'),
                              'white_list' : wlan2.get('white_list'),
                              'tunnel_mode': wlan2.get('tunnel_mode'),
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
                '%sGet BSSID for AP 1st' % tc_name,
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
                '%sGet BSSID for AP 2nd' % tc_name,
                2,
                False
                ))  
    
    tcs.append(({'sta_tag': 'sta_2', 
                 'wlan_cfg': wlan2_default_cfg,
                 'wlan_ssid': wlan2_default_cfg['ssid'],
                 'ap_tag': AP2}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan' % tc_name, 
                  2, 
                  False))
    
    rule_conf = {}
    rule_conf['2'] = {}      
    tcs.append(({'white_list_name':wlan1.get('white_list'),
                  'rule_conf':rule_conf,
                  },
                'CB_ZD_CLI_Delete_Rules_White_List',
                '%sDelete dhcp server rule from  White list from CLI' % tc_name,
                2,
                False))
    
    if not wlan1.get('white_list') == wlan2.get('white_list'):
        tcs.append(({'white_list_name':wlan2.get('white_list'),
                  'rule_conf':rule_conf,
                  },
                'CB_ZD_CLI_Delete_Rules_White_List',
                '%sDelete dhcp server rule from  White list from CLI for White list 2' % tc_name,
                2,
                False))

    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Gateway is Allowed' % tc_name, 
                  2, 
                  False))    

    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied' % tc_name, 
                  2, 
                  False))

    tcs.append(({'src_sta_tag': 'sta_1',
                 'dst_sta_tag': 'sta_2',
                 'condition': 'disallowed',
                 'clean_arp_before_ping': True},
                 'CB_ZD_Client_Ping_Another', 
                  '%sStation Ping Another Station is disallowed' % tc_name, 
                  2,
                  False))
    
    #add one entry
    tcs.append(({'white_list_name':wlan1.get('white_list'),
                  'rule_no':'2',
                  'rule_type': wlan1.get('rule_type'),
                  'value_type':'server',
                  'ip_tag': default_ip['server']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sAdd rule for server from CLI' % tc_name,
                2,
                False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed, after add server entry' % tc_name, 
                  2, 
                  False))
    
    #delete one entry
    rule_conf = {}
    rule_conf['2'] = {}      
    tcs.append(({'white_list_name':wlan1.get('white_list'),
                  'rule_conf':rule_conf,
                  },
                'CB_ZD_CLI_Delete_Rules_White_List',
                '%sDelete server rule from  White list from CLI' % tc_name,
                2,
                False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied after delete server entry' % tc_name, 
                  2, 
                  False))
    
    #add station entry
    tcs.append(({'white_list_name':wlan1.get('white_list'),
                  'rule_no':'2',
                  'rule_type': wlan1.get('rule_type'),
                  'value_type':'station',
                  'ip_tag': 'sta_1',
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sAdd rule for station from CLI' % tc_name,
                2,
                False))        
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch'],
                 'clean_arp_before_ping': True}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                 '%sStation Ping Gateway is Denied after add station entry' % tc_name, 
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

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation Whitelist Basic"
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
                                 "Client Isolation Whitelist Basic", 
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
    