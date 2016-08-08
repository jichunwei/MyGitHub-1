# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure Hotspot:
13.1    Sets the Hotspot entry name.
13.2    Sets the Login Page Url.
13.3    Redirect to the URL that the user intends to visit./or Redirect to the following URL.
13.4    Disables Session Timeout.
13.5    Enables and Sets Session Timeout time.
13.6    Disables Idle Timeout.
13.7    Enables and Sets Idle Timeout time.
13.8    Sets Authentication Server into local.
13.9    Sets Authentication Server.
13.10    Disables Accounting Server.
13.11    Sets Accounting Server.
13.12    Sets Location ID.
13.13    Sets Location Name.
13.14    Sets Wall Garden Url1.
13.15    Sets Wall Garden Url2.
13.16    Sets Wall Garden Url3.
13.17    Sets Wall Garden Url4.
13.18    Deletes a restrict access order.
13.19    Creates a new restrict access order or modifies an existing restrict access order.

Note:
Please update the upgrade configuration for test case upgrade to new build

Update @2011-9-15, by cwang@ruckuswireless.com  
Update content:
    Add simple data plane and make sure it works.
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def _get_wlan():
    return dict( name = "RAT-Open-None-CLI-Testing",
                 ssid = "RAT-Open-None-CLI-Testing", 
                 auth = "open", 
                 encryption = "none", 
                 type = 'hotspot',
                 hotspot_name = 'Test_Hotspot_CLI'
                 )

def _get_auth_info():
    return {'name':'local.username',
            'password':'local.password'}

def build_setup_env():
    test_cfgs = []
    test_cfgs.append((_get_auth_info(),
                      'CB_ZD_CLI_Create_Users',
                      'Create a User from CLI',
                      1, 
                      False
                      ))
        
    
    test_cfgs.append(({'wlan_conf' : _get_wlan()},
                      'CB_ZD_CLI_Create_Wlan',
                      'Create a WLAN from CLI',
                      1, 
                      False
                      ))
    
    return test_cfgs

def build_cls_env():
    test_cfgs = []
    test_cfgs.append(({'name':'RAT-Open-None-CLI-Testing'},
                       'CB_ZD_CLI_Remove_Wlan_Configuration',
                       'Remove WLAN from CLI',
                       0, 
                       False
                     ))
    test_cfgs.append(({'name':'local.user'},
                      'CB_ZD_CLI_Delete_User',
                      'Remove User from CLI',
                      0,
                      False
                      ))
    return test_cfgs

def build_asso_sta(sta = '192.168.1.11'):
    test_cfgs = []
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': sta}, 
                       'CB_ZD_Create_Station', 
                       'Get the station', 
                       1, 
                       False))
               
    
    test_cfgs.append(({'sta_tag': 'sta_1', 
                       'wlan_cfg': _get_wlan()}, 
                      'CB_ZD_Associate_Station_1', 
                      'Associate the station', 
                      1, 
                      False))    

    
    test_cfgs.append(({'sta_tag': 'sta_1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'Get wifi address', 
                      1, 
                      False))
    
    
    test_cfgs.append(({'sta_tag': 'sta_1'},
                      'CB_Station_CaptivePortal_Start_Browser',
                      'Open authentication web page',
                      2,
                      False,
                      ))
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'disallowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       '[Hotspot testing in station]The station ping a target IP before auth', 
                       2, 
                       False))
    return test_cfgs

def build_redirect_sta(auth_info = {'username': 'local.username', 
                                    'password': 'local.password'}):
    test_cfgs = []
    param_cfgs = {'sta_tag':'sta_1'}
    param_cfgs.update(auth_info)
    test_cfgs.append((param_cfgs, 
                      'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                      '[Hotspot testing in station]Perform Hotspot authentication', 
                      2, 
                      False))
    return test_cfgs

def build_chk_sta():
    test_cfgs = []
    test_cfgs.append(({'sta_tag':'sta_1'},
                      'CB_Station_CaptivePortal_Download_File',
                      '[Hotspot testing in station]Download files from server',
                      2,
                      False
                     ))
    
    test_cfgs.append(({'sta_tag': 'sta_1',
                       'condition': 'allowed',
                       'target_ip': '172.126.0.252',},
                       'CB_ZD_Client_Ping_Dest', 
                       '[Hotspot testing in station]The station ping a target IP after auth', 
                       2, 
                       False))
    
    test_cfgs.append(({'sta_tag':'sta_1'},
                      'CB_Station_CaptivePortal_Quit_Browser',
                      'Close Authentication browser',
                      2,
                      False,
                      ))
    return test_cfgs
    

def build_tcs(sta):
    test_cfgs = []
    test_name = 'CB_ZD_CLI_Configure_Hotspot'    
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True}, 
                      test_name, common_name, 0, False))
    
    
    
    common_name = '[Set the Hotspot entry name]create hotspot'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'login_page_url': 
                                        'http://192.168.0.250/login.html'}}, 
                                        test_name, common_name, 1, False))
            
    
    common_name = '[Set the Login Page Url]config login page'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'login_page_url': 
                                        'http://192.168.0.250/login.html'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set redirect URL]Redirect to the URL that the user intends to visit'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'start_page': 'http://172.16.10.252/'
                                       }}, test_name, common_name, 1, False))
    
    
    #@author: Liang Aihua, @change: Remove these steps not exist in database(2014-11-18)
    #test_cfgs.extend(build_setup_env())
    #test_cfgs.extend(build_asso_sta(sta))
    #test_cfgs.extend(build_redirect_sta())
    #test_cfgs.extend(build_chk_sta())
          
    
    common_name = '[Set session timeout]Disables Session Timeout'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'session_timeout': 'Disabled'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set session timeout]Enables and Sets Session Timeout time'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'session_timeout': '120'}}, 
                                        test_name, common_name, 2, False))
    
    common_name = '[Set idle timeout]Disables Idle Timeout'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'idle_timeout': 'Disabled'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set idle timeout]Enables and Sets Idle Timeout time'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'idle_timeout': '120'}}, 
                                        test_name, common_name, 2, False))
    
    server_list = [{'type':'radius-auth',
                        'server_name': 'RADIUS',
                        'server_addr': '192.168.0.252',
                        'radius_secret': '1234567890',
                        'server_port': '18120'
                        },        
                        {'type':'radius-acct',
                        'server_name': 'RADIUS Accounting',
                        'server_addr': '192.168.0.252',
                        'radius_secret': '1234567890',
                        'server_port': '18130'
                        }]
    server_name_list = [svr['server_name'] for svr in server_list]
    
    test_cfgs.append(({'server_cfg_list':server_list},
                      'CB_ZD_CLI_Configure_AAA_Servers',
                      '[set auth server]Configure AAA Server',
                      1,
                      False
                      ))
    
    common_name = '[Set auth server]Sets Authentication Server into local'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'authentication_server': 'Local Database'}}, 
                                        test_name, common_name, 2, False))
        
  
    
    common_name = '[Set auth server]Set Authentication Server'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'authentication_server': 'RADIUS',
                                        'by_pass': True}}, 
                                        test_name, common_name, 2, False))
    
    common_name = '[Set auth server]Disables Accounting Server'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'accounting_server': 'Disabled'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set auth server]Sets Accounting Server'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'accounting_server': 'RADIUS Accounting',
                                        'send_interim-update_time': '10'}}, 
                                        test_name, common_name, 2, False))
    
    common_name = '[Set location id]Sets Location ID'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'location_id': 'SDC'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set location name]Sets Location Name'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'location_name': 'Shenzhen Development Center'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set wall garden]Sets Wall Garden Url1'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'wall_garden_1': 'www.example.net'}}, 
                                        test_name, common_name, 1, False))
    
    common_name = '[Set wall garden]Sets Wall Garden Url2'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'wall_garden_2': '172.21.0.252'}}, 
                                        test_name, common_name, 2, False))
    
    common_name = '[Set wall garden]Sets Wall Garden Url3'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'wall_garden_3': '172.22.0.0/16'}}, 
                                        test_name, common_name, 2, False))
    
    common_name = '[Set wall garden]Sets Wall Garden Url4'
    test_cfgs.append(({'hotspot_conf': {'name': 'Test_Hotspot_CLI',
                                        'wall_garden_4': '172.23.0.252:8888'}}, 
                                        test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot_Restrict_Access'
    common_name = '[Set restrict access list]Creates a new restrict access order'
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                       }}, 
                                                       test_name, common_name, 1, False))
    
    common_name = '[Set restrict access list]Deletes a restrict access order'
    test_cfgs.append(({'test':'delete',
                       'hotspot_name': 'Test_Hotspot_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                       }}, 
                                                       test_name, common_name, 2, False))

    #test_cfgs.extend(build_cls_env())    
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True,
                       'hotspot_conf': {'name': 'Test_Hotspot_CLI'}}, 
                       test_name, common_name, 0, True))
            
    
    test_cfgs.append(({'server_name_list':server_name_list},
                     'CB_ZD_CLI_Delete_AAA_Servers',
                     'Remove AAA servers',
                     0,
                     True)
                     )

    return test_cfgs
  
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']    
    sta = testsuite.getTargetStation(sta_ip_list)                
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts_name = 'Configure Hotspot'
    #ts_name = 'Test ZDCLI Hotspot configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify the Hotspot setting by ZD CLI', combotest=True)
    test_cfgs = build_tcs(sta)

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
    createTestSuite(**_dict)
