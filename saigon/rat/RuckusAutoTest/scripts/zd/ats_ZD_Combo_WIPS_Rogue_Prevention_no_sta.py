"""
This test suite is configure to allow testing follow test cases - which are belong to WIPS:
    - Factory default configuration for WIPS
    - Report Rouge Devices?options in Configure->Service page
    - WIPS options in Configure->WIPS page
    - Configuration when Background Scanning is enabled
    - WIPS with spoofed SSID/BSSID/same-network Rouge AP     
    
    expect result: All steps should result properly.
    
    How to:
        1) Create an WLAN on genuine AP
        2) Create the same WLAN on potential Malicious AP, no STA associates to this WLAN
        3) Malicious AP and genuine AP use different channels.
        4) Verify that potential Malicious AP will be detected and marked to malicious correctly.
        5) The Genuine AP will send de-authentication broadcast with malicious AP's BSSID to disconnect all STAs that are associated to malicious AP at the moment.
        6) Check "Currently Active Rouge Devices" table the status of malicious AP.
        7) The genuine AP will send de-authentication (use the BSSID of Malicious AP) to STAs who are associating to malicious AP for every background scanning interval 
            until it detects that malicious AP vanishes.
        8) change AP channel to fixed channel, and repeat step 4) to 7).
    
Created on August 2012
@author: kevin.tan@ruckuswireless.com
"""
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def _get_wlan_cfg(ssid, wlan_params):
    #Open-None WLAN
    wlan_cfg = dict(ssid=ssid, auth="open", wpa_ver="", encryption="none", key_index="", key_string="",
                   do_webauth=False, #auth_svr = "", #Default is local database. 
                   username="", password="",)#username and password is for client to associate.
    wlan_cfg.update(wlan_params)
    return wlan_cfg


def define_test_cfg(cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    browser_tag = 'browser%s' % radio_mode

    ap_tag1 = 'ap%s1' % radio_mode
    ap_tag2 = 'ap%s2' % radio_mode

    channel=''
    channel_diff=''
    if radio_mode == 'ng':
        channel = '6'
        channel_diff = '11'
    else:
        channel = '48'
        channel_diff = '149'

    ssid1 = 'wips_no_sta_same_channel'
    ssid2 = 'wips_no_sta_diff_channel'
    ssid3 = 'wips_no_sta_auto'
    wlan_cfg1 = _get_wlan_cfg(ssid1, {})
    wlan_cfg2 = _get_wlan_cfg(ssid2, {})
    wlan_cfg3 = _get_wlan_cfg(ssid3, {})

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD in the beginning'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = 'clean environment by setting ZD to factory default'
    test_cfgs.append(({},test_name, common_name, 0, False))  
        
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP1'
    test_cfgs.append(({'ap_tag': ap_tag1,
                       'active_ap': 'AP_01'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP2'
    test_cfgs.append(({'ap_tag': ap_tag2,
                       'active_ap': 'AP_02'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Force_AP_Standalone'
    common_name = 'Force setting AP as standalone AP'
    test_cfgs.append(({'ap_tag': ap_tag2, 'op_type':'init'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': ''}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag1,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_case_name = '[WIPS configuration]'
    test_name = 'CB_ZD_WIPS_Configuration'
    common_name = '%sWIPS and background scanning configuration test' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 1, False))

    test_case_name = '[WIPS test same channel]'

    # stand-alone and under ZD control APs have the same channel
    test_name = 'CB_ZD_Create_Wlan_On_Standalone_AP'
    common_name = '%sCreate a WLAN on standalone AP' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag2, 'radio': radio_mode, 'wlan_cfg_list':[wlan_cfg1], 'channel':channel}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfig active AP Radio %s - change channel value' % (test_case_name, radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag1,
                   'ap_cfg': {'radio': radio_mode, 'channel':channel, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all events before' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD with the same ssid as standalone AP' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg1],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_WIPS_Rogue_AP_Prevention'
    common_name = '%sTest WIPS Rogue AP Prevention without user associated' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg':wlan_cfg1,'under_zd_ap_tag': ap_tag1,'standalone_ap_tag': ap_tag2, 'radio': radio_mode, 'type': 'ssid_spoof', 'client_join':False}, test_name, common_name, 2, False))

    test_case_name = '[WIPS test diff channel]'

    # stand-alone and under ZD control APs have different channel value
    test_name = 'CB_ZD_Create_Wlan_On_Standalone_AP'
    common_name = '%sCreate a WLAN on standalone AP' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag2, 'radio': radio_mode, 'wlan_cfg_list':[wlan_cfg2], 'channel':channel}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfig active AP Radio %s - change channel value' % (test_case_name, radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag1,
                   'ap_cfg': {'radio': radio_mode, 'channel':channel_diff, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all events before' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD with the same ssid as standalone AP' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg2],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_WIPS_Rogue_AP_Prevention'
    common_name = '%sTest WIPS Rogue AP Prevention without user associated' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg':wlan_cfg2,'under_zd_ap_tag': ap_tag1,'standalone_ap_tag': ap_tag2, 'radio': radio_mode, 'type': 'ssid_spoof', 'client_join':False}, test_name, common_name, 2, False))

    test_case_name = '[WIPS test auto channel]'

    # stand-alone and under ZD control APs are both auto channel
    test_name = 'CB_ZD_Create_Wlan_On_Standalone_AP'
    common_name = '%sCreate a WLAN on standalone AP' % (test_case_name,)
    test_cfgs.append(({'ap_tag': ap_tag2, 'radio': radio_mode, 'wlan_cfg_list':[wlan_cfg3], 'channel':'auto'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfig active AP Radio %s - change channel value' % (test_case_name, radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag1,
                   'ap_cfg': {'radio': radio_mode, 'channel':'Auto', 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Clear_Event'
    common_name = '%sClear all events before' % (test_case_name,)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD with the same ssid as standalone AP' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg3],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Test_WIPS_Rogue_AP_Prevention'
    common_name = '%sTest WIPS Rogue AP Prevention without user associated' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg':wlan_cfg3,'under_zd_ap_tag': ap_tag1,'standalone_ap_tag': ap_tag2, 'radio': radio_mode, 'type': 'ssid_spoof', 'client_join':False}, test_name, common_name, 2, False))

    #Recovery original environment that all APs are under ZD management
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Force_AP_Standalone'
    common_name = 'Recover standalone AP as under ZD controlled AP'
    test_cfgs.append(({'ap_tag': ap_tag2, 'op_type':'recovery'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
  
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
        
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:        
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        
    tcfg = {'target_station':'%s' % target_sta,
            'all_ap_mac_list': all_ap_mac_list,
            'radio_mode': target_sta_radio,
            }

    test_cfgs = define_test_cfg(tcfg)
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "WIPS Rogue AP Prevention no sta - 11%s" % (target_sta_radio,)

    ts = testsuite.get_testsuite(ts_name, "Verify WIPS Rogue AP Prevention properly - 11%s radio" % target_sta_radio, combotest=True)

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
    createTestSuite(**_dict)