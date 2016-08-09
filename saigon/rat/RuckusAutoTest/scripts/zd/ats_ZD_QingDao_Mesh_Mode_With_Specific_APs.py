import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(tcid, ap_model_id, ap_role_id):
    return "TCID:%s.%02d.%s.%s" % (30, tcid, ap_model_id, ap_role_id)

def defineTestConfiguration(active_ap, ap_model_id, ap_role_id, ap_type):
    test_cfgs = []
    test_name = 'ZD_AP_Mesh_Mode_Configuration'
    common_name = 'Mesh mode - Auto - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'testcase':'force-mesh-mode-to-auto'},
                      test_name, common_name, tcid(1, ap_model_id, ap_role_id)))

    common_name = 'Mesh mode - Root AP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'testcase':'force-mesh-mode-to-root'},
                      test_name, common_name, tcid(2, ap_model_id, ap_role_id)))

    common_name = 'Mesh mode - Mesh AP - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'testcase':'force-mesh-mode-to-mesh'},
                      test_name, common_name, tcid(3, ap_model_id, ap_role_id)))

    common_name = 'Mesh mode - Disable - %s' % ap_type
    test_cfgs.append(({'active_ap':active_ap, 'testcase':'force-mesh-mode-to-disabled'},
                      test_name, common_name, tcid(4, ap_model_id, ap_role_id)))

    return test_cfgs

def make_test_suite(**kwargs):
    #tbi = getTestbed(**kwargs)
    #tb_cfg = testsuite.getTestbedConfig(tbi)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    ts_name = 'Mesh Mode'

    test_cfgs = []
    for active_ap in active_ap_list:
        active_ap_conf = ap_sym_dict[active_ap]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
        test_cfgs.extend(defineTestConfiguration(active_ap, ap_model_id, ap_role_id, ap_type))

    ts = testsuite.get_testsuite(ts_name, 'Mesh Mode')

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
