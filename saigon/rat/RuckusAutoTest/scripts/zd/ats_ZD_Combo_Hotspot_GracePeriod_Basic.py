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


RANDOM_TEST_RANGE = (3, 143999)


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
        'hotspot_cfg': {},
        'wlan_cfg': {},
        'wg_cfg': {},
        'user_cfg': {},
        'radio_mode': '',
        'random': False,
        'random_range': RANDOM_TEST_RANGE,
        'grace_period': None,
        'target_ip': '',
        }
    conf.update(cfg)
    tcid = conf['tcid']
    sta_tag = conf['sta_tag']
    wlan_cfg = conf['wlan_cfg']
    grace_period = conf['grace_period']
    test_cfgs = []
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate a hotspot WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'hotspot_cfg': conf['hotspot_cfg'],
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': conf['wg_cfg'],
                   'random': conf['random'],
                   'random_range': conf['random_range'],
                   'grace_period': conf['grace_period'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
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
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = deepcopy(conf)
    test_params['associate_wlan'] = False 
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, conf['wg_cfg'], 1))
    
    return test_cfgs


def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_tag = tcfg['active_ap']
    sta_tag = tcfg['target_sta']
    radio_mode = tcfg['active_radio']
    target_ip = tcfg['target_ip']
    user_cfg = tcfg['local_user_cfg']

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
    
    
    tcid = '[Grace period range is correct]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-range-%s' % time.strftime("%H%M%S")
    
    grace_period = 1
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%s Minimum grace period '%s' can be set" % (tcid, grace_period)
    test_params = {'hotspot_cfg': hotspot_cfg, 
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    grace_period = 144000
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%s Maximum grace period '%s' can be set" % (tcid, grace_period)
    test_params = {'hotspot_cfg': hotspot_cfg, 
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%s Random grace period from '%s' to '%s' can be set"
    common_name = common_name % (tcid, RANDOM_TEST_RANGE[0], RANDOM_TEST_RANGE[1])
    test_params = {'hotspot_cfg': hotspot_cfg, 
                   'random': True,
                   'random_range': RANDOM_TEST_RANGE,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    grace_period = ''
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%s Empty grace period cannot be set" % tcid
    test_params = {'hotspot_cfg': hotspot_cfg, 
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    grace_period = 0
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%s Grace period '%s' cannot be set" % (tcid, grace_period)
    test_params = {'hotspot_cfg': hotspot_cfg, 
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    grace_period = 144001
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%s Grace period '%s' cannot be set" % (tcid, grace_period)
    test_params = {'hotspot_cfg': hotspot_cfg, 
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    
    tcid = '[Minimum grace period works]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-mini-%s' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-mini-%s' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'grace_period': 2,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(grace_period_test(test_params))
    

    tcid = '[Maximum grace period works]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-max-%s' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-max-%s' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'grace_period': 144000,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(grace_period_test(test_params))

    
    tcid = '[Random active grace period works]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-random-%s' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-random-%s' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'random': True,
                   'random_range': RANDOM_TEST_RANGE,
                   'target_ip': target_ip
                   }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Profiles'
    common_name = 'Remove all hotspot profiles to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all Users to clean up'
    test_cfgs.append(({}, test_name, common_name, 1, False))  
    
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
        active_ap = choose_active_ap(ap_sym_dict, "Choose an active AP: ")
            
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
    
    hotspot_cfg = {
        'name': '',
        'login_page': 'http://192.168.0.250/login.html',
        'idle_timeout': None,
        'auth_svr': 'Local Database',
        }
 
    wlan_cfg = {
        'ssid': "", 
        'type': 'hotspot',
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'hotspot_profile': "",
        }
    
    wg_cfg = {
        'name': 'rat-wg-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for Hotspot',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    tcfg = dict(active_ap = active_ap,
                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                hotspot_cfg = hotspot_cfg,
                local_user_cfg = local_user_cfg,
                wg_cfg = wg_cfg,
                target_ip = '172.16.10.252'
                )
    
    test_cfgs = define_test_cfgs(tcfg)

    test_cfgs = decorate_common_name(test_cfgs)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Hotspot - Grace Period - Basic - %s - %s" \
                  % (active_ap_model, active_radio)
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the grace period in Hotspot WLAN.",
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
    