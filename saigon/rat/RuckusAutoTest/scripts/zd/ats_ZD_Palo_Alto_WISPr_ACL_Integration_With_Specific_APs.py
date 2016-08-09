import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(tcid, ap_model_id, ap_role_id):
    return "TCID:21.04.%02d.%s.%s" % (tcid, ap_model_id, ap_role_id)

def get_common_name(id, description, ap_type):
    return "%s - %s - %s" % (id, description, ap_type)

def defineTestConfiguration(station, ap_sym_dict, attrs):
    if attrs["interactive_mode"]:
        active_ap_list = sorted(testsuite.getActiveAp(ap_sym_dict))
    else:
        active_ap_list = sorted(ap_sym_dict.keys())
    test_cfgs = []
    test_name = "ZD_Hotspot_Functionality"
    def_test_params = {'target_station': station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'A Sampe Hotspot Profile'},
                       'auth_info': {'type':'local', 'username': 'local.username', 'password': 'local.password'}}

    test_params = deepcopy(def_test_params)
    test_params.update({'acl_integration': True})
    test_cfgs.append((test_params, test_name,
                      (1,"Test with L2 ACL")))

    test_params = deepcopy(def_test_params)
    test_params.update({'number_of_profile': 32})
    test_cfgs.append((test_params, test_name,
                      (3,"Maximum Hotspot profile [32]")))

    # Distribute active AP to all the test cases
    test_cfgs_list = []
    for active_ap in active_ap_list:
        active_ap_conf = ap_sym_dict[active_ap]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
        for test_cfg in test_cfgs:
            test_cfg[0]['active_ap'] = active_ap
            test_cfgs_list.append((test_cfg[0], test_cfg[1],
                                  get_common_name(tcid(test_cfg[2][0], ap_model_id, ap_role_id), test_cfg[2][1], ap_type)))

    return test_cfgs_list

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
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(tb_cfg['sta_ip_list'])
    else:
        target_sta = tb_cfg['sta_ip_list'][attrs["sta_id"]]
    ap_sym_dict = tb_cfg["ap_sym_dict"]

    test_cfgs = defineTestConfiguration(target_sta, ap_sym_dict, attrs)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "ACL Integration WISPr"
    ts = testsuite.get_testsuite(ts_name, "", interactive_mode = attrs["interactive_mode"])

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
