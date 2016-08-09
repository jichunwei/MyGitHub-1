'''
Configure ZD AP settings via SNMP V3.

    Update ZD AP setting via SNMP V3 successfully and the value same as CLI.    
    1. Update read-write nodes in AP, and verify the values are same between get and set, snmp get and cli get.
        
    expect result: All steps should result properly.
    
    How to:
        1) Update AP settings, and verify the values between get and set.
        2) Get AP information from SNMP.
        3) Get AP information from CLI.
        4) Verify the values from SNMP and CLI are same.
    
Created on 2011-4-14
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent V3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V3'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[AP Info SNMP and CLI]'
    
    test_name = 'CB_ZD_SNMP_Get_APs'
    common_name = '%sGet ZD APs Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Show_AP_All'
    common_name = '%sGet ZD APs Info via CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_APs_SNMPGet_CLIGet'
    common_name = '%sVerify All APs between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Configure_WLAN_Groups'
    common_name = 'Create a wlan group via CLI'
    test_cfgs.append(( {'wg_cfg_list':[tcfg['wg_cfg']]}, test_name, common_name, 0, False))
    
    test_case_name = '[Update AP Info via SNMP]'
    
    test_name = 'CB_ZD_SNMP_Verify_Update_AP'
    common_name = '%sVerify Update AP Config via ZD SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'wg_name': tcfg['wg_cfg']['wg_name']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SNMP_Get_APs'
    common_name = '%sGet ZD APs Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Show_AP_All'
    common_name = '%sGet ZD APs Info via CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_APs_SNMPGet_CLIGet'
    common_name = '%sVerify APs Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    if tcfg['is_dual_testbed']:
        #If test bed is dual/ipv6 test bed, will set ap ip settings.
        ap_ip_cfg_list = tcfg['ip_cfg_list']
        for ap_ip_cfg in ap_ip_cfg_list:
            test_case_name = '[Set AP IP Setting %s]' % ap_ip_cfg['ip_version']
            
            test_name = 'CB_ZD_SNMP_Verify_Update_AP'
            common_name = '%sVerify Update AP Config via ZD SNMP' % (test_case_name,)
            test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                                'snmp_cfg': tcfg['snmp_cfg'],
                                'set_ap_cfg': ap_ip_cfg}, test_name, common_name, 1, False))
            
            test_name = 'CB_ZD_SNMP_Get_APs'
            common_name = '%sGet ZD APs Info via SNMP' % (test_case_name,)
            test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                                'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_CLI_Show_AP_All'
            common_name = '%sGet ZD APs Info via CLI' % (test_case_name,)
            test_cfgs.append(( {}, test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_SNMP_Verify_APs_SNMPGet_CLIGet'
            common_name = '%sVerify APs Info between SNMP Get and CLI Get' % (test_case_name,)
            test_cfgs.append(( {}, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_SNMP_Verify_Update_AP'
        common_name = 'Restore AP IP setting'
        test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                            'snmp_cfg': tcfg['snmp_cfg'],
                            'set_ap_cfg': tcfg['restore_ip_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[Delete AP via SNMP]'

    test_name = 'CB_ZD_SNMP_Verify_Delete_APs'
    common_name = '%sVerify Delete APs via ZD SNMP.' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Remove_All_WLAN_Groups'
    common_name = 'Remove all WLAN groups from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs
    
def _define_ap_ip_cfg(ap_ip_version, ip_mode, ipv6_mode):
    ap_ip_cfg = {'ip_version': '', #ipv4(1), 2: ipv6(2), 3: dualstack(3)
                 'ip_addr_mode':'', #1: admin-by-zd(1) 2: admin-by-dhcp(2) 3: admin-by-ap(3)
                 'ipv6_mode': '',  #admin-by-zd(1), admin-by-autoconfig(2), admin-by-ap(3)
                 }
                 
    values_mapping = {const.IPV4: 'ipv4(1)',
                      const.IPV6: 'ipv6(2)',
                      const.DUAL_STACK: 'dualstack(3)',
                      'dhcp': 'admin-by-dhcp(2)',
                      'auto': 'admin-by-autoconfig(2)',
                      'as_is': 'admin-by-ap(3)',
                      'manual': 'admin-by-zd(1)',
                      }      
                 
    ap_ip_cfg['ip_version'] = values_mapping[ap_ip_version]
    ap_ip_cfg['ip_addr_mode'] = values_mapping[ip_mode]
    ap_ip_cfg['ipv6_mode'] = values_mapping[ipv6_mode]
    
    
    if ap_ip_version in [const.DUAL_STACK, const.IPV4] and ip_mode == 'manual':
        ap_ip_cfg['ip_addr'] = '192.168.0.34'
        ap_ip_cfg['ip_addr_mask'] = '255.255.255.0'
        ap_ip_cfg['ip_gateway'] = '192.168.0.253'
        ap_ip_cfg['ip_pri_dns'] = '192.168.0.222'
        ap_ip_cfg['ip_sec_dns'] = '172.18.35.134'
    
    if ap_ip_version in [const.DUAL_STACK, const.IPV6] and ipv6_mode == 'manual':
        ap_ip_cfg['ipv6_addr'] = '2020:db8:1:3456'
        ap_ip_cfg['ipv6_prefix_len'] = '16'
        ap_ip_cfg['ipv6_gateway'] = '2020:db8:1::251'
        ap_ip_cfg['ipv6_pri_dns'] = '2020:34:34:34:35::3'
        ap_ip_cfg['ipv6_sec_dns'] = '2000::3'
        
    return ap_ip_cfg

def define_test_parameters(tbcfg):
    set_snmp_agent_cfg = {'version': 3,
                         'enabled': True,
                         'ro_sec_name': 'ruckus-read',
                         'ro_auth_protocol': 'MD5',
                         'ro_auth_passphrase': '12345678',
                         'ro_priv_protocol': 'DES',
                         'ro_priv_passphrase': '12345678',
                         'rw_sec_name': 'ruckus-write',
                         'rw_auth_protocol': 'MD5',
                         'rw_auth_passphrase': '12345678',
                         'rw_priv_protocol': 'DES',
                         'rw_priv_passphrase': '12345678',
                         }
    
    wg_cfg = dict(wg_name = 'WGforUpdateAP', description = 'Wlan groups for update AP config')
    
    dual_ip_cfg = _define_ap_ip_cfg(const.DUAL_STACK, 'dhcp', 'auto')
    ipv6_ip_cfg = _define_ap_ip_cfg(const.IPV6, 'dhcp', 'auto')
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            'wg_cfg': wg_cfg,
            'restore_ip_cfg': dual_ip_cfg,
            'ip_cfg_list': [dual_ip_cfg, ipv6_ip_cfg],
            }
    
    return tcfg
def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    is_dual_testbed = False
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        is_dual_testbed = True
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        
        ts_name = 'ZD SNMP V3 ZD %s AP %s - AP Configuration' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V3 - AP Configuration'
        
    tcfg = define_test_parameters(tbcfg)
    tcfg.update({'is_dual_testbed': is_dual_testbed})
    
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs AP Configuration: SNMP Set, CLI Get', combotest=True)
    test_cfgs = define_test_cfg(tcfg)

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
    