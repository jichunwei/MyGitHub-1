import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _tcid(mid, sid, description):
    return u'TCID:04.02.%02d.%02d - %s' % (mid, sid, description)

def defineTestConfiguration(tbcfg, attrs = {'interactive_mode':False}):
    serv_ip = testsuite.getTestbedServerIp(tbcfg)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]

    test_cfgs = []
    test_cfgs.append(({'target_station':target_sta, 'use_allow_acl':True, 'allow_station':True, 'ip':serv_ip, 'verify_acl':True},
                      _tcid(1, 1, "Create an allow ACL"),
                      "ZD_ACL_Policy",))
    test_cfgs.append(({'target_station':target_sta, 'use_allow_acl':True, 'allow_station':True, 'ip':serv_ip, 'verify_acl':False},
                      _tcid(1, 2, "A station matches an allow ACL has full access to the WLANs"),
                      "ZD_ACL_Policy",))
    test_cfgs.append(({'target_station':target_sta, 'use_allow_acl':True, 'allow_station':False, 'ip':serv_ip, 'verify_acl':False},
                      _tcid(1, 3, "A station doesn't match an allow ACL doesn't have access to the WLANs"),
                      "ZD_ACL_Policy",))
    test_cfgs.append(({'target_station':target_sta, 'use_allow_acl':False, 'allow_station':True, 'ip':serv_ip, 'verify_acl':True},
                      _tcid(2, 1, "Create a deny ACL"),
                      "ZD_ACL_Policy",))
    test_cfgs.append(({'target_station':target_sta, 'use_allow_acl':False, 'allow_station':False, 'ip':serv_ip, 'verify_acl':False},
                      _tcid(2, 2, "A station matches a deny ACL doesn't have access to the WLANs"),
                      "ZD_ACL_Policy",))
    test_cfgs.append(({'target_station':target_sta, 'use_allow_acl':False, 'allow_station':True, 'ip':serv_ip, 'verify_acl':False},
                      _tcid(2, 3, "A station doesn't match a deny ACL has full access to the WLANs"),
                      "ZD_ACL_Policy",))
    # default we will not import scalability/stress tests
    if tbcfg.has_key('doSSTests') and tbcfg['doSSTests']:
        test_cfgs.append(({'target_station':target_sta, 'verify_max_acls':True, 'max_entries':1024, 'ip':serv_ip},
                      _tcid(4, 0, "Create maximum number of ACLs"),
                      "ZD_ACL_Capacity",))
        test_cfgs.append(({'target_station':target_sta, 'verify_max_acls':False, 'max_entries':128, 'ip':serv_ip},
                      _tcid(5, 0, "Create maximum number of MAC entries within an ACL"),
                      "ZD_ACL_Capacity",))

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    mtb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    tbcfg.update(kwargs)
    test_cfgs = defineTestConfiguration(tbcfg, attrs)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "WLAN Options - ACL"
    ts = testsuite.get_testsuite(ts_name, 'Verify the ability of ZD to filter wireless clients based on ACL rules')

    test_order = 1
    test_added = 0
    
    for test_params, common_name, test_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

