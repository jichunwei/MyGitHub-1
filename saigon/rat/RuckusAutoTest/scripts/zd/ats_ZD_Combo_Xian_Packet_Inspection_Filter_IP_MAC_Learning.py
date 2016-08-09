'''
Title: IP_MAC Learning - Packet Inspection Filter

Test purpose: Verify IP_MAC learning mechanism in PIF
    
Expect result: The station IP_MAC info can be recorded or deleted by AP as expected
    
TestCase_1 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) Verify the wlan PIF service status on AP.

TestCase_2 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) A Station associates the wlan and get IP by DHCP;
3) Verify the station IP_MAC info on AP.

TestCase_3 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) A Station associates the wlan and get IP by DHCP;
3) Clean the IP_MAC info learned by AP;
4) Perform ping from AP to the station;
5) Verify the station IP_MAC info on AP.

TestCase_4 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) A Station associates the wlan and get IP by DHCP;
3) Clean the IP_MAC info learned by AP;
4) Perform ping from the station to the server(192.168.0.252 by default);
5) Verify the station IP_MAC info on AP.

TestCase_5 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) Two Stations associate the wlan and get IP by DHCP;
3) Clean station1's IP_MAC info learned by AP;
4) Perform ping from station2 to station1;
5) Verify station1's IP_MAC info on AP.

TestCase_6 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) A Station associates the wlan and get IP by DHCP;
3) The station disconnects from the wlan initiatively;
4) Verify the station IP_MAC info on AP.

TestCase_7 steps:
1) Create a wlan with Proxy ARP and deploy it;
2) A Station associates the wlan and get IP by DHCP;
3) Release the wifi IP address on the station;
4) Verify the station IP_MAC info on AP;
5) Set IP_MAC entry aging time on AP as 3 minutes;
6) Wait for 3 minutes and verify the station IP_MAC info on AP again.

TestCase_8 steps:
1) Enable Mesh and ABF;
2) Create a wlan without Proxy ARP and deploy it on Root AP;
3) A Station associates the wlan and get IP by DHCP;
4) Verify the station IP_MAC info on Root AP;
5) Dis-deploy the wlan on Root AP, deploy it on Mesh AP;
6) The station associates the wlan and get IP again;
7) Verify the station IP_MAC info on Mesh AP.

Created on 2012-11-16
@author: sean.chen@ruckuswireless.com
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    ap1_tag = 'ap1'
    ap2_tag = 'ap2'
    sta1_tag = 'sta1-%s' % radio_mode
    sta2_tag = 'sta2-%s' % radio_mode
    target_sta1_ip = cfg['target_station1']
    target_sta2_ip = cfg['target_station2']
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Initiate environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Disable WLAN service'
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wireless station1'
    test_cfgs.append(({'sta_ip_addr': target_sta1_ip,
                       'sta_tag': sta1_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wireless station2'
    test_cfgs.append(({'sta_ip_addr': target_sta2_ip,
                       'sta_tag': sta2_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WLANs on wireless station1'
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WLANs on wireless station2'
    test_cfgs.append(({'sta_tag': sta2_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP1'
    test_cfgs.append(({'active_ap': cfg['active_ap1'],
                       'ap_tag': ap1_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP2'
    test_cfgs.append(({'active_ap': cfg['active_ap2'],
                       'ap_tag': ap2_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure active AP1 radio %s - Enable WLAN service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap1_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True}}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

#---TestCase_1-----------------------------------------------------------------------------------    
    test_case_name = 'Verify wlan Proxy_ARP info on AP'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP and record it' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_WLAN_Proxy_ARP_On_AP'
    common_name = '%sVerify the wlan proxy arp info on AP' % (test_combo_case_name,)
    test_params = {'ap_tag': ap1_tag, 'bridge':'br0', 'expected_status': 'p'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_PIF_Status_On_AP'
    common_name = '%sVerify PIF status on AP' % (test_combo_case_name,)
    test_params = {'ap_tag': ap1_tag, 'bridge':'br0', 'expected_status': 'yes'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
#---TestCase_2---------------------------------------------------------------------------------------
    test_case_name = 'IP_MAC learning with Proxy_ARP by DHCP'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_combo_case_name,)
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning on AP by DHCP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station' % (test_combo_case_name)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))

#---TestCase_3-----------------------------------------------------------------------------------
    test_case_name = 'IP_MAC learning with Proxy_ARP by ARP request'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % test_combo_case_name
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % test_combo_case_name
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % test_combo_case_name
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % test_combo_case_name
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clean_Station_IP_MAC_Info_On_AP'
    common_name = '%sClean the station IP and MAC info on AP' % test_combo_case_name
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sStation sends arp request by ping' % test_combo_case_name
    test_params = {'sta_tag': sta1_tag,
                   'condition': 'allowed',
                   'target': '192.168.0.252',
                   'clean_arp_before_ping': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify station IP MAC info learned on AP by ARP request' % test_combo_case_name
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station ' % test_combo_case_name
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % test_combo_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))

#---TestCase_4-----------------------------------------------------------------------------------
    test_case_name = 'IP_MAC learning with Proxy_ARP by ARP reply'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % test_combo_case_name
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % test_combo_case_name
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % test_combo_case_name
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % test_combo_case_name
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clean_Station_IP_MAC_Info_On_AP'
    common_name = '%sClean the station IP and MAC info on AP' % test_combo_case_name
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_AP_Ping_Station'
    common_name = '%sAP ping station' % test_combo_case_name
    test_params = {'ap_tag': ap1_tag, 'sta_tag': sta1_tag}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify station IP MAC info learned on AP by ARP reply' % test_combo_case_name
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station' % test_combo_case_name
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % test_combo_case_name
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
#---TestCase_5-----------------------------------------------------------------------------------    
    test_case_name = 'IP_MAC learning by sta1 arp_reply to sta2'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station1 to the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station1' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station1 wifi ip address in expected subnet' % (test_combo_case_name,)
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station2 to the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta2_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station2' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta2_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station2 wifi ip address in expected subnet' % (test_combo_case_name,)
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta2_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Clean_Station_IP_MAC_Info_On_AP'
    common_name = '%sClean the station1 IP and MAC info on AP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Another'
    common_name = '%sStation2 ping station1' % (test_combo_case_name,)
    test_params = {'src_sta_tag': sta2_tag,
                   'dst_sta_tag': sta1_tag,
                   'condition': 'allowed',
                   'clean_arp_before_ping': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station1 IP and MAC info learning on AP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station1' % (test_combo_case_name)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station2' % (test_combo_case_name)
    test_cfgs.append(({'sta_tag': sta2_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
#---TestCase_6-----------------------------------------------------------------------------------    
    test_case_name = 'IP_MAC entry aging time when station leaves wlan initiatively'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning by AP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Station_Disconnect_From_WLAN'
    common_name = '%sStation disconnects from the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning by AP again' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 
                   'ap_tag': ap1_tag, 
                   'bridge': 'br0', 
                   'expect_iptype': '4',
                   'waiting_time': 10,
                   'expect_exist': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station' % (test_combo_case_name)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
#---TestCase_7-----------------------------------------------------------------------------------    
    test_case_name = 'IP_MAC entry aging time when station leaves wlan passively'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid, 'do_proxy_arp': True, 'do_tunnel': False})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Release_Station_Wifi_Addr'
    common_name = '%sRelease wifi address of the station' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning by AP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_IP_MAC_Aging_Time_On_AP'
    common_name = '%sSet IP_MAC entry aging time on AP' % (test_combo_case_name,)
    test_params = {'ap_tag': ap1_tag, 'bridge': 'br0', 'age_time': '2'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning by AP again' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 
                   'ap_tag': ap1_tag, 
                   'bridge': 'br0', 
                   'expect_iptype': '4', 
                   'waiting_time': 120, 
                   'expect_exist': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station' % (test_combo_case_name)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
#---TestCase_8-----------------------------------------------------------------------------------    
    test_case_name = 'IP_MAC learning with ABF'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = '%sEnable Mesh and make AP2 as Mesh AP' % (test_combo_case_name,)
    test_cfgs.append(({'mesh_ap_list':cfg['mesh_ap']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_ABF'
    common_name = '%sEnable ABF' % (test_combo_case_name,)
    test_cfgs.append(({'do_abf': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    time.sleep(2)
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan info on AP1' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan on AP1' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_combo_case_name,)
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning on RAP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap1_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure active AP1 radio %s - Disable WLAN service' % (test_combo_case_name, radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap1_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': False}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure active AP2 radio %s - Enable WLAN service' % (test_combo_case_name, radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap2_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True}}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan info on AP2' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap2_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan on AP2' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station again' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet again' % (test_combo_case_name,)
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_IP_MAC_Info_On_AP'
    common_name = '%sVerify the station IP and MAC info learning on MAP' % (test_combo_case_name,)
    test_params = {'sta_tag': sta1_tag, 'ap_tag': ap2_tag, 'bridge': 'br0', 'expect_iptype': '4'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan on station ' % (test_combo_case_name)
    test_cfgs.append(({'sta_tag': sta1_tag}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sRestore active AP1 radio' % (test_combo_case_name)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap1_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True}}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure active AP2 radio ' % (test_combo_case_name)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap2_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': False}}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_ABF'
    common_name = '%sDisable ABF' % (test_combo_case_name)
    test_cfgs.append(({'do_abf': False}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%sEnable SW port to AP2' % (test_combo_case_name)
    test_cfgs.append(({'device': 'ap'}, test_name, common_name, 2, True))
    
    #@author: yuyanan @since: 2014-8-19 optimize:clear up mesh enviorment
    test_name = 'CB_ZD_Set_Factory_Default'
    common_name = '%sZD set factory' % (test_combo_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
#---TestCases End--------------------------------------------------------------------------------
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Enable WLAN service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

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
            radio_mode_key = '24g'
        elif radio in ['na']:
            radio_mode_key = '5g'
        expect_wlan_info.update({radio_mode_key: {'wlan_tag1': {}}})
        expect_wlan_info[radio_mode_key]['wlan_tag1']['status'] = status
        expect_wlan_info[radio_mode_key]['wlan_tag1']['encryption_cfg'] = dict(ssid = wlan_cfg['ssid'])

    return expect_wlan_info

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station = (0, "g"),
                  targetap = False,
                  testsuite_name = "")
    ts_cfg.update(kwargs)

    tb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']

    if ts_cfg["interactive_mode"]:
        print "Select a station as station1:"
        target_sta1 = testsuite.getTargetStation(sta_ip_list)
        sta_ip_list.remove(target_sta1)
        print "Select a station as station2:"
        target_sta2 = testsuite.getTargetStation(sta_ip_list)
        
        target_sta_radio = testsuite.get_target_sta_radio()

    else:
        target_sta1 = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
    
    wlan_cfg = {'ssid': 'standard_wlan_for_test', 
                'type': 'standard',
                'auth': 'open', 
                'encryption': 'none', 
                'sta_auth': 'open', 
                'sta_encryption': 'none',
                'do_proxy_arp': None,
                'do_tunnel': None,
                }

    tcfg = {'mesh_ap':'AP_02',
            'target_station1':'%s' % target_sta1,
            'target_station2':'%s' % target_sta2,
            'radio_mode': target_sta_radio,
            'active_ap1':'AP_01',
#            'active_ap1_mac':'%s' % ap_sym_dict['AP_01']['mac'],
            'active_ap2':'AP_02',
#            'active_ap2_mac':'%s' % ap_sym_dict['AP_02']['mac'],
            'wlan_cfg': wlan_cfg,
            'expected_sub_mask': '255.255.255.0',
            'expected_subnet': utils.get_network_address(server_ip_addr, '255.255.255.0'),
           }

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'PIF - IP_MAC Learning'

    ts = testsuite.get_testsuite(
        ts_name, 'Verify IP_MAC Learning in Packet Inspection Filter.',
        interactive_mode = ts_cfg["interactive_mode"],
        combotest = True )
    
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

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

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    