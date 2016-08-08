import sys
import random
import time
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(id, radio, description, ap_model=None):
    aptcid = const.get_ap_model_id(ap_model)
    return "TCID:02.%02d.%02d.%02d - %s - %s" % (1 if radio=="g" else 2, id, aptcid, description, ap_model)

def apSupport11n(ap_model):
    if re.search("(7942|7962)", ap_model, re.I):
        return True
    return False

def get_wlan_cfg(ssid, wlan_params):
    wlanCfg = dict( ssid=ssid,
                    auth="open",
                    wpa_ver="",
                    encryption="none",
                    sta_auth="open",
                    sta_wpa_ver="",
                    sta_encryption="none",
                    key_index="",
                    key_string="",
                    username="",
                    password="",
                    ras_addr="",
                    ras_secret="",
                    use_radius=False)
    wlanCfg.update(wlan_params)
    return wlanCfg 

# return list of tuple(wlan_cfg, common_name)
def defineWlanCfgByAPModel(ssid, radio, ras_ip_addr, ap_model):
    if ap_model:
        ap_model = ap_model.upper()
    wlan_cfg_list = \
    [  (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="none")),
          tcid(1, radio, "Open System", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="WEP-64",
                       sta_encryption="WEP-64",
                       key_index="1",
                       key_string=utils.make_random_string(10,"hex"))),
          tcid(2, radio, "Open WEP 64 key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="open", 
                       encryption="WEP-128",
                       sta_encryption="WEP-128",
                       key_index="1",
                       key_string=utils.make_random_string(26,"hex"))),
          tcid(3, radio, "Open WEP 128 key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="shared",
                       encryption="WEP-64",
                       sta_auth="shared",
                       sta_encryption="WEP-64",
                       key_index="1",
                       key_string=utils.make_random_string(10,"hex"))),
          tcid(4, radio, "Shared WEP 64 key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="shared",
                       encryption="WEP-128",
                       sta_auth="shared",
                       sta_encryption="WEP-128",
                       key_index="1",
                       key_string=utils.make_random_string(26,"hex"))),
          tcid(5, radio, "Shared WEP 128 key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA",
                       encryption="TKIP",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA",
                       sta_encryption="TKIP",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"))),
          tcid(6, radio, "WPA PSK TKIP", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA",
                       encryption="AES",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA",
                       sta_encryption="AES",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"))),
          tcid(7, radio, "WPA PSK AES", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA2",
                       encryption="TKIP",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA2",
                       sta_encryption="TKIP",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"))),
          tcid(8, radio, "WPA2 PSK TKIP", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA2",
                       encryption="AES",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA2",
                       sta_encryption="AES",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"))),
          tcid(9, radio, "WPA2 PSK AES", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="EAP",
                       wpa_ver="WPA",
                       encryption="TKIP",
                       sta_auth="EAP",
                       sta_wpa_ver="WPA",
                       sta_encryption="TKIP",
                       username="ras.eap.user",
                       password="ras.eap.user",
                       ras_addr=ras_ip_addr,
                       ras_port="1812",
                       ras_secret="1234567890",
                       use_radius=True)),
          tcid(10, radio, "EAP WPA TKIP RADIUS", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="EAP",
                       wpa_ver="WPA",
                       encryption="AES",
                       sta_auth="EAP",
                       sta_wpa_ver="WPA",
                       sta_encryption="AES",
                       username="ras.eap.user",
                       password="ras.eap.user",
                       ras_addr=ras_ip_addr,
                       ras_port="1812",
                       ras_secret="1234567890",
                       use_radius=True)),
          tcid(11, radio, "EAP WPA AES RADIUS", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="EAP",
                       wpa_ver="WPA2",
                       encryption="TKIP",
                       sta_auth="EAP",
                       sta_wpa_ver="WPA2",
                       sta_encryption="TKIP",
                       username="ras.eap.user",
                       password="ras.eap.user",
                       ras_addr=ras_ip_addr,
                       ras_port="1812",
                       ras_secret="1234567890",
                       use_radius=True)),
          tcid(12, radio, "EAP WPA2 TKIP RADIUS", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="EAP",
                       wpa_ver="WPA2",
                       encryption="AES",
                       sta_auth="EAP",
                       sta_wpa_ver="WPA2",
                       sta_encryption="AES",
                       username="ras.eap.user",
                       password="ras.eap.user",
                       ras_addr=ras_ip_addr,
                       ras_port="1812",
                       ras_secret="1234567890",
                       use_radius=True)),
          tcid(13, radio, "EAP WPA2 AES RADIUS", ap_model))
    ]
    return wlan_cfg_list

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    ras_ip_addr = serv_ip = testsuite.getTestbedServerIp(tbcfg)

    while True:
        target_sta_11g = testsuite.getTargetStation(sta_ip_list, "Pick an 11g wireless station: ")
        target_sta_11n = testsuite.getTargetStation(sta_ip_list, "Pick an 11n wireless station: ")
        if (target_sta_11g or target_sta_11n): break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
 
    test_name = "ZD_EncryptionTypes"
    test_order = 1
    ts_name = "Verify the ability of ZD to deploy WLANs with different encryption types properly - %s"
    test_added = 0
    if target_sta_11g:
        ssid = "rat-encryptions-11g-%s" % time.strftime("%H%M%S")
        ts_11g = testsuite.get_testsuite("Encryption Types - 11g", ts_name % "11g radio")
        for target_sym_ap in active_ap_list:
            active_ap = ap_sym_dict[target_sym_ap]
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, "g", ras_ip_addr, active_ap['model'])

            test_params = {'ip':serv_ip, 'target_station':'%s' % target_sta_11g,
                           'active_ap':'%s' % target_sym_ap, 'radio_mode':'g', 'wlan_cfg':None}

            for wlan_cfg, common_name in wlan_cfg_list:
                test_params['wlan_cfg'] = wlan_cfg
                if testsuite.addTestCase(ts_11g, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1

        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11g.name)

    if target_sta_11n:
       ssid = "rat-encryptions-11n-%s" % time.strftime("%H%M%S")
       ts_11n = testsuite.get_testsuite("Encryption Types - 11n", ts_name % "11n radio")
       test_added = 0
       for target_sym_ap in active_ap_list:
            active_ap = ap_sym_dict[target_sym_ap]
            if not apSupport11n(active_ap['model']):
                continue
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, "n", ras_ip_addr, active_ap['model'])

            test_params = {'ip':serv_ip, 'target_station':'%s' % target_sta_11n,
                           'active_ap':'%s' % target_sym_ap, 'radio_mode':'n', 'wlan_cfg':None}

            for wlan_cfg, common_name in wlan_cfg_list:
                test_params['wlan_cfg'] = wlan_cfg
                if testsuite.addTestCase(ts_11n, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1

       print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11n.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
 
