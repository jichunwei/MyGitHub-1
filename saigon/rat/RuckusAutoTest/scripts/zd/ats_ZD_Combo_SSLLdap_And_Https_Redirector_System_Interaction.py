"""
Verify ldap over ssl and https redirector system interaction.

    Pre-condition:
       AP joins ZD1
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) import trusted CA to ZD
        2) create ldap server enable ldap ssl
        3) case1:[Authenticate with sslldap]
        4) case2:[role with sslldap group]
        5) case3:[factory and restore with sslldap]
        6) case4:[sslldap with unknow CA]
        7) case5:[zero-IT with sslldap]
        
    ps: CA needs manual generate. validity 365days. 
        save to TE: d:/CA/my-ca-ipv4-right.crt  
                    d:/CA/my-ca-error.crt
    
Created on 2014-10-28
@author: Yu.yanan@odc-ruckuswireless.com
"""

import sys
import random
from random import randint
import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as constant

def define_test_cfg(cfg):
 
    test_cfgs = [] 
    idx = 0
    
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove all Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove all aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create Ldap server enable ssl'
    test_cfgs.append(({'server_cfg_list':[{'grp_search': True, 'server_name': 'SSLLDAP_Server', 'win_domain_name':'dc=example,dc=net','admin_domain_name': 'cn=Manager,dc=example,dc=net','admin_password': 'lab4man1', 'server_port': '636', 'grp-search': True, 'type': 'ldap', 'server_addr': '192.168.0.252','ldap_encryption':True}]}, test_name, common_name, 0, False))  
   
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_sta'],
                       'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = 'create wlan with hotspot'
    test_cfgs.append(({'wlan_conf':cfg['hotspot_wlan_with_sslldap_cfg']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = 'Create a role for ldap'
    test_cfgs.append(({'role_cfg_list':cfg['role_cfg_list']}, test_name, common_name, 0, False))
      
    #****************************************case 1 ***************************************************
    
    tc_common_name = "Authenticate with sslldap"
    
    idx += 1
    step = 0
    
    test_name = 'CB_ZD_Backup_Admin_Cfg'
    step += 1
    common_name = '[%s]%s.%sBackup the admin configuration'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Configure_Admin'
    step += 1
    common_name = '[%s]%s.%sConfigure administer with ldap user in ZD CLI' % (tc_common_name, idx, step)
    test_cfgs.append(({'admin_cfg': cfg['admin_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Test_Login'
    step += 1
    common_name = '[%s]%s.%sLogin ZD GUI' %  (tc_common_name, idx, step)
    test_cfgs.append(({'login_name':cfg['admin_cfg']['login_name'], 'login_pass': cfg['admin_cfg']['login_pass']}, 
                          test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Admin_Cfg_In_GUI'
    step += 1
    common_name = '[%s]%s.%sVerify administer with ldap user configuration in ZD GUI' %  (tc_common_name, idx, step)
    test_cfgs.append(({'admin_cfg': cfg['admin_cfg']}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_CLI_Restore_Admin'
    step += 1
    common_name = '[%s]%s.%sRestore admin to original configuration in ZD CLI'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    #****************************************case 2 ***************************************************
    tc_common_name = "role with sslldap group"
    idx +=1
    step = 0
    
    for count in range(0,2):
    
        if count == 0:
            test_name = 'CB_ZD_Associate_Station_1'
            step += 1
            common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
            test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg']}, test_name, common_name, 1, False))
        else:
            test_name = 'CB_ZD_Associate_Station_1'
            step += 1
            common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
            test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg']}, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
        step += 1
        common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    
        test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
        step += 1
        common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','original_url': 'https://172.16.10.252/', 
                       'username': 'test.ldap.user', 'close_browser_after_auth': True, 'password': 'test.ldap.user', 'start_browser_before_auth': True}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        step += 1
        common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','username':'test.ldap.user','wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg'],'status': 'Authorized','role':'myrole'}, test_name, common_name, 2, False))
   
        test_name = 'CB_ZD_Client_Ping_Dest'
        step += 1
        common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
        if count == 0:
            test_name = 'CB_ZD_CLI_Reboot_ZD'
            step += 1
            common_name = '[%s]%s.%sReboot ZD from CLI'% (tc_common_name, idx, step)
            test_cfgs.append(( {}, test_name, common_name, 2, False))
      
    #****************************************case 3 ***************************************************
    tc_common_name = "factory and restore with sslldap"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_Backup'
    step += 1
    common_name = '[%s]%s.%s backup zd configuration' % (tc_common_name,idx, step)
    test_cfgs.append(({'wlan_conf':cfg['hotspot_wlan_with_sslldap_cfg'],'save_to':constant.save_to}, test_name, common_name, 0, False))
  
    
    test_name = 'CB_ZD_Set_Factory_Default'
    step += 1
    common_name = '[%s]%s.%s zd set factory' % (tc_common_name,idx, step)
    test_cfgs.append(({'relogin_zdcli':False,'sta_tag': 'sta_1','wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg']}, test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s verify station disconnect wlan' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','expected_failed': True,'wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Restore'
    step += 1
    common_name = '[%s]%s.%s zd restore configuration' % (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','original_url': 'https://172.16.10.252/', 
                       'username': 'test.ldap.user', 'close_browser_after_auth': True, 'password': 'test.ldap.user', 'start_browser_before_auth': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','username':'test.ldap.user','wlan_cfg': cfg['hotspot_wlan_with_sslldap_cfg'],'status': 'Authorized','role':'myrole'}, test_name, common_name, 2, False))
  
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    #****************************************case 4 ***************************************************
    
    tc_common_name = "zeroIT with sslldap"
    idx +=1
    step = 0
    
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    step += 1
    common_name = '[%s]%s.%s set sslldap server for zeroIT'%(tc_common_name, idx, step)
    test_cfgs.append(({'zero_it_auth_serv':'SSLLDAP_Server' }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%s create WLAN with stand-open' % (tc_common_name,idx, step)
    test_cfgs.append(({'wlan_conf':cfg['stand_open_wlan']}, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Station_Config_Wlan_With_ZeroIT'
    step += 1
    common_name = '[%s]%s.%s station connect wlan' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'wlan_cfg': {'username': 'test.ldap.user', 'password': 'test.ldap.user', 'use_radius': None, 'ssid': cfg['stand_open_wlan']['ssid'], 'auth': 'open'}}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify station status in zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['stand_open_wlan'],'status': 'Authorized'}, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    step += 1
    common_name = '[%s]%s.%s restore localDatabase for zeroIT'%(tc_common_name, idx, step)
    test_cfgs.append(({'zero_it_auth_serv':'Local Database' }, test_name, common_name, 2, True))
    #****************************************clean up**************************************************
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove the WLAN from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    step += 1
    common_name = 'Remove hotspot profile from ZDCLI'
    test_cfgs.append(({'cleanup':True,'hotspot_conf':{'name':'Hotsport_Default'}}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = 'Remove Roles from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, True))    

    return test_cfgs

def gen_random_int():
    return randint(1,10000)
    
    
def define_test_parameters(tbcfg):

    username = 'test.ldap.user'
    password = 'test.ldap.user'
    servername = 'SSLLDAP_Server'
    rand_num = gen_random_int()
    
    hotspot_name ='Hotsport_Default'
    hotspot_wlan_name = 'sslldap-https-hotspot'+str(rand_num)
    stand_open_wlan_name = 'stand-open-none'+str(rand_num)
    
    role_cfg_list= [{'description': '', 
                      'group_attr': 'ruckus', 
                      'guest_pass_gen': True, 
                      'role_name': 'myrole', 
                      'allow_all_wlans': True, 
                       'zd_admin_mode':'super',
                      'allow_zd_admin': True,
                      }]
    
    admin_cfg = dict(auth_method = 'external', 
                     auth_server = servername, 
                     fallback_local = True, 
                     login_name = username, 
                     login_pass =password,
                     admin_name='admin', 
                     admin_pass='admin',
                    )
                                                
    hotspot_with_sslldap_conf = {'name': hotspot_name, 
                    'start_page': '', 
                    'authentication_server':servername, 
                    'accounting_server': 'Disabled', 
                    'login_page_url':'http://192.168.0.250/login.html'}
    
    hotspot_wlan_with_sslldap_cfg = {'name' : hotspot_wlan_name,
                        'ssid': hotspot_wlan_name,
                        'auth': 'open',
                        'encryption' :'none',
                        'type':'hotspot', 
                        'hotspot_service': hotspot_with_sslldap_conf,
                        }
    stand_open_wlan = {'name' : stand_open_wlan_name,
                        'ssid': stand_open_wlan_name,
                        'auth': 'open',
                        'encryption' :'none',
                        'zero_it': True,
                       }
    
    tcfg = {'hotspot_with_sslldap_conf':hotspot_with_sslldap_conf,
            'hotspot_wlan_with_sslldap_cfg':hotspot_wlan_with_sslldap_cfg,
            'stand_open_wlan':stand_open_wlan,
            'role_cfg_list':role_cfg_list,
            'admin_cfg':admin_cfg,
           }
    
    return tcfg
    
    
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    ap_sym_dict = tbcfg['ap_sym_dict'] 
    sta_ip_list = tbcfg['sta_ip_list'] 
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
    
    ap_tag_list = []
    for ap_tag in ap_sym_dict:
        ap_tag_list.append(ap_tag)
    
    tcfg = {'target_sta':target_sta,
            'ap_tag_list':ap_tag_list,
            }
    
    ts_name = 'SSLLdap And Https Redirector System Interaction '
    ts = testsuite.get_testsuite(ts_name, 'Verify SSLLdap And Https Redirector System Interaction', combotest=True)
    dcfg = define_test_parameters(tbcfg)
    tcfg.update(dcfg)
    
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