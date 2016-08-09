import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as CONST

#Modified by Liang Aihua on 2014-8-28 to remove ap model from common name.
def tcid(base_id, radio, description, ap_model = None):
    aptcid = CONST.get_ap_model_id(ap_model)
    return u'TCID:03.01.%02d.%02d.%02d - %s' % (radio, base_id, aptcid, description)

#def tcid(base_id, radio, description, ap_model = None):
#    aptcid = CONST.get_ap_model_id(ap_model)
#    return u'TCID:03.01.%02d.%02d.%02d - %s - %s' % (radio, base_id, aptcid, description, ap_model)


def getRadioId(radio):
    return CONST.get_radio_id(radio)


def apSupport11n(ap_model):
    return CONST.is_ap_support_11n(ap_model)


def apSupportDualBand(ap_model):
    return CONST.is_ap_support_dual_band(ap_model)


def getWgsTypeByRadioAndAPModel(station_radio, ap_model):
    return CONST.get_wgs_type_by_radio_and_ap_model(station_radio, ap_model)


def get_wlan_cfg(ssid, wlan_params):
    wlanCfg = dict(
        ssid = ssid,
        auth = "open",
        wpa_ver = "",
        encryption = "none",
        sta_auth = "open",
        sta_wpa_ver = "",
        sta_encryption = "none",
        key_index = "",
        key_string = "",
        username = "ras.local.user",
        password = "ras.local.user",
        ras_addr = "",
        ras_port = "",
        ras_secret = "",
        ad_addr = "",
        ad_port = "",
        ad_domain = "",
    )
    wlanCfg.update(wlan_params)

    return wlanCfg


def defineWlanCfgByAPModel(ssid, station_radio, ap_model = None):
    if ap_model:
        ap_model = ap_model.upper()

    radio = getRadioId(station_radio)
    wlan_cfgs = \
    [  (get_wlan_cfg(ssid, dict(
                       auth = "open",
                       encryption = "none",
                       sta_auth = "open",
                       sta_encryption = "none",)),
          tcid(1, radio, "Open System", ap_model)),
       (get_wlan_cfg(ssid, dict(
                       auth = "open",
                       encryption = "WEP-64",
                       sta_auth = "open",
                       sta_encryption = "WEP-64",
                       key_index = "1",
                       key_string = utils.make_random_string(10, "hex"),)),
          tcid(2, radio, "Open WEP 64 Key 1", ap_model)),
       (get_wlan_cfg(ssid, dict(
                       auth = "open",
                       encryption = "WEP-128",
                       sta_auth = "open",
                       sta_encryption = "WEP-128",
                       key_index = "1",
                       key_string = utils.make_random_string(26, "hex"),)),
          tcid(3, radio, "Open WEP 128 Key 1", ap_model)),
     
     #Modified by Liang Aihua on 2014-8-26, for these securities not support any more.
           
       #(get_wlan_cfg(ssid, dict(
       #                auth = "shared",
       #                encryption = "WEP-64",
       #                sta_auth = "shared",
       #                sta_encryption = "WEP-64",
       #                key_index = "1",
       #                key_string = utils.make_random_string(10, "hex"),)),
       #   tcid(4, radio, "Shared WEP 64 Key 1", ap_model)),
       
       #(get_wlan_cfg(ssid, dict(
       #                auth = "shared",
       #                encryption = "WEP-128",
       #                sta_auth = "shared",
       #                sta_encryption = "WEP-128",
       #                key_index = "1",
       #                key_string = utils.make_random_string(26, "hex"),)),
       #   tcid(5, radio, "Shared WEP 128 Key 1", ap_model)),
       #(get_wlan_cfg(ssid, dict(
       #                auth = "PSK",
       #                wpa_ver = "WPA",
       #                encryption = "TKIP",
       #                sta_auth = "PSK",
       #                sta_wpa_ver = "WPA",
       #                sta_encryption = "TKIP",
       #                key_string = utils.make_random_string(random.randint(8, 63), "hex"),)),
       #   tcid(6, radio, "WPA PSK TKIP", ap_model)),
       #(get_wlan_cfg(ssid, dict(
       #                auth = "PSK",
       #                wpa_ver = "WPA" ,
       #                encryption = "AES",
       #                sta_auth = "PSK",
       #                sta_wpa_ver = "WPA",
       #                sta_encryption = "AES",
       #                key_string = utils.make_random_string(random.randint(8, 63), "hex"),)),
       #   tcid(7, radio, "WPA PSK AES", ap_model)),
       #(get_wlan_cfg(ssid, dict(
       #                auth = "PSK",
       #                wpa_ver = "WPA2",
       #                encryption = "TKIP",
       #                sta_auth = "PSK",
       #                sta_wpa_ver = "WPA2",
       #                sta_encryption = "TKIP",
       #                key_string = utils.make_random_string(random.randint(8, 63), "hex"),)),
       #   tcid(8, radio, "WPA2 PSK TKIP", ap_model)),        
    
       (get_wlan_cfg(ssid, dict(
                       auth = "PSK",
                       wpa_ver = "WPA2",
                       encryption = "AES",
                       sta_auth = "PSK",
                       sta_wpa_ver = "WPA2",
                       sta_encryption = "AES",
                       key_string = utils.make_random_string(random.randint(8, 63), "hex"))),
          tcid(9, radio, "WPA2 PSK AES", ap_model))
          
    ]
    return wlan_cfgs


def get_wgs_by_radio_and_ap_model(station_radio, ap_model):
    '''
    '''
    radio_list = CONST.get_radio_mode_by_ap_model(ap_model)

    if not isinstance(radio_list, list):
        radio_list = [radio_list]

    # in case station radio is ng, but AP might support only bg
    # configure AP radio to bg instead of ng
    radio_mode = 'bg'
    if not radio_mode in radio_list:
        radio_mode = station_radio

    wgs_cfg = {
        'name': '',
        'ap_rp': {},
    }
    for radio in radio_list:
        if radio == radio_mode:
            wgs_name = 'wlan-wg-%s' % radio
            wgs_cfg.update({
                'name': wgs_name,
            })
            wgs_cfg['ap_rp']['%s' % radio] = {'wlangroups': wgs_name}

        else:
            wgs_cfg['ap_rp']['%s' % radio] = {'default': True}

    return wgs_cfg


def getWgsCfg(mode = 'bg'):
    if mode == 'bg':
        wgs_cfg = {'name': 'wlan-wg-bg', 'description': '', 'ap_rp': {}}
        wgs_cfg['ap_rp']['bg'] = {'wlangroups': wgs_cfg['name']}

    elif mode == 'ng':
        wgs_cfg = {'name': 'wlan-wg-ng', 'description': '', 'ap_rp': {}}
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}

    elif mode == 'na':
        wgs_cfg = {'name': 'wlan-wg-ng-na', 'description': '', 'ap_rp': {}}
        wgs_cfg['ap_rp']['na'] = {'wlangroups': wgs_cfg['name']}

    else:
        wgs_cfg = {'name': 'wlan-wg-na-ng', 'description': '', 'ap_rp': {}}
        wgs_cfg['ap_rp']['na'] = {'wlangroups': wgs_cfg['name'], 'channel':'149'}
        wgs_cfg['ap_rp']['ng'] = {'default': True}

    return wgs_cfg


def getTestParams(wlan_cfg, wgs_cfg, active_ap, ip, target_station):
    test_params = {
        'dest_ip': ip,
        'wlan_cfg': wlan_cfg,
        'wgs_cfg': wgs_cfg,
        'active_ap': active_ap,
        'target_station': target_station
    }

    return test_params


def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)


def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    default_dest_ip = '172.126.0.252'
    new_dest_ip = raw_input('Input destination host ip address, press Enter to default(%s)' % default_dest_ip)
    dest_ip = default_dest_ip if new_dest_ip == "" else new_dest_ip

    while True:
        target_sta_11ng = testsuite.getTargetStation(sta_ip_list, "Pick an 11ng wireless station: ")
        target_sta_11na = testsuite.getTargetStation(sta_ip_list, "Pick an 11na wireless station: ")
        if (target_sta_11ng or target_sta_11na): break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    test_name = "ZD_EncryptionTypesWebAuth_WlanGroups"
    ts_name = "Verify the ability of ZD to deploy WLANs/WlanGroups with different security settings and Web Authentication - %s"

    if target_sta_11ng:
        test_order = 1
        test_added = 0
        station_radio = 'ng'
        ssid = "rat-web-auth-wgs-11%s" % station_radio
        ts_11ng = testsuite.get_testsuite("WLAN Types Web Auth with WlanGroups - 11ng 2.4G", ts_name % "11ng 2.4G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            wgs_cfg = get_wgs_by_radio_and_ap_model(station_radio, apcfg['model'])

            wlan_cfg_list = defineWlanCfgByAPModel(ssid, station_radio, apcfg['model'])
            for wlan_cfg, common_name in wlan_cfg_list:
                test_params = getTestParams(
                    wlan_cfg, wgs_cfg, active_ap,
                    dest_ip, target_sta_11ng
                )
                if testsuite.addTestCase(ts_11ng, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1

                test_order += 1

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11ng.name)


    if target_sta_11na:
        test_order = 1
        test_added = 0
        station_radio = 'na'
        ssid = "rat-web-auth-wgs-11%s" % station_radio
        ts_11na = testsuite.get_testsuite("WLAN Types Web Auth with WlanGroups - 11na 5G", ts_name % "11na 5.0G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            wgs_cfg = get_wgs_by_radio_and_ap_model(station_radio, apcfg['model'])
            if not apSupportDualBand(apcfg['model']):
                continue

            wlan_cfg_list = defineWlanCfgByAPModel(ssid, station_radio, apcfg['model'])
            for wlan_cfg, common_name in wlan_cfg_list:
                test_params = getTestParams(
                    wlan_cfg, wgs_cfg, active_ap,
                    dest_ip, target_sta_11na
                )
                if testsuite.addTestCase(ts_11na, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1

                test_order += 1

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11na.name)


if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

