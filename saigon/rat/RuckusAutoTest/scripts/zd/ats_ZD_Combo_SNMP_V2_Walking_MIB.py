'''
Walking the whole MIB via SNMP V2

    Walking the whole MIB can get correct information.   
    1. Walking RUCKUS-ZD-SYSTEM-MIB, get system information and compare the values with zd cli result.
    2. Walking RUCKUS-ZD-AP-MIB, get AP information and compare the values with zd cli result.
    expect result: All steps should result properly.
    
    How to:
        1) Walking MIB objects via SNMP V3 and parsing the result
        2) Get information via ZD CLI        
        4) Compare the result from SNMP and CLI are same        
    
Created on 2011-4-25
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP agent v2'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[Walking System MIB]'
    
    test_name = 'CB_ZD_SNMP_Walking_System_MIB'
    common_name = '%sWalking system mib and get system info' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_Basic_Info'
    common_name = '%sGet System Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_Basic_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_IP_Info'
    common_name = '%sGet System IP Info via ZD CLI' % (test_case_name)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_IP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System IP Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Walking ZD AP MIB]'
    
    test_name = 'CB_ZD_SNMP_Walking_ZD_AP_MIB'
    common_name = '%sWalking ZD AP mib' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Show_AP_All'
    common_name = '%sGet ZD APs Info via CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_APs_SNMPGet_CLIGet'
    common_name = '%sVerify All APs between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
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
        
        ts_name = 'ZD SNMP V2 ZD %s AP %s - Walking MIB' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V2 - Walking MIB'
    
    tcfg = define_test_parameters(tbcfg)
    ts = testsuite.get_testsuite(ts_name, 'Verify walking the mib via snmp v2', combotest=True)
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
    