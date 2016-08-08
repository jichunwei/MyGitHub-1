import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:%s.%02d" % ('18.02.24.', tcid)

def defineMACEncryptionWLANConf():
    default_wlan_conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
                         'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
                         'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
                         'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '',
                         'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    mac_none = default_wlan_conf.copy()
    mac_none.update({'ssid':'MAC-None', 'auth':'mac', 'encryption':'none'})

    mac_wep_64 = default_wlan_conf.copy()
    mac_wep_64.update({'ssid':'MAC-Wep-64', 'auth':'mac', 'encryption':'WEP-64',
                        'key_index':'1' , 'key_string':utils.make_random_string(10,"hex")})

    mac_wep_128 = default_wlan_conf.copy()
    mac_wep_128.update({'ssid':'MAC-Wep-128', 'auth':'mac', 'encryption':'WEP-128',
                        'key_index':'1' , 'key_string':utils.make_random_string(26,"hex")})

#    mac_wpa_psk_tkip = default_wlan_conf.copy()
#    mac_wpa_psk_tkip.update({'ssid':'MAC-WPA-PSK-TKIP', 'auth':'mac', 'encryption':'TKIP',
#                         'wpa_ver':'WPA', 'key_string':utils.make_random_string(random.randint(8,63),"hex")})
#
#    mac_wpa_psk_aes = default_wlan_conf.copy()
#    mac_wpa_psk_aes.update({'ssid':'MAC-WPA-PSK-AES', 'auth':'mac', 'encryption':'AES',
#                        'wpa_ver':'WPA', 'key_string':utils.make_random_string(random.randint(8,63),"hex")})
#
#    mac_wpa2_psk_tkip = default_wlan_conf.copy()
#    mac_wpa2_psk_tkip.update({'ssid':'MAC-WPA2-PSK-TKIP', 'auth':'mac', 'encryption':'TKIP',
#                          'wpa_ver':'WPA2', 'key_string':utils.make_random_string(random.randint(8,63),"hex")})

    mac_wpa2_psk_aes = default_wlan_conf.copy()
    mac_wpa2_psk_aes.update({'ssid':'MAC-WPA2-PSK-AES', 'auth':'mac', 'encryption':'AES',
                         'wpa_ver':'WPA2', 'key_string':utils.make_random_string(random.randint(8,63),"hex")})

#    return [mac_none, mac_wep_64, mac_wep_128, mac_wpa_psk_tkip, mac_wpa_psk_aes, mac_wpa2_psk_tkip, mac_wpa2_psk_aes]
    return [mac_none, mac_wep_64, mac_wep_128, mac_wpa2_psk_aes]

def defineTestConfiguration(target_station):
    test_cfgs = []

    test_name = 'ZD_MAC_Authentication'
    auth_server = {'server_addr': '192.168.0.252',
                   'server_port': '1812',
                   'server_name': 'freeRadius',
                   'radius_auth_secret': '1234567890'}
    temp_para = {'auth_server_info': auth_server,
                 'authorized_station':target_station,
                 'testcase':'with-encryption-type'}
    i = 1
    for wlan in defineMACEncryptionWLANConf():
        common_name = 'MAC Authentication with %s'
        test_para = temp_para.copy()
        test_para.update({'wlan_conf': wlan})
        test_cfgs.append((test_para, test_name, common_name % wlan['ssid'], tcid(i)))
        i += 1

    return test_cfgs

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs['interactive_mode']:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick a wireless station: ")
    else:
        target_sta = attrs['sta_id']

    ts_name = 'MAC Authentication with Encryption types'
    if attrs['testsuite_name']: ts_name = attrs['testsuite_name']
    test_cfgs = defineTestConfiguration(target_sta)
    ts = testsuite.get_testsuite(ts_name, 'MAC Authentication with Encryption types', interactive_mode = attrs["interactive_mode"])

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
