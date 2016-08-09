'''
Config SNMP V2 and V3 agent via ZD CLI

    Enable SNMP v2 and v3 agent, then disable v2 and v3.
    1. Enable v2 agent, verify snmpd is started, snmp v2 command works well.
    2. Enable v3 agent, verify snmp v2 and v3 command works well.
    3. Disable v2 agent, verify snmp v2 command can't work, v3 command works well.
    4. Disable v3 agent, verify snmp v2 and v3 commands can't work, snmpd is shutdown [not in ps list].
    
    expect result: All steps should result properly.
    
    How to:
        1) Enable snmp v2 agent via ZD CLI.
        2) Verify snmp v2 agent information are same between get and set.
        3) Verify snmpd process is in ps list.        
        4) Verify snmp v2 command works well.
        5) Enable snmp v3 agent via ZD CLI.
        6) Verify snmp v3 agent information are same between get and set.
        7) Verify snmp v2 and v3 command works well.
        8) Disable snmp v2 agent.
        7) Verify v2 agent information between get and set. 
        8) Verify snmp v2 command can't work.        
        9) Verify snmp v3 command works well.
        10) Disable snmp v3 agent.
        11) Verify snmp v3 command can't work.
        23) Verify snmpd is shutdown [not in ps list.]
    
Created on 2011-4-14
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
    
    test_name = 'CB_ZD_Set_SNMP_Agent_Info'
    common_name = 'Disable SNMP Agent V2 from GUI'
    param_cfg =  {'snmp_agent_cfg': tcfg['disable_snmp_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_SNMP_Agent_V3_Info'
    common_name = 'Disable SNMP Agent V3 from GUI'
    param_cfg =  {'snmp_agent_cfg': tcfg['disable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_case_name = '[Enable SNMP Agent V2 Then V3]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V2' % test_case_name
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    verify_enable_v2_cfg = define_verify_snmpv2_test_cfg(tcfg, test_case_name, True)
    test_cfgs.extend(verify_enable_v2_cfg)
    
    test_name = 'CB_ZD_CLI_Verify_SNMPD_Process'
    common_name = '%sVerify SNMPD is in Process List' % test_case_name
    param_cfg = {'enabled': True}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_SNMP_Agent_V3_Info'
    common_name = '%sEnable SNMP Agent V3' % test_case_name
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    verify_enable_v3_cfg = define_verify_snmpv3_test_cfg(tcfg, test_case_name, True)
    test_cfgs.extend(verify_enable_v3_cfg)
    
    test_name = 'CB_ZD_SNMP_Verify_SNMP_Commands'
    common_name = '%sVerify SNMP V2 Command after Enable V3' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v2_cfg'],
                 'snmp_cfg': tcfg['snmp_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_case_name = '[Disable SNMP Agent V2 Then V3]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sDisable SNMP Agent Version 2' % test_case_name
    param_cfg = {'snmp_agent_cfg': tcfg['disable_snmp_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    verify_disable_v2_cfg = define_verify_snmpv2_test_cfg(tcfg, test_case_name, False)
    test_cfgs.extend(verify_disable_v2_cfg)
    
    test_name = 'CB_ZD_SNMP_Verify_SNMP_Commands'
    common_name = '%sVerify SNMP V3 Command after Disable V2' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['enable_snmp_agent_v3_cfg'],
                 'snmp_cfg': tcfg['snmp_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sDisable SNMP Agent Version 3' % test_case_name
    param_cfg = {'snmp_agent_cfg': tcfg['disable_snmp_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    verify_disable_v3_cfg = define_verify_snmpv3_test_cfg(tcfg, test_case_name, False)
    test_cfgs.extend(verify_disable_v3_cfg)
    
    test_name = 'CB_ZD_CLI_Verify_SNMPD_Process'
    common_name = '%sVerify SNMPD is not in Process List' % test_case_name
    param_cfg = {'enabled': False}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
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
    
    enable_snmp_v3_agent_cfg = {'version': 3,
                                'enabled': True,
                                'ro_sec_name': 'ruckus-read',
                                'ro_auth_protocol': 'MD5',
                                'ro_auth_passphrase': '12345678',
                                'ro_priv_protocol': 'None',
                                'ro_priv_passphrase': '12345678',
                                'rw_sec_name': 'ruckus-write',
                                'rw_auth_protocol': 'MD5',
                                'rw_auth_passphrase': '12345678',
                                'rw_priv_protocol': 'None',
                                'rw_priv_passphrase': '12345678',
                                }
    
    disable_snmp_v3_agent_cfg = {'version': 3,
                                 'enabled': False,
                                 'ro_sec_name': 'ruckus-read',
                                 'ro_auth_protocol': 'MD5',
                                 'ro_auth_passphrase': '12345678',
                                 'ro_priv_protocol': 'None',
                                 'ro_priv_passphrase': '12345678',
                                 'rw_sec_name': 'ruckus-write',
                                 'rw_auth_protocol': 'MD5',
                                 'rw_auth_passphrase': '12345678',
                                 'rw_priv_protocol': 'None',
                                 'rw_priv_passphrase': '12345678',
                                 }
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'enable_snmp_agent_v2_cfg': enable_snmp_agent_v2_cfg,
            'disable_snmp_agent_v2_cfg': disable_snmp_agent_v2_cfg,
            'enable_snmp_agent_v3_cfg': enable_snmp_v3_agent_cfg,
            'disable_snmp_agent_v3_cfg': disable_snmp_v3_agent_cfg,
            }
    
    return tcfg

def define_verify_snmpv2_test_cfg(tcfg, test_case_name, enabled):
    test_cfgs = []
    
    if enabled:
        snmp_agent_cfg = tcfg['enable_snmp_agent_v2_cfg']
    else:
        snmp_agent_cfg = tcfg['disable_snmp_agent_v2_cfg']
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%sGet SNMPV2 Agent information from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info_CLI_Get_Set'
    common_name = '%sVerify SNMPV2 Agent setting between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':snmp_agent_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_SNMP_Commands'
    common_name = '%sVerify SNMP V2 Command' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':snmp_agent_cfg,
                 'snmp_cfg': tcfg['snmp_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    return test_cfgs

def define_verify_snmpv3_test_cfg(tcfg, test_case_name, enabled):
    test_cfgs = []
    
    if enabled:
        snmp_agent_cfg = tcfg['enable_snmp_agent_v3_cfg']
    else:
        snmp_agent_cfg = tcfg['disable_snmp_agent_v3_cfg']
        
    snmp_cfg = tcfg['snmp_cfg']
        
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMPV3 Agent information from CLI' % (test_case_name, )
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_CLI_Get_Set'
    common_name = '%sVerify SNMPV3 Agent setting between CLI Get and CLI Set' % (test_case_name, )
    param_cfg = {'snmp_agent_cfg': snmp_agent_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_SNMP_Commands'
    common_name = '%sVerify SNMP V3 Command' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':snmp_agent_cfg,
                 'snmp_cfg': snmp_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    return test_cfgs

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD CLI - SNMP Enable and Disable V2 Then V3'
    ts = testsuite.get_testsuite(ts_name, 'Verify Enable and Disable SNMP V2 Then V3', combotest=True)
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
    