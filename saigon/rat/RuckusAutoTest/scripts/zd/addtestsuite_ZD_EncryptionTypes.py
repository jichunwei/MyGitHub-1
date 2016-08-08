import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(radio, id):
    return "TCID:02.%02d.%02d" % (const.get_radio_id(radio), id)

def defineWlanCfg(ssid, radio, ras_ip_addr):
    wlan_cfgs = []
    wlan_cfgs.append((dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - Open System" % tcid(radio, 1),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "WEP-64",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "WEP-64",
                           key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - Open WEP 64 key 1" % tcid(radio, 2),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "WEP-128",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "WEP-128",
                           key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - Open WEP 128 key 1" % tcid(radio, 3),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "shared", wpa_ver = "", encryption = "WEP-64",
                           sta_auth = "shared", sta_wpa_ver = "", sta_encryption = "WEP-64",
                           key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - Shared WEP 64 key 1" % tcid(radio, 4),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "shared", wpa_ver = "", encryption = "WEP-128", sta_auth = "shared", sta_wpa_ver = "",
                           sta_encryption = "WEP-128", key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - Shared WEP 128 key 1" % tcid(radio, 5),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA PSK TKIP" % tcid(radio, 6),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA PSK AES" % tcid(radio, 7),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA2 PSK TKIP" % tcid(radio, 8),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA2 PSK AES" % tcid(radio, 9),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                           sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True),
                     "%s - EAP WPA TKIP RADIUS" % tcid(radio, 10),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                           sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True),
                     "%s - EAP WPA AES RADIUS" % tcid(radio, 11),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                           sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True),
                     "%s - EAP WPA2 TKIP RADIUS" % tcid(radio, 12),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                           sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True),
                     "%s - EAP WPA2 AES RADIUS" % tcid(radio, 13),))

    return wlan_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = ""
    )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    ras_ip_addr = serv_ip = testsuite.getTestbedServerIp(tbcfg)

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]

    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break

    test_name = "ZD_EncryptionTypes"

    test_added = 0
    if active_ap :
        ssid = "rat-encryptions-11%s-%s" % (target_sta_radio, time.strftime("%H%M%S"))
        wlan_cfgs = defineWlanCfg(ssid = ssid, radio = target_sta_radio, ras_ip_addr = ras_ip_addr)

        if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
        else: ts_name = "Encryption Types - 11%s" % target_sta_radio
        ts = testsuite.get_testsuite(ts_name,
                          "Verify the ability of ZD to deploy WLANs with different encryption types properly - 11%s radio" % target_sta_radio,
                          interactive_mode = attrs["interactive_mode"])

        test_params = {'ip':serv_ip, 'target_station':'%s' % target_sta,
                       'active_ap':'%s' % active_ap, 'radio_mode': target_sta_radio,
                       'target_sta_radio': target_sta_radio, 
                       'wlan_cfg':None}

        test_order = 1
        
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

