# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure Guest Access:
12.1    Sets the Guest Access rule order.
12.2    Sets the Guest Access rule description.
12.3    Sets the Guest Access rule type to 'allow'.
12.4    Sets the Guest Access rule type to 'deny'.
12.5    Sets the destination address of an Guest Access rule.
12.6    Sets the destination port of an Guest Access rule.
12.7    Sets the protocol of an Guest Access rule.

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
    target_url = 'http://www.example.net'
    username = 'rat.guest.localuser'
    password = 'rat.guest.localuser'
    wlan_name = "rat-wlan-guestaccess-%s" % (time.strftime("%H%M%S"))
    wlan_conf = {'name': wlan_name,
                 'ssid': wlan_name,
                 'auth': "open",
                 'encryption': "none",
                 'type': 'guest',
                 'do_tunnel': False,
                 #@author: liangaihua,@since: 2015-2-11,@change: add a new param not to configure guest profile when creating wlan
                 'create_guest_profile':False
                 }
    guest_policy = {'Auth/TOU/Redirection': {'guestaccess_policy_cfg': dict(enable_share_guestpass = False,
                                                                            use_guestpass_auth = True,
                                                                            use_tou =False,
                                                                            #@author: liang aihua,@since: 2015-1-26,@change: disable for zf-11793, will set to "True" after zf-11793 resolved.
                                                                            #use_tou = True,
                                                                            redirect_url = 'http://172.16.10.252/'),
                                             'guestpass_policy_cfg': dict(auth_serv = "Local Database",
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
                                                                            auth_ser = 'Local Database',
                                                                            username = username,
                                                                            password = password),
                                                },
                    }

    test_name = 'CB_ZD_CLI_Configure_Guest_Restrict_Access'
    
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True}, test_name, common_name, 0, False))
    
    common_name = '[Rule Order]Sets the Guest Access rule order'
    test_cfgs.append(({'guest_restrict_conf': {'order': '2'}}, test_name, common_name, 1, False))
    
    common_name = '[Rule Description]Sets the Guest Access rule description'
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'description': 'Guest restrict access rule 1',
                                              }}, test_name, common_name, 1, False))
    
    common_name = '[Rule Type]Sets the Guest Access rule type to "allow"'
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'type': 'allow'}}, test_name, common_name, 1, False))
    
    common_name = '[Rule Type]Sets the Guest Access rule type to "deny"'
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'type': 'deny',
                                              }}, test_name, common_name, 1, False))
    
    common_name = '[Destination Address]Sets the destination address of an Guest Access rule'
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'destination_address': '172.16.10.0/24'}}, test_name, common_name, 1, False))
    
    common_name = "[Destination Port]Sets the destination port of an Guest Access rule to deny 'any'"
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'destination_port': 'any'}}, test_name, common_name, 1, False))
    tcid = "[Rule Protocol]"
    common_name = "%sSets the protocol of an Guest Access rule to deny 'ICMP(1)'" %tcid
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'protocol': '1',
                                              }}, test_name, common_name, 1, False))
 
    test_name = 'CB_ZD_CLI_Create_Users'
    common_name = '%sCreates the guest user via CLI' %tcid
    test_cfgs.append(({'name': username, 'password': password}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = '%sSet the guest-access policy via GUI' %tcid
    test_params = guest_policy['Auth/TOU/Redirection']['guestaccess_policy_cfg']
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = '%sCreates the guest wlan via CLI' %tcid
    test_cfgs.append(({'wlan_conf': wlan_conf}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = '%sCreates the station' %tcid
    test_params = {'sta_tag': 'sta1', 'sta_ip_addr': sta_ipaddr}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate the guestpass by the guest user'%tcid
    test_params = guest_policy['Auth/TOU/Redirection']['generate_guestpass_cfg']
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sStation associated the guest wlan' %tcid
    test_params = {'sta_tag': 'sta1', 'wlan_cfg': wlan_conf}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet the station Wifi addresses'%tcid
    test_params = {'sta_tag': 'sta1'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Station_Verify_Client_Unauthorized'
    common_name = '%sVerify the station info which is unauthorized via GUI' %tcid
    test_params = {'sta_tag': 'sta1', 'check_status_timeout': 10000}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_GuestAccess_Policy'
    common_name = '%sVerify the guest access policy via GUI'%tcid
    test_params = guest_policy['Auth/TOU/Redirection']['guestaccess_policy_cfg']
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #@author: Liang Aihua,@change: Remove redundant steps.
    #test_name = 'CB_ZD_Verify_GuestPass_Policy'
    #common_name = 'Verify the guest pass policy via GUI'
    #test_params = guest_policy['Auth/TOU/Redirection']['guestpass_policy_cfg']
    #test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = "%sCreate the station's browser object" %tcid
    test_params = {'sta_tag': 'sta1'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = '%sPerform guest authentication' %tcid
    test_params = {'sta_tag': 'sta1', 
                   'no_auth': False, 
                   'use_tou': False,
                   #@author: liang aihua,@since: 2015-1-26,@change: disable for zf-11793, will set to "True" after zf-11793 resolved.
                   #'use_tou': True, 
                   'target_url': target_url, 
                   'redirect_url': guest_policy['Auth/TOU/Redirection']['guestaccess_policy_cfg']['redirect_url'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    common_name = '%sVerify the station info which is authorized via GUI' %tcid
    test_params = {'sta_tag': 'sta1', 
                   'username': guest_policy['Auth/TOU/Redirection']['generate_guestpass_cfg']['guest_fullname'], 
                   'check_status_timeout': 10000}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "%sPing the restrict subnet_ip[%s] disallow, even if the satus is authorized" % (tcid, dest_ip)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = '%sDownload the file allowed from the dest url to the station, when the order is deny ICMP(1)' %tcid
    test_params = {'sta_tag': 'sta1'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    #@author: Liang Aihua,@since: 2015-1-13,@change: no test_name, so add correct test_name
    test_name = "CB_ZD_CLI_Configure_Guest_Restrict_Access"
    common_name = '%sSets the Guest Access rule type to "allow"'%tcid
    test_cfgs.append(({'guest_restrict_conf': {'order': '2',
                                               'type': 'allow'}}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip[%s] allowed after edited to the allow type in the order' % (tcid, dest_ip)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = '%sDownload the file allowed from the dest url to the station, when the order is allowed ICMP(1)' %tcid
    test_params = {'sta_tag': 'sta1'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = "%sClosed the station's browser object"%tcid
    test_params = {'sta_tag': 'sta1'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the guest wlan from station' % tcid
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = "%sRemove the guest wlan from zd"%tcid
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = '%sRemove all users from ZD GUI after test'%tcid  
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Restrict_Access' 
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True,
                       'guest_restrict_conf': {'order': '2'}}, test_name, common_name, 0, True))

    return test_cfgs
  
def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']

    ts_name = 'Configure Guest Restrict Access'
    ts = testsuite.get_testsuite(ts_name, 'Verify the Guest Restrict Access setting by ZD CLI', combotest=True)
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
