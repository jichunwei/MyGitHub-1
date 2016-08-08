import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

pp = pprint.PrettyPrinter(indent=4)

description_list = dict()
description_list["27.01.01"] = "%sGHz - Streaming video downlink from Server behind ZD to stations%s"
description_list["27.01.09"] = "%sGHz - Verify  the maximum of 32 IGMP groups in the IGMP table%s"
description_list["27.01.14"] = "%sGHz - IGMP join%s"
description_list["27.01.15"] = "%sGHz - Station aged out when send leave%s"


def tcid(sub_id, base_id, radio, description, ap_model = None, ap_type = None, ap_role_id = None):
    aptcid = const.get_ap_model_id(ap_model)
    return u'TCID:27.%02d.%02d.%02d.%d.%d - %s - %s' % (sub_id, radio, base_id, aptcid, ap_role_id, description, ap_type)

def get_wlan_cfg(wlan_params):
    wlan_cfg = dict(
        auth = 'open',
        encryption = 'none',
        ssid = 'rat-zd-iptv'
    )

    wlan_cfg.update(wlan_params)
    return wlan_cfg

def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4
    if radio == 'ng': return 5

def get_wlan_group_cfg(wlan_groups_params):
    wgs_cfg = dict(
        description = 'rat-zd-iptv',
        name = 'rat-zd-iptv',
        vlan_override = False,
        wlan_member = {'rat-zd-iptv':{'vlan_override':'No Change', 'original_vlan':'None'}}
    )

    wgs_cfg.update(wlan_groups_params)
    return wgs_cfg


def getAPName(ap_model):
    return const._ap_model_info[ap_model.lower()]['name']

def showNotice():
    msg = "Please select 1 AP for test"
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)


def createTestSuite(**kwargs):
    global description
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="",
        user_wispr=False
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs['interactive_mode']:
        while True:
            target_station = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
            if target_station: break
            print "Pick one station as your target"

        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)

        combine_with_wispr_profile = raw_input("Combine with WISPr profile (Y/N)? [Enter = Y]:  ")
        if combine_with_wispr_profile.strip() == "" or combine_with_wispr_profile.strip().upper() == "Y":
            combine_with_wispr_profile = True
        else: combine_with_wispr_profile = False

    else:
        target_station = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
        combine_with_wispr_profile = attrs['user_wispr']

    for active_ap in active_ap_list:
        if ap_sym_dict[active_ap]['model'].upper() == "ZF7962":
            ap_radio_frequency = "5.0"
        else:
            ap_radio_frequency = "2.4"

        default_test_params = dict(
            wlan_cfg = get_wlan_cfg({}),
            wlan_group_cfg = get_wlan_group_cfg({}),
            target_station = target_station,
            stream_server = '239.255.0.1',
            active_ap = active_ap,
            radio = {"5.0":"na", "2.4":"ng"}[ap_radio_frequency],
            queue = 'video',
            test_case = 'smartcast',
            protocol = 'udp'
        )
        if combine_with_wispr_profile:
            wispr_profile_cfg = dict(
                auth_info   =  { 'password': 'local.password', 'type': 'local', 'username': 'local.username'},
                hotspot_cfg =  { 'auth_svr': 'Local Database', 'login_page': 'http://192.168.0.250/login.html',
                                 'name': 'A Sampe Hotspot Profile'},
                combine_with_wispr_profile = combine_with_wispr_profile
            )        
        default_test_params.update(wispr_profile_cfg)

        test_order = 1
        test_added = 0
        test_name = 'ZD_IPTV'
        ts_description = 'Test Zone Director\'s IPTV SmartCast Functionality for AP under Zone Director Control'
        ts_name = 'IPTV %sGHz: %s under ZD control - No mesh: SmartCast verification' % (ap_radio_frequency, getAPName(ap_sym_dict[active_ap]['model']))
        if combine_with_wispr_profile:
            ts_name = 'IPTV %sGHz: %s under ZD control - No mesh: Combine with WISPr profile' % (ap_radio_frequency, getAPName(ap_sym_dict[active_ap]['model']))

        smartcast_ts = testsuite.get_testsuite(ts_name, ts_description)
        subid = {True: 6, False: 3}[combine_with_wispr_profile]
        ap_model = ap_sym_dict[active_ap]['model']
        ap_role_id = const.get_ap_role_by_status(ap_sym_dict[active_ap]['status'])
        ap_type = testsuite.getApTargetType(active_ap, ap_sym_dict[active_ap])
        for integration_option in ["", " with L3 ACL", " with L4 ACL"]:
            for id in [1,9,14,15]:
                description = description_list["27.01.%02d" % id] % (ap_radio_frequency, integration_option)
                test_params = default_test_params.copy()
                test_params['test_case'] = { 1: 'smartcast_streaming_downlink',
                                             9: 'smartcast_max_igmp_groups',
                                            14: 'smartcast_igmp_join',
                                            15: 'smartcast_igmp_leave' }[id]

                if integration_option == " with L3 ACL":
                    if id in [1,9]:
                        id = 11
                        test_params['acl_cfg'] =  {'name': 'IPTV with ACL',
                                                   'description': 'IPTV with L3 ACL',
                                                   'default_mode':'allow-all',
                                                   'rules':[{'dst_port':'5001'}]}
                    else: break

                if integration_option == " with L4 ACL":
                    if id in [1,9]:
                        id = 12
                        test_params['acl_cfg'] =  {'name': 'IPTV with ACL',
                                                   'description': 'IPTV with L4 ACL',
                                                   'default_mode':'allow-all',
                                                   'rules':[{'dst_port':'5001'}]}
                    else: break
                common_name = tcid(1, id, getRadioId(test_params['radio']), description, ap_model, ap_type, ap_role_id)
                testsuite.addTestCase(smartcast_ts, test_name , common_name, test_params, test_order)
                test_added = test_added + 1
                test_order = test_order + 1

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, smartcast_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
