'''
Title: Ethernet Jumbo Frame Support - Basic

Test purpose: Verify mechanism for forwarding jumbo packet in basic scenario
    
Expect result: AP that supports the feature can support forwarding jumbo packet of special size
    
TestCase_1 steps:
1) Configure AP eth port MTU in jumbo frame MTU range;
2) Check if configure successfully.

TestCase_2 steps:
1) Configure AP eth port MTU to maximum;
2) Check if configure successfully.

TestCase_3 steps:
1) Configure AP eth port MTU to a value over maximum;
2) Check if configure successfully.

TestCase_4 steps:
1) Configure wired stations NIC MTU to maximum;
2) Configure AP eth port MTU to lower bound of jumbo frame MTU range;
3) Station ping another with different size packets.

TestCase_5 steps:
1) Configure wired stations NIC MTU to maximum;
2) Configure AP eth port MTU to upper bound of jumbo frame MTU range;
3) Station ping another with different size packets.

TestCase_6 steps:
1) Configure wired stations NIC MTU to maximum;
2) Configure AP eth port MTU to random value of jumbo frame MTU range;
3) Station ping another with different size packets.

TestCase_7 steps:
1) Configure wired stations NIC MTU to 1500;
2) Configure AP eth port MTU to 1500;
3) Station ping another with packet MTU larger than 1500, such as 1600 bytes.

TestCase_8 steps:
1) Configure wired stations NIC MTU to 9000;
2) Configure AP eth port MTU to 9000;
3) Station ping another with packet MTU larger than 9000, such as 9100 bytes.

TestCase_9 steps:
1) Configure wired stations NIC MTU to a random value in (1501, 8999);
2) Configure AP eth port MTU to a value same with wired stations;
3) Station ping another with packet MTU larger than the random value.

TestCase_10 steps:
1) Configure a wlan and make the wireless station connect to it;
2) Configure wired station NIC MTU to maximum;
3) Configure AP eth port MTU to a value larger than the maximum MTU supported in WLAN;
4) Wired station ping wireless station with packet of different MTU sizes, equal to or larger than the maximum MTU in WLAN.

TestCase_11 steps:
1) Enable Mesh and make APs as root AP and mesh AP;
2) Configure wired stations NIC MTU to maximum;
3) Configure AP eth port MTU to a value larger than the maximum MTU supported in Mesh;
4) Station ping another with packet of different MTU sizes, equal to or larger than the maximum MTU in Mesh. 

Created on 2013-01-18
@author: sean.chen@ruckuswireless.com
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    
    ap1_tag = 'ap1'
    ap2_tag = 'ap2'
    
    eth_sta1_tag = 'eth-sta1'
    eth_sta2_tag = 'eth-sta2'
    wifi_sta1_tag = 'sta1-%s' % radio_mode
    
    wifi_sta1_ip = cfg['sta1_cons_ip']
    eth_sta1_ip = cfg['sta2_cons_ip']
    eth_sta2_ip= cfg['sta3_cons_ip']
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Initiate environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Disable WLAN service'
    test_params = {'cfg_type': 'init', 'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wired station1'
    test_cfgs.append(({'sta_ip_addr': eth_sta1_ip,
                       'sta_tag': eth_sta1_tag,
                       'wired_sta': True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wired station2'
    test_cfgs.append(({'sta_ip_addr': eth_sta2_ip,
                       'sta_tag': eth_sta2_tag,
                       'wired_sta': True}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target wireless station'
    test_cfgs.append(({'sta_ip_addr': wifi_sta1_ip,
                       'sta_tag': wifi_sta1_tag}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WLANs on wireless station'
    test_cfgs.append(({'sta_tag': wifi_sta1_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP1'
    test_cfgs.append(({'active_ap': cfg['active_ap1'],
                       'ap_tag': ap1_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP2'
    test_cfgs.append(({'active_ap': cfg['active_ap2'],
                       'ap_tag': ap2_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure active AP2 radio %s - Enable WLAN service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap2_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True}}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

#---TestCase_1-----------------------------------------------------------------------------------
    test_case_name = 'Verify AP eth port MTU setting in jumbo frame MTU range'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'do_random': True,
                   'random_range': (1501, 9577),
                   'expect_status': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

#---TestCase_2-----------------------------------------------------------------------------------
    test_case_name = 'Verify AP eth port maximum MTU setting'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'mtu': 9578, 
                   'expect_status': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

#---TestCase_3-----------------------------------------------------------------------------------
    test_case_name = 'Verify AP eth port MTU setting over maximum'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'mtu': 9578, 
                   'over_data_size': 1,
                   'expect_status': False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

#---TestCase_4-----------------------------------------------------------------------------------    
    test_case_name = 'Verify AP forward when eth MTU set as lower bound'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with small frame' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 18,
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame up to AP current eth port MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 1472,
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame between small size and AP MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'do_random': True,
                   'random_range': (19, 1471),
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame over AP current eth port MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 1473,
                   'disfragment': True,
                   'condition': 'disallowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCase_5-----------------------------------------------------------------------------------
    test_case_name = 'Verify AP forward when eth MTU set as upper bound'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 9199}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 9199}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with small frame' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 18,
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame up to AP current eth port MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 9171,
                   'disfragment': True,
                   'allow_loss': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame between small size and AP MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'do_random': True,
                   'random_range': (19, 9170),
                   'disfragment': True,
                   'allow_loss': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame over AP current eth port MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 9172,
                   'disfragment': True,
                   'allow_loss': True,
                   'condition': 'disallowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCase_6-----------------------------------------------------------------------------------    
    test_case_name = 'Verify AP forward when eth MTU set as random'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU and record it' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'do_random': True, 
                   'random_range': (1501, 9198)}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 
                   'eth_interface': ['eth0', 'eth1'], 
                   'retrieve_mtu': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with small frame' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 18,
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame up to AP current eth port MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'retrieve_mtu': True,
                   'disfragment': True,
                   'allow_loss': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame between small size and AP MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'do_random': True,
                   'retrieve_mtu': True,
                   'disfragment': True,
                   'allow_loss': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame over AP current eth port MTU' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'retrieve_mtu': True,
                   'over_data_size': 1,
                   'disfragment': True,
                   'allow_loss': True,
                   'condition': 'disallowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCase_7-----------------------------------------------------------------------------------    
    test_case_name = 'AP forward fragment frame made at lower bound'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with fragment frame' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 1572,
                   'disfragment': False,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCase_8-----------------------------------------------------------------------------------    
    test_case_name = 'AP forward fragment frame made at upper bound'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 9000}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 9000}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 9000}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 9000}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with fragment frame' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'data_size': 9072,
                   'disfragment': False,
                   'allow_loss': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCase_9-----------------------------------------------------------------------------------    
    test_case_name = 'AP forward fragment frame made at random bound'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU and record it' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 
                   'do_random': True,
                   'random_range': (1501, 8999)}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 
                   'retrieve_sta_mtu': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'retrieve_sta_mtu': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'retrieve_sta_mtu': True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with fragment frame' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'src_sta_ip': cfg['wired_sta1_test_ip'],
                   'dst_sta_ip': cfg['wired_sta2_test_ip'],
                   'retrieve_sta_mtu': True,
                   'over_data_size': 100,
                   'disfragment': False,
                   'allow_loss': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#---TestCase_10-----------------------------------------------------------------------------------    
    test_case_name = 'Verify MTU supported in WLAN'
    test_combo_case_name = "[%s]" % test_case_name
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % test_combo_case_name 
    wlan_cfg = {}
    wlan_cfg.update(cfg['wlan_cfg'])
    ssid = 'standard_wlan_%s' % (time.strftime("%H%M%S"))
    wlan_cfg.update({'ssid': ssid})
    test_params = {'wlan_cfg_list':[wlan_cfg],
                   'enable_wlan_on_default_wlan_group': True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_combo_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap2_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate wireless station to the wlan' % (test_combo_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': wifi_sta1_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_combo_case_name,)
    test_cfgs.append(({'sta_tag': wifi_sta1_tag}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_combo_case_name,)
    expected_subnet = cfg['expected_subnet']
    expected_sub_mask = cfg['expected_sub_mask']
    test_cfgs.append(({'sta_tag': wifi_sta1_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1600}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1600}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping wireless sta1 with frame up to MAX MTU in WLAN' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': wifi_sta1_tag,
                   'data_size': 1472,
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping wireless sta2 with frame over MAX MTU in WLAN' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': wifi_sta1_tag,
                   'data_size': 1473,
                   'disfragment': True,
                   'condition': 'disallowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove the wlan on station after case: %s' % test_case_name
    test_cfgs.append(({'sta_tag': wifi_sta1_tag}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD after case: %s' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
#---TestCase_11-----------------------------------------------------------------------------------    
    test_case_name = 'Verify MTU supported in Mesh'
    test_combo_case_name = "[%s]" % test_case_name
    
    # Currently the maximum MTU in Mesh downlink is 2290, but the MTU in Mesh uplink is only up to 1500
    # So Mesh can only support 1500 MTU in bidirectional communication
    
    test_name = 'CB_ZD_Enable_Mesh'
    common_name = '%sEnable Mesh and make AP2 as Mesh AP' % test_combo_case_name
    test_cfgs.append(({'mesh_ap_mac_list': [cfg['active_ap2_mac']]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta1 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = '%sConfigure wired sta2 eth NIC MTU' % test_combo_case_name 
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 9578}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP1 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1600}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = '%sConfigure AP2 eth port MTU' % test_combo_case_name 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1600}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame up to maximum MTU in Mesh' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'data_size': 1472,
                   'disfragment': True,
                   'condition': 'allowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Eth_Client_Ping_Another'
    common_name = '%sWired sta1 ping sta2 with frame over maximum MTU in Mesh' % test_combo_case_name
    test_params = {'src_sta_tag': eth_sta1_tag,
                   'dst_sta_tag': eth_sta2_tag,
                   'data_size': 1473,
                   'disfragment': True,
                   'condition': 'disallowed'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'Enable SW port to AP2 after case: %s' % test_case_name
    test_cfgs.append(({'device': 'ap'}, test_name, common_name, 1, False))
    
#---TestCases End--------------------------------------------------------------------------------
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config all APs radio - Enable WLAN service'
    test_params = {'cfg_type': 'teardown', 'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = 'Restore wired sta1 default eth NIC MTU'
    test_params = {'sta_tag': eth_sta1_tag, 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Sta_Eth_Mtu_Setting'
    common_name = 'Restore wired sta2 default eth NIC MTU'
    test_params = {'sta_tag': eth_sta2_tag, 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = 'Restore AP1 default eth port MTU'
    test_params = {'ap_tag': ap1_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_AP_Eth_Mtu_Setting'
    common_name = 'Restore AP2 default eth port MTU' 
    test_params = {'ap_tag': ap2_tag, 'eth_interface': ['eth0', 'eth1'], 'mtu': 1500}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
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
                  sta_radio = 'ng',
                  testsuite_name = '')
    ts_cfg.update(kwargs)

    tb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    target_sta1 = sta_ip_list[0]
    target_sta2 = sta_ip_list[1]
    target_sta3 = sta_ip_list[2]
    
    if ts_cfg['interactive_mode']:
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta_radio = ts_cfg['sta_radio']
    
    wlan_cfg = {'ssid': 'standard_wlan_for_test', 
                'type': 'standard',
                'auth': 'open', 
                'encryption': 'none', 
                'sta_auth': 'open', 
                'sta_encryption': 'none',
                'do_tunnel': None,
                }

    tcfg = {'all_ap_mac_list': all_ap_mac_list,
            'sta1_cons_ip':'%s' % target_sta1,
            'sta2_cons_ip':'%s' % target_sta2,
            'sta3_cons_ip':'%s' % target_sta3,
            'wired_sta1_test_ip':'192.168.0.101',
            'wired_sta2_test_ip':'192.168.0.102',
            'radio_mode': target_sta_radio,
            'active_ap1':'AP_01',
            'active_ap1_mac':'%s' % ap_sym_dict['AP_01']['mac'],
            'active_ap2':'AP_02',
            'active_ap2_mac':'%s' % ap_sym_dict['AP_02']['mac'],
            'wlan_cfg': wlan_cfg,
            'expected_sub_mask': '255.255.255.0',
            'expected_subnet': utils.get_network_address(server_ip_addr, '255.255.255.0'),
           }

    test_cfgs = define_test_cfg(tcfg)

    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]

    else:
        ts_name = 'Ethernet Jumbo Frame Support - Basic'

    ts = testsuite.get_testsuite(
        ts_name, 'Verify mechanism for forwarding jumbo packet in basic scenario',
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
    