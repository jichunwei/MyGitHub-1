'''
Configure L3 IVP6 ACL via GUI and CLI.

    Configure L3 IPV6 ACL via GUI and CLI.
    expect result: All steps should result properly.
    
    How to:
        1) Create L3 IPV6 ACL via GUI.
        2) Get L3 IPV6 ACL via GUI.         
        3) Compare the information are same between GUI set and GUI get.
        4) Get L3 IPV6 ACL via CLI.
        5) Compare the information are same between GUI get and CLI get.
        6) Repeat step 1)-5) for CLI.
    
Created on 2012-2-03
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    l3acl_cfg_list = tcfg['l3acl_cfg_list']
    
    test_name = 'CB_ZD_Remove_All_L3_ACLs_IPV6'
    common_name = 'Remove all existing L3 IPV6 ACLs'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name = '[GUI Set L3 IPV6 ACL]'

    test_name = 'CB_ZD_Create_L3_ACLs_IPV6'
    common_name = '%sCreate L3 IPV6 ACLs via GUI and verify between get and set' % (test_case_name,)
    test_cfgs.append(({'l3_acl_cfgs': l3acl_cfg_list},
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_L3_ACLs_IPV6'
    common_name = '%sGet L3 IPV6 ACL via CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_L3_IPV6_ACL_GUI_CLI_Get'
    common_name = '%sVerify L3 IPV6 ACL between GUI get and CLI get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_L3_ACLs_IPV6'
    common_name = 'Remove all L3 IPV6 ACLs after GUI set test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name = '[CLI Set L3 IPV6 ACL]'

    test_name = 'CB_ZD_CLI_Create_L3_ACLs_IPV6'
    common_name = '%sCreate L3 IPV6 ACLs via CLI and verify between get and set' % (test_case_name,)
    param_cfg = {'l3_acl_cfgs': l3acl_cfg_list}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_L3_ACLs_IPV6'
    common_name = '%sGet L3 IPV6 ACL via GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_L3_IPV6_ACL_GUI_CLI_Get'
    common_name = '%sVerify L3 IPV6 ACL between GUI get and CLI get' % (test_case_name,)
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_L3_ACLs_IPV6'
    common_name = 'Remove all L3 IPV6 ACLs after test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_l3_ipv6_acls(server_ipv6_addr, prefix_len):
    l3_acl_cfg_list = []
    
    l3_acl_cfg_list.append({'name':'L3 ACL Allow',
                            'description': '',
                            'default_mode': 'allow-all',
                            'rules': _define_acl_rule_list(),
                            })
    
    l3_acl_cfg_list.append({'name':'L3 ACL Deny',
                            'description': '',
                            'default_mode': 'deny-all',
                            'rules': _define_acl_rule_list(),
                            })
    
    return l3_acl_cfg_list

def _define_acl_rule_list():
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
    
    #There is a four default ipv6 rules.
    order = 5
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
                'dst_addr': 'Any',
                'dst_port': 'Any',
                'application': 'Any',
                'protocol': 'Any',
                'icmp_type': 'Any'}
    
    app_pro_port_mapping = {'HTTP': {'protocol': '6', 'dst_port': '80',},
                            'HTTPS': {'protocol': '6', 'dst_port': '443',},
                            'FTP': {'protocol': '6', 'dst_port': '21',},
                            'SSH': {'protocol': '6', 'dst_port': '22',},
                            'TELNET': {'protocol': '6', 'dst_port': '23',},
                            'SMTP': {'protocol': '6', 'dst_port': '25',},
                            'DNS': {'protocol': 'Any', 'dst_port': '53',},
                            'DHCPv6': {'protocol': 'Any', 'dst_port': '547',},
                            'SNMP': {'protocol': 'Any', 'dst_port': '161',},
                            }
    
    if action:
        rule_cfg['action'] = action
    if description:
        rule_cfg['description'] = description
    if dst_addr:
        rule_cfg['dst_addr'] = dst_addr
        
    if application:
        rule_cfg['application'] = application
        if app_pro_port_mapping.has_key(application):
            rule_cfg['protocol'] = app_pro_port_mapping[application]['protocol']
            rule_cfg['dst_port'] = app_pro_port_mapping[application]['dst_port']
        else:
            raise Exception("Application value is incorrect")
    
    if protocol:
        rule_cfg['protocol'] = protocol
    if dst_port:
        rule_cfg['dst_port'] = dst_port
    if icmp_type:
        rule_cfg['icmp_type'] = icmp_type
    
    return rule_cfg

def define_test_parameters(tbcfg):
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg)
    prefix_len = '64'
    
    tcfg = {'l3acl_cfg_list': _define_l3_ipv6_acls(server_ipv6_addr, prefix_len)}
    
    return tcfg
   

def create_test_suite(**kwargs):    
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
        
    ts_name = 'Configure L3 IPV6 ACL via GUI CLI'
    ts = testsuite.get_testsuite(ts_name, 'Verify configure L3 IPV6 ACL via GUI and CLI', combotest=True)
    tcfg = define_test_parameters(tbcfg)
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
    