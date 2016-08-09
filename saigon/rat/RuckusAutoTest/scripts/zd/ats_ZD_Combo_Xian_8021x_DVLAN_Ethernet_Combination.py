'''
Combination testing.
1)DVLAN function with Ethernet 802.1x Port-based Authenticator -- WONT AUTO
2)Backup Radius server
3)DVLAN function with accounting
4)Backup 9.5 / Restore 9.5 - Full / Failover/ Policy

Detail Please reference:
https://jira-wiki.ruckuswireless.com/display/Team/Ethernet+802.1x+with+DVLAN#Ethernet8021xwithDVLAN-CombinationTest

Topo:

LinuxPC/Win2003==>Radius/Accounting/DHCP/IOP
                  |
         ZD------SW--AP[LAN#2]--Wire Station#3, XP
                  |
              AP[LAN#2])))))Wireless Station#1, XP
                  |
Station#2, Win7--Hub--Station#4, Win7

    Notes:
        VLAN#1,2,10,20,4094
      
Created on 2012-10-10
@author: cwang
'''

from copy import deepcopy
import time
import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

ap_mac = "24:c9:a1:13:47:d0"
ap_model = "zf7962"#2 port requirement, 1-- Controller Port, 2 -- Testing Port.

sta_a = "sta3"#wire station
sta_b = "sta4"#wire station
#sta_c = "sta3"


sta_list_map = [('192.168.1.31', sta_a),#os_type=win7
                ('192.168.1.41', sta_b),#os_type=win7
#                ('192.168.1.41', sta_c),#ox_type=win7
                ]

svr_list = [    
            {
            'server_name': 'radius-svr',
            'server_addr': '192.168.0.252',
            'radius_auth_secret': '1234567890',
            'server_port': '1812',
            'secondary_server_addr':'192.168.0.250',
            'secondary_server_port':'18120',
            'secondary_radius_auth_secret':'1234567890',                                                                
            },                
            {
            'server_name': 'radius-acct-svr',
            'server_addr': '192.168.0.252',
            'radius_acct_secret': '1234567890',
            'server_port': '1813',
            },                                      
            ]

def get_sta_ipaddr_by_tag(sta_tag):
    for ipaddr, tag in sta_list_map:
        if tag == sta_tag:
            return ipaddr
    raise Exception("Not found station %s in list %s" % (sta_tag, 
                                                         sta_list_map))
default_port_setting = {
                        'override_parent': True,
                        'lan2': {
                                 'enabled': True,
                                 'type': 'trunk',              #[trunk, access, general]
                                 'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                 'vlan_members': "1-4094",   #[1-4094] (expected String type)
                                 'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]                                             
                              }}

primary_secondary_setting_map = [(ap_mac, 
                                    {'override_parent': True,
                                     'lan2': {
                                             'enabled': True,
                                             'type': 'access',              #[trunk, access, general]
                                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                             'vlan_members': '1',   #[1-4094] (expected String type)
                                             'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                             'dot1x_mac_bypass_enabled': True, #optional param.
                                             'enable_dvlan':True,
                                             'guest_vlan': '10',
                                          }},  
                                    '[8021x DVLAN with p/s radius server]',
                                    {sta_a:{'username':'finance.user',
                                            'password':'finance.user',                                            
                                            'before_status':'Guest',
                                            'after_status':'Authorized',
                                            'before_vlan':'10',
                                            'after_vlan':'10',
                                            'target_ip':'192.168.10.252'
                                            },
                                     }                            
                                    ),]

backup_restore_setting_map = [(ap_mac,
                               {'override_parent': True,
                                 'lan2': {
                                         'enabled': True,
                                         'type': 'access',              #[trunk, access, general]
                                         'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                         'vlan_members': '1',   #[1-4094] (expected String type)
                                         'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                         'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                         'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                         'dot1x_mac_bypass_enabled': True, #optional param.
                                         'enable_dvlan':True,
                                         'guest_vlan': '10',
                                      }},  
                                '[Full restore]',
                                {sta_a:{'username':'finance.user',
                                        'password':'finance.user',                                                                                        
                                        'target_ip':'192.168.10.252',
                                        'after_status':'Authorized',
                                        },},
                                None,
                                "restore_everything",
                                ),
                              (ap_mac,
                               {'override_parent': True,
                                 'lan2': {
                                         'enabled': True,
                                         'type': 'access',              #[trunk, access, general]
                                         'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                         'vlan_members': '1',   #[1-4094] (expected String type)
                                         'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                         'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                         'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                         'dot1x_mac_bypass_enabled': False, #optional param.
                                         'enable_dvlan':True,
                                         'guest_vlan': '20',
                                      }},  
                                '[Failover restore]',
                                {sta_a:{'username':'marketing.user',
                                        'password':'marketing.user',                                                                                        
                                        'target_ip':'192.168.20.252',
                                        'after_status':'Authorized',            
                                        },},
                                None,
                                "restore_everything_except_ip",                                
                                        ),
                              (ap_mac,
                               {'override_parent': True,
                                 'lan2': {
                                         'enabled': True,
                                         'type': 'access',              #[trunk, access, general]
                                         'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                         'vlan_members': '1',   #[1-4094] (expected String type)
                                         'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                         'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                         'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                         'dot1x_mac_bypass_enabled': False, #optional param.
                                         'enable_dvlan':True,
                                         'guest_vlan': '',
                                      }},  
                                '[Policy restore]',
                                {sta_a:{'username':'ras.local.user',
                                        'password':'ras.local.user',                                                                                        
                                        'target_ip':'192.168.0.252',
                                        'after_status':None,
                                        },},
                                None,
                                'restore_basic_config'
                                ),                                        
                              ]

accouting_map = [
                 (ap_mac,
                               {'override_parent': True,
                                 'lan2': {
                                         'enabled': True,
                                         'type': 'access',              #[trunk, access, general]
                                         'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                         'vlan_members': '1',   #[1-4094] (expected String type)
                                         'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                                         'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                                         'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                                         'dot1x_mac_bypass_enabled': True, #optional param.
                                         'enable_dvlan':True,
                                         'guest_vlan': '10',
                                      }},  
                                '[DVLAN with accounting]',
                                {sta_a:{'username':'finance.user',
                                        'password':'finance.user',                                                                                        
                                        'target_ip':'192.168.10.252',
                                        'after_status':'Authorized',
                                        'after_vlan':'10',
                                        },},                                                                                                
                                ),
                 ]


def build_init_tcs(ap_mac_list):
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
                  'Create AAA servers',
                  0,
                  False,
                  ))
    
    return tcs



def build_primary_secondary(ap_mac_list):
    tcs = []
    tcs.extend(build_init_tcs(ap_mac_list))    
    for target_station, sta_tag in sta_list_map:
        tcs.append(({'sta_tag': sta_tag, 
                     'sta_ip_addr': target_station}, 
                     'CB_ZD_Create_WireStation', 
                     'Get the station %s' % target_station, 
                     0, 
                     False))
    
    for ap_mac_addr,  port_setting, tcid, attrs in primary_secondary_setting_map:
                    
        tcs.append(({'ap_mac_addr':ap_mac_addr,
                     'port_setting': port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting', 
                    '%sSet Port Setting from ZD GUI' % tcid,
                    1,
                    False))
                                    
        sta_tag_list = attrs.keys()
        for sta in sta_tag_list:        
            tcs.append(({'sta_tag':sta,                                
                         },
                        'CB_Wired_Station_Get_IP_Cfg',
                        '%sGet IP configuration at %s' % (tcid, sta),
                        2,
                        False
                        ))            
        
#            tcs.append(({'sta_tag':sta,
#                         'ap_mac_addr':ap_mac_addr,
#                         'lan_port': 'LAN2',
#                         'status':attrs[sta]['before_status'],
#                         'vlan':attrs[sta]['before_vlan'],                 
#                         },
#                        'CB_ZD_Verify_Wired_Client_Info',
#                        '%sMonitor Page display before auth at %s'  % (tcid, sta),
#                        0,
#                        False
#                        ))                            
#                        
#            tcs.append(({'sta_tag': sta,
#                         'condition': 'disallowed',
#                         'target': attrs[sta]['target_ip'],},
#                         'CB_ZD_Client_Ping_Dest', 
#                         '%s station %s ping a target IP before auth' % (tcid, sta), 
#                         2, 
#                         False))
            ap_mac_bypass = port_setting['lan2']['dot1x_mac_bypass_enabled']
            tcs.append(({'sta_tag':sta,
                         'ap_mac_addr':ap_mac_addr,
                         'lan_port': 'LAN2',
                         'status':attrs[sta]['after_status'],
                         'user':attrs[sta]['username'],
                         'vlan':attrs[sta]['after_vlan'], 
                         'ap_port_macbypass':ap_mac_bypass                
                         },
                        'CB_ZD_Verify_Wired_Client_Info',
                        '%sMonitor Page display before auth at %s' % (tcid, sta),
                        2,
                        False
                        ))  
        
            tcs.append(({'sta_tag':sta,
                         'username':attrs[sta]['username'],
                         'password':attrs[sta]['password'],
                         },
                        'CB_Wired_Station_Perform_Auth',
                        '%s {%s}Perform authenticate' % (tcid, sta),
                        2,
                        False,
                        ))
        
            tcs.append(({'sta_tag':sta,
                         'ap_mac_addr':ap_mac_addr,
                         'lan_port': 'LAN2',
                         'status':attrs[sta]['after_status'],
                         'user':attrs[sta]['username'],
                         'vlan':attrs[sta]['after_vlan']                 
                         },
                        'CB_ZD_Verify_Wired_Client_Info',
                        '%sMonitor Page display after auth at %s' % (tcid, sta),
                        2,
                        False
                        ))    
            condition = "allowed" if attrs[sta]['after_status'] == "Authorized" \
                                    else "disallowed"
            tcs.append(({'sta_tag': sta,
                         'condition': condition,
                         'target': attrs[sta]['target_ip'],},
                         'CB_ZD_Client_Ping_Dest', 
                         '%s station %s ping a target IP after auth' % (tcid, sta), 
                         2, 
                         False))
            
            tcs.append(({'new_cfg':{'server_name': 'radius-svr',
                                    'server_addr': '192.168.0.252',#invaid address
                                    'radius_auth_secret': '1234567890',
                                    'server_port': '1812',
                                    'secondary_server_addr':'192.168.0.250',
                                    'secondary_server_port':'18120',
                                    'secondary_radius_auth_secret':'1234567890',},
                          'server_name':'radius-svr'
                                    },
                                    
                        'CB_ZD_Update_Radius_Setting',
                        '%sUpdate Radius Setting' % tcid,
                        2,
                        False                        
                        )) 
              
            tcs.append(({'sta_tag':sta,
                         'username':attrs[sta]['username'],
                         'password':attrs[sta]['password'],
                         },
                        'CB_Wired_Station_Perform_Auth',
                        '%s {%s}Perform while auth in secondary server' % (tcid, sta),
                        2,
                        False,
                        ))
        
            tcs.append(({'sta_tag':sta,
                         'ap_mac_addr':ap_mac_addr,
                         'lan_port': 'LAN2',
                         'status':attrs[sta]['after_status'],
                         'user':attrs[sta]['username'],
                         'vlan':attrs[sta]['after_vlan']                 
                         },
                        'CB_ZD_Verify_Wired_Client_Info',
                        '%sDisplay while auth in secondary server %s' % (tcid, sta),
                        2,
                        False
                        ))  
              
            condition = "allowed" if attrs[sta]['after_status'] == "Authorized" \
                                    else "disallowed"
            tcs.append(({'sta_tag': sta,
                         'condition': condition,
                         'target': attrs[sta]['target_ip'],},
                         'CB_ZD_Client_Ping_Dest', 
                         '%s station %s ping while auth in seconday server' % (tcid, sta), 
                         2, 
                         False))        
        
            tcs.append(({'ap_mac_addr':ap_mac_addr,
                     'port_setting': default_port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting_Default', 
                    '%sSet Port Setting to default' % tcid,
                    2,
                    True))
        
        tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Clean all AAA servers',
             0,
             True))   
        
        
    return tcs
    

def build_backup_restore(ap_mac_list):
    tcs = []
    tcs.extend(build_init_tcs(ap_mac_list))    
    for target_station, sta_tag in sta_list_map:
        tcs.append(({'sta_tag': sta_tag, 
                     'sta_ip_addr': target_station}, 
                     'CB_ZD_Create_WireStation', 
                     'Get the station %s' % target_station, 
                     0, 
                     False))
    
    for (ap_mac_addr,  
         port_setting, 
         tcid, attrs, save_to, 
         restore_type) in backup_restore_setting_map:
                    
        tcs.append(({'ap_mac_addr':ap_mac_addr,
                     'port_setting': port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting', 
                    '%sSet Port Setting from ZD GUI' % tcid,
                    1,
                    False))
                                    
        sta_tag_list = attrs.keys()
        for sta in sta_tag_list:        
            tcs.append(({'sta_tag':sta,                                
                         },
                        'CB_Wired_Station_Get_IP_Cfg',
                        '%sGet IP configuration at %s before backup' % (tcid, sta),
                        2,
                        False
                        ))
            
            tcs.append(({'sta_tag':sta,
                         'username':attrs[sta]['username'],
                         'password':attrs[sta]['password'],
                         },
                        'CB_Wired_Station_Perform_Auth',
                        '%s {%s}Perform authenticate before backup' % (tcid, sta),
                        2,
                        False,
                        ))
            
            condition = "allowed" if attrs[sta]['after_status'] == "Authorized" \
                                    else "disallowed"
            
            if restore_type == "restore_basic_config":
                condition = "allowed"
            
            tcs.append(({'sta_tag': sta,
                         'condition': condition,
                         'target': attrs[sta]['target_ip'],},
                         'CB_ZD_Client_Ping_Dest', 
                         '%s station %s ping before backup' % (tcid, sta), 
                         2, 
                         False))
            
            tcs.append(({'save_to':save_to},
                        'CB_ZD_Backup',
                        '%s Backup file' % tcid,
                        2,
                        False
                        ))
            
            tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting': default_port_setting,
                 }, 
                'CB_ZD_Set_Port_Setting_Default', 
                '%sSet Port Setting to default' % tcid,
                2,
                False))
        
            tcs.append(({},
                 'CB_ZD_Remove_All_Authentication_Server',
                 '%sClean all AAA servers' % tcid,
                 2,
                 False))
            
            tcs.append(({'restore_type':restore_type,
                         },
                        'CB_ZD_Restore',
                        '%s Restore configuration' % tcid,
                        2,
                        False,                        
                        ))
            
            tcs.append(({'ap_mac_addr':ap_mac_addr,},
                    'CB_ZD_Get_Port_Setting',
                    '%sGet Port Setting after restore' % tcid,
                    2,
                    False
                    ))
            
            if attrs[sta]['after_status'] == "Authorized":                        
                tcs.append(({'port_setting': port_setting,},
                    'CB_ZD_Verify_Port_Setting',
                    '%sVerify Port Setting after restore' % tcid,
                    2,
                    False
                    ))            
            
                tcs.append(({'sta_tag':sta,                                
                             },
                            'CB_Wired_Station_Get_IP_Cfg',
                            '%sGet IP configuration at %s after restore' % (tcid, sta),
                            2,
                            False
                            ))
                
                tcs.append(({'sta_tag':sta,
                             'username':attrs[sta]['username'],
                             'password':attrs[sta]['password'],
                             },
                            'CB_Wired_Station_Perform_Auth',
                            '%s {%s}Perform authenticate after restore' % (tcid, sta),
                            2,
                            False,
                            ))
                
                condition = "allowed" if attrs[sta]['after_status'] == "Authorized" \
                                        else "disallowed"
                tcs.append(({'sta_tag': sta,
                             'condition': condition,
                             'target': attrs[sta]['target_ip'],},
                             'CB_ZD_Client_Ping_Dest', 
                             '%s station %s ping after restore' % (tcid, sta), 
                             2, 
                             False))
            else:
                expected_setting = {
                                    'override_parent': False,
                                    'lan2': {
                                             'enabled': True,
                                             'type': 'trunk',              #[trunk, access, general]
                                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                             'vlan_members': "1-4094",   #[1-4094] (expected String type)
                                             'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]                                             
                                          }}
                tcs.append(({'port_setting': expected_setting,},
                    'CB_ZD_Verify_Port_Setting',
                    '%sVerify Port Setting after restore' % tcid,
                    2,
                    False
                    ))
            
            tcs.append(({'ap_mac_addr':ap_mac_addr,
                     'port_setting': default_port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting', 
                    '%sSet Port Setting to default' % tcid,
                    2,
                    True))
                
    return tcs 


def build_accouting_server(ap_mac_list):
    tcs = []
    tcs.extend(build_init_tcs(ap_mac_list))    
    for target_station, sta_tag in sta_list_map:
        tcs.append(({'sta_tag': sta_tag, 
                     'sta_ip_addr': target_station}, 
                     'CB_ZD_Create_WireStation', 
                     'Get the station %s' % target_station, 
                     0, 
                     False))
    
    for ap_mac_addr,  port_setting, tcid, attrs in accouting_map:
                    
        tcs.append(({'ap_mac_addr':ap_mac_addr,
                     'port_setting': port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting', 
                    '%sSet Port Setting from ZD GUI' % tcid,
                    1,
                    False))
                                    
        sta_tag_list = attrs.keys()
        for sta in sta_tag_list:        
            tcs.append(({'sta_tag':sta,                                
                         },
                        'CB_Wired_Station_Get_IP_Cfg',
                        '%sGet IP configuration at %s' % (tcid, sta),
                        2,
                        False
                        ))            
        
            tcs.append(({                 
                         },
                        'CB_ZD_Start_Sniffer_On_Server',
                        '%sStart sniffer'  % (tcid),
                        2,
                        False
                        ))                            
                                     
            tcs.append(({'sta_tag':sta,
                         'username':attrs[sta]['username'],
                         'password':attrs[sta]['password'],
                         },
                        'CB_Wired_Station_Perform_Auth',
                        '%s {%s}Perform authenticate' % (tcid, sta),
                        2,
                        False,
                        ))
        
            tcs.append(({'sta_tag':sta,
                         'ap_mac_addr':ap_mac_addr,
                         'lan_port': 'LAN2',
                         'status':attrs[sta]['after_status'],
                         'user':attrs[sta]['username'],
                         'vlan':attrs[sta]['after_vlan']                 
                         },
                        'CB_ZD_Verify_Wired_Client_Info',
                        '%sMonitor Page display after auth at %s' % (tcid, sta),
                        2,
                        False
                        ))    
            condition = "allowed" if attrs[sta]['after_status'] == "Authorized" \
                                    else "disallowed"
                                    
            tcs.append(({'sta_tag': sta,
                         'condition': condition,
                         'target': attrs[sta]['target_ip'],},
                         'CB_ZD_Client_Ping_Dest', 
                         '%s station %s ping a target IP after auth' % (tcid, sta), 
                         2, 
                         False))
            
            
#            tcs.append(({},
#                        'CB_ZD_Stop_Sniffer_On_Server',
#                        '%sStop Sniffer' % tcid,
#                        2,
#                        False
#                        ))
            
            tcs.append(({'acct_svr_port': '1813',
                         'acct_enable': True,
                         'pause': 2.0},
                        'CB_ZD_Accounting_Wire_Station_Join',
                        '%sVerify Sniffer' % tcid,
                        2,
                        False
                        ))
            
            tcs.append(({'ap_mac_addr':ap_mac_addr,
                     'port_setting': default_port_setting,
                     }, 
                    'CB_ZD_Set_Port_Setting', 
                    '%sSet Port Setting to default' % tcid,
                    2,
                    True))
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Udaipur 802.1x Ethernet Combination",
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
    
    ts_name_list = [('Xian 802.1x DVLAN Ethernet with primary-secondary', build_primary_secondary),                                        
                    ('Xian 802.1x DVLAN Ethernet with port backup-restore', build_backup_restore),
                    ('Xian 802.1x DVLAN Ethernet with port accounting', build_accouting_server),
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(all_aps_mac_list)
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        #check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
    


def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)


