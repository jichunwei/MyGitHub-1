import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tsid, tcid):
    return "TCID:%s.%02d" % (tsid, tcid)

def defineTestConfiguration(active_ap_list):
    test_cfgs = []
    test_name = "ZD_LWAPP"
    tsid = "13.01"

    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l2", "discovery_method": "fixed-pri"},
                      tcid(tsid, 1),
                      "Discover ZD through fixed IP in L2LWAPP network"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l3", "discovery_method": "fixed-pri"},
                      tcid(tsid, 2),
                      "Discover ZD through fixed IP in L3LWAPP network"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l3", "discovery_method": "fixed-sec", "pre_conn_mode": "l3", "pre_discovery_method": "fix-pri"},
                      tcid(tsid, 3),
                      "Primary and Secondary fixed IP in L3LWAPP network"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l2", "discovery_method": ""},
                      tcid(tsid, 4),
                      "Discover ZD through L2LWAPP network"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l3", "discovery_method": "", "pre_conn_mode": "l3", "pre_discovery_method": ""},
                      tcid(tsid, 5),
                      "Discover ZD through L2LWAPP with AP registered to ZD through L3LWAPP before"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l3", "discovery_method": "dhcp"},
                      tcid(tsid, 6),
                      "Discover ZD through L3LWAPP DHCP option 43"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l3", "discovery_method": "dns"},
                      tcid(tsid, 8),
                      "Discover ZD through L3LWAPP DHCP option 15"))
    test_cfgs.append((test_name,
                      {"active_ap": "", "conn_mode": "l3", "discovery_method": "record", "pre_conn_mode": "l2", "pre_discovery_method": ""},
                      tcid(tsid, 16),
                      "The history record of ZD in AP"))

    # Distribute active AP to all the test cases
    idx = 0
    total_ap = len(active_ap_list)
    for test_cfg in test_cfgs:
        test_cfg[1]["active_ap"] = sorted(active_ap_list)[idx]
        idx = (idx + 1) % total_ap

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
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "L3LWAPP"

    test_cfgs = defineTestConfiguration(active_ap_list)
    ts = testsuite.get_testsuite(ts_name, "", interactive_mode = attrs["interactive_mode"])

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

