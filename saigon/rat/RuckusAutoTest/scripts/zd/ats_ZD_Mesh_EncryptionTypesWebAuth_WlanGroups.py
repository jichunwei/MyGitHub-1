import sys
import random
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(id, radio_id, description, ap_model, ap_type_role):
    aptcid = const.get_ap_model_id(ap_model)
    rband = "2.4G" if radio_id in [1, 2] else "5G"
    xdescription = description + ' - ' + ap_type_role + ' -  ' + rband
    aprtid = getApTypeRoleId(ap_type_role)
    return "TCID:10.05.04.%02d.%02d.%02d.%02d - %s" % (radio_id, id , aptcid, aprtid, xdescription)

def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4

def apSupport11n(ap_model):
    if re.search("(7942|7962|7762)", ap_model, re.I):
        return True
    return False

def apSupportdualband(ap_model):
    if re.search("(7962|7762)", ap_model, re.I):
        return True
    return False

def getApTypeRoleId(ap_type_role):
    if re.search("(root)", ap_type_role, re.I):
        return 1
    if re.search("(mesh)", ap_type_role, re.I):
        return 2
    if re.search("(ap)", ap_type_role, re.I):
        return 3

def getRadioModeByAPModel(ap_model):
    rlist = []
    if re.search("(2925|2942|2741)", ap_model, re.I):
        rlist.append('g')
    if re.search("(7942)", ap_model, re.I):
        rlist.append('n')
    if re.search("(7962|7762)", ap_model, re.I):
        rlist.append('n')
        rlist.append('na')
    return rlist

def getWgsTypeByRadioAndAPModel(radio_mode, ap_model):
    if radio_mode == 'g':
        wgscfg = 'bg'
    elif radio_mode == 'n':
        if re.search("(7962|7762)", ap_model):
            wgscfg = 'ng_na'
        else:
            wgscfg = 'ng'
    elif radio_mode == 'na':
        wgscfg = 'na_ng'
    return wgscfg

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

def defineWlanCfgByAPModel(ssid, radio_mode, ap_model, ap_type_role):
    if ap_model:
        ap_model = ap_model.upper()
    radio = getRadioId(radio_mode)
    wlan_cfgs = \
    [  (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="none",
                       sta_auth="open",
                       sta_encryption="none",)),
          tcid(1,radio,"Open System", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="WEP-64",
                       sta_auth="open",
                       sta_encryption="WEP-64",
                       key_index="1",
                       key_string=utils.make_random_string(10,"hex"),)),
          tcid(2,radio,"Open WEP 64 Key 1", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="open",
                       encryption="WEP-128",
                       sta_auth="open",
                       sta_encryption="WEP-128",
                       key_index="1",
                       key_string=utils.make_random_string(26,"hex"),)),
          tcid(3,radio,"Open WEP 128 Key 1", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid,  dict(
                       auth="shared",
                       encryption="WEP-64",
                       sta_auth="shared",
                       sta_encryption="WEP-64",
                       key_index="1",
                       key_string=utils.make_random_string(10,"hex"),)),
          tcid(4,radio,"Shared WEP 64 Key 1", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="shared",
                       encryption="WEP-128",
                       sta_auth="shared",
                       sta_encryption="WEP-128",
                       key_index="1",
                       key_string=utils.make_random_string(26,"hex"),)),
          tcid(5,radio,"Shared WEP 128 Key 1", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA",
                       encryption="TKIP",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA",
                       sta_encryption="TKIP",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          tcid(6,radio,"WPA PSK TKIP", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA" ,
                       encryption="AES",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA",
                       sta_encryption="AES",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          tcid(7,radio,"WPA PSK AES", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA2",
                       encryption="TKIP",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA2",
                       sta_encryption="TKIP",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          tcid(8,radio,"WPA2 PSK TKIP", ap_model, ap_type_role)),
       (  get_wlan_cfg(  ssid, dict(
                       auth="PSK",
                       wpa_ver="WPA2",
                       encryption="AES",
                       sta_auth="PSK",
                       sta_wpa_ver="WPA2",
                       sta_encryption="AES",
                       key_string=utils.make_random_string(random.randint(8,63),"hex"),)),
          tcid(9,radio,"WPA2 PSK AES", ap_model, ap_type_role)),
    ]
    return wlan_cfgs

def getWgsCfg(mode='bg'):
    if mode =='bg':
        wgs_cfg = {'name': 'wlan-wg-bg', 'description': 'utest-wg-22bg', 'ap_rp': {}}
        wgs_cfg['ap_rp']['bg'] = {'wlangroups': wgs_cfg['name']}
    elif mode == 'ng':
        wgs_cfg = {'name': 'wlan-wg-ng', 'description': 'utest-wg-22ng', 'ap_rp': {}}
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
    elif mode == 'ng_na':
        wgs_cfg = {'name': 'wlan-wg-ng-na', 'description': 'utest-wg-22ng-na', 'ap_rp': {}}
        wgs_cfg['ap_rp']['ng'] = {'wlangroups': wgs_cfg['name']}
        wgs_cfg['ap_rp']['na'] = {'default': True}
    else:
        wgs_cfg = {'name': 'wlan-wg-na-ng', 'description': 'utest-wg-22na-ng', 'ap_rp': {}}
        wgs_cfg['ap_rp']['na'] = {'wlangroups': wgs_cfg['name'],'channel':'Auto'}
        wgs_cfg['ap_rp']['ng'] = {'default': True}
    return wgs_cfg

def getTestParams(wlan_cfg, wgs_cfg, active_ap, ip, target_station):
    test_params = { 'dest_ip': ip,
                    'wlan_cfg': wlan_cfg,
                    'wgs_cfg': wgs_cfg,
                    'active_ap': active_ap,
                    'target_station': target_station}
    return test_params

def showNotice():
    msg = "Please select the APs under test."
    dsh = "+-" + "-" * len(msg) + "-+"
    print "\n%s\n| %s |\n%s" % (dsh, msg, dsh)

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_11ng = 0,
        sta_11na = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    dest_ip = '172.126.0.252'

    if attrs["interactive_mode"]:
        while True:
            target_sta_11ng = testsuite.getTargetStation(sta_ip_list, "Pick an 11n 2.4G wireless station: ")
            target_sta_11na = testsuite.getTargetStation(sta_ip_list, "Pick an 11n 5.0G wireless station: ")
            if (target_sta_11ng or target_sta_11na): break
            print "Pick at least one station as your target"
        showNotice()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta_11ng = sta_ip_list[attrs["sta_11ng"]]
        target_sta_11na = sta_ip_list[attrs["sta_11na"]]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())

    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "Mesh - Integration - WebAuth - WlanGroups"
    ts = testsuite.get_testsuite( ts_name,
                       "Verify different encryption types with Web authentication in mesh environment.",
                       interactive_mode = attrs["interactive_mode"])

    ssid = "rat-webAuthWGS-mesh"

    test_order = 1
    test_added = 0
    test_name="ZD_EncryptionTypesWebAuth_WlanGroups"

    for active_ap in sorted(active_ap_list):
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)
        radio_mode_list = getRadioModeByAPModel(apcfg['model'])
        for radio_mode in radio_mode_list:
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, radio_mode, apcfg['model'], ap_type_role)
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            target_sta = target_sta_11na if radio_mode == 'na' else target_sta_11ng
            if target_sta:
                for wlan_cfg, common_name in wlan_cfg_list:
                    test_params = getTestParams( wlan_cfg,
                                                 getWgsCfg(wgscfg),
                                                 active_ap,
                                                 dest_ip,
                                                 target_sta)
                    if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                        test_added += 1
                    test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


# Example:
#
#    # add test cases
#    addtestsuite_ZD_Mesh_EncryptionTypesWebAuth.py name='mesh'
#
if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    createTestSuite(**_dict)

