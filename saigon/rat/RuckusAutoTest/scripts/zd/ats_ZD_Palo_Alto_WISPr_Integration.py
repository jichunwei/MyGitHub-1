import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:21.02.%02d" % tcid

def get_common_name(id, name):
    return "%s - %s" % (id, name)

def defineTestConfiguration(station, ap_mode, ap_sym_dict):
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    test_cfgs = []
    test_name = "ZD_Hotspot_Functionality"
    def_test_params = {'target_station': station, 'target_ip': '172.126.0.252',
                       'hotspot_cfg': {'login_page': 'http://192.168.0.250/login.html',
                                       'name': 'A Sampe Hotspot Profile'},
                       'auth_info': {'type':'local', 'username': 'local.username', 'password': 'local.password'}}

    # Integration test cases
    wlan_cfgs = []
    wlan_cfgs.append(({'auth': 'open', 'encryption': 'none'},
                      0, "Open System", "root"))
    wlan_cfgs.append(({'auth': 'open', 'encryption': 'WEP-64', 'key_index': '1' , 'key_string': utils.make_random_string(10,"hex")},
                      1, "Open WEP64 KEY1", "mesh"))
    wlan_cfgs.append(({'auth': 'PSK', 'wpa_ver':'WPA', 'encryption':'TKIP', 'key_string': utils.make_random_string(63,"alnum")},
                      2, "WPA PSK TKIP", "root"))
    wlan_cfgs.append(({'auth': 'PSK', 'wpa_ver':'WPA2', 'encryption':'AES', 'key_string': utils.make_random_string(63,"alnum")},
                      3, "WPA2 PSK AES", "mesh"))

    aps = {}
    aps['root'] = testsuite.getApByRole('root', ap_sym_dict)
    aps['mesh'] = testsuite.getApByRole('mesh', ap_sym_dict)
    try:
        if ap_mode == "l2":
            base_id = 1
            exp_subnet = "192.168.0.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_params = deepcopy(def_test_params)
                test_params.update({'wlan_cfg': wlan_cfg[0], 'expected_subnet': exp_subnet,
                                    'do_tunnel': True, 'active_ap': active_ap})
                test_cfgs.append((test_params, test_name,
                                  get_common_name(tcid(base_id+wlan_cfg[1]),
                                                  'Integrated with %s - %s - L2 tunnel' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 5
            vlan_id = "2"
            exp_subnet = "20.0.2.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_params = deepcopy(def_test_params)
                test_params.update({'wlan_cfg': wlan_cfg[0], 'expected_subnet': exp_subnet,
                                    'do_tunnel': True, 'active_ap': active_ap, 'vlan_id': vlan_id})
                test_cfgs.append((test_params, test_name,
                                  get_common_name(tcid(base_id+wlan_cfg[1]),
                                                  'Integrated with %s - %s - L2 tunnel - VLAN tagging' % (wlan_cfg[2], wlan_cfg[3].upper()))))
        else:
            base_id = 9
            exp_subnet = "192.168.0.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_params = deepcopy(def_test_params)
                test_params.update({'wlan_cfg': wlan_cfg[0], 'expected_subnet': exp_subnet,
                                    'do_tunnel': True, 'active_ap': active_ap})
                test_cfgs.append((test_params, test_name,
                                  get_common_name(tcid(base_id+wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 tunnel' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 13
            vlan_id = "2"
            exp_subnet = "20.0.2.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_params = deepcopy(def_test_params)
                test_params.update({'wlan_cfg': wlan_cfg[0], 'expected_subnet': exp_subnet,
                                    'do_tunnel': True, 'active_ap': active_ap, 'vlan_id': vlan_id})
                test_cfgs.append((test_params, test_name,
                                  get_common_name(tcid(base_id+wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 tunnel - VLAN tagging' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 17
            exp_subnet = "192.168.33.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_params = deepcopy(def_test_params)
                test_params.update({'wlan_cfg': wlan_cfg[0], 'expected_subnet': exp_subnet,
                                    'do_tunnel': False, 'active_ap': active_ap})
                test_cfgs.append((test_params, test_name,
                                  get_common_name(tcid(base_id+wlan_cfg[1]),
                                                  'Integrated with %s - %s - L3 w/o tunnel' % (wlan_cfg[2], wlan_cfg[3].upper()))))
            base_id = 21
            vlan_id = "2"
            exp_subnet = "20.0.2.0/255.255.255.0"
            for wlan_cfg in wlan_cfgs:
                active_ap = aps[wlan_cfg[3]].next()
                test_params = deepcopy(def_test_params)
                test_params.update({'wlan_cfg': wlan_cfg[0], 'expected_subnet': exp_subnet,
                                    'do_tunnel': False, 'active_ap': active_ap, 'vlan_id': vlan_id})
                test_cfgs.append((test_params, test_name,
                                  get_common_name(tcid(base_id+wlan_cfg[1]),
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
    ts_name = "WISPr integration - %s AP Mode" % ap_mode.upper()
    ts_desc = "Verify Hotspot/WISPr integration with Mesh/VLAN/Tunnelling - %s AP Mode" % ap_mode.upper()
    ts = testsuite.get_testsuite(ts_name, ts_desc)

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
