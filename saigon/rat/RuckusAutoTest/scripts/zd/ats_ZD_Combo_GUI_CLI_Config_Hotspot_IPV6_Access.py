'''
Configure ZD device IP setting as dual stack and ipv6 only via GUI and CLI.

    Configure ZD device IP setting via GUI and CLI.
    Dual stack: ipv4 - DHCP, ipv6 - manual
    IPV6 only: ipv6 - manual    
    
    expect result: All steps should result properly.
    
    How to:
        1) Set device IP setting as dual stack via GUI.
        2) Get device IP setting via GUI.         
        3) Compare the information are same between GUI set and GUI get.
        4) GEt device IP setting via CLI.
        5) Compare the information are same between GUI get and CLI get.
        6) Repeat step 1)-5) for ipv6 only.
        7) Repeat step 1)-6) for CLI.
    
Created on 2012-1-15
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    gui_hotspot_cfg = tcfg['gui_hotspot_cfg']
    cli_hotspot_cfg = tcfg['cli_hotspot_cfg']
    
    hotspot_name = gui_hotspot_cfg['name']
    gui_ipv6_access_list = gui_hotspot_cfg['restricted_ipv6_list']
    cli_ipv6_access_list = cli_hotspot_cfg.pop('restricted_ipv6_list')
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name = '[GUI Set Hotspot with Restricted IPV6 Access]'
    
    test_name = 'CB_ZD_Create_Hotspot_Profiles'
    common_name = '%sCreate a hotspot with restricted ipv6 access via ZD GUI' % test_case_name
    param_cfg = {'hotspot_profiles_list': [gui_hotspot_cfg]}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Hotspot_Profiles'
    common_name = '%sGet hotspot profile via ZD GUI' % test_case_name
    param_cfg = {'hotspot_name_list': [hotspot_name]}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Hotspot_Restrict_IPV6_GUI_Set_Get'
    common_name = '%sVerify hotspot restricted ipv6 access between GUI set and get' % test_case_name
    param_cfg = {'ipv6_access_list': gui_ipv6_access_list,
                 'hotspot_name': hotspot_name}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Hotspot_Profiles'
    common_name = '%sGet hotspot profile via ZD CLI' % test_case_name
    param_cfg = {'hotspot_name_list': [hotspot_name]}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Hotspot_Restrict_IPV6_GUI_CLI_Get'
    common_name = '%sVerify hotspot restricted ipv6 access list between GUI get and CLI get' % test_case_name
    param_cfg = {'hotspot_name': hotspot_name}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all hotspot profiles from ZD after GUI test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name = '[CLI Set Hotspot with Restricted IPV6 Access]'
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    common_name = '%sCreate a hotspot via ZD CLI' % (test_case_name,)
    param_cfg = {'hotspot_conf': cli_hotspot_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot_Restrict_Access_IPV6'
    common_name = '%sConfigure Restricted IPV6 Access via CLI' % (test_case_name,)
    param_cfg = {'hotspot_restrict_access_list': cli_ipv6_access_list,
                 'hotspot_name': hotspot_name}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Hotspot_Profiles'
    common_name = '%sGet hotspot profile via ZD GUI' % test_case_name
    param_cfg = {'hotspot_name_list': [hotspot_name]}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Hotspot_Restrict_IPV6_GUI_CLI_Get'
    common_name = '%sVerify hotspot profile between GUI get and CLI get' % test_case_name
    param_cfg = {'hotspot_name': hotspot_name}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Hotspot_Profiles'
    common_name = 'Remove all hotspot profiles from ZD after test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_restricted_access_list():
    '''
    Define restricted ipv6 list.
    '''
    ACTION_DENY = 'Deny'
    ACTION_ALLOW = 'Allow'

    restricted_access_list = []
    action = ACTION_DENY
    restricted_access_list.append(_define_restricted_rule_cfg(description ='denytest1'))
    restricted_access_list.append(_define_restricted_rule_cfg('2020:db8:10::251/64', action = action, description ='denytest2'))
    restricted_access_list.append(_define_restricted_rule_cfg('2020::3/3', '8034', action = action, description ='denytest3'))
    restricted_access_list.append(_define_restricted_rule_cfg('2020::3/64', '80-133', action = action, description ='denytest4'))
    action = ACTION_ALLOW
    restricted_access_list.append(_define_restricted_rule_cfg('2020:1:2:3:4:5:6:7/127', action = action, description ='allowtest1'))
    restricted_access_list.append(_define_restricted_rule_cfg(application='HTTP', action = action, description ='allowtest2'))
    restricted_access_list.append(_define_restricted_rule_cfg(application='DHCPv6', action = action, description ='allowtest3'))
    restricted_access_list.append(_define_restricted_rule_cfg(protocol='34', action = action, description ='allowtest4'))
    restricted_access_list.append(_define_restricted_rule_cfg(protocol='58', icmp_type='34', action = action, description ='allowtest5'))
    
    order = 1
    for ipv6_access in restricted_access_list:
        ipv6_access['order'] = str(order)
        order += 1
    
    return restricted_access_list

def _define_restricted_rule_cfg(dst_addr = '', dst_port = '', protocol = '', icmp_type = '', action = '', description = '', application = ''):
    '''
    Define restricted access rule cnofiguration.
    '''
    rule_cfg = {'order': '',
                'description': '',
                'action': 'Deny',
                'destination_addr': 'Any',
                'destination_port': 'Any',
                'application': 'Any',
                'protocol': 'Any',
                'icmp_type': 'Any'}
    
    app_pro_port_mapping = {'HTTP': {'protocol': '6', 'destination_port': '80',},
                            'HTTPS': {'protocol': '6', 'destination_port': '443',},
                            'FTP': {'protocol': '6', 'destination_port': '21',},
                            'SSH': {'protocol': '6', 'destination_port': '22',},
                            'TELNET': {'protocol': '6', 'destination_port': '23',},
                            'SMTP': {'protocol': '6', 'destination_port': '25',},
                            'DNS': {'protocol': 'Any', 'destination_port': '53',},
                            'DHCPv6': {'protocol': 'Any', 'destination_port': '547',},
                            'SNMP': {'protocol': 'Any', 'destination_port': '161',},
                            }
    
    if action:
        rule_cfg['action'] = action
    if description:
        rule_cfg['description'] = description
    if dst_addr:
        rule_cfg['destination_addr'] = dst_addr
        
    if application:
        rule_cfg['application'] = application
        if app_pro_port_mapping.has_key(application):
            rule_cfg['protocol'] = app_pro_port_mapping[application]['protocol']
            rule_cfg['destination_port'] = app_pro_port_mapping[application]['destination_port']
        else:
            raise Exception("Application value is incorrect")
    
    if protocol:
        rule_cfg['protocol'] = protocol
    if dst_port:
        rule_cfg['destination_port'] = dst_port
    if icmp_type:
        rule_cfg['icmp_type'] = icmp_type
    
    return rule_cfg

def _define_test_parameters():
    gui_hotspot_cfg = {'login_page': 'http://192.168.0.250/login.html',
                       'name': 'wispr_gui_cli_test',
                       'restricted_ipv6_list': _define_restricted_access_list()
                       }
    
    cli_hotspot_cfg = _convert_test_for_cli(gui_hotspot_cfg)
    
    test_cfg = {'gui_hotspot_cfg': gui_hotspot_cfg,
                'cli_hotspot_cfg': cli_hotspot_cfg,
                }

    return test_cfg
    
def _convert_test_for_cli(hotspot_cfg):
    '''
    Convert test data for cli.
    '''
    keys_mapping = {'action': 'type',
                    'login_page': 'login_page_url'}
    
    new_hotspot_cfg = _convert_dict_with_new_keys(hotspot_cfg, keys_mapping)
    ipv6_access_list = new_hotspot_cfg['restricted_ipv6_list']
    
    new_ipv6_access_list = []
    for ipv6_access in ipv6_access_list:
        new_ipv6_access_list.append(_convert_dict_with_new_keys(ipv6_access, keys_mapping))
        
    new_hotspot_cfg['restricted_ipv6_list'] = new_ipv6_access_list
    
    return new_hotspot_cfg
                
        
def _convert_dict_with_new_keys(org_dict, keys_mapping):
    new_dict = {}
    for key,value in org_dict.items():
        if keys_mapping.has_key(key):
            new_key = keys_mapping[key]
            new_dict[new_key] = value
        else:
            new_dict[key] = value
            
    return new_dict    
               
def create_test_suite(**kwargs):    
    #tb = testsuite.get_test_bed(**kwargs)
    #tbcfg = testsuite.get_testbed_config(tb)
        
    ts_name = 'Configure Hotspot with Restricted IPV6 Access via ZD GUI CLI'
    ts = testsuite.get_testsuite(ts_name, 'Verify configure hotspot restricted ipv6 access via GUI and CLI', combotest=True)
    
    tcfg = _define_test_parameters()
    
    test_cfgs = define_test_cfg(tcfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.add_test_case(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    