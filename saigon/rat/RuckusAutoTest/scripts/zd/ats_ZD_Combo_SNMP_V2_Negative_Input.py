'''
Negative input testing: error message should be displayed when input invalid values. [The string more than max length]

    Verify error is displayed when set the node as invalid values.
    1. Verify read-write nodes in system mib.
    2. Verify read-write nodes in aaa mib.
    3. Verify read-write nodes in wlan config mib.
    4. Verify read-write nodes in ap mib.
    
    expect result: All steps should result properly.
    
    How to:
        1) Create aaa server, wlan.
        2) Set read-write nodes as invalid values [the string more than max length].        
        4) Verify error message is displayed and correct.        
    
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
    common_name = 'Disable SNMP agent v2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP agent v3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP agent v2'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[System Info Negative Input]'
    
    test_name = 'CB_ZD_SNMP_Negative_Input_Sys_Info'
    common_name = '%sVerify Negative Input for System Info' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_case_name = '[AP Info Negative Input]'
    
    test_name = 'CB_ZD_SNMP_Negative_Input_AP'
    common_name = '%sVerify Negative Input for AP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
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
        ts_name = 'ZD SNMP V2 ZD %s AP %s - Negative Testing' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V2 - Negative Testing'
    
    tcfg = define_test_parameters(tbcfg)
    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP Negative Input', combotest=True)
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
    