"""
Verify ER395: Mitsui: 9.3.4.0.14 retrieving supportinfo causes the AP to reboot - CC-APPROVED

    Verify support command don't cause AP reboot.
        
    expect result: All steps should result properly.
    
    How to:    
        1) Enable active AP's wlan service based on radio.
        2) Create a wlan and make sure it is in default wlan group
        3) Execute "support" in AP CLI.
        4) Verify AP is not reboot:
             a. Ping AP IP address for some time (ping_duration), verify no timeout in result
             b. Get AP uptime, verify it is greater than duration between starting execute support
                command and current time.
        
Repro ER steps:
    Create a wlan in ZD.
    In AP, at least one wlan state is up.
    Go to AP CLI, execute "support".
    AP will reboot after about 60 seconds.   
    
Created on 2012-11-27
@author: cherry.cheng@ruckuswireless.com
"""

import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_cfg(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']    
    ap_tag = 'ap%s' % radio_mode
    
    active_ap = cfg['active_ap']
    active_ap_mac = cfg['active_ap_mac']
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap': active_ap,
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    wg_name = 'Default'
    wg_cfg = dict(name=wg_name, description=None, ap_rp={radio_mode: {'wlangroups': wg_name}},)
    test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    test_cfgs.append(({'wgs_cfg': wg_cfg,
                       'ap_tag': ap_tag, },
                  test_name, common_name, 0, False))
    
    wlan_cfg = cfg['wlan_cfg']
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a wlan on ZD'
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 1, False))
    
    test_case_name = "[ER395-AP CLI]"
    test_name = 'CB_AP_CLI_Exec_Support_Cmd'
    common_name = '%sExecute support and verify AP is not reboot' % (test_case_name)
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ping_duration': cfg['ping_duration'],
                       'ping_timeout': cfg['ping_timeout'],
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = 'Verify APs Join ZD'
    test_cfgs.append(({ 'auto_approval': True,
                        'verify_ap_component': False,
                        'mac_addr_list': [active_ap_mac]
                        }, test_name, common_name, 0, False))
    
    test_case_name = "[ER395-ZD CLI]"
    test_name = 'CB_ZD_CLI_Exec_Support_Verify_ZD_Not_Reboot'
    common_name = '%sSaves debug information in ZD CLI and verify ZD is not reboot' % test_case_name
    test_cfgs.append(({'debug_info': cfg['debug_info'],
                       'ap_tag': ap_tag,
                       'ping_duration': cfg['ping_duration'],
                       'ping_timeout': cfg['ping_timeout'],
                       },
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs

def _get_wlan_cfg(ssid, wlan_params):
    wlanCfg = dict(ssid=ssid, auth="open", wpa_ver="", encryption="none", key_index="", key_string="",
                   do_webauth=True, #auth_svr = "", #Default is local database. 
                   #username and password is for client to associate.
                   username="", password="",)
    
    wlanCfg.update(wlan_params)
    
    return wlanCfg

def _define_wlan_cfg(ssid):    
    wlan_cfg = _get_wlan_cfg(ssid, dict(auth="open", encryption="none"))
    
    return wlan_cfg

def get_selected_input(depot = [], prompt = ""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select option: "

    selection = []
    id = raw_input(prompt)
    try:
        selection = depot[int(id)]
    except:
        selection = ""

    return selection

def create_test_suite(**kwargs):
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
     
    tftp_server_ip = raw_input("Please input TFTP server IP [Default is 192.168.0.10]: ")
    if not tftp_server_ip:
        tftp_server_ip= '192.168.0.10'
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:        
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        
    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            active_ap_mac = ap_info['mac']
            break
                
    ssid = "WlanTest%04d" % random.randrange(1,9999)
    wlan_cfg = _define_wlan_cfg(ssid)
    
    tcfg = {'target_station':'%s' % target_sta,
            'active_ap': active_ap,
            'active_ap_mac': active_ap_mac,
            'radio_mode': target_sta_radio,
            'wlan_cfg': wlan_cfg,
            'ping_duration': 180, #seconds
            'ping_timeout': 1, #seconds
            'debug_info': {'tftp_server_ip': tftp_server_ip},
            }
    
    ap_model = ap_sym_dict[active_ap]['model']
    
    test_cfgs = define_test_cfg(tcfg)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "ER395 AP Reboot After Exec Support - 11%s %s" % (target_sta_radio, ap_model)

    ts = testsuite.get_testsuite(ts_name, "Verify AP not reboot after support command - 11%s radio" % target_sta_radio, combotest=True)

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
    create_test_suite(**_dict)