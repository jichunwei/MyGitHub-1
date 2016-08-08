import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_Debug as bugme

def makeWlanCfg(ssid, sta_radio):
    wlan_cfg = dict()
    _wcid = 0
    ts_base_id = "TCID:10.05.01"
    wlan_cfg[1] = (dict(ssid = ssid, auth = "open"  , wpa_ver = ""    , encryption = "none"
                        , sta_auth = "open"  , sta_wpa_ver = ""    , sta_encryption = "none"
                        , key_index = "" , key_string = ""
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 1
    wlan_cfg[2] = (dict(ssid = ssid, auth = "open"  , wpa_ver = ""    , encryption = "WEP-64"
                        , sta_auth = "open"  , sta_wpa_ver = ""    , sta_encryption = "WEP-64"
                        , key_index = "1", key_string = utils.make_random_string(10, "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 2
    wlan_cfg[3] = (dict(ssid = ssid, auth = "open"  , wpa_ver = ""    , encryption = "WEP-128"
                        , sta_auth = "open"  , sta_wpa_ver = ""    , sta_encryption = "WEP-128"
                        , key_index = "1", key_string = utils.make_random_string(26, "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid))
    _wcid = 3
    wlan_cfg[4] = (dict(ssid = ssid, auth = "shared", wpa_ver = ""    , encryption = "WEP-64"
                        , sta_auth = "shared", sta_wpa_ver = ""    , sta_encryption = "WEP-64"
                        , key_index = "1", key_string = utils.make_random_string(10, "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 4
    wlan_cfg[5] = (dict(ssid = ssid, auth = "shared", wpa_ver = ""    , encryption = "WEP-128"
                        , sta_auth = "shared", sta_wpa_ver = ""    , sta_encryption = "WEP-128"
                        , key_index = "1", key_string = utils.make_random_string(26, "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 5
    wlan_cfg[6] = (dict(ssid = ssid, auth = "PSK"   , wpa_ver = "WPA" , encryption = "TKIP"
                        , sta_auth = "PSK"   , sta_wpa_ver = "WPA" , sta_encryption = "TKIP"
                        , key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid))
    _wcid = 6
    wlan_cfg[7] = (dict(ssid = ssid, auth = "PSK"   , wpa_ver = "WPA" , encryption = "AES"
                        , sta_auth = "PSK"   , sta_wpa_ver = "WPA" , sta_encryption = "AES"
                        , key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 7
    wlan_cfg[8] = (dict(ssid = ssid, auth = "PSK"   , wpa_ver = "WPA2", encryption = "TKIP"
                        , sta_auth = "PSK"   , sta_wpa_ver = "WPA2", sta_encryption = "TKIP"
                        , key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 8
    wlan_cfg[9] = (dict(ssid = ssid, auth = "PSK"   , wpa_ver = "WPA2", encryption = "AES"
                        , sta_auth = "PSK"   , sta_wpa_ver = "WPA2", sta_encryption = "AES"
                        , key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex")
                        , username = "ras.local.user", password = "ras.local.user"
                        , ras_addr = "", ras_port = "", ras_secret = ""
                        , ad_addr = "", ad_port = "", ad_domain = "")
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio)) 
    _wcid = 9
    # EAP-WPA-TKIP
    wlan_cfg[10] = (dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                          sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                          key_index = "" , key_string = '',
                          username = "ras.eap.user", password = "ras.eap.user", ras_addr = "192.168.0.252", ras_port = "1812",
                          ras_secret = "1234567890", use_radius = True)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid))
    _wcid = 10
    # EAP-WPA-AES
    wlan_cfg[11] = (dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                        sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                        key_index = "" , key_string = '',
                        username = "ras.eap.user", password = "ras.eap.user", ras_addr = "192.168.0.252", ras_port = "1812",
                        ras_secret = "1234567890", use_radius = True)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 11
    # EAP-WPA2-TKIP
    wlan_cfg[12] = (dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                        sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                        key_index = "" , key_string = '',
                        username = "ras.eap.user", password = "ras.eap.user", ras_addr = "192.168.0.252", ras_port = "1812",
                        ras_secret = "1234567890", use_radius = True)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    _wcid = 12
    # EAP-WPA2-AES
    wlan_cfg[13] = (dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                        sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                        key_index = "" , key_string = '',
                        username = "ras.eap.user", password = "ras.eap.user", ras_addr = "192.168.0.252", ras_port = "1812",
                        ras_secret = "1234567890", use_radius = True)
                  , const.get_idlist_from_support_model(ts_base_id, _wcid, sta_radio))
    return wlan_cfg

def getCommonNameWithTcid(active_ap_type_role, apcfg, wlan_cfg):
    tcid = wlan_cfg[1][active_ap_type_role] if wlan_cfg[1].has_key(active_ap_type_role) else 'tcid:0.0.0.0'
    cname = getCommonName(wlan_cfg[0])
    return tcid + " - " + cname + " - " + active_ap_type_role

def getCommonName(wcfg):
    cname = wcfg['auth'].upper()
    cname += ' ' + (wcfg['wpa_ver'].upper() if wcfg['wpa_ver'] else 'NONE')
    cname += ' ' + (wcfg['encryption'].upper())
    return cname

def getTargetStation(sta_ip_list):
    ip_list = []
    for i in range(len(sta_ip_list)):
        ip_list.append("  %d - %s" % (i, sta_ip_list[i]))
    print "Station IP list:"
    print ";".join(ip_list)
    id = raw_input("Pick an IP support 11n in the list above: ")
    target_sta = sta_ip_list[int(id)]
    return target_sta

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = (0,"g"), # default value for station 0
        targetap = False,
        testsuite_name = "Wlan Encryption Type"
    )
    attrs.update(kwargs)
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:        
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    ts = testsuite.get_testsuite(attrs["testsuite_name"], "Verify different encryption types in mesh environment.",
                      interactive_mode = attrs["interactive_mode"])
    ssid = "rat-encrypt-%s" % time.strftime("%H%M%S")

    wlan_cfg = makeWlanCfg(ssid, target_sta_radio)
    # Adding test case using local database for Web authentication
    test_order = 1
    test_added = 0
    test_name = "ZD_EncryptionTypes"
    for active_ap in sorted(active_ap_list):
        test_params = { 'ip': tbcfg['server']['ip_addr']
                      , 'target_station': '%s' % target_sta
                      , 'active_ap': '%s' % active_ap
                      , 'wlan_cfg':None
                      , 'radio_mode':None}
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg, interactive_mode = attrs["interactive_mode"])
        radio_mode = 'n' if apcfg['model'].lower() == 'zf7942' else 'g'
        for idx, wcfg_tcid in wlan_cfg.iteritems():
            test_params['wlan_cfg'] = wcfg_tcid[0]
            test_params['radio_mode'] = radio_mode
            test_params['target_sta_radio'] = target_sta_radio
            test_order = test_order + 1
            common_name = "Mesh %s" % getCommonNameWithTcid(ap_type_role, apcfg, wcfg_tcid)
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
# Example:
#
#    # add test cases
#    addtestsuite_ZD_Mesh_EncryptionTypes.py name='mesh'
#
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)


