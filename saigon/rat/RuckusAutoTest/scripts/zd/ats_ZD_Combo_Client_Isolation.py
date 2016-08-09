"""
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_WlanGroup_cfg():
    wlangroup_cfg = dict(
        name = 'client-isolation-wlangroup',
        description = 'client-isolation-wlangroup',
        wlan_member = [],
        vlan_override = False,
    )

    return wlangroup_cfg

def define_Wlan_cfg(ssid):
    wlan_cfgs = []
    wlan_cfgs.append(dict(ssid = 'rat-client-isolation-01', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False,
                           do_isolation = "local"))

    wlan_cfgs.append(dict(ssid = 'rat-client-isolation-02', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False,
                           do_isolation = "local"))

    return wlan_cfgs


def define_test_cfg(cfg):
    test_cfgs = []

    test_name = 'CB_ZD_Find_Station'
    common_name = 'get the station %s' % cfg['target_station_01']
    test_cfgs.append(( {'target_station':cfg['target_station_01'],}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Find_Station'
    common_name = 'get the station %s' % cfg['target_station_02']
    test_cfgs.append(( {'target_station':cfg['target_station_02'],}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Find_Active_AP'
    common_name = 'get the active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'remove all wlans from the station %s' %  cfg['target_station_01']
    test_cfgs.append(({'target_station': 0}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'remove all wlans from the station %s' %  cfg['target_station_02']
    test_cfgs.append(({'target_station': 1}, test_name, common_name, 0, False))

    for wlan_cfg in cfg['wlan_cfg_list']:
        wlan_cfg['do_isolation'] = cfg['isolation_option']
        test_name = 'CB_ZD_Create_Wlan'
        common_name = "[Isolation %s]: create a wlan %s with encryption %s - %s on ZD" % (cfg['isolation_option'], wlan_cfg['auth'], wlan_cfg['encryption'], wlan_cfg['ssid'])
        test_cfgs.append(( {'wlan_cfg_list':[wlan_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlan_Group'
    common_name = '[Isolation %s]: create wlangroup %s' % (cfg['isolation_option'], cfg['wgs_cfg']['name'])
    cfg['wgs_cfg']['wlan_member'] = [cfg['wlan_cfg_list'][0]['ssid']]
    test_cfgs.append(({'wgs_cfg': cfg['wgs_cfg']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_Wlan_On_Wlan_Group'
    common_name = '[Isolation %s]: config wlan %s to wlangroup %s' % (cfg['isolation_option'], cfg['wlan_cfg_list'][0]['ssid'],cfg['wgs_cfg']['name'])
    cfg['wgs_cfg']['wlan_member'] = [cfg['wlan_cfg_list'][0]['ssid']]
    test_cfgs.append(({'wgs_cfg': cfg['wgs_cfg'], 'wlan_list': cfg['wgs_cfg']['wlan_member']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '[Isolation %s]: assign %s to wlangroup %s' % (cfg['isolation_option'], cfg['active_ap'], cfg['wgs_cfg']['name'])
    test_cfgs.append(({'active_ap': cfg['active_ap'], 'wlan_group_name': cfg['wgs_cfg']['name'], 'radio_mode': cfg['radio_mode']},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group'
    common_name = '[Isolation %s]: remove wlan %s from default wlan group' % (cfg['isolation_option'], cfg['wlan_cfg_list'][0]['ssid'])
    cfg['wgs_cfg']['wlan_member'] = [cfg['wlan_cfg_list'][0]['ssid']]
    test_cfgs.append(({'wlan_name_list': cfg['wgs_cfg']['wlan_member']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Associate_Station'
    common_name = '[Isolation %s]: associate the station %s' % (cfg['isolation_option'], cfg['target_station_01'])
    test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'target_station': 0}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '[Isolation %s]: get wifi address of the station %s'  % (cfg['isolation_option'], cfg['target_station_01'])
    test_cfgs.append(({'target_station': 0}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Associate_Station'
    common_name = '[Isolation %s]: associate the station %s' % (cfg['isolation_option'], cfg['target_station_02'])
    if(cfg['isolation_option'] == 'local'):
        test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][0], 'target_station': 1}, test_name, common_name, 0, False))
    else:
        test_cfgs.append(( {'wlan_cfg':cfg['wlan_cfg_list'][1], 'target_station': 1}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '[Isolation %s]: get wifi address of the station %s' % (cfg['isolation_option'], cfg['target_station_02'])
    test_cfgs.append(({'target_station': 1}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[Isolation %s]: ping from station %s to station %s' % ( cfg['isolation_option'], cfg['target_station_01'],  cfg['target_station_02'])
    test_cfgs.append(({'source_station': 0, 'target_station': 1, 'isolation_option': cfg['isolation_option']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Test_Client_Isolation_Connectivity'
    common_name = '[Isolation %s]: ping from station %s to station %s' % ( cfg['isolation_option'], cfg['target_station_02'],  cfg['target_station_01'])
    test_cfgs.append(({'source_station': 1, 'target_station': 0, 'isolation_option': cfg['isolation_option']}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'remove all configuration from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'remove all wlans from the station %s to clean up' % cfg['target_station_01']
    test_cfgs.append(({'target_station': 0}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'remove all wlans from the station %s to clean up' % cfg['target_station_02']
    test_cfgs.append(({'target_station': 1}, test_name, common_name, 0, False))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station1 = (0,"g"),
                 station2 = (1,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if attrs["interactive_mode"]:
        target_sta_01 = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        target_sta_01_radio = testsuite.get_target_sta_radio()

        target_sta_02 = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        target_sta_02_radio = testsuite.get_target_sta_radio()

    else:
        target_sta_01 = sta_ip_list[attrs["station1"][0]]
        target_sta_01_radio = attrs["station1"][1]
        target_sta_02 = sta_ip_list[attrs["station2"][0]]
        target_sta_02_radio = attrs["station2"][1]

    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_01_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break
    wlangroup_cfg = define_WlanGroup_cfg()
    if active_ap :
        for isolation_option in ['none','local','full']:
            ssid = "rat-client-isolation-%s" % (time.strftime("%H%M%S"))
            wlan_cfg_list = define_Wlan_cfg(ssid)
            tcfg = {
                    'target_station_01':'%s' % target_sta_01,
                    'target_station_02':'%s' % target_sta_02,
                    'active_ap':'%s' % active_ap,
                    'radio_mode': target_sta_01_radio,
                    'target_sta_01_radio': target_sta_01_radio,
                    'target_sta_02_radio': target_sta_02_radio,
                    'wlan_cfg_list': wlan_cfg_list,
                    'wgs_cfg': wlangroup_cfg,
                    'ssid': ssid,
                    'isolation_option': isolation_option
                    }
            test_cfgs = define_test_cfg(tcfg)

            if attrs["testsuite_name"]:
                ts_name = attrs["testsuite_name"]
            else:
                ts_name = "Client Isolation set to %s - Combo" % isolation_option

            ts = testsuite.get_testsuite(ts_name,
                                         "Verify client isolation with Isolation set to %s" % isolation_option,
                                         interactive_mode = attrs["interactive_mode"],
                                         combotest=True)

            test_order = 1
            test_added = 0
            for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
                if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                    test_added += 1
                    test_order += 1

                    print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

            print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
