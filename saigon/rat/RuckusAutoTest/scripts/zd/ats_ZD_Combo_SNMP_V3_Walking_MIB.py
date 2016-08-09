'''
Walking the whole MIB via SNMP V3

    Walking the whole MIB can get correct information.   
    1. Walking RUCKUS-ZD-SYSTEM-MIB, get system information and compare the values with zd cli result.
    2. Walking RUCKUS-ZD-AP-MIB, get AP information and compare the values with zd cli result.
    3. Walking RUCKUS-ZD-AAA-MIB, get AAA servers information and compare the values with zd cli result.
    4. Walking RUCKUS-ZD-WLAN-CONFIG-MIB, get wlan and wlan group information and compare the values with zd cli result.
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
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
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
    common_name = '%sGet System IP Info via ZD CLI' % (test_case_name,)
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
    
    test_case_name = '[Walking AAA MIB]'
    
    test_name = 'CB_ZD_SNMP_Walking_AAA_MIB'
    common_name = '%sWalking AAA server mib' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Get_AAA_Servers'
    common_name = '%sGet AAA servers via ZD CLI' % (test_case_name,)
    test_cfgs.append(( {'server_name_list': tcfg['server_name_list']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_AAA_Servers_SNMPGet_CLIGet'
    common_name = '%sVerify All AAA servers between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Walking Wlan Config MIB]'
    
    test_name = 'CB_ZD_SNMP_Walking_Wlan_Config_MIB'
    common_name = '%sWalking wlan config mib' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Get_All_Wlan'
    common_name = '%sGet ZD All Wlans Info via CLI' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Wlans_SNMPGet_CLIGet'
    common_name = '%sVerify All wlans between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '%sGet all WLAN groups information from ZD via CLI' % (test_case_name,)   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Wlan_Groups_SNMPGet_CLIGet'
    common_name = '%sVerify All wlan groups between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
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
                   auth_server_id = '1', wireless_client = 'none(1)', #zero_it_activation = 'enable(1)', #@ZJ When enable Webauth,zero_it is gray.ZF-10117 
                   service_priority = 'high(1)',
                   accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable', downlink_rate = 'disable',
                   vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                   max_clients_per_ap = '100', web_auth = 'enable(1)')
    
    wlan_group_cfg = dict(name = 'GroupTest-new1', desc = 'GroupTest1-123',
                          wlan_member = {})
    
    tcfg = {'snmp_cfg': snmp_cfg,
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            'server_cfg_list': [server_cfg],
            'server_name_list': [server_name],            
            'wlan_cfg_list': [wlan_cfg],            
            'wlan_group_cfg_list': [wlan_group_cfg],            
            }
    
    return tcfg
    
def create_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)        
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        
        ts_name = 'ZD SNMP V3 ZD %s AP %s - Walking MIB' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V3 - Walking MIB'
    
    tcfg = define_test_parameters(tbcfg)
    ts = testsuite.get_testsuite(ts_name, 'Verify walking mib via snmp v3', combotest=True)
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
    