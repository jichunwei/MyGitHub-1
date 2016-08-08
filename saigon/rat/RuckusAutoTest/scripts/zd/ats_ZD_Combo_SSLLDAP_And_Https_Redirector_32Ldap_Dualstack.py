
"""
Verify ldap over ssl and https redirector system interaction.

    Pre-condition:
       AP joins ZD1
    Test Data:ipv6 linux server:2020:db8:1::151
        
    expect result: All steps should result properly.
    
    How to:Hotsport_Default'
    
        1) import trusted CA to ZD
        2) create 30 ldap server enable ldap ssl
        3) create a ldap server enable ssl
        4) create a ldap server disable ssl
        5) case1:[32sslldap with webauth by https redirector]
         
    ps: CA needs manual generate. validity 365days. 
        save to TE: d:/CA/my-ca-ipv6-right.crt  
        

    
Created on 2014-10-28
@author: Yu.yanan@odc-ruckuswireless.com
"""


import sys
from random import randint
from copy import deepcopy
import libZD_TestSuite_SM as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
 
    test_cfgs = [] 
    idx = 0
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
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
    common_name = 'Create 30 Ldap server enable ssl'
    test_cfgs.append(({'server_cfg_list':cfg['err_sslldap_server_cfg_list']}, test_name, common_name, 0, False))  
   
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create a Ldap server enable ssl'
    test_cfgs.append(({'server_cfg_list':cfg['sslldap_server_cfg_list']}, test_name, common_name, 0, False))  

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create a Ldap server disable ssl'
    test_cfgs.append(({'server_cfg_list':cfg['ldap_server_cfg_list']}, test_name, common_name, 0, False))  


    #****************************************case 1 ***************************************************
    
    wlan_cfgs = {'webauth_sslldaap':[cfg['webauth_wlan_with_sslldap_cfg'],1],
                 'webauth_ldap':[cfg['webauth_wlan_with_ldap_cfg'],2]
                 }
    
    tc_common_name = "32sslldap with webauth by https redirector"
    idx +=1
    step = 0
    
    for tc_name in wlan_cfgs:
        test_name = 'CB_ZD_CLI_Create_Wlan'    
        step += 1
        common_name = '[%s]%s.%s Edit WLAN with %s server' % (tc_common_name,idx, step,tc_name)
        test_cfgs.append(({'wlan_conf':wlan_cfgs[tc_name][0]}, test_name, common_name, wlan_cfgs[tc_name][1], False))
   
 
        test_name = 'CB_ZD_Associate_Station_1'
        step += 1
        common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': wlan_cfgs[tc_name][0]}, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Get_Wifi_Addr_Verify_Expect_Subnet_IPV6'
        step += 1
        common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1', 'ip_version': 'dualstack', 'expected_subnet_ipv6': '2020:db8:1::151/64', 'expected_subnet': '192.168.0.252/255.255.255.0'}, test_name, common_name, 2, False))
        
        
        test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
        step += 1
        common_name = '[%s]%s.%s perform client auth wlan' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','start_browser_before_auth': True, 'close_browser_after_auth': True ,'target_url': 'https://[2020:db8:50::151]/',
                       'username': 'test.ldap.user', 'password': 'test.ldap.user'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Verify_Station_Info_V2'
        step += 1
        common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','username':'test.ldap.user','wlan_cfg':wlan_cfgs[tc_name][0],'status': 'Authorized'}, test_name, common_name, 2, False))
    
        test_name = 'CB_ZD_Client_Ping_Dest'
        step += 1
        common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1','target': '2020:db8:50::151', 'condition': 'allowed'}, test_name, common_name, 2, False))

        test_name = 'CB_Station_Remove_All_Wlans'
        step += 1
        common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
        test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
        
    #****************************************clean up**************************************************
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove the WLAN from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove aaa server'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs

def gen_random_int():
    return randint(1,10000)

def define_test_parameters(tbcfg):

    rand_num = gen_random_int()
    sslldap_servername = 'SSLLDAP_Server'
    ldap_servername = 'LDAP_Server'
    err_server_addr = '2020:db8:1::111' 
    server_addr = '2020:db8:1::151'
    username = 'test.ldap.user'
   
    webauth_wlan_name = 'sslldap-https-webauth'+str(rand_num)
     
    sslldap_server_cfg_list = [{ 
                        'server_name': sslldap_servername,
                        'win_domain_name':'dc=example,dc=net',
                        'admin_domain_name': 'cn=Manager,dc=example,dc=net',
                        'admin_password': 'lab4man1', 
                        'server_port': '636', 
                        'grp-search': True,
                        'type': 'ldap',
                        'server_addr': server_addr,
                        'ldap_encryption':True}]
    
    ldap_server_cfg_list = [{
                        'server_name': ldap_servername, 
                        'win_domain_name':'dc=example,dc=net',
                        'admin_domain_name': 'cn=Manager,dc=example,dc=net',
                        'admin_password': 'lab4man1', 
                        'server_port': '389', 
                        'grp-search': True,
                        'type': 'ldap',
                        'server_addr': server_addr,
                        'ldap_encryption':False}]
    
    # generate 30 fake sslldap server
    err_sslldap_server_cfg_list = []
    for num in range(1,31):
        server_name = sslldap_servername + "_"+str(num)
        err_server = deepcopy(sslldap_server_cfg_list[0])
        err_server.update({'server_addr':err_server_addr,'server_name':server_name})
        err_sslldap_server_cfg_list.append(err_server)
    
 
    
    webauth_wlan_with_sslldap_cfg = {
                        'name' : webauth_wlan_name,
                        'ssid': webauth_wlan_name,
                        'auth': 'open',
                        'encryption' :'none',
                        'web_auth':True,
                        'auth_server':sslldap_servername,
                        'username':username,
                    }
                        
    webauth_wlan_with_ldap_cfg = {
                        'name' : webauth_wlan_name,
                        'ssid': webauth_wlan_name,
                        'auth': 'open',
                        'encryption' :'none',
                        'web_auth':True,
                        'auth_server':ldap_servername,
                        'username':username,
                        }
                        
    
    tcfg = {
            'webauth_wlan_with_sslldap_cfg':webauth_wlan_with_sslldap_cfg,
            'webauth_wlan_with_ldap_cfg':webauth_wlan_with_ldap_cfg,
            
            'sslldap_server_cfg_list':sslldap_server_cfg_list,
            'ldap_server_cfg_list':ldap_server_cfg_list,
            'err_sslldap_server_cfg_list':err_sslldap_server_cfg_list,
            }
    
    return tcfg
    
    
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    sta_ip_list = tbcfg['sta_ip_list'] 
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ")
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
    
    
    tcfg = {'target_sta':target_sta,
            }
    ts_name = 'SSLLdap And Https Redirector 32 ldap under Dualstack '
    ts = testsuite.get_testsuite(ts_name, 'Verify SSLLdap And Https Redirector 32 ldap under Dualstack', combotest=True)
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
