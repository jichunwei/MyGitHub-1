'''
Created on 2011-3-18
@author: serena.tan@ruckuswireless.com

Description: This test suite is used to verify whether the configure role commands in ZD CLI work well.

'''


import time
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_wlan_cfg_list(user_cfg):
    wlan_cfg_list = []
    
    wlan_cfg_list.append(dict(ssid = "guest-access-wlan-%s" % time.strftime("%H%M%S"), 
                              type = 'guest', auth = "open", 
                              wpa_ver = "", encryption = "none", 
                              key_index = "" , key_string = "",
                              username = user_cfg["username"], 
                              password = user_cfg["password"]))
    
    wlan_cfg_list.append(dict(ssid = "EAP-wlan-%s" % time.strftime("%H%M%S"), 
                              type = 'standard', auth = "EAP", 
                              wpa_ver = "WPA2", encryption = "AES",
                              #@author: Liang Aihua,@change: WPA/TKIP not support any more.
                              #wpa_ver = "WPA", encryption = "TKIP",
                              key_index = "" , key_string = "",
                              username = user_cfg["username"], 
                              password = user_cfg["password"]))
    
    return wlan_cfg_list
    
    
def define_role_cfg_list(wlan_cfg_list):
    role_cfg_list = []
    
    role_cfg_list.append(dict(role_name = 'rat_role_init', 
                              new_role_name = 'rat_role',
                              description = 'Role For ZD CLI Test',
                              group_attr = '0123456789',
                              tcid = '[Edit name, description and group attributes]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              guest_pass_gen = True,
                              #@author: liang aihua,@since: 2015-5-15,@change: if no wlan selected, guest pass can't get.
                              allow_all_wlans = True, 
                              tcid = '[Allow guest pass generate]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              guest_pass_gen = False, 
                              tcid = '[Disallow guest pass generate]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              allow_all_wlans = False, 
                              specify_wlan_list = [wlan_cfg_list[1]['ssid']], 
                              tcid = '[Add specify WLAN]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              allow_all_wlans = False, 
                              specify_wlan_list = [], 
                              tcid = '[Delete all specify WLAN]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              allow_all_wlans = True, 
                              tcid = '[Allow access to all WLANs]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role', 
                              allow_zd_admin = True, 
                              zd_admin_mode = 'super',
                              tcid = '[Allow ZD admin as super]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              allow_zd_admin = True, 
                              zd_admin_mode = 'operator',
                              tcid = '[Allow ZD admin as operator]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              allow_zd_admin = True, 
                              zd_admin_mode = 'monitoring',
                              tcid = '[Allow ZD admin as monitoring]'))
    
    role_cfg_list.append(dict(role_name = 'rat_role',
                              description = '',
                              group_attr = '',
                              allow_zd_admin = False, 
                              tcid = '[Disallow ZD admin]'))
    
    return role_cfg_list

    
def define_test_cfg(tcfg):
    sta_tag = tcfg['sta_ip_addr']
    test_cfgs = []  
  
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create the target station'
    test_params = {'sta_tag': sta_tag, 'sta_ip_addr': tcfg['sta_ip_addr']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in the station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD GUI before test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
  
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create wlans in ZD GUI'
    test_cfgs.append(({'wlan_cfg_list': tcfg['wlan_cfg_list']}, 
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create a local user in ZD GUI'
    test_cfgs.append((tcfg['user_cfg'], test_name, common_name, 0, False))  
    
    
    tcid = tcfg['role_cfg_list'][0]['tcid']
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = '%s Create a role in ZD CLI' % tcid
    test_cfgs.append(({'role_cfg_list': [tcfg['role_cfg_list'][0]]}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Get_Roles_Cfg'
    common_name = '%s Get the role info from ZD GUI' % tcid
    test_cfgs.append(({'role_name_list': [tcfg['role_cfg_list'][0]['new_role_name']]}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Roles_Cfg_In_GUI'
    common_name = '%s Verify the role info in ZD GUI' % tcid
    test_cfgs.append(({'role_cfg_list': [tcfg['role_cfg_list'][0]]}, 
                      test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Edit_User'
    common_name = '%s Assign the role to local user in ZD GUI' % tcid
    test_cfgs.append(({'old_name': tcfg['user_cfg']['username'], 
                       'cfg': {'role': tcfg['role_cfg_list'][0]['new_role_name']}},
                       test_name, common_name, 0, False))     
    
    
    for i in range(1, len(tcfg['role_cfg_list'])):
        tcid = tcfg['role_cfg_list'][i]['tcid']
    
        test_name = 'CB_ZD_CLI_Configure_Roles'
        common_name = '%s Edit the existing role in ZD CLI' % tcid
        test_cfgs.append(({'role_cfg_list': [tcfg['role_cfg_list'][i]]}, 
                          test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Get_Roles_Cfg'
        common_name = '%s Get the role info from ZD GUI' % tcid
        test_cfgs.append(({'role_name_list': [tcfg['role_cfg_list'][i]['role_name']]}, 
                          test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_CLI_Verify_Roles_Cfg_In_GUI'
        common_name = '%s Verify the role info in ZD GUI' % tcid
        test_cfgs.append(({'role_cfg_list': [tcfg['role_cfg_list'][i]]}, 
                          test_name, common_name, 2, False))
    
        if i == 1 or i == 2:
            test_name = 'CB_ZD_Test_Guest_Pass_Generate'
            common_name = '%s Test guest pass generate' % tcid
            test_cfgs.append(({'username': tcfg['user_cfg']['username'], 
                               'password': tcfg['user_cfg']['password'], 
                               'guess_db': 'Local Database', 
                               'allow': tcfg['role_cfg_list'][i]['guest_pass_gen']}, 
                               test_name, common_name, 2, False))   
       
        elif i == 3 or i == 5:
            test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
            common_name = '%s Station associate the wlan and get wifi address' % tcid
            test_cfgs.append(({'wlan_cfg': tcfg['wlan_cfg_list'][1], 'sta_tag': sta_tag}, 
                              test_name, common_name, 2, False))
            
            #test_name = 'CB_Station_CaptivePortal_Download_File'
            #common_name = '%s Station download file from web server' % tcid
            #test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
        elif i == 4:
            test_name = 'CB_Station_Remove_All_Wlans'
            common_name = '%s Remove all wlans from station' % tcid
            test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
            
            test_name = 'CB_ZD_Test_WLAN_Access_Deny'
            common_name = '%s Test station can not associate the wlan' % tcid   
            test_cfgs.append(({'wlan_cfg': tcfg['wlan_cfg_list'][1], 'sta_tag': sta_tag}, 
                              test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Close browser in the station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all roles from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        station = 0,
        testsuite_name=""
    )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs["interactive_mode"]:
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list)
        
    else:
        sta_ip_addr = sta_ip_list[attrs["station"]]

    user_cfg = {'username': 'username', 
                'password': 'userpass'}
    
    wlan_cfg_list = define_wlan_cfg_list(user_cfg)
    role_cfg_list = define_role_cfg_list(wlan_cfg_list) 
    
    guest_access_cfg = {'use_guestpass_auth': True, 
                        'use_tou': True , 
                        'redirect_url': 'http://172.16.10.252/',
                        'target_url': 'http://www.example.net/'
                        }
     
    tcfg = {'wlan_cfg_list': wlan_cfg_list,
            'role_cfg_list': role_cfg_list,
            'user_cfg': user_cfg,
            'sta_ip_addr': sta_ip_addr,
            'guest_access_cfg': guest_access_cfg
            }
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else: 
        ts_name = "ZD CLI - Configure Role"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the configure role commands in ZD CLI work well",
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
    