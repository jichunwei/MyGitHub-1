'''
Set SNMP Agent settings via ZD CLI.

    Set SNMP agent settings with valid values, and error is displayed for invalid values.    
    SNMP V2 agent:
    1. Set snmp agent setting with valid value, the setting is correct and snmp works well.
    1. Set snmp agent setting with invalid value, error message is displayed.      
    SNMP V3 agent:
    1. Set snmp agent setting with valid value, the setting is correct and snmp works well.
    1. Set snmp agent setting with invalid value, error message is displayed.
    
    expect result: All steps should result properly.
    
    How to:
        1) Set snmp v2 agent setting with mid range values via CLI.
        2) Get snmp v2 agent setting via CLI.         
        4) Verify the values between CLI get and set.
        5) Get snmp v2 agent setting via GUI.
        6) Verify the value between CLI get and GUI get.
        7) Get snmp v2 agent setting via CLI [For comparision with SNMP get]. 
        7) Get snmp v2 agent setting via SNMP.
        8) Verify the values between CLI get and SNMP get.
        9) Repeat step 1)-8) with lower range values.
        10) Repeat step 1)-8) with upper range values.
        11) Set snmp agent settings as outside boundary values [Invalid], verify error message is displayed.
        12) Repeat 1)-11) for snmp v3 agent settings.
    
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
    common_name = 'apmgr and stamgr daemon pid mark'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V2 via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP Agent V3 via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_agent_v3_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
    
    test_case_name = '[V2 Valid Values - Mid Range]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V2 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v2_cfg_mid_range']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%sGet SNMPV2 Agent Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V2 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v2_cfg_mid_range']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_Info'
    common_name = '%sGet SNMP V2 Agent Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info'
    common_name = '%sVerify SNMP Agent V2 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'v2_agent'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Agent V2 Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['snmp_agent_v2_cfg_mid_range'],
                 'info_type': 'v2_agent',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Agent V2 Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[V2 Valid Values - Lower Boundary]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V2 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v2_cfg_lower_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%sGet SNMPV2 Agent Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V2 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v2_cfg_lower_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_Info'
    common_name = '%sGet SNMP V2 Agent Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info'
    common_name = '%sVerify SNMP Agent V2 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'v2_agent'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Agent V2 Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['snmp_agent_v2_cfg_lower_boundary'],                 
                 'info_type': 'v2_agent',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Agent V2 Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[V2 Valid Values - Upper Boundary]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V2 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v2_cfg_upper_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV2_Info'
    common_name = '%sGet SNMPV2 Agent Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V2 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v2_cfg_upper_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_Info'
    common_name = '%sGet SNMP V2 Agent Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV2_Info'
    common_name = '%sVerify SNMP Agent V2 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'v2_agent'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Agent V2 Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['snmp_agent_v2_cfg_upper_boundary'],                 
                 'info_type': 'v2_agent',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Agent V2 Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))    
    
    test_case_name = '[V3 Valid Values - Mid Range]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V3 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v3_cfg_mid_range']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMP Agent V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V3 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v3_cfg_mid_range']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_GUIGet_CLIGet'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'v3_agent'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Agent V2 Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['snmp_agent_v3_cfg_mid_range'],
                 'info_type': 'v3_agent',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Agent V3 Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[V3 Valid Values - Lower Boundary]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V3 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v3_cfg_lower_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMP Agent V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V3 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v3_cfg_lower_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_GUIGet_CLIGet'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'v3_agent'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Agent V2 Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['snmp_agent_v3_cfg_lower_boundary'],
                 'info_type': 'v3_agent',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Agent V3 Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))    
    
    test_case_name = '[V3 Valid Values - Upper Boundary]'
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = '%sEnable SNMP Agent V3 from CLI' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v3_cfg_upper_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMPV3_Info'
    common_name = '%sGet SNMP Agent V3 Info from CLI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_CLI_Get_Set'
    common_name = '%sVerify SNMP Agent V3 Info between CLI Get and CLI Set' % (test_case_name,)
    param_cfg = {'snmp_agent_cfg':tcfg['snmp_agent_v3_cfg_upper_boundary']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_SNMP_Agent_V3_Info'
    common_name = '%sGet SNMP Agent V3 Info from GUI' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_CLI_Verify_SNMPV3_Info_GUIGet_CLIGet'
    common_name = '%sVerify SNMP Agent V3 Info between GUI Get and CLI Get' % (test_case_name,)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_Sys_SNMP_Info'
    common_name = '%sGet System SNMP Info via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'info_type':'v3_agent'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Get_Sys_SNMP_Info'
    common_name = '%sGet SNMP Agent V2 Info from SNMP' % (test_case_name,)
    param_cfg = {'snmp_cfg': tcfg['snmp_cfg'],
                 'snmp_agent_cfg': tcfg['snmp_agent_v3_cfg_upper_boundary'],
                 'info_type': 'v3_agent',
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet'
    common_name = '%sVerify System SNMP Agent V3 Info between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Invalid Values - Outside Boundary]'
    
    test_name = 'CB_ZD_CLI_Config_SNMP_Agent_Outside_Boundary'
    common_name = '%sVerify outside boundary values for snmp agent' % (test_case_name,)
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Restore SNMP Agent V2 Settings via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_agent_v2_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Restore SNMP Agent V3 settings via CLI'
    param_cfg = {'snmp_agent_cfg':tcfg['enable_agent_v3_cfg']}
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
            ran_str = ran_str.replace("'",'b')            
        if ran_str.find('"')>-1:
            ran_str = ran_str.replace('"','c')
        #Remove ; because parsing issue in zd cli.            
        if ran_str.find(';')>-1:
            ran_str = ran_str.replace(';','d')
                    
    return ran_str

def define_test_parameters(tbcfg):
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
                           
    enable_agent_v3_cfg = {'version': 3,
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
                           'rw_priv_passphrase': '12345678',}
        
    snmp_agent_v3_cfg_mid_range = {'version': 3,
                                   'enabled': True,
                                   'ro_sec_name': gen_random_string(2, 30),
                                   'ro_auth_protocol': 'MD5',
                                   'ro_auth_passphrase': gen_random_string(9, 31),
                                   'ro_priv_protocol': 'DES',
                                   'ro_priv_passphrase': gen_random_string(9, 31),
                                   'rw_sec_name': gen_random_string(2, 30),
                                   'rw_auth_protocol': 'MD5',
                                   'rw_auth_passphrase': gen_random_string(9, 31),
                                   'rw_priv_protocol': 'DES',
                                   'rw_priv_passphrase': gen_random_string(9, 31),
                                   }
    
    snmp_agent_v3_cfg_lower_boundary = {'version': 3,
                                        'enabled': True,
                                        'ro_sec_name': '1',
                                        'ro_auth_protocol': 'MD5',
                                        'ro_auth_passphrase': gen_random_string(8),
                                        'ro_priv_protocol': 'DES',
                                        'ro_priv_passphrase': gen_random_string(8),
                                        'rw_sec_name': '9',
                                        'rw_auth_protocol': 'MD5',
                                        'rw_auth_passphrase': gen_random_string(8),
                                        'rw_priv_protocol': 'DES',
                                        'rw_priv_passphrase': gen_random_string(8),
                                        }
    
    snmp_agent_v3_cfg_upper_boundary = {'version': 3,
                                        'enabled': True,
                                        'ro_sec_name': gen_random_string(31),
                                        'ro_auth_protocol': 'MD5',
                                         'ro_auth_passphrase': gen_random_string(32),
                                         'ro_priv_protocol': 'DES',
                                         'ro_priv_passphrase': gen_random_string(32),
                                         'rw_sec_name': gen_random_string(31),
                                         'rw_auth_protocol': 'MD5',
                                         'rw_auth_passphrase': gen_random_string(32),
                                         'rw_priv_protocol': 'DES',
                                         'rw_priv_passphrase': gen_random_string(32),
                                         }
    
    snmp_agent_v2_cfg_mid_range = {'version': 2,
                                   'enabled': True,
                                   'ro_community': gen_random_string(2,31),
                                   'rw_community': gen_random_string(2,31),
                                   'contact': gen_random_string(2,63),
                                   'location': gen_random_string(2,63)}
    
    snmp_agent_v2_cfg_lower_boundary = {'version': 2,
                                        'enabled': True,
                                        'ro_community': '3',
                                        'rw_community': '8',
                                        'contact': gen_random_string(1),
                                        'location': gen_random_string(1),}
    
    snmp_agent_v2_cfg_upper_boundary = {'version': 2,
                                        'enabled': True,
                                        'ro_community': gen_random_string(32),
                                        'rw_community': gen_random_string(32),
                                        'contact': gen_random_string(64),
                                        'location': gen_random_string(64),
                                        }
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'enable_agent_v2_cfg': enable_agent_v2_cfg,
            'enable_agent_v3_cfg': enable_agent_v3_cfg,
            'snmp_agent_v2_cfg_mid_range': snmp_agent_v2_cfg_mid_range,
            'snmp_agent_v2_cfg_lower_boundary': snmp_agent_v2_cfg_lower_boundary,
            'snmp_agent_v2_cfg_upper_boundary': snmp_agent_v2_cfg_upper_boundary,
            'snmp_agent_v3_cfg_mid_range': snmp_agent_v3_cfg_mid_range,
            'snmp_agent_v3_cfg_lower_boundary': snmp_agent_v3_cfg_lower_boundary,
            'snmp_agent_v3_cfg_upper_boundary': snmp_agent_v3_cfg_upper_boundary,}
    
    return tcfg

def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD CLI - SNMP Agent Configuration - Length Checking'
    ts = testsuite.get_testsuite(ts_name, 'Verify SNMP Agent Configuration: Length Checking', combotest=True)
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
    