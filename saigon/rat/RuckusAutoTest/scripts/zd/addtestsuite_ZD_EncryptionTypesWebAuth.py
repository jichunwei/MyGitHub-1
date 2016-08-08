import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(base_id, description, target_sta_radio):
    return u'TCID:03.01.%02d.%d - %s' % (base_id, const.get_radio_id(target_sta_radio), description)

def defineWlanCfg(ssid, target_sta_radio):
    wlan_cfgs = []
    wlan_cfgs.append((dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "none", sta_auth = "open",
                           sta_wpa_ver = "", sta_encryption = "none", key_index = "", key_string = "",
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                      _tcid(1, "Open System", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "WEP-64", sta_auth = "open",
                           sta_wpa_ver = "", sta_encryption = "WEP-64", key_index = "1", key_string = utils.make_random_string(10, "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(2, "Open WEP 64 Key 1", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "WEP-128", sta_auth = "open",
                           sta_wpa_ver = "", sta_encryption = "WEP-128", key_index = "1", key_string = utils.make_random_string(26, "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(3, "Open WEP 128 Key 1", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "shared", wpa_ver = "", encryption = "WEP-64", sta_auth = "shared",
                           sta_wpa_ver = "", sta_encryption = "WEP-64", key_index = "1", key_string = utils.make_random_string(10, "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(4, "Shared WEP 64 Key 1", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "shared", wpa_ver = "", encryption = "WEP-128", sta_auth = "shared",
                           sta_wpa_ver = "", sta_encryption = "WEP-128", key_index = "1", key_string = utils.make_random_string(26, "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(5, "Shared WEP 128 Key 1", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA", encryption = "TKIP", sta_auth = "PSK",
                           sta_wpa_ver = "WPA", sta_encryption = "TKIP", key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(6, "WPA PSK TKIP", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA" , encryption = "AES", sta_auth = "PSK",
                           sta_wpa_ver = "WPA", sta_encryption = "AES", key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(7, "WPA PSK AES", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP", sta_auth = "PSK",
                           sta_wpa_ver = "WPA2", sta_encryption = "TKIP", key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(8, "WPA2 PSK TKIP", target_sta_radio),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA2", encryption = "AES", sta_auth = "PSK",
                           sta_wpa_ver = "WPA2", sta_encryption = "AES", key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "ras.local.user", password = "ras.local.user",
                           ras_addr = "", ras_port = "", ras_secret = "",
                           ad_addr = "", ad_port = "", ad_domain = ""),
                     _tcid(9, "WPA2 PSK AES", target_sta_radio),))
    return wlan_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = "WLAN Types - Web Auth"        
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    serv_ip = testsuite.getTestbedServerIp(tbcfg)

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:        
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]        
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    ssid = "rat-encrypt-webauth-%s" % time.strftime("%H%M%S")
    wlan_cfgs = defineWlanCfg(ssid, target_sta_radio)

    target_ap = active_ap_list[0]
    tap = ap_sym_dict[target_ap]
    print "AP under test is %s [%s %s]" % (target_ap, tap['model'], tap['mac'])

    test_params = {'ip': serv_ip, 'target_station': '%s' % target_sta,
                   'active_ap': '%s' % target_ap, 'target_sta_radio': target_sta_radio}

    test_name = "ZD_EncryptionTypesWebAuth"
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]    
    ts = testsuite.get_testsuite(ts_name,
                      "Verify the ability of ZD to deploy WLANs with different security settings and Web Authentication",
                      interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for wlan_cfg, common_name in wlan_cfgs:
        test_params['wlan_cfg'] = wlan_cfg
        test_params['target_sta_radio'] = target_sta_radio
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

