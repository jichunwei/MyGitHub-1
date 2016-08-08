"""
Verify ldap over ssl and https redirector function.

    Pre-condition:
       AP joins ZD1
       ZD1 ZD2 Enable S.R
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) both zd enale S.R
        2) import trusted CA to ZD
        3) create ldap server enable ldap ssl
        4) case1:[sslldap with webauth by https redirector]
        5) case2:[sslldap with guestaccess by https redirector]
        6) case3:[sslldap with hotspot by https redirector]contain failover
        7) disable S.R 
        8) make sure all APs connect zd1
        
    ps: CA needs manual generate. validity 365days. 
        save to TE: d:/CA/my-ca-ipv4-right.crt 
         
Created on 2014-10-28
@author: Yu.yanan@odc-ruckuswireless.com
"""

import sys
from random import randint
import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
 
    test_cfgs = [] 
    idx = 0
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'Both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({'zdcli_tag':'active_zd_cli'}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove all aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_sta'],
                       'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
 
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create Ldap server enable ssl'
    test_cfgs.append(({'server_cfg_list':[{'grp_search': True, 'server_name': 'SSLLDAP_Server', 'win_domain_name':'dc=example,dc=net','admin_domain_name': 'cn=Manager,dc=example,dc=net','admin_password': 'lab4man1', 'server_port': '636', 'grp-search': True, 'type': 'ldap', 'server_addr': '192.168.0.252','ldap_encryption':True}]}, test_name, common_name, 0, False))  
    
    #**************************(1)webauth wlan***********************************************************
    
    tc_common_name = "sslldap with webauth by https redirector"
    
    idx += 1
    step = 0
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%screate wlan with webauth' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':cfg['webauth_wlan_cfg']}, test_name, common_name, 1, False))


    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['webauth_wlan_cfg']}, test_name, common_name, 2, False))
    
            
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','start_browser_before_auth': True, 'close_browser_after_auth': True ,'target_url': 'https://172.16.10.252/',
                       'username': 'test.ldap.user', 'password': 'test.ldap.user'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','username':'test.ldap.user','wlan_cfg': cfg['webauth_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, True))
  
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
  
    #*************************(2)guest access wlan*********************************************************************
    idx +=1
    step = 0
    tc_common_name = "sslldap with guestaccess by https redirector"
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%screate wlan with guestaccess' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Generate_Guest_Pass'
    step += 1
    common_name = '[%s]%s.%sGenerate the guestpass by the guest user'% (tc_common_name, idx, step)
    test_cfgs.append((cfg['generate_guestpass_cfg'], test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','start_browser_before_auth': True,  'close_browser_after_auth': True, 'target_url': 'https://172.16.10.252/', 'use_tou': False}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'Guest-Auth','username':'test.ldap.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    step += 1
    common_name = '[%s]%s.%s Remove all Guest Access service from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Set_GuestPass_Policy'
    step += 1
    common_name = '[%s]%s.%s set GuestPass Policy is default'% (tc_common_name, idx, step)
    test_cfgs.append(({'auth_serv': 'Local Database'}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
    #*********************************(3) hotspot wlan**************************************************************************
    idx +=1
    step = 0
    tc_common_name = "sslldap with hotspot by https redirector"
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    step += 1
    common_name = '[%s]%s.%screate wlan with hotspot' % (tc_common_name, idx, step)
    test_cfgs.append(({'wlan_conf':cfg['hotspot_wlan_cfg']}, test_name, common_name, 1, False))
    
    for num in range(0,2):
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['hotspot_wlan_cfg']}, test_name, common_name, 2, False))
    
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
        test_cfgs.append(({'sta_tag': 'sta_1','username':'test.ldap.user','wlan_cfg': cfg['hotspot_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        step += 1
        common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','target': '172.16.10.252', 'condition': 'allowed'}, test_name, common_name, 2, False))

        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
        
        if num == 0:
            test_name = 'CB_ZD_SR_Failover'
            step += 1
            common_name = '[%s]%s.%s Failover the active zd'% (tc_common_name, idx, step)
            test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLAN from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({'zdcli_tag':'active_zd_cli'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    step += 1
    common_name = '[%s]%s.%s Remove hotspot profile from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({'cleanup':True,'hotspot_conf':{'name':'Hotsport_Default'}}, test_name, common_name, 2, True))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
      
    #****************************************clean up**************************************************
    
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd1 before test'
    test_cfgs.append(({'target_zd':'zd1'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Disable_SR'
    common_name = 'Disable Smart Redundancy via CLI on zd2 before test'
    test_cfgs.append(({'target_zd':'zd2'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD'
    common_name = 'Make all aps connect init active zd'
    test_cfgs.append(({'ap_num':2,'from_zd':'zd2','to_zd':'zd1'}, test_name, common_name, 0, True))
    
    for ap_tag in cfg['ap_tag_list']:
        test_name = 'CB_ZD_CLI_Wait_AP_Connect'
        common_name = 'Make sure %s connect init active zd'%ap_tag
        test_cfgs.append(({'zd_tag':'zdcli1','ap_tag':ap_tag}, test_name, common_name, 0, True))
        
    return test_cfgs

def gen_random_int():
    return randint(1,10000)

def define_test_parameters(tbcfg):

    rand_num = gen_random_int()
    username = 'test.ldap.user'
    password = 'test.ldap.user'
    servername = 'SSLLDAP_Server'
    
    guest_name = 'Guest-Auth'
    hotspot_name = 'Hotsport_Default'
    
    webauth_wlan_name = 'webauth-https-std'+str(rand_num)
    guest_wlan_name = 'sslldap-https-guest'+str(rand_num)
    hotspot_wlan_name = 'sslldap-https-hotspot'+str(rand_num)
    
    webauth_wlan_cfg = {"name" : webauth_wlan_name,
                    "ssid" : webauth_wlan_name,
                    "auth" : "open",
                    "encryption" : "none",
                    'web_auth':True,
                    'auth_server':servername,
                    'username':username
                    }
    
    generate_guestpass_cfg= dict(type = "single",
                                 guest_fullname = guest_name,
                                 duration = "5",
                                 duration_unit = "Days",
                                 key = "",
                                 wlan = guest_wlan_name,
                                 remarks = "",
                                 is_shared = "YES",
                                 auth_ser = servername,
                                 username = username,
                                 password = password)
                                                
                    
    guest_access_conf = {'authentication_server': servername,
                         'authentication': 'Use guest pass authentication.',      
                         'terms_of_use': 'Disabled'}
    
    guest_wlan_cfg =  {"name" :guest_wlan_name,
                       'ssid': guest_wlan_name,
                       'auth': 'open',
                       'encryption' : 'none',     
                       'type':'guest-access',
                       'guest_access_service':guest_access_conf,}
    
    hotspot_conf = {'name': hotspot_name, 
                    'start_page': '', 
                    'authentication_server':servername, 
                    'accounting_server': 'Disabled', 
                    'login_page_url':'http://192.168.0.250/login.html'}
    
    hotspot_wlan_cfg = {'name' :hotspot_wlan_name,
                        'ssid': hotspot_wlan_name,
                        'auth': 'open',
                        'encryption' :'none',
                        'type':'hotspot', 
                        'hotspot_service': hotspot_conf,
                        }
    tcfg = {'generate_guestpass_cfg':generate_guestpass_cfg,
            'hotspot_conf':hotspot_conf,
            'guest_wlan_cfg':guest_wlan_cfg,
            'hotspot_wlan_cfg':hotspot_wlan_cfg,
            'webauth_wlan_cfg':webauth_wlan_cfg}
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
            'ap_tag_list':ap_tag_list}
    ts_name = 'SSLLdap And Https Redirector Combination Function Under S.R'
    ts = testsuite.get_testsuite(ts_name, 'Verify SSLLdap And Https Redirector Combination Function', combotest=True)
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