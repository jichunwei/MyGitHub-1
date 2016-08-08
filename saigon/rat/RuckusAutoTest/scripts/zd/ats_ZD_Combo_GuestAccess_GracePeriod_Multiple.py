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


def remove_wlan_from_wg(tcid, wlan_cfg, wg_cfg, exe_level = 2):
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
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        common_name = "%sStation '%s' associate WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
        test_params = {'sta_tag': sta_tag, 
                       'wlan_cfg': wlan_cfg,
                       'verify_ip_subnet': False,
                       'start_browser': False,}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%sPerform guest auth in station: %s" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'guest_pass': conf['guest_pass_cfg']['key'], 
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


def define_test_cfgs(tcfg):
    test_cfgs = []
    ap_tag = tcfg['active_ap']
    sta_tag = tcfg['target_sta']
    sta_tag_2 = tcfg['target_sta_2']
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
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station: %s' % sta_tag_2
    test_params = {'sta_tag': sta_tag_2, 'sta_ip_addr': sta_tag_2}
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
    
    
    tcid = '[Grace period is accurate when 2 clients connected]'
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'gp-clients-%s' % time.strftime("%H%M%S")
    grace_period = 6
    
    guest_pass_cfg_1 = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg_1['wlan'] = wlan_cfg['ssid']
    guest_pass_cfg_1['guest_fullname'] = 'guest-clients-1'
    guest_pass_cfg_1['key'] = 'clients1'
    
    guest_pass_cfg_2 = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg_2['wlan'] = wlan_cfg['ssid']
    guest_pass_cfg_2['guest_fullname'] = 'guest-clients-2'
    guest_pass_cfg_2['key'] = 'clients2'
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate a guest pass for WLAN: %s' % (tcid, wlan_cfg['ssid'])
    test_cfgs.append((guest_pass_cfg_1, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate another guest pass for WLAN: %s' % (tcid, wlan_cfg['ssid'])
    test_cfgs.append((guest_pass_cfg_2, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_1,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag_2,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_2,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'wlan_cfg': wlan_cfg,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag_2, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag_2,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'wlan_cfg': wlan_cfg,
                   'pause_before_disconnect': 120,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sWait before grace period of station '%s' expired" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'wlan_cfg': wlan_cfg,
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = "%sStation '%s' reconnect to WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag, 'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sWait before grace period of station '%s' expired" % (tcid, sta_tag_2)
    test_params = {'sta_tag': sta_tag_2,
                   'wlan_cfg': wlan_cfg,
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = "%sStation '%s' reconnect to WLAN: %s" % (tcid, sta_tag_2, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag_2, 'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sVerify connectivity of station '%s' within grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'no_need_auth': True,
                   'wlan_cfg': wlan_cfg,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sVerify connectivity of station '%s' within grace period" % (tcid, sta_tag_2)
    test_params = {'sta_tag': sta_tag_2,
                   'ap_tag': ap_tag,
                   'no_need_auth': True,
                   'wlan_cfg': wlan_cfg,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'wlan_cfg': wlan_cfg,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag_2, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag_2,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'wlan_cfg': wlan_cfg,
                   'pause_before_disconnect': 120,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sExpire grace period of station: %s" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'wlan_cfg': wlan_cfg,
                   'grace_period': grace_period,
                   'reconnect_within_gp': False,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = "%sStation '%s' reconnect to WLAN: %s" % (tcid, sta_tag, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag, 'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sExpire grace period of station: %s" % (tcid, sta_tag_2)
    test_params = {'sta_tag': sta_tag_2,
                   'wlan_cfg': wlan_cfg,
                   'grace_period': grace_period,
                   'reconnect_within_gp': False,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = "%sStation '%s' reconnect to WLAN: %s" % (tcid, sta_tag_2, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag_2, 'wlan_cfg': wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sVerify connectivity of station '%s' beyond grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_1,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sVerify connectivity of station '%s' beyond grace period" % (tcid, sta_tag_2)
    test_params = {'sta_tag': sta_tag_2,
                   'ap_tag': ap_tag,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag_2,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_2,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 1))


    tcid = '[Grace period is accurate when client switches between 2 WLANs]'
    wlan_cfg_1 = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg_1['ssid'] = 'gp-wlans-%s-1' % time.strftime("%H%M%S")
    grace_period_1 = 7
    guest_pass_cfg_1 = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg_1['wlan'] = wlan_cfg_1['ssid']
    guest_pass_cfg_1['guest_fullname'] = 'guest-wlans-1'
    guest_pass_cfg_1['key'] = 'wlans1'
   
    wlan_cfg_2 = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg_2['ssid'] = 'gp-wlans-%s-2' % time.strftime("%H%M%S")
    grace_period_2 = 8
    guest_pass_cfg_2 = deepcopy(tcfg['guest_pass_cfg'])
    guest_pass_cfg_2['wlan'] = wlan_cfg_2['ssid']
    guest_pass_cfg_2['guest_fullname'] = 'guest-wlans-2'
    guest_pass_cfg_2['key'] = 'wlan2'
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg_1['ssid'])
    test_params = {'wlan_cfg': wlan_cfg_1,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period_1,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate a guest pass for WLAN: %s' % (tcid, wlan_cfg_1['ssid'])
    test_cfgs.append((guest_pass_cfg_1, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg_2['ssid'])
    test_params = {'wlan_cfg': wlan_cfg_2,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period_2,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%sGenerate a guest pass for WLAN: %s' % (tcid, wlan_cfg_2['ssid'])
    test_cfgs.append((guest_pass_cfg_2, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_1,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_1,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'wlan_cfg': wlan_cfg_1,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_2,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_2,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sWait before grace period expired in WLAN: %s" % (tcid, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'wlan_cfg': wlan_cfg_1,
                   'grace_period': grace_period_1-1,
                   'additional_exe_time': 30,
                   'reconnect_within_gp': True,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg_2['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'wlan_cfg': wlan_cfg_2,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station reconnect to WLAN '%s' within grace period" % (tcid, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_1,
                   'no_need_auth': True,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'reconnect_within_gp': True,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': True,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sWait before grace period expired in WLAN: %s" % (tcid, wlan_cfg_2['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'wlan_cfg': wlan_cfg_2,
                   'grace_period': grace_period_2-1,
                   'additional_exe_time': 30,
                   'reconnect_within_gp': True,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'wlan_cfg': wlan_cfg_1,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station reconnect to WLAN '%s' within grace period" % (tcid, wlan_cfg_2['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_2,
                   'no_need_auth': True,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'target_ip': target_ip,
                   'radio_mode': radio_mode,
                   'reconnect_within_gp': True,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': True,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sExpire grace period in WLAN: %s" % (tcid, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'wlan_cfg': wlan_cfg_1,
                   'grace_period': grace_period_1,
                   'reconnect_within_gp': False,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg_2['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'wlan_cfg': wlan_cfg_2,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station reconnect to WLAN '%s' beyond grace period" % (tcid, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_1,
                   'no_need_auth': False,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'reconnect_within_gp': False,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': True,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_1,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_1,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sExpire grace period in WLAN: %s" % (tcid, wlan_cfg_2['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'wlan_cfg': wlan_cfg_2,
                   'grace_period': grace_period_2,
                   'reconnect_within_gp': False,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': True,
                   'reconnect_to_wlan': False,
                   'verify_connectivity': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sDisconnect station '%s' from WLAN: %s" % (tcid, sta_tag, wlan_cfg_1['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'guest_name': guest_pass_cfg_1['guest_fullname'],
                   'wlan_cfg': wlan_cfg_1,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station reconnect to WLAN '%s' beyond grace period" % (tcid, wlan_cfg_2['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_2,
                   'no_need_auth': False,
                   'guest_name': guest_pass_cfg_2['guest_fullname'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'reconnect_within_gp': False,
                   'clear_events': False,
                   'disconnect_from_wlan': False,
                   'expire_grace_period': False,
                   'reconnect_to_wlan': True,
                   'verify_connectivity': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg_2,
                   'guest_access_cfg': tcfg['guest_access_cfg'],
                   'guest_pass_cfg': guest_pass_cfg_2,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'associate_wlan': False,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    
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
                 target_sta_2 = '',
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
        target_sta_2 = testsuite.getTargetStation(sta_ip_list)
        
        active_radio = testsuite.get_target_sta_radio()
        
    else:
        active_ap = attrs["active_ap"]
        target_sta = attrs['target_sta']
        target_sta_2 = attrs['target_sta_2']
        active_radio = attrs["active_radio"]
    
    active_ap_model = ap_sym_dict[active_ap]['model']
    support_radio_mode = lib_Constant.get_radio_mode_by_ap_model(active_ap_model)
    if active_radio not in support_radio_mode:
        print "The active AP[%s] doesn't support radio[%s]" % (active_ap_model, active_radio)
        return
    
    local_user_cfg = {'username': 'local_user', 'password': 'local_user',}
    
    wlan_cfg = {
        'ssid': "", 
        'type': 'guest',
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
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
                target_sta = target_sta,
                target_sta_2 = target_sta_2,
                active_radio = active_radio,
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
        ts_name = "Guest Access - Grace Period - Multiple - %s" 
        ts_name = ts_name % (active_radio)
        
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the grace period in Guest Access WLAN.",
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
    