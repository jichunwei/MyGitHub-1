import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(tcid, ap_model_id, ap_role_id):
    return "TCID:%s.%02d.%s.%s" % (18.02, tcid, ap_model_id, ap_role_id)

def defineTestConfiguration(target_station, active_ap, ap_model_id, ap_role_id, ap_type):
    test_cfgs = []

    common_name = 'Block wireless client - MAC Authentication - %s' % ap_type
    test_cfgs.append(({'target_station':target_station, 'ip': '192.168.0.2',
                       'active_ap':active_ap, 'test_policy':'mac authentication',
                       'test_option':'block'},
                      'ZD_Client_Management', common_name, tcid(1, ap_model_id, ap_role_id)))

    common_name = 'Isolation - MAC Authentication - %s' % ap_type
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'authorized_station':target_station,
                                            'active_ap': active_ap,
                                            'testcase':'with-isolation'},
                      'ZD_MAC_Authentication', common_name, tcid(2, ap_model_id, ap_role_id)))

    common_name = 'L2 ACL - MAC Authentication - %s' % ap_type
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'target_station':target_station,
                                            'active_ap': active_ap,
                                            'dest_ip':'192.168.0.252',
                                            'testcase':'with-mac-authentication'},
                      'ZD_L2ACL_Integration', common_name, '18.02.03.01.%s.%s' % (ap_model_id, ap_role_id)))

    common_name = 'L3/L4 ACL - MAC Authentication - %s' % ap_type
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'target_station':target_station,
                                            'active_ap': active_ap,
                                            'dest_ip':'192.168.0.252',
                                            'testcase':'with-mac-authentication'},
                      'ZD_L3ACL_Integration', common_name, '18.02.03.02.%s.%s' % (ap_model_id, ap_role_id)))

    common_name = 'Rate Limiting - MAC Authentication - %s' % ap_type
    test_cfgs.append(({'auth_server_info': {'server_addr': '192.168.0.252',
                                            'server_port': '1812',
                                            'server_name': 'freeRadius',
                                            'radius_auth_secret': '1234567890'},
                                            'target_station':target_station,
                                            'active_ap': active_ap,
                                            'dest_ip':'192.168.0.252',
                                            'wlan_config_set':'mac_none'},
                      'ZD_MultiWlans_Rate_Limit_Integration', common_name, tcid(4, ap_model_id, ap_role_id)))

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
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs['interactive_mode']:
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
    ts_name = 'MAC Authentication Integration'
    if attrs['testsuite_name']: ts_name = attrs['testsuite_name']
    test_cfgs = []
    for active_ap in active_ap_list:
        active_ap_conf = ap_sym_dict[active_ap]
        ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
        ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
        ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
        test_cfgs.extend(defineTestConfiguration(target_sta, active_ap, ap_model_id, ap_role_id, ap_type))

    ts = testsuite.get_testsuite(ts_name, 'MAC Authentication Integration', interactive_mode = attrs["interactive_mode"])

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
