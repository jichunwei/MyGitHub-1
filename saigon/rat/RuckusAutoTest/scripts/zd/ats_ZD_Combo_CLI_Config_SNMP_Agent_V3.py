'''
Configure SNMP V3 agent via ZD CLI

    SNMP V3 agent is enabled/disabled via ZD CLI successfully.
    1. The agent information from CLI and GUI are same.
    2. Enable v3 agent, the information are same between get and set, CLI get and GUI get; verify snmpd is started, snmp command works well.
    2. Disable v3 agent, the information are same between get and set, CLI get and GUI get; verify snmpd is shutdown, snmp command can't work.
    expect result: All steps should result properly.
    
    How to:
        1) Get snmp v3 agent setting from CLI and GUI, verify they are same.
        2) Enable snmp v3 agent via ZD CLI.        
        4) Get snmp v3 agent information from GUI and CLI.
        5) Compare the information are same between CLI set and CLI get.
        6) Compare the information are same between CLI get and GUI get.
        7) Verify snmpd process is started [in ps list]. 
        8) Verify snmp v3 command works well.
        9) Disable snmp v3 agent via ZD CLI.        
        10) repeat do 4)-6).
        11) Verify snmpd process is shutdown [not in ps list].
        12) Verify snmp v3 command can't work.
    
Created on 2011-4-25
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_SNMP_Agent_V3_Info'
    common_name = 'Enable SNMP Agent V3 via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_case_name = '[Current Agent Info GUI and CLI]'
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMP Agent V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_GUIGet_CLIGet'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_case_name = '[Enable SNMP Agent V3]'
    
    test_name = 'CB_ZD_Set_SNMP_Agent_V3_Info'
    common_name = '%sDisable SNMP Agent V3 from GUI' % (test_case_name,)
    param_cfg =  {'snmp_agent_cfg': tcfg['disable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V3 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMP Agent V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V3 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_GUIGet_CLIGet'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPD_Process'
    common_name = '%sVerify SNMPD in Process List' % (test_case_name,)
    param_cfg = {'enabled': True}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_SNMP_Commands'
    common_name = '%sVerify SNMP V3 Command Works Well' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v3_cfg'],
                 'snmp_cfg': tcfg['snmp_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_case_name = '[Disable SNMP Agent V3]'
    
    test_name = 'CB_ZD_Set_SNMP_Agent_V3_Info'
    common_name = '%sEnable SNMP Agent V3 from GUI' % (test_case_name,)
    param_cfg =  {'snmp_agent_cfg': tcfg['enable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sDisable SNMP Agent V3 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['disable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMP Agent V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V3 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['disable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_GUIGet_CLIGet'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPD_Process'
    common_name = '%sVerify SNMPD not in Process List' % (test_case_name,)
    param_cfg = {'enabled': False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_SNMP_Verify_SNMP_Commands'
    common_name = '%sVerify SNMP V3 Command Can not Work' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['disable_snmp_agent_v3_cfg'],
                 'snmp_cfg': tcfg['snmp_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    return test_cfgs

def define_test_parameters(tbcfg):
    enable_snmp_agent_v2_cfg = {'version': 2,
                             'enabled': True,
                             'ro_community': 'public',
                             'rw_community': 'private',
                             'contact': 'support@ruckuswireless.com',
                             'location': 'shenzhen',}
    
    disable_snmp_agent_v2_cfg = {'version': 2,
                              'enabled': False,
                              'ro_community': 'public',
                              'rw_community': 'private',
                              'contact': 'support@ruckuswireless.com',
                              'location': 'shenzhen',
                              }
    
    enable_snmp_agent_v3_cfg = {'version': 3,
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
    
    disable_snmp_agent_v3_cfg = {'version': 3,
                                 'enabled': False,
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
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'enable_snmp_agent_v2_cfg': enable_snmp_agent_v2_cfg,
            'disable_snmp_agent_v2_cfg': disable_snmp_agent_v2_cfg,
            'enable_snmp_agent_v3_cfg': enable_snmp_agent_v3_cfg,
            'disable_snmp_agent_v3_cfg': disable_snmp_agent_v3_cfg,
            }
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD CLI - SNMP Agent V3 Configuration'
    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP Agent V3 Configuration: CLI Set, GUI Get', combotest=True)
    tcfg = define_test_parameters(tbcfg)    
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
    