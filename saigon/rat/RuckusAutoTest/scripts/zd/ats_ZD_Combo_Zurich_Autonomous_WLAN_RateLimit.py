"""
Verify rate limit configuration in Autonomous wlan with encryption type Open-None

    Verify rate limit configuration in wlan, 
    - Shaper value is correct
    - Send zing traffic, and rate of 50% is between the range [>min_rate, <=allowed_rate]
       min_rate=default is 0
       allowed_rate= rate_limit_mbps * (1.0 + margin_of_error), margin_of_error is 0.2 by default
    - Rate limit range is from 0.25mbps to 20.00mbps step is 0.25mbps.
    - Coverage: uplink and downlink rate limit is same, uplink     
    
    expect result: All steps should result properly.
    
    How to:
        1) Disable all AP's wlan service
        2) Enable active AP's wlan service based on radio   
        4) Create an Autonomous wlan and make sure it is in default wlan group
        5) Station associate the wlan
        6) Get station wifi address and verify it is in expected subnet
        7) Verify station information in ZD, status is authorized
        8) Verify station can ping target ip
        9) Verify station information in AP side
        10) Verify uplink shaper value in AP side
        11) Verify downlink shaper value in AP side
        12) Verify uplink zing traffic [From linux PC to wireless station]
        13) Verify downlink zing traffic [From wireless station to linux PC]
        14) Repeat step 4)-13) for all rate limit configuration.

Created on 2013-04-15
@author: kevin.tan@ruckuswireless.com
"""

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def _def_rate_limit_cfg_list():
    '''
    uplink and downlink rate limit is between 0.25mbps - 20.00mbps.
    '''
    rate_cfg_list = []
    
    rate_cfg_list.append(dict(uplink_rate_limit = "0.25mbps", downlink_rate_limit = "0.25mbps", margin_of_error = 0.2))
    rate_cfg_list.append(dict(uplink_rate_limit = "0.50mbps", downlink_rate_limit = "0.50mbps", margin_of_error = 0.2))
    rate_cfg_list.append(dict(uplink_rate_limit = "1.00mbps", downlink_rate_limit = "1.00mbps", margin_of_error = 0.2))    
    rate_cfg_list.append(dict(uplink_rate_limit = "13.75mbps", downlink_rate_limit = "13.75mbps", margin_of_error = 0.2))
    rate_cfg_list.append(dict(uplink_rate_limit = "15.00mbps", downlink_rate_limit = "15.00mbps", margin_of_error = 0.2))
    rate_cfg_list.append(dict(uplink_rate_limit = "20.00mbps", downlink_rate_limit = "20.00mbps", margin_of_error = 0.2))
    rate_cfg_list.append(dict(uplink_rate_limit = "0.75mbps", downlink_rate_limit = "5.00mbps", margin_of_error = 0.2))
    rate_cfg_list.append(dict(uplink_rate_limit = "10.50mbps", downlink_rate_limit = "2.25mbps", margin_of_error = 0.2))
    return rate_cfg_list    

def _define_wlan_cfg(uplink_rate_limit, downlink_rate_limit):
    wlan_cfg = dict(ssid='rate-limit-autonomous', auth="open", encryption="none")
    
    wlan_cfg['type'] = 'autonomous'

    wlan_cfg['uplink_rate_limit'] = uplink_rate_limit
    wlan_cfg['downlink_rate_limit'] = downlink_rate_limit
    
    return wlan_cfg

def define_test_cfg(cfg):
    test_cfgs = []
    
    target_ip_addr = cfg['server_ip_addr']
    radio_mode = cfg['radio_mode']
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    for rate_cfg in cfg['rate_limit_cfg_list']:
        uplink_rate_limit = rate_cfg['uplink_rate_limit']
        downlink_rate_limit = rate_cfg['downlink_rate_limit']
        margin_of_error = rate_cfg['margin_of_error']
                
        wlan_cfg = _define_wlan_cfg(uplink_rate_limit, downlink_rate_limit)
        
        test_case_name = '[Up=%s-Down=%s]' % (uplink_rate_limit,downlink_rate_limit)
    
        test_name = 'CB_ZD_Create_Wlan'
        common_name = '%sCreate or edit WLAN on ZD' % (test_case_name,)
        test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                           'check_wlan_timeout': 90}, test_name, common_name, 1, False))
            
        expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the WLAN on the active AP' % (test_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': ap_tag}, test_name, common_name, 2, False))
        
        test_cfgs.extend(_define_sta_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag))
        
        test_name = 'CB_ZD_Verify_AP_Shaper'
        common_name = '%sVerify uplink shaper in AP' % (test_case_name)
        test_cfgs.append(({'rate_limit': uplink_rate_limit,
                           'link_type': 'up',
                           'ap_tag': ap_tag,
                           'ssid': wlan_cfg['ssid']}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Shaper'
        common_name = '%sVerify downlink shaper in AP' % (test_case_name)
        test_cfgs.append(({'rate_limit': downlink_rate_limit,
                           'link_type': 'down',
                           'ap_tag': ap_tag,
                           'ssid': wlan_cfg['ssid']}, test_name, common_name, 2, False))
        
        test_name = 'CB_Zing_Traffic_Station_LinuxPC'
        common_name = '%sSend uplink zap traffic and verify traffic rate' % (test_case_name)
        test_cfgs.append(({'rate_limit': uplink_rate_limit,
                           'margin_of_error': margin_of_error,
                           'link_type': 'up',
                           'sta_tag': sta_tag,
                           'ssid': wlan_cfg['ssid']}, test_name, common_name, 2, False))
        
        test_name = 'CB_Zing_Traffic_Station_LinuxPC'
        common_name = '%sSend downlink zap traffic and verify traffic rate' % (test_case_name)
        test_cfgs.append(({'rate_limit': downlink_rate_limit,
                           'margin_of_error': margin_of_error,
                           'link_type': 'down',
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan from station' % (test_case_name)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
                            
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs

def _define_expect_wlan_info_in_ap(tcfg, wlan_cfg):
    if type(tcfg['radio_mode']) == list:
        radio_mode_list = tcfg['radio_mode']
    else:
        radio_mode_list = [tcfg['radio_mode']]                                                                                                          
    
    expect_wlan_info = dict()
    for radio in radio_mode_list:
        status = 'up'
        if radio in ['bg', 'ng']:            
            wlan_name = "wlan0"
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])
        elif radio in ['na']:
            MAXIMUM_WLAN = 8
            wlan_name = "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])

    return expect_wlan_info

def _define_sta_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_wpa_auto=False):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information in ZD' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name)
    test_cfgs.append(({'ssid': wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    return test_cfgs


def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)
    expected_sub_mask = '255.255.255.0'
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
            
    rate_limit_cfg_list = _def_rate_limit_cfg_list()
            
    for active_ap in active_ap_list:
        tcfg = {'server_ip_addr': server_ip_addr,
                'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap':'%s' % active_ap,
                'all_ap_mac_list': all_ap_mac_list,
                'expected_sub_mask': expected_sub_mask,
                'expected_subnet': utils.get_network_address(server_ip_addr, expected_sub_mask),
                'rate_limit_cfg_list': rate_limit_cfg_list,
                }
        
        test_cfgs = define_test_cfg(tcfg)
        
        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            ts_name = "Autonomous WLAN Rate Limiting - 11%s" % (target_sta_radio)
    
        ts = testsuite.get_testsuite(ts_name, "Autonomous WLAN Rate Limiting - 11%s" % (target_sta_radio), combotest=True)
    
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

