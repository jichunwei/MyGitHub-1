import sys
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def tcid(id, radio_id, description, ap_model, ap_type_role):
    aptcid = const.get_ap_model_id(ap_model)
    rband = "2.4G" if radio_id in [1, 2] else "5G"
    xdescription = description + ' - ' + ap_type_role + ' -  ' + rband
    aprtid = getApTypeRoleId(ap_type_role)
    return "TCID:10.05.05.%02d.%02d.%02d.%02d - %s" % (radio_id, id , aptcid, aprtid, xdescription)

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

def getTestCfg(ssid, dest_ip, test_param):
    testCfg = dict(ssid=ssid,
                   dest_ip=dest_ip,
                   use_guest_auth='',
                   use_tou='',
                   redirect_url = '')
    testCfg.update(test_param)
    return testCfg

def defineTestCfgByAPModel(ssid, radio_mode, ap_model, ap_type_role, zd_ip_addr='192.168.0.2'):
    restricted_ip_list=['172.21.0.252', '172.22.0.252', '172.23.0.252', '172.24.0.252', '172.25.0.252']
    dest_ip = '172.126.0.252'
    radio = getRadioId(radio_mode)
    test_cfgs = \
    [  (  getTestCfg( ssid, dest_ip,
                      dict(use_guest_auth=True,
                           use_tou=False,
                           redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(1, radio, "Auth/No TOU/No Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=True,
                            use_tou=False,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(2, radio, "Auth/No TOU/Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=True,
                            use_tou=True,
                            redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(3, radio, "Auth/TOU/No Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=True,
                            use_tou=True,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(4, radio, "Auth/TOU/Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=False,
                            redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(5, radio, "No Auth/No TOU/No Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=False,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(6, radio, "No Auth/No TOU/Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=True,
                            redirect_url = '',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(7, radio, "No Auth/TOU/No Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth=False,
                            use_tou=True,
                            redirect_url = 'http://www.example.net/',)),
          "ZD_GuestAccess_WlanGroups",
          tcid(8, radio, "No Auth/TOU/Redirection",ap_model, ap_type_role)),
        (  getTestCfg( ssid, dest_ip,
                       dict(use_guest_auth = True,
                            use_tou = True,
                            redirect_url = '',
                            zd_ip=zd_ip_addr,
                            restricted_ip_list=restricted_ip_list,)),
          "ZD_RestrictedSubnetAccess_WlanGroups",
                      tcid(9, radio, "Restricted Subnet Access",ap_model, ap_type_role)),
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
    zd_ip_addr = tbcfg['ZD']['ip_addr']

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
    else: ts_name = "Mesh - Integration - Guest Access - WlanGroups"
    ts = testsuite.get_testsuite(ts_name,
                      'Verify that the ZD performs guest access policy on mesh network properly',
                      interactive_mode = attrs["interactive_mode"])

    ssid = "rat-gaWGS-mesh"

    test_order = 1
    test_added = 0

    for active_ap in sorted(active_ap_list):
        apcfg = ap_sym_dict[active_ap]
        ap_type_role = testsuite.getApTargetType(active_ap, apcfg)
        radio_mode_list = getRadioModeByAPModel(apcfg['model'])
        for radio_mode in radio_mode_list:
            test_cfg_list = defineTestCfgByAPModel(ssid, radio_mode, apcfg['model'], ap_type_role, zd_ip_addr)
            wgscfg = getWgsTypeByRadioAndAPModel(radio_mode, apcfg['model'])
            target_sta = target_sta_11na if radio_mode == 'na' else target_sta_11ng
            if target_sta:
                for test_cfg, test_name, common_name in test_cfg_list:
                    test_params = getTestParams( test_cfg,
                                                 getWgsCfg(wgscfg),
                                                 active_ap,
                                                 target_sta)
                    if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
                        test_added += 1
                    test_order += 1
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    createTestSuite(**_dict)

