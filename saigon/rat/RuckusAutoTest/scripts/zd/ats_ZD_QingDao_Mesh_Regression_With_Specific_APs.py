import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(sub_id, tcid, ap_model_id, ap_role_id):
    return "TCID:33.%02d.%02d.%s.%s" % (sub_id, tcid, ap_model_id, ap_role_id)

def defineTestConfiguration(sub_id, root_ap, mesh_ap, ap_radio, ap_model_id, ap_role_id, ap_type):
    test_cfgs = []
    test_name = 'ZD_Mesh_Regression'
    common_name = 'Change RootAP channel for %sGhz - %s' % (ap_radio, ap_type)
    test_cfgs.append(({'active_ap':root_ap,'new_channel': '40', 'test_case': 'change_channel', 'mesh_ap': mesh_ap, 'ap_radio': ap_radio},
                      test_name, common_name, tcid(sub_id, 1, ap_model_id, ap_role_id)))

    common_name = 'Change MAP channel for %sGhz - %s' % (ap_radio, ap_type)
    test_cfgs.append(({'active_ap':mesh_ap,'new_channel': '40', 'root_ap': root_ap, 'test_case': 'change_channel', 'ap_radio': ap_radio},
                      test_name, common_name, tcid(sub_id, 2, ap_model_id, ap_role_id)))

    common_name = 'Tuning mesh with mesh ACL - %s' % (ap_type)
    test_cfgs.append(({'active_ap':mesh_ap, 'root_ap': root_ap, 'test_case': 'tuning_mesh_acl', 'ap_radio': ap_radio},
                      test_name, common_name, tcid(sub_id, 3, ap_model_id, ap_role_id)))

    return test_cfgs

def showNotice():
    msg = "Please select 2 APs are the same model for testing (separate by space)"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)


def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    sub_id = 6
    test_cfgs = []
    root_ap = active_ap_list[0]
    mesh_ap = active_ap_list[1]
    active_ap = root_ap

    if ap_sym_dict[active_ap]['model'].upper() == "ZF7962":
        ap_radio_frequency = "5.0"
    else:
        ap_radio_frequency = "2.4"

    active_ap_conf = ap_sym_dict[active_ap]
    ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
    ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
    ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
    test_cfgs.extend(defineTestConfiguration(sub_id, root_ap, mesh_ap, ap_radio_frequency, ap_model_id, ap_role_id, ap_type))

    ts_name = "Mesh regression"
    ts = testsuite.get_testsuite(ts_name, 'Regression test for Mesh feature')
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
