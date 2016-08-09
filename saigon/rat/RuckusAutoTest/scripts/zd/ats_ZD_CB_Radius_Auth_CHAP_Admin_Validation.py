'''
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration(cfg):
    test_cfgs = []

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove AAA Servers from GUI before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all roles from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    auth_ser_cfg_list = [cfg['radius_server']]
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '[Auth by Radius CHAP]Create Authentication Servers'
    param_cfg = dict(auth_ser_cfg_list = auth_ser_cfg_list)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))  

    test_name = 'CB_ZD_Verify_Radius_Server_Auth_Method'
    common_name = '[Auth by Radius CHAP]Test Radius Authentication Server'
    param_cfg = {'server_name': cfg['radius_server']['server_name'], 
                 'user': cfg['radius_server']['username'], 'password':cfg['radius_server']['password'], 
                 'invalid_user': 'rad.cisco', 'invalid_password':'rad.cisco',
                 'radius_auth_method': cfg['radius_server']['radius_auth_method'],}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))                        
   
    test_name = 'CB_ZD_Create_Single_Role'
    common_name = '[Auth by Radius CHAP]Create a role for admin auth in ZD GUI'
    test_cfgs.append(({'role_cfg':cfg['role_cfg']}, test_name, common_name, 2, False)) 

    test_name = 'CB_ZD_Set_Admin_Info'
    common_name = '[Auth by Radius CHAP]Set external admin information'
    param_cfg = dict(cfg['external_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Test_Login'
    common_name = '[Auth by Radius CHAP]Login ZD GUI by radius user password'
    param_cfg = {'login_name': cfg['radius_server']['username'], 'login_pass': cfg['radius_server']['password']}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))

    test_name = 'CB_ZD_Set_Admin_Info'
    common_name = '[Auth by Radius CHAP]Set original local admin information'
    param_cfg = dict(cfg['local_admin'])
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  

    test_name = 'CB_ZD_Test_Login'
    common_name = '[Auth by Radius CHAP] Login ZD GUI by original user password'
    param_cfg = {'login_name': cfg['local_admin']['admin_name'], 'login_pass': cfg['local_admin']['admin_pass1']}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove AAA Servers from GUI at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))         

    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all roles from ZD GUI after test at last'   
    test_cfgs.append(({}, test_name, common_name, 0, True))
                
    return test_cfgs


def define_test_paramter():
    cfg = {}   

    ras_name = 'ruckus-radius-%s' % (time.strftime("%H%M%S"),)

    cfg['radius_server'] = {'server_addr': '192.168.0.252',
                        'server_port' : '1812',
                        'server_name' : ras_name,
                        'radius_auth_secret': '1234567890',
                        'radius_auth_method': 'chap',
                        'username': 'rad.cisco.user',
                        'password': 'rad.cisco.user',
                        }

    cfg['role_cfg'] = {"rolename": "AdminAuthRole", 
                "guestpass": False,
                "group_attr": "0123456789", 
                "zd_admin": "full"
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
         auth_server = cfg['radius_server']['server_name'],
    )    
          
    return cfg


def create_test_suite(**kwargs):
    ts_name = 'Admin Validation - Radius Auth CHAP'
    ts = testsuite.get_testsuite(ts_name, 'Administrtor Name authenticated by Radius CHAP method', combotest=True)
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
    