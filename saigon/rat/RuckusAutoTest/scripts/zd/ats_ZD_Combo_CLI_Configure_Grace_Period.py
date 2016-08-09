'''
Created on Dec 20, 2011

@author: serena.tan@ruckuswireless.com
'''


import sys
import time
from copy import deepcopy
import re
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


GP_RANGE = (2, 144000)


def decorate_common_name(test_cfgs):
    new_test_cfgs = []
    pre_tcid = ''
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        res = re.search("^\[(.*)\]", common_name)
        if res:
            tcid = res.group(1)
            if tcid != pre_tcid:
                pre_tcid = tcid
                counter = 1
            
            else:
                counter += 1
            
            common_name = common_name.replace("]", "] %s." % counter)
                              
        new_test_cfgs.append((test_params, testname, common_name, exc_level, is_cleanup))
    
    return new_test_cfgs


def remove_wlan_from_wg(tcid, wlan_cfg, wg_cfg, exe_level):
    test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
    common_name = "%sRemove WLAN '%s' from the WLAN group" % (tcid, wlan_cfg['ssid'])
    test_params = {'wgs_cfg': wg_cfg,
                   'wlan_list': [wlan_cfg['ssid']]}
    
    return (test_params, test_name, common_name, exe_level, False)


def remove_all_wlans(tcid, exe_level = 2):
    test_name = 'CB_ZD_Remove_All_Wlans'   
    common_name = "%sRemove all WLANs from ZD" % tcid
    
    return ({}, test_name, common_name, exe_level, False)


def config_wlan_in_zdcli(tcid, wlan_cfg, exe_level = 1):
    test_cfgs = []
    
    test_name = 'CB_ZD_CLI_Create_Wlan'   
    common_name = "%sConfigure WLAN '%s' in ZD CLI" % (tcid, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_conf': wlan_cfg}, test_name, common_name, exe_level, False))

    test_name = 'CB_ZD_CLI_Verify_All_Wlan_Info_Between_Set_Get'   
    common_name = "%sVerify WLAN between CLI set and CLI get" % tcid
    test_cfgs.append(({'cli_set_list': [wlan_cfg]}, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_CLI_Verify_All_Wlan_Info_Between_CLISet_GUIGet'   
    common_name = "%sVerify WLAN between Cli set and GUI get" % tcid
    test_cfgs.append(({'cli_set_list': [wlan_cfg]}, test_name, common_name, 2, False))
    
    return test_cfgs
   

def client_connect_to_wlan(cfg):
    conf = {
        'tcid': '', 
        'sta_tag': '', 
        'ap_tag': '', 
        'wlan_cfg': {}, 
        'guest_access_cfg': {}, 
        'guest_pass_cfg': {},
        'user_cfg': {}, 
        'radio_mode': '', 
        'target_ip': '', 
        'associate_wlan': True,
        }
    conf.update(cfg)
    test_cfgs = []
    tcid = conf['tcid']
    sta_tag = conf['sta_tag']
    wlan_cfg = conf['wlan_cfg']
    
    if conf['associate_wlan']:
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        common_name = "%sStation '%s' associate WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
        test_params = {'sta_tag': sta_tag, 
                       'wlan_cfg': wlan_cfg,
                       'verify_ip_subnet': False,}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    if wlan_cfg.get('web_auth'):
        test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
        common_name = "%sStation '%s' perform web auth" % (tcid, sta_tag)
        test_params = {'sta_tag': sta_tag, 
                       'username': conf['user_cfg']['username'],
                       'password': conf['user_cfg']['password'],
                       'start_browser_before_auth': True,
                       'close_browser_after_auth': True}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    elif wlan_cfg.get('type') == 'guest':
        test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
        common_name = "%sPerform guest auth in station: %s" % (tcid, sta_tag)
        test_params = {'sta_tag': sta_tag, 
                       'use_tou': conf['guest_access_cfg']['use_tou'], 
                       'redirect_url': conf['guest_access_cfg']['redirect_url'], 
                       'no_auth': not conf['guest_access_cfg']['use_guestpass_auth'],
                       'start_browser_before_auth': True,
                       'close_browser_after_auth': True}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    elif wlan_cfg.get('type') == 'hotspot':
        test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
        common_name = "%sStation '%s' perform hotspot auth" % (tcid, sta_tag)
        test_params = {'sta_tag': sta_tag, 
                       'username': conf['user_cfg']['username'],
                       'password': conf['user_cfg']['password'],
                       'start_browser_before_auth': True,
                       'close_browser_after_auth': True}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Verify_Station_Connectivity'
    common_name = "%sVerify the connectivity of station: %s" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': conf['ap_tag'],
                   'wlan_cfg': wlan_cfg,
                   'status': 'Authorized',
                   'username': conf['user_cfg']['username'],
                   'guest_name': conf['guest_pass_cfg'].get('guest_fullname'),
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    return test_cfgs

     
def grace_period_test(cfg):
    conf = {
        'tcid': '',
        'sta_tag': '',
        'ap_tag': '',
        'wlan_cfg': {},
        'wg_cfg': {},
        'guest_access_cfg': {},
        'guest_pass_cfg': {},
        'user_cfg': {},
        'radio_mode': '',
        'target_ip': '',
        'grace_period': None,
        }
    conf.update(cfg)
    tcid = conf['tcid']
    sta_tag = conf['sta_tag']
    grace_period = conf['grace_period']
    wlan_cfg = conf['wlan_cfg']
    if wlan_cfg.get('type') == 'guest-access':
        wlan_cfg['type'] = 'guest'
        
    test_cfgs = []
    
    test_name = 'CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group'   
    common_name = "%sRemove WLAN from Default WLAN group" % tcid
    test_params = {'wlan_name_list': [wlan_cfg['ssid']],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'   
    common_name = "%sAssign WLAN to WLAN group: %s" % (tcid, conf['wg_cfg']['name'])
    test_params = {'wlangroup_name': conf['wg_cfg']['name'],
                   'wlan_name_list': [wlan_cfg['ssid']],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    if wlan_cfg.get('type') == 'guest':
        test_name = 'CB_ZD_Set_GuestAccess_Policy'
        common_name = '%sSet the guest access policy' % tcid
        test_cfgs.append((conf['guest_access_cfg'], test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Generate_Guest_Pass'
        common_name = '%sGenerate a guest pass' % tcid
        test_cfgs.append((conf['guest_pass_cfg'], test_name, common_name, 2, False))
    
    test_params = deepcopy(conf)
    test_cfgs.extend(client_connect_to_wlan(conf))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect within grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': conf['ap_tag'],
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'no_need_auth': True,
                   'wlan_cfg': wlan_cfg,
                   'username': conf['user_cfg']['username'],
                   'guest_name': conf['guest_pass_cfg'].get('guest_fullname'),
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect beyond grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': conf['ap_tag'],
                   'grace_period': grace_period,
                   'reconnect_within_gp': False,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'username': conf['user_cfg']['username'],
                   'guest_name': conf['guest_pass_cfg'].get('guest_fullname'),
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = deepcopy(conf)
    test_params['associate_wlan'] = False 
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    return test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_tag = tcfg['active_ap']
    sta_tag = tcfg['target_sta']
    radio_mode = tcfg['active_radio']
    target_ip = tcfg['target_ip']

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % ap_tag
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station: %s' % sta_tag
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create WLAN group: %s" % (tcfg['wg_cfg']['name']) 
    test_cfgs.append(({'wgs_cfg': tcfg['wg_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the WLAN group to radio '%s' of AP: %s" % (radio_mode, ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create local user: %s' % tcfg['local_user_cfg']['username']
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    
    tcid = "[Enable grace period in web auth WLAN]"
    wlan_cfg = deepcopy(tcfg['web_auth_wlan_cfg'])
    wlan_cfg['grace_period'] = random.randint(GP_RANGE[0], GP_RANGE[1])
    test_cfgs.extend(config_wlan_in_zdcli(tcid, wlan_cfg))
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'user_cfg': deepcopy(tcfg['local_user_cfg']),
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'grace_period': wlan_cfg['grace_period'],
                   }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    tcid = "[Disable grace period in web auth WLAN]"
    wlan_cfg = deepcopy(tcfg['web_auth_wlan_cfg'])
    wlan_cfg['grace_period'] = False
    test_cfgs.extend(config_wlan_in_zdcli(tcid, wlan_cfg, 2))
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 1))
    test_cfgs.append(remove_all_wlans(tcid, 2))
    

    tcid = "[Enable grace period in guest access WLAN]"
    wlan_cfg = deepcopy(tcfg['guest_wlan_cfg'])
    wlan_cfg['grace_period'] = random.randint(GP_RANGE[0], GP_RANGE[1])
    guest_pass_cfg = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg['guest_fullname'] = 'ruckus-guest'
    test_cfgs.extend(config_wlan_in_zdcli(tcid, wlan_cfg))
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg,
                   'user_cfg': deepcopy(tcfg['local_user_cfg']),
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'grace_period': wlan_cfg['grace_period'],
                   }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    tcid = "[Disable grace period in guest access WLAN]"
    wlan_cfg = deepcopy(tcfg['guest_wlan_cfg'])
    wlan_cfg['grace_period'] = False
    test_cfgs.extend(config_wlan_in_zdcli(tcid, wlan_cfg, 2))
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 1))
    test_cfgs.append(remove_all_wlans(tcid, 2))
    
    
    tcid = "[Enable grace period in hotspot profile]"
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['idle_timeout'] = random.randint(GP_RANGE[0], GP_RANGE[1])
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'   
    common_name = "%sConfigure and verify hotspot '%s' in ZD CLI" % (tcid, hotspot_cfg['name'])
    test_cfgs.append(({'hotspot_conf': hotspot_cfg}, test_name, common_name, 1, False))
    
    wlan_cfg = deepcopy(tcfg['hotspot_wlan_cfg'])
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    test_name = 'CB_ZD_Create_Wlan'   
    common_name = "%sCreate a hotspot WLAN in ZD GUI" % tcid
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg]}, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'user_cfg': deepcopy(tcfg['local_user_cfg']),
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'grace_period': hotspot_cfg['idle_timeout'],
                   }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    tcid = "[Disable grace period in hotspot profile]"
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['idle_timeout'] = 'Disabled'
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'   
    common_name = "%sConfigure and verify hotspot '%s' in ZD CLI" % (tcid, hotspot_cfg['name'])
    test_cfgs.append(({'hotspot_conf': hotspot_cfg}, test_name, common_name, 1, False))
    
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Remove all guest passes to clean up'
    test_cfgs.append(({}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Profiles'
    common_name = 'Remove all hotspot profiles to clean up'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all Users to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 
    
    return test_cfgs


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 target_sta = '',
                 active_radio = '',
                 ts_name = "",
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
            
        target_sta = testsuite.getTargetStation(sta_ip_list)
        active_radio = testsuite.get_target_sta_radio()
        
    else:
        active_ap = attrs["active_ap"]
        target_sta = attrs['target_sta']
        active_radio = attrs["active_radio"]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if active_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, active_radio)
        return
    
    local_user_cfg = {'username': 'local_user', 'password': 'local_user',}
    
    web_auth_wlan_cfg = {
        'ssid': "gp-web-%s" % time.strftime("%H%M%S"),
        'auth': "open", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'web_auth': True, 
        'auth_server': "local", 
        'grace_period': None,
        }
    web_auth_wlan_cfg['name'] = web_auth_wlan_cfg['ssid']
    
    guest_wlan_cfg = {
        'ssid': "gp-guest-%s" % time.strftime("%H%M%S"), 
        'type': 'guest-access',
        'auth': "open", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'grace_period': None,
        }
    guest_wlan_cfg['name'] = guest_wlan_cfg['ssid']
    
    guest_pass_cfg = {
        'is_shared': 'No', 
        'auth_ser': 'Local Database',
        'username': local_user_cfg['username'], 
        'password': local_user_cfg['password'],
        'type': 'single', 
        'guest_fullname': '', 
        'duration': '300', 
        'duration_unit': 'Days', 
        'wlan': '',
        'key': '',
        }

    guest_access_cfg = {
        'use_guestpass_auth': True,
        'use_tou': False, 
        'redirect_url': '',
        }
    
    hotspot_cfg = {
        'name': "gp-hotspot-%s" % time.strftime("%H%M%S"),
        'login_page_url': 'https://192.168.0.250/slogin.html',
        'idle_timeout': None,
        }
    
    hotspot_wlan_cfg = {
        'ssid': "wispr-%s" % time.strftime("%H%M%S"),
        'type': 'hotspot',
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'hotspot_profile': "",
        }
    
    wg_cfg = {
        'name': 'rat-gp-wg-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for Grace Period Test',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    tcfg = dict(active_ap = active_ap,
                active_radio = active_radio,
                target_sta = target_sta,
                web_auth_wlan_cfg = web_auth_wlan_cfg,
                guest_wlan_cfg = guest_wlan_cfg,
                guest_pass_cfg = guest_pass_cfg,
                guest_access_cfg = guest_access_cfg,
                hotspot_cfg = hotspot_cfg,
                hotspot_wlan_cfg= hotspot_wlan_cfg,
                local_user_cfg = local_user_cfg,
                wg_cfg = wg_cfg,
                target_ip = '172.16.10.252'
                )
    
    test_cfgs = define_test_cfgs(tcfg)

    test_cfgs = decorate_common_name(test_cfgs)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "ZD CLI - Configure Grace Period - %s - %s" 
        ts_name = ts_name % (active_ap_model, active_radio)
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Configure grace period in ZD CLI.",
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
    