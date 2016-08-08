# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure Guest Access:
11.1	Disables Authentication.
11.2	Allow or Disallow multiple users to share a single guest pass.
11.3	Do not show terms of use.
11.4	Enables and Sets the terms of use.
11.5	Redirect to the URL that the user intends to visit/ or Redirect to the following URL.
11.6	Sets Authentication Server.
11.7	Set Effective from the creation time/or Effective from first use, Expire new guest passes if not used with
11.8	Sets the Title.
11.9	Deletes a restrict access order.
11.10	Creates a new restrict access order or modifies an existing restrict access order.



Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def defineTestConfiguration():
    test_cfgs = []
    sta_ipaddr = '192.168.1.11'
    dest_ip = '172.16.10.252'
    target_url = 'http://172.16.10.252/'
    username = 'ras.local.user'
    password = 'ras.local.user'
    wlan_name = "rat-wlan-guestaccess-%s" % (time.strftime("%H%M%S"))
    wlan_conf = {'name': wlan_name,
                 'ssid': wlan_name,
                 'auth': "open",
                 'encryption': "none",
                 'type': 'guest',
                 'do_tunnel': False,
                 }
    guest_policy = {'Auth/TOU/No Redirection': {'guestaccess_policy_cfg': dict(enable_share_guestpass = True,
                                                                               use_guestpass_auth = True,
                                                                               use_tou = True,
                                                                               redirect_url = ''),
                                                'guestpass_policy_cfg': dict(auth_serv = "radius_server",
                                                                               is_first_use_expired = False,
                                                                               valid_day = '5'),
                                                'generate_guestpass_cfg': dict(type = "single",
                                                                               guest_fullname = "Guest-Auth",
                                                                               duration = "5",
                                                                               duration_unit = "Days",
                                                                               key = "",
                                                                               wlan = wlan_conf['ssid'],
                                                                               remarks = "",
                                                                               is_shared = "YES",
                                                                               auth_ser = '',
                                                                               username = username,
                                                                               password = password),
                                                },
                    }

    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True}, test_name, common_name, 0, False))
    
    common_name = '[Authentication]Disables Authentication'
    test_cfgs.append(({'guest_access_conf': {'authentication': 'No Authentication'}}, test_name, common_name, 1, False))
    
    #Modified by Liang Aihua on 2014-11-4 for this function not support any more.
    #common_name = 'Allow or Disallow multiple users to share a single guest pass'
    #test_cfgs.append(({'guest_access_conf': {'authentication': 'Use guest pass authentication',
    #                                          'multiple_users_to_share_a_single_guest_pass': 'Allowed'}}, test_name, common_name, 1, False))
    
    common_name = '[Terms of Use]Do not show terms of use'
    test_cfgs.append(({'guest_access_conf': {'terms_of_use': 'Disabled'}}, test_name, common_name, 1, False))
    
    common_name = '[Terms of Use]Enables and Sets the terms of use'
    test_cfgs.append(({'guest_access_conf': {'terms_of_use': 'Enabled',
                                              'terms': 'Test set term of use by CLI.'}}, test_name, common_name, 1, False))
    
    common_name = '[Redirect URL]Redirect to the URL that the user intends to visit'
    test_cfgs.append(({'guest_access_conf': {'redirection': 'To the URL that the user intends to visit'}}, test_name, common_name, 1, False))
    
    common_name = '[Sets Authentication Server]: Creates AAA Server via CLI'
    ptest_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    test_params = dict(server_cfg_list = [dict(server_name = 'radius_server', type = 'radius-auth', backup = False, 
                                        server_addr = '192.168.0.252', server_port = '1812', radius_secret = '1234567890')])
    test_cfgs.append((test_params, ptest_name, common_name, 1, False))
    
    common_name = '[Sets Authentication Server]: Sets Authentication Server'
    test_cfgs.append(({'guest_access_conf': {'authentication_server': 'radius_server'}}, test_name, common_name, 1, False))
    
    common_name = '[Effective Time]Set Effective from the creation time'
    test_cfgs.append(({'guest_access_conf': {'validity_period': 'Effective from first use',
                                              'expire_days': '10'}}, test_name, common_name, 1, False))
    
    common_name = '[Title]Sets the Title'
    test_cfgs.append(({'guest_access_conf': {'title': 'Welcome to CLI Guest Access Test'}}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Restrict_Access'
    common_name = '[Restricted Subnet Access]Creates a new restrict access order'
    test_cfgs.append(({'guest_restrict_conf': {'order': '2'}}, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_CLI_Create_Wlan'
    #common_name = 'Creates the guest wlan via CLI'
    #test_cfgs.append(({'wlan_conf': wlan_conf}, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Create_Station'
    #common_name = 'Creates the station'
    #test_params = {'sta_tag': 'sta1', 'sta_ip_addr': sta_ipaddr}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Generate_Guest_Pass'
    #common_name = 'Generate the guestpass by the guest user'
    #test_params = guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg']
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Associate_Station_1'
    #common_name = 'Station associated the guest wlan'
    #test_params = {'sta_tag': 'sta1', 'wlan_cfg': wlan_conf}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    #common_name = 'Get the station Wifi addresses'
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Station_Verify_Client_Unauthorized'
    #common_name = 'Verify the station info which is unauthorized via GUI'
    #test_params = {'sta_tag': 'sta1', 'check_status_timeout': 10000}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
            
    #test_name = 'CB_Station_Ping_Dest_Is_Denied'
    #common_name = 'Client ping dest-ip[%s] which is disallow before the guest auth' % dest_ip
    #test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    
    #test_name = 'CB_ZD_Verify_GuestAccess_Policy'
    #common_name = 'Verify the guest access policy via GUI'
    #test_params = guest_policy['Auth/TOU/No Redirection']['guestaccess_policy_cfg']
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #test_name = 'CB_ZD_Verify_GuestPass_Policy'
    #common_name = 'Verify the guest pass policy via GUI'
    #test_params = guest_policy['Auth/TOU/No Redirection']['guestpass_policy_cfg']
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #test_name = 'CB_Station_CaptivePortal_Start_Browser'
    #common_name = "Create the station's browser object"
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
        
    #test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    #common_name = 'Perform guest authentication'
    #test_params = {'sta_tag': 'sta1',
    #               'no_auth': False, 
    #               'use_tou': True,
    #               'target_url': target_url, 
    #               'redirect_url': '',
    #               }
    #test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    #test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    #common_name = "Closed the station's browser object"
    #test_params = {'sta_tag': 'sta1'}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    #common_name = 'Verify the station info which is authorized via GUI'
    #test_params = {'sta_tag': 'sta1',
    #               'username': guest_policy['Auth/TOU/No Redirection']['generate_guestpass_cfg']['guest_fullname'], 
    #               'check_status_timeout': 10000}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #test_name = 'CB_Station_Ping_Dest_Is_Denied'
    #common_name = "Ping the restrict subnet_ip[%s] disallow, even if the satus is authorized" % dest_ip
    #test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Restrict_Access'
    common_name = '[Restrict Subnet Access]Deletes a restrict access order'
    test_cfgs.append(({'test': 'delete',
                       'guest_restrict_conf': {'order': '2'}}, test_name, common_name, 1, False))
    
    #test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    #common_name = 'Ping the dest-ip[%s] allowed after deleted the restrict access order' % dest_ip
    #test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True}, test_name, common_name, 0, True))

    return test_cfgs
  
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts_name = 'Configure Guest Access'
    ts = testsuite.get_testsuite(ts_name, 'Verify the Guest Access setting by ZD CLI', combotest=True)
    test_cfgs = defineTestConfiguration()

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
