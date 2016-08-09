"""
Verify configuration limited ZD discovery settings in ZD CLI. 

    Verify set limited ZD discovery settings.
    
    Test Data:
        Keep AP setting
        Primary Lower Range Length=1
        Primary IPV6
        Primary Mid Range
        Primary Upper Range Length=64
        Primary Mid Range IPV6 Length=39
        Secondary Lower Range Empty
        Secondary IPV6
        Secondary Mid Range
        Secondary Upper Range Length=64
        Disable Limited ZD Discovery
        
    expect result: All steps should result properly.
    
    How to:
        1) Get ZD components via zd tag.
        2) Create active ap components.
        3) Set limited zd discovery in zd cli.
        4) Verify limited zd discovery setting between set and get.
        5) Get limited zd discovery in zd gui.
        6) Verify data between gui and cli get.
        7) Verify limited zd discovery setting in AP CLI if not keep ap setting.
        8) Verify error message for outside boundary values.
    
Created on 2012-04-22
@author: cherry.cheng@ruckuswireless.com
"""

import sys, copy

import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common.Ratutils import get_random_string

def define_test_cfg(cfg):
    test_cfgs = []
    
    ap_tag = "aptest"
    
    zd_discovery_cfg_list = cfg['zd_discovery_cfg_list']
    zd_discovery_cfg_keep_ap_setting = cfg['zd_discovery_cfg_keep_ap_setting']
    invalid_primary_zd_addr_list = cfg['invalid_primary_zd_addr_list']
    invalid_secondary_zd_addr_list = cfg['invalid_secondary_zd_addr_list']
    
    zd1_gui_tag = cfg['zd1_gui_tag']
    zd2_gui_tag = cfg['zd2_gui_tag']
    zd1_cli_tag = cfg['zd1_cli_tag']
    zd2_cli_tag = cfg['zd2_cli_tag']
    
    enable_mgmt_vlan = cfg['enable_mgmt_vlan']
    ap_mgmt_vlan = cfg['ap_mgmt_vlan']
    ap_default_vlan = cfg['ap_default_vlan']
    
    test_engine_ip = cfg['test_engine_ip']
    
    test_name = 'CB_ZD_Primary_Secondary_Create_ZDs'
    common_name = 'Find or Create ZD components'
    test_params = {'zd_tag_list': [zd1_gui_tag, zd2_gui_tag, zd1_cli_tag, zd2_cli_tag]}
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
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Configure FQDN as Keep AP setting for ZD2'
    test_params = {'zd_tag': zd2_cli_tag}
    test_params.update(zd_discovery_cfg_keep_ap_setting)    
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable FQDN in ZD1 before test'
    test_params = {'enabled': False, 'zd_tag': zd1_cli_tag}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
#    for ap_sym_name in all_ap_sym_list:
#        test_name = 'CB_ZD_Create_Active_AP'
#        common_name = 'Create active AP %s' % ap_sym_name
#        test_cfgs.append(({'active_ap': ap_sym_name,
#                           'ap_tag': ap_sym_name}, test_name, common_name, 0, False))
#        
#        test_name = 'CB_AP_CLI_Set_Primary_Secondary_ZD'
#        common_name = 'Disable FQDN in AP CLI for %s' % ap_sym_name
#        test_params = {'ap_tag': ap_sym_name}
#        test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Delete_All_AP'
    common_name = 'Remove all APs from ZD1 ZD2 before test'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = 'Verify AP Join ZD1 before test'
    test_cfgs.append(( {'auto_approval': True,
                        'zd_tag': zd1_gui_tag,
                        'all_ap': True}, test_name, common_name, 0, False))
    
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
    
    for zd_discovery_test_cfg in zd_discovery_cfg_list:
        test_case_name = '%s' % zd_discovery_test_cfg['case_name']
        zd_discovery_cfg = zd_discovery_test_cfg['cfg']
        
        keep_ap_setting = zd_discovery_cfg['keep_ap_setting']
        
        if not keep_ap_setting:
            test_name = 'CB_ZD_Clear_Event'
            common_name = '[%s]Clear all events in ZD' % test_case_name
            test_params = {'zd_tag': zd1_gui_tag}
            test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
        common_name = '[%s]Configure FQDN via CLI' % test_case_name
        test_params = {'zd_tag': zd1_cli_tag}
        test_params.update(zd_discovery_cfg)        
        test_cfgs.append((test_params, test_name, common_name, 1, False))
        
        if not keep_ap_setting:
            test_name = 'CB_ZD_Verify_FQDN_Change_Event'
            common_name = '[%s]Verify FQDN change event in log' % test_case_name
            test_params = {'zd_tag': zd1_gui_tag,
                           'enabled': zd_discovery_cfg['enabled'],
                           'access_ip': test_engine_ip,
                           'pri_zd_addr': zd_discovery_cfg['primary_zd_ip'],
                           'sec_zd_addr': zd_discovery_cfg['secondary_zd_ip'],
                           'timeout': 120,
                           }
            test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Get_Primary_Secondary_ZD'
        common_name = '[%s]Get FQDN via CLI' % test_case_name
        test_cfgs.append(({'zd_tag': zd1_cli_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Primary_Secondary_CLI_Set_Get'
        common_name = '[%s]Verify FQDN between CLI Set and Get' % test_case_name
        test_params = {'set_zd_discovery_cfg': zd_discovery_cfg}
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Get_Primary_Secondary_ZD'
        common_name = '[%s]Get FQDN via GUI' % test_case_name
        test_cfgs.append(({'zd_tag': zd1_gui_tag}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Primary_Secondary_GUI_CLI_Get'
        common_name = '[%s]Verify FQDN between GUI Get and CLI Get' % test_case_name
        test_cfgs.append(({}, test_name, common_name, 2, False))
        
        if not keep_ap_setting:
            test_name = 'CB_AP_CLI_Get_Verify_Primary_Secondary_ZD'
            common_name = '[%s]Verify FQDN in AP CLI' % test_case_name
            test_params = {'ap_tag': ap_tag,
                           'is_verify': True,
                           'primary_zd_ip': zd_discovery_cfg['primary_zd_ip'],
                           'secondary_zd_ip': zd_discovery_cfg['secondary_zd_ip']
                           }
            test_cfgs.append((test_params, test_name, common_name, 2, False))
            
    test_case_name = "CLI - Reboot ZD"
    zd_discovery_cfg = zd_discovery_cfg_list[2]['cfg']
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = '[%s]Configure FQDN via CLI' % test_case_name
    test_params = {'zd_tag': zd1_cli_tag}
    test_params.update(zd_discovery_cfg)        
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '[%s]Reboot ZD from CLI'% test_case_name
    test_cfgs.append(( {'timeout':10*60,
                        'zd_tag': zd1_cli_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Primary_Secondary_ZD'
    common_name = '[%s]Get FQDN via CLI' % test_case_name
    test_cfgs.append(({'zd_tag': zd1_cli_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Primary_Secondary_CLI_Set_Get'
    common_name = '[%s]Verify FQDN between CLI Set and Get' % test_case_name
    test_params = {'set_zd_discovery_cfg': zd_discovery_cfg}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
        
    test_case_name = "CLI - Outside Boundary for Primary and Secondary"
    
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD_Invalid_Values'
    common_name = '[%s]Verify error message for invalid values' % test_case_name
    test_params = {'invalid_primary_zd_addr_list': invalid_primary_zd_addr_list,
                   'invalid_secondary_zd_addr_list': invalid_secondary_zd_addr_list,
                   'zd_tag': zd1_cli_tag}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    if enable_mgmt_vlan:
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Restore AP Mgmt VLAN on ZD1 after test"
        test_params = {'cfg_type': "teardown",
                       'zd_tag': zd1_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, True))
        
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Restore AP Mgmt VLAN on ZD2 after test"
        test_params = {'cfg_type': "teardown",
                       'zd_tag': zd2_gui_tag,
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, True))
        
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = 'Verify all APs Join ZD1 after test'
        test_cfgs.append(({ 'auto_approval': True,
                            'zd_tag': zd1_gui_tag,
                            'verify_ap_component': False,
                            }, test_name, common_name, 0, True))
        
        test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
        common_name = "Config AP Mgmt VLAN as keep ap setting on ZD2 after test"
        test_params = {'mgmt_vlan': {'mode': "keep"},
                       'cfg_type': "config",
                       'zd_tag': zd2_gui_tag
                       }
        test_cfgs.append((test_params, test_name, common_name, 0, True))
        
        #Recreate all ap components based on enable mgmt vlan for ap.
        test_name = 'CB_ZD_Recreate_All_APs'
        common_name = 'Recreate all AP components after test'
        test_cfgs.append(({'zd_tag': zd1_gui_tag}, test_name, common_name, 0, True))
    else:
        test_name = 'CB_ZD_Verify_AP_Join'
        common_name = 'Verify AP Join ZD1 after test'
        test_cfgs.append(( {'auto_approval': True,
                            'zd_tag': zd1_gui_tag,
                            'all_ap': True}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable FQDN in ZD1 after test'
    test_params = {'enabled': False, 'zd_tag': zd1_cli_tag}        
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_CLI_Set_Primary_Secondary_ZD'
    common_name = 'Disable FQDN in ZD2 after test'
    test_params = {'enabled': False, 'zd_tag': zd2_cli_tag}        
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    return test_cfgs

def _define_zd_discovery_test_cfg(tbcfg):
    zd1_ipv6_addr = '2020:db8:128::2'
    zd2_ipv6_addr = '2020:db8:128::3'
    
    import re
    for key in tbcfg.keys():
        if re.search("\Azd1ipv6\Z", key, re.IGNORECASE):
            zd1_ipv6_addr = tbcfg.get(key).get('ip_addr')
        
        if re.search("\Azd2ipv6\Z", key, re.IGNORECASE):
            zd2_ipv6_addr = tbcfg.get(key).get('ip_addr')
    
    zd1_ipv4_dn = 'www.ruckuszd1.net'
    zd1_ipv6_dn = 'www.ipv6-ruckuszd1.net'    
    zd2_ipv4_dn = 'www.ruckuszd2.net'
    zd2_ipv6_dn = 'www.ipv6-ruckuszd2.net'
    
    zd1_ipv4_dn_max_len = 'www.ipv4-ruckuszd1-max-length-ruckusruckusruckusruckusruckus.net'
    zd2_ipv6_dn_max_len = 'www.ipv6-ruckuszd2-max-length-ruckusruckusruckusruckusruckus.net'
    
    test_cfg_list = []
    
    default_cfg = {'enabled': True,
                   'primary_zd_ip': '',
                   'secondary_zd_ip': '',
                   'keep_ap_setting': False,
                   'prefer_prim_zd': False,
                   }
    
    test_cfg_list.append({'case_name': 'Keep AP setting',
                          'keep_ap_setting': True
                          })
    
    test_cfg_list.append({'case_name': 'Primary Lower Range Length=1',
                          'primary_zd_ip': 'a', 
                          'secondary_zd_ip': zd1_ipv4_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Primary IPV6',
                          'primary_zd_ip': zd1_ipv6_addr, 
                          'secondary_zd_ip': zd2_ipv4_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Primary Mid Range',
                          'primary_zd_ip': zd1_ipv6_addr, 
                          'secondary_zd_ip': zd2_ipv6_addr,
                          })
    
    test_cfg_list.append({'case_name': 'Primary Upper Range Length=64',
                          'primary_zd_ip': zd1_ipv4_dn_max_len, 
                          'secondary_zd_ip': zd2_ipv4_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Primary Mid Range IPV6 Length=39',
                          'primary_zd_ip': '2020:1234:ABCD:5678:EF00:EF00:1234:67AB', 
                          'secondary_zd_ip': zd1_ipv4_dn,
                          })
    
    #Secondary\
    test_cfg_list.append({'case_name': 'Secondary Lower Range Empty',
                          'primary_zd_ip': zd1_ipv6_dn, 
                          'secondary_zd_ip': '',
                          })
    
    test_cfg_list.append({'case_name': 'Secondary IPV6',
                          'primary_zd_ip': zd1_ipv6_dn, 
                          'secondary_zd_ip': zd2_ipv6_addr,
                          })
    
    test_cfg_list.append({'case_name': 'Secondary Mid Range',
                          'primary_zd_ip': zd1_ipv6_addr, 
                          'secondary_zd_ip': zd2_ipv6_dn,
                          })
    
    test_cfg_list.append({'case_name': 'Secondary Upper Range Length=64',
                          'primary_zd_ip': zd1_ipv4_dn, 
                          'secondary_zd_ip': zd2_ipv6_dn_max_len,
                          })
    
    test_cfg_list.append({'case_name': 'Disable Limited ZD Discovery',
                          'enabled': False,
                          })
    
    zd_cfg_list = []
    for cfg in test_cfg_list:
        new_cfg = copy.deepcopy(default_cfg)
        
        zd_test_cfg = {}
        zd_test_cfg['case_name'] = cfg.pop('case_name')
        
        new_cfg.update(cfg)
        zd_test_cfg['cfg'] = new_cfg
        
        zd_cfg_list.append(zd_test_cfg)   
    
    return zd_cfg_list    

def _define_invalid_pri_sec_list():
    str_65 = get_random_string('alnum', 65, 65)
    invalid_primary_zd_addr_list = ['', str_65]
    invalid_secondary_zd_addr_list = [str_65]
    
    return invalid_primary_zd_addr_list, invalid_secondary_zd_addr_list

def _define_zd_discovery_keep_ap_setting():
    zd_keep_ap_setting = {'enabled': True,
                          'keep_ap_setting': True
                          }
    
    return zd_keep_ap_setting    

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )

    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    zd1_gui_tag = 'zd1'
    zd2_gui_tag = 'zd2'
    zd1_cli_tag = 'ZDCLI1'
    zd2_cli_tag = 'ZDCLI2'
    default_engine_ip = 'Local Host'
    
    test_engine_ip = default_engine_ip
    
    '''
    test_engine_ip = raw_input("Please input test engine IP, enter to access default [%s]:" % (default_engine_ip))
    if not test_engine_ip:
        test_engine_ip = default_engine_ip
    '''
    
    if ts_cfg["interactive_mode"]:
        active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    else:
        if kwargs["targetap"]:
            active_ap_list = sorted(ap_sym_dict.keys())
            
    ap_mgmt_vlan = '1'
    enable_mgmt_vlan = raw_input("Enable management vlan for ap (y/n):").lower() == 'y'
    if enable_mgmt_vlan:
        ap_mgmt_vlan = raw_input("Please input management vlan for ap [default is 10]:")
        if not ap_mgmt_vlan:
            ap_mgmt_vlan = '10'
    
    for active_ap in active_ap_list:
        zd_discovery_cfg_list = _define_zd_discovery_test_cfg(tbcfg)
        zd_discovery_cfg_keep_ap_setting = _define_zd_discovery_keep_ap_setting()
        invalid_primary_zd_addr_list, invalid_secondary_zd_addr_list = _define_invalid_pri_sec_list()
         
        tcfg = {'zd_discovery_cfg_list': zd_discovery_cfg_list,
                'zd_discovery_cfg_keep_ap_setting': zd_discovery_cfg_keep_ap_setting,
                'invalid_primary_zd_addr_list': invalid_primary_zd_addr_list,
                'invalid_secondary_zd_addr_list': invalid_secondary_zd_addr_list,
                'active_ap': active_ap,
                'all_ap_sym_list': [active_ap],
                'zd1_gui_tag': zd1_gui_tag,
                'zd2_gui_tag': zd2_gui_tag,
                'zd1_cli_tag': zd1_cli_tag,
                'zd2_cli_tag': zd2_cli_tag,
                'enable_mgmt_vlan': enable_mgmt_vlan,
                'ap_mgmt_vlan': ap_mgmt_vlan,
                'ap_default_vlan': '1',
                'test_engine_ip': test_engine_ip,
                }
    
        test_cfgs = define_test_cfg(tcfg)
    
        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            if enable_mgmt_vlan:
                ts_name = "ZD CLI - Configuration FQDN with AP Mgmt Vlan"
            else:
                ts_name = "ZD CLI - Configuration FQDN"
    
        ts = testsuite.get_testsuite(ts_name, "Verify configure FQDN with IPV4 IPV6 Domain Name", combotest = True)
    
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