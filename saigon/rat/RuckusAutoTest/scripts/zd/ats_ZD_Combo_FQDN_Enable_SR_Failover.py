"""
Verify AP joins expected ZD when enable FQDN in AP CLI, enable mgmt vlan in ZD.

    Verify AP join ZD successfully when enable FQDN in AP CLI.
    Pre-condition:
       AP joins ZD1
       ZD1 is auto approval
       ZD2 is manual approval
       ZD2 enable FQDN and set as Keep AP's setting
    Test Data:
        Primary ZD1 IPV4 FQDN Secondary ZD2 IPV6 FQDN
        Primary ZD1 IPV6 FQDN Secondary ZD2 IPV4 FQDN
        Primary ZD2 IPV4 FQDN Secondary ZD1 IPV4 FQDN
        Primary ZD2 IPV6 FQDN Secondary ZD1 IPV6 FQDN
    
    expect result: All steps should result properly.
    
    How to:
        1) Create and Get ZD components from testbed and put them in carrier bag.
        2) Init SR environment.
        3) Enable Smart Redundancy in zd1 and zd2.
        4) Remove all wlan groups and wlans from active ZD.
        5) Set auto approval as False in active ZD.
        6) Create station.
        7) Create active ap.
        8) Create wlan and wlan group in active ZD.
        9) Prepare for test:
              Disable FQDN in active ZD and AP CLI 
              Remove all APs from ZD1 and ZD2
              Verify AP joins active ZD.
        10) Configure FQDN in ZD, one is ZD1, another is ZD2.
        11) Verify FQDN settings in AP CLI between set and get.
        12) Make active ZD unreachable: 
                Disable active ZD switch port.
                Click Failover button.
        13) Verify AP join standby ZD.
        14) Verify FQDN settings after AP join ZD2.
        15) Associate the station to wlan and verify ping traffic to server.
        16) Clean up the environment:
              Disable Smart Redundancy
              Disable FQDN in ZD1, ZD2 and AP CLI
              Remove all APs in ZD1 and ZD2
              Make sure AP joins ZD1.        
              Remove all wlan and wlan group in ZD2.       
    
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
    #zd_discovery_cfg_keep_ap_setting = cfg['zd_discovery_cfg_keep_ap_setting']
    
    wlan_cfg = cfg['wlan_cfg']
    wg_name = cfg['wg_name']
    
    target_ip_list = cfg['target_ip_list']

    zd1_gui_tag = cfg['zd1_gui_tag']
    zd2_gui_tag = cfg['zd2_gui_tag']    
    
    radio_mode = cfg['radio_mode']
    active_ap = cfg['active_ap']
    active_ap_mac = cfg['active_ap_mac']
    
    enable_mgmt_vlan = cfg['enable_mgmt_vlan']
    ap_mgmt_vlan = cfg['ap_mgmt_vlan']
    ap_default_vlan = cfg['ap_default_vlan']

    sta_tag = 'statest'
    ap_tag = 'aptest'
    
    zd1_if_tag = 'if%s' % zd1_gui_tag
    zd2_if_tag = 'if%s' % zd2_gui_tag
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial SR  Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_Switch_Interface' 
    common_name = 'Get ZD1 Switch Interface'
    test_cfgs.append(({'zd_tag': zd1_gui_tag, 
                       'if_tag': zd1_if_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_Switch_Interface' 
    common_name = 'Get ZD2 Switch Interface'
    test_cfgs.append(({'zd_tag': zd2_gui_tag, 
                       'if_tag': zd2_if_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Enable SR in Both ZD'
    test_cfgs.append(({'zd1': zd1_gui_tag,
                       'zd2': zd2_gui_tag,
                       'timeout': 300},test_name,common_name,0,False))
    
    active_zd = 'active_zd'
    standby_zd = 'standby_zd'
    active_zd_cli = 'active_zd_cli'
    standby_zd_cli = 'standby_zd_cli'
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups from active ZD'
    test_cfgs.append(({'zd_tag': active_zd}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from active ZD'
    test_cfgs.append(({'zd_tag': active_zd}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'Set active ZD Auto Approval as False'
    test_params = {'auto_approval': False,
                   'zd_tag': active_zd}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    if enable_mgmt_vlan:
        #Steps for enable management vlan.
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Backup AP Mgmt VLAN on ZD1"
        test_params = {'cfg_type': "init",
                       'zd_tag': zd1_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Config AP Mgmt VLAN to %s on active ZD" % ap_mgmt_vlan
        test_params = {'mgmt_vlan': {'mode': "enable", 'vlan_id': ap_mgmt_vlan, },
                       'cfg_type': "config",
                       'zd_tag': active_zd,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = 'Verify all APs Join active ZD'
        test_cfgs.append(({'is_need_approval': True,
                           'auto_approval': False,
                           'zd_tag': active_zd,
                           'verify_ap_component': False,
                           'mac_addr_list': [active_ap_mac]
                           }, test_name, common_name, 0, False))
        
        #Recreate all ap components based on enable mgmt vlan for ap.
        test_name = 'CB_ZD_Recreate_All_APs'
        common_name = 'Recreate all AP components'
        test_cfgs.append(({'zd_tag': active_zd}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a wlan and remove from default wlan group on active ZD'
    test_cfgs.append(({'zd_tag': active_zd,
                       'wlan_cfg_list':[wlan_cfg],
                       'enable_wlan_on_default_wlan_group': False,
                       'check_wlan_timeout': 10}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_WLANGroups_with_WLANs' 
    common_name = 'Create a wlan group with wlan on active ZD'
    test_cfgs.append(({'zd_tag': active_zd,
                       'wlangroups_map': {wg_name: [wlan_cfg['ssid']]},
                       }, test_name, common_name, 0, False))
    
    #for zd_discovery_test_cfg in zd_discovery_cfg_list:
    for index in range(1, len(zd_discovery_cfg_list)+1):
        
        zd_discovery_test_cfg = zd_discovery_cfg_list[index-1]
        
        if index % 2 == 0:
            case_type = "failover"
            test_case_prefix = "Click Failover"
        else:
            case_type = "shutdown"
            test_case_prefix = "Shutdown ZD Port"
            
        test_case_name = '%s %s' % (test_case_prefix, zd_discovery_test_cfg['case_name'])
        
        zd_discovery_cfg = zd_discovery_test_cfg['cfg']

        primary_zd_ip = zd_discovery_cfg['primary_zd_ip']
        secondary_zd_ip = zd_discovery_cfg['secondary_zd_ip']
        
        test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
        common_name = '%s-Disable FQDN in active ZD before test' % test_case_name
        test_params = {'enabled': False, 'zd_tag': active_zd_cli}
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
        common_name = '%s-Disable FQDN in AP CLI before test' % test_case_name
        test_params = {'ap_tag': ap_tag}
        test_cfgs.append((test_params, test_name, common_name, 1, False))

        test_name = 'CB_ZD_SR_Delete_All_AP'
        common_name = '%s-Remove all APs from ZD1 ZD2 before test' % test_case_name
        test_params = {}
        test_cfgs.append((test_params, test_name, common_name, 1, False))

        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = '%s-Verify AP Join active ZD before test' % test_case_name
        test_cfgs.append(({'auto_approval': False,
                           'is_need_approval': True,
                           'zd_tag': active_zd,
                           'mac_addr_list': [active_ap_mac]}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
        common_name = '[%s]Configure FQDN in active ZD via CLI' % test_case_name
        test_params = {'zd_tag': active_zd_cli}
        test_params.update(zd_discovery_cfg)
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_AP_CLI_Get_Verify_Primary_Secondary_ZD'
        common_name = '[%s]Verify FQDN in AP CLI' % test_case_name
        test_params = {'ap_tag': ap_tag,
                       'is_verify': True,
                       'primary_zd_ip': primary_zd_ip,
                       'secondary_zd_ip': secondary_zd_ip,
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        if case_type == "failover":
            exp_zd_tag = active_zd
            
            test_name = 'CB_ZD_SR_Failover'
            common_name = '[%s]Failover ZD' % (test_case_name,)
            param_cfg = dict()
            test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        else:
            exp_zd_tag = standby_zd
            #Shutdown ZD switch port.
            active_zd_if_tag = 'if%s' % active_zd
            
            test_name = 'CB_ZD_Get_Switch_Interface' 
            common_name = '[%s]Get Active ZD Switch Interface' % (test_case_name,)
            test_cfgs.append(({'zd_tag': active_zd, 
                               'if_tag': active_zd_if_tag}, test_name, common_name, 0, False))
            
            test_name = 'CB_ZD_Disable_Enable_ZD_Switch_Port'
            common_name = '[%s]Disable switch port on active ZD' % (test_case_name,)
            test_params = {'enable':False, 'zd_tag': active_zd, 'if_tag': active_zd_if_tag}
            test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = '[%s]Verify AP Join standby ZD' % (test_case_name,)
        test_cfgs.append(({'auto_approval': False,
                           'is_need_approval': True,
                           'zd_tag': exp_zd_tag,
                           'mac_addr_list': [active_ap_mac]}, test_name, common_name, 2, False))

        test_name = 'CB_AP_CLI_Get_Verify_Primary_Secondary_ZD'
        common_name = '[%s]Verify setting in AP CLI after AP join standby ZD' % (test_case_name,)
        test_params = {'ap_tag': ap_tag,
                       'is_verify': True,
                       'primary_zd_ip': primary_zd_ip,
                       'secondary_zd_ip': secondary_zd_ip,
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = "[%s]Assign wlan group to AP %s on %s on standby ZD" % (test_case_name, active_ap, radio_mode)
        test_params = {'active_ap': active_ap,
                       'wlan_group_name': wg_name, 
                       'radio_mode': radio_mode,
                       'zd_tag': exp_zd_tag}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        common_name = '[%s]Associate the station to standby ZD wlan' % (test_case_name)
        params = {'sta_tag': sta_tag,
                  'wlan_cfg': wlan_cfg,
                  'start_browser': False,
                  'get_sta_wifi_ip': False,
                  'verify_ip_subnet': False,
                  }
        test_cfgs.append((params, test_name, common_name, 2, False))

        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '[%s]Verify ping target IPs for standby ZD wlan' % (test_case_name)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': target_ip_list,
                  'download_file': False,
                  'close_browser': False,
                  }
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        if case_type == 'shutdown':
            test_name = 'CB_ZD_Disable_Enable_ZD_Switch_Port'
            common_name = '%s-Enable switch port on active ZD' % test_case_name
            test_cfgs.append(({'enable': True, 'zd_tag': active_zd, 'if_tag': active_zd_if_tag}, test_name, common_name, 1, False))
        
            test_name = 'CB_ZD_SR_Get_Active_ZD'
            common_name = '%s-Get active and standby ZD' % test_case_name
            test_cfgs.append(({'wait_time': 100}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Disable_Enable_ZD_Switch_Port'
    common_name = 'Enable switch port on ZD1'
    test_cfgs.append(({'enable': True, 
                       'zd_tag': zd1_gui_tag,
                       'if_tag': zd1_if_tag}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Disable_Enable_ZD_Switch_Port'
    common_name = 'Enable switch port on ZD2'
    test_cfgs.append(({'enable': True, 
                       'zd_tag': zd2_gui_tag,
                       'if_tag': zd2_if_tag}, test_name, common_name, 0, True))
    
    zd_discovery_cfg = zd_discovery_cfg_list[0]
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable FQDN in active ZD after test'
    test_params = {'enabled': False, 'zd_tag': active_zd_cli}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all WLAN groups from active ZD after test'
    test_cfgs.append(({'zd_tag': active_zd,
                       'is_ap_on_zd': True,}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from active ZD after test'
    test_cfgs.append(({'zd_tag': active_zd}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD'
    test_cfgs.append(({},test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'Set ZD1 Auto Approval as True'
    test_params = {'auto_approval': True,
                   'zd_tag': zd1_gui_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Policy'
    common_name = 'Set ZD2 Auto Approval as False'
    test_params = {'auto_approval': False,
                   'zd_tag': zd2_gui_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable all AP FQDN in AP CLI after test'
    test_params = {} #{'ap_tag': ap_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Delete_All_AP'
    common_name = 'Remove all APs from ZD1 and ZD2 after test'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
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
                            'mac_addr_list': [active_ap_mac]}, test_name, common_name, 0, True))
    
    return test_cfgs

def _define_zd_discovery_keep_ap_setting():
    zd_keep_ap_setting = {'enabled': True,
                          'keep_ap_setting': True
                          }

    return zd_keep_ap_setting

def _define_zd_discovery_test_cfg(zd1_gui_tag, zd2_gui_tag, zd1_cli_tag, zd2_cli_tag, zd1_gui_ipv6_tag, zd2_gui_ipv6_tag):
    zd1_ipv4_dn = 'www.ruckuszd1.net'
    zd1_ipv6_dn = 'www.ipv6-ruckuszd1.net'    
    zd2_ipv4_dn = 'www.ruckuszd2.net'
    zd2_ipv6_dn = 'www.ipv6-ruckuszd2.net'
    
    test_cfg_list = []

    default_cfg = {'enabled': True,
                   'primary_zd_ip': '',
                   'secondary_zd_ip': '',
                   'keep_ap_setting': False,
                   'prefer_prim_zd': False,
                   }

    test_cfg_list.append({'case_name': 'Primary ZD1 IPV4 FQDN Secondary ZD2 IPV6 FQDN',
                          'primary_zd_ip': zd1_ipv4_dn,
                          'secondary_zd_ip': zd2_ipv6_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Primary ZD1 IPV6 FQDN Secondary ZD2 IPV4 FQDN',
                          'primary_zd_ip': zd1_ipv6_dn,
                          'secondary_zd_ip': zd2_ipv4_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Primary ZD2 IPV4 FQDN Secondary ZD1 IPV4 FQDN',
                          'primary_zd_ip': zd2_ipv4_dn,
                          'secondary_zd_ip': zd1_ipv4_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Primary ZD2 IPV6 FQDN Secondary ZD1 IPV6 FQDN',
                          'primary_zd_ip': zd2_ipv6_dn,
                          'secondary_zd_ip': zd1_ipv6_dn,
                          })

    zd_cfg_list = []
    for cfg in test_cfg_list:
        new_cfg = copy.deepcopy(default_cfg)
        new_cfg['primary_zd_ip'] = cfg['primary_zd_ip']
        new_cfg['secondary_zd_ip'] = cfg['secondary_zd_ip']

        zd_test_cfg = {}
        zd_test_cfg['case_name'] = cfg['case_name']
        zd_test_cfg['cfg'] = new_cfg

        zd_cfg_list.append(zd_test_cfg)

    return zd_cfg_list

def _def_wlan_cfg():
    wlan_cfg = dict(ssid = 'wlan-fqdn-%04d' % random.randrange(1, 9999),
                   auth = "open", wpa_ver = "", encryption = "none",
                   key_index = "", key_string = "",)

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

    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]        
        active_ap_mac = active_ap_cfg['mac']
        active_ap_model = active_ap_cfg['model']
        
        wlan_cfg = _def_wlan_cfg()
        wg_name = _def_wlan_group_name()
        
        zd_discovery_cfg_list = _define_zd_discovery_test_cfg(zd1_gui_tag, zd2_gui_tag, zd1_cli_tag, zd2_cli_tag, zd1_gui_ipv6_tag, zd2_gui_ipv6_tag)
        zd_discovery_cfg_keep_ap_setting = _define_zd_discovery_keep_ap_setting()
        
        tcfg = {'zd_discovery_cfg_list': zd_discovery_cfg_list,
                'zd_discovery_cfg_keep_ap_setting': zd_discovery_cfg_keep_ap_setting,
                'target_station':'%s' % target_sta,
                'active_ap':'%s' % active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,
                'radio_mode': target_sta_radio,
                'wlan_cfg': wlan_cfg,
                'wg_name': wg_name,
                'target_ip_list': [server_ip_addr],
                'zd1_gui_tag': zd1_gui_tag,
                'zd2_gui_tag': zd2_gui_tag,
                'zd1_cli_tag': zd1_cli_tag,
                'zd2_cli_tag': zd2_cli_tag,
                'enable_mgmt_vlan': enable_mgmt_vlan,
                'ap_mgmt_vlan': ap_mgmt_vlan,
                'ap_default_vlan': '1',            
                }

        test_cfgs = define_test_cfg(tcfg)

        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            if enable_mgmt_vlan:
                ts_name = "ZD CLI - Enable FQDN with SR and AP Mgmt Vlan Failover 11%s" % (target_sta_radio)
            else:
                ts_name = "ZD CLI - Enable FQDN with SR Failover 11%s" % (target_sta_radio)

        ts = testsuite.get_testsuite(ts_name, "Verify AP join specified ZD when enabled Smart Redundancy", combotest = True)

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
