'''
Config system information via SNMP V2.

    Can set system nodes via snmp v2 successfully and the values are same with cli get.
    1. Set system nodes values, and compare snmp get with cli get. 
    
    expect result: All steps should result properly.
    
    How to:
        1) Update system nodes values with test data. 
        2) Get system nodes value via SNMP.        
        4) Get system information via CLI.
        5) Compare the values from SNMP and CLI are same.
        6) Repeat step 1)-5) for system IP and SNMP information.
    
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
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent Version 2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP Agent Version 3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent Version 2'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[System Basic Info SNMP and CLI Get]'
    
    test_name = 'CB_ZD_SNMP_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via SNMP' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_SNMP_Verify_Sys_Basic_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Update System Basic Info]'
    
    test_name = 'CB_ZD_SNMP_Config_Sys_Basic_Info'
    common_name = '%sUpdate System Info on ZD via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                       test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via SNMP' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_Basic_Info_SNMP_Get_Set'
    common_name = '%sVerify System Info between SNMP Get and Set' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_Basic_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg'], 'recovery': True}, 
	                   test_name, common_name, 2, False))
    
    test_case_name = '[System IP Info SNMP and CLI Get]'
    
    test_name = 'CB_ZD_SNMP_Get_Sys_IP_Info'
    common_name = '%sGet System IP Info via SNMP' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_IP_Info'
    common_name = '%sGet System IP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_IP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System IP Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[System SNMP Info SNMP and CLI Get]'
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via SNMP' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Update System SNMP Info]'
    
    test_name = 'CB_ZD_SNMP_Verify_Update_Sys_SNMP_Info'
    common_name = '%sVerify Update System SNMP Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                       test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sRestore SNMP Agent V2 Config' % (test_case_name,)
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Disable_SNMP_Agent'
    common_name = '%sVerify Disable SNMP Agent V2 via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 'snmp_cfg': tcfg['snmp_cfg']}, 
                       test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def define_test_parameters(tbcfg):
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
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            }
    
    return tcfg

def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        ts_name = 'ZD SNMP V2 ZD %s AP %s - System Info Configuration' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V2 - System Info Configuration'
        
    tcfg = define_test_parameters(tbcfg)    
    ts = testsuite.get_testsuite(ts_name, 'Verify System Information Configuration: SNMP Set, CLI Get', combotest=True)
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
    