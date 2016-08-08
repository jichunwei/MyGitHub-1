import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % (13.03, tcid)

def defineTestConfiguration(target_station):
    test_cfgs = []
    test_name = 'ZD_DHCPServer_Function'

    common_name = 'DHCP server only works in static IP address'
    test_cfgs.append(({'test_option':'dhcp server', 'target_station':target_station}, test_name, common_name, tcid(1)))
    common_name = 'Lease time testing'
    test_cfgs.append(({'test_option':'lease time', 'target_station':target_station}, test_name, common_name, tcid(3)))
    common_name = 'WebUI fields - enable/disable'
    test_cfgs.append(({'test_option':'enable/disable'}, test_name, common_name, tcid(6)))
    common_name = 'WebUI fields - Valid IP range'
    test_cfgs.append(({'test_option':'valid ip'}, test_name, common_name, tcid(7)))
    common_name = 'WebUI fields - View IP assignments'
    test_cfgs.append(({'test_option':'view ip assignments'}, test_name, common_name, tcid(8)))
    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'DHCPs'
    test_cfgs = defineTestConfiguration(target_sta)
    ts = testsuite.get_testsuite(ts_name, 'Test DHCP server options', interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

