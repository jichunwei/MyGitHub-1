'''
Description: 
    Show AAA Server information on ZD CLI, verify the information on ZD GUI.
    By Chris
    cwang@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def gen_id(id):
    ex_id = "[AAA Servers configure from GUI, check from CLI]"
    return '%s(%d) ' % (ex_id, id)

def define_test_configuration(cfg):
    test_cfgs = []
    i = 1 
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = '%sRemove AAA Servers from GUI' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1
    auth_ser_cfg_list = [cfg['ad_server'], cfg['ldap_server'], cfg['radius_server'], cfg['radius_acc_server']]
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '%sCreate Authentication Servers' % gen_id(i)
    param_cfg = dict(auth_ser_cfg_list = auth_ser_cfg_list)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    i += 1
    test_name = 'CB_ZD_CLI_Get_All_AAA_Servers'
    common_name = '%sGet All AAA Servers Information' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
      
    
    cfg['ad_server']['type'] = 'ad'
    cfg['ldap_server']['type'] = 'ldap'
    cfg['radius_server']['type'] = 'radius-auth'
    cfg['radius_acc_server']['type'] = 'radius-acct'
    auth_ser_cfg_list = [cfg['ad_server'], cfg['ldap_server'], cfg['radius_server'], cfg['radius_acc_server']]
    
    i += 1
    test_name = 'CB_ZD_CLI_Verify_AAA_Servers'
    common_name = '%sVerify all AAA Servers in CLI' % gen_id(i)
    param_cfg = dict(server_list = auth_ser_cfg_list)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
      
        
    i += 1
    test_name = 'CB_ZD_CLI_Get_AAA_Server_By_Name'
    common_name = '%sShow ZD CLI: show aaa name %s' % (gen_id(i), cfg['ad_server']['server_name'])
    param_cfg = dict(server_name = cfg['ad_server']['server_name'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    i += 1
    test_name = 'CB_ZD_CLI_Verify_AAA_Server'
    common_name = '%sVerify ZD CLI: show aaa name %s' % (gen_id(i), cfg['ad_server']['server_name'])
    param_cfg = dict(server_conf = cfg['ad_server'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    
    i += 1
    test_name = 'CB_ZD_CLI_Get_AAA_Server_By_Name'
    common_name = '%sShow ZD CLI: show aaa name %s' % (gen_id(i), cfg['ldap_server']['server_name'])
    param_cfg = dict(server_name = cfg['ldap_server']['server_name'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
    
    i += 1
    test_name = 'CB_ZD_CLI_Verify_AAA_Server'
    common_name = '%sVerify ZD CLI: show aaa name %s' % (gen_id(i), cfg['ldap_server']['server_name'])
    param_cfg = dict(server_conf = cfg['ldap_server'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
     
    
    i += 1
    test_name = 'CB_ZD_CLI_Get_AAA_Server_By_Name'
    common_name = '%sShow ZD CLI: show aaa name %s' % (gen_id(i), cfg['radius_server']['server_name'])
    param_cfg = dict(server_name = cfg['radius_server']['server_name'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))      

    i += 1
    test_name = 'CB_ZD_CLI_Verify_AAA_Server'
    common_name = '%sVerify ZD CLI: show aaa name %s' % (gen_id(i), cfg['radius_server']['server_name'])
    param_cfg = dict(server_conf = cfg['radius_server'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False)) 
    
    i += 1
    test_name = 'CB_ZD_CLI_Get_AAA_Server_By_Name'
    common_name = '%sShow ZD CLI: show aaa name %s' % (gen_id(i), cfg['radius_acc_server']['server_name'])
    param_cfg = dict(server_name = cfg['radius_acc_server']['server_name'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))      

    i += 1
    test_name = 'CB_ZD_CLI_Verify_AAA_Server'
    common_name = '%sVerify ZD CLI: show aaa name %s' % (gen_id(i), cfg['radius_acc_server']['server_name'])
    param_cfg = dict(server_conf = cfg['radius_acc_server'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))     
                  
    i += 1
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = '%sRemove all AAA Servers' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
        
    return test_cfgs


def define_test_paramter():
    cfg = {}
    
    cfg['ad_server'] = {
        'server_name': 'ACTIVE_DIRECTORY',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'rat.ruckuswireless.com',
    }
    
    cfg['ldap_server'] = {
        'server_name': 'LDAP',
        'server_addr':'192.168.0.252',
        'server_port':'389',
        'ldap_search_base':'dc=example,dc=net',
        'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
        'ldap_admin_pwd': 'lab4man1'
    }
   

    cfg['radius_server'] = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.252',
        'radius_auth_secret': '1234567890',
        'server_port': '1812'
    }
    
        
    cfg['radius_acc_server'] = {
        'server_name': 'RADIUS Accounting',
        'server_addr': '192.168.0.252',
        'radius_acct_secret': '1234567890',
        'server_port': '1813'
    }
        
    return cfg


def create_test_suite(**kwargs):
    ts_name = 'TCID: x-Show AAA Server information in CLI'
    ts = testsuite.get_testsuite(ts_name, 'Show AAA Servers information in CLI', combotest=True)
    cfg = define_test_paramter()
    test_cfgs = define_test_configuration(cfg)

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
    