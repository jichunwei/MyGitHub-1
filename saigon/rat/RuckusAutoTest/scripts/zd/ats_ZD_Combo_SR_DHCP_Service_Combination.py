"""
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
"""

import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

wlan_cfg = {'ssid': 'OPEN-WPA-DHCP-SR', 'auth': 'open', 'encryption': 'none', 'do_tunnel': True}
linux_server_cfg = { 'ip_addr': '192.168.0.252', 'username': 'lab', 'password': 'lab4man1', 'root_password': 'lab4man1'}

dhcp_server_cfg1 = {'enable': True, 'start_ip': '192.168.0.10', 'number_ip': 10, 'leasetime': 'One day'}
dhcp_server_cfg2 = {'enable': True, 'start_ip': '192.168.0.50', 'number_ip': 15, 'leasetime': 'Six hours'}
disable_dhcp_server_cfg = {'enable': False}

dhcp_relay_agent_cfg = {'name': '192.168.0.252', 'description': 'Agent for default server', 'first_server': '192.168.0.252'}

target_vlan = ['301']
sr_timeout = 3600

def define_test_cfg(cfg):
    test_cfgs = []
    sta_tag = 'STA1'
    active_zd_tag = 'active_zd'
    standby_zd_tag = 'standby_zd'
    
    test_name = 'CB_ZD_SR_Init_Env'
    common_name = 'Initial SR ENV'
    test_cfgs.append(({}, test_name, common_name, 0, False))
   
    #TC1
    tc_name = 'S.R synchronize'
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy'
    test_cfgs.append(({},test_name,common_name, 0, False))
    
    test_name = 'CB_ZD_Configure_DHCP_Server'
    common_name = '[%s] Success to configure DHCP server on ZD1' % tc_name
    test_cfgs.append(({'zd_tag': 'zd1',
                       'dhcp_ser_cfg': dhcp_server_cfg1}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Configure_DHCP_Server'
    common_name = '[%s] Success to configure DHCP server on ZD2' % tc_name
    test_cfgs.append(({'zd_tag': 'zd2',
                       'dhcp_ser_cfg': dhcp_server_cfg2}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s] Enable Smart Redundancy for synchronize configuration' % tc_name
    test_cfgs.append(({'timeout':sr_timeout},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_Backup_DHCP_Server_Info'
    common_name = '[%s] Get all active ZD DHCP server configuration and released IPs info' % tc_name
    test_cfgs.append(({'zd_tag': active_zd_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_DHCP_Server_Info'
    common_name = '[%s] Verify dhcp server configure on standby ZD' % tc_name
    test_cfgs.append(({'zd_tag': standby_zd_tag}, test_name, common_name, 2, False))

    
    #Disable the test bed dhcp server and relay setting 
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = 'Configure APs get dynamic IP'
    test_cfgs.append(({'zd_tag': active_zd_tag,
                       'ip_cfg': {'ip_version': 'ipv4',
                                  'ipv4': {'ip_mode': 'dhcp'}}}, test_name, common_name, 0, True))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = 'Disable DHCP service on Linux server'
    test_cfgs.append(({'start_server': False,
                       'server_info': linux_server_cfg}, test_name, common_name, 0, False))
    
    test_name = 'CB_L3Switch_Configure_DHCP_Relay'
    common_name = 'Disable DHCP relay on L3 Switch'
    test_cfgs.append(({'dhcp_relay_conf': {'enable': False,
                                           'vlans': target_vlan}}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Reboot_APs'
    common_name = 'Reboot to Reconnect All APs by new IPs'
    test_cfgs.append(({'zd_tag': active_zd_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr': cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs on ZD'
    test_cfgs.append(({'zd_tag': active_zd_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Delete_All_DHCP_Relay_Server'
    common_name = 'Remove all DHCP relay setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    #TC2
    tc_name= 'DHCP server with tunnel wlan'
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s] Create the tunnel WLAN on ZD' % tc_name
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                       'check_wlan_timeout': 90}, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] Verify Station connect to WLAN' % tc_name
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Assigned_IP_Display'
    common_name = '[%s] Verify station info in assigned ip list' % tc_name
    test_cfgs.append(({'zd_tag': active_zd_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    #TC3
    tc_name = 'DHCP relay not supported under dhcp server'
    test_name = 'CB_ZD_Create_DHCP_Relay_Server'
    common_name = '[%s] Configure DHCP relay on active ZD' % tc_name
    test_cfgs.append(({'zd_tag': active_zd_tag,
                       'dhcp_relay_svr_cfg': dhcp_relay_agent_cfg}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s] Unable to set DHCP relay option' % tc_name
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 
                       'new_wlan_cfg': {'dhcp_relay_svr': dhcp_relay_agent_cfg['name']}, 
                       'negative_test': True}, test_name, common_name, 2, False))
    

    #
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Cleanup by remove all WLANs on ZD'
    test_cfgs.append(({'zd_tag': active_zd_tag}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Delete_All_DHCP_Relay_Server'
    common_name = 'Remove all DHCP relay setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Configure_DHCP_Server'
    common_name = 'Disable ZD DHCP server'
    test_cfgs.append(({'zd_tag': active_zd_tag,
                       'dhcp_ser_cfg': disable_dhcp_server_cfg}, test_name, common_name, 0, True))
    
    test_name = 'CB_LinuxPC_Config_DHCP_Server_Option'
    common_name = 'Enable DHCP service on Linux server'
    test_cfgs.append(({'start_server': True,
                       'server_info': linux_server_cfg}, test_name, common_name, 0, True))
    
    test_name = 'CB_L3Switch_Configure_DHCP_Relay'
    common_name = 'Enable DHCP relay on L3 Switch'
    test_cfgs.append(({'dhcp_relay_conf': {'enable': True,
                                           'vlans': target_vlan}}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Reboot_APs'
    common_name = 'Reboot to Reconnect All APs by new IPs from Linux Server'
    test_cfgs.append(({'zd_tag': active_zd_tag}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD after test'
    test_cfgs.append(({},test_name, common_name, 0, True))
           
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
   
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 1: ")        
    else:
        target_sta = sta_ip_list[attrs["station1"]][0]
    
    cfg = {'target_station': target_sta}
    
    test_cfgs = define_test_cfg(cfg)
    

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "DHCP Service Support under S.R Enabled - Combination"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the Service Support under S.R Enabled - Combination",
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