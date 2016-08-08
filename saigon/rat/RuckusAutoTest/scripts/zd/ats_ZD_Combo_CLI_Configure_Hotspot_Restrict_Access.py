# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure Hotspot Restrict Access:
12.1    Sets the Hotspot rule order.
12.2    Sets the Hotspot rule description.
12.3    Sets the Hotspot rule type to 'allow'.
12.4    Sets the Hotspot rule type to 'deny'.
12.5    Sets the destination address of an Hotspot rule.
12.6    Sets the destination port of an Hotspot rule.
12.7    Sets the protocol of an Hotspot rule.

Update @2011-9-20 by cwang@ruckuswireless.com
Add data plane for it.

Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _get_wlan():
    return dict( name = "RAT-Open-None-CLI-Hotspot",
                 ssid = "RAT-Open-None-CLI-Hotspot", 
                 auth = "open", 
                 encryption = "none", 
                 type = 'hotspot',
                 hotspot_name = 'Test_Hotspot_Restrict_Access_CLI'
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
    test_cfgs.append(({'name':'RAT-Open-None-CLI-Hotspot'},
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

    test_name = 'CB_ZD_CLI_Configure_Hotspot_Restrict_Access'
    
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True,
                       'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'login_page_url': 'http://192.168.0.250/login.html'}, 
                       test_name, common_name, 0, False))
    
    #@author: Liang Aihua,@change: Remove cases not exist in database(2014-11-18)
    #test_cfgs.extend(build_setup_env())
    #test_cfgs.extend(build_asso_sta(sta)) 
    #test_cfgs.append(({'sta_tag': 'sta_1',
    #                   'condition': 'disallowed',
    #                   'target_ip': '192.168.0.2',},
    #                   'CB_ZD_Client_Ping_Dest', 
    #                   'The station ping a target IP before auth', 
    #                   2, 
    #                   False))  
    #test_cfgs.extend(build_redirect_sta())
    #test_cfgs.extend(build_chk_sta())
    
    #@author: Liang Aihua, @change: Modify test case name(2014-11-18)
    #tcid = '[Testing Restrict Access as allow]'
    tcid = '[Restrict Access Configuration]'
    common_name = '%sSets the Hotspot rule order' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1'}}, test_name, common_name, 1, False))
    
    common_name = '%sSets the Hotspot rule description' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                 'description': 'Hotspot Restrict Access rule 2',
                                                }}, test_name, common_name, 2, False))
    
    common_name = '%sSets the Hotspot rule type to "allow"' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                 'type': 'allow'}}, test_name, common_name, 2, False))    
    
    #@author: Liang Aihua, @change: Remove these steps not exist in database(2014-11-18)       
    #test_cfgs.append(({'sta_tag': 'sta_1',
    #                   'condition': 'allowed',
    #                   'target_ip': '192.168.0.2',},
    #                   'CB_ZD_Client_Ping_Dest', 
    #                   '%sThe station ping a target IP after auth' % tcid, 
    #                   2, 
    #                   False))    
    
    #@author: Liang Aihua,@change: Remove this case name.
    #tcid = '[Testing Restrict Access as deny]'
    common_name = '%sSets the Hotspot rule type to "deny"' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                 'type': 'deny',
                                                }}, test_name, common_name, 2, False))
    
    common_name = '%sSets the destination address of an Hotspot rule' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                 'destination_address': '192.168.0.2/24'}}, test_name, common_name, 2, False))
    
    #@author: Liang Aihua,@change: Remove these step(2014-11-18)
    #test_cfgs.append(({'sta_tag': 'sta_1',
    #                   'condition': 'disallowed',
    #                   'target_ip': '192.168.0.2',},
    #                   'CB_ZD_Client_Ping_Dest', 
    #                   '%sThe station ping a target IP after auth' % tcid, 
    #                   2, 
    #                   False))
    
    common_name = '%sSets the destination port of an Hotspot rule' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                 'destination_port': '8080'}}, test_name, common_name, 2, False))
    
    common_name = '%sSets the protocol of an Hotspot rule' % tcid
    test_cfgs.append(({'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       'hotspot_restrict_access_conf': {'order': '1',
                                                 'protocol': 'any',
                                                }}, test_name, common_name, 2, False))
    
    
    #@author: Liang Aihua,@change: Remove these steps(2014-11-18)
    #test_cfgs.extend(build_cls_env())
    
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True,
                       'hotspot_name': 'Test_Hotspot_Restrict_Access_CLI',
                       }, test_name, common_name, 0, True))
    
    

    return test_cfgs
  
def create_ts(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']    
    sta = testsuite.getTargetStation(sta_ip_list)
    ts_name = 'Configure Hotspot Restrict Access'
    ts = testsuite.get_testsuite(ts_name, 'Verify the Hotspot Restrict Access setting by ZD CLI', combotest=True)
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
    create_ts(**_dict)
