import sys
import random
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(id, radio_id, description, ap_model=None):
    aptcid = const.get_ap_model_id(ap_model)
    return "TCID:02.%02d.%02d.%02d - %s - %s" % (radio_id, id, aptcid, description, ap_model)

def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4
    
def apSupport11n(ap_model):
    if re.search("(7942|7962)", ap_model, re.I):
        return True
    return False

def apSupportdualband(ap_model):
    if re.search("(7962)", ap_model, re.I):
        return True
    return False

def getWgsTypeByRadioAndAPModel(radio_mode, ap_model):
    if radio_mode == 'g':
        if not re.search("(7962)", ap_model):
            wgscfg = 'bg'
        else:
            wgscfg = 'ng_na'
    elif radio_mode == 'n':
        if not re.search("(7962)", ap_model):
            wgscfg = 'ng'
        else:
            wgscfg = 'ng_na'
    else:
        wgscfg ='na_ng'
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
                    username="",
                    password="",
                    ras_addr="",
                    ras_secret="",
                    use_radius=False)
    wlanCfg.update(wlan_params)
    return wlanCfg 

# return list of tuple(wlan_cfg, common_name)
def defineWlanCfgByAPModel(ssid, radio_mode, ras_ip_addr, ap_model):
    if ap_model:
        ap_model = ap_model.upper()
    radio = getRadioId(radio_mode)
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
#if wgscfg=='bg':wgs_cfg={'ap_rp':{'bg': {'wlangroups': 'wlan-wg-bg'}}, 'name': 'wlan-wg-bg','description': 'utest-wg-22bg'}
#if wgscfg=='ng':wgs_cfg={'ap_rp':{'ng':{'wlangroups': 'wlan_wg-ng'}},'name':'wlan-wg-ng','description': 'utest-wg-22ng'}
#if wgscfg=='ng_na':wgs_cfg={'ap_rp':{'ng':{wlangroups':  'wlan_wg-ng'},'na':{'default':True}}, 'name':'wlan-wg-7962ng','description': 'utest-wg-22ng'}
#if wgscfg=='na_ng';wgs_cfg={'ap_rp':{'na':{wlangroups':  'wlan_wg-na'},'ng':{'default':True}}, 'name':'wlan-wg-7962na','description': 'utest-wg-22na'}

def getWgsCfg(mode):
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

def getTestParams(wlan_cfg, wgs_cfg, active_ap, ip, target_station, radio_mode):
    test_params = { 'dest_ip': ip,
                    'wlan_cfg': wlan_cfg,
                    'wgs_cfg': wgs_cfg,
                    'active_ap': active_ap,
                    'target_station': target_station,
                    'radio_mode': radio_mode}
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
    ras_ip_addr = serv_ip = testsuite.getTestbedServerIp(tbcfg)

    while True:
        target_sta_11g = testsuite.getTargetStation(sta_ip_list, "Pick an 11g wireless station: ")
        target_sta_11n = testsuite.getTargetStation(sta_ip_list, "Pick an 11n 2.4G wireless station: ")
        target_sta_11n50 = testsuite.getTargetStation(sta_ip_list, "Pick an 11n 5.0G wireless station: ")
        target_sta_11a = testsuite.getTargetStation(sta_ip_list, "Pick an 11a wireless station: ")
        if (target_sta_11g or target_sta_11n or target_sta_11n50 or target_sta_11a): break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
 
    test_name = "ZD_EncryptionTypes_WlanGroups"
    ts_name = "Verify the ability of ZD to deploy WLANs/WlanGroups with different encryption types properly - %s"
    if target_sta_11g:
        test_order = 1
        test_added = 0
        ssid = "rat-etWGS-11g"
        radio_mode = 'g'
        ts_11g = testsuite.get_testsuite("Encryption Types - WlanGroups - 11g 2.4G", ts_name % "11g 2.4G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode ,apcfg['model'])
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, radio_mode, ras_ip_addr, apcfg['model'])
            for wlan_cfg, common_name in wlan_cfg_list:
                test_params = getTestParams( wlan_cfg,
                                             getWgsCfg(wgscfg),
                                             active_ap,
                                             serv_ip,
                                             target_sta_11g,
                                             radio_mode)
                if testsuite.addTestCase(ts_11g, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11g.name)

    if target_sta_11n:
        test_order = 1
        test_added = 0
        ssid = "rat-etWGS-11n"
        radio_mode = 'n'
        ts_11n = testsuite.get_testsuite("Encryption Types - WlanGroups - 11n 2.4G", ts_name % "11n 2.4G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            if not apSupport11n(apcfg['model']):
                continue
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode,apcfg['model'])
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, radio_mode, ras_ip_addr, apcfg['model'])
            for wlan_cfg, common_name in wlan_cfg_list:
                test_params = getTestParams( wlan_cfg,
                                             getWgsCfg(wgscfg),
                                             active_ap,
                                             serv_ip,
                                             target_sta_11n,
                                             radio_mode)
                if testsuite.addTestCase(ts_11n, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11n.name)

    if target_sta_11n50:
        test_order = 1
        test_added = 0
        ssid = "rat-etWGS-11n5G"
        radio_mode= 'na'
        ts_11n5G = testsuite.get_testsuite("Encryption Types - WlanGroups - 11n 5G", ts_name % "11n 5.0G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            if not apSupportdualband(apcfg['model']):
                continue
            wgscfg=getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, radio_mode, ras_ip_addr, apcfg['model'])
            for wlan_cfg, common_name in wlan_cfg_list:
                test_params = getTestParams( wlan_cfg,
                                             getWgsCfg(wgscfg),
                                             active_ap,
                                             serv_ip,
                                             target_sta_11n50,
                                             radio_mode)
                if testsuite.addTestCase(ts_11n5G, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11n5G.name)

    if target_sta_11a:
        test_order = 1
        test_added = 0
        ssid = "rat-etWGS-11a5G"
        radio_mode = 'a'
        ts_11a5G = testsuite.get_testsuite("Encryption Types - WlanGroups - 11a 5G", ts_name % "11a 5.0G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            if not apSupportdualband(apcfg['model']):
                continue
            wgscfg=getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            wlan_cfg_list = defineWlanCfgByAPModel(ssid, radio_mode, ras_ip_addr, apcfg['model'])
            for wlan_cfg, common_name in wlan_cfg_list:
                test_params = getTestParams( wlan_cfg,
                                             getWgsCfg(wgscfg),
                                             active_ap,
                                             serv_ip,
                                             target_sta_11a,
                                             radio_mode)
                if testsuite.addTestCase(ts_11a5G, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11a5G.name)



if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
 
