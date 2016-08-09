import sys
import random
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def defineDefaultWlanConfiguration():
    wlan_cfg_list = dict()
    wlan_cfg_list['open-none'] = dict(
        auth = 'open',
        encryption = 'none',
        ssid = 'meshtree-open-none'
    )

    wlan_cfg_list['shared-wep64'] = dict(
        auth = 'shared',
        encryption = 'WEP-64',
        key_index = '1',
        key_string = utils.make_random_string(10,"hex"),
        ssid = 'meshtree-shared-wep64',
        vlan_id = '2'
    )

    wlan_cfg_list['eap-wpa-tkip'] = dict(
        auth = 'PSK',
        encryption = 'TKIP',
        wpa_ver = 'WPA',
        key_string= utils.make_random_string(random.randint(8,63),"hex"),
        ssid = 'meshtree-eap-wpa-tkip',
        vlan_id = '2'
    )

    wlan_cfg_list['eap-wpa-aes'] = dict(
        auth = 'PSK',
        encryption = 'AES',
        wpa_ver = 'WPA',
        key_string= utils.make_random_string(random.randint(8,63),"hex"),
        ssid = 'meshtree-eap-wpa-aes'
    )

    wlan_cfg_list['open-wep128'] = dict(
        auth = 'open',
        encryption = 'WEP-128',
        key_index = '1',
        key_string = utils.make_random_string(26,"hex"),
        ssid = 'meshtree-open-wep128',
        vlan_id = '2'
    )

    return wlan_cfg_list


def defineTestConfiguration(target_station, meshtree_cfg, wlan_cfg_list, active_ap_list):
    target_ip = '192.168.0.252'
    target_ip_vlan_2 = '20.0.2.252'

    test_cfgs = [
            ( dict(),
            "CB_RemoveZDAllConfig",
            "Remove All Configuration on ZD", 0, False),
            ( pprint.pformat(dict(meshtree_cfg = meshtree_cfg, test_case = "create_meshtree"),4),
            "CB_ZD_MeshTree",
            "Create a mesh tree with 1 RootAP and 2 hops", 0, False),
            ( pprint.pformat(dict(meshtree_cfg = meshtree_cfg, test_case = "verify_meshtree"),4),
            "CB_ZD_MeshTree",
            "Verify mesh tree status", 0, False),
            ( pprint.pformat(dict(wlan_cfg_list = [wlan_cfg_list['open-none']]),4),
            "CB_ZD_CreateWlan",
            "Create a Wlan [OPEN-OPEN]", 0, False),
            ( pprint.pformat(dict(target_station = target_station, target_wlan_list = ['meshtree-open-none'], target_ip = target_ip),4),
            "cbZD_AssocTest",
            "Test client Associate to Wlan[OPEN-OPEN]", 1, False),
            ( pprint.pformat(dict(wlan_cfg_list = [wlan_cfg_list['shared-wep64']]),4),
            "CB_ZD_CreateWlan",
            "Create a Wlan [SHARED-WEP64] VLAN=2", 0, False),
            ( pprint.pformat(dict(target_station = target_station, target_wlan_list = ['meshtree-shared-wep64'], target_ip = target_ip_vlan_2),4),
            "CB_ZD_AssocTest",
            "Test client Associate to Wlan[SHARED-WEP64] VLAN=2", 1, False),
            ( pprint.pformat(dict(channel="6", target_ap = active_ap_list[0], test_case = "verify_meshtree_change_channel"),4),
            "CB_ZD_MeshTree",
            "Change RootAP Channel and verify Mesh Tree not change", 0, False),
            ( pprint.pformat(dict(target_ap = active_ap_list[0], test_case = "verify_meshtree_reboot_ap"),4),
            "CB_ZD_MeshTree",
            "Reboot RootAP and verify Mesh Tree not change", 0, False),
            ( pprint.pformat(dict(target_ap = active_ap_list[1], test_case = "verify_meshtree_reboot_ap"),4),
            "CB_ZD_MeshTree",
            "Reboot MeshAP and verify Mesh Tree not change", 0, False),
            ( pprint.pformat(dict(test_case = "verify_meshtree_reboot_zonedirector"),4),
            "CB_ZD_MeshTree",
            "Reboot Zone Director and verify Mesh Tree not change", 0, False),
            ( pprint.pformat(dict(wlan_cfg_list = [wlan_cfg_list['eap-wpa-tkip'], wlan_cfg_list['eap-wpa-aes'], wlan_cfg_list['open-wep128']]),4),
            "CB_ZD_CreateWlan",
            "Create 3 Wlan [eap-wpa-tkip], [eap-wpa-aes], [open-wep128]", 0, False),
            ( pprint.pformat(dict(target_station = target_station, target_wlan_list = ['meshtree-eap-wpa-tkip', 'meshtree-eap-wpa-aes', 'meshtree-open-wep128'],
                           target_ip = target_ip),4),
            "CB_ZD_AssocTest",
            "Test client Assocciate to 3 Wlan [eap-wpa-tkip], [eap-wpa-aes], [open-wep128]", 1, False),

        ]
    return test_cfgs

def defineMeshTree(ap_sym_dict):
    print "Current AP on testbed\nEnter symbolic APs from above list to define your Mesh Tree testbed"
    testsuite.showApSymList(ap_sym_dict)
    meshtree_cfg = dict()
    for key in sorted(ap_sym_dict.keys()):
        uplink_ap = raw_input("Set Uplink AP for '%s' (enter to set AP as Root AP): " % key).split()
        if not uplink_ap: uplink_ap = [""]
        meshtree_cfg[key] = dict()
        meshtree_cfg[key]['uplink_ap'] = uplink_ap[0]
        meshtree_cfg[key]['downlink_ap'] = []

    # Build a mesh tree structure after get input from user
    for uplink_ap in sorted(meshtree_cfg.keys()):
        for downlink_ap in sorted(meshtree_cfg.keys()):
            if meshtree_cfg[downlink_ap]['uplink_ap'] == uplink_ap:
                meshtree_cfg[uplink_ap]['downlink_ap'].append(downlink_ap)

    print "Mesh Tree Configuration: "
    print pprint.pformat(meshtree_cfg, indent=8)

    print "Select a Root AP and a Mesh AP from Mesh Tree: "
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    return meshtree_cfg, active_ap_list

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']
    target_station = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")

    meshtree_cfg, active_ap_list = defineMeshTree(ap_sym_dict)

    ts_name = 'TCID: 37.01 Mesh Tree Basic Wireless Access [Combo Tests] - Non AP specific test'
    ts = testsuite.get_testsuite(ts_name, 'Verify Mesh Tree forming with different scenarios', combotest=True)
    test_cfgs = defineTestConfiguration(target_station, meshtree_cfg, defineDefaultWlanConfiguration(), active_ap_list)

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order, exc_level=exc_level, is_cleanup=is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)
