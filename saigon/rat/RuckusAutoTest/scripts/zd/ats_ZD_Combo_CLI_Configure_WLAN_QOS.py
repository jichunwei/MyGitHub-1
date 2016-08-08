# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Sep 2010

This testsuite is configure to allow testing follow test cases - which are belong to Configure WLAN - QoS:
27.71	Enables qos classification.
27.72	Disables qos classification.
27.73	Enables qos heuristics udp.
27.74	Disables qos heuristics udp.
27.75	Enables qos directed multicast.
27.76	Disables qos directed multicast.
27.77	Enables qos igmp-snooping.
27.78	Disables qos igmp-snooping.
27.79	Enables qos mld snooping.
27.80	Disables qos mld snooping.
27.81	Enables qos tos classification.
27.82	Disables qos tos classification.
27.83	Sets qos priority high.
27.84	Sets qos priority low.
27.85	Configures QoS directed threshold.

Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys
import copy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

def defineTestConfiguration(cfg):
    test_cfgs = []
    
    wlan_cfg = cfg['wlan_cfg']
    
    #@author: Liang Aihua, @change: these params only used in qos function verification.
    #target_ip_addr = cfg['server_ip_addr']
    #radio_mode = cfg['radio_mode']
    
    #sta_tag = 'sta%s' % radio_mode
    #browser_tag = 'browser%s' % radio_mode
    #ap_tag = 'ap%s' % radio_mode
    
    #@author: Liang Aihua, @change: These test cases have be included in Configure QoS, so remove them.
    #test_name = 'CB_ZD_Remove_All_Config'
    #common_name = 'Remove all configuration from ZD'
    #test_cfgs.append(({}, test_name, common_name, 0, False))    
    
    #Global Qos setting.
    #test_name = 'CB_ZD_CLI_Configure_QoS'
    
    #common_name = 'Initiate global Qos test environment'
    #test_cfgs.append(({'init_env': True}, test_name, common_name, 0, False))
    
    #test_case_name = '[Global Qos - Tx Failed Threshold]'
    #common_name = '%sSets threshold value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'tx_failure_threshold': '100'}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Heuristics Video Inter-Packet-Gap]'
    #common_name = '%sSets Inter-Packet-Gap min and max value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_gap_video': '0',
    #                                'heuristic_max_pkt_gap_video': '70',}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Heuristics Voice Inter-Packet-Gap]'
    #common_name = '%sSets Inter-Packet-Gap min and max value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_gap_voice': '10',
    #                                'heuristic_max_pkt_gap_voice': '270',}}, test_name, common_name, 1, False))
     
    #test_case_name = '[Global Qos - Heuristics Video Packet Length]'
    #common_name = '%sSets packet-length min and max value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_len_video': '1100',
    #                                'heuristic_max_pkt_len_video': '1600',}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Heuristics Voice Packet Length]'
    #common_name = '%sSets packet-length min and max value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'heuristic_min_pkt_len_voice': '65',
    #                                'heuristic_max_pkt_len_voice': '350',}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Heuristics Calssification Video Packet-Octet-Count]'
    #common_name = '%sSets packet-octet-count value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'heuristic_octet_count_video': '55000'}}, test_name, common_name, 1, False))    
    
    #test_case_name = '[Global Qos - Heuristics Calssification Voice Packet-Octet-Count]'
    #common_name = '%sSets packet-octet-count value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'heuristic_octet_count_voice': '650'}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Heuristics No-Calssification Video Packet-Octet-Count]'
    #common_name = '%sSets packet-octet-count value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'no_heuristic_octet_count_video': '550000'}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Heuristics No-Calssification Voice Packet-Octet-Count]'
    #common_name = '%sSets packet-octet-count value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'no_heuristic_octet_count_voice': '15000'}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Tos Calssification Video]'
    #common_name = '%sSets tos classification video value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'tos_classification_video': '0xA0'}}, test_name, common_name, 1, False))
    
    #test_case_name = '[Global Qos - Tos Calssification Voice]'
    #common_name = '%sSets tos classification voice value' % (test_case_name,)
    #test_cfgs.append(({'qos_conf': {'tos_classification_voice': '0xC0'}}, test_name, common_name, 1, False))
    
    #test_name = 'CB_ZD_Config_AP_Radio'
    #common_name = 'Config All APs Radio - Disable WLAN Service'
    #test_params = {'cfg_type': 'init',
    #               'all_ap_mac_list': cfg['all_ap_mac_list']}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Create_Station'
    #common_name = 'Create target station'
    #test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
    #                   'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    #test_name = 'CB_Station_Remove_All_Wlans'
    #common_name = 'Remove all wlans from station'
    #test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Create_Active_AP'
    #common_name = 'Create active AP'
    #test_cfgs.append(({'active_ap':cfg['active_ap'],
    #                   'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Config_AP_Radio'
    #common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    #test_params = {'cfg_type': 'config',
    #               'ap_tag': ap_tag,
    #               'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
    #               }
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #wg_name = 'Default'
    #wg_cfg = dict(name=wg_name, description=None, ap_rp={radio_mode: {'wlangroups': wg_name}},)
    #test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    #common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    #test_cfgs.append(({'wgs_cfg': wg_cfg,
    #                   'ap_tag': ap_tag, },
    #              test_name, common_name, 0, False))
    
    #test_name = 'CB_Station_CaptivePortal_Start_Browser'
    #common_name = 'Start browser in station'
    #test_cfgs.append(({'sta_tag': sta_tag,
    #                   'browser_tag':browser_tag}, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Create_Wlan'
    #common_name = 'Create a wlan on ZD'
    #test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
    #                   'enable_wlan_on_default_wlan_group': True,
    #                   'check_wlan_timeout': 90}, test_name, common_name, 1, False))
    
    
    #Confiure wlan qos settings.
    ssid = wlan_cfg['ssid']
    test_name = 'CB_ZD_CLI_Configure_WLAN_QoS'
    
    common_name = 'Initiate test environment'
    test_cfgs.append(({'init_env': True, 'qos_conf':{'wlan':ssid}}, test_name, common_name, 0, False))
    
    test_case_name = '[Wlan Qos - Disable Qos Classification]'
    common_name = '%sDisables qos classification' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'classification': 'disabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Enable Qos Classification]'
    common_name = '%sEnables qos classification' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'classification': 'enabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Enable Qos Heuristics UDP]'
    common_name = '%sEnables qos heuristics udp' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'udp_heuristic_classification': 'enabled'}}, test_name, common_name, 1, False))
    
    #@author: Liang Aihua, @@change: These case not exist in database(data:2014-11-13)
    #Add data plane testing for Heuristics classification.
    #test_cfgs.extend(_define_data_plane_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, False))
    
    test_case_name = '[Wlan Qos - Disable Qos Heuristics UDP]'
    common_name = '%sDisables qos heuristics udp' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'udp_heuristic_classification': 'disabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Enable Qos Directed Multicast]'
    common_name = '%sEnables qos directed multicast' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'directed_multicast': 'enabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Disable Qos Directed Multicast]'
    common_name = '%sDisables qos directed multicast' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'directed_multicast': 'disabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Enable Qos IGMP Snooping]'
    common_name = '%sEnables qos igmp snooping' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'igmp_snooping_mode': 'enabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Disable Qos IGMP Snooping]'
    common_name = '%sDisables qos igmp snooping' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'igmp_snooping_mode': 'disabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Enable Qos MLD Snooping]'
    common_name = '%sEnables qos mld snooping' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'mld_snooping_mode': 'enabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Disable Qos MLD Snooping]'
    common_name = '%sDisables qos mld snooping' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'mld_snooping_mode': 'disabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Enable Qos Tos Classification]'
    common_name = '%sEnables qos tos classification' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'tos_classification': 'enabled'}}, test_name, common_name, 1, False))
    
    #@author: Liang Aihua, @@change: These case not exist in database(data:2014-11-13)
    #Add data plane testing for TOS classification.
    #test_cfgs.extend(_define_data_plane_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, True))
    
    test_case_name = '[Wlan Qos - Disable Qos Tos Classification]'
    common_name = '%sDisables qos tos classification' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'tos_classification': 'disabled'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Qos Priority]'
    common_name = '%sSets qos priority high' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'priority': 'high'}}, test_name, common_name, 1, False))
    
    common_name = '%sSets qos priority low' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'priority': 'low'}}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Qos - Qos Directed Threshold]'
    common_name = '%sConfigures QoS directed threshold' % (test_case_name,)
    test_cfgs.append(({'qos_conf': {'wlan': ssid, 'directed_threshold': '100'}}, test_name, common_name, 1, False))
    
    common_name = 'Cleanup test environment'
    test_cfgs.append(({'cleanup': True}, test_name, common_name, 0, True))
    
    
    #@author: Liang Aihua, @change: remove all these test cases that existed in Test Suite "configure qos"(data:2014-11-13)
    #Clean up for global qos setting.
    #test_name = 'CB_ZD_CLI_Configure_QoS'
    #common_name = 'Cleanup global Qos test environment'
    #test_cfgs.append(({'cleanup': True}, test_name, common_name, 0, True))
    
    #test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    #common_name = 'Quit browser in Station'
    #test_cfgs.append(({'sta_tag': sta_tag,
    #                   'browser_tag':browser_tag}, test_name, common_name, 0, False))
    
    #test_name = 'CB_ZD_Config_AP_Radio'
    #common_name = 'Config All APs Radio - Enable WLAN Service'
    #test_params = {'cfg_type': 'teardown',
    #               'all_ap_mac_list': cfg['all_ap_mac_list']}
    #test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #Remove wlan.
    #test_name = 'CB_ZD_Remove_All_Wlans'
    #common_name = 'Remove all WLANs from ZD'
    #test_cfgs.append(({}, test_name, common_name, 0, False))
    
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

def _define_data_plane_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_tos = False):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    
    sta_wlan_cfg = copy.deepcopy(wlan_cfg)
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, sta_wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg': sta_wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_case_name,) 
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information in ZD' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': sta_wlan_cfg,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Download_File'
    common_name = '%sVerify download file from server' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag': browser_tag,
                       #'validation_url': "http://%s/authenticated/" % target_ip_addr,
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name,)
    test_cfgs.append(({'ssid': sta_wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    #Define qos verification test cases.
    if is_tos:
        qos_conf = {'num_of_pkts':1000,
                    'tos':'0xc0',
                    'expect_queue':'voice',}
        
        test_name = 'CB_ZD_AP_Tos_Classification'
        common_name = '%sVerify TOS classification' % (test_case_name,)
        test_cfgs.append(({'wlan_name': sta_wlan_cfg['ssid'],
                           'ap_tag': ap_tag,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    else:
        qos_conf = {'num_of_pkts':1000,
                    'len_of_pkt':1500,
                    'pkt_gap':20000,
                    'expect_queue':'video',}
        
        test_name = 'CB_ZD_AP_Heuristic_Classification'
        common_name = '%sVerify heuristic classification' % (test_case_name,)
        test_cfgs.append(({'wlan_name': sta_wlan_cfg['ssid'],
                           'qos_conf': qos_conf,
                           'ap_tag': ap_tag,
                           'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove the wlan %s from station' % (sta_wlan_cfg['ssid'])
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_verify_qos_test_cfg(cfg):
    pass 
 
def _define_wlan_cfg():
    wlan_cfg = dict(ssid='qos-test-open-none', auth="open", encryption="none")
    
    return wlan_cfg
 
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
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break
            
    wlan_cfg = _define_wlan_cfg()
            
    if active_ap:
        tcfg = {'server_ip_addr': server_ip_addr,
                'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap':'%s' % active_ap,
                'all_ap_mac_list': all_ap_mac_list,
                'expected_sub_mask': expected_sub_mask,
                'expected_subnet': utils.get_network_address(server_ip_addr, expected_sub_mask),
                'wlan_cfg': wlan_cfg,
                }
        
        active_ap_cfg = ap_sym_dict[active_ap]        
        ap_type = testsuite.getApTargetType(active_ap,active_ap_cfg)
        
        test_cfgs = defineTestConfiguration(tcfg)
        
        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            ts_name = "Configure WLAN - QoS"
            #ts_name = "Configure Qos - Global and Wlan - 11%s %s" % (target_sta_radio, ap_type)
        ts = testsuite.get_testsuite(ts_name, "Verify WLAN qos configuration", combotest=True)    
        #ts = testsuite.get_testsuite(ts_name, "Verify qos configuration include global qos and wlan qos - 11%s %s" % (target_sta_radio, ap_type), combotest=True)
    
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
