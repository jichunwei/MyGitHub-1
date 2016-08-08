'''
Description:
    1). Create a station.
    2). Create an active ap[Single band/Dual band AP].
    3). Create a user account[Local User/LDAP User/AD User/Radius User].
    4). Create a guest policy.
    5). Create a open-none WLAN.
    6). Verify the guest policy on ZD.
    7). Generate a Guest Pass with the user account.
    8). Associate ssid to station.
    9). Verify the station info on ZD.
    10).Ping to target server from station befor perform guestpass auth.
    11).Verify the guest policy is corrected.
    12).Perform the guestpass auth with the redirect page from the station.
    13).Ping to target server from station after perform guestpass auth.
        [if it have restricted subnet list, ping the restricted subnet.]
    14).Verify the station info on ZD.
    15).Verify the station traffic is the corrected behavior.

Created on 2011-08-15
@author: serena.tan@ruckuswireless.com
'''


import sys
import time
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant
from RuckusAutoTest.common import Ratutils as utils


def define_guest_access_cfgs():
    define_guest_access_cfgs = []
    
    restricted_ips = ['172.21.0.252', '172.22.0.252', '172.23.0.252', '172.24.0.252', '172.25.0.252']
    restricted_subnet_list = []
    for ip in restricted_ips:
        restricted_subnet_list.append("%s/%s" % (utils.get_network_address(ip), utils.get_subnet_mask(ip)))
 
    define_guest_access_cfgs.append(dict(use_guestpass_auth = True , use_tou = False, 
                                         redirect_url = '',
                                         target_url = 'http://172.16.10.252/',
                                         set_name = 'Auth/No TOU/No Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = True , use_tou = False, 
                                         redirect_url = 'http://172.16.10.252/',
                                         target_url = 'http://www.example.net/',
                                         set_name= 'Auth/No TOU/Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = True , use_tou = True , 
                                         redirect_url = '',
                                         target_url = 'http://172.16.10.252/',
                                         set_name= 'Auth/TOU/No Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = True , use_tou = True , 
                                         redirect_url = 'http://172.16.10.252/',
                                         target_url = 'http://www.example.net/',
                                         set_name= 'Auth/TOU/Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = False, use_tou = False, 
                                         redirect_url = '',
                                         target_url = 'http://172.16.10.252/',
                                         set_name= 'No Auth/No TOU/No Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = False, use_tou = False, 
                                         redirect_url = 'http://172.16.10.252/',
                                         target_url = 'http://www.example.net/',
                                         set_name= 'No Auth/No TOU/Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = False, use_tou = True , 
                                         redirect_url = '',
                                         target_url = 'http://172.16.10.252/',
                                         set_name= 'No Auth/TOU/No Redirection'))
    
    define_guest_access_cfgs.append(dict(use_guestpass_auth = False, use_tou = True , 
                                         redirect_url = 'http://172.16.10.252/',
                                         target_url = 'http://www.example.net/',
                                         set_name= 'No Auth/TOU/Redirection'))

    define_guest_access_cfgs.append(dict(use_guestpass_auth = False, use_tou = True , 
                                         redirect_url = 'http://172.16.10.252/',
                                         target_url = 'http://www.example.net/',
                                         restricted_subnet_list = restricted_subnet_list,
                                         set_name= 'Restricted Subnet Access'))
    
    return define_guest_access_cfgs


def define_guest_access_test_cfgs(tcfg, guest_access_cfg, ap_sym):
    test_cfgs = []
    com_name = "[%s]" % guest_access_cfg['set_name']
            
    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = '%s Set the guest access policy' % com_name
    test_params = {'use_guestpass_auth': guest_access_cfg['use_guestpass_auth'],
                   'use_tou': guest_access_cfg['use_tou'],
                   'redirect_url': guest_access_cfg['redirect_url']}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    if guest_access_cfg['set_name'] == 'Restricted Subnet Access':
        test_name = 'CB_ZD_Create_Guest_Restricted_Subnet_Access'
        common_name = '%s Create the guest restricted subnets' % com_name
        test_params = {'restricted_subnet_list': guest_access_cfg['restricted_subnet_list']}
        test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all wlans from station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate station' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'wlan_cfg': tcfg['wlan_cfg']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%s Get station Wifi address' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "%s Station ping ip '%s' before auth" % (com_name, tcfg['allowed_ip'])
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 
                   'ping_timeout_ms': 10000, 
                   'dest_ip': tcfg['allowed_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD before auth' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 
                   'status': 'Unauthorized',
                   'radio_mode': tcfg['zd_sta_radio'], 
                   'wlan_cfg': tcfg['wlan_cfg'], 
                   'ap_tag': ap_sym}
    test_cfgs.append((test_params, test_name, common_name, 2, False))   
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%s Start browser in the station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%s Perform guest authentication in station" % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 
                   'use_tou': guest_access_cfg['use_tou'], 
                   'redirect_url': guest_access_cfg['redirect_url'],
                   'target_url': guest_access_cfg['target_url'],
                   'no_auth': not guest_access_cfg['use_guestpass_auth']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = "%s Station download file from web server" % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))

    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = '%s Close browser in the station' % com_name
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "%s Station ping ZD '%s' after auth" % (com_name, tcfg['zd_ip'])
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'ping_timeout_ms': 10000, 'dest_ip': tcfg['zd_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    if guest_access_cfg['set_name'] == 'Restricted Subnet Access':
        for restricted_subnet in guest_access_cfg['restricted_subnet_list']:
            restricted_ip = restricted_subnet.split('/')[0]
            test_name = 'CB_Station_Ping_Dest_Is_Denied'
            common_name = "%s Station ping restricted ip '%s' after auth" % (com_name, restricted_ip)
            test_params = {'sta_tag': tcfg['sta_ip_addr'], 'ping_timeout_ms': 10000, 'dest_ip': restricted_ip}
            test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '%s Verify station info on ZD after auth' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'status': 'Authorized', 
                   'radio_mode': tcfg['zd_sta_radio'], 'wlan_cfg': tcfg['wlan_cfg'], 
                   'ap_tag': ap_sym, 'guest_name': tcfg['generate_guestpass_cfg']['guest_fullname'],
                   'use_guestpass_auth': guest_access_cfg['use_guestpass_auth']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP'
    common_name = '%s Verify station info on AP: %s' % (com_name, ap_sym)
    test_params = {'ap_tag': ap_sym, 'sta_tag': tcfg['sta_ip_addr'], 'ssid': tcfg['wlan_cfg']['ssid']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_In_Tunnel_Mode'
    common_name = '%s Verify station traffic info in tunnel mode' % com_name
    test_params = {'sta_tag': tcfg['sta_ip_addr'], 'ap_tag': ap_sym, 'wlan_cfg': tcfg['wlan_cfg']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    return test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_sym = tcfg['active_ap']
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create the active AP: %s' % ap_sym
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
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a guest access wlan'
    test_cfgs.append(({'wlan_cfg_list': [tcfg['wlan_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Wlan_On_APs'
    common_name = 'Verify wlan on AP: %s' % ap_sym
    test_params = {'ap_tag': ap_sym, 'ssid': tcfg['wlan_cfg']['ssid'], 'romove_other_aps': False}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create a local user'
    test_params = {'username': tcfg['user_cfg']['username'], 
                   'password': tcfg['user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = 'Generate a guest pass'
    test_cfgs.append((tcfg['generate_guestpass_cfg'], test_name, common_name, 0, False))
    
    for guest_access_cfg in tcfg['guest_access_cfgs']:
        test_cfgs.extend(define_guest_access_test_cfgs(tcfg, guest_access_cfg, ap_sym))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the target station'
    test_cfgs.append(({'sta_tag': tcfg['sta_ip_addr']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Remove all guest passes from ZD to cleanup'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
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
    
    user_cfg = dict(username = 'ruckus_guest_access', password = 'ruckus_guest_access')
    
    wlan_cfg = dict(ssid = "rat-wlan-guestaccess-%s" % (time.strftime("%H%M%S")),
                    auth = "open", encryption = "none", 
                    type = 'guest', do_tunnel = False)
    
    generate_guestpass_cfg = dict(is_shared = 'No', auth_ser = 'Local Database',
                                  username = user_cfg['username'], password = user_cfg['password'],
                                  type = 'single', guest_fullname = 'Rat_Guest', 
                                  duration = '5', duration_unit = 'Days', 
                                  wlan = wlan_cfg['ssid'], key = '')
    
    guest_access_cfgs = define_guest_access_cfgs()
    
    tcfg = dict(all_ap_mac_list = tbcfg['ap_mac_list'],
                active_ap = active_ap,
                active_radio = active_radio,
                zd_sta_radio = zd_sta_radio,
                sta_ip_addr = sta_ip_addr,
                zd_ip = tbcfg['ZD']['ip_addr'],
                user_cfg = user_cfg,
                wlan_cfg = wlan_cfg,
                generate_guestpass_cfg = generate_guestpass_cfg,
                guest_access_cfgs = guest_access_cfgs,
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
            
        ts_name = "Mesh - Guest Access - %s%s - %s" % (active_ap_model, active_ap_role, active_radio)

    ts = testsuite.get_testsuite(ts_name,
                                 'Verify that the ZD performs guest access policy on mesh network properly',
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
    
