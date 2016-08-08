'''
Verify SNMPV3 Trap is received after enable with specified setting.

    Enable snmp trap and set as v3 format.
    1. Trap is sent with specified settings when an AP is joined.
    expect result: All steps should result properly.
    
    How to:
        1) Enable SNMP v3 trap with specified settings. [Auth=MD5, Privacy=None]
        2) Delete an AP from ZD.        
        4) Start trap receiver and check trap information is correct.
        5) Repeat step 1)-4) for all combination of auth and privacy.
    
Created on 2011-7-05
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
    
    default_v3_trap_cfg = tcfg['default_v3_trap_cfg']
    for auth in tcfg['auth_list']:
        for privacy in tcfg['privacy_list']:
            #Enable the trap and verify AP join trap is received.
            trap_cfg = {}
            trap_cfg.update(default_v3_trap_cfg)
            trap_cfg['auth_protocol'] = auth
            trap_cfg['priv_protocol'] = privacy
            test_cfgs.extend(define_test_cfg_verify_trap(trap_cfg, True))
            #Disable the trap and verify AP join trap is not received.            
            test_cfgs.extend(define_test_cfg_verify_trap(trap_cfg, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def define_test_cfg_verify_trap(trap_cfg, enabled):
    test_cfgs = []
    test_case_name = '[V3 Trap - Auth=%s Privacy=%s]' % (trap_cfg['auth_protocol'], trap_cfg['priv_protocol'])
    
    trap_cfg_new = {}
    trap_cfg_new.update(trap_cfg)
    trap_cfg_new['enabled'] = enabled

    if enabled:
        action = 'Enable' 
    else:
        action = 'Disable'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%s%s SNMP Trap V3 from CLI' % (test_case_name, action)
    param_cfg = {'snmp_trap_cfg':trap_cfg_new}
    
    if enabled:
        test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    else:
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V3 Info from CLI when Trap is %s' % (test_case_name, action)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Trap V3 Info between CLI Set and Get when Trap is %s' % (test_case_name, action)
    param_cfg = {'snmp_trap_cfg':trap_cfg_new}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap when Trap is %s' % (test_case_name, action)
    param_cfg = {'snmp_trap_cfg':trap_cfg_new}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    return test_cfgs
    
def define_test_parameters(tbcfg, trap_server_ip):
    server_ip = raw_input('Please input test engine ip address[%s]' % trap_server_ip)
    if not server_ip:
        server_ip = trap_server_ip
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    auth_list = ['MD5', 'SHA']
    privacy_list = ['None', 'AES', 'DES']
    
    default_v3_trap_cfg = {'version': 3,
                           'enabled': True,
                           '1': {'sec_name': 'ruckus-read',
                                 'server_ip': server_ip,
                                 'auth_protocol': 'MD5',
                                 'auth_passphrase': '12345678',
                                 'priv_protocol': 'DES',
                                 'priv_passphrase': '12345678',
                                 }
                           }
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'default_v3_trap_cfg': default_v3_trap_cfg,
            'auth_list': auth_list,
            'privacy_list': privacy_list,
            }
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        trap_server_ip = '2020:db8:1::10'
        ts_name = 'ZD SNMP Trap ZD %s AP %s - Verify V3 Trap' % (zd_ip_version, ap_ip_version)
    else:
        trap_server_ip = '192.168.0.10'
        ts_name = 'ZD SNMP Trap - Verify V3 Trap'

    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP V3 Trap', combotest=True)
    tcfg = define_test_parameters(tbcfg, trap_server_ip)    
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
    