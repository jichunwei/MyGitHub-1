"""
Verify guest access wlan works well for dual stack and ipv6 only

    Verify guest access wlan works well for dual stack and ipv6 only
    Encryption type coverage:
        Open-none
    AAA server type:
        Local Database
        Radius Server
        Active Directory - only ipv4 ad server, no ipv6 server
        LDAP
    expect result: All steps should result properly.
    
    How to:
        1) Get ZD and AP IP version from testbed config
        2) Disable all AP's wlan service
        3) Enable active AP's wlan service based on radio   
        4) Create a wlan and make sure it is in default wlan group
        5) Set retricted ipv6 acess list
        5) Set guest pass policy 
        6) Set guest access policy
        7) Generate guest pass
        8) Verify guest pass policy
        9) Verify guest access policy
        5) Station associate the wlan
        6) Get station wifi ipv4 and ivp6 address and verify they are in expected subnet
        7) Verify station can't send traffic before guest access
        8) Verify staiton is unauthorized in ZD GUI
        9) Perform guest access authenticaiton      
        10) Verify station send traffic
                Can ping target IPs in restricted allow access list
                Can't ping target IPs in restricted deny access list 
                Can ping target IPs not in restricted access list
        12) Verify station information in ZD, status is authorized
        13) Verify station information in AP side
    
Created on 2011-12-05
@author: cherry.cheng@ruckuswireless.com
"""

import sys
import random

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

ACTION_DENY = 'Deny'
ACTION_ALLOW = 'Allow'

def _define_aaa_server_cfg():
    '''
    Define aaa server configuration for all authentication types: local database.
    ''' 
    server_cfg = {'server_name': 'Local Database',
                  'username': 'rat_guest_pass',
                  'password': 'rat_guest_pass',
                  }
    return server_cfg

def _define_wlan_cfg():
    '''
    Define guest wlan configuration. open-none, and do_tunnel is True.
    '''
    wlan_cfg = {'ssid': "guestaccess-%04d" % random.randrange(1,9999),
                'auth': "open",
                'encryption': "none",
                'type': 'guest',
                'do_tunnel': False,
                }
    
    return wlan_cfg

def _define_guest_access_policy_cfg(use_guestpass_auth = False, use_tou = False, redirect_url = ''):
    '''
    Define guest access policy configuration: use guest auth, use guest pass auth, use tou, redirect url.    
    '''
    guest_access_policy_cfg = dict(use_guestpass_auth=use_guestpass_auth,
                                   use_tou=use_tou,
                                   redirect_url=redirect_url)
    
    return guest_access_policy_cfg

def _define_guest_pass_cfg(server_cfg):
    '''
    Generate guest pass policy configuration.
    '''
    auth_server_name = server_cfg['server_name']
    username = server_cfg['username']
    password = server_cfg['password']
    
    guestpass_policy_cfg = dict(auth_serv=auth_server_name, is_first_use_expired=False, valid_day='5')
    
    generate_guestpass_cfg = dict(type="single", guest_fullname="Guest-Auth", duration="5",
                                  duration_unit="Days", key="", wlan="", remarks="", is_shared="No", 
                                  auth_ser=auth_server_name, username=username, password=password)
    
    return guestpass_policy_cfg, generate_guestpass_cfg

def _define_restricted_rule_cfg(dst_addr, action = 'Deny'):
    '''
    Define restricted access rule cnofiguration.
    '''
    rule_cfg = {'order': '', 'description': '', 'action': '', 'dst_addr': 'Any',
                'application': 'Any', 'protocol': 'Any', 'dst_port': 'Any', 'icmp_type': 'Any'}
    
    rule_cfg['action'] = action    
    rule_cfg['dst_addr'] = dst_addr
    
    return rule_cfg

def _define_restricted_access_list():
    '''
    Define restricted ipv6 list.
    '''
    restricted_access_list = []
    action = ACTION_DENY
    restricted_access_list.append(_define_restricted_rule_cfg('2020:db8:10::251/64', action))
    action = ACTION_ALLOW
    restricted_access_list.append(_define_restricted_rule_cfg('2020:db8:2::251/64', action))
    
    #add order for restricted access list, start from 2.
    order = 2
    for access_cfg in restricted_access_list:
        access_cfg['order'] = order
        order += 1
    
    return restricted_access_list

def _define_guest_policys(web_ipv6_addr):
    '''
    Define all possible guest policy configuration.
    '''
    redirect_url = 'http://[%s]/' % web_ipv6_addr
    guest_policys_cfg = {'Restricted IPV6 Access':  _define_guest_access_policy_cfg(True, True, redirect_url)}
    
    return guest_policys_cfg
                                                              
def define_test_cfg(cfg):
    test_cfgs = []
    
    web_ip_addr = cfg['web_ip_addr']
    web_ipv6_addr = cfg['web_ipv6_addr']
    server_ip_addr = cfg['server_ip_addr']
    server_ipv6_addr = cfg['server_ipv6_addr']
    zd_ipv4_addr = cfg['zd_ipv4_addr']
    zd_ipv6_addr = cfg['zd_ipv6_addr']
    ip_version = cfg['ip_version']
    
    server_cfg = cfg['server_cfg']    
    radio_mode = cfg['radio_mode']
    wlan_cfg = cfg['wlan_cfg']
    wlan_cfg['username'] = server_cfg['username']
    wlan_cfg['password'] = server_cfg['password']
    
    gp_policy_cfg = cfg['guest_pass_policy']
    gen_guestpass_cfg = cfg['gen_guest_pass_policy']
    restricted_access_list = cfg['restricted_access_list']
    
    allow_access_list = []
    deny_access_list = []
    for access_cfg in restricted_access_list:
        dst_ip_addr = access_cfg['dst_addr'].split('/')[0]
        if access_cfg['action'] == ACTION_ALLOW:
            allow_access_list.append(dst_ip_addr)
        elif access_cfg['action'] == ACTION_DENY:
            deny_access_list.append(dst_ip_addr)
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    wg_name = 'Default'
    wg_cfg = dict(name = wg_name, description = None, ap_rp = {radio_mode: {'wlangroups': wg_name}},)
    test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    test_cfgs.append(({'wgs_cfg': wg_cfg,
                       'ap_tag': ap_tag, },
                  test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create Local User'
    test_params = {'username': server_cfg['username'],
                   'password': server_cfg['password']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create a guest wlan'
    test_params = {'wlan_cfg_list': [wlan_cfg]}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = 'Generate the guest pass'
    test_cfgs.append((gen_guestpass_cfg, test_name, common_name, 0, False))
        
    for policy_type, ga_policy_cfg in cfg['guest_policy_dict'].items():
        test_case_name = '[%s]' % policy_type
        gen_guestpass_cfg.update(dict(wlan=wlan_cfg['ssid']))
        
        ipv4_expected_sub_mask = cfg['netmask']
        ipv4_expected_subnet_ip_addr = cfg['server_ip_addr']
        ipv6_expected_prefix_len = cfg['prefix_len']
        ipv6_expected_subnet_ip_addr = cfg['server_ipv6_addr']
        
        #For guest access, the same subnet with zd is denied by default.
        target_ip_list = []
        zd_ip_addr_list = []
        web_ip_addr_list = []
        
        if ip_version in [const.IPV4, const.DUAL_STACK]:
            target_ip_list.append(web_ip_addr)
            target_ip_list.append(server_ip_addr)
            target_ip_list.append(zd_ipv4_addr)
            
            zd_ip_addr_list.append(zd_ipv4_addr)
            
            web_ip_addr_list.append(web_ip_addr)
            
        if ip_version in [const.IPV6, const.DUAL_STACK]:
            target_ip_list.append(web_ipv6_addr)
            target_ip_list.append(server_ipv6_addr)
            target_ip_list.append(zd_ipv6_addr)
            
            zd_ip_addr_list.append(zd_ipv6_addr)
            
            web_ip_addr_list.append(web_ipv6_addr)
            
        if 'No Auth' in policy_type:
            no_auth = True
        else:
            no_auth = False
        if 'No Redirection' in policy_type:
            target_url = 'http://[%s]/' % web_ipv6_addr
            redirect_url = ''
        else:
            target_url = 'http://www.ipv6-example.net'
            redirect_url = ga_policy_cfg['redirect_url']
            
        radio_mode = cfg['radio_mode']
        if radio_mode == 'bg':
            radio_mode = 'g'
    
        test_name = 'CB_ZD_Set_GuestAccess_Policy'
        common_name = '%sSet the guest access policy' % test_case_name
        test_cfgs.append((ga_policy_cfg, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Set_Guest_Restricted_IPV6_Access'
        common_name = '%sSet the guest restricted ipv6 access list' % test_case_name
        test_cfgs.append(({'restricted_ipv6_access_list': restricted_access_list},
                           test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_GuestAccess_Policy'
        common_name = '%sVerify the guest access policy on ZD' % test_case_name
        test_cfgs.append((ga_policy_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_GuestPass_Policy'
        common_name = '%sVerify the guest pass policy on ZD' % test_case_name
        test_cfgs.append((gp_policy_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
        common_name = '%sAssociate the station and verify wifi ip in subnet' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'browser_tag': browser_tag,
                  'wlan_cfg': wlan_cfg,
                  'expected_subnet': '%s/%s' % (ipv4_expected_subnet_ip_addr, ipv4_expected_sub_mask),
                  'expected_subnet_ipv6': '%s/%s' % (ipv6_expected_subnet_ip_addr, ipv6_expected_prefix_len),
                  'ip_version': ip_version,
                  'start_browser': True,
                  }    
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify can not ping target IPs' % (test_case_name,)
        params = {'sta_tag': sta_tag,                  
                  'target_ip_list': target_ip_list,
                  'allow': False,
                  'download_file':False}   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_On_ZD_AP'
        common_name = '%sVerify station is unauthorized on ZD' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'ap_tag': ap_tag,
                  'status': 'unauthorized',
                  'radio_mode': radio_mode,
                  'wlan_cfg': wlan_cfg,
                  'verify_sta_info_ap': False,
                  }  
        test_cfgs.append((params, test_name, common_name, 2, False))
            
        test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
        common_name = '%sPerform guest authentication' % test_case_name
        test_params = {'sta_tag': sta_tag,
                       'browser_tag':browser_tag,
                       'no_auth': no_auth, 
                       'use_tou': ga_policy_cfg['use_tou'],
                       'target_url': target_url, 
                       'redirect_url': redirect_url,
                       }
        test_cfgs.append((test_params, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_On_ZD_AP'
        common_name = '%sVerify station is authorized on ZD and info on AP and tunnel mode' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'ap_tag': ap_tag,
                  'status': 'Authorized',
                  'radio_mode': radio_mode,
                  'wlan_cfg': wlan_cfg,
                  'guest_name': gen_guestpass_cfg['guest_fullname'],
                  'use_guestpass_auth': ga_policy_cfg['use_guestpass_auth'],
                  'verify_sta_tunnel_mode': False,
                  }  
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can not ping ZD IP after guest access' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': zd_ip_addr_list,
                  'allow': False,
                  'download_file': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can not ping denied target IPV6 addresses' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': deny_access_list,
                  'allow': False,
                  'download_file': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can ping allowed target IPV6 addresses' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': allow_access_list,
                  'allow': True,
                  'download_file': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can ping target IPV6 addresses not in access list' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': web_ip_addr_list,
                  'allow': True,
                  'download_file': False,
                  'close_browser': True,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD after test'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs
    
def get_selected_input(depot = [], prompt = ""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select option: "

    selection = []
    id = raw_input(prompt)
    try:
        selection = depot[int(id)]
    except:
        selection = ""

    return selection

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )

    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    
    sta_ip_list = testsuite.get_sta_ip_list(tbcfg)
    zd_ipv6_addr = testsuite.get_zd_ipv6_addr(tbcfg)
    zd_ipv4_addr = testsuite.get_zd_ipv4_addr(tbcfg)
    ap_sym_dict = testsuite.get_ap_sym_dict(tbcfg)
    all_ap_mac_list = testsuite.get_ap_mac_list(tbcfg)
    server_ip_addr = testsuite.get_server_ip(tbcfg)   
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg) 
    netmask = testsuite.get_ipv4_net_mask(tbcfg)
    prefix_len = testsuite.get_ipv6_prefix_len(tbcfg)
    
    zd_ip_version = testsuite.get_zd_ip_version(tbcfg)
    ap_ip_version = testsuite.get_ap_ip_version(tbcfg)
    
    web_ip_addr = '172.16.10.252'
    web_ipv6_addr = '2020:db8:50::251'
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.get_target_station(sta_ip_list, "Pick an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]

    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break
        
    server_cfg = _define_aaa_server_cfg()
    guest_policy_dict = _define_guest_policys(web_ipv6_addr)
    guest_pass_policy, gen_guest_pass_policy = _define_guest_pass_cfg(server_cfg)
    restricted_access_list = _define_restricted_access_list()
    wlan_cfg = _define_wlan_cfg()
    
    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]        
        active_ap_mac = active_ap_cfg['mac']        
        
        tcfg = {'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap': active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,
                'wlan_cfg': wlan_cfg,
                'server_cfg': server_cfg,                
                'guest_policy_dict': guest_policy_dict,
                'guest_pass_policy': guest_pass_policy,
                'gen_guest_pass_policy': gen_guest_pass_policy,
                'restricted_access_list': restricted_access_list,
                'server_ip_addr': server_ip_addr,
                'netmask': netmask,
                'server_ipv6_addr': server_ipv6_addr,
                'web_ipv6_addr': web_ipv6_addr,
                'web_ip_addr': web_ip_addr,
                'prefix_len': prefix_len,
                'zd_ipv4_addr': zd_ipv4_addr,
                'zd_ipv6_addr': zd_ipv6_addr,
                'ip_version': zd_ip_version,
                }

        test_cfgs = define_test_cfg(tcfg)

        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            ts_name = "Guest Access Restricted Access - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)

        ts = testsuite.get_testsuite(ts_name, "Verify Guest Access WLAN Restricted Access - 11%s" % (target_sta_radio), combotest = True)

        test_order = 1
        test_added = 0
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.add_test_case(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
                test_order += 1

                print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
        
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)