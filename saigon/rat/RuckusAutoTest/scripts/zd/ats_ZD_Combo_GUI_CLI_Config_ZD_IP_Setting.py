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
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    ip_cfg_list = tcfg['ip_cfg_list']
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V2'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, 
                      test_name, common_name, 0, False))
    
    for zd_ip_cfg in ip_cfg_list:
        test_case_name = '[GUI Set Device IP Settings %s]' % zd_ip_cfg['ip_version']
    
        test_name = 'CB_ZD_Set_Device_IP_Settings'
        common_name = '%sSet ZD device IP settings via GUI and verify set and get' % (test_case_name,)
        param_cfg = {'ip_cfg': zd_ip_cfg}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_CLI_Get_Device_IP_Settings'
        common_name = '%sGet ZD device IP settings via CLI' % (test_case_name,)
        param_cfg = dict()
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Device_IP_Settings_GUI_CLI_Get'
        common_name = '%sVerify ZD device IP settings between GUI get and CLI get' % (test_case_name,)
        param_cfg = dict()
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    for zd_ip_cfg in ip_cfg_list:
        test_case_name = '[CLI Set Device IP Settings %s]' % zd_ip_cfg['ip_version']
    
        test_name = 'CB_ZD_CLI_Set_Device_IP_Settings'
        common_name = '%sSet ZD device IP settings via CLI and verify set and get' % (test_case_name,)
        param_cfg = {'ip_cfg': zd_ip_cfg}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Get_Device_IP_Settings'
        common_name = '%sGet ZD device IP settings via GUI' % (test_case_name,)
        param_cfg = dict()
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Device_IP_Settings_GUI_CLI_Get'
        common_name = '%sVerify ZD device IP settings between GUI get and CLI get' % (test_case_name,)
        param_cfg = {}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    for zd_ip_cfg in ip_cfg_list:
        test_case_name = '[CLI Set SNMP Get  %s]' % zd_ip_cfg['ip_version']
        
        test_name = 'CB_ZD_CLI_Set_Device_IP_Settings'
        common_name = '%sSet ZD device IP settings via CLI and verify set and get' % (test_case_name,)
        param_cfg = {'ip_cfg': zd_ip_cfg}
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_SNMP_Get_Sys_IP_Info'
        common_name = '%sGet System IP Info via SNMP' % (test_case_name,)
        test_cfgs.append(({'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                          test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_CLI_Get_Sys_IP_Info'
        common_name = '%sGet System IP Info via ZD CLI' % (test_case_name,)
        test_cfgs.append(( {}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_SNMP_Verify_Sys_IP_Info_SNMPGet_CLIGet'
        common_name = '%sVerify System IP Info between SNMP Get and CLI Get' % (test_case_name,)
        test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = 'Restore ZD device IP settings as dual stack via GUI'
    param_cfg = {'ip_cfg': tcfg['restore_ip_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_zd_ip_cfg(zd_ip_version, zd_ipv4_addr, server_ip_addr, netmask, switch_ip_addr, zd_ipv6_addr, server_ipv6_addr, prefix_len):
    zd_ip_cfg = {}
    
    zd_ip_cfg['ip_version'] = zd_ip_version
    if zd_ip_version in [const.IPV4, const.DUAL_STACK]:
        zd_ip_cfg[const.IPV4] = {'ip_alloc': 'dhcp', #dhcp, manual, as-is.
                                 #'ip_addr': zd_ipv4_addr,
                                 #'netmask': netmask,
                                 #'gateway': switch_ip_addr,
                                 #'pri_dns': server_ip_addr,
                                 #'sec_dns': '',
                                 }
    if zd_ip_version in [const.IPV6, const.DUAL_STACK]:
        zd_ip_cfg[const.IPV6] = {'ipv6_alloc': 'manual', #auto, dhcp, as-is.
                                 'ipv6_addr': zd_ipv6_addr,
                                 'ipv6_prefix_len': prefix_len,
                                 'ipv6_gateway': server_ipv6_addr,
                                 'ipv6_pri_dns': server_ipv6_addr,
                                 'ipv6_sec_dns': '2020:db8:1::252',
                                 }
        
    #zd_ip_cfg['vlan'] = ''
    
    return zd_ip_cfg

def define_test_parameters(tbcfg):
    zd_ipv4_addr = tbcfg['ZD']['ipv4_addr']
    switch_ip_addr = tbcfg['L3Switch']['ip_addr']
    server_ip_addr = testsuite.get_server_ip(tbcfg)
    netmask = '255.255.255.0'
    
    zd_ipv6_addr = tbcfg['ZD']['ip_addr']   
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg)
    prefix_len = '64'
    
    dual_ip_cfg = _define_zd_ip_cfg(const.DUAL_STACK, zd_ipv4_addr, server_ip_addr, netmask, switch_ip_addr, zd_ipv6_addr, server_ipv6_addr, prefix_len)
    ipv6_ip_cfg = _define_zd_ip_cfg(const.IPV6, zd_ipv4_addr, server_ip_addr, netmask, switch_ip_addr, zd_ipv6_addr, server_ipv6_addr, prefix_len)
    
    set_snmp_agent_cfg = {'version': 2,
                          'enabled': True,
                          'ro_community': 'public',
                          'rw_community': 'private',
                          'contact': 'support@ruckuswireless.com',
                          'location': 'shenzhen',
                         }
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    tcfg = {'restore_ip_cfg': dual_ip_cfg,
            'ip_cfg_list': [dual_ip_cfg, ipv6_ip_cfg],
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            'snmp_cfg': snmp_cfg,}
    
    return tcfg
   

def create_test_suite(**kwargs):    
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
        
    ts_name = 'Configure Device IP Settings via GUI CLI'
    ts = testsuite.get_testsuite(ts_name, 'Verify configure ZD device IP settings via GUI and CLI', combotest=True)
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
    