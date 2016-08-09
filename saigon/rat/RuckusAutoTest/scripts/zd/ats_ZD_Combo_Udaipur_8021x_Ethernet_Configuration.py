'''
Check the ZD CLI command work correctly.
    1. Check ZD CLI and ZD WEB will synchronization.
    2. Check 802.1X CLI command setting can't lose even ZD reboot.
Created on 2012-3-18
@author: cwang@ruckuswireless.com
'''

#import time
import sys
import re
#from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
#from RuckusAutoTest.common import lib_Constant

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

default_port_setting = {'override_parent': True,
                        'lan2': {
                                 'enabled': True,
                                 'type': 'trunk',              #[trunk, access, general]
                                 'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                 'vlan_members': "1-4094",   #[1-4094] (expected String type)
                                 'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]                                             
                              }}

param_cfgs =[
    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to disabled]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                          },
                  }
    },    
    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to general + auth-port]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'general',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-10,100-500,600',   #[1-4094] (expected String type)
                             'dot1x': 'auth-port', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': False, #optional param.
                          },
                  }
    },
    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to access + auth-mac]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'access',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1',   #[1-4094] (expected String type)
                             'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': False, #optional param.
                          },
                  }
    },
    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to trunk + auth-port + mac bypass]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'auth-port', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': True, #optional param.
                          },
                  }
    },
    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to access + auth-mac + mac bypass]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'access',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1',   #[1-4094] (expected String type)
                             'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': True, #optional param.
                          },
                  }
    }, 
    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to trunk + supp + mac]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'supp', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_supp_mac_enabled':True, #optional param.
                             'dot1x_supp_auth_enabled':False, #optional param.                             
                          },
                  }
    },

    {
    'gui':True,
    'tcid':'[GUI set 802.1x lan2 to trunk + supp + auth]',
    'port_setting':{'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'supp', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_supp_mac_enabled':False, #optional param.
                             'dot1x_supp_auth_enabled':True, #optional param.
                             'dot1x_supp_username':'ras.local.user',
                             'dot1x_supp_password': 'ras.local.user',
                          },
                  }
    },       
    
    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to disabled]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                          },
                  }
    },    
    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to general + auth-port]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'general',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-10,100-500,600',   #[1-4094] (expected String type)
                             'dot1x': 'auth-port', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': False, #optional param.
                          },
                  }
    },
    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to access + auth-mac]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'access',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1',   #[1-4094] (expected String type)
                             'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': False, #optional param.
                          },
                  }
    },
    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to trunk + auth-port + mac bypass]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'auth-port', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': True, #optional param.
                          },
                  }
    },
    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to access + auth-mac + mac bypass]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'access',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1',   #[1-4094] (expected String type)
                             'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_auth_svr': 'radius-svr', #Radius Server Name "radius-svr"
                             'dot1x_acct_svr': 'radius-acct-svr', #Radius Accounting Server Name "radius-acct-svr"
                             'dot1x_mac_bypass_enabled': True, #optional param.
                          },
                  }
    }, 
    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to trunk + supp + mac]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'supp', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_supp_mac_enabled':True, #optional param.
                             'dot1x_supp_auth_enabled':False, #optional param.                             
                          },
                  }
    },

    {
    'gui':False,
    'tcid':'[CLI set 802.1x lan2 to trunk + supp + auth]',
    'port_setting':{
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'supp', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_supp_mac_enabled':False, #optional param.
                             'dot1x_supp_auth_enabled':True, #optional param.
                             'dot1x_supp_username':'ras.local.user',
                             'dot1x_supp_password': 'ras.local.user',
                          },
                  }
    },                     
]
    
def build_cli_cfg_tcs(tcid, port_setting, ap_mac_addr):
    tcs = []
    tcs.append(({'port_setting': port_setting,
                 'ap_mac_addr':ap_mac_addr
                 }, 
                'CB_ZDCLI_Set_Port_Setting', 
                '%sSet Port Setting from ZD CLI' % tcid,
                1,
                False))    
    
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZD_Get_Port_Setting', 
                '%sGet Port Setting from ZD GUI' % tcid,
                2,
                False))
    
            
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZDCLI_Get_Port_Setting', 
                '%sGet Port Setting from ZD CLI' % tcid,
                2,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting':port_setting,
                 }, 
                'CB_ZDCLI_Verify_Port_Setting', 
                '%sVerify Port Setting from ZD CLI' % tcid,
                2,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr},
                'CB_ZD_ZDCLI_Verify_Port_Setting',
                '%sVerify Port Setting between GUI and CLI' % tcid,
                2,
                False
                ))
    
    return tcs

def build_gui_cfg_tcs(tcid, port_setting, ap_mac_addr):
    tcs = []    
    tcs.append(({'port_setting': port_setting,
                 'ap_mac_addr':ap_mac_addr
                 }, 
                'CB_ZD_Set_Port_Setting', 
                '%sSet Port Setting from ZD GUI' % tcid,
                1,
                False))    
    
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZD_Get_Port_Setting', 
                '%sGet Port Setting from ZD GUI' % tcid,
                2,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting':port_setting
                 }, 
                'CB_ZD_Verify_Port_Setting', 
                '%sVerify Port Setting from ZD GUI' % tcid,
                2,
                False))
        
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZDCLI_Get_Port_Setting', 
                '%sGet Port Setting from ZD CLI' % tcid,
                2,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,},
                'CB_ZD_ZDCLI_Verify_Port_Setting',
                '%sVerify Port Setting between GUI and CLI' % tcid,
                2,
                False
                ))
    
    return tcs

def build_basic_tcs(ap_mac_addr, ap_mac_list):        
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
    
    tcid = "[Check 802.1x Ethernet default setting]"    
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZD_Get_Port_Setting', 
                '%sGet Port Setting from ZD GUI' % tcid,
                1,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting':{'override_parent': False}
                 }, 
                'CB_ZD_Verify_Port_Setting', 
                '%sVerify Port Setting from ZD GUI' % tcid,
                2,
                False))
        
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZDCLI_Get_Port_Setting', 
                '%sGet Port Setting from ZD CLI' % tcid,
                2,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr},
                'CB_ZD_ZDCLI_Verify_Port_Setting',
                '%sVerify Port Setting between GUI and CLI' % tcid,
                2,
                False
                ))
    
    for param_cfg in param_cfgs:
        port_setting = param_cfg['port_setting']
        tcid = param_cfg['tcid']
        if param_cfg['gui']:
            tcs.extend(build_gui_cfg_tcs(tcid, port_setting, ap_mac_addr))
        else:
            tcs.extend(build_cli_cfg_tcs(tcid, port_setting, ap_mac_addr))
                
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting': default_port_setting,
                 }, 
                'CB_ZD_Set_Port_Setting_Default', 
                '%sSet Port Setting from ZD GUI' % tcid,
                2,
                True))
        
    tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Clean all AAA servers',
             0,
             True))
    
    return tcs

def build_reboot_tcs(ap_mac_addr, ap_mac_list):
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
    
       
    port_setting = {'override_parent': True,
                    'lan2': {
                             'enabled': True,
                             'type': 'trunk',              #[trunk, access, general]
                             'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                             'vlan_members': '1-4094',   #[1-4094] (expected String type)
                             'dot1x': 'supp', #[disabled, supp, auth-port, auth-mac]
                             'dot1x_supp_mac_enabled':False, #optional param.
                             'dot1x_supp_auth_enabled':True, #optional param.
                             'dot1x_supp_username':'ras.local.user',
                             'dot1x_supp_password': 'ras.local.user',
                          },
                  }
    
    tcs.append(({'port_setting': port_setting,
                 'ap_mac_addr':ap_mac_addr
                 }, 
                'CB_ZD_Set_Port_Setting', 
                'Set Port Setting from ZD GUI',
                0,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZD_Get_Port_Setting', 
                'Get Port Setting from ZD GUI',
                0,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting':port_setting
                 }, 
                'CB_ZD_Verify_Port_Setting', 
                'Verify Port Setting from ZD GUI',
                0,
                False))
    
    tcs.append(({},
                'CB_ZD_Reboot',
                'Reboot ZD',
                0,
                False
                ))
    
    tcid = "[Check 802.1x Ethernet after reboot]"
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZDCLI_Get_Port_Setting', 
                '%sGet Port Setting from ZD CLI' % tcid,
                1,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,                 
                 },
                'CB_ZD_ZDCLI_Verify_Port_Setting',
                '%sVerify Port Setting between GUI and CLI' % tcid,
                2,
                False
                ))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr}, 
                'CB_ZD_Get_Port_Setting', 
                '%sGet Port Setting from ZD GUI' % tcid,
                2,
                False))
    
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting':port_setting
                 }, 
                'CB_ZD_Verify_Port_Setting', 
                '%sVerify Port Setting from ZD GUI' % tcid,
                2,
                False))
        
    #tcs.append(({'ap_mac_addr':ap_mac_addr}, 
    #            'CB_ZDCLI_Get_Port_Setting', 
    #            '%sGet Port Setting from ZD CLI' % tcid,
    #            1,
    #            False))
    
    #tcs.append(({'ap_mac_addr':ap_mac_addr},
    #            'CB_ZD_ZDCLI_Verify_Port_Setting',
    #            '%sVerify Port Setting between GUI and CLI' % tcid,
    #            2,
    #            False
    #            ))
        
    tcs.append(({'ap_mac_addr':ap_mac_addr,
                 'port_setting': default_port_setting,
                 }, 
                'CB_ZD_Set_Port_Setting_Default', 
                '%sSet Port Setting from ZD GUI' % tcid,
                2,
                True))
    
    tcs.append(({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Clean all AAA servers',
             0,
             True))
    
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Udaipur 802.1x Ethernet Configuration",
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
                ap_mac_addr = ap_info['mac']
                break
                    
    if not ap_mac_addr:
        raise Exception("Have't found any valid AP in test bed, please check your AP port number which must be >=2")
    
    ts_name_list = [('Udaipur 802.1x Ethernet Configuration', build_basic_tcs),
                    ('Udaipur 802.1x Ethernet Reboot Checking', build_reboot_tcs),                    
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(ap_mac_addr, all_aps_mac_list)
    
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
