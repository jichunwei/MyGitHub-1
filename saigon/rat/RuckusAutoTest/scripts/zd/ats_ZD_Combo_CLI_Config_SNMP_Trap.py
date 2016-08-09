'''
Config SNMP Trap via ZD CLI

    Config snmp trap via ZD CLI successfully
    1. The trap information from CLI and GUI are same.
    2. Enable trap v2, the information are same between get and set, CLI get and GUI get.
    3. Enable trap v3, the information are same between get and set, CLI get and GUI get.
    2. Disable trap, the information are same between get and set, CLI get and GUI get.
    expect result: All steps should result properly.
    
    How to:
        1) Get snmp trap setting from CLI and GUI, verify they are same.
        2) Enable snmp trap v2 via ZD CLI.        
        3) Get snmp trap information from GUI and CLI.
        4) Compare the information are same between CLI set and CLI get.
        5) Compare the information are same between CLI get and GUI get.
        6) Verify ap join trap is received.
        7) Repeat do 4)-6) for enable trap v3.
        8) Disable snmp trap, repeat do 3)-6), verify trap is not received.        
    
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
    
    test_case_name = '[Current Trap Info GUI and CLI]'
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_case_name = '[Enable SNMP Trap V2]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sEnable SNMP Trap V2 from CLI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V2 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Trap V2 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V2 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap V2 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap when trap is enable' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['enable_v2_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    
    
    test_case_name = '[Enable SNMP Trap V3]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sEnable SNMP Trap V3 from CLI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Trap V3 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join trap when trap is enable' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['enable_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_case_name = '[Disable SNMP Trap]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Trap'
    common_name = '%sDisable SNMP Trap from CLI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Trap Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['disable_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    disable_trap_cfg = {}
    disable_trap_cfg.update(tcfg['enable_v2_trap_cfg'])
    disable_trap_cfg['enabled'] = False
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join v2 trap when trap is disable' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':disable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    disable_trap_cfg = {}
    disable_trap_cfg.update(tcfg['enable_v3_trap_cfg'])
    disable_trap_cfg['enabled'] = False
    
    test_name = 'CB_ZD_SNMP_Verify_AP_Join_Trap'
    common_name = '%sVerify AP Join v3 trap when trap is disable' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':disable_trap_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    return test_cfgs

def define_test_parameters(tbcfg, trap_server_ip):
    server_ip = raw_input('Please input test engine ip address[%s]' % trap_server_ip)
    if not server_ip:
        server_ip = trap_server_ip
        
    enable_v2_trap_cfg = {'version': 2,
                          'enabled': True,
                          '1': {'server_ip': server_ip},
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
    
    disable_trap_cfg = {'enabled': False}
    
    tcfg = {'enable_v2_trap_cfg': enable_v2_trap_cfg,
            'enable_v3_trap_cfg': enable_v3_trap_cfg,
            'disable_trap_cfg': disable_trap_cfg,
            }
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        trap_server_ip = '2020:db8:1::10'
        ts_name = 'ZD CLI ZD %s AP %s - SNMP V2 and V3 Trap Configuration' % (zd_ip_version, ap_ip_version)
    else:
        trap_server_ip = '192.168.0.10'
        ts_name = 'ZD CLI - SNMP Trap Configuration'
        #ts_name = 'ZD CLI - SNMP V2 and V3 Trap Configuration'

    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP Trap Configuration: CLI Set, GUI Get', combotest=True)
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
    