'''
Configure AAA servers with ipv6 addresses via GUI and CLI.

    Configure AAA servers with ipv6 addresses via GUI and CLI.
    AAA server type:
    AD, LDAP, Radius, Radius Accounting
    expect result: All steps should result properly.
    
    How to:
        1) Create a new AAA server.
        2) Get AAA server via GUI.         
        3) Compare the information are same between GUI set and GUI get.
        4) Get AAA servers via CLI.
        5) Compare the information are same between GUI get and CLI get.
        6) Repeat the step for different kind of AAA server type.
        7) Repeat step 1)-6) for CLI.
    
Created on 2012-2-03
@author: cherry.cheng@ruckuswireless.com
'''

import sys

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    for server_cfg in tcfg['gui_server_cfg_list']:
        server_name = server_cfg['server_name']
            
        test_case_name = "[GUI Set AAA Server %s]" % server_cfg['cfg_name']
        
        test_name = 'CB_ZD_Create_Authentication_Server'
        common_name = '%sCreate a AAA server via ZD GUI' % test_case_name
        test_cfgs.append(({'auth_ser_cfg_list':[server_cfg]}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Get_AAA_Servers'
        common_name = '%sGet AAA server info via ZD GUI' % test_case_name
        test_cfgs.append(({'server_name_list': [server_name]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AAA_Server_GUI_Set_Get'
        common_name = '%sVerify AAA server info between GUI set and GUI get' % test_case_name  
        test_cfgs.append(({'auth_ser_cfg_list': [server_cfg]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Get_AAA_Servers'
        common_name = '%sGet AAA server info via ZD CLI' % test_case_name  
        test_cfgs.append(({'server_name_list': [server_name]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AAA_Server_GUI_CLI_Get'
        common_name = '%sVerify AAA server info between GUI get and CLI get' % test_case_name  
        test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA servers from ZD GUI after GUI test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    for server_cfg in tcfg['cli_server_cfg_list']:
        if server_cfg.get('new_server_name'):
            server_name = server_cfg['new_server_name']
        else:
            server_name = server_cfg['server_name']
            
        test_case_name = "[CLI Set AAA Server %s]" % server_cfg['cfg_name']
            
        test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
        common_name = '%sConfigure an AAA server via ZD CLI and verify set and get' % test_case_name  
        test_cfgs.append(({'server_cfg_list': [server_cfg]}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_CLI_Get_AAA_Servers'
        common_name = '%sGet AAA server info via ZD CLI' % test_case_name  
        test_cfgs.append(({'server_name_list': [server_name]}, test_name, common_name, 2, False))
            
        test_name = 'CB_ZD_Get_AAA_Servers'
        common_name = '%sGet AAA server info via ZD GUI' % test_case_name
        test_cfgs.append(({'server_name_list': [server_name]}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AAA_Server_GUI_CLI_Get'
        common_name = '%sVerify the AAA server info between GUI get and CLI get' % test_case_name  
        test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA servers from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs

def _define_aaa_server_cfg_list():
    server_cfg_list = []
    
    server_cfg_list.append(dict(server_name = 'ad_server_1', new_server_name = 'ad_server_new_1', type = 'ad', global_catalog = False, 
                                server_addr = '2020:db8:1::249', server_port = '389', win_domain_name = 'domain.ruckuswireless.com',
                                cfg_name = 'AD without Global Catalog'))
    
    server_cfg_list.append(dict(server_name = 'ad_server_2', new_server_name = 'ad_server_new_2', type = 'ad', global_catalog = True, 
                                server_addr = '2020:db8:1::249', server_port = '3289', win_domain_name = 'domain.ruckuswireless.com', 
                                admin_domain_name = 'admin@domain.ruckuswireless.com', admin_password = '1234567890',
                                cfg_name = 'AD with Global Catalog'))
                
    server_cfg_list.append(dict(server_name = 'ldap_server_1', new_server_name = 'ldap_server_new_1', type = 'ldap', server_addr = '2020:db8:1::249', 
                                server_port = '389', ldap_search_base = 'domain.ruckuswireless.com', 
                                ldap_admin_dn = 'admin@domain.ruckuswireless.com', ldap_admin_pwd = '1234567890',
                                ldap_key_attribute = 'uid', ldap_search_filter = 'objectClass=*',
                                cfg_name = 'LDAP'))
    
    server_cfg_list.append(dict(server_name = 'radius_server_1', new_server_name = 'radius_server_new_1', type = 'radius-auth', backup = False, 
                                server_addr = '2020:db8:1::252', server_port = '1812', radius_auth_secret = '1234567890', radius_auth_method = 'pap',
                                cfg_name = 'RADIUS without Backup'))

    server_cfg_list.append(dict(server_name = 'radius_server_2', new_server_name = 'radius_server_new_2', type = 'radius-auth', backup = True, 
                                server_addr = '2020:db8:1::252', server_port = '1813', radius_auth_secret = '1234567890', radius_auth_method = 'chap',
                                secondary_server_addr = '2020:db8:1::251', secondary_server_port = '1813', 
                                secondary_radius_auth_secret = '1234567890', 
                                request_timeout = '3', retry_count = '2', retry_interval = '5',
                                cfg_name = 'RADIUS with Backup'))
    
    server_cfg_list.append(dict(server_name = 'acct_server_1', new_server_name = 'acct_server_new_1', type = 'radius-acct', backup = False, 
                                server_addr = '2020:db8:1::252', server_port = '1812', radius_acct_secret = '1234567890',
                                cfg_name = 'Radius Accounting without Backup'))

    server_cfg_list.append(dict(server_name = 'acct_server_2', new_server_name = 'acct_server_new_2', type = 'radius-acct', backup = True, 
                                server_addr = '2020:db8:1::252', server_port = '1813', radius_acct_secret = '1234567890',
                                secondary_server_addr = '2020:db8:1::249', secondary_server_port = '1813', 
                                secondary_acct_secret = '1234567890', 
                                primary_timeout = '3', failover_retries = '2', primary_reconnect = '5',
                                cfg_name = 'Radius Accounting with Backup'))

    return server_cfg_list

def _convert_server_cfg_list_for_cli(server_cfg_list):
    '''
    Convert set server configuration list to cli set dict structure.
    '''
    gui_cli_set_keys_mapping = {#'win_domain_name': 'win_domain_name', #AD
                                #'admin_domain_name': 'admin_domain_name',
                                #'admin_password': 'admin_password',
                                'ldap_search_base': 'win_domain_name',#LDAP
                                'ldap_admin_dn': 'admin_domain_name',
                                'ldap_admin_pwd': 'admin_password',
                                'radius_auth_secret': 'radius_secret',
                                'radius_acct_secret': 'radius_secret',
                                'secondary_server_addr': 'backup_server_addr',
                                'secondary_server_port': 'backup_server_port',
                                'secondary_radius_auth_secret': 'backup_radius_secret',
                                'secondary_acct_secret': 'backup_radius_secret',
                                'primary_timeout': 'request_timeout',
                                'failover_retries': 'retry_count',
                                'primary_reconnect': 'retry_interval',
                                }
    
    new_server_cfg_list = []
    
    for server_cfg in server_cfg_list:
        new_server_cfg = {}
        for key, value in server_cfg.items():
            if gui_cli_set_keys_mapping.has_key(key):
                new_key = gui_cli_set_keys_mapping[key]
            else:
                new_key = key
            
            new_server_cfg[new_key] = value
            
        new_server_cfg_list.append(new_server_cfg)
    
    return new_server_cfg_list

def create_test_suite(**kwargs):    
    ts_name = 'Configure AAA Servers IPV6 via GUI CLI'
    ts = testsuite.get_testsuite(ts_name, 'Verify configure AAA servers with IPV6 address via GUI and CLI', combotest=True)
    
    server_cfg_list = _define_aaa_server_cfg_list()
    tcfg = {'gui_server_cfg_list': server_cfg_list,
            'cli_server_cfg_list': _convert_server_cfg_list_for_cli(server_cfg_list),
            }
    test_cfgs = define_test_cfg(tcfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.add_test_case(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    