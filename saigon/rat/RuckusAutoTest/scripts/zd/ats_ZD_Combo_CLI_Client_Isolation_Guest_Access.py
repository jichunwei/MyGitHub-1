"""
Guest Access wlan(8 tcs)

    client isolation disabled
    client isolation enabled
    client isolation enabled and bind the whitelist to the wlan
    bind whitelist to Guest Access wlan(MAC only)
    bind whitelist to Guest Access wlan(IP and MAC entry)
    redirect url, whitelist enable
    redirect ipaddr, whitelist enable
    different subnet
    
Created on 2013-7-26
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-GuestAccess-1",
            "ssid" : "Rqa-auto-RAT-CI-GuestAccess-1",
            'type': 'guest',
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

    tcs.append(({'guest_access_conf': guest_access_conf}, 
                   'CB_ZD_CLI_Configure_Guest_Access', 
                   'Set guest access authentication server', 
                   0, 
                   False))
    
    guest_restrict_conf = {'order': '2',
     '2':{'destination_address': '192.168.0.0/16', 
          'type': 'Allow',
          'order':'1'}
    }
    tcs.append(({'guest_restrict_conf': guest_restrict_conf}, 
                   'CB_ZD_CLI_Configure_Guest_Restrict_Access', 
                   'Configure restricted subnet access', 
                   0, 
                   False))
    
    test_list = _generate_test_cfg()

    for test_case in test_list:
        tcs.extend(build_stcs_main(test_case))

    guest_access_clear_conf = {'authentication_server': 'Local Database',                 
                      'terms_of_use': 'Disabled',
                      'redirection': 'To the URL that the user intends to visit',}
    
    tcs.append(({'guest_access_conf': guest_access_clear_conf},
                'CB_ZD_CLI_Configure_Guest_Access',
                'Cleanup Guest Access',
                2,
                True))

    guest_restrict_conf = {'order': '1'}
    tcs.append(({'guest_restrict_conf': guest_restrict_conf,
                 'cleanup': True,}, 
                   'CB_ZD_CLI_Configure_Guest_Restrict_Access', 
                   'Configure restricted subnet access to default', 
                   0, 
                   True))
    
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
    
    test_cfg.append(({'tc_name' : '[Redirect URL]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MAC',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      'redirection': 'To the following URL',
                      'url':'http://www.example.net/',
                      }))
    
    test_cfg.append(({'tc_name' : '[Redirect IP]',
                      'white_list' : whitelist_conf['name'],
                      'rule_type' : 'MACandIP',
                      'isolation_per_ap' : True,
                      'isolation_across_ap' : True,
                      'redirection': 'To the following URL',
                      'url':'http://172.16.10.252/',
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
    
    if test_case.get('redirection'):
        redirection_conf = {'redirection':test_case.get('redirection'),
                            'url':test_case.get('url')}
        tcs.append(({'guest_access_conf': redirection_conf}, 
                   'CB_ZD_CLI_Configure_Guest_Access', 
                   '%sSet guest access redirection' % tc_name, 
                   1, 
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

    tcs.append(( guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg'],
                'CB_ZD_Generate_Guest_Pass',
                '%sGenerate the guestpass by the guest user' % tc_name,
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
                 'dest_ip': default_ip['server'],
                 'clean_arp_before_ping': True,}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sStation Ping Linux Server is Denied before authentication' % tc_name, 
                  2, 
                  False))
    
    #Perform Guest Auth
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_CaptivePortal_Start_Browser', 
                  "%sCreate the station's browser object" % tc_name, 
                  2, 
                  False))

    if test_case.get('redirection'):
        redirect_url = test_case.get('url')
    else:
        redirect_url = ""
                
    tcs.append(({'sta_tag': 'sta_1',
                   'no_auth': False, #@author: Jane.Guo @since: 2013-10, If we don't add linux mac or ip, redirect will fail,so no auth first
                   'use_tou': True,
                   'target_url': target_url, 
                   'redirect_url': redirect_url,
                   }, 
                'CB_Station_CaptivePortal_Perform_GuestAuth', 
                '%sPerform guest authentication' % tc_name, 
                2, 
                False))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_CaptivePortal_Quit_Browser', 
                  "%sClosed the station's browser object" % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'dest_ip': default_ip['switch']}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Gateway is Allowed after auth' % tc_name, 
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
    
    if test_case.get('redirection'):
        redirection_conf = {'redirection':'To the URL that the user intends to visit'}
        tcs.append(({'guest_access_conf': redirection_conf}, 
                   'CB_ZD_CLI_Configure_Guest_Access', 
                   '%sSet guest access redirection to default' % tc_name, 
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
    attrs = dict(testsuite_name = "Client Isolation with Guest Access"
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
                                 "Client Isolation with Guest Access", 
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
    