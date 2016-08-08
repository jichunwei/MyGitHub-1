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
    
    test_name = 'CB_ZD_SNMP_Config_AAA_Servers'
    common_name = 'Create AAA servers on ZD via SNMP'
    test_cfgs.append(( {'server_cfg_list': tcfg['server_cfg_list'],
                        'server_name_list': tcfg['server_name_list'], 
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SNMP_Create_Wlans'
    common_name = 'Create wlans via SNMP'
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'create_wlan_cfg_list': tcfg['wlan_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SNMP_Create_Wlan_Groups'
    common_name = 'Create wlan groups via SNMP'
    test_cfgs.append(( {'wlan_group_cfg_list': tcfg['wlan_group_cfg_list'],
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[System Info Negative Input]'
    
    test_name = 'CB_ZD_SNMP_Negative_Input_Sys_Info'
    common_name = '%sVerify Negative Input for System Info' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_case_name = '[AAA Server Negative Input]' 
    
    test_name = 'CB_ZD_SNMP_Negative_Input_AAA_Server'
    common_name = '%sVerify Negative Input for AAA Server' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'server_name': tcfg['server_name']}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Info Negative Input]'
    
    test_name = 'CB_ZD_SNMP_Negative_Input_Wlan'
    common_name = '%sVerify Negative Input for Wlan' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'wlan_name': tcfg['wlan_name']}, test_name, common_name, 1, False))
    
    test_case_name = '[Wlan Group Negative Input]'
    
    test_name = 'CB_ZD_SNMP_Negative_Input_Wlan_Group'
    common_name = '%sVerify Negative Input for Wlan Group' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg'],
                        'wlan_group_name': tcfg['wlan_group_name']}, test_name, common_name, 1, False))
    
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
    
    snmp_cfg = {#'ip_addr': tbcfg['ZD']['ip_addr'],
                'timeout': 20,
                'retries': 3,}
    
    server_cfg = dict(server_name = 'Radius-Auth-Server', type = 'aaa-authentication(3)',
                      server_addr = '192.168.30.252', server_port = '1812', radius_secret = '123456789',
                      backup = 'disable(2)', backup_server_addr = '192.168.30.252',
                      backup_server_port = '0', backup_radius_secret = '123456789',
                      request_timeout = '3', retry_count = '2', retry_interval = '5',)
    
    server_name = server_cfg['server_name']
    
    wlan_cfg = dict(ssid = 'Standard-Open-None', desc = 'Standard open and no encryption', name = 'Standard-Open-None', service_type = 'standardUsage(1)',
                   auth = 'open(1)', encrypt = 'none-enc(6)', wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                   auth_server_id = '1', wireless_client = 'none(1)', zero_it_activation = 'enable(1)', service_priority = 'high(1)',
                   accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable', downlink_rate = 'disable',
                   vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                   max_clients_per_ap = '100', web_auth = 'enable(1)')
    
    wlan_name = wlan_cfg['name']
    
    wlan_group_cfg = dict(name = 'GroupTest-new1', desc = 'GroupTest1-123',
                          wlan_member = {wlan_name: {'override_type': 'tag(2)', 'vlan_tag': '3'}})
    
    wlan_group_name = wlan_group_cfg['name']
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            'server_cfg_list': [server_cfg],
            'server_name_list': [server_name],
            'server_name': server_name,
            'wlan_cfg_list': [wlan_cfg],
            'wlan_name': wlan_name,
            'wlan_group_cfg_list': [wlan_group_cfg],
            'wlan_group_name': wlan_group_name
            }
    
    return tcfg
    
def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        
        ts_name = 'ZD SNMP V3 ZD %s AP %s - Negative Testing' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V3 - Negative Testing'
        
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
    