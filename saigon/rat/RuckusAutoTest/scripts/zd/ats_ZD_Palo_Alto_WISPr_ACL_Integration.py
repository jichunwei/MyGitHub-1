import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:22.04.%02d" % tcid

def get_common_name(id, name):
    return "%s - %s" % (id, name)

def defineTestConfiguration(station, ap_sym_dict):
    active_ap_list = sorted(testsuite.getActiveAp(ap_sym_dict))
    test_cfgs = []
    test_name = "ZD_Hotspot_Functionality"
    def_test_params = {'target_station': station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'A Sampe Hotspot Profile'},
                       'auth_info': {'type':'local', 'username': 'local.username', 'password': 'local.password'}}

    test_params = deepcopy(def_test_params)
    test_params.update({'acl_integration': True})
    test_cfgs.append((test_params, test_name,
                      get_common_name(tcid(1),"Test with L2 ACL")))

    test_params = deepcopy(def_test_params)
    test_params.update({'number_of_profile': 32})
    test_cfgs.append((test_params, test_name,
                      get_common_name(tcid(3),"Maximum Hotspot profile [32]")))

    # Distribute active AP to all the test cases
    idx = 0
    total_ap = len(active_ap_list)
    for test_cfg in test_cfgs:
        test_cfg[0]['active_ap'] = active_ap_list[idx]
        idx = (idx+1)%total_ap

    return test_cfgs

def make_test_suite(**kwargs):
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    target_sta = testsuite.getTargetStation(tb_cfg['sta_ip_list'])
    ap_sym_dict = tb_cfg["ap_sym_dict"]

    test_cfgs = defineTestConfiguration(target_sta, ap_sym_dict)
    ts_name = "ACL Integration WISPr"
    ts = testsuite.get_testsuite(ts_name, "")

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
