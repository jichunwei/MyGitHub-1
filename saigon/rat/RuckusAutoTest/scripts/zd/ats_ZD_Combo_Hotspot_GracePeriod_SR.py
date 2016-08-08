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


def remove_wlan_from_wg(tcid, wlan_cfg, wg_cfg, exe_level):
    test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
    common_name = "%sRemove WLAN '%s' from the WLAN group" % (tcid, wlan_cfg['ssid'])
    test_params = {'wgs_cfg': wg_cfg,
                   'wlan_list': [wlan_cfg['ssid']]}
    
    return (test_params, test_name, common_name, exe_level, True)

    
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

    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
    
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
    test_params = {'username': user_cfg['username'], 
                   'password': user_cfg['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    
    tcid = '[Connect, leave and reconnect without ZD state change]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-sr-%s-1' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-sr-%s-1' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    grace_period = 3
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_params = {
        'tcid': tcid, 
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
                   'no_need_auth': True,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sTest station '%s' reconnect beyond grace period" % (tcid, sta_tag)
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'grace_period': grace_period,
                   'reconnect_within_gp': False,
                   'no_need_auth': False,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_params = {
        'tcid': tcid, 
        'sta_tag': sta_tag, 
        'ap_tag': ap_tag, 
        'wlan_cfg': wlan_cfg, 
        'user_cfg': user_cfg, 
        'radio_mode': radio_mode, 
        'target_ip': target_ip, 
        'associate_wlan': False,
        }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 2))
    
    
    tcid = '[Connect and leave both online/reconnect ZD state changed]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-sr-%s-2' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-sr-%s-2' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    grace_period = 8
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
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
    common_name = "%sClient disconnect from WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'username': user_cfg['username'],
                   'wlan_cfg': wlan_cfg,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover the active ZD' % tcid
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Grace_Period_In_GUI'
    common_name = "%sVerify grace period after failover" % tcid
    test_params = {'hotspot_name': hotspot_cfg['name'],
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sClient reconnect within grace period" % tcid
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'grace_period': grace_period,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'reconnect_within_gp': True,
                   'no_need_auth': True,
                   'disconnect_from_wlan': False,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))    
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 2))
    
    
    tcid = '[Connect both online/leave ZD2 offline/reconnect ZD2 active]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-sr-%s-3' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-sr-%s-3' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    grace_period = 10
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD_Mac' 
    common_name = '%sGet active ZD and standby ZD mac' %tcid
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '%sDisable switch port connected standby ZD' % tcid
    test_cfgs.append(({'zd': 'standby_zd_mac', 'device': 'zd'}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sClient disconnect from WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'username': user_cfg['username'],
                   'wlan_cfg': wlan_cfg,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable SW port connected to standby ZD' % tcid
    test_params = {'device': 'zd', 
                   'number': 1, 
                   'zdcli': 'standby_zd_cli',}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:wait zd sync for 60 seconds ' % (tcid)
    test_cfgs.append(({'timeout':60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover the active ZD'% tcid
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Grace_Period_In_GUI'
    common_name = "%sVerify grace period after failover" % tcid
    test_params = {'hotspot_name': hotspot_cfg['name'],
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sClient reconnect within grace period" % tcid
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'grace_period': grace_period,
                   'reconnect_within_gp': True,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'no_need_auth': True,
                   'disconnect_from_wlan': False,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))    
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 2))
    
    
    tcid = '[Connect ZD2 offline/leave ZD2 online/reconnect ZD2 active]'
    hotspot_cfg = deepcopy(tcfg['hotspot_cfg'])
    hotspot_cfg['name'] = 'gp-sr-%s-4' % time.strftime("%H%M%S")
    wlan_cfg = deepcopy(tcfg['wlan_cfg'])
    wlan_cfg['ssid'] = 'wispr-sr-%s-4' % time.strftime("%H%M%S")
    wlan_cfg['hotspot_profile'] = hotspot_cfg['name']
    grace_period = 8
    
    test_name = 'CB_ZD_Test_Grace_Period_Setting'
    common_name = "%sCreate WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'hotspot_cfg': hotspot_cfg,
                   'wlan_cfg': wlan_cfg,
                   'wg_cfg': tcfg['wg_cfg'],
                   'grace_period': grace_period,
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Get_Active_ZD_Mac' 
    common_name = '%sGet active zd and standby ZD mac' %tcid
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '%sDisable switch port connectet standby zd' % tcid
    test_cfgs.append(({'zd': 'standby_zd_mac', 'device': 'zd'}, 
                      test_name, common_name, 2, False))
    
    test_params = {'tcid': tcid,
                   'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'user_cfg': user_cfg,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   }
    test_cfgs.extend(client_connect_to_wlan(test_params))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable SW port connected to standby ZD' % tcid
    test_params = {'device': 'zd',
                   'number': 1,
                   'zdcli': 'standby_zd_cli',}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%s:wait zd sync for 60 seconds ' % (tcid)
    test_cfgs.append(({'timeout':60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Disconnect_Client'
    common_name = "%sClient disconnect from WLAN: %s" % (tcid, wlan_cfg['ssid'])
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'username': user_cfg['username'],
                   'wlan_cfg': wlan_cfg,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover the active ZD'%tcid
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Grace_Period_In_GUI'
    common_name = "%sVerify grace period after failover" % tcid
    test_params = {'hotspot_name': hotspot_cfg['name'],
                   'grace_period': grace_period}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Test_Grace_Period'
    common_name = "%sClient reconnect within grace period" % tcid
    test_params = {'sta_tag': sta_tag,
                   'ap_tag': ap_tag,
                   'wlan_cfg': wlan_cfg,
                   'username': user_cfg['username'],
                   'grace_period': grace_period,
                   'radio_mode': radio_mode,
                   'target_ip': target_ip,
                   'reconnect_within_gp': True,
                   'no_need_auth': True,
                   'disconnect_from_wlan': False,
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))    
    
    test_cfgs.append(remove_wlan_from_wg(tcid, wlan_cfg, tcfg['wg_cfg'], 2))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable SW port connected to standby ZD'
    test_params = {'device': 'zd',
                   'number': 1, 
                   'zdcli': 'standby_zd_cli',}
    test_cfgs.append((test_params, test_name, common_name, 0, True)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WLANs from station: %s' % sta_tag
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy after test'
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
                hotspot_cfg = hotspot_cfg,
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
        ts_name = "Hotspot - Grace Period - SR"
#        ts_name = "Hotspot - Grace Period - SR - %s - %s" 
#        ts_name = ts_name % (active_ap_model, active_radio)
        
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
    