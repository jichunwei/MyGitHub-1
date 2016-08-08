'''
Description:

Created on 2011-08-20
@author: serena.tan@ruckuswireless.com
'''


import sys
import time
import random
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant
from RuckusAutoTest.common import Ratutils as utils


def define_wlan_cfgs(user_cfg):
    wlan_cfgs = []
    
    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-0" % (time.strftime("%H%M%S")), 
                          auth = "open", wpa_ver = "", encryption = "none",
                          key_index = "", key_string = "",
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'],
                          set_name = 'Open None'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-1" % (time.strftime("%H%M%S")), 
                          auth = "open", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1", key_string = utils.make_random_string(10, "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'Open WEP-64'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-2" % (time.strftime("%H%M%S")), 
                          auth = "open", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1", key_string = utils.make_random_string(26, "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'Open WEP-128'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-3" % (time.strftime("%H%M%S")), 
                          auth = "shared", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1", key_string = utils.make_random_string(10, "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'Shared WEP-64'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-4" % (time.strftime("%H%M%S")), 
                          auth = "shared", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1", key_string = utils.make_random_string(26, "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'Shared WEP-128'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-5" % (time.strftime("%H%M%S")), 
                          auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'PSK WPA TKIP'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-6" % (time.strftime("%H%M%S")), 
                          auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                          key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'PSK WPA AES'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-7" % (time.strftime("%H%M%S")), 
                          auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'PSK WPA2 TKIP'))

    wlan_cfgs.append(dict(ssid = "rat-encrypt-webauth-%s-8" % (time.strftime("%H%M%S")), 
                          auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "", key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          do_webauth = True, auth_svr = "", do_tunnel = False, 
                          username = user_cfg['username'], password = user_cfg['password'], 
                          set_name = 'PSK WPA2 AES'))  
    
    return wlan_cfgs


def define_encryption_types_webauth_test_cfgs(tcfg, wlan_cfg, ap_sym):
    test_cfgs = []
    com_name = "[%s]" % wlan_cfg['set_name']

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%s Remove all wlans from ZD' % com_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%s Create a web auth wlan' % com_name
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg]}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_On_APs'
    common_name = '%s Verify the wlan on AP: %s' % (com_name, ap_sym)
    test_params = {'ap_tag': ap_sym, 'ssid': wlan_cfg['ssid'], 'romove_other_aps': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all wlans from station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate station' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%s Get station Wifi address' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "%s Station ping target ip '%s' before auth" % (com_name, tcfg['allowed_ip'])
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'ping_timeout_ms': 10000, 'dest_ip': tcfg['allowed_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD before auth' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'status': 'Unauthorized',
                   'radio_mode': tcfg['zd_sta_radio'], 'wlan_cfg': wlan_cfg, 'ap_tag': ap_sym}
    test_cfgs.append((test_params, test_name, common_name, 2, False))   
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%s Start browser in the station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    common_name = "%s Perform web auth in station" % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 
                   'username': tcfg['user_cfg']['username'],
                   'password': tcfg['user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))   

    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = "%s Station download file from web server" % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = '%s Close browser in the station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD after auth' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'status': 'Authorized', 
                   'radio_mode': tcfg['zd_sta_radio'], 'wlan_cfg': wlan_cfg, 
                   'ap_tag': ap_sym}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP'
    common_name = '%s Verify station info on AP: %s' % (com_name, ap_sym)
    test_params = {'ap_tag': ap_sym, 'sta_tag': tcfg['sta_ip_addr'], 'ssid': wlan_cfg['ssid']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_In_Tunnel_Mode'
    common_name = '%s Verify station traffic info in tunnel mode' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'ap_tag': ap_sym, 'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    return test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_sym = tcfg['active_ap']

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create the active AP:%s' % ap_sym
    test_cfgs.append(({'ap_tag': ap_sym, 'active_ap': ap_sym}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create the target station'
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'sta_ip_addr': tcfg['sta_ip_addr']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Disable the wlan service of all APs'
    test_params = {'cfg_type': 'init', 'all_ap_mac_list': tcfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = "Enable radio '%s' wlan service of %s" % (tcfg['active_radio'], ap_sym)
    test_params = {'ap_tag': ap_sym, 
                   'cfg_type': 'config',
                   'ap_cfg': {'wlan_service': True, 'radio': tcfg['active_radio']}}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create a local user'
    test_params = {'username': tcfg['user_cfg']['username'], 
                   'password': tcfg['user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    for wlan_cfg in tcfg['wlan_cfgs']:
        test_cfgs.extend(define_encryption_types_webauth_test_cfgs(tcfg, wlan_cfg, ap_sym))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the target station'
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD to cleanup'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD to cleanup'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable the wlan service of all APs'
    test_params = {'cfg_type': 'teardown', 'all_ap_mac_list': tcfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    return test_cfgs


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_station = (0, "ng"),
                 ts_name = ""
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        while True:
            active_ap = raw_input("Choose an active AP: ")
            if active_ap not in ap_sym_dict:
                print "AP[%s] doesn't exist." % active_ap
            
            else:
                break
            
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio() 
        
    else:
        active_ap = attrs["active_ap"]
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if target_sta_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, target_sta_radio)
        return
    
    active_radio = target_sta_radio
    #Client radio info shown in ZD
    zd_sta_radio = 'g' if active_radio == 'bg' else active_radio

    user_cfg = dict(username = 'ruckus_web_auth', password = 'ruckus_web_auth')

    wlan_cfgs = define_wlan_cfgs(user_cfg)
    
    tcfg = dict(all_ap_mac_list = tbcfg['ap_mac_list'],
                active_ap = active_ap,
                active_radio = active_radio,
                zd_sta_radio = zd_sta_radio,
                sta_ip_addr = sta_ip_addr,
                user_cfg = user_cfg,
                wlan_cfgs = wlan_cfgs,
                #The IP which client is allowed to access after authentication
                allowed_ip = '172.16.10.252',
                )
    
    test_cfgs = define_test_cfgs(tcfg)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        active_ap_status = ap_sym_dict[active_ap]['status']
        active_ap_role = ''
        res = re.search('Connected \((.+)\)', active_ap_status, re.I)
        if res:
            active_ap_role = ' - %s' % res.group(1).split(' ')[0]
            
        ts_name = "Mesh - Encryption Types Web Auth - %s%s - %s" 
        ts_name = ts_name % (active_ap_model, active_ap_role, active_radio)
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify different encryption types with Web authentication in mesh environment.",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest = True)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
    
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    