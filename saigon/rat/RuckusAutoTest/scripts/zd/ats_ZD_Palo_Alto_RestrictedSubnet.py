import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:22.03.%02d" % tcid

def get_common_name(id, name):
    return "%s - %s" % (id, name)

def defineTestConfiguration(station, ap_mode, ap_sym_dict):
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    test_cfgs = []
    test_name = 'ZD_GuestAccess_RestrictedSubnet_Enhancement'

    if ap_mode == "l2":
        # These test cases will be executed on the L2 test bed
        test_cfgs.append(({'target_station': station, 'test_case': 'create-acl'}, test_name,
                          get_common_name(tcid(1), 'Add a new access control rule')))
        test_cfgs.append(({'target_station': station, 'test_case': 'edit-acl'}, test_name,
                          get_common_name(tcid(2), 'Edit an existing access control rule')))
        test_cfgs.append(({'target_station': station, 'test_case': 'clone-acl'}, test_name,
                          get_common_name(tcid(3), 'Clone an existing access control rule to a new one')))
        test_cfgs.append(({'target_station': station, 'test_case': 'remove-acl'}, test_name,
                          get_common_name(tcid(4), 'Remove an existing access control rule')))
        test_cfgs.append(({'target_station': station, 'test_case': 'maximum-acl', 'number_of_acl': 22}, test_name,
                          get_common_name(tcid(5), 'Create maximum guest access control rules (22)')))
        test_cfgs.append(({'target_station': station, 'test_case': 'all-acl'}, test_name,
                          get_common_name(tcid(6), 'Verify all guest access control rule combinations')))

        # Distribute active AP to all the test cases
        idx = 0
        total_ap = len(active_ap_list)
        for test_cfg in test_cfgs:
            test_cfg[0]['active_ap'] = sorted(active_ap_list)[idx]
            idx = (idx + 1) % total_ap

    # Integration test cases
    wlan_cfgs = []
    wlan_cfgs.append(({'auth': 'open', 'encryption': 'none'},
                      0, "Open System", "root"))
    wlan_cfgs.append(({'auth': 'open', 'encryption': 'WEP-64', 'key_index': '1' , 'key_string': utils.make_random_string(10, "hex")},
                      1, "Open WEP64 KEY1", "mesh"))
    wlan_cfgs.append(({'auth': 'PSK', 'wpa_ver':'WPA', 'encryption':'TKIP', 'key_string': utils.make_random_string(63, "alnum")},
                      2, "WPA PSK TKIP", "root"))
    wlan_cfgs.append(({'auth': 'PSK', 'wpa_ver':'WPA2', 'encryption':'AES', 'key_string': utils.make_random_string(63, "alnum")},
                      3, "WPA2 PSK AES", "mesh"))

    aps = {}
    aps['root'] = testsuite.getApByRole('root', ap_sym_dict)
    aps['mesh'] = testsuite.getApByRole('mesh', ap_sym_dict)
    
    try:
        if ap_mode == "l2":
            base_id = 7
            exp_subnet = "192.168.0.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_cfgs.append(({'target_station': station, 'test_case': 'integration', 'do_tunnel': True,
                                   'wlan_cfg':wlan_cfg[0], 'active_ap': active_ap, 'expected_subnet': exp_subnet},
                                  test_name,
                                  get_common_name(tcid(base_id + wlan_cfg[1]),
                                                  'Integrated with %s - %s - L2 tunnel' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 11
            vlan_id = "2"
            exp_subnet = "20.0.2.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_cfgs.append(({'target_station': station, 'test_case': 'integration', 'do_tunnel': True,
                                   'wlan_cfg':wlan_cfg[0], 'active_ap': active_ap, 'expected_subnet': exp_subnet, 'vlan_id': vlan_id},
                                  test_name,
                                  get_common_name(tcid(base_id + wlan_cfg[1]),
                                                  'Integrated with %s - %s - L2 tunnel - VLAN tagging' % (wlan_cfg[2], wlan_cfg[3].upper()))))
        else:
            base_id = 15
            exp_subnet = "192.168.0.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_cfgs.append(({'target_station': station, 'test_case': 'integration', 'do_tunnel': True,
                                   'wlan_cfg':wlan_cfg[0], 'active_ap': active_ap, 'expected_subnet': exp_subnet},
                                  test_name,
                                  get_common_name(tcid(base_id + wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 tunnel' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 19
            vlan_id = "2"
            exp_subnet = "20.0.2.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_cfgs.append(({'target_station': station, 'test_case': 'integration', 'do_tunnel': True,
                                   'wlan_cfg':wlan_cfg[0], 'active_ap': active_ap, 'expected_subnet': exp_subnet, 'vlan_id': vlan_id},
                                  test_name,
                                  get_common_name(tcid(base_id + wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 tunnel - VLAN tagging' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 23
            exp_subnet = "192.168.33.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_cfgs.append(({'target_station': station, 'test_case': 'integration',
                                   'wlan_cfg':wlan_cfg[0], 'active_ap': active_ap, 'expected_subnet': exp_subnet},
                                  test_name,
                                  get_common_name(tcid(base_id + wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 w/o tunnel' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 27
            vlan_id = "2"
            exp_subnet = "20.0.2.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_cfgs.append(({'target_station': station, 'test_case': 'integration',
                                   'wlan_cfg':wlan_cfg[0], 'active_ap': active_ap, 'expected_subnet': exp_subnet, 'vlan_id': vlan_id},
                                  test_name,
                                  get_common_name(tcid(base_id + wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 w/o tunnel - VLAN tagging' % (wlan_cfg[2], wlan_cfg[3].upper()))))
    except StopIteration:
        raise Exception("There is no mesh/root APs in the test bed")

    return test_cfgs


def make_test_suite(**kwargs):
    tbi = testsuite.getTestbed2(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    target_sta = testsuite.getTargetStation(tb_cfg['sta_ip_list'])
    ap_sym_dict = tb_cfg["ap_sym_dict"]

    if "l2" in tbi.name: ap_mode = "l2"
    elif "l3" in tbi.name: ap_mode = "l3"
    else: raise Exception("Unexpected test bed name. It should be 'l2.mesh.fanout' or 'l3.mesh.fanout'")

    test_cfgs = defineTestConfiguration(target_sta, ap_mode, ap_sym_dict)
    ts_name = "Guest WLAN Access Control - %s AP Mode" % ap_mode.upper()
    ts = testsuite.get_testsuite(ts_name, "Verify the ACL rules in guest access WLANs")

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

