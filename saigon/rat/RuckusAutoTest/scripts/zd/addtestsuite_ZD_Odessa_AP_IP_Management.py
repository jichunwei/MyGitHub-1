import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (13.04, tcid)

def defineTestConfiguration(active_ap):
    test_cfgs = []
    test_name = 'ZD_AP_IP_Management'

    common_name = 'Dynamic AP IP Assigned'
    test_cfgs.append(({'test_option':'dynamic', 'active_ap':active_ap}, test_name, common_name, tcid(1)))
    common_name = 'Manual AP IP Assigned through L2LWAPP'
    test_cfgs.append(({'test_option':'l2_manual', 'active_ap':active_ap}, test_name, common_name, tcid(2)))
    common_name = 'Manual AP IP Assigned through L3LWAPP'
    test_cfgs.append(({'test_option':'l3_manual', 'active_ap':active_ap}, test_name, common_name, tcid(3)))
    common_name = 'Invalid IP/Subnet/Gateway address'
    test_cfgs.append(({'test_option':'invalid_ip', 'active_ap':active_ap}, test_name, common_name, tcid(4)))

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    ap_sym_dict = tb_cfg["ap_sym_dict"]
    if attrs["interactive_mode"]:
        active_ap = testsuite.getActiveAp(ap_sym_dict)[0]
    else:
        if kwargs["targetap"]:
            active_ap = sorted(ap_sym_dict.keys())[0]

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'AP IP Management'
    test_cfgs = defineTestConfiguration(active_ap)
    ts = testsuite.get_testsuite(ts_name, 'Verify AP IP Management feature', interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)


