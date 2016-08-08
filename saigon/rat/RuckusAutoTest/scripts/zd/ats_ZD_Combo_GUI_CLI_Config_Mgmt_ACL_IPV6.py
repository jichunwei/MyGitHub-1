'''
Configure Management IVP6 ACL via GUI and CLI.

    Configure Management IPV6 ACL via GUI and CLI.
    expect result: All steps should result properly.
    
    How to:
        1) Create Management IPV6 ACL via GUI.
        2) Get Management IPV6 ACL via GUI.         
        3) Compare the information are same between GUI set and GUI get.
        4) Get Management IPV6 ACL via CLI.
        5) Compare the information are same between GUI get and CLI get.
        6) Repeat step 1)-5) for CLI.
    
Created on 2012-2-13
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    mgmt_acl_cfg_list = tcfg['mgmt_acl_cfg_list']
    
    test_name = 'CB_ZD_Remove_All_Mgmt_IPV6_ACLs'
    common_name = 'Remove all existing Mgmt IPV6 ACLs'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name = '[GUI Set Mgmt IPV6 ACL]'

    test_name = 'CB_ZD_Create_Mgmt_IPV6_ACLs'
    common_name = '%sCreate Mgmt IPV6 ACLs via GUI and verify between set and get' % (test_case_name,)
    test_cfgs.append(({'mgmt_acl_list': mgmt_acl_cfg_list},
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Mgmt_IPV6_ACLs'
    common_name = '%sGet Mgmt IPV6 ACL via CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Mgmt_IPV6_ACLs_GUI_CLI_Get'
    common_name = '%sVerify Mgmt IPV6 ACL between GUI get and CLI get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Mgmt_IPV6_ACLs'
    common_name = 'Remove all Mgmt IPV6 ACLs after GUI set test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_case_name = '[CLI Set Mgmt IPV6 ACL]'

    test_name = 'CB_ZD_CLI_Create_Mgmt_IPV6_ACLs'
    common_name = '%sCreate Mgmt IPV6 ACLs via CLI and verify between set and get' % (test_case_name,)
    param_cfg = {'mgmt_acl_list': mgmt_acl_cfg_list}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Mgmt_IPV6_ACLs'
    common_name = '%sGet Mgmt IPV6 ACL via GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Mgmt_IPV6_ACLs_GUI_CLI_Get'
    common_name = '%sVerify Mgmt IPV6 ACL between GUI get and CLI get' % (test_case_name,)
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Mgmt_IPV6_ACLs'
    common_name = 'Remove all Mgmt IPV6 ACLs after test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_mgmt_ipv6_acls(tbcfg):
    default_test_engine_ip = '2020:db8:1::10'
    test_engine_ip = raw_input('Please input test engine ip address[%s]' % default_test_engine_ip)
    if not test_engine_ip:
        test_engine_ip = default_test_engine_ip
    server_ipv6 = testsuite.get_server_ipv6(tbcfg)
    ipv6_prefix = testsuite.get_ipv6_prefix_len(tbcfg)
    
    mgmt_acl_cfg_list = []
    mgmt_acl_cfg_list.append({'name': 'allowtestengine',
                              'type': 'single',
                              'addr': test_engine_ip})
    mgmt_acl_cfg_list.append({'name': 'allowsingleip',
                              'type': 'single',
                              'addr': server_ipv6})
    mgmt_acl_cfg_list.append({'name': 'allowprefix',
                              'type': 'prefix',
                              'addr': '%s / %s' % (server_ipv6, ipv6_prefix)})
    
    return mgmt_acl_cfg_list

def define_test_parameters(tbcfg):
    tcfg = {'mgmt_acl_cfg_list': _define_mgmt_ipv6_acls(tbcfg),
            'remove_acl_name': 'allowserver',
            }    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
        
    ts_name = 'Configure Management IPV6 ACL via GUI CLI'
    ts = testsuite.get_testsuite(ts_name, 'Verify Management IPV6 ACL via GUI and CLI', combotest=True)
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
    