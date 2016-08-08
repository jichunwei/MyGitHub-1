import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.tests.zd import libZD_TestConfig as lib_cfg 

def tcid(sub_id, tcid, ap_model_id, ap_role_id):
    return "TCID:33.03.%02d.%02d.%s.%s" % (sub_id, tcid, ap_model_id, ap_role_id)

def get_wlan_cfg_list():
    wlan_cfg_list = dict()    
    wlan_cfg_list['open'] = lib_cfg.get_wlan_profile('open_none')[0]
    wlan_cfg_list['open'].update({'ssid': 'rat-zd-11n-only-mode'})
    wlan_cfg_list['aes'] = lib_cfg.get_wlan_profile('wpa_psk_aes')[0]
    wlan_cfg_list['aes'].update({'ssid': 'rat-zd-11n-only-mode'})
    wlan_cfg_list['wep'] = lib_cfg.get_wlan_profile('open_wep_64')[0]
    wlan_cfg_list['wep'].update({'ssid': 'rat-zd-11n-only-mode'})
    wlan_cfg_list['tkip'] = lib_cfg.get_wlan_profile('wpa_psk_tkip')[0]
    wlan_cfg_list['tkip'].update({'ssid': 'rat-zd-11n-only-mode'})
    return wlan_cfg_list

def get_wlan_group_cfg(wlan_groups_params):
    wgs_cfg = dict(
        description = 'rat-zd-11n-only-mode',
        name = 'rat-zd-11n-only-mode',
        vlan_override = False,
        wlan_member = {'rat-zd-11n-only-mode':{'vlan_override':'No Change', 'original_vlan':'None'}}        
    )

    wgs_cfg.update(wlan_groups_params)
    return wgs_cfg


def defineTestConfiguration(sub_id, active_ap, ap_radio, ap_radio_frequency, ap_model_id, ap_role_id, ap_type, sta_support_radio, mode_11n, target_station, encryption_name):
    test_cfgs = []
    test_name = 'AP_11N_Only_Mode'
    if mode_11n:
        if sta_support_radio in ["11a/b/g"] and encryption_name in ["open","aes"]:
            common_name = '%s client can\'t connect %s with %s when 11n-only %sG %s' % (sta_support_radio, ap_type, encryption_name, 
                                                                                    ap_radio_frequency, {True:'enabled', False: 'disabled'}[mode_11n])
        else:
            common_name = '%s client can connect %s with %s when 11n-only %sG %s' % (sta_support_radio, ap_type, encryption_name, 
                                                                                    ap_radio_frequency, {True:'enabled', False: 'disabled'}[mode_11n])
    else:
            common_name = '%s client can connect %s with %s when 11n-only %sG %s' % (sta_support_radio, ap_type, encryption_name, 
                                                                                    ap_radio_frequency, {True:'enabled', False: 'disabled'}[mode_11n])

    test_cfgs.append(({'active_ap':active_ap,
                       'radio': ap_radio,
                       'target_station': target_station,
                       'mode_11n': mode_11n,
                       'sta_support_radio': sta_support_radio,
                       'wlan_cfg': get_wlan_cfg_list()[encryption_name],
                       'wlan_group_cfg': get_wlan_group_cfg({})},
                      test_name, common_name, tcid(sub_id, 1, ap_model_id, ap_role_id)))
    return test_cfgs

def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

    target_station = testsuite.getTargetStation(sta_ip_list)
    sta_support_radio = testsuite.getStationSupportRadio(['11a/b/g/n', '11a/b/g'], target_station)

    sub_id = 1    
    for mode_11n in [True, False]:
        test_cfgs = []
        for active_ap in active_ap_list:
            for ap_radio_frequency in ["2.4","5.0"]:    
                active_ap_conf = ap_sym_dict[active_ap]
                ap_model_id = const.get_ap_model_id(active_ap_conf['model'])
                ap_role_id = const.get_ap_role_by_status(active_ap_conf['status'])
                ap_type = testsuite.getApTargetType(active_ap, active_ap_conf)
                ap_radio = {"5.0":"na", "2.4":"ng"}[ap_radio_frequency]                
                for encryption_name in get_wlan_cfg_list():
                    generate = False
                    if (mode_11n and sta_support_radio in ['11a/b/g/n', '11a/b/g'] and 
                        active_ap_conf['model'].upper() == "ZF7962" and encryption_name in ["open", "aes"]): generate = True
                    if (mode_11n and sta_support_radio in ["11a/b/g"] and 
                        active_ap_conf['model'].upper() == "ZF7962" and encryption_name in ["wep", "tkip"]): generate = True
                    if (mode_11n and sta_support_radio in ["11a/b/g"] 
                        and active_ap_conf['model'].upper() == "ZF2942" and encryption_name in ["open", "aes"]
                        and ap_radio_frequency == "2.4"): generate = True
                    if (not mode_11n and sta_support_radio in ["11a/b/g"] and encryption_name in ["open", "aes"] 
                        and active_ap_conf['model'].upper() == "ZF7962"): generate = True 
                    if generate:   
                        test_cfgs.extend(defineTestConfiguration(sub_id, active_ap, ap_radio, ap_radio_frequency, ap_model_id, ap_role_id, ap_type,
                                                             sta_support_radio, mode_11n, target_station, encryption_name))
                      
        if test_cfgs:
            ts_name = "%s11N-Only Mode for AP" % {True:"", False: "Not "}[mode_11n]            
            ts = testsuite.get_testsuite(ts_name, 'Verify 11N-Only Mode feature on AP')
            test_order = 1     
            test_added = 0   
            for test_params, test_name, common_name, tcid in test_cfgs:
                cname = "%s - %s" % (tcid, common_name)
                if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
                    test_added += 1
                test_order += 1            
                print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, cname)
            sub_id += 1
            print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
