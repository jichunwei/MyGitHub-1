import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(radio, id, ap_model):
    aptcid = const.get_ap_model_id(ap_model)
    return "TCID:02.%02d.%02d.%02d" % (const.get_radio_id(radio), id, aptcid)

def defineWlanCfg(ssid, radio, ras_ip_addr, ap_model):
    wlan_cfgs = []
    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK TKIP - Station WPA-TKIP - %s" % (tcid(radio, 14, ap_model), ap_model.upper()),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK AES - Station WPA EAS - %s" % (tcid(radio, 15, ap_model), ap_model.upper()),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK TKIP - Station WPA2 TKIP - %s" % (tcid(radio, 16, ap_model), ap_model.upper()),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK AES - Station WPA2 AES - %s" % (tcid(radio, 17, ap_model), ap_model.upper()),))
    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK Auto - Station WPA TKIP - %s" % (tcid(radio, 18, ap_model), ap_model.upper()),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK Auto - STA WPA AES - %s" % (tcid(radio, 19, ap_model), ap_model.upper()),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK Auto - Station WPA2 TKIP - %s" % (tcid(radio, 20, ap_model), ap_model.upper()),))

    wlan_cfgs.append((dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False),
                     "%s - WPA-Mixed PSK Auto - Station WPA2 AES - %s" % (tcid(radio, 21, ap_model), ap_model.upper()),))


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

    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break

    test_name = "ZD_EncryptionTypes"

    test_added = 0
    for active_ap in active_ap_list: 
        if active_ap :
            ssid = "rat-encryptions-11%s-%s" % (target_sta_radio, time.strftime("%H%M%S"))
            wlan_cfgs = defineWlanCfg(ssid = ssid, radio = target_sta_radio, ras_ip_addr = ras_ip_addr, 
                                      ap_model = ap_sym_dict[active_ap]['model'])    
            if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
            else: ts_name = "Encryption Types WPA Mixed - 11%s" % target_sta_radio
            ts = testsuite.get_testsuite(ts_name,
                              "Verify the ability of ZD to deploy WLANs with WPA-Mixed properly",
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

