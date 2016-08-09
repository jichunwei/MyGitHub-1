"""
Wlan enabled dvlan [with optional vlan and tunnel] works well with dualstack and IPV6

    Verify wlan with dvlan [with vlan or tunnel] works well when ZD is dual stack and ipv6 only.
    Encryption type coverage:
        EAP-WPA2-AES with Radius Server  
    
    expect result: All steps should result properly.
    
    How to:
        1) Get ZD and AP IP version from testbed config
        2) Disable all AP's wlan service
        3) Enable active AP's wlan service based on radio   
        4) Create a wlan and make sure it is in default wlan group
        5) Station associate the wlan with finance.user [dvlan user, vlan is 10]
        6) Get station wifi ipv4 and ivp6 address and verify they are in expected subnet
        7) Verify station can ping target ipv4 and ipv6
        8) Verify station can download a file from server
        9) Verify station information in ZD, status is authorized
        10) Verify station information in AP side
        11) If tunnel mode, verify station traffic is in tunnel mode.
        12) Station associate the wlan with ras.eap.user [Normal user, if no specified vlan id, it is 1, else it is vlan id.]
        12) Repeat step 7 to 10 to do validation.
    
Created on 2011-11-15
@author: cherry.cheng@ruckuswireless.com
"""

import sys
import copy
import random

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

all_vlan_mapping = {'10': {const.IPV4: {'ip_addr': '192.168.10.252',
                                        'mask': '255.255.255.0', },
                           const.IPV6: {'ip_addr': '2020:db8:10::251',
                                        'prefix_len': '64'},},
                    '20': {const.IPV4: {'ip_addr': '192.168.20.252',
                                        'mask': '255.255.255.0', },
                           const.IPV6: {'ip_addr': '2020:db8:20::251',
                                        'prefix_len': '64'},},
                    '301': {const.IPV4: {'ip_addr': '192.168.0.252',
                                         'mask': '255.255.255.0', },
                            const.IPV6: {'ip_addr': '2020:db8:1::251',
                                         'prefix_len': '64'},},
                    '2': {const.IPV4: {'ip_addr': '20.0.2.252',
                                       'mask': '255.255.255.0', },
                          const.IPV6: {'ip_addr': '2020:db8:2::251',
                                       'prefix_len': '64'},},
                    }

vlan_options = ['2']

def define_test_cfg(cfg):
    test_cfgs = []

    ras_cfg = cfg['ras_cfg']    
    radio_mode = cfg['radio_mode']
    ip_version = cfg['ip_version']
    vlan_id = cfg['vlan_id']
    tunnel_mode = cfg['tunnel_mode']
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
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
        #Station verificaton for dvlan.
        ssid = wlan_cfg['ssid']
        wlan_cfg['ssid']= '%s-%04d' % (ssid, random.randrange(1, 9999))
        wlan_cfg['name']= wlan_cfg['ssid']
        
        dvlan = True
        test_cfgs.extend(_define_station_test_cfg(cfg, wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version, dvlan, vlan_id, tunnel_mode))
            
        #test_name = 'CB_ZD_Remove_All_Wlans'
        #common_name = 'Remove WLAN %s from ZD' % wlan_cfg['ssid']
        #test_cfgs.append(({}, test_name, common_name, 0, True))
        
        #Station verification for vlan id, id is 301 if no vlan id is set.
        wlan_cfg['ssid']= '%s-%04d' % (ssid, random.randrange(1, 9999))
        wlan_cfg['name']= wlan_cfg['ssid']
        dvlan = False        
        test_cfgs.extend(_define_station_test_cfg(cfg, wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version, dvlan, vlan_id, tunnel_mode))
            
        #test_name = 'CB_ZD_Remove_All_Wlans'
        #common_name = 'Remove WLAN %s from ZD' % wlan_cfg['ssid']
        #test_cfgs.append(({}, test_name, common_name, 0, True))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    return test_cfgs

def _define_station_test_cfg(cfg, wlan_cfg, sta_tag, browser_tag, ap_tag, ip_version, dvlan, vlan_id, tunnel_mode):
    test_cfgs = []
        
    target_ip_addr = cfg['server_ip_addr']
    target_ipv6_addr = cfg['server_ipv6_addr']
    
    default_netmask = cfg['netmask']
    default_prefix_len = cfg['prefix_len']
    
    radio_mode = cfg['radio_mode']
    
    #Get expected vlan id and username and password based on dvlan.        
    dvlan_id_user_mapping = {'dvlan': {'username': 'finance.user',
                                       'password': 'finance.user',
                                       'vlan_id' : '10'},
                             'vlan' : {'username': 'ras.eap.user',
                                       'password': 'ras.eap.user',
                                       'vlan_id': '301'},
                             }
    
    if vlan_id:
        dvlan_id_user_mapping['vlan']['vlan_id'] = vlan_id
    
    sta_wlan_cfg = copy.deepcopy(wlan_cfg)
               
    if dvlan:
        vlan_info = dvlan_id_user_mapping['dvlan']
    else:
        vlan_info = dvlan_id_user_mapping['vlan']
        
    sta_wlan_cfg['username'] = vlan_info['username']
    sta_wlan_cfg['password'] = vlan_info['password']
    expect_vlan_id = vlan_info['vlan_id']
    
    test_case_name = '[%s-%s]' % (_get_wlan_encrypt_type(wlan_cfg), sta_wlan_cfg['username'])
        
    if all_vlan_mapping.has_key(expect_vlan_id):
        vlan_ip_cfg = all_vlan_mapping[expect_vlan_id]
        vlan_ipv4_cfg = vlan_ip_cfg[const.IPV4]
        vlan_ipv6_cfg = vlan_ip_cfg[const.IPV6]
        
        if vlan_ipv4_cfg.has_key('mask'):
            ipv4_expected_sub_mask = vlan_ipv4_cfg['mask']
        else:
            ipv4_expected_sub_mask = default_netmask    
        ipv4_expected_subnet_ip_addr = vlan_ipv4_cfg['ip_addr']
        
        if vlan_ipv6_cfg.has_key('prefix_len'):
            ipv6_expected_prefix_len = vlan_ipv6_cfg['prefix_len']
        else:
            ipv6_expected_prefix_len = default_prefix_len            
        ipv6_expected_subnet_ip_addr = vlan_ipv6_cfg['ip_addr']
    else:
        raise Exception("The key [%s] is not in all vlan mapping." % (expect_vlan_id))
    
    target_ip_list = []
    if ip_version in [const.IPV4, const.DUAL_STACK]:
        target_ip_list.append(target_ip_addr)
    if ip_version in [const.IPV6, const.DUAL_STACK]:
        target_ip_list.append(target_ipv6_addr)
        
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[sta_wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True,
                       'check_wlan_timeout': 80}, test_name, common_name, 1, False))
    
    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '%sAssociate the station and verify wifi ip in subnet' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'wlan_cfg': sta_wlan_cfg,
              'browser_tag': browser_tag,
              'is_restart_adapter': True,
              'check_status_timeout': 600,
              'break_time': 60,
              'expected_subnet': '%s/%s' % (ipv4_expected_subnet_ip_addr, ipv4_expected_sub_mask),
              'expected_subnet_ipv6': '%s/%s' % (ipv6_expected_subnet_ip_addr, ipv6_expected_prefix_len),
              'ip_version': ip_version,
              'start_browser': False,
              }    
    test_cfgs.append((params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Targets_Download_File'
    common_name = '%sVerify ping target IPs' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'browser_tag': browser_tag,
              'target_ip_list': target_ip_list,
              'download_file': False,
              'close_browser': False,
              }   
    test_cfgs.append((params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_ZD_AP'
    common_name = '%sVerify station info on ZD and AP and tunnel mode' % (test_case_name,)
    params = {'sta_tag': sta_tag,
              'ap_tag': ap_tag,
              'status': 'authorized',
              'radio_mode': radio_mode,
              'wlan_cfg': sta_wlan_cfg,
              'verify_sta_tunnel_mode': tunnel_mode,
              }  
    test_cfgs.append((params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove WLAN %s from ZD' % (test_case_name, wlan_cfg['ssid'])
    test_cfgs.append(({}, test_name, common_name, 2, True))
      
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
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])
        elif radio in ['na']:
            MAXIMUM_WLAN = 8
            wlan_name = "wlan%d" % (MAXIMUM_WLAN)
            expect_wlan_info[wlan_name] = {}
            expect_wlan_info[wlan_name]['status'] = status
            expect_wlan_info[wlan_name]['encryption_cfg'] = dict(ssid=wlan_cfg['ssid'])

    return expect_wlan_info

def _get_wlan_encrypt_type(wlan_cfg):
    auth = wlan_cfg['auth']
    encryption = wlan_cfg.get('encryption')
    wpa_ver = wlan_cfg.get('wpa_ver')
    key_index = wlan_cfg.get('key_index')        
    wlan_encrypt = '%s_%s' % (auth, encryption)
    if wpa_ver:
        wlan_encrypt = wlan_encrypt + '_%s' % (wpa_ver,)
    if key_index:
        wlan_encrypt = wlan_encrypt + '_%s' % (key_index,)
        
    return wlan_encrypt

def _get_wlan_cfg(wlan_params):
    ssid = ''
    
    wlanCfg = dict(ssid=ssid, name="", auth="open", wpa_ver="", encryption="none", key_index="", key_string="",
                   username="", password="",)
    
    wlanCfg.update(wlan_params)
    
    ssid = '%s-%04d' % (_get_wlan_encrypt_type(wlanCfg), (random.randrange(1, 9999)))
    wlanCfg['ssid'] = ssid
    wlanCfg['name'] = ssid
    
    return wlanCfg

def _define_wlan_cfg_list(ras_name, vlan_id, tunnel_mode):
    '''
    Adapter method to update each wlan_cfg and generate a list of wlan_cfg
    '''
    wlan_list = []
    
    wlan_cfg = _get_wlan_cfg(dict(auth="EAP", wpa_ver="WPA2", encryption="AES", auth_svr = ras_name, dvlan=True))
    
    wlan_cfg.update({'do_tunnel': tunnel_mode})
    if vlan_id:
        wlan_cfg.update({'vlan_id': vlan_id})

    wlan_list.append(wlan_cfg)

    return wlan_list

def _define_aaa_server_cfg(server_ip):
    aaa_server_cfg = {'server_name': 'ruckus-ras-%04d' % random.randrange(1,9999),
                      'server_addr': server_ip,
                      'radius_auth_secret': '1234567890',
                      'server_port': '50001', }
    
    return aaa_server_cfg

def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                 station = (0, "g"),
                 targetap = False,
                 testsuite_name = "",
                 )

    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    
    sta_ip_list = testsuite.get_sta_ip_list(tbcfg)
    ap_sym_dict = testsuite.get_ap_sym_dict(tbcfg)
    all_ap_mac_list = testsuite.get_ap_mac_list(tbcfg)
    server_ip_addr = testsuite.get_server_ip(tbcfg)   
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg) 
    netmask = testsuite.get_ipv4_net_mask(tbcfg)
    prefix_len = testsuite.get_ipv6_prefix_len(tbcfg)
    
    zd_ip_version = testsuite.get_zd_ip_version(tbcfg)
    ap_ip_version = testsuite.get_ap_ip_version(tbcfg)
    
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
        
    tunnel_mode = raw_input("Tunnel mode (y/n)?: ").lower() == "y"
    enable_vlan = raw_input("Enable VLAN (y/n)?: ").lower() == "y"
    
    if enable_vlan:
        vlan_id = '2'
    else:
        vlan_id= None
    
    aaa_server_cfg = _define_aaa_server_cfg(server_ipv6_addr)
    wlan_cfg_list = _define_wlan_cfg_list(aaa_server_cfg['server_name'], vlan_id, tunnel_mode)
     
    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]        
        active_ap_mac = active_ap_cfg['mac']        
        
        tcfg = {'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap': active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,
                'wlan_cfg_list': wlan_cfg_list,
                'vlan_id': vlan_id,
                'tunnel_mode': tunnel_mode,
                'ras_cfg': aaa_server_cfg,
                'server_ip_addr': server_ip_addr,
                'netmask': netmask,
                'server_ipv6_addr': server_ipv6_addr,
                'prefix_len': prefix_len,
                'ip_version': zd_ip_version,
                }

        test_cfgs = define_test_cfg(tcfg)

        if ts_cfg["testsuite_name"]:
            ts_name = ts_cfg["testsuite_name"]
        else:
            if vlan_id:
                if tunnel_mode:
                    ts_name = "WLAN DVLAN TUNNEL VLAN - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)
                else:
                    ts_name = "WLAN DVLAN VLAN - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)
            else:
                if tunnel_mode:
                    ts_name = "WLAN DVLAN TUNNEL - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)
                else:
                    ts_name = "WLAN DVLAN - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)            

        ts = testsuite.get_testsuite(ts_name, "Verify WLAN with DVlan, Vlan and Tunnel - 11%s" % (target_sta_radio), combotest = True)

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



