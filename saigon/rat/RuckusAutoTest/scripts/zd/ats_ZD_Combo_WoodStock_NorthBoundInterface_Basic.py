'''
+ZD-19132:enable/disable Northbound Interface by WebUI
+Do user-authenticate
+Do user-status-check
+Do user-unrestricted
Created on 2012-5-24
@author: cwang@ruckuswireless.com
'''
from copy import deepcopy

import time
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


#Configuration for test suites.
_base_cfg = {
        'req-password':'1234',              
        }

_aaa_cfg = {
        'server_name': 'freeradius',
        'server_addr': '192.168.0.252',
        'radius_auth_secret': '1234567890',
        'server_port': '1812',
        'auth_info': {'username': 'ras.local.user', 'password': 'ras.local.user',},        
        }

_hotspot_cfg = {
                'login_page': 'http://192.168.0.250/login.html',
                'name':       'northbound_interface_testing',
                'auth_svr':_aaa_cfg['server_name']
                }

_wlan_cfg = {
             'ssid':        'RAT-Open-None-NB',
             'auth':        'open',
             'encryption':  'none',
             'type':        'hotspot',
             'hotspot_profile': 'northbound_interface_testing',
             }

_wgs_cfg = {
            }

def init_tcs():
    return [({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup ENV', 
            0, 
            False),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup ENV', 
            0, 
            False),            
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles', 
            0, 
            False),            
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers',
             0,
             False)             
            ]

def clean_tcs():
    return [({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Clean All WLAN Groups for cleanup ENV', 
            0, 
            False),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Remove all WLANs for cleanup ENV', 
            0, 
            False),            
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Clean all profiles', 
            0, 
            False),            
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Clean all AAA servers',
             0,
             False)
            ]

def prepare(cfg, gui=True):
    tcs = []
    radio_mode = cfg['radio_mode']
    tcs.append((dict(auth_ser_cfg_list = [_aaa_cfg]),
                      'CB_ZD_Create_Authentication_Server',
                      'Create aaa server %s' % _aaa_cfg['server_name'],
                      0,
                      False,
                      ))
    
    tcs.append(({'hotspot_profiles_list': [_hotspot_cfg]},
                  'CB_ZD_Create_Hotspot_Profiles',
                  'Create a Hotspot %s' % _hotspot_cfg['name'],
                  0, 
                  False,                      
                  ))
    
    tcs.append(({'wlan_cfg_list':[_wlan_cfg]},
                  'CB_ZD_Create_Wlan',
                  'Create WLAN %s' % _wlan_cfg['ssid'],
                  0, 
                  False,
                  ))       
    
    tcs.append(({'cfg_type': 'init',
                 'all_ap_mac_list': None}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Config All APs Radio - Disable WLAN Service', 
                 0, 
                 False))
        
    tcs.append(({'active_ap':cfg['active_ap'],
                 'ap_tag': 'tap'}, 
                 'CB_ZD_Create_Active_AP', 
                 'Create active AP', 
                 0, 
                 False))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'sta_ip_addr': cfg['target_station'],
                 },
                'CB_ZD_Create_Station',
                'Find a station',
                0, 
                False
                ))
    
    tcs.append(({'cfg_type': 'config',
                 'ap_tag': 'tap',
                 'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                 }, 
                'CB_ZD_Config_AP_Radio', 
                'Config active AP Radio %s - Enable WLAN Service' % (radio_mode), 
                0, 
                False))
    
    if gui:
        tcs.append(({'enable':True,
                     'password':'1234',
                     },
                    'CB_ZD_Set_Northbound_Interface',
                    'Enable Northbound Interface',
                    0,
                    False
                    ))
    else:
        tcs.append(({'enable':True,
                     'password':'1234',
                     },
                    'CB_ZD_CLI_Set_Northbound_Interface',
                    'Enable Northbound Interface',
                    0,
                    False
                    ))
    
    tcs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': _wlan_cfg}, 
                      'CB_ZD_Associate_Station_1', 
                      'Associate the station', 
                      1, 
                      False))    

    
    tcs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get wifi address', 
                      1, 
                      False))
     
    param_cfg = {'wlan_cfg':_wlan_cfg, 
                 'chk_empty':False, 
                 'status':'Unauthorized',
                 'chk_radio':False,
                 'radio_mode':radio_mode,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',                 
                 }
    tcs.append((param_cfg,                        
                  'CB_ZD_Verify_Station_Info_V2',
                  'Verify the station before auth', 
                  2, 
                  False)) 
    
    tcs.append(({'sta_tag': 'sta_1',
                   'condition': 'disallowed',
                   'target_ip': '172.126.0.252',},
                   'CB_ZD_Client_Ping_Dest', 
                   'The station ping a target IP before auth', 
                   2, 
                   False))
    return tcs


def validate(cfg):
    tcs = []
    radio_mode = cfg['radio_mode']
    param_cfg = {'wlan_cfg':_wlan_cfg, 
                 'chk_empty':False, 
                 'status':'Authorized',
                 'chk_radio':False,
                 'radio_mode':radio_mode,
                 'sta_tag':'sta_1',
                 'ap_tag':'tap',  
                 'username': _aaa_cfg['auth_info']['username']         
                 }
    tcs.append((param_cfg,                        
                  'CB_ZD_Verify_Station_Info_V2',
                  'Verify the station After auth', 
                  2, 
                  False)) 
    
    tcs.append(({'sta_tag': 'sta_1',
                   'condition': 'allowed',
                   'target_ip': '172.126.0.252',},
                   'CB_ZD_Client_Ping_Dest', 
                   'The station ping a target IP after auth', 
                   2, 
                   False))
    return tcs


def post(gui=True):
    tcs = []
    if gui:
        tcs.append(({'enable':False,                     
                     },
                    'CB_ZD_Set_Northbound_Interface',
                    'Disable Northbound Interface',
                    0,
                    False
                    ))
    else:
        tcs.append(({'enable':False,                     
                     },
                    'CB_ZD_CLI_Set_Northbound_Interface',
                    'Disable Northbound Interface',
                    0,
                    False
                    ))        
    return tcs

def build_base_request_command_cli_tcs(cfg):
    tcs = []    
    tcs.extend(init_tcs())
    tcs.extend(prepare(cfg))
    tcs.append(({'cmd':'check-user-status',
                 'expected_code': '100',
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Check User Status-Client unauthorized]Validate User Status',
                1,
                False
                ))
    
    tcs.append(({'cmd':'user-authenticate',
                 'expected_code': '202',
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username'],
                            'password': _aaa_cfg['auth_info']['password']
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate]Validate User Info',
                1,
                False
                ))
    
    tcs.append(({'cmd':'check-user-status',
                #zj20140613 zf-7392
                 'expected_code': ['201','202',],
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Check User Status]Validate User Status',
                2,
                False
                ))
    
    tcs.extend(validate(cfg))
    
    tcs.append(({'cmd':'del-user',
                 'expected_code': '200',
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Delete User]Terminate User',
                2,
                False
                ))
    
    tcs.extend(post(gui=False))
    
    tcs.extend(clean_tcs())    
    return tcs

def build_base_request_command_tcs(cfg):
    tcs = []    
    tcs.extend(init_tcs())
    tcs.extend(prepare(cfg))
    tcs.append(({'cmd':'check-user-status',
                 'expected_code': '100',
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Check User Status-Client unauthorized]Validate User Status',
                1,
                False
                ))
    
    tcs.append(({'cmd':'user-authenticate',
                 'expected_code': '202',
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username'],
                            'password': _aaa_cfg['auth_info']['password']
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate]Validate User Info',
                1,
                False
                ))
    
    tcs.append(({'cmd':'check-user-status',
                 #zj20140613 zf-7392
                 'expected_code': ['202','201'],
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Check User Status]Validate User Status',
                2,
                False
                ))
    
    tcs.extend(validate(cfg))
    
    tcs.append(({'cmd':'del-user',
                 'expected_code': '200',
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Delete User]Terminate User',
                2,
                False
                ))
    
    tcs.extend(post(gui=True))
    
    tcs.extend(clean_tcs())
    
    return tcs
    
    
def build_bad_request_tcs(cfg):
    tcs = []
    tcs.extend(init_tcs())
    tcs.extend(prepare(cfg))
    tcs.append(({'expected_code': '303',                
                 'sta_tag': 'sta_1',
                 #chen.tao 2014-01-16 to fix ZF-6816
                 #'data': "<ruckus><version>2.0</version></ruckus>"
                 'data': "<ruckus><req-password>1234</req-password><version>2.0</version></ruckus>"
                 #chen.tao 2014-01-16 to fix ZF-6816
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with wrong version]303 Error',
                1,
                False
                ))
    
    tcs.append(({'expected_code': '302',                
                 'sta_tag': 'sta_1',
                 'data': "<ruckus><version>1.0</version/></ruckus>"
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with bad request]302 Error',
                1,
                False
                ))
    
    svr_cfg = deepcopy(_aaa_cfg)
    svr_cfg['server_addr'] = '192.168.0.10'#Un-reachable server.    
    tcs.append(({'old_name':_aaa_cfg['server_name'],
                 'auth_ser_cfg': svr_cfg
                 },
                'CB_ZD_Update_Authentication_Server',
                'Update AAA Server Profile to Wrong Configuration',
                1,
                False
                ))
    
    tcs.append(({'cmd':'user-authenticate',
                 #chen.tao 2014-01-06 to fix ZF-6821
                 'expected_code': '202',
                 #chen.tao 2014-01-06 to fix ZF-6821
                 'retries':10,
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username'],
                            'password': _aaa_cfg['auth_info']['password']
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                #chen.tao 2014-01-06 to fix ZF-6821
                '[User Authenticate with Radius Server error]202 Error',
                #chen.tao 2014-01-06 to fix ZF-6821
                2,
                False
                ))
    
    tcs.append(({'cmd':'check-user-status',
                 #zj20140613 zf-7392
                 'expected_code': ['401','100'],
                 'retries':5,
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with Radius Server error]Validate User Status',
                2,
                False
                )) 
    
    
    tcs.append(({'old_name':svr_cfg['server_name'],
                 'auth_ser_cfg': _aaa_cfg
                 },
                'CB_ZD_Update_Authentication_Server',
                'Update AAA Server Profile to Correct Configuration',
                1,
                False
                ))
    
    tcs.append(({'cmd':'user-authenticate',
                 'expected_code': '202',
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username'],
                            'password': _aaa_cfg['auth_info']['password']
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with Client authorized]client authenticate',
                2,
                False
                ))
    
    tcs.append(({'cmd':'check-user-status',
                 #zj20140613 zf-7392
                 'expected_code': ['201','101'],
                 'kwargs': {'req_password':_base_cfg['req-password'],                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with Client authorized]Validate User Status',
                2,
                False
                ))    
    
    tcs.append(({'cmd':'user-authenticate',
                 'expected_code': '101',
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username'],
                            'password': _aaa_cfg['auth_info']['password']
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with Client authorized]client authenticate - response 101 code',
                2,
                False
                ))
    
    tcs.append(({'cmd':'user-authenticate',
                 'expected_code': '300',
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username'],
                            'password': _aaa_cfg['auth_info']['password']
                            },
                  'sta_tag': 'sta_1',
                  'macaddr': '00:10:00:00:00:00'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[User Authenticate with wrong macaddr]client authenticate - response 300 code',
                2,
                False
                ))   
        
    tcs.extend(clean_tcs())
    
    return tcs


def build_unrestricted_mode_tcs(cfg):
    tcs = []
    tcs.extend(init_tcs())
    tcs.extend(prepare(cfg))
    tcs.append(({'cmd':'unrestricted',
                 'expected_code': '200',
                 'kwargs': {'req_password':_base_cfg['req-password'],
                            'name': _aaa_cfg['auth_info']['username']                            
                            },
                  'sta_tag': 'sta_1'
                 },
                'CB_WebPortal_Talk_With_Northbound_Interface',
                '[Unrestricted User]unrestricted user',
                2,
                False
                ))
    tcs.extend(validate(cfg))
    tcs.extend(clean_tcs())
    
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Woodstock Northbound Interface-Basic",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
        
    if attrs["interactive_mode"]:        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:        
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name            
            break
        
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)

    ts_name_list = [('Woodstock Northbound Interface-Basic', build_base_request_command_tcs),
                    ('Woodstock Northbound Interface-Basic-CLI', build_base_request_command_cli_tcs),
                    ('Woodstock Northbound Interface-Bad request', build_bad_request_tcs),
                    ('Woodstock Northbound Interface-Unrestricted', build_unrestricted_mode_tcs)
                    ]
    cfg = {}
    cfg['radio_mode'] = target_sta_radio
    cfg['active_ap'] = active_ap
    cfg['target_station'] = sta_ip_addr
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)
                
        test_cfgs = fn(cfg)
        
        test_order = 1
        test_added = 0
        check_validation(test_cfgs)
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 

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
