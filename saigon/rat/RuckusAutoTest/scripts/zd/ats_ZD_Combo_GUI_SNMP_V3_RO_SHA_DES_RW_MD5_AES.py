'''
Configure SNMP V3 agent via ZD GUI [RO Auth=SHA Priv=DES RW Auth=MD5 Priv=AES]
  
    Set SNMP V3 agent with specified Auth and Priv, snmp works well.    
    1. Enable snmp v3 agent with the setting, snmp command works well.
    expect result: All steps should result properly.
    
    How to:
        1) Enable snmp v3 agent with the setting via ZD GUI.
        2) Get snmp v3 agent via ZD GUI.        
        4) Verify snmp v3 agent setting between GUI get and set.
        5) Get system information via snmp v3.
        6) Get system information via ZD CLI.
        7) Verify system information between SNMP and CLI. 
        8) Verify Ro and Rw users: get system name via ro user, set system name via rw user.
        
Created on 2011-4-25
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common.Ratutils import get_random_string

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent Version 2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, 
                      test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent Version 3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, 
                      test_name, common_name, 0, False))
    
    test_case_name = '[RO Auth=SHA Priv=DES RW Auth=MD5 Priv=AES]'
    
    test_name = 'CB_ZD_Set_SNMP_Agent_V3_Info'
    common_name = '%sEnable SNMP Agent Version 3' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['snmp_agent_cfg']}, 
                        test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMPV3_Info_Get_Set'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and GUI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_SNMP_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via SNMP' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_Basic_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System Info between SNMP Get and CLI Get' % (test_case_name)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_RO_RW_Agent_Setting'
    common_name = '%sVerify Set System Name via ZD SNMP' % (test_case_name)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Restore SNMP Agent Version 3 with Default Setting'
    test_cfgs.append(({'snmp_agent_cfg': tcfg['default_snmp_agent_cfg']}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def define_test_parameters(tbcfg):
    type = 'alnum'
    ro_auth_key = get_random_string(type, 9, 30)
    ro_priv_key = get_random_string(type, 9, 30)
    rw_auth_key = get_random_string(type, 9, 30)
    rw_priv_key = get_random_string(type, 9, 30) 
    
    default_key = '12345678'
    
    default_snmp_agent_cfg = {'version': 3,
                              'enabled': True,
                              'ro_sec_name': 'ruckus-read',
                              'ro_auth_protocol': 'MD5',
                              'ro_auth_passphrase': default_key,
                              'ro_priv_protocol': 'AES',
                              'ro_priv_passphrase': default_key,
                              'rw_sec_name': 'ruckus-write',
                              'rw_auth_protocol': 'MD5',
                              'rw_auth_passphrase': default_key,
                              'rw_priv_protocol': 'AES',
                              'rw_priv_passphrase': default_key,
                              } 
    
    snmp_agent_cfg = {'version': 3,
                      'enabled': True,
                      'ro_sec_name': 'ruckus-read',
                      'ro_auth_protocol': 'SHA',
                      'ro_auth_passphrase': ro_auth_key,
                      'ro_priv_protocol': 'DES',
                      'ro_priv_passphrase': ro_priv_key,
                      'rw_sec_name': 'ruckus-write',
                      'rw_auth_protocol': 'MD5',
                      'rw_auth_passphrase': rw_auth_key,
                      'rw_priv_protocol': 'AES',
                      'rw_priv_passphrase': rw_priv_key,
                      }
        
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'version': 3,
                'timeout': 20,
                'retries': 3,}
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'snmp_agent_cfg': snmp_agent_cfg,
            'default_snmp_agent_cfg': default_snmp_agent_cfg,
            }
    
    return tcfg
    
def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    tcfg = define_test_parameters(tbcfg)
    
    
    ts_name = 'ZD GUI - SNMP V3 Validation - RO (SHA,DES) RW (MD5,AES)'
    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP V3 RO (auth=SHA,priv=DES) RW (auth=MD5,priv=AES)', combotest=True)
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
    