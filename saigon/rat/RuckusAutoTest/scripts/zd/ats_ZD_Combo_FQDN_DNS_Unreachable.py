"""
Verify AP joins expected ZD when enable FQDN in ZD CLI, shutdown and start dns server.

    Verify AP join ZD successfully when enable FQDN in ZD CLI.
    Pre-condition:
       AP joins ZD1
       ZD1 is auto approval
       ZD2 is manual approval
       ZD2 enable FQDN and set as Keep AP's setting
    Test Data:
       Primary IPV4 FQDN Secondary Invalid IPV6 FQDN
       Primary IPV6 FQDN Secondary Invalid IPV4 FQDN
    
    expect result: All steps should result properly.
    
    How to:
        1) Create and Get ZD components from testbed and put them in carrier bag.
        2) Remove all wlan groups and wlans from ZD2.
        3) Enable FQDN in ZD2 and set it as keep ap's setting.   
        4) Set auto approval as True in ZD1 and False in ZD2.
        5) Create station.
        6) Create active ap.
        7) Create wlan and wlan group in ZD2.
        8) Prepare for test:
              Disable FQDN in ZD1 and AP CLI 
              Remove all APs from ZD1 and ZD2
              Verify AP joins ZD1.
        9) Shutdown DNS server.
        10) Configure FQDN in ZD1, primary is zd2 and secondary is invalid domain name.
        11) Verify FQDN settings in AP CLI.
        12) Verify FQDN didn't join any ZD.
        13) Start DNS server and reboot AP.
        14) Verify AP joins ZD2.
        15) Associate the station to wlan and verify ping traffic to server.
        16) Clean up the environment: 
              Disable FQDN in ZD1, ZD2 and AP CLI
              Remove all APs in ZD1 and ZD2
              Make sure AP joins ZD1.        
              Remove all wlan and wlan group in ZD2.
              Start DNS server.           
    
Created on 2012-04-22
@author: cherry.cheng@ruckuswireless.com
"""

import sys, copy
import random

import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_cfg(cfg):
    test_cfgs = []
    
    zd_discovery_cfg_list = cfg['zd_discovery_cfg_list']
    zd_discovery_cfg_keep_ap_setting = cfg['zd_discovery_cfg_keep_ap_setting']
    
    target_ip_list = cfg['target_ip_list']
    
    zd1_wlan_cfg = cfg['zd1_wlan_cfg']
    zd2_wlan_cfg = cfg['zd2_wlan_cfg']
    zd1_wg_name = cfg['zd1_wg_name']
    zd2_wg_name = cfg['zd2_wg_name']
    
    zd1_gui_tag = cfg['zd1_gui_tag']
    zd2_gui_tag = cfg['zd2_gui_tag']
    zd1_cli_tag = cfg['zd1_cli_tag']
    zd2_cli_tag = cfg['zd2_cli_tag']
    
    dns_service_name = cfg['dns_service_name']
    
    radio_mode = cfg['radio_mode']
    active_ap = cfg['active_ap']
    active_ap_mac = cfg['active_ap_mac']
    
    enable_mgmt_vlan = cfg['enable_mgmt_vlan']
    ap_mgmt_vlan = cfg['ap_mgmt_vlan']
    ap_default_vlan = cfg['ap_default_vlan']
    
    sta_tag = 'statest'
    ap_tag = 'aptest'
    
    test_name = 'CB_ZD_Primary_Secondary_Create_ZDs'
    common_name = 'Find or Create ZD IPV4 and IPV6 components'
    test_params = {'zd_tag_list': [zd1_gui_tag, zd2_gui_tag, zd1_cli_tag, zd2_cli_tag]}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups from ZD2'
    test_cfgs.append(({'zd_tag': zd2_gui_tag,
                       'is_ap_on_zd': False,}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD2'
    test_cfgs.append(({'zd_tag': zd2_gui_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Configure FQDN as Keep AP setting for ZD2'
    test_params = {'zd_tag': zd2_cli_tag}
    test_params.update(zd_discovery_cfg_keep_ap_setting)    
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'Set ZD1 Auto Approval as True'
    test_params = {'auto_approval': True,
                   'zd_tag': zd1_gui_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'Set ZD2 Auto Approval as False'
    test_params = {'auto_approval': False,
                   'zd_tag': zd2_gui_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    if enable_mgmt_vlan:
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Backup AP Mgmt VLAN on ZD1"
        test_params = {'cfg_type': "init",
                       'zd_tag': zd1_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        #Steps for enable management vlan.
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Config AP Mgmt VLAN to %s on ZD1" % ap_mgmt_vlan
        test_params = {'mgmt_vlan': {'mode': "enable", 'vlan_id': ap_mgmt_vlan, },
                       'cfg_type': "config",
                       'zd_tag': zd1_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = 'Verify all APs Join ZD1'
        test_cfgs.append(({ 'auto_approval': True,
                            'zd_tag': zd1_gui_tag,
                            'verify_ap_component': False,
                            #'mac_addr_list': [active_ap_mac]
                            }, test_name, common_name, 0, False))
        
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Config AP Mgmt VLAN as keep ap setting on ZD2"
        test_params = {'mgmt_vlan': {'mode': "keep"},
                       'cfg_type': "config",
                       'zd_tag': zd2_gui_tag
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        #Recreate all ap components based on enable mgmt vlan for ap.
        test_name = 'CB_ZD_Recreate_All_APs'
        common_name = 'Recreate all AP components'
        test_cfgs.append(({'zd_tag': zd1_gui_tag}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a wlan on ZD2'
    test_cfgs.append(({'zd_tag': zd2_gui_tag,
                       'wlan_cfg_list':[zd2_wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                       'check_wlan_timeout': 10}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_WLANGroups_with_WLANs' 
    common_name = 'Create a wlan group with wlan on ZD2'
    test_cfgs.append(({'zd_tag': zd2_gui_tag,
                       'wlangroups_map': {zd2_wg_name: [zd2_wlan_cfg['ssid']]},
                       }, test_name, common_name, 0, False))
    
    for zd_discovery_test_cfg in zd_discovery_cfg_list:
        test_case_name = '%s' % zd_discovery_test_cfg['case_name']
        
        zd_discovery_cfg = zd_discovery_test_cfg['cfg']
        primary_zd_ip = zd_discovery_cfg['primary_zd_ip']
        secondary_zd_ip = zd_discovery_cfg['secondary_zd_ip']
        expected_zd_tag = zd_discovery_test_cfg['expected_zd_tag']
        
        test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
        common_name = '%s-Disable FQDN in ZD1 before test' % test_case_name
        test_params = {'enabled': False, 'zd_tag': zd1_cli_tag}        
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
        common_name = '%s-Disable FQDN in AP CLI before test' % test_case_name
        test_params = {'ap_tag': ap_tag}
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_SR_Delete_All_AP'
        common_name = '%s-Remove all APs from ZD1 and ZD2 before test' % test_case_name
        test_params = {}
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = '%s-Verify AP Join ZD1 before test' % test_case_name
        test_cfgs.append(( {'auto_approval': True,
                            'zd_tag': zd1_gui_tag,
                            'mac_addr_list': [active_ap_mac]}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Start_Stop_DNS_On_Server'
        common_name = '[%s]Stop DNS on Server' % test_case_name
        test_params = {'is_ipv6_server': True,
                       'is_start_server': False,
                       'dns_service_name': dns_service_name}        
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
        common_name = '[%s]Configure FQDN in ZD1 via CLI' % test_case_name
        test_params = {'zd_tag': zd1_cli_tag}
        test_params.update(zd_discovery_cfg)
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_AP_CLI_Get_Verify_Primary_Secondary_ZD'
        common_name = '[%s]Verify FQDN in AP CLI' % test_case_name
        test_params = {'ap_tag': ap_tag,
                       'is_verify': True,
                       'primary_zd_ip': primary_zd_ip,
                       'secondary_zd_ip': secondary_zd_ip
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Reboot_AP'
        common_name = '[%s]Reboot AP' % test_case_name
        test_cfgs.append(( {'ap_tag': ap_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = "[%s]Verify AP don't Join ZD1" % test_case_name
        test_cfgs.append(( {'auto_approval': True,
                            'is_allow': False,
                            'timeout': 120,
                            'zd_tag': zd1_gui_tag,
                            'mac_addr_list': [active_ap_mac]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = "[%s]Verify AP don't Join ZD2" % test_case_name
        test_cfgs.append(( {'is_need_approval': True,
                            'auto_approval': False,
                            'is_allow': False,
                            'timeout': 120,
                            'zd_tag': zd2_gui_tag,
                            'mac_addr_list': [active_ap_mac]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_SR_Delete_All_AP'
        common_name = '[%s]Remove all APs from ZD1 and ZD2 before start DNS' % (test_case_name,)
        test_params = {}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Start_Stop_DNS_On_Server'
        common_name = '[%s]Start DNS on Server' % test_case_name
        test_params = {'is_ipv6_server': True,
                       'is_start_server': True,
                       'dns_service_name': dns_service_name}        
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Reboot_AP'
        common_name = '[%s]Reboot AP after start DNS' % test_case_name
        test_cfgs.append(( {'ap_tag': ap_tag}, test_name, common_name, 2, False))
        
        if 'zd1' in expected_zd_tag.lower():
            exp_zd_name = "ZD1"
            wg_name = zd1_wg_name            
            sta_wlan_cfg = zd1_wlan_cfg
        else:
            exp_zd_name = "ZD2"
            wg_name = zd2_wg_name
            sta_wlan_cfg = zd2_wlan_cfg
            
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = '[%s]Verify AP Joins %s' % (test_case_name, exp_zd_name)
        test_cfgs.append(( {'is_need_approval': True,
                            'auto_approval': False,
                            'zd_tag': expected_zd_tag,
                            'mac_addr_list': [active_ap_mac]}, test_name, common_name, 2, False))        
        
        test_name = 'CB_AP_CLI_Get_Verify_Primary_Secondary_ZD'
        common_name = '[%s]Verify FQDN in AP CLI after AP join %s' % (test_case_name, exp_zd_name)
        test_params = {'ap_tag': ap_tag,
                       'is_verify': True,
                       'primary_zd_ip': primary_zd_ip,
                       'secondary_zd_ip': secondary_zd_ip
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = "[%s]Assign wlan group to radio '%s' of AP %s on %s" % (test_case_name, radio_mode, active_ap, exp_zd_name)
        test_params = {'active_ap': active_ap,
                       'wlan_group_name': wg_name, 
                       'radio_mode': radio_mode,
                       'zd_tag': expected_zd_tag}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        common_name = '[%s]Associate the station to %s wlan' % (test_case_name, exp_zd_name)
        params = {'sta_tag': sta_tag,
                  'wlan_cfg': sta_wlan_cfg,
                  'start_browser': False,
                  'get_sta_wifi_ip': False,   
                  'verify_ip_subnet': False,           
                  }    
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '[%s]Verify ping target IPs for %s wlan' % (test_case_name, exp_zd_name)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': target_ip_list,
                  'download_file': False,
                  'close_browser': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Start_Stop_DNS_On_Server'
    common_name = 'Start DNS on Server after test'
    test_params = {'is_ipv6_server': True,
                   'is_start_server': True,
                   'dns_service_name': dns_service_name}        
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    #Clean up the environment, make sure AP join ZD1.
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable FQDN in ZD1 after test'
    test_params = {'enabled': False, 'zd_tag': zd1_cli_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable FQDN in ZD2 after test'
    test_params = {'enabled': False, 'zd_tag': zd2_cli_tag}        
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable all AP FQDN in AP CLI after test'
    test_params = {} #{'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Delete_All_AP'
    common_name = 'Remove all APs from ZD1 and ZD2 after test'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    if enable_mgmt_vlan:
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Restore AP Mgmt VLAN on ZD1 after test"
        test_params = {'cfg_type': "teardown",
                       'zd_tag': zd1_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Restore AP Mgmt VLAN on ZD2 after test"
        test_params = {'cfg_type': "teardown",
                       'zd_tag': zd2_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = 'Verify all APs Join ZD1 after test'
        test_cfgs.append(({ 'auto_approval': True,
                            'zd_tag': zd1_gui_tag,
                            'verify_ap_component': False,
                            #'mac_addr_list': [active_ap_mac]
                            }, test_name, common_name, 0, False))
        
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Config AP Mgmt VLAN as keep ap setting on ZD2 after test"
        test_params = {'mgmt_vlan': {'mode': "keep"},
                       'cfg_type': "config",
                       'zd_tag': zd2_gui_tag
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        #Recreate all ap components based on enable mgmt vlan for ap.
        test_name = 'CB_ZD_Recreate_All_APs'
        common_name = 'Recreate all AP components after test'
        test_cfgs.append(({'zd_tag': zd1_gui_tag}, test_name, common_name, 0, False))
    else:
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = 'Verify AP Join ZD1 after test'
        test_cfgs.append(( {'auto_approval': True,
                            'zd_tag': zd1_gui_tag,
                            'mac_addr_list': [active_ap_mac]}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups from ZD2 after test'
    test_cfgs.append(({'zd_tag': zd2_gui_tag,
                       'is_ap_on_zd': False,}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD2 after test'
    test_cfgs.append(({'zd_tag': zd2_gui_tag}, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_zd_discovery_keep_ap_setting():
    zd_keep_ap_setting = {'enabled': True,
                          'keep_ap_setting': True
                          }
    
    return zd_keep_ap_setting                        

def _define_zd_discovery_test_cfg(zd1_gui_tag, zd2_gui_tag, zd1_cli_tag, zd2_cli_tag, zd1_gui_ipv6_tag, zd2_gui_ipv6_tag):
    zd2_ipv4_dn = 'www.ruckuszd2.net'
    zd2_ipv6_dn = 'www.ipv6-ruckuszd2.net'
    
    zd_ipv4_dn_unreachable = 'www.ruckuszd-unreacheable.net'
    zd_ipv6_dn_unreachable = 'www.ipv6-ruckuszd-unreacheable.net'
    
    test_cfg_list = []
    
    default_cfg = {'enabled': True,
                   'primary_zd_ip': '',
                   'secondary_zd_ip': '',
                   'keep_ap_setting': False,
                   'prefer_prim_zd': False,
                   }
    
    test_cfg_list.append({'case_name': 'Primary IPV4 FQDN Secondary Invalid IPV6 FQDN',
                          'primary_zd_ip': zd2_ipv4_dn,
                          'secondary_zd_ip': zd_ipv6_dn_unreachable,
                          'expected_zd_tag': zd2_gui_tag})
    
    test_cfg_list.append({'case_name': 'Primary IPV6 FQDN Secondary Invalid IPV4 FQDN',
                          'primary_zd_ip': zd2_ipv6_dn,
                          'secondary_zd_ip': zd_ipv4_dn_unreachable,
                          'expected_zd_tag': zd2_gui_tag})
    
    zd_cfg_list = []
    for cfg in test_cfg_list:
        new_cfg = copy.deepcopy(default_cfg)
        new_cfg['primary_zd_ip'] = cfg['primary_zd_ip']
        new_cfg['secondary_zd_ip'] = cfg['secondary_zd_ip']
        
        zd_test_cfg = {}
        zd_test_cfg['case_name'] = cfg['case_name']
        zd_test_cfg['expected_zd_tag'] = cfg['expected_zd_tag']
        zd_test_cfg['cfg'] = new_cfg
        
        zd_cfg_list.append(zd_test_cfg)     
    
    return zd_cfg_list    

def _def_wlan_cfg():
    wlan_cfg = dict(ssid='wlan-fqdn-%04d' % random.randrange(1, 9999), 
                   auth="open", wpa_ver="", encryption="none", 
                   key_index="", key_string="",)
    
    return wlan_cfg

def _def_wlan_group_name():
    wg_name = 'wg-fqdn-%03d' % random.randrange(1, 999)
    
    return wg_name

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    
    zd1_gui_tag = 'zd1'
    zd2_gui_tag = 'zd2'
    zd1_cli_tag = 'ZDCLI1'
    zd2_cli_tag = 'ZDCLI2'
    zd1_gui_ipv6_tag = 'ZD1IPV6'
    zd2_gui_ipv6_tag = 'ZD2IPV6'
        
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
            break
        
    ap_mgmt_vlan = '1'
    enable_mgmt_vlan = raw_input("Enable management vlan for ap (y/n):").lower() == 'y'
    if enable_mgmt_vlan:
        ap_mgmt_vlan = raw_input("Please input management vlan for ap [default is 10]:")
        if not ap_mgmt_vlan:
            ap_mgmt_vlan = '10'
        
    dns_service_name = raw_input("Please input DNS service name [Default is dnsmasq]: ")
    if not dns_service_name:
        dns_service_name = 'dnsmasq'
    
    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]        
        active_ap_mac = active_ap_cfg['mac']
        active_ap_model = active_ap_cfg['model']
        
        zd1_wlan_cfg = _def_wlan_cfg()
        zd2_wlan_cfg = _def_wlan_cfg()
        
        zd1_wg_name = _def_wlan_group_name()
        zd2_wg_name = _def_wlan_group_name()
        
        zd_discovery_cfg_list = _define_zd_discovery_test_cfg(zd1_gui_tag, zd2_gui_tag, zd1_cli_tag, zd2_cli_tag, zd1_gui_ipv6_tag, zd2_gui_ipv6_tag)
        zd_discovery_cfg_keep_ap_setting = _define_zd_discovery_keep_ap_setting()
            
        tcfg = {'zd_discovery_cfg_list': zd_discovery_cfg_list,
                'zd_discovery_cfg_keep_ap_setting': zd_discovery_cfg_keep_ap_setting,
                'target_station':'%s' % target_sta,
                'active_ap':'%s' % active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,
                'radio_mode': target_sta_radio,
                'zd1_wlan_cfg': zd1_wlan_cfg,
                'zd2_wlan_cfg': zd2_wlan_cfg,
                'zd1_wg_name': zd1_wg_name,
                'zd2_wg_name': zd2_wg_name,
                'target_ip_list': [server_ip_addr],
                'zd1_gui_tag': zd1_gui_tag,
                'zd2_gui_tag': zd2_gui_tag,
                'zd1_cli_tag': zd1_cli_tag,
                'zd2_cli_tag': zd2_cli_tag,
                'zd1_gui_ipv6_tag': zd1_gui_ipv6_tag,
                'zd2_gui_ipv6_tag': zd2_gui_ipv6_tag,
                'dns_service_name': dns_service_name,
                'enable_mgmt_vlan': enable_mgmt_vlan,
                'ap_mgmt_vlan': ap_mgmt_vlan,
                'ap_default_vlan': '1',
                }
    
        test_cfgs = define_test_cfg(tcfg)
    
        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            if enable_mgmt_vlan:
                ts_name = "ZD CLI - Enable FQDN DNS Unreachable with AP Mgmt Vlan 11%s" % (target_sta_radio)
            else:
                ts_name = "ZD CLI - Enable FQDN DNS Unreachable 11%s" % (target_sta_radio)
    
        ts = testsuite.get_testsuite(ts_name, "Verify AP join ZD when enable FQDN and shutdown and start DNS server", combotest = True)
    
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