"""
Verify wlan with different authentication server works well for dual stack and ipv6.

    Verify wlan with different authentication servers works well for dual stack and ipv6.
    Encryption type coverage:
        EAP-WPA2-[TKIP, AES, Auto]
    Authentication Server:
        Radius
        Active Directory - Only support ipv4 server now
        LDAP
    expect result: All steps should result properly.
    
    How to:
        1) Get ZD and AP IP version from testbed config
        3) Disable all AP's wlan service
        4) Enable active AP's wlan service based on radio   
        5) Create a wlan and make sure it is in default wlan group
        6) Station associate the wlan
        7) Get station wifi ip addresses and verify they are in expected subnet
        8) Verify station can ping target ipv4 and ipv6
        9) Verify station can download a file from server
        10) Verify station information in ZD, status is authorized
        11) Verify station information in AP side
    
Created on 2012-2-21
@author: cherry.cheng@ruckuswireless.com
"""

AUTH_TYPE_RADIUS = 'RADIUS'
AUTH_TYPE_LOCAL_DATABASE = 'Local Database'

import sys
import random

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_test_cfg(cfg):
    test_cfgs = []

    ras_cfg = cfg['ras_cfg']
    radio_mode = cfg['radio_mode']
    ip_version = cfg['ip_version']

    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    if cfg['server_type'] == AUTH_TYPE_LOCAL_DATABASE:
        test_name = 'CB_ZD_Create_Local_User'
        common_name = 'Create Local User'
        test_params = {'username': ras_cfg['username'],
                       'password': ras_cfg['password']}
        test_cfgs.append((test_params, test_name, common_name, 0, False))
    elif cfg['server_type'] == AUTH_TYPE_RADIUS:
        test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
        common_name = 'Create Radius authentication server'
        test_cfgs.append(({'server_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))
    
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

    wlans_cfg_list = cfg['wlan_cfg_list']
    for wlan_cfg in wlans_cfg_list:
        test_case_name = '[%s]' % (_get_wlan_encrypt_type(wlan_cfg),)

        test_name = 'CB_ZD_CLI_Create_Wlan'
        common_name = '%sCreate a wlan on ZD' % (test_case_name,)
        test_cfgs.append(({'wlan_conf':wlan_cfg,
                           'check_wlan_timeout': 80}, test_name, common_name, 1, False))

        expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP' % (test_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': ap_tag}, test_name, common_name, 2, False))

        test_cfgs.extend(_define_station_test_cfg(cfg, test_case_name, wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version))

        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = '%sRemove WLAN %s from ZD' %(test_case_name, wlan_cfg['ssid'])
        test_cfgs.append(({}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    #test_params = {'cfg_type': 'teardown',
    #               'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA Server'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    return test_cfgs

def _define_station_test_cfg(cfg, test_case_name, wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    #zd_ipv6_addr = cfg['zd_ipv6_addr']

    target_ip_addr = cfg['server_ip_addr']
    netmask = cfg['netmask']
    target_ipv6_addr = cfg['server_ipv6_addr']
    prefix_len = cfg['prefix_len']

    web_ipv6_addr = cfg['web_ipv6_addr']
    web_ipv4_addr = cfg['web_ipv4_addr']

    ipv4_expected_sub_mask = netmask
    ipv4_expected_subnet_ip_addr = target_ip_addr
    ipv6_expected_prefix_len = prefix_len
    ipv6_expected_subnet_ip_addr = target_ipv6_addr

    target_ip_list = []
    web_ip_addr_list = []
    if ip_version in [const.IPV4, const.DUAL_STACK]:
        target_ip_list.append(target_ip_addr)
        web_ip_addr_list.append(web_ipv4_addr)
    if ip_version in [const.IPV6, const.DUAL_STACK]:
        target_ip_list.append(target_ipv6_addr)
        #target_ip_list.append(zd_ipv6_addr)
        web_ip_addr_list.append(web_ipv6_addr)
        
    sta_wlan_cfg = _convert_wlan_for_assoc_station(wlan_cfg)

    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '%sAssociate the station and verify wifi ip in subnet' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'wlan_cfg': sta_wlan_cfg,
              'browser_tag': browser_tag,
              'expected_subnet': '%s/%s' % (ipv4_expected_subnet_ip_addr, ipv4_expected_sub_mask),
              'expected_subnet_ipv6': '%s/%s' % (ipv6_expected_subnet_ip_addr, ipv6_expected_prefix_len),
              'ip_version': ip_version,
              'start_browser': True,
              }
    test_cfgs.append((params, test_name, common_name, 2, False))

    test_name = 'CB_Station_Ping_Targets_Download_File'
    common_name = '%sVerify can ping target IPs and download file' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'browser_tag': browser_tag,
              'target_ip_list': target_ip_list,
              'allow': True,
              'web_ip_addr_list': web_ip_addr_list,
              'close_browser': True,
              }
    test_cfgs.append((params, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_On_ZD_AP'
    common_name = '%sVerify station is authorized on ZD and info on AP' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'ap_tag': ap_tag,
              'status': 'Authorized',
              'radio_mode': radio_mode,
              'wlan_cfg': sta_wlan_cfg,
              }
    test_cfgs.append((params, test_name, common_name, 2, False))

    return test_cfgs

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
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid = wlan_cfg['ssid'])
        elif radio in ['na']:
            MAXIMUM_WLAN = 8
            wlan_name = "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid = wlan_cfg['ssid'])

    return expect_wlan_info

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
        
    if wlan_cfg.get('eap_type'):
        wlan_encrypt += '_%s' % wlan_cfg.get('eap_type')

    return wlan_encrypt

def _get_wlan_cfg(wlan_params):
    wlanCfg = dict(ssid = '', name = '', type = 'standard-usage', auth = "open",
                   algorithm = "", encryption = "none", key_index = "", key_string = "",
                   username = "", password = "",)

    wlanCfg.update(wlan_params)

    ssid = '%s-%04d' % (_get_wlan_encrypt_type(wlanCfg), (random.randrange(1, 9999)))
    wlanCfg['ssid'] = ssid
    wlanCfg['name'] = ssid

    return wlanCfg

def _define_wlan_cfg_list(ras_cfg):
    '''
    Adapter method to update each wlan_cfg and generate a list of wlan_cfg
    '''
    wlan_cfgs = []

    ras_name = ras_cfg['server_name']
    username = ras_cfg['username']
    password = ras_cfg['password']

    if ras_name == AUTH_TYPE_LOCAL_DATABASE:
        ras_name = 'local'
    '''
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = 'dot1x-eap', encryption = 'none', eap_type = 'EAP-SIM',
                                        auth_server = ras_name, username = username, password = password)))
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = 'dot1x-eap', encryption = 'none', eap_type = 'PEAP',
                                        auth_server = ras_name, username = username, password = password)))
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = "dot1x-eap", encryption = "wep-64",
                                        auth_server = ras_name, username = username, password = password)))
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = "dot1x-eap", encryption = "wep-128",
                                        auth_server = ras_name, username = username, password = password)))
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = "dot1x-eap", encryption = "wpa", algorithm = random.choice(['TKIP', 'AES']),
                                        auth_server = ras_name, username = username, password = password)))
    '''
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = "dot1x-eap", encryption = "wpa2", algorithm = 'AES',
                                        auth_server = ras_name, username = username, password = password)))
    
    '''
    wlan_cfgs.append(_get_wlan_cfg(dict(auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['TKIP', 'AES']),
                                        auth_server = ras_name, username = username, password = password)))
    '''

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

def _define_aaa_server_cfg(server_ipv6_addr):
    radius_server_cfg = {'server_name': 'ruckus-ras-%04d' % random.randrange(1, 9999),
                         'server_addr': server_ipv6_addr,
                         'radius_secret': '1234567890',
                         'server_port': '50001',
                         'username':'ras.eap.user',
                         'password': 'ras.eap.user',
                         'type': 'radius-auth',
                         'backup': False,
                         }

    local_database_cfg = {'server_name': AUTH_TYPE_LOCAL_DATABASE,
                          'username': 'rat_local_user',
                          'password': 'rat_local_user',
                          }

    servers_cfg = {AUTH_TYPE_LOCAL_DATABASE: local_database_cfg,
                   AUTH_TYPE_RADIUS: radius_server_cfg,
                   }

    return servers_cfg

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

    #Select AAA server type.
    aaa_server_types = [AUTH_TYPE_LOCAL_DATABASE, AUTH_TYPE_RADIUS]
    server_type = get_selected_input(aaa_server_types, 'Please select AAA server type[Default is Local Database]')
    if not server_type:
        server_type = AUTH_TYPE_LOCAL_DATABASE

    servers_cfg = _define_aaa_server_cfg(server_ipv6_addr)
    server_cfg = servers_cfg[server_type]
    wlan_cfg_list = _define_wlan_cfg_list(server_cfg)

    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]
        active_ap_mac = active_ap_cfg['mac']

        tcfg = {'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap': active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,
                'wlan_cfg_list': wlan_cfg_list,
                'server_type': server_type,
                'ras_cfg': server_cfg,
                'server_ip_addr': server_ip_addr,
                'netmask': netmask,
                'server_ipv6_addr': server_ipv6_addr,
                'prefix_len': prefix_len,
                'ip_version': zd_ip_version,
                'zd_ipv6_addr': zd_ipv6_addr,
                'web_ipv4_addr': web_ipv4_addr,
                'web_ipv6_addr': web_ipv6_addr,
                }

        test_cfgs = define_test_cfg(tcfg)

        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            ts_name = "ZD CLI - EAP Wlan with %s - ZD %s AP %s 11%s" % (server_type, zd_ip_version, ap_ip_version, target_sta_radio)

        ts = testsuite.get_testsuite(ts_name, "Verify WLAN with different AAA servers - 11%s" % (target_sta_radio), combotest = True)

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
