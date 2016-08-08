'''
Created on Dec 20, 2011

@author: serena.tan@ruckuswireless.com
'''


import sys
import time
from copy import deepcopy
import re

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


def choose_active_ap(ap_sym_dict, input_prompt = ''):
    message = "Choose an active AP: "
    if input_prompt:
        message = input_prompt
        
    while True:
        active_ap = raw_input(message)
        if active_ap not in ap_sym_dict:
            print "AP[%s] doesn't exist." % active_ap
            
        else:
            return active_ap
        

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

    
def client_connect_to_wlan(cfg):
    conf = {
        'tcid': '', 
        'sta_tag': '', 
        'ap_tag': '', 
        'wlan_cfg': {}, 
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
                       'verify_ip_subnet': False,
                       'start_browser': False}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    common_name = "%sStation '%s' perform web auth" % (tcid, sta_tag)
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
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    return test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_tag = tcfg['active_ap']
    ap_tag_2 = tcfg['active_ap_2']
    sta_tag = tcfg['target_sta']
    radio_mode = tcfg['active_radio']
    target_ip = tcfg['target_ip']
    user_cfg = tcfg['local_user_cfg']

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % ap_tag
    test_params = {'ap_tag': ap_tag, 'active_ap': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % ap_tag_2
    test_params = {'ap_tag': ap_tag_2, 'active_ap': ap_tag_2}
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
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create local user: %s' % tcfg['local_user_cfg']['username']
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    
    tcid = '[Grace period - client reconnect after deleted by ZD]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-zd-delete-%s' % time.strftime("%H%M%S")
    grace_period = 2
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign WLAN group '%s' to AP: %s" % (tcid, tcfg['wg_cfg']['name'], ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect within grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'disconnect_method': 'delete_client_on_zd',
                   'reconnect_to_wlan': False,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 1))
    
    
    tcid = '[Grace period - client reconnect to another AP]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-diff-ap-%s' % time.strftime("%H%M%S")
    grace_period = 3
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign WLAN group '%s' to AP: %s" % (tcid, tcfg['wg_cfg']['name'], ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid, 
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sSet WLAN group of AP '%s' to 'Default'" % (tcid, ap_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'username': user_cfg['username'],
                   'wlan_cfg': wlan_cfg,
                   'disconnect_method': 'set_wg_to_default',
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign WLAN group '%s' to AP: %s" % (tcid, tcfg['wg_cfg']['name'], ap_tag_2)
    test_params = {'active_ap': ap_tag_2,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': tcfg['active_radio']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect within grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag_2,
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'radio_mode': radio_mode,
                   'target_ip': tcfg['target_ip'],
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': True,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_params = {'tcid': tcid, 
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag_2,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))

    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 1))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign 'Default' WLAN group to AP: %s" % (tcid, ap_tag_2)
    test_params = {'active_ap': ap_tag_2,
                   'wlan_group_name': 'Default', 
                   'radio_mode': tcfg['active_radio']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))


    tcid = '[Grace period - client roam to another AP]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-roam-ap-%s' % time.strftime("%H%M%S")
    grace_period = 3
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign WLAN group '%s' to AP: %s" % (tcid, tcfg['wg_cfg']['name'], ap_tag)
    test_params = {'active_ap': ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid, 
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "%sAssign WLAN group '%s' to AP: %s" % (tcid, tcfg['wg_cfg']['name'], ap_tag_2)
    test_params = {'active_ap': ap_tag_2,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Roam_To_Another_AP'
    common_name = "%sMake client roam to AP: %s" % (tcid, ap_tag_2)
    test_params = {'current_ap_tag': ap_tag,
                   'current_radio_mode': radio_mode,
                   'target_ap_tag': ap_tag_2,
                   'target_radio_mode': radio_mode,
                   'wlan_cfg': wlan_cfg,
                   'sta_tag': sta_tag,
                   'username': user_cfg['username']
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect within grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag_2,
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'no_need_auth': True,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'radio_mode': radio_mode,
                   'target_ip': tcfg['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect beyond grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag_2,
                   'grace_period': grace_period,
                   'reconnect_within_gp': False,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'radio_mode': radio_mode,
                   'target_ip': tcfg['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid, 
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag_2,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all Users to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))  
    
    return test_cfgs


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode = True,
                 active_ap = '',
                 active_ap_2 = '',
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
        active_ap = choose_active_ap(ap_sym_dict, "Choose an active AP: ")
        active_ap_2 = choose_active_ap(ap_sym_dict, "Choose another active AP: ")
        
        target_sta = testsuite.getTargetStation(sta_ip_list)
        active_radio = testsuite.get_target_sta_radio()
        
    else:
        active_ap = attrs["active_ap"]
        active_ap_2 = attrs["active_ap_2"]
        target_sta = attrs['target_sta']
        active_radio = attrs["active_radio"]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if active_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, active_radio)
        return
    
    local_user_cfg = {'username': 'local_user', 'password': 'local_user',}
    
    wlan_cfg = {
        'ssid': "", 
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': True, 
        'auth_svr': "Local Database", 
        }
    
    wg_cfg = {
        'name': 'rat-wg-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for Web Auth',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    tcfg = dict(active_ap = active_ap,
                active_ap_2 = active_ap_2,
                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                local_user_cfg = local_user_cfg,
                wg_cfg = wg_cfg,
                target_ip = '172.16.10.252'
                )
    
    test_cfgs = define_test_cfgs(tcfg)

    test_cfgs = decorate_common_name(test_cfgs)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Web Auth - Grace Period - Client Reconnect - %s - %s" \
                  % (active_ap_model, active_radio)
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the grace period in Web Auth WLAN.",
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
    