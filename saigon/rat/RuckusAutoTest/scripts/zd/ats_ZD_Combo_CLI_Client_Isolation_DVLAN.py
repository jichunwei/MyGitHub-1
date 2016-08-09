"""
Dvlan(3 tcs)

    dvlan wlan and enable client isolation
    dvlan wlan bind ip entry only whitelist
    dvlan wlan bind mac and ip entry whitelist
    
Created on 2013-8-5
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

default_ip = {'switch' : '192.168.10.253',
              'server' : '192.168.10.252',
              }

whitelist_conf = {'name':'White-Basic-1',
                  'description':'White-Basic-1'
                      }

ras_user_cfg = {'username': 'finance.user', 'password': 'finance.user', 'vlan': '10'}
test_params = dict(server_cfg_list = [dict(server_name = 'radius_server', type = 'radius-auth', backup = False, 
                                        server_addr = '192.168.0.252', server_port = '1812', radius_secret = '1234567890')])

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-DVLAN-1",
            "ssid" : "Rqa-auto-RAT-CI-DVLAN-1",
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
        }


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
    
    tcs.append((test_params, 
                'CB_ZD_CLI_Configure_AAA_Servers', 
                'Creates AAA Server via CLI', 
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

    tcs.append(({'server_name_list': [test_params['server_cfg_list'][0]['server_name']]},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove AAA server',
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

    return test_cfg

def build_stcs_main(test_case):
    tcs = []

    tc_name = test_case['tc_name']
    white_list = test_case.get('white_list')

    default_wlan = deepcopy(ci_wlan1_cfg)
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

    #The CLI parameters are different between association, so we need to convert it
    get_cfg = deepcopy(default_wlan)
    if get_cfg['auth'] == "dot1x-eap":
        get_cfg['auth'] = get_cfg['sta_auth']
        get_cfg['encryption'] = get_cfg['sta_encryption']
        if get_cfg.has_key('wpa_ver') and get_cfg['wpa_ver'] == 'WPA-Mixed':
            get_cfg['wpa_ver'] = 'WPA2'
                
    #Station associate
    tcs.append(({'sta_tag': 'sta_1', 
             'wlan_cfg': get_cfg,
             'wlan_ssid': get_cfg['ssid']}, 
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
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Gateway is Allowed after auth' % tc_name, 
                  2, 
                  False))
        
    if white_list:
        tcs.append(({'sta_tag': 'sta_1',
                     'dest_ip': default_ip['server']}, 
                     'CB_Station_Ping_Dest_Is_Denied', 
                      '%sStation Ping Linux Server is Denied after auth before add entry' % tc_name, 
                      2, 
                      False))

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
                 'dest_ip': default_ip['server']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Linux Server is Allowed after auth' % tc_name, 
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
    attrs = dict(testsuite_name = "Client Isolation with DVLAN"
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
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation with DVLAN", 
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
    