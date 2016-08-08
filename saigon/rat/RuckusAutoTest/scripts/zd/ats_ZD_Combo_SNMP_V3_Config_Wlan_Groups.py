'''
Configure wlan group settings via SNMP V3.

    Update wlan group setting via SNMP V3 successfully and the value same as CLI.    
    1. Update read-write nodes in wlan group, and verify the values are same between get and set, snmp get and cli get.
        
    expect result: All steps should result properly.
    
    How to:
        1) Create AAA servers.
        2) Create three wlans.
        3) Create one wlan group, assign three wlans to this group.         
        4) Update wlan group settings, and verify the values between get and set.
        5) Get wlan group information from SNMP.
        6) Get wlan group information from CLI.
        7) Verify the values from SNMP and CLI are same.
    
Created on 2011-4-14
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
    
    test_name = 'CB_ZD_SNMP_Create_Wlans'
    common_name = 'Create wlans via SNMP'
    test_cfgs.append(( {'create_wlan_cfg_list': tcfg['wlan_cfg_list'],
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 0, False))
    
    test_case_name = '[Create Wlan Groups]'
    
    test_name = 'CB_ZD_SNMP_Create_Wlan_Groups'
    common_name = '%sCreate wlan groups via SNMP' % (test_case_name,)
    test_cfgs.append(( {'wlan_group_cfg_list': tcfg['wlan_group_cfg_list'],
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SNMP_Get_Wlan_Groups'
    common_name = '%sGet ZD All wlan groups Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Wlan_Groups_SNMP_Get_Set'
    common_name = '%sVerify All Wlan groups Info Between SNMP get and set' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '%sGet all WLAN groups information from ZD via CLI' % (test_case_name,)   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Wlan_Groups_SNMPGet_CLIGet'
    common_name = '%sVerify All wlan groups between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Update Wlan Group]'
    
    test_name = 'CB_ZD_SNMP_Verify_Update_Wlan_Group'
    common_name = '%sVerify update wlan group config via ZD SNMP' % (test_case_name,)
    test_cfgs.append(( {'edit_wlan_group_cfg_list': tcfg['edit_wlan_group_cfg_list'],
                        'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SNMP_Get_Wlan_Groups'
    common_name = '%sGet ZD All wlan groups Info via SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Show_WlanGroup_All'
    common_name = '%sGet all WLAN groups information from ZD via CLI' % (test_case_name,)   
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SNMP_Verify_Wlan_Groups_SNMPGet_CLIGet'
    common_name = '%sVerify All wlan groups between SNMP Get and CLI Get' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_case_name = '[Delete Wlan Groups]'
    
    test_name = 'CB_ZD_SNMP_Verify_Delete_Wlan_Groups'
    common_name = '%sVerify delete wlan groups via ZD SNMP' % (test_case_name,)
    test_cfgs.append(( {'snmp_agent_cfg': tcfg['set_snmp_agent_cfg'], 
                        'snmp_cfg': tcfg['snmp_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs


def define_wlan_cfg_list():
    wlan_cfg_list = []
    
    wlan_cfg_list.append(dict(ssid = 'Standard-Open-None', desc = 'Standard open and no encryption', 
                              name = 'Standard-Open-None', service_type = 'standardUsage(1)',
                              auth = 'open(1)', encrypt = 'none-enc(6)', 
                              #wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                              auth_server_id = '1', wireless_client = 'none(1)', 
                              #zero_it_activation = 'enable(1)',  #@ZJ When enable Webauth,zero_it is gray.ZF-10117
                              service_priority = 'high(1)',
                              accounting_server_id = '0', accounting_update_interval = '10', 
                              uplink_rate = 'disable', downlink_rate = 'disable',
                              vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', 
                              tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                              max_clients_per_ap = '100', web_auth = 'enable(1)'))
    wlan_cfg_list.append(dict(ssid = 'Standard-Open-WEP', desc = 'Standard open and WEP encryption', 
                              name = 'Standard-Open-WEP', service_type = 'standardUsage(1)', 
                              auth = 'open(1)', encrypt = 'wep-64(4)', wep_key_index = '2', wep_key = '6D1E046A8D',
                              #wpa_cipher_type = 'none(0)', wpa_key = '1234567890', 
                              auth_server_id = '0', zero_it_activation = 'enable(1)', 
                              service_priority = 'low(2)', accounting_server_id = '0', accounting_update_interval = '20',
                              uplink_rate = 'disable', downlink_rate = 'disable', 
                              vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)',
                              tunnel_mode = 'false(2)', bg_scanning = 'true(1)', max_clients_per_ap = '100', web_auth = 'disable(2)'))
    
    return wlan_cfg_list

def get_wlan_name_list(wlan_cfg_list):
    wlan_name_list = []
    
    for wlan_cfg in wlan_cfg_list:
        wlan_name_list.append(wlan_cfg['name'])
    
    return wlan_name_list

def define_create_wlan_group_cfg_list(wlan_name_list):
    wlan_group_list = []
    
    wlan_group_list.append(dict(name = 'GroupTest-new1', desc = 'GroupTest1-123', wlan_member = {}),)
    
    if wlan_name_list:
        wlan_members = {}
        wlan_member_cfg = [{'override_type': 'tag(2)', 'vlan_tag': '3'},
                           #{'override_type': 'untag(2)' },
                           {'override_type': 'nochange(1)'}
                          ]

        for i in range(0, len(wlan_name_list)):
            wlan_name = wlan_name_list[i]
            cfg_index = i % 2
            wlan_members[wlan_name] = wlan_member_cfg[cfg_index]

        wlan_group_list.append(dict(name = 'GroupTest-new2', desc = 'GroupTest2-123',
                             wlan_member = wlan_members))

    return wlan_group_list

def define_update_wlan_group_cfg_list(wlan_name_list):
    update_cfg_list = []
    
    update_cfg_list.append(dict(desc = 'DescriptionUpdateTest.'))
    
    if wlan_name_list:
        wlan_members = {}
        wlan_member_cfg = [{'override_type': 'tag(2)', 'vlan_tag': '3'},
#                           {'override_type': 'untag(2)' },
                           {'override_type': 'nochange(1)'}
                          ]

        for i in range(0, len(wlan_name_list)):
            wlan_name = wlan_name_list[i]
            cfg_index = i % 2
            wlan_members[wlan_name] = wlan_member_cfg[cfg_index]
    
        update_cfg_list.append(dict(wlan_member = wlan_members))
        
        wlan_members_2 = {}
        wlan_member_cfg_2 = [#{'override_type': 'untag(2)' },
                           {'override_type': 'nochange(1)'},
                           {'override_type': 'tag(2)', 'vlan_tag': '3'},]
                               
        for i in range(0, len(wlan_name_list)):
            wlan_name = wlan_name_list[i]
            cfg_index = i % 2
            wlan_members_2[wlan_name] = wlan_member_cfg_2[cfg_index]
        
        update_cfg_list.append(dict(wlan_member = wlan_members_2))

    return update_cfg_list

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
    
    wlan_cfg_list = define_wlan_cfg_list()
    wlan_name_list = get_wlan_name_list(wlan_cfg_list)
    
    new_wlan_group_cfg_list = define_create_wlan_group_cfg_list(wlan_name_list)
    edit_wlan_group_cfg_list = define_update_wlan_group_cfg_list(wlan_name_list)
    
    tcfg = {'wlan_cfg_list': wlan_cfg_list,
            'wlan_name_list': wlan_name_list,
            'wlan_group_cfg_list': new_wlan_group_cfg_list,
            'edit_wlan_group_cfg_list': edit_wlan_group_cfg_list,
            'snmp_cfg': snmp_cfg,
            'set_snmp_agent_cfg': set_snmp_agent_cfg,
            }
    
    return tcfg
    
def create_test_suite(**kwargs):    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    if str(tb.tbtype) == "ZD_Stations_IPV6":
        zd_ip_version = tbcfg['ip_cfg']['zd_ip_cfg']['ip_version']
        ap_ip_version = tbcfg['ip_cfg']['ap_ip_cfg']['ip_version']
        ts_name = 'ZD SNMP V3 ZD %s AP %s - Wlan Group Configuration' % (zd_ip_version, ap_ip_version)
    else:
        ts_name = 'ZD SNMP V3 - Wlan Group Configuration'
    
    tcfg = define_test_parameters(tbcfg)
    ts = testsuite.get_testsuite(ts_name, 'Verify ZDs Wlan Group Configuration: SNMP Set, CLI Get', combotest=True)
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
    