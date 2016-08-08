'''
By West
switch channel on ap continuously for long time
check channel can be deploy to ap correctly,and the client can associate to ap and ping
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = []    
    
    wlan_cfg = tcfg['wlan_cfg']
    active_ap_tag = tcfg['active_ap_tag']
    sta_tag = tcfg['target_sta']
    radio_mode = tcfg['active_radio']
    dest_ip = tcfg['dest_ip']
    country_para = tcfg['country_para']
    switch_timer = tcfg['switch_timer']
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'set country code to %s'%country_para['name']
    param_cfg = {'country_code':country_para['name'],'allow_indoor_channel':True}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create AP: %s' % (active_ap_tag)
    test_params = {'ap_tag': active_ap_tag, 'active_ap': active_ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create station: %s' % (sta_tag)
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_New_WlanGroup'
    common_name = "Create WLAN group: %s" % (tcfg['wg_cfg']['name']) 
    test_cfgs.append(({'wgs_cfg': tcfg['wg_cfg'],'add_wlan':False}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Single_Wlan'
    common_name = "Create WLAN : %s" % (wlan_cfg['ssid']) 
    test_cfgs.append(({'wlan_cfg': wlan_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_Wlan_On_Wlan_Group'
    common_name = "assign WLAN %s to group: %s" % (wlan_cfg['ssid'],tcfg['wg_cfg']['name']) 
    test_cfgs.append(({'wlan_list':[wlan_cfg['ssid']],'wgs_cfg': tcfg['wg_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign the WLAN group to radio '%s' of AP: %s" % (radio_mode, active_ap_tag)
    test_params = {'active_ap': active_ap_tag,
                   'wlan_group_name': tcfg['wg_cfg']['name'], 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = 'Associate the station %s to the wlan %s' % (sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = 'Ping the dest-ip:%s ' % (dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_case_name = '[continuously switch %s channel]'%radio_mode
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '%srecord webmgr ,apmgr and stamgr psid'%test_case_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Long_Time_Switch_AP_Channel'
    common_name = '%sswitch channels for %s secondss'%(test_case_name,switch_timer['test_period_lenth'])
    param_cfg = {'ng_channel_list':country_para['ng_channels'],
                 'na_channel_list':country_para['na_channels'],
                'test_period_lenth':switch_timer['test_period_lenth'],
                'switch_interval':switch_timer['switch_interval'],
                'check_deploy_interval':switch_timer['check_deploy_interval'],
                'ap_tag':tcfg['active_ap_tag'],
                'radio':tcfg['active_radio']
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%s Associate the station %s to the wlan %s' % (test_case_name,sta_tag, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_cfg': wlan_cfg,'sta_tag':sta_tag},test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '%sPing the dest-ip:%s ' % (test_case_name,dest_ip)
    test_params = {'sta_tag': sta_tag, 'ping_timeout_ms': 10000, 'dest_ip': dest_ip}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '%scheck webmgr ,apmgr and stamgr psid'%test_case_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = "Assign Default WLAN group to radio '%s' of AP: %s" % (radio_mode, active_ap_tag)
    test_params = {'active_ap': active_ap_tag,
                   'wlan_group_name': 'Default', 
                   'radio_mode': radio_mode}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_Wlan_Group'
    common_name = "remove wlan group %s" % (tcfg['wg_cfg']['name'])
    test_params = {'wg_name': tcfg['wg_cfg']['name'],}
    test_cfgs.append((test_params, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_Wlan'
    common_name = "Remove WLAN : %s" % (wlan_cfg['ssid']) 
    test_cfgs.append(({'ssid': wlan_cfg['ssid']}, test_name, common_name, 0, True))
    
    return test_cfgs
    

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)#@author:yuyanan @since:2014-8-12 optimize
        target_sta = testsuite.getTargetStation(sta_ip_list)
        active_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="switch %s channel on ap continuously"%active_radio
    wlan_cfg = {
        'ssid': "channel_select_long-%s" % time.strftime("%H%M%S"),
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
    
    wg_cfg = {
        'name': 'rat-wg-upgrade-%s' % time.strftime("%H%M%S"),
        'description': 'WLANs for channel switch long time',
        'vlan_override': False,
        'wlan_member': {},
        }
    
    country_para={'name':'United States',
                  'na_channels':[36,40,44,48],
                  'ng_channels':[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                  }

    #@author:yuyanan @since:2014-8-12 optimize: allow user input float type or enter
    test_period_lenth_raw = raw_input("how long do you want to switch the channel?(hour):")
    if not test_period_lenth_raw:
        test_period_lenth = 0.5
    else:
        test_period_lenth = float(test_period_lenth_raw)
        
    switch_interval_raw = raw_input("how long do you want to wait after one channel setting?(second):")
    if not switch_interval_raw:
        switch_interval = 5
    else:
        switch_interval = int(switch_interval_raw)
    
    check_deploy_interval_raw = raw_input("how long check the channel deployment on ap?(hour):")
    if not check_deploy_interval_raw:
        check_deploy_interval = 0.2
    else:
        check_deploy_interval = float(check_deploy_interval_raw)
    switch_timer = dict(
                        test_period_lenth =test_period_lenth*60*60,
                        switch_interval = switch_interval,
                        check_deploy_interval = check_deploy_interval*60*60,
                        )
    
    tcfg = dict(active_ap_tag = active_ap_list[0],#@author:yuyanan @since:2014-8-12 zf-9537 optimize ap tag
                active_radio = active_radio,
                target_sta = target_sta,
                wlan_cfg = wlan_cfg,
                wg_cfg = wg_cfg,
                dest_ip= '192.168.0.252',
                country_para = country_para,
                switch_timer = switch_timer
                )
    test_cfgs = define_test_configuration(tcfg)
    ts = testsuite.get_testsuite(ts_name, "switch %s channel on ap continuously"%active_radio, interactive_mode = attrs["interactive_mode"], combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":    
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)
    
