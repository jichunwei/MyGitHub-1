'''
Created on 2010-12-23
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure user commands in ZD CLI work well.

'''


import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
   
   
def define_user_cfg_list(rolename):
    user_cfg_list = []
    user_cfg_list.append(dict(name = 'rat_user_0', 
                              fullname = 'zdcli test user',
                              role = 'Default', 
                              password = 'abcd'
                              ))
    
    user_cfg_list.append(dict(user = 'rat_user_0', 
                              name = 'rat_user_1', 
                              fullname = 'new zdcli test user', 
                              role = rolename, 
                              password = 'abcd01234'
                              ))
      
    return user_cfg_list


def define_test_cfg(tcfg):
    test_cfgs = []
   
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Single_Role'
    common_name = 'Create a role in ZD GUI'
    test_cfgs.append(({'role_cfg': tcfg['role_cfg']}, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_CLI_Create_Users'
    common_name = '[Create a User with Default Role] Create a user in ZD CLI'
    test_cfgs.append((tcfg['user_cfg_list'][0], test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_User_By_Name'
    common_name = '[Create a User with Default Role] Get the user info from ZD GUI'   
    test_cfgs.append(({'name': tcfg['user_cfg_list'][0]['name']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_User_Cfg_In_GUI'
    common_name = '[Create a User with Default Role] Verify the user cfg in ZD GUI'   
    test_cfgs.append(({'user_cfg': tcfg['user_cfg_list'][0]}, test_name, common_name, 2, False))


    test_name = 'CB_ZD_CLI_Edit_User'
    common_name = '[Edit the Existing User] Edit the existing user in ZD CLI'
    test_cfgs.append((tcfg['user_cfg_list'][1], test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_User_By_Name'
    common_name = '[Edit the Existing User] Get the user info from ZD GUI'   
    test_cfgs.append(({'name': tcfg['user_cfg_list'][1]['name']}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Verify_User_Cfg_In_GUI'
    common_name = '[Edit the Existing User] Verify the user cfg in ZD GUI'   
    test_cfgs.append(({'user_cfg': tcfg['user_cfg_list'][1]}, test_name, common_name, 2, False))  

    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)
    
    role_cfg = {"rolename": "rat_role",
                "guestpass": False, 
                }
    
    user_cfg_list = define_user_cfg_list(role_cfg['rolename'])
    
    tcfg = {'role_cfg': role_cfg,
            'user_cfg_list': user_cfg_list}
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "ZD CLI - Configure User" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure user commands in ZD CLI work well",
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
    