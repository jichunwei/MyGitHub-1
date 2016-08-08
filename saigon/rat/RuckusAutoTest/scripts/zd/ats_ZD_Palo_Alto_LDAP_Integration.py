import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration(target_station):
    test_cfgs = []

    test_name = 'ZD_GuestAccess'
    common_name = 'LDAP Integration Guest Pass'
    test_cfgs.append(({'auth_type':'ldap',
                       'auth_srv_addr':'192.168.0.252',
                       'auth_srv_port':'389',
                       'auth_srv_info':'dc=example,dc=net',
                       'ldap_admin_dn':'cn=Manager,dc=example,dc=net',
                       'ldap_admin_pwd': 'lab4man1',
                       'auth_username':'test.ldap.user', 'auth_password':'test.ldap.user',
                       'target_station':target_station, 'ip':'172.126.0.252',
                       'use_guest_auth': True, 'use_tou': True,
                       'redirect_url': 'http://www.example.net/',
                       },
                      test_name, common_name, '17.05.01'))

    test_name = 'ZD_Admin_Authentication'
    common_name = 'LDAP Integration Admin Authentication'
    test_cfgs.append(({'auth_type':'ldap',
                       'auth_srv_addr':'192.168.0.252',
                       'auth_srv_port':'389',
                       'auth_srv_info':'dc=example,dc=net',
        		       'ldap_admin_dn':'cn=Manager,dc=example,dc=net',
        		       'ldap_admin_pwd':'lab4man1',
                       'external_username':'test.ldap.user', 'external_password':'test.ldap.user',
                       'group_attribute':'ruckus'},
                      test_name, common_name, '17.06.01'))

    test_name = 'ZD_EncryptionTypesWebAuth'
    common_name = 'LDAP Integration Web Authentication'
    test_cfgs.append(({'auth_type':'ldap',
                       'auth_srv_addr':'192.168.0.252',
                       'auth_srv_port':'389',
                       'auth_srv_info':'dc=example,dc=net',
                       'ldap_admin_dn':'cn=Manager,dc=example,dc=net',
                       'ldap_admin_pwd': 'lab4man1',
                       'auth_username':'test.ldap.user', 'auth_password':'test.ldap.user',
                       'target_station':target_station, 'ip':'192.168.0.252',
                       },
                      test_name, common_name, '17.07.01'))

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]

    test_cfgs = defineTestConfiguration(target_sta)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'LDAP Integration'
    ts = testsuite.get_testsuite(ts_name, 'Verify LDAP Integration', interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
