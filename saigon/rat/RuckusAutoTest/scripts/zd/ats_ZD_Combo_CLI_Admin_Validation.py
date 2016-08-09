'''
Description: 
    Show admin information on ZD CLI, verify the information on ZD GUI.
    By Chris
    cwang@ruckuswireless.com
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def gen_id(id):
    ex_id = "[Admin info configure from GUI, check from CLI]"
    return '%s(%d) ' % (ex_id, id)

def define_test_configuration(cfg):
    test_cfgs = []
    i = 1     
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = '%sRemove AAA Servers from GUI' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1
    auth_ser_cfg_list = [cfg['ad_server']]
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '%sCreate Authentication Servers' % gen_id(i)
    param_cfg = dict(auth_ser_cfg_list = auth_ser_cfg_list)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
        
    i += 1        
    test_name = 'CB_ZD_Set_Admin_Info'
    common_name = '%sSet external admin information' % gen_id(i)
    param_cfg = dict(cfg['external_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    i += 1    
    test_name = 'CB_ZD_CLI_Get_Admin_Info'
    common_name = '%sGet admin info' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    i += 1
    test_name = 'CB_ZD_CLI_Verify_Admin_Info'
    common_name = '%sVerify admin info ' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  
       
    
    i += 1    
    test_name = 'CB_ZD_Set_Admin_Info'
    common_name = '%sSet local admin info' % gen_id(i)
    param_cfg = dict(cfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    i += 1
    test_name = 'CB_ZD_CLI_Get_Admin_Info'
    common_name = '%slocal admin info' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    

    i += 1
    test_name = 'CB_ZD_CLI_Verify_Admin_Info'
    common_name = '%sChecking local admin info' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    i += 1
    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = '%sRemove AAA Servers from GUI' % gen_id(i)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))         
    
    return test_cfgs


def define_test_paramter():
    cfg = {}   

    cfg['ad_server'] = {
        'server_name': 'ACTIVE_DIRECTORY',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'rat.ruckuswireless.com',
    }
    
    cfg['local_admin'] = dict(auth_method = 'local',
         admin_name = 'admin',
         admin_old_pass = 'admin',
         admin_pass1 = 'admin',
         admin_pass2 = 'admin'
        )
   
    cfg['external_admin'] = dict(auth_method = 'external',
         admin_name = 'admin',
         admin_old_pass = 'admin',
         admin_pass1 = 'admin',
         admin_pass2 = 'admin',
         fallback_local = True,
         auth_server = cfg['ad_server']['server_name']
    )    
    
          
    return cfg


def create_test_suite(**kwargs):
    ts_name = 'TCID: x-Show admin information in CLI'
    ts = testsuite.get_testsuite(ts_name, 'Show admin information in CLI', combotest=True)
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
    