import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(base_id, radio, description, ap_model=None):
    aptcid = const.get_ap_model_id(ap_model)
    return u'TCID:03.02.%02d.%02d.%02d - %s - %s' % (radio, base_id, aptcid, description, ap_model)

def getRadioId(radio):
    if radio == 'g': return 1
    if radio == 'n': return 2
    if radio == 'a': return 3
    if radio == 'na': return 4

def apSupport11n(ap_model):
    if re.search("(7942|7962)", ap_model, re.I):
        return True
    return False

def apSupportDualBand(ap_model):
    if re.search("(7962)", ap_model, re.I):
        return True
    return False

def getWgsTypeByRadioAndAPModel(radio_mode, ap_model):
    if radio_mode == 'ng':
        if re.search("(7962)", ap_model):
            wgscfg = 'ng_na'
        elif re.search("(7942)", ap_model):
            wgscfg = 'ng'
        else:
            wgscfg = 'bg'
    elif radio_mode == 'na':
        wgscfg = 'na_ng'
    return wgscfg

def getTestCfg(ssid, dest_ip, test_param):
    testCfg = dict(ssid=ssid,
                   dest_ip=dest_ip,
                   use_guest_auth='',
                   use_tou='',
                   redirect_url = '')
    testCfg.update(test_param)
    return testCfg

def defineTestCfgByAPModel(ssid, radio_mode, ap_model, zd_ip_addr='192.168.0.2'):
    restricted_ip_list=['172.21.0.252', '172.22.0.252', '172.23.0.252', '172.24.0.252', '172.25.0.252']
    default_dest_ip = '172.126.0.252'
    new_dest_ip = raw_input('Input destination host ip address, press Enter to default(%s)' % default_dest_ip)
    dest_ip = default_dest_ip if new_dest_ip == "" else new_dest_ip
    radio = getRadioId(radio_mode)
    test_cfgs = \
    [  (  getTestCfg( ssid, dest_ip,
                      dict(use_guest_auth=True,
                           use_tou=False,
                           redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(1, radio, "Auth/No TOU/No Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=True,
                            use_tou=False,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(2, radio, "Auth/No TOU/Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=True,
                            use_tou=True,
                            redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(3, radio, "Auth/TOU/No Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=True,
                            use_tou=True,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(4, radio, "Auth/TOU/Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=False,
                            redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(5, radio, "No Auth/No TOU/No Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=False,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(6, radio, "No Auth/No TOU/Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=True,
                            redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(7, radio, "No Auth/TOU/No Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=True,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(8, radio, "No Auth/TOU/Redirection",ap_model)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth = True,
                            use_tou = True,
                            redirect_url = '',
                            zd_ip=zd_ip_addr,
                            restricted_ip_list=restricted_ip_list,)),
          "ZD_RestrictedSubnetAccess_WlanGroups",
                      tcid(9, radio, "Restricted Subnet Access",ap_model)),
    ]
    return test_cfgs

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

def getTestParams(test_cfg, wgs_cfg, active_ap, target_station):
    test_params={ 'wgs_cfg': wgs_cfg,
                  'active_ap': active_ap,
                  'target_station': target_station}
    test_params.update(test_cfg)
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
    zd_ip_addr = tbcfg['ZD']['ip_addr']

    while True:
        target_sta_11ng = testsuite.getTargetStation(sta_ip_list, "Pick an 11ng wireless station: ")
        target_sta_11na = testsuite.getTargetStation(sta_ip_list, "Pick an 11na wireless station: ")
        if (target_sta_11ng or target_sta_11na): break
        print "Pick at least one station as your target"

    showNotice()
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    ts_name = "Verify the ability of the ZD to handle guest access properly - %s"

    if target_sta_11ng:
        test_order = 1
        test_added = 0
        radio_mode = 'n'
        ts_11ng = testsuite.get_testsuite("Guest Access with WlanGroups - 11ng 2.4G", ts_name % "11ng 2.4G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            if apSupport11n(apcfg['model']):
                ssid = "rat-gaWGS-11ng"
            else:
                ssid = "rat-gaWGS-11bg"
            test_cfg_list = defineTestCfgByAPModel(ssid, radio_mode, apcfg['model'], zd_ip_addr)
            for test_cfg, test_name, common_name in test_cfg_list:
                test_params = getTestParams( test_cfg,
                                             getWgsCfg(wgscfg),
                                             active_ap,
                                             target_sta_11ng)
                if testsuite.addTestCase(ts_11ng, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11ng.name)

    if target_sta_11na:
        test_order = 1
        test_added = 0
        ssid = "rat-gaWGS-11na"
        radio_mode = 'na'
        ts_11na = testsuite.get_testsuite("Guest Access with WlanGroups - 11na 5G", ts_name % "11na 5.0G radio")
        for active_ap in active_ap_list:
            apcfg = ap_sym_dict[active_ap]
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            if not apSupportDualBand(apcfg['model']):
                continue
            test_cfg_list = defineTestCfgByAPModel(ssid, radio_mode, apcfg['model'], zd_ip_addr)
            for test_cfg, test_name, common_name in test_cfg_list:
                test_params = getTestParams( test_cfg,
                                             getWgsCfg(wgscfg),
                                             active_ap,
                                             target_sta_11na)
                if testsuite.addTestCase(ts_11na, test_name, common_name, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts_11na.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict( sys.argv[1:] )
    createTestSuite(**_dict)

