'''
Created on Dec 20, 2011

@author: serena.tan@ruckuswireless.com
'''


import sys
import time
import re
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant


VLAN_ID = '10'


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
        'guest_access_cfg': {}, 
        'guest_pass_cfg': {},
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
        if not wlan_cfg['vlan_id']:
            expected_subnet = "192.168.0.252/255.255.255.0"
        
        elif wlan_cfg['vlan_id'] == '10':
            expected_subnet = "192.168.10.252/255.255.255.0"
            
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        common_name = "%sStation '%s' associate WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
        test_params = {'sta_tag': sta_tag, 
                       'wlan_cfg': wlan_cfg,
                       'expected_subnet': expected_subnet,
                       'start_browser': False}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%sPerform guest auth in station: %s" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag, 
                   'use_tou': conf['guest_access_cfg']['use_tou'], 
                   'redirect_url': conf['guest_access_cfg']['redirect_url'], 
                   'no_auth': not conf['guest_access_cfg']['use_guestpass_auth'],
                   'start_browser_before_auth': True,
                   'close_browser_after_auth': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Verify_Station_Connectivity'
    common_name = "%sVerify the connectivity of station: %s" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': conf['ap_tag'],
                   'wlan_cfg': wlan_cfg,
                   'status': 'Authorized',
                   'guest_name': conf['guest_pass_cfg']['guest_fullname'],
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
        'radio_mode': '',
        'grace_period': None,
        'target_ip': '',
        }
    conf.update(cfg)
    tcid = conf['tcid']
    sta_tag = conf['sta_tag']
    wlan_cfg = conf['wlan_cfg']
    test_cfgs = []
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'wlan_cfg': wlan_cfg,
                   'wg_cfg': conf['wg_cfg'],
                   'grace_period': conf['grace_period'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate a guest pass for WLAN: %s' % (tcid, wlan_cfg['ssid'])
    test_cfgs.append((conf['guest_pass_cfg'], test_name, common_name, 2, False))
    
    test_params = deepcopy(conf)
    test_cfgs.extend(client_connect_to_wlan(conf))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect within grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': conf['ap_tag'],
                   'grace_period': conf['grace_period'],
                   'reconnect_within_gp': True,
                   'no_need_auth': True,
                   'wlan_cfg': wlan_cfg,
                   'guest_name': conf['guest_pass_cfg']['guest_fullname'],
                   'radio_mode': conf['radio_mode'],
                   'target_ip': conf['target_ip'],
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect beyond grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': conf['ap_tag'],
                   'grace_period': conf['grace_period'],
                   'reconnect_within_gp': False,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'guest_name': conf['guest_pass_cfg']['guest_fullname'],
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
                   'radio_mode': [radio_mode,'na']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create local user: %s' % tcfg['local_user_cfg']['username']
    test_params = {'username': tcfg['local_user_cfg']['username'], 
                   'password': tcfg['local_user_cfg']['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = 'Set the guest access policy'
    test_cfgs.append((tcfg['guest_access_cfg'], test_name, common_name, 0, False))
    

    tcid = '[Grace period can work when inactivity timeout set manually]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-inactive-%s' % time.strftime("%H%M%S")
#    zj 2014-0217 fix ZF-7474 behavior change for inactivity_timeout range
#    wlan_cfg['inactivity_timeout'] = 30   
    wlan_cfg['inactivity_timeout'] = 10
    guest_pass_cfg = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg['wlan'] = wlan_cfg['ssid']
    guest_pass_cfg['guest_fullname'] = 'guest-inactive'
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg,
                   'radio_mode': radio_mode,
                   'grace_period': 3,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    tcid = '[Grace period is accurate when client uses VLAN]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-vlan-%s' % time.strftime("%H%M%S")
    wlan_cfg['vlan_id'] = VLAN_ID
    guest_pass_cfg = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg['wlan'] = wlan_cfg['ssid']
    guest_pass_cfg['guest_fullname'] = 'guest-vlan'
    test_params = {
        'tcid': tcid,
        'sta_tag': sta_tag,
        'ap_tag': ap_tag,
        'wlan_cfg': wlan_cfg,
        'wg_cfg': tcfg['wg_cfg'],
        'guest_access_cfg': tcfg['guest_access_cfg'],
        'guest_pass_cfg': guest_pass_cfg,
        'radio_mode': radio_mode,
        'grace_period': 3,
        'target_ip': target_ip,
        }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    tcid = '[Grace period is accurate in tunnel mode]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-tunnel-%s' % time.strftime("%H%M%S")
    wlan_cfg['do_tunnel'] = True
    guest_pass_cfg = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg['wlan'] = wlan_cfg['ssid']
    guest_pass_cfg['guest_fullname'] = 'guest-tunnel'
    test_params = {
        'tcid': tcid,
        'sta_tag': sta_tag,
        'ap_tag': ap_tag,
        'wlan_cfg': wlan_cfg,
        'wg_cfg': tcfg['wg_cfg'],
        'guest_access_cfg': tcfg['guest_access_cfg'],
        'guest_pass_cfg': guest_pass_cfg,
        'radio_mode': radio_mode,
        'grace_period': 3,
        'target_ip': target_ip,
        }
    test_cfgs.extend(grace_period_test(test_params))
    
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Remove all guest passes to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all Users to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
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
    
    local_user_cfg = {'username': 'local.user', 'password': 'local.user'}
    
    wlan_cfg = {
        'ssid': "", 
        'type': 'guest',
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_tunnel': False,
        'vlan_id': None
        }
    
    wg_cfg = {
        'name': 'rat-wg-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for Guest Access',
        'vlan_override': False,
        'wlan_member': {},
        }
   
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
    
    tcfg = dict(active_ap = active_ap,
                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                wg_cfg = wg_cfg,
                local_user_cfg = local_user_cfg,
                guest_access_cfg = guest_access_cfg,
                guest_pass_cfg = guest_pass_cfg,
                target_ip = '172.16.10.252'
                )
    
    test_cfgs = define_test_cfgs(tcfg)
    
    test_cfgs = decorate_common_name(test_cfgs)
    
    if attrs['ts_name']:
        ts_name = attrs['ts_name']

    else:
        ts_name = "Guest Access - Grace Period - Combine - %s" 
        ts_name = ts_name % (active_radio)
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the grace period in guest access WLAN.",
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
    