import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration():
    test_cfgs = []
    input_cfg = defineInputConfig()

    test_name = 'CB_RemoveZDAllConfig'
    common_name = 'Cleanup testing environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Create_Wlan_Groups'
    common_name = 'Create 10 WLAN Groups'
    test_cfgs.append(({'num_of_wgs':10},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create 3 authentication servers: LDAP, RADIUS and RADIUS Accounting'
    test_cfgs.append(({'auth_ser_cfg_list':[input_cfg['ldap_ser_cfg'], input_cfg['radius_ser_cfg'], input_cfg['accounting_ser_cfg']]},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create 3 WLANs: WEBAUTH(LDAP server), MAC-OPEN-NONE(RADIUS server) and EAP-WPA-TKIP(RADIUS Accounting)'
    test_cfgs.append(({'wlan_cfg_list': [input_cfg['webauth-ldap'], input_cfg['mac-open-none'], input_cfg['eap-wpa-tkip']]},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Guest_Pass_Printout'
    common_name = 'Import a valid guest pass printout'
    test_cfgs.append(({'guestpass_printout_cfg': [input_cfg['gp_print_cfg']]},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_L3_ACLs'
    common_name = 'Create 2 L3 ACLs: "Allow All" and "Deny All"'
    test_cfgs.append(({'l3_acl_cfgs': [input_cfg['l3acl_allow'], input_cfg['l3acl_deny']]},
                      test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Backup'
    common_name = 'Backup the current WLAN Groups configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN Groups configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Guest_Pass_Printout'
    common_name = 'Remove all non default GuestPass Printout'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_L3_ACLs'
    common_name = 'Remove all L3 ACLs configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore the configuration to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Verify_Wlan_Groups_Info'
    common_name = 'Verify if 10 WLAN Groups are restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Wlans_Info'
    common_name = 'Verify if WLANs are restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Authentication_Server_Info'
    common_name = 'Verify if all authentication servers are restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Guest_Pass_Printout_Info'
    common_name = 'Verify if all guest pass printouts are restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_L3_ACLs_Info'
    common_name = 'Verify if L3 ACLs are restored to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_RemoveZDAllConfig'
    common_name = 'Remove all configuration before upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Upgrade'
    common_name = 'Upgrade the ZD'
    #@author: An Nguyen: add to variable to test download build from server
    #@since: 16 July 2010
    test_cfgs.append(({'image_file_path': input_cfg['img_file_path'],
                       'build_stream': input_cfg['build_stream'],
                       'build_number': input_cfg['build_number']},
                      test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore the configuration to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_ZD_Verify_Wlan_Groups_Info'
    common_name = 'Verify if 10 WLAN Groups are restored to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Wlans_Info'
    common_name = 'Verify if WLANs are restored to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Authentication_Server_Info'
    common_name = 'Verify if all authentication servers are restored to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Guest_Pass_Printout_Info'
    common_name = 'Verify if all guest pass printouts are restored to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_L3_ACLs_Info'
    common_name = 'Verify if L3 ACLs are restored to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))
# -----------------------------------------------------------------------------------------------------
    test_name = 'CB_RemoveZDAllConfig'
    common_name = 'Remove all configuration to cleanup'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs

def defineInputConfig():
    test_conf = {'ldap_ser_cfg':{'server_name': 'LDAP',
                                 'server_addr': '192.168.0.252',
                                 'server_port': '389',
                                 'ldap_search_base':'dc=example,dc=net',
                                 'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
                                 'ldap_admin_pwd': 'lab4man1',},
                 'radius_ser_cfg':{'server_name': 'RADIUS',
                                   'server_addr': '192.168.0.252',
                                   'radius_auth_secret': '1234567890',
                                   'server_port': '1812'},
                 'accounting_ser_cfg':{'server_name': 'RADIUS Accounting',
                                       'server_addr': '192.168.0.252',
                                       'radius_acct_secret': '1234567890',
                                       'server_port': '1813'},
                 'eap-wpa-tkip': {'ssid':'EAP-WPA-TKIP', 'auth':'EAP', 'encryption':'TKIP',
                                  'wpa_ver':'WPA', 'auth_svr': 'RADIUS', 'acct_svr': 'RADIUS Accounting','type': None,
                                  'username':'ras.eap.user', 'password':'ras.eap.user',
                                  'use_radius': True, 'key_string': ''},
                 'webauth-ldap': {'ssid':'WEBAUTH-LDAP', 'auth':'open', 'encryption':'none',
                                  'wpa_ver':'', 'auth_svr': 'LDAP', 'type': None,
                                  'username':'test.ldap.user', 'password':'test.ldap.user',
                                  'do_webauth': True, 'key_string': ''},
                 'mac-open-none':{'ssid':'MAC-OPEN-NONE', 'auth':'mac', 'encryption':'none',
                                  'wpa_ver':'', 'auth_svr': 'RADIUS', 'type': None,
                                  'username':'ras.eap.user', 'password':'ras.eap.user',
                                  'use_radius': True, 'key_string': ''},
                 'gp_print_cfg':{'name':'New English', 'description': 'English version for English users',
                                 'html_file': 'C:\\Documents and Settings\\Anthony-Nguyen\\Desktop\\guestpass_print.html'},
                 'l3acl_allow':{'name':'L3 ACL ALLOW ALL', 'description': '','default_mode': 'allow-all', 'rules': []},
                 'l3acl_deny':{'name':'L3 ACL DENY ALL', 'description': '','default_mode': 'deny-all', 'rules': []},
                 # Please set the value for 3 variables below; if the "img_file_path" is set
                 # the build_stream and build_number will not be used.
                 'img_file_path': '',
                 'build_stream': '',
                 'build_number': '',
                 }

    return test_conf

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD_CB_Backup_Restore_Upgrade_With_Multi_Combination'
    ts = testsuite.get_testsuite(ts_name, 'Verify the function backup, restore and upgrade of ZD with multi-config combination', combotest=True)
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
