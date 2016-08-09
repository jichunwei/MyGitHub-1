"""
Verify wlan with open none encryption types with l3 ipv6 acl works well for ipv6

    Verify wlan with l3 ipv6 acl works well when ZD is dual stack and ipv6 only.
    Encryption type coverage:
          
    
    expect result: All steps should result properly.
    
    How to:
        1) Get ZD and AP IP version from testbed config
        2) Disable all AP's wlan service
        3) Enable active AP's wlan service based on radio   
        4) Create a wlan and make sure it is in default wlan group
        5) Station associate the wlan
        6) Get station wifi ipv4 and ivp6 address and verify they are in expected subnet
        7) Verify station can ping target ipv4 and ipv6
        7) Verify station can download a file from server
        9) Verify station information in ZD, status is authorized
        10) Verify station information in AP side
    
Created on 2012-2-21
@author: cherry.cheng@ruckuswireless.com
"""

import sys
import random

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_cfg(cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    ip_version = cfg['ip_version']
    l3acl_ipv6_allow = cfg['l3acl_ipv6_allow']
    l3acl_ipv6_deny = cfg['l3acl_ipv6_deny']
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    #test_params = {'cfg_type': 'init',
    #               'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
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
    
    test_name = 'CB_ZD_CLI_Create_L3_ACLs_IPV6'
    common_name = 'Create 2 L3 IPV6 ACLs allow and deny'
    test_cfgs.append(({'l3_acl_cfgs': [l3acl_ipv6_allow, l3acl_ipv6_deny]},
                      test_name, common_name, 0, False))
        
    wlans_cfg_list = cfg['wlan_cfg_list']
    for wlan_cfg in wlans_cfg_list:
        allow_wlan_cfg = {}
        allow_wlan_cfg.update(wlan_cfg)
        
        allow_wlan_cfg['l3acl_ipv6'] = l3acl_ipv6_allow['name']
        test_case_name = '[Allow All ACL - %s]' % (_get_wlan_encrypt_type(allow_wlan_cfg),)
        
        test_name = 'CB_ZD_CLI_Create_Wlan'
        common_name = 'Create a wlan on ZD with allow acl'
        test_cfgs.append(({'wlan_conf': allow_wlan_cfg,
                           'check_wlan_timeout': 80}, test_name, common_name, 1, False))
        
        expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, allow_wlan_cfg)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP' % (test_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': ap_tag}, test_name, common_name, 2, False))
        
        test_cfgs.extend(_define_station_test_cfg(cfg, test_case_name, allow_wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version, l3acl_ipv6_allow))
        
        deny_wlan_cfg = {}
        deny_wlan_cfg.update(wlan_cfg)
        deny_wlan_cfg['l3acl_ipv6'] = l3acl_ipv6_deny['name']
        test_case_name = '[Deny All ACL - %s]' % (_get_wlan_encrypt_type(deny_wlan_cfg),)
        
        test_name = 'CB_ZD_CLI_Create_Wlan'
        common_name = '%sUpdate a wlan on ZD as deny acl' % (test_case_name,)
        test_cfgs.append(({'wlan_conf': deny_wlan_cfg}, test_name, common_name, 1, False))
        
        test_cfgs.extend(_define_station_test_cfg(cfg, test_case_name, deny_wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version, l3acl_ipv6_deny))
            
        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = 'Remove WLAN %s from ZD' %wlan_cfg['ssid']
        test_cfgs.append(({}, test_name, common_name, 2, True))    
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    #test_params = {'cfg_type': 'teardown',
    #               'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_L3_ACLs_IPV6'
    common_name = 'Remove all L3 IPV6 ACLs'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs

def _define_station_test_cfg(cfg, test_case_name, wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version, acl_cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    server_ip_addr = cfg['server_ip_addr']
    netmask = cfg['netmask']
    server_ipv6_addr = cfg['server_ipv6_addr']
    prefix_len = cfg['prefix_len']
    zd_ipv4_addr = cfg['zd_ipv4_addr']
    zd_ipv6_addr = cfg['zd_ipv6_addr']
    web_ipv4_addr = cfg['web_ipv4_addr']
    web_ipv6_addr = cfg['web_ipv6_addr']
    
    ipv4_expected_sub_mask = netmask
    ipv4_expected_subnet_ip_addr = server_ip_addr
    ipv6_expected_prefix_len = prefix_len
    ipv6_expected_subnet_ip_addr = server_ipv6_addr
    
    default_action, allow_ip_in_acl_list, deny_ip_in_acl_list = _get_deny_allow_from_acl(acl_cfg)
    
    all_target_ip_list = []
    ipv6_not_in_acl_list = []
    
    if ip_version in [const.IPV4, const.DUAL_STACK]:
        all_target_ip_list.append(zd_ipv4_addr)
        all_target_ip_list.append(server_ip_addr)
        all_target_ip_list.append(web_ipv4_addr)
        
    if ip_version in [const.IPV6, const.DUAL_STACK]:
        all_target_ip_list.append(zd_ipv6_addr)
        all_target_ip_list.append(server_ipv6_addr)
        all_target_ip_list.append(web_ipv6_addr)
        
        ipv6_not_in_acl_list.append(web_ipv6_addr)
        
    allow_ip_list = []
    deny_ip_list = []
    if default_action == 'allow':
        is_allow = True
        deny_ip_list = deny_ip_in_acl_list
        allow_ip_list = ipv6_not_in_acl_list
    else:
        is_allow = False
        allow_ip_list = allow_ip_in_acl_list
        deny_ip_list = ipv6_not_in_acl_list
        
    sta_wlan_cfg = _convert_wlan_for_assoc_station(wlan_cfg)
        
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '%sAssociate the station and verify wifi ip in subnet' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'wlan_cfg': sta_wlan_cfg,
              'expected_subnet': '%s/%s' % (ipv4_expected_subnet_ip_addr, ipv4_expected_sub_mask),
              'expected_subnet_ipv6': '%s/%s' % (ipv6_expected_subnet_ip_addr, ipv6_expected_prefix_len),
              'ip_version': ip_version,
              'start_browser': False,
              }    
    test_cfgs.append((params, test_name, common_name, 2, False))
    
    if is_allow:
        #Default action is allow, can't ping ip in deny list, and can ping ip not in list.
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can ping IPs not in deny list' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': allow_ip_list,
                  'allow': True,
                  'download_file': False,
                  'close_browser': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can not ping IPs in deny list' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': deny_ip_list,
                  'allow': False,
                  'download_file': False,
                  'close_browser': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
    else:
        #Default action is deny, can ping ips in allow list, can't ping ip not in list.
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can not ping IPs not in allow list' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'target_ip_list': deny_ip_list,
                  'allow': False,
                  'download_file': False,
                  'close_browser': False,
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Ping_Targets_Download_File'
        common_name = '%sVerify client can ping IPs in allow list' % (test_case_name,)
        params = {'sta_tag': sta_tag,
                  'allow': True,
                  'target_ip_list': allow_ip_list,
                  'download_file': False,
                  'close_browser': False,                  
                  }   
        test_cfgs.append((params, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Verify_Station_Info_On_ZD_AP'
    common_name = '%sVerify station info on ZD and AP' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'ap_tag': ap_tag,
              'status': 'authorized',
              'radio_mode': radio_mode,
              'wlan_cfg': sta_wlan_cfg,
              }  
    test_cfgs.append((params, test_name, common_name, 2, False))
        
    return test_cfgs

def _get_deny_allow_from_acl(acl_cfg):
    allow_ip_list = []
    deny_ip_list = []
    
    default_action = 'allow' if 'allow' in acl_cfg['default_mode'].lower() else 'deny'
    
    if acl_cfg.has_key('rules'):
        rule_list = acl_cfg['rules']
    else:
        rule_list = []
    
    for rule in rule_list:
        if rule['action'].lower() == 'allow':
            allow_ip_list.append(rule['dst_addr'].split('/')[0])
        elif rule['action'].lower() == 'deny':
            deny_ip_list.append(rule['dst_addr'].split('/')[0])
            
    return default_action, allow_ip_list, deny_ip_list

def _define_expect_wlan_info_in_ap(tcfg, wlan_cfg):
    if type(tcfg['radio_mode']) == list:
        radio_mode_list = tcfg['radio_mode']
    else:
        radio_mode_list = [tcfg['radio_mode']]                                                                                                          
    
    expect_wlan_info = dict()
    for radio in radio_mode_list:
        status = 'up'
        if radio in ['bg', 'ng']:            
            wlan_name = "wlan0"
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])
        elif radio in ['na']:
            MAXIMUM_WLAN = 8
            wlan_name = "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])

    return expect_wlan_info

def _define_l3_ipv6_acls(server_ipv6_addr, prefix_len):
    l3acl_allow = {'name':'l3ipv6acl-allow',
                   'description': '',
                   'default_mode': 'allow-all',
                   'rules': [{'action': u'Deny',
                             #'application': u'Any',
                             'description': u'denyrules',
                             'dst_addr': '%s/%s' % (server_ipv6_addr,prefix_len), #u'2020:db8:1::2/64',
                             #'dst_port': u'Any',
                             #'order': u'5',
                             #'protocol': u'Any',
                             #'icmp_type': '',
                             }]
                   }
    l3acl_deny = {'name':'l3ipv6acl-deny',
                  'description': '',
                  'default_mode': 'deny-all',
                  'rules': [{'action': u'Allow',
                             #'application': u'Any',
                             'description': u'allowrules',
                             'dst_addr': '%s/%s' % (server_ipv6_addr,prefix_len), #u'2020:db8:1::2/64',
                             #'dst_port': u'Any',
                             #'order': u'5',
                             #'protocol': u'Any',
                             #'icmp_type': '',
                             }]}
    
    return l3acl_allow, l3acl_deny 

def _get_wlan_encrypt_type(wlan_cfg):
    auth = wlan_cfg['auth']
    encryption = wlan_cfg.get('encryption')
    wpa_ver = wlan_cfg.get('algorithm')
    key_index = wlan_cfg.get('key_index')        
    wlan_encrypt = '%s_%s' % (auth, encryption)
    if wpa_ver:
        wlan_encrypt = wlan_encrypt + '_%s' % (wpa_ver,)
    if key_index:
        wlan_encrypt = wlan_encrypt + '_%s' % (key_index,)
        
    return wlan_encrypt

def _get_wlan_cfg(wlan_params):
    ssid = ''
    
    wlanCfg = dict(ssid=ssid, name="", type='standard-usage', auth="open", 
                   algorithm="", encryption="none", key_index="", key_string="",
                   passphrase="", username="", password="",)
    
    wlanCfg.update(wlan_params)
    
    ssid = '%s-%04d' % (_get_wlan_encrypt_type(wlanCfg), (random.randrange(1, 9999)))
    wlanCfg['ssid'] = ssid
    wlanCfg['name'] = ssid
    
    return wlanCfg

def _define_wlan_cfg_list():
    '''
    Adapter method to update each wlan_cfg and generate a list of wlan_cfg
    '''
    wlan_cfgs = []
    
    wlan_cfgs.append(_get_wlan_cfg(dict(auth="open", encryption="none")))
    
    return wlan_cfgs

def _convert_wlan_for_assoc_station(wlan_cfg):
    keys_mapping = {'passphrase': 'key_string',
                    'auth_server': 'auth_svr',                    
                    'web_auth': 'do_webauth',
                    'zero_it': 'do_zero_it',
                    'tunnel_mode': 'do_tunnel',
                    #'eap_type':
                    #'acc_server': 'acct_svr',
                    #'interim': 'interim_update',
                    #'l2acl': 'acl_name',
                    #'l3acl': 'l3_l4_acl_name',
                    #'l3acl_ipv6': 'l3_l4_ipv6_acl_name',
                    #'rate_limit_uplink': 'uplink_rate_limit',
                    #'rate_limit_downlink': 'downlink_rate_limit',
                    #'hide_ssid': 'do_hide_ssid',
                    #'client_isolation': 'do_isolation',
                    #'hotspot_name': 'hotspot_profile',
                    
                    }

    values_mapping = {'standard-usage': 'standard',
                      'guest-access': 'guest',
                      #'hotspot': 'hotspot',
                      'wep-64': 'WEP-64',
                      'wep-128': 'WEP-128',
                      #'open': 'open',
                      #'shared': 'shared',
                      'dot1x-eap': 'EAP',
                      #'mac': 'mac',
                      #'wpa': 'WPA',
                      #'wpa2': 'WPA2',
                      #'wpa-mixed': 'WPA_Mixed',
                      #'TKIP': 'TKIP',
                      #'AES': 'AES',
                      'auto': 'Auto',
                      'local': 'Local Database',
                      }

    new_wlan_cfg = {}
    for key, value in wlan_cfg.items():
        new_key = key
        new_value = value

        if keys_mapping.has_key(key):
            new_key = keys_mapping[key]
        if values_mapping.has_key(value):
            new_value = values_mapping[value]

        new_wlan_cfg[new_key] = new_value
        
    #If auth=open, and algorithm is wpa related, auth is PSK.
    if 'wpa' in wlan_cfg.get('encryption').lower():
        wpa_ver = wlan_cfg['encryption']
        if wpa_ver.lower() in ['wpa', 'wpa2']:
            wpa_ver = wpa_ver.upper()
        else:
            wpa_ver = 'WPA_Mixed'
        new_wlan_cfg['wpa_ver'] = wpa_ver    
        
        
        new_wlan_cfg['encryption'] = wlan_cfg['algorithm']
        
        if new_wlan_cfg.get('auth').lower() == 'open':
            new_wlan_cfg['auth'] = 'PSK'
    else:
        new_wlan_cfg['encryption'] = wlan_cfg['encryption']
         
    return new_wlan_cfg

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
    zd_ipv4_addr = testsuite.get_zd_ipv4_addr(tbcfg)
    zd_ipv6_addr = testsuite.get_zd_ipv6_addr(tbcfg)
    ap_sym_dict = testsuite.get_ap_sym_dict(tbcfg)
    all_ap_mac_list = testsuite.get_ap_mac_list(tbcfg)
    server_ip_addr = testsuite.get_server_ip(tbcfg)   
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg) 
    netmask = testsuite.get_ipv4_net_mask(tbcfg)
    prefix_len = testsuite.get_ipv6_prefix_len(tbcfg)
    
    zd_ip_version = testsuite.get_zd_ip_version(tbcfg)
    ap_ip_version = testsuite.get_ap_ip_version(tbcfg)
    
    web_ipv4_addr = '172.16.10.252'
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
    
    wlan_cfg_list = _define_wlan_cfg_list()
    l3acl_ipv6_allow, l3acl_ipv6_deny = _define_l3_ipv6_acls(server_ipv6_addr, prefix_len)
    
    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]        
        active_ap_mac = active_ap_cfg['mac']        
        
        tcfg = {'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap': active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,
                'wlan_cfg_list': wlan_cfg_list,
                'server_ip_addr': server_ip_addr,
                'netmask': netmask,
                'server_ipv6_addr': server_ipv6_addr,
                'prefix_len': prefix_len,
                'ip_version': zd_ip_version,
                'l3acl_ipv6_allow': l3acl_ipv6_allow,
                'l3acl_ipv6_deny': l3acl_ipv6_deny,
                'zd_ipv4_addr': zd_ipv4_addr,
                'zd_ipv6_addr': zd_ipv6_addr,
                'web_ipv6_addr': web_ipv6_addr,
                'web_ipv4_addr': web_ipv4_addr,
                }

        test_cfgs = define_test_cfg(tcfg)

        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            ts_name = "ZD CLI - WLAN with L3 IPV6 ACL Open - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)

        ts = testsuite.get_testsuite(ts_name, "Verify WLAN with open shared encryption type - 11%s" % (target_sta_radio), combotest = True)

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