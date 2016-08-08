import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def _tcid(base_id, description, ap_model=None):
    aptcid = const.get_ap_model_id(ap_model)
    return u'TCID:03.01.%02d.%02d - %s - %s' % (base_id, aptcid, description, ap_model)

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
                    username="ras.local.user",
                    password="ras.local.user",
                    ras_addr="",
                    ras_port="",
                    ras_secret="",
                    ad_addr="",
                    ad_port="",
                    ad_domain="")
    wlanCfg.update(wlan_params)
    return wlanCfg 

def defineWlanCfgByAPModel(ssid,ap_model=None):
    if ap_model:
        ap_model = ap_model.upper()
    wlan_cfgs = \
    [  (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="none",
                       sta_auth="open",
                       sta_encryption="none",)),
          _tcid(1,"Open System", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="WEP-64",
                       sta_auth="open",
                       sta_encryption="WEP-64",
                       key_index="1",
                       key_string=utils.make_random_string(10,"hex"),)),
          _tcid(2,"Open WEP 64 Key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="WEP-128",
                       sta_auth="open",
                       sta_encryption="WEP-128",
                       key_index="1",
                       key_string=utils.make_random_string(26,"hex"),)),
          _tcid(3,"Open WEP 128 Key 1", ap_model)),
       (  get_wlan_cfg(  ssid,  dict(
                       auth="shared",
                       encryption="WEP-64",
                       sta_auth="shared",
                       sta_encryption="WEP-64",
                       key_index="1",
                       key_string=utils.make_random_string(10,"hex"),)),
          _tcid(4,"Shared WEP 64 Key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="shared",
                       encryption="WEP-128",
                       sta_auth="shared",
                       sta_encryption="WEP-128",
                       key_index="1",
                       key_string=utils.make_random_string(26,"hex"),)),
          _tcid(5,"Shared WEP 128 Key 1", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA",
                       encryption="TKIP",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA",
                       sta_encryption="TKIP",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          _tcid(6,"WPA PSK TKIP", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA" ,
                       encryption="AES",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA",
                       sta_encryption="AES",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          _tcid(7,"WPA PSK AES", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA2",
                       encryption="TKIP",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA2",
                       sta_encryption="TKIP",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          _tcid(8,"WPA2 PSK TKIP", ap_model)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA2",
                       encryption="AES",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA2",
                       sta_encryption="AES",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          _tcid(9,"WPA2 PSK AES", ap_model)),
    ]
    return wlan_cfgs

def showNotice():
    msg = "Please select the APs under test. Only RootAP if your testbed is meshed."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    serv_ip = testsuite.getTestbedServerIp(tbcfg)

    target_sta = testsuite.getTargetStation(sta_ip_list)
    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    test_name = "ZD_EncryptionTypesWebAuth"

    ts = testsuite.get_testsuite("WLAN Types - Web Auth",
                      "Verify the ability of ZD to deploy WLANs with different security settings and Web Authentication")

    test_order = 1
    test_added = 0
    for target_sym_ap in active_ap_list:
        ssid = "rat-encrypt-webauth-%s" % time.strftime("%H%M%S")
        
        active_ap = ap_sym_dict[target_sym_ap]
        wlan_cfgs = defineWlanCfgByAPModel(ssid, active_ap['model'])

        test_params = {'ip': serv_ip, 'target_station': target_sta, 'active_ap': target_sym_ap}

        for wlan_cfg, common_name in wlan_cfgs:
            test_params['wlan_cfg'] = wlan_cfg
            if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                test_added += 1
            test_order += 1
    
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)

