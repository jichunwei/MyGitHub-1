import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tsid, tcid):
    return "TCID:%s.%02d" % (tsid, tcid)

def defineTestConfiguration():
    test_cfgs = []
    test_name = "ZD_Admin_Authentication"
    tsid = "15.01"

    test_cfgs.append((test_name,
                      {"auth_type":"ad", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"389", "auth_srv_info":"rat.ruckuswireless.com",
                       "external_username":"ad.user", "external_password":"ad.user",
                       "group_attribute":"0123456789012345678901234567890123456789012345678901234567890123"},
                      tcid(tsid, 1), "Group Attribute Length"))
    test_cfgs.append((test_name,
                      {"auth_type":"local", "local_username":"zd.admin", "local_password":"zd.admin"},
                      tcid(tsid, 2), "AdminAuth - None"))
    test_cfgs.append((test_name,
                      {"auth_type":"ad", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"389", "auth_srv_info":"rat.ruckuswireless.com",
                       "external_username":"ad.user", "external_password":"ad.user",
                       "group_attribute":"0123456789", "enable_fallback":False},
                      tcid(tsid, 3), "AdminAuth - AD"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.252", "auth_srv_port":"1812", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789", "enable_fallback":False},
                      tcid(tsid, 4), "AdminAuth - RAS"))
    test_cfgs.append((test_name,
                      {"auth_type":"ad", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"389", "auth_srv_info":"rat.ruckuswireless.com",
                       "external_username":"ad.user", "external_password":"ad.user",
                       "group_attribute":"0123456789", "enable_fallback":True},
                      tcid(tsid, 5), "AdminAuth - AD with fallback"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.252", "auth_srv_port":"1812", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789", "enable_fallback":True},
                      tcid(tsid, 6), "AdminAuth - RAS with fallback"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789", "zd_admin_priv":"full"},
                      tcid(tsid, 7), "Full privileges"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789", "zd_admin_priv":"limited"},
                      tcid(tsid, 8), "Limited privileges"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789", "verify_event_log":True},
                      tcid(tsid, 9), "Events"))
    test_cfgs.append((test_name,
                      {"auth_type":"ad", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"389", "auth_srv_info":"rat.ruckuswireless.com",
                       "external_username":"ad.user", "external_password":"ad.user",
                       "group_attribute":"0123456789"},
                      tcid(tsid, 10), "IOP - Windows 2003 AD"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789"},
                       tcid(tsid, 11), "IOP - Windows 2003 IAS"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.252", "auth_srv_port":"1812", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789"},
                       tcid(tsid, 12), "IOP - FreeRadius"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789"},
                       tcid(tsid, 13), "IOP - ACSv4.1"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.cisco.user", "external_password":"rad.cisco.user",
                       "group_attribute":"0123456789"},
                       tcid(tsid, 15), "Cisco A/V attribute (1 value list)"))
    test_cfgs.append((test_name,
                      {"auth_type":"radius", "auth_srv_addr":"192.168.0.250", "auth_srv_port":"18120", "auth_srv_info":"1234567890",
                       "external_username":"rad.ruckus.user", "external_password":"rad.ruckus.user",
                       "group_attribute":"abcdefghij"},
                       tcid(tsid, 16), "Ruckus A/V attribute (2 value list)"))

    return test_cfgs

def make_test_suite(**kwargs):
    ts_name = "AdminAuth"

    test_cfgs = defineTestConfiguration()
    ts = testsuite.get_testsuite(ts_name, "Verify administrator authentication using different authentication servers")

    test_order = 1
    test_added = 0
    for test_name, test_params, tcid, common_name in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)


