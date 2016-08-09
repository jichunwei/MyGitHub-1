"""
Whitelist and entry(about 12 tcs)

    [before bind, add whitelist]add whitelist, blank whitelist add fail
    [before bind, modify whitelist]modify whitelist
    [before bind, delete whitelist]del whitelist
    [before bind, add entry]add entry, MAC only
    [before bind, add entry]create wlan,sta1 ping gw success
    [before bind, modify entry]modify entry
    [before bind, modify entry]create wlan,sta1 ping linux server success
    [before bind, delete entry]del entry
    [before bind, delete entry]create wlan,sta1 ping server fail
    [after bind, add whitelist]create wlan bind no whitelist fail
    [after bind, add whitelist]add whitelist, wlan re-bind whitelist
    [after bind, modify whitelist]modify whitelist
    [after bind, delete whitelist]del whitelist fail
    [after bind, add entry]add entry,IP and MAC
    [after bind, add entry]create wlan,sta1 ping server success
    [after bind, modify entry]modify entry
    [after bind, modify entry]create wlan,sta1 ping linux server success
    [after bind, delete entry]del entry
    [after bind, delete entry]create wlan,sta1 ping server fail
    
Created on 2013-7-23
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Entry-1",
            "ssid" : "Rqa-auto-RAT-CI-Entry-1",
            "auth" : "open",
            "encryption" : "none",
            'isolation_per_ap' : True,
            'isolation_across_ap' : True,
            'white_list' : 'White-Entry-1',
            }

default_ip = {'switch' : '192.168.0.253',
              'server' : '192.168.0.252',
              }

whitelist_conf = {'name':'White-Entry-1',
                  'description':'White-Entry-1'
                      }

whitelist2_conf = {'name':'White-Entry-2',
                  'description':'White-Entry-2'
                      }

rule_conf_mac_ip= {'1':{
                                        'mac':'ca:bb:11:22:33:44',
                                        'ip':'192.168.0.7',
                                        'description': 'rule1'
                                      },
                                '2':{
                                        'mac':'cc:bb:11:22:33:44',
                                        'ip':'192.168.0.6',
                                        'description': 'rule2'
                                    }
                   }

rule_conf_mac= {'1':{
                                        'mac':'ce:bb:11:22:33:44',
                                        'description': 'rule1'
                                      },
                                '2':{
                                        'mac':'c0:bb:11:22:33:44',
                                        'description': 'rule2'
                                    }
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

    test_cfg = {'tc_name' : 'before bind',
                  'wlan_cfg' : ci_wlan1_cfg,
                  'white_list' : whitelist_conf,
                  'rule_mac_ip' : rule_conf_mac_ip,
                  'rule_mac' : rule_conf_mac,}
    tcs.extend(build_stcs_before_bind(test_cfg))

    test_cfg = {'tc_name' : 'after bind',
                  'wlan_cfg' : ci_wlan1_cfg,
                  'white_list' : whitelist_conf,
                  'white_list2':whitelist2_conf,
                  'rule_mac_ip' : rule_conf_mac_ip,
                  'rule_mac' : rule_conf_mac,}    
    tcs.extend(build_stcs_after_bind(test_cfg))    
    

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

def build_stcs_before_bind(test_cfg):
    tcs = []
    white_list = test_cfg['white_list']['name']
    tc_name = '[%s,whitelist without rule]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                 'expect_failed':True,
                 'rule_conf': {},
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sCreate White list with no rule' % tc_name,
                1,
                False))
    #----------------------------
    tc_name = '[%s,add/modify/delete whitelist]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                 'rule_conf': test_cfg['rule_mac_ip'],
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sCreate White list with mac and ip rule' % tc_name,
                1,
                False))
    
    tcs.append(({'white_list_name':white_list,
                 'rule_conf': test_cfg['rule_mac'],
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sModify White list to mac only rule' % tc_name,
                2,
                False))

    tcs.append(({'white_list_name':white_list,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list' % tc_name,
                2,
                True))
    #----------------------------
    
    tc_name = '[%s,add entry]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                  'rule_no':'1',
                  'rule_type': 'MAC',
                  'value_type':'switch',
                  'ip_tag': default_ip['switch']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sCreate White list add gateway mac from CLI' % tc_name,
                1,
                False)) 
    
    test_add = {'des_ip':default_ip['switch'],
                'ping_result': True,}
    tcs.extend(build_stcs_associate(test_cfg,tc_name,test_add, 'MAC'))
    
    tcs.append(({'white_list_name':white_list,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list' % tc_name,
                2,
                True))    
    
    #---------------------------- 
    
    tc_name = '[%s,modify/delete entry]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                 'rule_conf': test_cfg['rule_mac_ip'],
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sCreate White list with mac and ip rule' % tc_name,
                1,
                False))  
    
    tcs.append(({'white_list_name':white_list,
                  'rule_no':'1',
                  'rule_type': 'MACandIP',
                  'value_type':'switch',
                  'ip_tag': default_ip['switch']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sModify gateway entry from CLI' % tc_name,
                2,
                False))

    tcs.append(({'white_list_name':white_list,
                  'rule_no':'2',
                  'rule_type': 'MACandIP',
                  'value_type':'server',
                  'ip_tag': default_ip['server']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sModify server entry CLI' % tc_name,
                2,
                False))
    
    test_add = {'des_ip':default_ip['server'],
                'ping_result': True,}
    tcs.extend(build_stcs_associate(test_cfg,tc_name,test_add, 'MACandIP'))
    
    tc_name = '[%s,modify/delete entry]delete:' % test_cfg['tc_name']
    rule_conf = {}
    rule_conf['2'] = {}      
    tcs.append(({'white_list_name':white_list,
                  'rule_conf':rule_conf,
                  },
                'CB_ZD_CLI_Delete_Rules_White_List',
                '%sDelete server rule from  White list from CLI' % tc_name,
                2,
                False))

    test_add = {'des_ip':default_ip['server'],
                'ping_result': False,}
    tcs.extend(build_stcs_associate(test_cfg,tc_name,test_add, 'MACandIP'))
    
    tc_name = '[%s,modify/delete entry]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list' % tc_name,
                2,
                True))
    
    return tcs 

def build_stcs_after_bind(test_cfg):
    tcs = []
    white_list = test_cfg['white_list']['name']
    white_list2 = test_cfg['white_list2']['name']
    
    tc_name = '[%s, add/modify/delete whitelist]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                 'rule_conf': test_cfg['rule_mac'],
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sCreate White list 1' % tc_name,
                1,
                False))
    
    wlan_cfg_white = deepcopy(test_cfg['wlan_cfg'])
    wlan_cfg_white.update({'white_list': white_list})
    tcs.append(({'wlan_conf':wlan_cfg_white},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN bind white list from CLI' % tc_name,
                2,
                False))

    tcs.append(({'white_list_name':white_list2,
                 'rule_conf': test_cfg['rule_mac_ip'],
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sCreate White list 2' % tc_name,
                2,
                False))

    wlan_cfg_white = deepcopy(test_cfg['wlan_cfg'])
    wlan_cfg_white.update({'white_list': white_list2})
    tcs.append(({'wlan_conf':wlan_cfg_white},
                'CB_ZD_CLI_Create_Wlan',
                '%sModify white list of WLAN from CLI' % tc_name,
                2,
                False))
    
    
    check_dict = {"no whitelist '%s'"%(white_list2):"cannot be deleted"}
    tcs.append(({'white_list_name':white_list2,
                 'expect_failed':True,
                 'check_dict':check_dict,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list when bind to WLAN' % tc_name,
                2,
                False))
    
    tcs.append(({'wlan_name_list':[test_cfg['wlan_cfg']['ssid']]}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean WLANs for cleanup ENV' % tc_name, 
                2,
                True)) 
    
    tcs.append(({'white_list_name':white_list,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list 1' % tc_name,
                2,
                True))

    tcs.append(({'white_list_name':white_list2,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list 2' % tc_name,
                2,
                True))     
    #----------------------------
    tc_name = '[%s,add/modify/delete entry]' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                 'rule_conf': test_cfg['rule_mac_ip'],
                  },
                'CB_ZD_CLI_Edit_White_List',
                '%sCreate White list with mac and ip rule' % tc_name,
                1,
                False))

    tcs.append(({'wlan_conf':test_cfg['wlan_cfg']},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN bind white list from CLI' % tc_name,
                2,
                False))
    
    tc_name = '[%s,add/modify/delete entry]modify:' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                  'rule_no':'2',
                  'rule_type': 'MACandIP',
                  'value_type':'switch',
                  'ip_tag': default_ip['switch']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%smodify gateway mac and ip from CLI' % tc_name,
                2,
                False))

    test_add = {'des_ip':default_ip['switch'],
                'ping_result': True,}
    tcs.extend(build_stcs_associate_with_wlan(test_cfg,tc_name,test_add, 'MACandIP'))
        
    tc_name = '[%s,add/modify/delete entry]add:' % test_cfg['tc_name']
    tcs.append(({'white_list_name':white_list,
                  'rule_no':'3',
                  'rule_type': 'MACandIP',
                  'value_type':'server',
                  'ip_tag': default_ip['server']
                  },
                'CB_ZD_CLI_Edit_White_List_Special',
                '%sadd server entry from CLI' % tc_name,
                2,
                False))
    
    test_add = {'des_ip':default_ip['server'],
                'ping_result': True,}
    tcs.extend(build_stcs_associate_with_wlan(test_cfg,tc_name,test_add, 'MACandIP'))    
    
    tc_name = '[%s,add/modify/delete entry]delete:' % test_cfg['tc_name']
    rule_conf = {}
    rule_conf['3'] = {}
    tcs.append(({'white_list_name':white_list,
                  'rule_conf':rule_conf,
                  },
                'CB_ZD_CLI_Delete_Rules_White_List',
                '%sDelete server rule from  White list from CLI' % tc_name,
                2,
                False))

    test_add = {'des_ip':default_ip['server'],
                'ping_result': False,}
    tcs.extend(build_stcs_associate_with_wlan(test_cfg,tc_name,test_add, 'MACandIP'))

    tcs.append(({'wlan_name_list':[test_cfg['wlan_cfg']['ssid']]}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
                2,
                True))
        
    tcs.append(({'white_list_name':white_list,
                  },
                'CB_ZD_CLI_Delete_White_List',
                '%sDelete White list' % tc_name,
                2,
                True))
    
    return tcs 

def build_stcs_associate(test_cfg,tc_name,test_add, rule_type):
    tcs = []

    if test_add['des_ip'] != default_ip['server'] or test_add['ping_result'] != True:
        tcs.append(({'white_list_name':test_cfg['white_list']['name'],
                     'rule_no':'2',
                     'rule_type': rule_type,
                     'value_type':'server',
                     'ip_tag': default_ip['server']
                    },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule for dhcp server from CLI for White list' % tc_name,
                    2,
                    False))
    
    tcs.append(({'wlan_conf':test_cfg['wlan_cfg']},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN 1 from CLI' % tc_name,
                2,
                False))

    tcs.append(({'ap_tag': 'AP_01', 
                 'wlan_cfg': test_cfg['wlan_cfg'],
                 'whitelist_name': test_cfg['wlan_cfg']['white_list']}, 
                 'CB_AP_CLI_Verify_Client_Isolation_With_ZD', 
                  '%sVerify Client Isolation from AP CLI with ZD' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': test_cfg['wlan_cfg'],
                 'wlan_ssid': test_cfg['wlan_cfg']['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))
    
    if test_add['des_ip'] != default_ip['server'] or test_add['ping_result'] != True:
        rule_conf = {}
        rule_conf['2'] = {}      
        tcs.append(({'white_list_name':test_cfg['white_list']['name'],
                      'rule_conf':rule_conf,
                      },
                    'CB_ZD_CLI_Delete_Rules_White_List',
                    '%sDelete dhcp server rule from  White list from CLI' % tc_name,
                    2,
                    False))

    if test_add['ping_result']:
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': test_add['des_ip']}, 
                     'CB_Station_Ping_Dest_Is_Allowed', 
                      '%sPing Dest is Allowed' % tc_name, 
                      2, 
                      False))   
    else:
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': test_add['des_ip']}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation Ping Dest is Denied' % tc_name, 
                      2,
                      False)) 
        
    tcs.append(({'wlan_name_list':[test_cfg['wlan_cfg']['ssid']]}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
                2,
                True))
    
    return tcs

def build_stcs_associate_with_wlan(test_cfg,tc_name,test_add, rule_type):
    tcs = []
    
    if test_add['des_ip'] != default_ip['server'] or test_add['ping_result'] != True:
        tcs.append(({'white_list_name':test_cfg['white_list']['name'],
                     'rule_no':'3',
                     'rule_type': rule_type,
                     'value_type':'server',
                     'ip_tag': default_ip['server']
                    },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule for dhcp server from CLI for White list' % tc_name,
                    2,
                    False))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': test_cfg['wlan_cfg'],
                 'wlan_ssid': test_cfg['wlan_cfg']['ssid']}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))
    
    if test_add['des_ip'] != default_ip['server'] or test_add['ping_result'] != True:
        rule_conf = {}
        rule_conf['3'] = {}      
        tcs.append(({'white_list_name':test_cfg['white_list']['name'],
                      'rule_conf':rule_conf,
                      },
                    'CB_ZD_CLI_Delete_Rules_White_List',
                    '%sDelete dhcp server rule from  White list from CLI' % tc_name,
                    2,
                    False))

    if test_add['ping_result']:
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': test_add['des_ip']}, 
                     'CB_Station_Ping_Dest_Is_Allowed', 
                      '%sPing Dest is Allowed' % tc_name, 
                      2, 
                      False))   
    else:
        tcs.append(({'sta_tag': 'sta_1',
                     'des_sta_tag': 'sta_2'}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation Ping Dest is Denied' % tc_name, 
                      2,
                      False)) 
    
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation Whitelist Entry"
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
                                 "Client Isolation Whitelist Entry", 
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
    