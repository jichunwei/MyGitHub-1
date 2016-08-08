'''
Created on 2011-3-11
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure admin commands in ZD CLI work well.

'''


import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
    
    
def define_admin_cfg_list(ras_name):
    admin_cfg_list = []
    
    admin_cfg_list.append(dict(admin_name = 'zdadmin', 
                               admin_pass = '', 
                               auth_method = 'local', 
                               login_name = 'zdadmin', 
                               login_pass = '',
                               cfg_name = 'Authenticate with Local'
                               ))
    
    admin_cfg_list.append(dict(auth_method = 'external', 
                               auth_server = ras_name, 
                               fallback_local = False, 
                               login_name = 'rad.cisco.user', 
                               login_pass = 'rad.cisco.user',
                               cfg_name = 'Authenticate with Radius Server'
                               ))
    
    admin_cfg_list.append(dict(admin_name = 'zd.admin_123',
                               admin_pass = 'zd.admin_123',
                               auth_method = 'external', 
                               auth_server = ras_name, 
                               fallback_local = True,
                               login_name = 'zd.admin_123',
                               login_pass = 'zd.admin_123',
                               cfg_name = 'Authenticate with Radius Server and Fallback'
                               ))
    
    return admin_cfg_list
    
def define_test_cfg(tcfg):
    test_cfgs = []
   
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create a radius server in ZD GUI'
    test_cfgs.append(({'auth_ser_cfg_list':[tcfg['ras_cfg']]}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_Create_Single_Role'
    common_name = 'Create a role for admin auth in ZD GUI'
    test_cfgs.append(({'role_cfg':tcfg['role_cfg']}, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Backup_Admin_Cfg'
    common_name = 'Backup the admin configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    for admin_cfg in tcfg['admin_cfg_list']:
        test_name = 'CB_ZD_CLI_Configure_Admin'
        common_name = '[%s] Configure admin in ZD CLI' % admin_cfg['cfg_name']
        test_cfgs.append(({'admin_cfg': admin_cfg}, test_name, common_name, 1, False))
    
        test_name = 'CB_ZD_Test_Login'
        common_name = '[%s] Login ZD GUI' % admin_cfg['cfg_name']
        test_cfgs.append(({'login_name': admin_cfg['login_name'], 'login_pass': admin_cfg['login_pass']}, 
                          test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_CLI_Verify_Admin_Cfg_In_GUI'
        common_name = '[%s] Verify admin configuration in ZD GUI' % admin_cfg['cfg_name']
        test_cfgs.append(({'admin_cfg': admin_cfg}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Restore_Admin'
    common_name = 'Restore admin to original configuration in ZD CLI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    ras_cfg = dict(server_addr = ras_ip_addr,
                   server_port = '1812',
                   server_name = ras_ip_addr,
                   radius_auth_secret = '1234567890'
                   )
    
    role_cfg = {"rolename": "Admin Auth Role", 
                "guestpass": False,
                "group_attr": "0123456789", 
                "zd_admin": "full"
    }
    
    admin_cfg_list = define_admin_cfg_list(ras_cfg['server_name'])
    
    tcfg = {'ras_cfg': ras_cfg,
            'role_cfg': role_cfg,
            'ras_user': '',
            'admin_cfg_list': admin_cfg_list,
            }
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "ZD CLI - Configure Administrative Settings"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure admin commands in ZD CLI work well",
                                 combotest=True)
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test cases with test name: %s\n\t\common name: %s" % (testname, common_name)
            
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
    