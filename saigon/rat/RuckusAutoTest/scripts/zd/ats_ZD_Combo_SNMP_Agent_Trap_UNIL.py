'''
Verify SNMP Agent V2 and V3 works well with V2 and V3 Trap

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
    
    test_cfgs.extend(define_test_cfg_sub(tcfg, '2'))
    test_cfgs.extend(define_test_cfg_sub(tcfg, '3'))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def define_test_cfg_sub(tcfg, trap_version):
    test_cfgs = []
    
    if str(trap_version) == '2':
        enable_trap_cfg = tcfg['enable_v2_trap_cfg']
        disable_trap_cfg = tcfg['disable_v2_trap_cfg']        
    elif str(trap_version) == '3':
        enable_trap_cfg = tcfg['enable_v3_trap_cfg']
        disable_trap_cfg = tcfg['disable_v3_trap_cfg']
    
    test_case_name = '[SNMP Agent V2 V3 and V%s Trap]' % (trap_version)    
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent Version 2' % test_case_name
    param_cfg = {'snmp_agent_cfg': tcfg['enable_snmp_v2_agent_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent Version 3' % test_case_name
    param_cfg = {'snmp_agent_cfg': tcfg['enable_snmp_v3_agent_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sEnable SNMP Trap V%s from CLI' % (test_case_name, trap_version)
    param_cfg = {'snmp_trap_cfg': enable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V%s Info from CLI when Trap is Enable' % (test_case_name, trap_version)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Trap V%s Info between CLI Get and Set when Trap is Enable' % (test_case_name, trap_version)
    param_cfg = {'snmp_trap_cfg':enable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap after enable trap' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg': enable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sDisable SNMP Agent Version 2' % test_case_name
    param_cfg = {'snmp_agent_cfg': tcfg['disable_snmp_v2_agent_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap after disable v2 agent' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg': enable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sDisable SNMP Agent Version 3' % test_case_name
    param_cfg = {'snmp_agent_cfg': tcfg['disable_snmp_v3_agent_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap after disable v3 agent' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':enable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sDisable SNMP Trap from CLI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg': disable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V%s Info from CLI when Trap is Disable' % (test_case_name, trap_version)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Trap V%s Info between CLI Get and Set when Trap is Disable' % (test_case_name, trap_version)
    param_cfg = {'snmp_trap_cfg': disable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap after disable trap' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg': disable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    return test_cfgs
    
def define_test_parameters(tbcfg, trap_server_ip):
    server_ip = raw_input('Please input test engine ip address[%s]' % trap_server_ip)
    if not server_ip:
        server_ip = trap_server_ip

    enable_snmp_v2_agent_cfg = {'version': 2,
                                'enabled': True,
                                'ro_community': 'public',
                                'rw_community': 'private',
                                'contact': 'support@ruckuswireless.com',
                                'location': 'shenzhen',
                                }
    
    disable_snmp_v2_agent_cfg = {'version': 2,
                                 'enabled': False
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
                                 }
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    enable_v2_trap_cfg = {'version': 2,
                          'enabled': True,
                          #chen.tao 2014-01-16 to fix ZF-6551
                          '1':{'server_ip': server_ip},
                          #chen.tao 2014-01-16 to fix ZF-6551
                          }
    
    enable_v3_trap_cfg = {'version': 3,
                          'enabled': True,
                          '1': {'sec_name': 'ruckus-read',
                              'server_ip': server_ip,
                              'auth_protocol': 'MD5',
                              'auth_passphrase': '12345678',
                              'priv_protocol': 'DES',
                              'priv_passphrase': '12345678',
                              }
                          }
    
    disable_v2_trap_cfg = {}
    disable_v2_trap_cfg.update(enable_v2_trap_cfg)
    disable_v2_trap_cfg['enabled'] = False
    
    disable_v3_trap_cfg = {}
    disable_v3_trap_cfg.update(enable_v3_trap_cfg)
    disable_v3_trap_cfg['enabled'] = False
    
        
    tcfg = {'enable_snmp_v2_agent_cfg': enable_snmp_v2_agent_cfg,
            'disable_snmp_v2_agent_cfg': disable_snmp_v2_agent_cfg,
            'enable_snmp_v3_agent_cfg': enable_snmp_v3_agent_cfg,
            'disable_snmp_v3_agent_cfg': disable_snmp_v3_agent_cfg,
            'snmp_cfg': snmp_cfg,
            'enable_v2_trap_cfg': enable_v2_trap_cfg,
            'enable_v3_trap_cfg': enable_v3_trap_cfg,
            'disable_v2_trap_cfg': disable_v2_trap_cfg,
            'disable_v3_trap_cfg': disable_v3_trap_cfg,
            }
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        trap_server_ip = '2020:db8:1::10'
        ts_name = 'ZD SNMP Trap ZD %s AP %s - Verify V2 and V3 Trap with V2 and V3 Agent' % (zd_ip_version, ap_ip_version)
    else:
        trap_server_ip = '192.168.0.10'
        ts_name = 'ZD SNMP Trap - Verify V2 and V3 Trap with V2 and V3 Agent'

    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP V2 and V3 Trap works well with V2 and V3 agent', combotest=True)
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
    