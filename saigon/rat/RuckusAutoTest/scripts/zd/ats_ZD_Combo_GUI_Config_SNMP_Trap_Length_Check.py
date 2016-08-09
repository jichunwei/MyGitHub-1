'''
Set SNMP Trap settings via ZD GUI

    Set SNMP Trap settings with valid values, and error is displayed for invalid values.    
    SNMP Trap V3:
    1. Set snmp v3 trap setting with valid value, the setting is correct.
    1. Set snmp v3 trap setting with invalid value, error message is displayed.      
    
    expect result: All steps should result properly.
    
    How to:
        1) Set snmp v3 trap setting with mid range values via GUI.
        2) Get snmp v3 trap setting via GUI.         
        4) Verify the values between GUI get and set.
        5) Get snmp v3 trap setting via CLI.
        6) Verify the value between CLI get and GUI get.
        7) Repeat step 1)-6) with lower range values.
        8) Repeat step 1)-6) with upper range values.
        9) Set snmp v2 and v3 trap settings as outside boundary values [Invalid], verify error message is displayed.
    
Created on 2011-5-09
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_SNMP_Agent_Info'
    common_name = 'Enable SNMP Agent V2 via GUI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = 'Enable SNMP Trap V3 with Default Config from GUI'
    param_cfg = {'snmp_trap_cfg':tcfg['default_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_case_name = '[Trap V3 Valid Values - Mid Range]'
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sEnable SNMP Trap V3 from GUI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['v3_trap_cfg_mid_range']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP Trap V3 Info between GUI Get and GUI Set' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['v3_trap_cfg_mid_range']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'trap'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_agent_v2_cfg'],
                 'info_type': 'trap',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Trap Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Trap V3 Valid Values - Lower Boundary]'
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sEnable SNMP Trap V3 from GUI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['v3_trap_cfg_lower_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP Trap V3 Info between GUI Get and GUI Set' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['v3_trap_cfg_lower_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'trap'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_agent_v2_cfg'],
                 'info_type': 'trap',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Trap Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Trap V3 Valid Values - Upper Boundary]'
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = '%sEnable SNMP Trap V3 from GUI' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['v3_trap_cfg_upper_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_SNMP_Trap_Info_Get_Set'
    common_name = '%sVerify SNMP Trap V3 Info between GUI Get and GUI Set' % (test_case_name,)
    param_cfg = {'snmp_trap_cfg':tcfg['v3_trap_cfg_upper_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Trap_Info'
    common_name = '%sGet SNMP Trap Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMP_Trap_Info'
    common_name = '%sVerify SNMP Trap Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'trap'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Trap Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['enable_agent_v2_cfg'],
                 'info_type': 'trap',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Trap Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Invalid Values - Outside Boundary]'
    
    test_name = 'CB_ZD_Config_SNMP_Trap_Outside_Boundary'
    common_name = '%sVerify outside boundary values for snmp trap' % (test_case_name,)
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Set_SNMP_Trap_Info'
    common_name = 'Restore SNMP Trap V3 Config from GUI'
    param_cfg = {'snmp_trap_cfg':tcfg['default_v3_trap_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def gen_random_string(min_len, max_len = '', type = 'alnum'):
    '''
    Generate a random string between min_len and max_len. 
    Type can be 'ascii'[char 32 -126], 'alpha'[letters], 'hex'[0-9 a-f], 'alnum'[letters,digits].     
    ''' 
    ran_str = utils.get_random_string(type, min_len, max_len)
        
    if type.lower() == 'ascii':
        #In webui, can't input the string include <, / and > in order.
        if ran_str.find('<')>-1 and ran_str.find('>')>-1 and ran_str.find('/')>-1:
            ran_str = ran_str.replace('/','a')
        
        #Remove ' and ".
        if ran_str.find("'")>-1:
            ran_str = ran_str.replace("'",'a')            
        if ran_str.find('"')>-1:
            ran_str = ran_str.replace('"','a')
        #Remove ; because parsing issue in zd cli.            
        if ran_str.find(';')>-1:
            ran_str = ran_str.replace(';','a')
                    
    return ran_str
    
def define_test_parameters(tbcfg, trap_server_ip):
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    enable_agent_v2_cfg = {'version': 2,
                           'enabled': True,
                           'ro_community': 'public',
                           'rw_community': 'private',
                           'contact': 'support@ruckuswireless.com',
                           'location': 'Shenzhen',
                           }
    
    default_v3_trap_cfg = {'version': 3,
                           'enabled': True,
                           '1': {'sec_name': 'ruckus-read',
                               'server_ip': trap_server_ip,
                               'auth_protocol': 'MD5',
                               'auth_passphrase': '12345678',
                               'priv_protocol': 'DES',
                               'priv_passphrase': '12345678',
                               }
                           }
    
    v3_trap_cfg_mid_range = {'version': 3,
                             'enabled': True,
                             '1': {'sec_name': gen_random_string(2,31),
                                 'server_ip': trap_server_ip,
                                 'auth_protocol': 'MD5',
                                 'auth_passphrase': gen_random_string(9, 31),
                                 'priv_protocol': 'DES',
                                 'priv_passphrase': gen_random_string(9, 31),
                                 }
                             }
    
    v3_trap_cfg_lower_boundary = {'version': 3,
                                  'enabled': True,
                                  '1':{'sec_name': gen_random_string(1),
                                      'server_ip': trap_server_ip,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': gen_random_string(8),
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': gen_random_string(8),
                                      }
                          }
    
    v3_trap_cfg_upper_boundary = {'version': 3,
                                  'enabled': True,
                                  '1': {'sec_name': gen_random_string(32),
                                      'server_ip': trap_server_ip,
                                      'auth_protocol': 'MD5',
                                      'auth_passphrase': gen_random_string(32),
                                      'priv_protocol': 'DES',
                                      'priv_passphrase': gen_random_string(32),
                                      }
                                  }
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'enable_agent_v2_cfg': enable_agent_v2_cfg,
            'default_v3_trap_cfg': default_v3_trap_cfg,
            'v3_trap_cfg_mid_range': v3_trap_cfg_mid_range,
            'v3_trap_cfg_lower_boundary': v3_trap_cfg_lower_boundary,
            'v3_trap_cfg_upper_boundary': v3_trap_cfg_upper_boundary,
            }
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        trap_server_ip = '2020:db8:1::10'
        ts_name = 'ZD GUI ZD %s AP %s - SNMP Trap Configuration - Length Checking' % (zd_ip_version, ap_ip_version)
    else:
        trap_server_ip = '192.168.0.10'
        ts_name = 'ZD GUI - SNMP Trap Configuration - Length Checking'

    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP Trap Configuration: Length Checking', combotest=True)
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
    