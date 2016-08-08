"""
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
"""

import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

{'wlan_ssid': '', 'new_wlan_cfg': {}, 'negative_test': False}

wlan_cfg = dict(ssid = 'OPEN-WPA-DHCP-RELAY', auth = 'open', encryption = 'none')
default_server = {'ip_addr': '192.168.0.252', 'username': 'lab', 'password':'lab4man1', 'root_password':'lab4man1'}
relay_server = {'ip_addr': '192.168.0.152', 'username': 'lab', 'password':'lab4man1', 'root_password':'lab4man1'}
dhcp_relay_agent = [{'name': '192.168.0.252', 'description': 'Agent for default server',
                     'first_server': '192.168.0.252'},
                    {'name': '192.168.0.152', 'description': 'Agent for relay server',
                     'first_server': '192.168.0.152'},
                    {'name': 'agent for 152 and 252', 'description': 'Agent for two servers',
                     'first_server': '192.168.0.152', 'second_server': '192.168.0.252'}]

def define_test_cfg(cfg):
    test_cfgs = []
    sta_tag = 'STA1'
    ap_tag = 'AP1'
    
    tcname_list = ['DHCP Relay default setting',
                   'ZD DHCP Server is enabled',
                   'ZD DHCP Server is disabled',
                   'AP can not obtain IP via ZD relay agent',
                   'ZD - AP in same subnet and WLAN without tunnel',
                   'ZD - AP in same subnet and WLAN with tunnel',
                   'ZD - AP in diff subnet and WLAN without tunnel',
                   'ZD - AP in diff subnet and WLAN with tunnel',
                   'ZD DHCP Relay setting with two DHCP server'
                   ]
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = 'start DHCP service on server %s' % (relay_server['ip_addr'])
    test_cfgs.append(({'start_server': True,
                       'server_info': relay_server}, test_name, common_name, 0, False))   
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Identify the active AP'
    test_cfgs.append(({'ap_tag': ap_tag,
                       'active_ap': cfg['active_ap']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Delete_All_DHCP_Relay_Server'
    common_name = 'Remove all DHCP relay setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create the test WLAN on ZD'
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                       'check_wlan_timeout': 90}, test_name, common_name, 0, False))
    
    # TC1
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] by default DHCP relay is disable' % tcname_list[0]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] unable to set DHCP relay option without the DHCP Relay agents' % tcname_list[0]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel': True, 'dhcp_relay_svr': dhcp_relay_agent[1]['name']},
                       'negative_test': True}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = 'Create the DHCP Relay agent use server %s' % dhcp_relay_agent[1]['first_server']
    test_cfgs.append(({'dhcp_relay_svr_cfg': dhcp_relay_agent[1]}, test_name, common_name, 0, False))
    
    # TC2
    test_name = 'CB_ZD_Config_DHCP_Server'
    common_name = '[%s] enable DHCP server on ZD' % tcname_list[1]
    test_cfgs.append(({'option': 'enable'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] unable to set DHCP relay option' % tcname_list[1]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': True}, test_name, common_name, 2, False))
        
    # TC3
    test_name = 'CB_ZD_Config_DHCP_Server'
    common_name = '[%s] disable DHCP server on ZD' % tcname_list[2]
    test_cfgs.append(({'option': 'disable'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] enable to set tunnel mode option' % tcname_list[2]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel':True}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] enable to set DHCP relay option' % tcname_list[2]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    # Add a DHCP relay agent to ZD
    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = 'Create the DHCP Relay agent use server %s' % dhcp_relay_agent[0]['first_server']
    test_cfgs.append(({'dhcp_relay_svr_cfg': dhcp_relay_agent[0]}, test_name, common_name, 0, False))
    
    # TC5
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] disable tunnel mode on WLAN' % tcname_list[4]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel': False}, 
                       'negative_test': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] unable to set the DHCP relay option' % tcname_list[4]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': True}, test_name, common_name, 2, False))
    
    # TC6    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] enable the tunnel mode on WLAN' % tcname_list[5]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel': True}, 
                       'negative_test': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] set the DHCP relay option use server %s' % (tcname_list[5], dhcp_relay_agent[1]['name'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] associate station to WLAN' % tcname_list[5]
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] verify station got IP from server %s' % (tcname_list[5], dhcp_relay_agent[1]['name'])
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_dhcp_svr': dhcp_relay_agent[1]['first_server']
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] set the DHCP relay option use server %s' % (tcname_list[5], dhcp_relay_agent[0]['name'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[0]['name']}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] reconnect station to WLAN' % tcname_list[5]
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] verify station got IP from server %s' % (tcname_list[5], dhcp_relay_agent[0]['name'])
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_dhcp_svr': dhcp_relay_agent[0]['first_server']
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = 'Disable the DHCP Relay option on WLAN'
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel':True, 
                                        'dhcp_relay_svr': None}, 
                       'negative_test': False}, test_name, common_name, 0, True))    
    
    test_name = 'CB_ZD_Delete_All_DHCP_Relay_Server'
    common_name = 'Remove all DHCP relay setting on ZD for next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    # Reconnect AP to ZD from different subnet
    test_name = 'CB_ZD_Reconnect_AP_By_LWAPP'
    common_name = 'Reconnect AP to ZD from different subnet'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'mode': 'l3',
                       }, test_name, common_name, 0, False))
    
    # Add a DHCP relay agent to ZD
    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = 'Recreate the DHCP Relay agent use server %s' % dhcp_relay_agent[0]['first_server']
    test_cfgs.append(({'dhcp_relay_svr_cfg': dhcp_relay_agent[0]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = 'Recreate the DHCP Relay agent use server %s' % dhcp_relay_agent[1]['first_server']
    test_cfgs.append(({'dhcp_relay_svr_cfg': dhcp_relay_agent[1]}, test_name, common_name, 0, False))
    
    # TC4
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] enable the tunnel mode on WLAN' % tcname_list[3]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel': True}, 
                       'negative_test': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] set the DHCP relay option use server %s' % (tcname_list[3], dhcp_relay_agent[1]['name'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = '[%s] configure AP use DHCP and reboot' % tcname_list[3]
    test_cfgs.append(({'ap_tag': ap_tag,
                       'ip_cfg': {'ipv4':{'ip_mode': 'dhcp'}}}, test_name, common_name, 2, False))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = '[%s] stop DHCP service on server %s' % (tcname_list[3], default_server['ip_addr'])
    test_cfgs.append(({'start_server': False,
                       'server_info': default_server}, test_name, common_name, 1, False))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = '[%s] start DHCP service on server %s' % (tcname_list[3], relay_server['ip_addr'])
    test_cfgs.append(({'start_server': True,
                       'server_info': relay_server}, test_name, common_name, 1, False))   
    
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '[%s] reboot AP to get DHCP IP address' % tcname_list[3]
    test_cfgs.append(({'ap_tag': ap_tag,
                       'reboot': 'by zd'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '[%s] verify AP reconnect to ZD is fail' % tcname_list[3]
    test_cfgs.append(({'ap_tag': ap_tag, 'is_allow': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = '[%s] start DHCP service on server %s' % (tcname_list[3], default_server['ip_addr'])
    test_cfgs.append(({'start_server': True,
                       'server_info': default_server}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '[%s] verify AP reconnect to ZD is pass' % tcname_list[3]
    test_cfgs.append(({'ap_tag': ap_tag, 'is_allow': True}, test_name, common_name, 2, True))
    
    # TC7
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] disable tunnel mode on WLAN' % tcname_list[6]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel': False}, 
                       'negative_test': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] unable to set the DHCP relay option' % tcname_list[6]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': True}, test_name, common_name, 2, False))
    
    # TC8    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] enable the tunnel mode on WLAN' % tcname_list[7]
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'do_tunnel': True}, 
                       'negative_test': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] set the DHCP relay option use server %s' % (tcname_list[7], dhcp_relay_agent[1]['name'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[1]['name']}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] associate station to WLAN' % tcname_list[7]
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] verify station got IP from server %s' % (tcname_list[7], dhcp_relay_agent[1]['name'])
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_dhcp_svr': dhcp_relay_agent[1]['first_server']}
                      , test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] set the DHCP relay option use server %s' % (tcname_list[7], dhcp_relay_agent[0]['name'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[0]['name']}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] reconnect station to WLAN' % tcname_list[7]
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] verify station got IP from server %s' % (tcname_list[7], dhcp_relay_agent[0]['name'])
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_dhcp_svr': dhcp_relay_agent[0]['first_server']}, test_name, common_name, 2, False))
    
    # TC9
    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = '[%s] create the DHCP Relay %s' % (tcname_list[8], dhcp_relay_agent[2]['name'])
    test_cfgs.append(({'dhcp_relay_svr_cfg': dhcp_relay_agent[2]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] edit WLAN to use the %s' % (tcname_list[8], dhcp_relay_agent[2]['name'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent[2]['name']}, 
                       'negative_test': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] station associate to WLAN' % tcname_list[8]
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] verify station get IP address from server %s' % (tcname_list[8], dhcp_relay_agent[2]['first_server'])
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_dhcp_svr': [dhcp_relay_agent[2]['first_server'],
                                             dhcp_relay_agent[2]['second_server']]}, test_name, common_name, 2, False))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = '[%s] stop the service on server %s' % (tcname_list[8], relay_server['ip_addr'])
    test_cfgs.append(({'start_server': False,
                       'server_info': relay_server}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] reconnect station to WLAN' % tcname_list[8]
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] verify station get IP address from server %s' % (tcname_list[8], dhcp_relay_agent[2]['second_server'])
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_dhcp_svr': dhcp_relay_agent[2]['second_server']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Cleanup by remove all WLANs on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Delete_All_DHCP_Relay_Server'
    common_name = 'Cleanup by remove all DHCP relay setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Reconnect_AP_By_LWAPP'
    common_name = 'Cleanup by reconnect AP to ZD in the same subnet'
    test_cfgs.append(({'ap_tag': 'AP1',
                       'mode': 'l2',
                       }, test_name, common_name, 0, True))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = 'stop DHCP service on server %s' % (relay_server['ip_addr'])
    test_cfgs.append(({'start_server': False,
                       'server_info': relay_server}, test_name, common_name, 0, True))   
    
    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = testsuite.getActiveAp(ap_sym_dict)[0]
    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 1: ")        
    else:
        target_sta = sta_ip_list[attrs["station1"]][0]
    
    cfg = {'active_ap': active_ap,
           'target_station': target_sta}
    
    test_cfgs = define_test_cfg(cfg)
    

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "DHCP Relay in ZD"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the DHCP relay option in Zone Director",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
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