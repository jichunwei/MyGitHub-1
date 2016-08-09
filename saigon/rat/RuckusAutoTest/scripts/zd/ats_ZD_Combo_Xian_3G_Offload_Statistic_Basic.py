'''
Doc@https://jira-wiki.ruckuswireless.com/display/Team/3G-offload+statistic
Topology:
    Zone Director----- L3 Switch --------AP  ))))))  Wireless Client

                             |

        DHCP/Radius Server/Win2003 web portal server

Created on 2012-10-31
@author: cwang@ruckuswireless.com
'''

from copy import deepcopy
import time
import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


hotspot_cfg = {'login_page': 'http://192.168.0.250/login.html',
               'name': 'wispr_test'}

auth_info = {'username': 'local.username', 'password': 'local.password'}

wlan_cfg = dict(ssid = "RAT-Open-None", 
                auth = "open", 
                encryption = "none", 
                type = 'hotspot',
                hotspot_profile = 'wispr_test',
#                ignore_unauth_stats = True,
                )

cfg_map = [( dict(ssid = "RAT-Open-None", 
                auth = "open", 
                encryption = "none", 
                type = 'hotspot',
                hotspot_profile = 'wispr_test',
                ignore_unauth_stats = True,
                ),
            '[Enable 3G Offload statistic]',
            {'before_sta':0,
             'after_sta':1,
             'cli':False
             }
            ),
            (dict(ssid = "RAT-Open-None", 
                auth = "open", 
                encryption = "none", 
                type = 'hotspot',
                hotspot_profile = 'wispr_test',
                ignore_unauth_stats = False,
                ),
            '[Disable 3G Offload statistic]',
            {'before_sta':1,
             'after_sta':1,
             'cli':False
             }
            ),                            
           ]


cfg_map_vlan = [
                ( dict(ssid = "RAT-Open-None-V20", 
                auth = "open", 
                encryption = "none", 
                type = 'hotspot',
                hotspot_profile = 'wispr_test',
                ignore_unauth_stats = True,
                vlan_id = '20'
                ),
                '[Enable 3G Offload statistic with VLAN 20]',
                {'before_sta':0,
                 'after_sta':1,
                 'cli':False
                 }
                ),
                ( dict(ssid = "RAT-Open-None-V20", 
                    auth = "open", 
                    encryption = "none", 
                    type = 'hotspot',
                    hotspot_profile = 'wispr_test',
                    ignore_unauth_stats = False,
                    vlan_id = '20'
                    ),
                '[Disable 3G Offload statistic with VLAN 20]',
                {'before_sta':1,
                 'after_sta':1,
                 'cli':False,
                 }
                ), 
                                            
            ]

cfg_map_cli = [(dict(name = "CLI-Open-None-V20",
                       ssid = "CLI-Open-None-V20", 
                    auth = "open", 
                    encryption = "none", 
                    type = 'hotspot',
                    hotspot_name = 'wispr_test',
                    ignore_unauth_stats = False,
                    vlan_id = '20'
                    ),
                '[Disable 3G Offload statistic with VLAN 20 at CLI]',
                {'before_sta':1,
                 'after_sta':1,
                 'cli':True
                 }
                ),  
                ( dict(name = "CLI-Open-None-V20",
                       ssid = "CLI-Open-None-V20", 
                    auth = "open", 
                    encryption = "none", 
                    type = 'hotspot',
                    hotspot_name = 'wispr_test',
                    ignore_unauth_stats = True,
                    vlan_id = '20'
                    ),
                '[Enable 3G Offload statistic with VLAN 20 at CLI]',
                {'before_sta':0,
                 'after_sta':1,
                 'cli':True
                 })
            ]

def _build_init_tcs(LEVEL=0):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Remove All WLAN Groups for cleanup ENV', 
            LEVEL, 
            False),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Clean all WLANs for cleanup ENV', 
            LEVEL, 
            False),            
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Remove all profiles', 
            LEVEL, 
            False),            
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Remove all AAA servers',
             LEVEL,
             False),
            ({},
             'CB_ZD_Remove_All_Users',
             'Remove all Users',
             LEVEL,
             False),              
            ]
    
    
def _build_tear_down_tcs(LEVEL=0):
    return [
            ({}, 
            'CB_ZD_Remove_All_Wlan_Groups', 
            'Delete All WLAN Groups for cleanup ENV', 
            LEVEL, 
            True),              
            ({}, 
            'CB_ZD_Remove_All_Wlans', 
            'Delete all WLANs for cleanup ENV', 
            LEVEL, 
            True),            
            ({}, 
            'CB_ZD_Remove_All_Profiles', 
            'Delete all profiles', 
            LEVEL, 
            True),            
            ({},
             'CB_ZD_Remove_All_Authentication_Server',
             'Delete all AAA servers',
             LEVEL,
             True),
            ({},
             'CB_ZD_Remove_All_Users',
             'Delete all Users',
             LEVEL,
             True),              
            ]


def build_basic_test(target_station, cfg):
    test_cfgs = []
    test_cfgs.extend(_build_init_tcs())
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       0, 
                       False))                
    
    test_cfgs.append(({'hotspot_profiles_list': [hotspot_cfg]},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create a hotspot',
                      0, 
                      False,                      
                      ))
    
    test_cfgs.append((auth_info,
                      'CB_ZD_Create_Local_User',
                      'Create a local user',
                      0, 
                      False,
                      ))
    
    for wlan, tcid, attr in cfg:
#        test_cfgs.append(({'ssid':wlan['ssid']},
#                          'CB_ZD_Remove_Wlan',
#                          '%sRemove wlan %s' % (tcid, wlan['ssid']),
#                          0,
#                          False
#                          ))
        
        if not attr.get('cli', False):
            test_cfgs.append(({'wlan_cfg_list':[wlan]},
                              'CB_ZD_Create_Wlans',
                              '%sCreate WLAN' % tcid,
                              0,
                              False
                              ))
        else:
 #           test_cfgs.append(({'ssid':wlan['ssid']}, #@auth:yuyanan #@since:2014-7-23 bug:zf-9067
 #                         'CB_ZD_Remove_Wlan',
 #                         '%sRemove wlan %s' % (tcid, wlan['ssid']),
 #                         0,
 #                         False
 #                         ))            
            test_cfgs.append(({'wlan_cfg_list':[wlan]},
                              'CB_ZD_CLI_Create_Wlans',
                              '%sCreate WLAN' % tcid,
                              0,
                              False
                              ))
        
        test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': wlan}, 
                      'CB_ZD_Associate_Station_1', 
                      '%sAssociate the station' % tcid, 
                      1, 
                      False))    

    
        test_cfgs.append(({'sta_tag': 'sta_1'}, 
                          'CB_ZD_Get_Station_Wifi_Addr_1', 
                          '%sGet wifi address' % tcid, 
                          2, 
                          False))
        
        test_cfgs.append(({'sta_tag': 'sta_1'},
                          'CB_Station_CaptivePortal_Start_Browser',
                          '%sOpen authentication web page' % tcid,
                          2,
                          False,
                          ))
                
        
        test_cfgs.append(({'wlan_name':wlan.get('ssid'),
                           'pause':90,
                           },
                          'CB_ZD_Get_WLAN_Info',
                          '%sGet WLAN information before auth' % tcid,
                          2,
                          False
                          ))
        val = attr.get('before_sta')
        test_cfgs.append(({'wlan_info':{'ssid':wlan.get('ssid'),
                                        'auth':wlan.get('auth'),
                                        'encryption': wlan.get('encryption'),
                                        'rxPkts':val,
                                        'rxBytes':val
                                       }},
                          'CB_ZD_Verify_WLAN_Info',
                          '%sVerfiy WLAN information before auth' % tcid,
                          2,
                          False
                          ))
        
        param_cfgs = {'sta_tag':'sta_1'}
        param_cfgs.update(auth_info)
        test_cfgs.append((param_cfgs, 
                          'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                          '%sPerform Hotspot authentication' % tcid, 
                          2, 
                          False)) 
        
        test_cfgs.append(({'sta_tag':'sta_1'},
                         'CB_Station_CaptivePortal_Download_File',
                         '%sDownload files from server' % tcid,
                         2,
                         False
                         ))
    
        test_cfgs.append(({'wlan_name':wlan.get('ssid'),
                           'pause':90,                           
                           },
                          'CB_ZD_Get_WLAN_Info',
                          '%sGet WLAN Information after auth' % tcid,
                          2,
                          False
                          ))
        
        val = attr.get('after_sta')            
        test_cfgs.append(({'wlan_info':{'ssid':wlan.get('ssid'),
                                        'auth':wlan.get('auth'),
                                        'encryption': wlan.get('encryption'),
                                        'rxPkts':val,
                                        'rxBytes':val
                                       }},
                          'CB_ZD_Verify_WLAN_Info',
                          '%sVerfiy WLAN information after auth' % tcid,
                          2,
                          False
                          ))
        
#        test_cfgs.append(({'ssid':wlan['ssid']},
#                          'CB_ZD_Remove_Wlan',
#                          '%sDelete up wlan %s' % (tcid, wlan['ssid']),
#                          0,
#                          True
#                          ))
        
        test_cfgs.append(({'sta_tag':'sta_1'},
              'CB_Station_CaptivePortal_Quit_Browser',
              '%sClose Authentication browser' % tcid,
              2,
              True,
              ))
        
        
    test_cfgs.extend(_build_tear_down_tcs())
    
    return test_cfgs

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "3G offload statistic basic",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
        
    if attrs["interactive_mode"]:        
        target_station = testsuite.getTargetStation(sta_ip_list, 
                                                    "Choose an wireless station: ")
    else:        
        target_station = sta_ip_list[attrs["target_station"][0]]
        
    ts_name_list = [('Xian-3G offload statistic basic', build_basic_test, cfg_map),                                                        
                    ('Xian-3G offload statistic basic-vlan', build_basic_test, cfg_map_vlan),
                    ('Xian-3G offload statistic basic-cli', build_basic_test, cfg_map_cli),
                    ]
    
    for ts_name, fn, cfg in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(target_station, cfg)
    
        test_order = 1
        test_added = 0
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
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

    
    