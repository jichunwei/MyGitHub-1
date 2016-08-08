'''
Configure AAA server settings via SNMP V3.

    Update AAA server setting via SNMP V3 successfully and the value same as CLI.    
    1. Update read-write nodes in AAA server, and verify the values are same between get and set, snmp get and cli get.
        
    expect result: All steps should result properly.
    
    How to:
        1) Create AAA servers, two types: Radius, and Radius Account.
        2) Update AAA server settings, and verify the values between get and set.
        3) Get AAA server information from SNMP.
        4) Get AAA server information from CLI.
        5) Verify the values from SNMP and CLI are same.
    
Created on 2011-3-25
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
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP agent v2'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 2, 'enabled': False}}, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Disable SNMP agent v3'
    test_cfgs.append(({'snmp_agent_cfg': {'version': 3, 'enabled': False}}, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_CLI_Set_SNMP_Agent'
    common_name = 'Enable SNMP agent v3'
    test_cfgs.append(({'snmp_agent_cfg':tcfg['set_snmp_agent_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[Create AAA Server]'
    
    test_name = 'CB_ZD_SNMP_Config_AAA_Servers'
    common_name = '%sCreate AAA servers on ZD via SNMP' % (test_case_name,)
    test_cfgs.append(( {'server_cfg_list': tcfg['server_cfg_list'],
                        'server_name_list': tcfg['server_name_list'], 
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SNMP_Get_AAA_Servers'
    common_name = '%sGet ZD All Servers Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'server_name_list': tcfg['server_name_list'], 
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AAA_Servers_SNMP_Get_Set'
    common_name = '%sVerify all servers info between SNMP get and set' % (test_case_name,)
    test_cfgs.append(( {'server_cfg_list':tcfg['server_cfg_list']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_AAA_Servers'
    common_name = '%sGet AAA servers via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'server_name_list': tcfg['server_name_list']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AAA_Servers_SNMPGet_CLIGet'
    common_name = '%sVerify All AAA servers between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Update AAA Server]'
    
    test_name = 'CB_ZD_SNMP_Verify_Update_AAA_Server'
    common_name = '%sVerify update AAA server configuration via ZD SNMP' % (test_case_name,)
    test_cfgs.append(( {'server_name': tcfg['server_name_list'][0],
                        'update_server_cfg_list': tcfg['update_server_cfg_list'], 
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SNMP_Get_AAA_Servers'
    common_name = '%sGet ZD All Servers Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'server_name_list': tcfg['server_name_list'], 
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Get_AAA_Servers'
    common_name = '%sGet AAA servers via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'server_name_list': tcfg['server_name_list']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AAA_Servers_SNMPGet_CLIGet'
    common_name = '%sVerify All AAA servers between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Delete AAA Servers]'
    
    test_name = 'CB_ZD_SNMP_Verify_Delete_AAA_Servers'
    common_name = '%sVerify delete AAA server via ZD SNMP' % (test_case_name,)
    test_cfgs.append(( {'server_name_list': tcfg['server_name_list'], 
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
        
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs

def define_create_aaa_server_cfg_list(test_cfg):
    server_cfg_list = []
        
    #zd_ip_addr = test_cfg['ip_addr']
    svr_ip_addr = test_cfg['svr_ip_addr']
    svr_ip_addr_backup = test_cfg['svr_ip_addr_backup'] 
    svr_port_auth = test_cfg['svr_port_auth']
    svr_port_acct = test_cfg['svr_port_acct']
            
    server_cfg_list.append(dict(server_name = 'Radius-Auth-Server', type = 'aaa-authentication(3)',
                                  server_addr = svr_ip_addr, server_port = svr_port_auth, radius_secret = '123456789',
                                  backup = 'disable(2)', backup_server_addr = svr_ip_addr_backup,
                                  backup_server_port = svr_port_auth, backup_radius_secret = '123456789',
                                  request_timeout = '3', retry_count = '2', retry_interval = '5',))
                     
    server_cfg_list.append(dict(server_name = 'Radius-Account-Server', type = 'aaa-accounting(4)',
                                 server_addr = svr_ip_addr, server_port = svr_port_acct, radius_secret = '123456789',
                                 backup = 'enable(1)', backup_server_addr = svr_ip_addr_backup,
                                 backup_server_port = svr_port_acct, backup_radius_secret = '123456789',
                                 request_timeout = '3', retry_count = '2', retry_interval = '5',))
    
    return server_cfg_list

def define_update_aaa_server_cfg_list(test_cfg):
    zd_ip_addr = test_cfg['ip_addr']
    svr_ip_addr = test_cfg['svr_ip_addr']
    svr_ip_addr_backup = test_cfg['svr_ip_addr_backup'] 
    svr_port_auth = test_cfg['svr_port_auth']
    svr_port_acct = test_cfg['svr_port_acct']
    
    update_server_cfg_list = [dict(server_addr = zd_ip_addr, server_port = svr_port_acct, radius_secret = '8756423975'),
                              dict(backup = 'enable(1)', backup_server_addr = svr_ip_addr, backup_server_port = svr_port_acct,
                                   backup_radius_secret = '123456789', request_timeout = '10', retry_count = '10', retry_interval = '10',),
                              dict(request_timeout = '6', retry_count = '7', retry_interval = '8'),
                              dict(backup = 'disable(2)'),
                              dict(type = 'aaa-accounting(4)'),
                              dict(server_addr = svr_ip_addr_backup, server_port = svr_port_auth, radius_secret = '123456789'),
                              dict(backup = 'enable(1)', backup_server_addr = svr_ip_addr, backup_server_port = svr_port_acct,
                                   backup_radius_secret = '123456789', request_timeout = '4', retry_count = '6', retry_interval = '10',),
                              dict(request_timeout = '5', retry_count = '5', retry_interval = '5'),
                              dict(backup = 'disable(2)')
                              ]
    
    return update_server_cfg_list

def get_server_name_list(server_cfg_list):
    server_name_list = []
    for server_cfg in server_cfg_list:
        server_name_list.append(server_cfg['server_name'])
        
    return server_name_list

def define_test_parameters(test_cfg):
    set_snmp_agent_cfg = {'version': 3,
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
                         'rw_priv_passphrase': '12345678',
                         }
    
    
    snmp_cfg = {#'ip_addr': test_cfg['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    server_cfg_list = define_create_aaa_server_cfg_list(test_cfg)
    tcfg = {'server_cfg_list': server_cfg_list,
            'update_server_cfg_list': define_update_aaa_server_cfg_list(test_cfg),
            'server_name_list': get_server_name_list(server_cfg_list),
            'snmp_cfg': snmp_cfg,
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            }
    
    return tcfg
 
def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ip_addr = tbcfg['ZD']['ip_addr']
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        ts_name = 'ZD SNMP V3 ZD %s AP %s - AAA Server Configuration' % (zd_ip_version, ap_ip_version)
        
        svr_ip_addr = tbcfg['ipv6_server']['ip_addr']
        svr_ip_addr_backup = '2020:db8:1::252'
        svr_port_auth = '50001'
        svr_port_acct = '1813'
    else:
        svr_ip_addr = testsuite.getTestbedServerIp(tbcfg)
        svr_ip_addr_backup = '192.168.0.251'
        svr_port_auth = '1812'
        svr_port_acct = '1813'
        ts_name = 'ZD SNMP V3 - AAA Server Configuration'
    
    test_cfg = {'ip_addr': ip_addr,
                'svr_ip_addr': svr_ip_addr, 
                'svr_ip_addr_backup': svr_ip_addr_backup, 
                'svr_port_auth': svr_port_auth, 
                'svr_port_acct': svr_port_acct,
                }
    
    tcfg = define_test_parameters(test_cfg)
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs AAA Server Configuration: SNMP Set, CLI Get', combotest=True)
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
    