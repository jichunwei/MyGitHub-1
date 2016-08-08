import sys
import pprint

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

pp = pprint.PrettyPrinter(indent=4)

description_list = dict()
description_list["27.04.01"] = "%sGHz use zing udp protocol with port matching filter%s"
description_list["27.04.02"] = "%sGHz use zing tcp protocol with port matching filter%s"
description_list["27.04.03"] = "%sGHz use zing udp protocol with port matching filter and TOS marking%s"

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
    return const.get_ap_name_by_model(ap_model)#@author:yuyanan @since:2014-8-8 optimize 

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
        
        target_sta_radio = testsuite.get_target_sta_radio()#@author: yuyanan @since: 2014-8-8  @bug:zf-9404
        
        combine_with_wispr_profile = raw_input("Combine with WISPr profile (Y/N)? [Enter = Y]:  ")
        if combine_with_wispr_profile.strip() == "" or combine_with_wispr_profile.strip().upper() == "Y":
            combine_with_wispr_profile = True
        else: combine_with_wispr_profile = False

    else:
        target_station = sta_ip_list[attrs["sta_id"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
        combine_with_wispr_profile = attrs['user_wispr']
        
        
    #@author: yuyanan @since: 2014-8-8  @bug:zf-9404  optimize: get ap radio from nteractive_mode
    active_ap_radio_list = []
    for key in active_ap_list:
        if key in ap_sym_dict:
            ap_info = ap_sym_dict[key]
            ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios']
            if target_sta_radio in ap_support_radio_list:
                active_ap_radio_list.append(key)

    ap_radio_frequency = target_sta_radio
    if not active_ap_radio_list:
        print "no active ap! please confirm ap radio is correct!"

    for active_ap in active_ap_radio_list:
        default_test_params = dict(
            wlan_cfg = get_wlan_cfg({}),
            wlan_group_cfg = get_wlan_group_cfg({}),
            target_station = target_station,
            stream_server = '192.168.0.252',
            active_ap = active_ap,
            radio = ap_radio_frequency,
            queue = 'video',
            filter_media = 'video',
            filter_matching = True,
            tos_classify_value = '0xA0',
            tos_classify_enable = True,
            tos_matching = True,
            test_case = 'port_matching_filter',
            protocol = 'udp',
            tos_mark_enable = False
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
        ts_description = 'Test Zone Director\'s IPTV Port Matching Filter Functionality for AP under Zone Director Control'
        ts_name = 'IPTV %sGHz: %s under ZD control - No mesh: Port Matching Filter verification' % (ap_radio_frequency, getAPName(ap_sym_dict[active_ap]['model']))
        if combine_with_wispr_profile:
            ts_name = 'IPTV %sGHz: %s under ZD control - No mesh: Combine with WISPr profile' % (ap_radio_frequency, getAPName(ap_sym_dict[active_ap]['model']))

        port_matching_filter_ts = testsuite.get_testsuite(ts_name, ts_description)
        subid = {True: 6, False: 3}[combine_with_wispr_profile]
        ap_model = ap_sym_dict[active_ap]['model']
        ap_role_id = const.get_ap_role_by_status(ap_sym_dict[active_ap]['status'])
        ap_type = testsuite.getApTargetType(active_ap, ap_sym_dict[active_ap],ap_tag = True)#@author:yuyanan @since:2014-8-6 zf-9438 add ap_tag parameter

        for integration_option in ["", " with VLAN", " with ACL L4"]:
            for id in [1,2,3]:
                description = description_list["27.04.%02d" % id] % (ap_radio_frequency, integration_option)
                test_params = default_test_params.copy()
                if id == 2: test_params['protocol'] = 'tcp'
                if id == 3:
                    test_params['tos_mark_enable'] = True
                    test_params['tos_mark_value'] = '0x80'
                    test_params['media'] = 'video'
                if integration_option ==  " with VLAN":
                    id = 4
                    test_params['wlan_cfg']['vlan_id'] = '2'
                if integration_option == " with ACL L4":
                    id = 5
                    test_params['acl_cfg'] =  {'name': 'IPTV with ACL',
                                               'description': '',
                                               'default_mode':'allow-all',
                                               'rules':[{'dst_port':'5001'}]}

                common_name = tcid(subid, id, getRadioId(test_params['radio']), description, ap_model, ap_type, ap_role_id)
                testsuite.addTestCase(port_matching_filter_ts, test_name , common_name, test_params, test_order)
                test_added = test_added + 1
                test_order = test_order + 1

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, port_matching_filter_ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
