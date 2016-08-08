'''

To verify the Wired 802.1X Station Monitor Page display correctly.
1. Check web disaply correctly when client authorized/unauthorized.
2. The Delete button in Action is used to remove the entry of wired station and clean its statistic.
3. Check the client statis is correct.
4. Check the event is sent and correct information.


To verify MAC-based authenticator work normally on AP.
1. SW -- Rockus AP(MAC-based) -- End Device*2 (Supplicant)
3. The AP will automatic send STA MAC to radius server authorized by default.

To verify Port-based authenticator work normally on AP.
1. SW -- Rockus AP(Port-based) -- End Device*1 (Supplicant)

To verify Supplicant work normally on AP.
1. SW(MAC-based) -- (Supplicant)Rockus AP --SW-- End Device*2(Supplicant)

Created on 2012-3-18
@author: cwang@ruckukswireless.com
'''
#import time
import sys
import re
#from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
#from RuckusAutoTest.common import lib_Constant

sta_list_map = [('192.168.1.31', 'sta_3', 'xp'),
                ('192.168.1.41', 'sta_4', 'win7'),
                ]

default_port_setting = {
                        'override_parent': True,
                        'lan2': {
                                 'enabled': True,
                                 'type': 'trunk',              #[trunk, access, general]
                                 'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                 'vlan_members': "1-4094",   #[1-4094] (expected String type)
                                 'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]                                             
                              }}

for target_station, sta_tag, os_type in sta_list_map:
    ap_station_portbase_setting_map=[('%s',                             
                                             {
                                              'lan2': {
                                                   'enabled': True,
                                                   'type': 'trunk',              #[trunk, access, general]
                                                   'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                                   'vlan_members': '1-4094',   #[1-4094] (expected String type)
                                                   'dot1x': 'auth-port', #[disabled, supp, auth-port, auth-mac]
                                                   'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                                   'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                                   'dot1x_mac_bypass_enabled': False, #optional param.
                                                }},
                                          #'[ZDCLI Port-based authenticator disable mac bypass on ap=%s, os_type=%s]'#tcid, ap model, os type
                                            '[ZDCLI Port-based authenticator disable mac bypass,os_type=%s]'#tcid, ap model, os type
                                              ),
                                           
                                        #('24:c9:a1:13:47:d0', 'zf7363', 'sta_2', 'win7',
                                        #{
                                        #'lan2': {
                                        #           'enabled': True,
                                        #           'type': 'trunk',              #[trunk, access, general]
                                        #           'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                        #           'vlan_members': '1-4094',   #[1-4094] (expected String type)
                                        #           'dot1x': 'auth-port', #[disabled, supp, auth-port, auth-mac]
                                        #           'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                        #           'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                        #           'dot1x_mac_bypass_enabled': True, #optional param.
                                        #        }},
                                        # '[ZDCLI Port-based authenticator enable mac bypass on ap=%s, os_type=%s]'#tcid, ap model, os type
                                        # )
                                     ]
        
    ap_station_macbase_setting_map=[('%s',
                                            {
                                             'lan2': {
                                                 'enabled': True,
                                                 'type': 'access',              #[trunk, access, general]
                                                 'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                                 'vlan_members': '1',   #[1-4094] (expected String type)
                                                 'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                                'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                                'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                                'dot1x_mac_bypass_enabled': True, #optional param.
                                             }},  
                                       '[ZDCLI Mac-based authenticator enable mac bypass, os_type=%s]'#tcid, ap model, os type
                                       #'[ZDCLI Mac-based authenticator enable mac bypass on ap=%s, os_type=%s]'#tcid, ap model, os type                              
                                       ),  
                                    
                                    #('24:c9:a1:13:47:d0', 'zf7363', 'sta_2', 'win7',
                                    #{
                                    # 'lan2': {
                                    #         'enabled': True,
                                    #         'type': 'access',              #[trunk, access, general]
                                    #         'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                    #         'vlan_members': '1',   #[1-4094] (expected String type)
                                    #         'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                    #         'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                    #         'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                    #         'dot1x_mac_bypass_enabled': False, #optional param.
                                    #      }},
                                    #'[ZDCLI Mac-based authenticator disable mac bypass on ap=%s, os_type=%s]'#tcid, ap model, os type
                                    #),                             
                                      ]

svr_list = [    
            {
            'server_name': 'radius-svr',
            'server_addr': '192.168.0.252',
            'radius_auth_secret': '1234567890',
            'server_port': '1812',                                        
            },                
            {
            'server_name': 'radius-acct-svr',
            'server_addr': '192.168.0.252',
            'radius_acct_secret': '1234567890',
            'server_port': '1813',
            },                        
            ]

def build_port_based_tcs(ap_mac_list):
    tcs = []    
    for ap_mac in ap_mac_list:
        tcs.append(({'ap_mac_addr':ap_mac,
                     'port_setting': default_port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting_Default', 
                    'Set %s Port Setting to Default' % ap_mac,
                    0,
                    False))
        
    tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers',
             0,
             False))
    
    tcs.append(({'auth_ser_cfg_list' : svr_list},
                  'CB_ZD_Create_Authentication_Server',
                  'Create aaa servers',
                  0,
                  False,
                  ))
    
    
    for target_station, sta_tag, os_type in sta_list_map:
        tcs.append(({'sta_tag': sta_tag, 
                     'sta_ip_addr': target_station}, 
                     'CB_ZD_Create_WireStation', 
                     'Get the station %s - %s' % (target_station, os_type), 
                     0, 
                     False)) 
   
    #for ap_mac_addr, ap_model, sta_tag, os_type, port_setting, tcid in ap_station_portbase_setting_map: 
    for i in range(len(ap_mac_list)):
        for ap_mac_addr, port_setting, tcid in ap_station_portbase_setting_map:      
            ap_mac_address = ap_mac_addr %ap_mac_list[i]
            tcs.append(({'ap_mac_addr':ap_mac_address,
                     'port_setting': port_setting,
                     }, 
                    'CB_ZDCLI_Set_Port_Setting', 
                    'Set Port Setting from ZD CLI',
                    0,
                    False))
            
            stas_list = sta_list_map[:]
            sta_info = stas_list[0]
            sta_tag = sta_info[1]
            os_type = sta_info[2]
            test_case_name = tcid %os_type    
            tcs.append(({},
                        'CB_ZD_Clear_Event',
                        '%sClear events' %test_case_name,
                        1,
                        False
                        ))
        
            tcs.append(({'sta_tag':sta_tag,                                
                        },
                        'CB_Wired_Station_Get_IP_Cfg',
                        '%sGet IP configuration' % test_case_name,
                        2,
                        False
                        ))    
        
            if port_setting ['lan2']['dot1x_mac_bypass_enabled']== False: 
                tcs.append(({'sta_tag':sta_tag,
                            'target':'192.168.0.252',
                            'condition':'disallowed',                 
                            },
                            'CB_ZD_Client_Ping_Dest',
                            '%sPing target before auth' % test_case_name,
                            2,
                            False
                            ))
             
                tcs.append(({'sta_tag':sta_tag,
                             'ap_mac_addr':ap_mac_address,
                             'lan_port': 'LAN2',
                             'status':'Unauthorized',                 
                             },
                             'CB_ZD_Verify_Wired_Client_Info',
                             '%sMonitor Page display correctly before auth' % test_case_name,
                             2,
                             False
                            ))
                tcs.append(({'sta_tag':sta_tag},
                             'CB_Wired_Station_Perform_Auth',
                             '%sPerform authenticate' % test_case_name,
                             2,
                             False,
                             ))
        
                tcs.append(({'sta_tag':sta_tag,
                         'target':'192.168.0.252',
                         'condition':'allowed',                 
                          },
                         'CB_ZD_Client_Ping_Dest',
                         '%sPing target after auth' % test_case_name,
                          2,
                          False
                          ))
        
                tcs.append(({'sta_tag':sta_tag,
                            'ap_mac_addr':ap_mac_address,
                            'lan_port': 'LAN2',
                            'status':'Authorized',
                            'user':'ras.local.user',              
                            },
                           'CB_ZD_Verify_Wired_Client_Info',
                           '%sMonitor Page display correctly after auth' % test_case_name,
                           2,
                           False
                           ))
            else:
                tcs.append(({'sta_tag':sta_tag,
                         'target':'192.168.0.252',
                         'condition':'allowed',                 
                          },
                         'CB_ZD_Client_Ping_Dest',
                         '%sPing target after auth' % test_case_name,
                          2,
                          False
                          ))
        
                tcs.append(({'sta_tag':sta_tag,
                            'ap_mac_addr':ap_mac_address,
                            'lan_port': 'LAN2',
                            'status':'Authorized',
                            'user':sta_tag,              
                            },
                           'CB_ZD_Verify_Wired_Client_Info',
                           '%sMonitor Page display correctly after auth' % test_case_name,
                           2,
                           False
                           ))
            
            stas_list.pop(0)        
            for target_station, sta_tag , os_type in stas_list:
                test_case_name = tcid %os_type 
                exec_level = 1
                if port_setting ['lan2']['dot1x_mac_bypass_enabled']== True:
                    tcs.append(({'user_name':sta_tag,
                            'password':sta_tag,
                            'use_mac': True,             
                            },
                           'CB_Server_Add_And_Delete_Radius_Users',
                           '%sDelete RADIUS User' % test_case_name,
                           1,
                           False
                           ))
                    exec_level = 2
                    
                tcs.append(({},
                        'CB_ZD_Clear_Event',
                        '%sClear events' %test_case_name,
                        exec_level,
                        False
                        ))
        
                tcs.append(({'sta_tag':sta_tag,                                
                        },
                        'CB_Wired_Station_Get_IP_Cfg',
                        '%sGet IP configuration' % test_case_name,
                        2,
                        False
                        ))    
                
                tcs.append(({'sta_tag':sta_tag,
                         'target':'192.168.0.252',
                         'condition':'allowed',                 
                          },
                         'CB_ZD_Client_Ping_Dest',
                         '%sPing target after auth' % test_case_name,
                          2,
                          False
                          ))
        
                tcs.append(({'sta_tag':sta_tag,
                            'ap_mac_addr':ap_mac_address,
                            'lan_port': 'LAN2',
                            'status':'Authorized'              
                            },
                           'CB_ZD_Verify_Wired_Client_Info',
                           '%sMonitor Page display correctly after auth' % test_case_name,
                           2,
                           False
                           ))
                
                if port_setting ['lan2']['dot1x_mac_bypass_enabled']== True:
                    tcs.append(({'user_name':sta_tag,
                            'password':sta_tag,
                            'use_mac': True,             
                            },
                           'CB_Server_Add_And_Delete_Radius_Users',
                           '%sADD RADIUS User' % test_case_name,
                           2,
                           False
                           ))
                
        
            tcs.append(({'ap_mac_addr':ap_mac_address,
                         'port_setting': default_port_setting,
                         }, 
                        'CB_ZD_Set_Port_Setting_Default', 
                        'Set Port Setting from ZD CLI',
                        0,
                        True))
        
    '''                
        
        #tcs.append(({'sta_tag':sta_tag},
        #             'CB_ZD_Delete_Wired_Client',
        #             '%sDelete entity from ZD GUI' % tcid,
        #             2,
        #             False
        #             )
        #            )
        
        #tcs.append(({'sta_tag':sta_tag,
        #              'ap_mac_addr':ap_mac_addr,
        #              'lan_port': 'LAN2',
        #              'status':'Unauthorized',                 
        #              },
        #             'CB_ZD_Verify_Wired_Client_Info',
        #             '%sMonitor Page display correctly after delete action' % tcid,
        #             2,
        #             False
        #             ))
                        
            #tcs.append(({'ap_mac_addr':ap_mac_addr,
            #         'port_setting': default_port_setting,
            #         }, 
            #        'CB_ZD_Set_Port_Setting_Default', 
            #        'Set Port Setting from ZD GUI',
            #        0,
            #        True))
   '''     
    tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Clean all AAA servers',
             0,
             False))
    
    return tcs

def build_mac_based_tcs(ap_mac_list):
    tcs = []    
    for ap_mac in ap_mac_list:
        tcs.append(({'ap_mac_addr':ap_mac,
                     'port_setting': default_port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting_Default', 
                    'Set %s Port Setting to Default' % ap_mac,
                    0,
                    False))
    
    tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers',
             0,
             False))
    
    tcs.append(({'auth_ser_cfg_list' : svr_list},
                  'CB_ZD_Create_Authentication_Server',
                  'Create aaa servers',
                  0,
                  False,
                  ))
    
    for target_station, sta_tag , os_type in sta_list_map:
        tcs.append(({'sta_tag': sta_tag, 
                     'sta_ip_addr': target_station}, 
                     'CB_ZD_Create_WireStation', 
                     'Get the station %s - %s' %(target_station, os_type), 
                     0, 
                     False))
        
   
    #for ap_mac_addr, ap_model, sta_tag, os_type, port_setting, tcid in ap_station_macbase_setting_map:
    for i in range(len(ap_mac_list)):
        for ap_mac_addr, port_setting, tcid in ap_station_macbase_setting_map:
            #tcid = tcid %(os_type) 
            #tcid = tcid % (ap_model, os_type)               
            #tcs.append(({'ap_mac_addr':ap_mac_addr,
            #         'port_setting': port_setting,
            #         }, 
            #        'CB_ZDCLI_Set_Port_Setting', 
            #        'Set Port Setting from ZD GUI',
            #        0,
            #        False))
            ap_mac_address = ap_mac_addr %ap_mac_list[i]
            tcs.append(({'ap_mac_addr':ap_mac_address,
                     'port_setting': port_setting,
                     }, 
                    'CB_ZDCLI_Set_Port_Setting', 
                    'Set Port Setting from ZD CLI',
                    0,
                    False))
            
            for target_station, sta_tag , os_type in sta_list_map:  
                test_case_name = tcid %os_type  
                tcs.append(({},
                        'CB_ZD_Clear_Event',
                        '%sClear events' % test_case_name,
                        1,
                        False
                        ))
        
                tcs.append(({'sta_tag':sta_tag,                                
                        },
                        'CB_Wired_Station_Get_IP_Cfg',
                        '%sGet IP configuration' % test_case_name,
                        2,
                        False
                        ))    
        
                if port_setting ['lan2']['dot1x_mac_bypass_enabled']== False:       
                    tcs.append(({'sta_tag':sta_tag,
                            'target':'192.168.0.252',
                            'condition':'disallowed',                 
                            },
                            'CB_ZD_Client_Ping_Dest',
                            '%sPing target before auth' % test_case_name,
                            2,
                            False
                            ))
             
                    tcs.append(({'sta_tag':sta_tag,
                             'ap_mac_addr':ap_mac_address,
                             'lan_port': 'LAN2',
                             'status':'Unauthorized',                 
                             },
                             'CB_ZD_Verify_Wired_Client_Info',
                             '%sMonitor Page display correctly before auth' % test_case_name,
                             2,
                             False
                            ))
                    tcs.append(({'sta_tag':sta_tag},
                             'CB_Wired_Station_Perform_Auth',
                             '%sPerform authenticate' % test_case_name,
                             2,
                             False,
                             ))
        
                    tcs.append(({'sta_tag':sta_tag,
                         'target':'192.168.0.252',
                         'condition':'allowed',                 
                          },
                         'CB_ZD_Client_Ping_Dest',
                         '%sPing target after auth' % test_case_name,
                          2,
                          False
                          ))
        
                    tcs.append(({'sta_tag':sta_tag,
                            'ap_mac_addr':ap_mac_address,
                            'lan_port': 'LAN2',
                            'status':'Authorized',  
                            'user':'ras.local.user',           
                            },
                           'CB_ZD_Verify_Wired_Client_Info',
                           '%sMonitor Page display correctly after auth' % test_case_name,
                           2,
                           False
                           ))
                else:
                    tcs.append(({'sta_tag':sta_tag,
                         'target':'192.168.0.252',
                         'condition':'allowed',                 
                          },
                         'CB_ZD_Client_Ping_Dest',
                         '%sPing target after auth' % test_case_name,
                          2,
                          False
                          ))
        
                    tcs.append(({'sta_tag':sta_tag,
                            'ap_mac_addr':ap_mac_address,
                            'lan_port': 'LAN2',
                            'status':'Authorized',  
                            'user':sta_tag,           
                            },
                           'CB_ZD_Verify_Wired_Client_Info',
                           '%sMonitor Page display correctly after auth' % test_case_name,
                           2,
                           False
                           ))
        
            tcs.append(({'ap_mac_addr':ap_mac_address,
                         'port_setting': default_port_setting,
                         }, 
                        'CB_ZD_Set_Port_Setting_Default', 
                        'Set Port Setting from ZD CLI',
                        0,
                        True))
        #tcs.append(({'sta_tag':sta_tag},
        #           'CB_ZD_Delete_Wired_Client',
        #          '%sDelete entity from ZD GUI' % tcid,
        #         2,
        #        False
        #       )
        #     )
        
        #tcs.append(({'sta_tag':sta_tag,
        #            'ap_mac_addr':ap_mac_addr,
        #           'lan_port': 'LAN2',
        #          'status':'Unauthorized',                 
        #         },
        #       'CB_ZD_Verify_Wired_Client_Info',
        #      '%sMonitor Page display correctly after delete action' % tcid,
        #     2,
        #   False
        #  ))
                        
            #tcs.append(({'ap_mac_addr':ap_mac_addr,
            #             'port_setting': default_port_setting,
            #             }, 
            #            'CB_ZD_Set_Port_Setting_Default', 
            #            'Set Port Setting from ZD CLI',
            #            0,
            #            True))
    
    tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Clean all AAA servers',
             0,
             True))
    
    return tcs

def build_supp_tcs():
    pass


def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Udaipur 802.1x Ethernet Basic-CLI",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
       
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    ap_mac_addr = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        expr = "zf\d{3}(\d)"
        res = re.match(expr, ap_info['model'], re.I)
        if res:
            port = int(res.group(1))
            if port >1:
                ap_mac_addr = ap_sym_name
                break
                    
    if not ap_mac_addr:
        raise Exception("Have't found any valid AP in test bed, please check your AP port number which must be >=2")
    
    ts_name_list = [('Udaipur 802.1x Ethernet Mac Based-CLI', build_mac_based_tcs),
                    ('Udaipur 802.1x Ethernet Port Based-CLI', build_port_based_tcs),                    
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(all_aps_mac_list)
    
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
