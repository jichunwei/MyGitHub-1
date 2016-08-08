'''
ZD-35950:Verify LDAP Group Search work correctly with WLAN type is Standard Usage
ZD-35951:Verify LDAP Group Search work correctly with WLAN type is Guest Access
ZD-35952:Verify LDAP Group Search work correctly with WLAN type is Hotspot Service

Case#1
finance.grp, finance.user, ad server:
  1) Create a Role with attribute 'group search', name as myrole
  2) Create AD server
  3) Create a standard WLAN with web auth.
  4) Associate wlan from station
  5) Do authenticate with ad.user/ad.user
  6) Check status from ZD, make sure role of client is Default
  7) Delete Station from ZD
  8) Do authenticate with finance.user/finance.user
  9) Check status from ZD, make sure role of client is myrole

Case#2
finance.grp, finance.user, ldap server:
    1) create a Role with attribute 'group.search', name as my role
    2) Create ad server
    3) Create a guest access profile with ad server
    4) Create a guest access WLAN
    5) Associate wlan from station
    6) Do authenticate with finance.user/finance.user
    7) Check status from ZD, make sure role of client is Default
    8) Delete Station from ZD
    9) Do authenticate with marketing.user/marketing.user
    10) Check status from ZD, make sure role of client is Default

Case#3
marketing.grp, marketing.user, ldap server:
    1) Create a Role with attribute 'group.search', name as my role
    2) Create ldap server
    3) Create a hotspot profile with ldap server
    4) Create WISPr WLAN
    5) Associate wlan from station
    6) Do authenticate with marketing.user/marketing.user
    7) Check status from ZD, make sure role of client is myrole
    8) Delete Station from ZD
    9) Do authenticate with finance.user/finance.user
    10) Check Status from ZD, make sure role of client is Default.  

Created on 2014-2-12
@author: cwang@ruckuswireless.com
'''

import sys
import random
import copy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


ad_cfg = dict(server_name = 'ad_server_2',
              type = 'ad', 
              global_catalog = False, 
              server_addr = '192.168.0.250', 
              win_domain_name = 'rat.ruckuswireless.com')

ldap_cfg = dict(server_name = 'ldap_server_1',                  
                type = 'ldap', 
                server_addr = '192.168.0.252', 
                win_domain_name='dc=example,dc=net',
                admin_domain_name='cn=Manager,dc=example,dc=net',
                admin_password = 'lab4man1'
               )


def build_standard_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Remove all WLANs',
                0,
                False
                ))    
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove All AAA Servers',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Roles',
                'Remove all Roles',
                0,
                False
                ))
    
    tcs.append(({'server_cfg_list':[ldap_cfg]},
                'CB_ZD_CLI_Configure_AAA_Servers',
                'Create AAA Servers',
                0,
                False
                ))
    
    wlan_cfg = dict(ssid='rat_sta_grp_search', 
                    auth="open", 
                    wpa_ver="", 
                    encryption="none", 
                    key_index="", 
                    key_string="",
                    do_webauth=True, 
                    auth_svr = ldap_cfg['server_name'], #Default is local database.                    
                    username="test.ldap.user",
                    password="test.ldap.user",)
        
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_CLI_Create_Wlans',
                'Create WLAN',
                0,
                False
                ))
        
    role_cfg = {"role_name": "myrole",                  
                "allow_all_wlans": True,                 
                "guest_pass_gen": True, 
                "description": "",
                "group_attr": "ruckus", 
                "allow_zd_admin": None,}
    
    tcs.append(({'role_cfg_list':[role_cfg]},
                'CB_ZD_CLI_Configure_Roles',
                'Configure Roles',
                0,
                False
                )) 
        
    
    tcs.append(({'sta_ip_addr':'192.168.1.11',
                       'sta_tag': 'sta1'}, 
                       'CB_ZD_Create_Station', 
                       'Create target station', 
                       0, 
                       False))
    
    tcs.append(({'wlan_cfg':wlan_cfg,
                 'sta_tag':'sta1'},
                'CB_ZD_Associate_Station_1',
                'Associate WLAN',
                0,
                False
                ))
    
    tcs.append(({'sta_tag': 'sta1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'get wifi address of station', 
                      0,
                      False))
    
    tcid = "Verify LDAP Group Search with Standard WLAN with role group.search"        
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Start_Browser',
                '[%s]Start Browser' % tcid,
                1,
                False
                ))    
        
    tcs.append(({'sta_tag':'sta1',
                 'username':wlan_cfg['username'],
                 'password':wlan_cfg['password']
                 },
                'CB_Station_CaptivePortal_Perform_WebAuth',
                '[%s]Do web auth' % tcid,
                2,
                False
                ))
    
    tcs.append(({'username':wlan_cfg['username'],
                 'wlan_cfg':wlan_cfg,
                 'role':'myrole',
                 'status': 'authorized',
                 'sta_tag':'sta1'
                 },
                'CB_ZD_Verify_Station_Info_V2',
                '[%s]Check Station information' % tcid, 
                2,
                False
                ))
    
    tcs.append(({},
                'CB_Station_CaptivePortal_Quit_Browser',
                '[%s]Quit browser' % tcid, 
                2,
                True
                ))
    
    
    
    tcid = "Verify ldap Group Search with Standard WLAN and default role"
    tcs.append(({'sta_tag':'sta1',
                 'test_policy':'web authentication',
                 'status':'Unauthorized',
                 'wlan_cfg':wlan_cfg
                 },
                'CB_ZD_Delete_Active_Client',
                '[%s]Delete Active Client' % tcid,
                1,
                False
                ))
    
    tcs.append(({},
                'CB_Station_CaptivePortal_Start_Browser',
                '[%s]Start Browser' % tcid,
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1',
                 'username':'my.ldap.user',
                 'password':'my.ldap.user'
                 },
                'CB_Station_CaptivePortal_Perform_WebAuth',
                '[%s]Do web auth' % tcid,
                2,
                False
                ))
    
    tcs.append(({'username':'my.ldap.user',
                 'wlan_cfg':wlan_cfg,
                 'role':'Default',
                 'sta_tag':'sta1'
                 },
                'CB_ZD_Verify_Station_Info_V2',
                '[%s]Check Station information' % tcid, 
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Quit_Browser',
                '[%s]Quit browser' % tcid, 
                2,
                True
                ))    
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Delete wlans',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Roles',
                'Delete Roles',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Delete AAA Servers',
                0,
                True
                ))
    
    return tcs
    

def build_wispr_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Remove all WLANs',
                0,
                False
                ))
    
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove All AAA Servers',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Roles',
                'Remove all Roles',
                0,
                False
                ))
    
    tcs.append(({'server_cfg_list':[ad_cfg]},
                'CB_ZD_CLI_Configure_AAA_Servers',
                'Create AAA Servers',
                0,
                False
                ))
    
    tcs.append(({"hotspot_conf":{'name': 'Test_Hotspot_CLI',
                 'login_page_url': 'http://192.168.0.250/login.html',
                 'authentication_server':ad_cfg['server_name'],
                 'server_type':'ad'
                 }
                 },
                'CB_ZD_CLI_Configure_Hotspot',
                'Configure Hotspot with AAA server',
                0,
                False
                ))
    
    wlan_cfg = dict(ssid='rat_hotspot_grp_search', 
                    auth="open", 
                    wpa_ver="", 
                    encryption="none", 
                    key_index="", 
                    key_string="",
                    hotspot_profile='Test_Hotspot_CLI', 
                    auth_svr = ad_cfg['server_name'], #Default is local database.                    
                    username="finance.user",
                    password="finance.user",
                    type='hotspot'
                    )
    
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_CLI_Create_Wlans',
                'Create WLAN',
                0,
                False
                ))
    
    role_cfg = {"role_name": "myrole",                  
                "allow_all_wlans": True,                 
                "guest_pass_gen": True, 
                "description": "",
                "group_attr": "finance.grp", 
                "allow_zd_admin": None,}
        
    tcs.append(({'role_cfg_list':[role_cfg]},
                'CB_ZD_CLI_Configure_Roles',
                'Configure Roles',
                0,
                False
                ))  
    
    tcs.append(({'sta_ip_addr':'192.168.1.11',
                       'sta_tag': 'sta1'}, 
                       'CB_ZD_Create_Station', 
                       'Create target station', 
                       0, 
                       False))
    
    
    tcs.append(({'wlan_cfg':wlan_cfg,
                 'sta_tag':'sta1',                 
                 },
                'CB_ZD_Associate_Station_1',
                'Associate WLAN',
                0,
                False
                ))
    
    tcs.append(({'sta_tag': 'sta1'}, 
                      'CB_ZD_Get_Station_Wifi_Addr_1', 
                      'get wifi address of station', 
                      0,
                      False))
    
    tcid = "Verify LDAP Group Search with WISPr with role group.search"    
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Start_Browser',
                '[%s]Start Browser' % tcid,
                1,
                False
                ))    
    
    tcs.append(({'sta_tag':'sta1',
                 'username':wlan_cfg['username'],
                 'password':wlan_cfg['password']
                 },
                'CB_Station_CaptivePortal_Perform_HotspotAuth',
                '[%s]Do web auth' % tcid,
                2,
                False
                ))
    
    tcs.append(({'username':wlan_cfg['username'],
                 'wlan_cfg':wlan_cfg,
                 'role':'myrole',
                 'status': 'authorized',
                 'sta_tag':'sta1'
                 },
                'CB_ZD_Verify_Station_Info_V2',
                '[%s]Check Station information' % tcid, 
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Quit_Browser',
                '[%s]Quit browser' % tcid, 
                2,
                True
                ))
    
    
    
    tcid = "Verify AD Group Search with WISPr and default role"
    tcs.append(({'sta_tag':'sta1',
                 'test_policy':'hotspot authentication',
                 'username':wlan_cfg['username'],
                 'status':'Unauthorized',
                 'wlan_cfg':wlan_cfg
                 },
                'CB_ZD_Delete_Active_Client',
                '[%s]Delete Active Client' % tcid,
                1,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Start_Browser',
                '[%s]Start Browser' % tcid,
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1',
                 'username':'marketing.user',
                 'password':'marketing.user'
                 },
                'CB_Station_CaptivePortal_Perform_HotspotAuth',
                '[%s]Do web auth' % tcid,
                2,
                False
                ))
    
    tcs.append(({'username':'marketing.user',
                 'wlan_cfg':wlan_cfg,
                 'role':'Default',
                 'status': 'authorized',
                 'sta_tag':'sta1'
                 },
                'CB_ZD_Verify_Station_Info_V2',
                '[%s]Check Station information' % tcid, 
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Quit_Browser',
                '[%s]Quit browser' % tcid, 
                2,
                True
                ))    
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Delete wlans',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Roles',
                'Delete Roles',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Hotspot_Profiles',
                'Delete profiles',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Delete AAA Servers',
                0,
                True
                ))
    
    return tcs


def build_guest_access_tcs():
    tcs = []
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Remove all WLANs',
                0,
                False
                ))
    
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove All AAA Servers',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Roles',
                'Remove all Roles',
                0,
                False
                ))
    
    tcs.append(({'server_cfg_list':[ldap_cfg]},
                'CB_ZD_CLI_Configure_AAA_Servers',
                'Create AAA Servers',
                0,
                False
                ))
    
    gcfg = {'use_guestpass_auth':True,                               
            'use_tou':False,
            'redirect_url' : 'http://172.16.10.252',            
            }
    
    tcs.append((gcfg,
                'CB_ZD_Create_GuestAccess_Policy',
                'Configure Guest Access',
                0,
                False
                ))
    
    gpcfg = {'auth_serv':ldap_cfg['server_name']}
    tcs.append((gpcfg,
                'CB_ZD_Set_GuestPass_Policy',
                'Update Guest Pass Policy',
                0,
                False
                ))
    
    
    wlan_cfg = dict(ssid='rat_guest_grp_search', 
                    auth="open", 
                    wpa_ver="", 
                    encryption="none", 
                    key_index="", 
                    key_string="",                                        
                    username="test.ldap.user",
                    password="test.ldap.user",
                    type='guest-access'
                    )             
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_CLI_Create_Wlans',
                'Create WLAN',
                0,
                False
                ))
    
    role_cfg = {"role_name": "myrole",                  
                "allow_all_wlans": True,                 
                "guest_pass_gen": True, 
                "description": "",
                "group_attr": "ruckus", 
                "allow_zd_admin": None,}
        
    tcs.append(({'role_cfg_list':[role_cfg]},
                'CB_ZD_CLI_Configure_Roles',
                'Configure Roles',
                0,
                False
                ))
    
    
    tcs.append(({'sta_ip_addr':'192.168.1.11',
                       'sta_tag': 'sta1'}, 
                       'CB_ZD_Create_Station', 
                       'Create target station', 
                       0, 
                       False))
    
    
    tcs.append(({'wlan_cfg':wlan_cfg,
                 'sta_tag':'sta1'},
                'CB_ZD_Associate_Station_1',
                'Associate WLAN',
                0,
                False
                ))
    
    
    tcs.append(({'sta_tag': 'sta1'}, 
                  'CB_ZD_Get_Station_Wifi_Addr_1', 
                  'get WIFI address of station', 
                  0,
                  False))  
    
    tcid = "Verify LDAP Group Search with Guest Access with role group.search"    
    gscfg = {'type':'single',
             'guest_fullname':'mytest',             
             'wlan': wlan_cfg['ssid'],                                     
             'auth_ser': ldap_cfg['server_name'],
             'username': wlan_cfg['username'],
             'password': wlan_cfg['password']}
    
    tcs.append((gscfg,
                'CB_ZD_Generate_Guest_Pass',
                '[%s]Generate Guest Pass' % tcid,
                1,
                False
                ))
        
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Start_Browser',
                '[%s]Start Browser' % tcid,
                2,
                False
                ))
    
    
    tcs.append(({'sta_tag':'sta1',
                 'use_tou':False,
                 'redirect_url':'http://172.16.10.252/'
                 },
                'CB_Station_CaptivePortal_Perform_GuestAuth',
                '[%s]Do web auth' % tcid,
                2,
                False
                ))
    
    tcs.append(({'username':wlan_cfg['username'],
                 'wlan_cfg':wlan_cfg,
                 'role':'myrole',
                 'status': 'authorized',
                 'sta_tag':'sta1',
                 'use_guestpass_auth':True,
                 'guest_name':'mytest'
                 },
                'CB_ZD_Verify_Station_Info_V2',
                '[%s]Check Station information' % tcid, 
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Quit_Browser',
                '[%s]Quit browser' % tcid, 
                2,
                True
                ))
    
    tcid = "Verify AD Group Search with Guest Access and default role"
    tcs.append(({'sta_tag':'sta1',
                 'test_policy':'guest access',
                 'use_guestpass_auth':True,
                 'guest_name':'mytest',
                 'status':'Unauthorized',
                 'wlan_cfg':wlan_cfg            
                 },
                'CB_ZD_Delete_Active_Client',
                '[%s]Delete Active Client' % tcid,
                1,
                False
                ))
    

    gscfg = {'type':'single',
             'guest_fullname':'mytest',             
             'wlan': wlan_cfg['ssid'],                                     
             'auth_ser': ldap_cfg['server_name'],
             'username': 'my.ldap.user',
             'password': 'my.ldap.user'}
    
    tcs.append((gscfg,
                'CB_ZD_Generate_Guest_Pass',
                '[%s]Generate Guest Pass' % tcid,
                2,
                False
                ))  
      
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Start_Browser',
                '[%s]Start Browser' % tcid,
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1',
                 'use_tou':False,
                 'redirect_url':'http://172.16.10.252/'
                 },
                'CB_Station_CaptivePortal_Perform_GuestAuth',
                '[%s]Do web auth' % tcid,
                2,
                False
                ))
    
    tcs.append(({'username':'my.ldap.user',
                 'wlan_cfg':wlan_cfg,
                 'role':'Default',
                 'status': 'authorized',
                 'sta_tag':'sta1',
                 'use_guestpass_auth':True,
                 'guest_name':'mytest'
                 },
                'CB_ZD_Verify_Station_Info_V2',
                '[%s]Check Station information' % tcid, 
                2,
                False
                ))
    
    tcs.append(({'sta_tag':'sta1'},
                'CB_Station_CaptivePortal_Quit_Browser',
                '[%s]Quit browser' % tcid, 
                2,
                True
                ))    
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Delete wlans',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Remove_All_Roles',
                'Delete Roles',
                0,
                True
                ))
    
    
    tcs.append(({'auth_serv':'Local Database'},
                'CB_ZD_Set_GuestPass_Policy',
                'Update Guest Pass Policy to Default',
                0,
                True))
    
    
    tcs.append(({},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Delete AAA Servers',
                0,
                True
                ))
    
    return tcs



def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "GroupSearchAttribute-Functionalities",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    
    ts_name_list = [
                    ('AD or LDAP group search with webauth',build_standard_tcs),
                    ('AD or LDAP group search with wispr',build_wispr_tcs),
                    ('AD or LDAP group search with guest',build_guest_access_tcs),                   
                    ]
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)          
        test_cfgs = fn()
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
            
def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    # _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)