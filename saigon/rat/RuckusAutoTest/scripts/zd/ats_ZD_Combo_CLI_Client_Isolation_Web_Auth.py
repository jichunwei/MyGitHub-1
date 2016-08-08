"""
Webauth wlan(7 tcs)

    webauth wlan client isolation disable
    webauth wlan client isolation enable
    enable whitelist
    bind whitelist to webauth wlan(MAC only)
    bind whitelist to webauth wlan(IP and MAC entry)
    enable whitelist, sta query domain webpage
    different subnet
    
Created on 2013-7-29
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-WebAuth-1",
            "ssid" : "Rqa-auto-RAT-CI-WebAuth-1",
            'web_auth' : True, 
            'auth_server' : 'local',
            "auth" : "open",
            "encryption" : "none",
            }

default_ip = {'switch' : '192.168.0.253',
              'server' : '192.168.0.252',
              }

whitelist_conf = {'name':'White-Basic-1',
                  'description':'White-Basic-1'
                      }

local_user_cfg = {'username': 'local_user', 'password': 'local_user','role':'Default'}

def build_tcs(sta1_ip_addr, active_ap1):
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
        tcs.extend(build_stcs_main(test_case))

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

    return test_cfg

def build_stcs_main(test_case):
    tcs = []

    tc_name = test_case['tc_name']
    white_list = test_case.get('white_list')

    default_wlan = deepcopy(ci_wlan1_cfg)
    default_wlan.update({'white_list' : white_list,
                        'tunnel_mode': test_case.get('tunnel_mode'),
                        'vlan_id': test_case.get('vlan_id'),
                        'isolation_per_ap' : test_case.get('isolation_per_ap'),
                        'isolation_across_ap' : test_case.get('isolation_across_ap'),
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
        
        tcs.append(({'white_list_name':white_list,
                      'rule_no':'3',
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
        rule_conf['3'] = {}      
        tcs.append(({'white_list_name':white_list,
                      'rule_conf':rule_conf,
                      },
                    'CB_ZD_CLI_Delete_Rules_White_List',
                    '%sDelete dhcp server rule from  White list from CLI' % tc_name,
                    2,
                    False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'clean_arp_before_ping': True,
                 'dest_ip': default_ip['server']}, 
                'CB_Station_Ping_Dest_Is_Denied', 
                '%sStation Ping Linux Server is Denied before authentication' % tc_name, 
                2, 
                False))

    if white_list and not test_case.get('vlan_id'):
        tcs.append(({'white_list_name':white_list,
                      'rule_no':'3',
                      'rule_type': rule_type,
                      'value_type':'server',
                      'ip_tag': default_ip['server']
                      },
                    'CB_ZD_CLI_Edit_White_List_Special',
                    '%sAdd rule for server from CLI' % tc_name,
                    2,
                    False))
            
    tcs.append(({'sta_tag': 'sta_1',
                 'username':local_user_cfg['username'], 
                 'password':local_user_cfg['password']}, 
                 'CB_ZD_Station_Perform_Web_Auth', 
                  "%sDo web auth" % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'clean_arp_before_ping': True,
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed' % tc_name, 
                  2, 
                  False))

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
    attrs = dict(testsuite_name = "Client Isolation with Web Auth"
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
    if len(active_ap_list) < 2:
        raise Exception("Need two active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with Web Auth", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, active_ap1)

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
    