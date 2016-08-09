import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(tcid, ap_model_id, ap_role_id):
    return "TCID:%s.%02d.%s.%s" % (22.01, tcid, ap_model_id, ap_role_id)

def defineTestConfiguration(target_station, ap_sym_dict, attrs={}):
    test_cfgs = []
    test_name = 'ZD_L2ACL_Option'
    if attrs["interactive_mode"]:
        print '----------------------------------------------------------------'
        print 'Pick up APs that supports 2Ghz: '
        print '----------------------------------------------------------------'
        active_aps_2ghz = testsuite.getActiveAp(ap_sym_dict)
        print '----------------------------------------------------------------'
    else:
        active_aps_2ghz = []
        for ap in ap_sym_dict:
            #bugme.pdb.set_trace()
            if ap_sym_dict[ap]['model'] not in ['zf7962']:
                active_aps_2ghz.append(ap)

    for active_ap in active_aps_2ghz:
        active_ap_conf = ap_sym_dict[active_ap]
        common_name = 'Apply ACL on wlan for 2Ghz - %s' % testsuite.getApTargetType(active_ap, active_ap_conf)
        test_cfgs.append(({'target_station': target_station, 'testcase':'apply-to-wlan-for-2ghz', 'active_ap': active_ap},
                          test_name, common_name,
                          tcid(7, const.get_ap_model_id(active_ap_conf['model']), const.get_ap_role_by_status(active_ap_conf['status']))))

    if attrs["interactive_mode"]:
        print '----------------------------------------------------------------'
        print 'Pick up APs that supports 5Ghz: '
        print '----------------------------------------------------------------'
        active_aps_5ghz = testsuite.getActiveAp(ap_sym_dict)
        print '----------------------------------------------------------------'
    else:
        active_aps_5ghz = []
        for ap in ap_sym_dict:
            if ap_sym_dict[ap]['model'] not in ['zf7962']:
                active_aps_5ghz.append(ap)

    for active_ap in active_aps_5ghz:
        active_ap_conf = ap_sym_dict[active_ap]
        common_name = 'Apply ACL on wlan for 5Ghz - %s' % testsuite.getApTargetType(active_ap, active_ap_conf)
        test_cfgs.append(({'target_station': target_station, 'testcase':'apply-to-wlan-for-5ghz', 'active_ap': active_ap},
                          test_name, common_name,
                          tcid(6, const.get_ap_model_id(active_ap_conf['model']), const.get_ap_role_by_status(active_ap_conf['status']))))

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
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]

    test_cfgs = defineTestConfiguration(target_sta, ap_sym_dict, attrs)
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = 'L2 ACL'
    ts = testsuite.get_testsuite(ts_name, 'Verify L2 ACL Functionality', interactive_mode = attrs["interactive_mode"])

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
