'''
Configure AP device IP setting as dual stack and ipv6 only via GUI and CLI.

    Configure AP device IP setting via GUI and CLI.
    Dual stack: ipv4 - DHCP, ipv6 - auto
    IPV6 only: ipv6 - auto    
    
    expect result: All steps should result properly.
    
    How to:
        1) Set device IP setting as dual stack via GUI.
        2) Get device IP setting via GUI.         
        3) Compare the information are same between GUI set and GUI get.
        4) GEt device IP setting via CLI.
        5) Compare the information are same between GUI get and CLI get.
        6) Repeat step 1)-5) for ipv6 only.
        7) Repeat step 1)-6) for CLI.
    
Created on 2012-01-20
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    ip_cfg_list = tcfg['ip_cfg_list']
    ap_mac_addr = tcfg['ap_mac_addr']
    
    for ap_ip_cfg in ip_cfg_list:
        test_case_name = '[GUI Set Device IP Settings %s]' % ap_ip_cfg['ip_version']
    
        test_name = 'CB_ZD_Config_AP_IP_Settings'
        common_name = '%sSet AP device IP settings via GUI' % (test_case_name,)
        param_cfg = {'ip_cfg': ap_ip_cfg,
                     'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Get_AP_IP_Settings'
        common_name = '%sGet AP device IP settings via GUI' % (test_case_name,)
        param_cfg = {'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_IP_Settings_GUI_Set_Get'
        common_name = '%sVerify AP device IP settings between GUI set and get' % (test_case_name,)
        param_cfg = {'set_ip_cfg': ap_ip_cfg,
                     'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Get_AP_IP_Settings'
        common_name = '%sGet AP device IP settings via CLI' % (test_case_name,)
        param_cfg = {'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_IP_Settings_GUI_CLI_Get'
        common_name = '%sVerify AP device IP settings between GUI get and CLI get' % (test_case_name,)
        param_cfg = {'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    for ap_ip_cfg in ip_cfg_list:
        test_case_name = '[CLI Set Device IP Settings %s]' % ap_ip_cfg['ip_version']
    
        test_name = 'CB_ZD_CLI_Set_AP_IP_Settings'
        common_name = '%sSet AP device IP settings via CLI' % (test_case_name,)
        param_cfg = {'ip_cfg': ap_ip_cfg,
                     'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_CLI_Get_AP_IP_Settings'
        common_name = '%sGet AP device IP settings via CLI' % (test_case_name,)
        param_cfg = {'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_IP_Settings_CLI_Set_Get'
        common_name = '%sVerify AP device IP settings between CLI set and get' % (test_case_name,)
        param_cfg = {'set_ip_cfg': ap_ip_cfg,
                     'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Get_AP_IP_Settings'
        common_name = '%sGet AP device IP settings via GUI' % (test_case_name,)
        param_cfg = {'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_IP_Settings_GUI_CLI_Get'
        common_name = '%sVerify AP device IP settings between GUI get and CLI get' % (test_case_name,)
        param_cfg = {'ap_mac_list': ap_mac_addr}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_IP_Settings'
    common_name = 'Restore AP device IP settings as dual stack via GUI'
    param_cfg = {'ip_cfg': tcfg['restore_ip_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_ap_ip_cfg(ap_ip_version):
    ap_ip_cfg = {}
    
    ap_ip_cfg['ip_version'] = ap_ip_version
    if ap_ip_version in [const.IPV4, const.DUAL_STACK]:
        ap_ip_cfg[const.IPV4] = {'ip_mode': 'dhcp'}
    if ap_ip_version in [const.IPV6, const.DUAL_STACK]:
        ap_ip_cfg[const.IPV6] = {'ipv6_mode': 'auto'}
    
    return ap_ip_cfg

def define_test_parameters(tbcfg, ap_mac_addr):
    dual_ip_cfg = _define_ap_ip_cfg(const.DUAL_STACK)
    ipv6_ip_cfg = _define_ap_ip_cfg(const.IPV6)

    tcfg = {'restore_ip_cfg': dual_ip_cfg,
            'ip_cfg_list': [dual_ip_cfg, ipv6_ip_cfg],
            'ap_mac_addr': ap_mac_addr}    
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    
    all_ap_mac_list = tbcfg['ap_mac_list']
    if len(all_ap_mac_list) > 0:
        ap_mac_addr = all_ap_mac_list[0]
    else:
        raise Exception("No AP in testbed configuration.")
    
    ts_name = 'Configure AP Device IP Settings via GUI CLI'
    ts = testsuite.get_testsuite(ts_name, 'Verify configure AP device IP settings via GUI and CLI', combotest=True)
    tcfg = define_test_parameters(tbcfg, ap_mac_addr)
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
    