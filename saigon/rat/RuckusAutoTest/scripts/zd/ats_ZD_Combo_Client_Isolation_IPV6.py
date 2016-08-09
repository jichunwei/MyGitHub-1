"""
Verify wlan with different client isolation setting works well.

    Verify wlan with different client isolation setting works well for dual stack and ipv6 only.
    Encryption type coverage:
        Open-none
    expect result: All steps should result properly.
    
    How to:
        1) Disable all AP's wlan service
        4) Enable active AP's wlan service based on radio   
        5) Create a wlan and make sure it is in default wlan group
        6) Station 01 associate the wlan
        7) Station 02 associate the wlan
        7) Verify traffic between two stations:
            for none, ping successfully between stations
            for local and full, ping failed between stations
        8) Verify traffic from station to zd and server in subnet
            for none and local, ping zd and server successfully.
            for full, can not ping zd and server successfully.
        9) Verify traffic from station to server in different subnet.
            for none, full, local, can ping server in different subnet.
    
Created on 2012-4-05
@author: cherry.cheng@ruckuswireless.com
"""

import sys
import time

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

def define_wlan_cfg(ssid, isolation_option):
    wlan_cfg = dict(ssid = 'rat-client-isolation-01', auth = "open", wpa_ver = "", encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", use_radius = False,
                           do_isolation = "local")
    
    wlan_cfg['do_isolation'] = isolation_option
    
    return wlan_cfg

def define_test_cfg(cfg):
    test_cfgs = []
    
    wlan_cfg = cfg['wlan_cfg']
    radio_mode = cfg['radio_mode']    
    ip_version = cfg['ip_version']
    
    isolation_option = cfg['isolation_option']
    
    sta_tag_01 = "sta01%s" % radio_mode
    sta_tag_02 = "sta02%s" % radio_mode
    
    browser_tag_01 = "browser%s" % radio_mode
    browser_tag_02 = "browser%s" % radio_mode
    
    ap_tag = "ap%s" % radio_mode
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station %s' % cfg['target_station_01'] 
    test_cfgs.append(({'sta_ip_addr': cfg['target_station_01'],
                       'sta_tag': sta_tag_01}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station %s' % cfg['target_station_02']
    test_cfgs.append(({'sta_ip_addr': cfg['target_station_02'],
                       'sta_tag': sta_tag_02}, test_name, common_name, 0, False))
    
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
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = "Create a open-none wlan with %s via GUI" % isolation_option
    test_cfgs.append(( {'wlan_cfg_list':[wlan_cfg]}, test_name, common_name, 0, False))

    wg_name = 'Default'
    wg_cfg = dict(name = wg_name, description = None, ap_rp = {radio_mode: {'wlangroups': wg_name}},)
    test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    test_cfgs.append(({'wgs_cfg': wg_cfg,
                       'ap_tag': ap_tag, },
                  test_name, common_name, 0, False))
        
    test_case_name = "[Client Isolation %s]" % (isolation_option)
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '%s Associate the station %s and get wifi ip addresss' % (test_case_name, sta_tag_01)
    params = {'sta_tag': sta_tag_01,
              'wlan_cfg': wlan_cfg,
              'browser_tag': browser_tag_01,
              'verify_ip_subnet': False,
              'ip_version': ip_version,
              'start_browser': False,
              }    
    test_cfgs.append((params, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Get_IP_Verify_Subnet'
    common_name = '%s Associate the station %s and get wifi ip addresss' % (test_case_name, sta_tag_02)
        
    params = {'sta_tag': sta_tag_02,
              'wlan_cfg': wlan_cfg,
              'browser_tag': browser_tag_02,
              'verify_ip_subnet': False,
              'ip_version': ip_version,
              'start_browser': False,
              }    
    test_cfgs.append((params, test_name, common_name, 2, False))
    
    #When client isolation is local and full, two clients can't access each other.    
    if isolation_option in ['local', 'full']:
        is_allow_clients = False
    else:
        is_allow_clients = True
    
    test_name = 'CB_ZD_Verify_Clients_Connectivity_IPV6'
    if is_allow_clients:
        common_name = '%s Verify can ping between station [%s] and [%s]' % (test_case_name, sta_tag_01, sta_tag_02)
    else:
        common_name = "%s Verify can't ping between station [%s] and [%s]" % (test_case_name, sta_tag_01, sta_tag_02)
    test_cfgs.append(({'station_01_tag': sta_tag_01,
                       'station_02_tag': sta_tag_02,
                       'is_allow': is_allow_clients,
                       'ip_version': ip_version}, 
                      test_name, common_name, 2, False))
    
    #Verify ping zd and server in same subnet.
    if isolation_option == 'full':
        is_allow_zd_subnet = False
    else:
        is_allow_zd_subnet = True
        
    server_ip_addr = cfg['server_ip_addr']
    server_ipv6_addr= cfg['server_ipv6_addr']
    zd_ipv4_addr = cfg['zd_ipv4_addr']
    zd_ipv6_addr = cfg['zd_ipv6_addr']
    same_subnet_ip_list = []
    if ip_version in [const.IPV4, const.DUAL_STACK]:
        same_subnet_ip_list.append(zd_ipv4_addr)
        same_subnet_ip_list.append(server_ip_addr)
        
    if ip_version in [const.IPV6, const.DUAL_STACK]:
        same_subnet_ip_list.append(zd_ipv6_addr)
        same_subnet_ip_list.append(server_ipv6_addr)
    
    test_name = 'CB_Station_Ping_Targets_IPV6'
    if is_allow_zd_subnet:
        common_name = '%s Verify station %s can ping ZD and ipv6 server in same subnet' % (test_case_name, sta_tag_01)
    else:
        common_name = "%s Verify station %s can't ping ZD and ipv6 server in same subnet" % (test_case_name, sta_tag_01)
    test_cfgs.append(({'sta_tag': sta_tag_01,
                       'allow': is_allow_zd_subnet,
                       'target_ip_list': same_subnet_ip_list,
                       'ping_timeout_ms':30 * 1000
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Targets_IPV6'
    if is_allow_zd_subnet:
        common_name = '%s Verify station %s can ping ZD and ipv6 server in same subnet' % (test_case_name, sta_tag_02)
    else:
        common_name = "%s Verify station %s can't ping ZD and ipv6 server in same subnet" % (test_case_name, sta_tag_02)
    test_cfgs.append(({'sta_tag': sta_tag_02,
                       'allow': is_allow_zd_subnet,
                       'target_ip_list': same_subnet_ip_list,
                       'ping_timeout_ms':30 * 1000
                       }, test_name, common_name, 2, False))
    
    #Verify can ping different subnet ip address.
    web_ipv4_addr = cfg['web_ipv4_addr']
    web_ipv6_addr = cfg['web_ipv6_addr']
    
    is_allow_diff_subnet = True
    
    diff_subnet_ip_list = []
    if ip_version in [const.IPV4, const.DUAL_STACK]:
        diff_subnet_ip_list.append(web_ipv4_addr)
    if ip_version in [const.IPV6, const.DUAL_STACK]:
        diff_subnet_ip_list.append(web_ipv6_addr)
        
    test_name = 'CB_Station_Ping_Targets_IPV6'
    common_name = '%s Verify station %s can ping server in different subnet' % (test_case_name, sta_tag_01)
    test_cfgs.append(({'sta_tag': sta_tag_01,
                       'allow': is_allow_diff_subnet,
                       'target_ip_list': diff_subnet_ip_list,
                       'ping_timeout_ms':30 * 1000
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Targets_IPV6'
    common_name = '%s Verify station %s can ping server in different subnet' % (test_case_name, sta_tag_02)
    test_cfgs.append(({'sta_tag': sta_tag_02,
                       'allow': is_allow_diff_subnet,
                       'target_ip_list': diff_subnet_ip_list,
                       'ping_timeout_ms':30 * 1000
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove WLAN %s from ZD' % wlan_cfg['ssid']
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station %s' % cfg['target_station_01']
    test_cfgs.append(({'sta_tag': sta_tag_01}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station %s' % cfg['target_station_02']
    test_cfgs.append(({'sta_tag': sta_tag_02}, test_name, common_name, 0, False))

    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station1 = (0,"g"),
                 station2 = (1,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    
    sta_ip_list = testsuite.get_sta_ip_list(tbcfg)
    ap_sym_dict = testsuite.get_ap_sym_dict(tbcfg)
    all_ap_mac_list = testsuite.get_ap_mac_list(tbcfg)
    
    zd_ipv4_addr = testsuite.get_zd_ipv4_addr(tbcfg)
    zd_ipv6_addr = testsuite.get_zd_ipv6_addr(tbcfg)
    server_ip_addr = testsuite.get_server_ip(tbcfg)   
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg)
    web_ipv4_addr = '172.16.10.252'
    web_ipv6_addr = '2020:db8:50::251'
    
    zd_ip_version = testsuite.get_zd_ip_version(tbcfg)
    ap_ip_version = testsuite.get_ap_ip_version(tbcfg)

    if attrs["interactive_mode"]:
        target_sta_01 = testsuite.get_target_station(sta_ip_list, "Pick an wireless station: ")
        target_sta_01_radio = testsuite.get_target_sta_radio()

        target_sta_02 = testsuite.get_target_station(sta_ip_list, "Pick an wireless station: ")
        target_sta_02_radio = testsuite.get_target_sta_radio()

    else:
        target_sta_01 = sta_ip_list[attrs["station1"][0]]
        target_sta_01_radio = attrs["station1"][1]
        target_sta_02 = sta_ip_list[attrs["station2"][0]]
        target_sta_02_radio = attrs["station2"][1]

    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_01_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break
    
    if active_ap:
        for isolation_option in ['none','local','full']:
            ssid = "rat-client-isolation-%s" % (time.strftime("%H%M%S"))
            wlan_cfg = define_wlan_cfg(ssid, isolation_option)
            
            active_ap_cfg = ap_sym_dict[active_ap]        
            active_ap_mac = active_ap_cfg['mac']
            
            tcfg = {'ip_version': zd_ip_version,
                    'target_station_01':'%s' % target_sta_01,
                    'target_station_02':'%s' % target_sta_02,
                    'active_ap': active_ap,
                    'active_ap_mac': active_ap_mac,
                    'all_ap_mac_list': all_ap_mac_list,                    
                    'radio_mode': target_sta_01_radio,
                    'target_sta_01_radio': target_sta_01_radio,
                    'target_sta_02_radio': target_sta_02_radio,
                    'wlan_cfg': wlan_cfg,
                    'ssid': ssid,
                    'isolation_option': isolation_option,
                    'server_ip_addr': server_ip_addr,
                    'server_ipv6_addr': server_ipv6_addr,
                    'zd_ipv4_addr': zd_ipv4_addr,
                    'zd_ipv6_addr': zd_ipv6_addr,
                    'web_ipv4_addr': web_ipv4_addr,
                    'web_ipv6_addr': web_ipv6_addr,
                    }
            test_cfgs = define_test_cfg(tcfg)
            
            ts_name = 'ZD GUI - Client Isolation %s Sta01-11%s Sta02-11%s ZD %s AP %s' % (isolation_option, 
                                                                                                 target_sta_01_radio, 
                                                                                                 target_sta_02_radio,
                                                                                                 zd_ip_version, 
                                                                                                 ap_ip_version,)
            ts = testsuite.get_testsuite(ts_name,
                                         "Verify client isolation with Isolation set to %s" % isolation_option,
                                         interactive_mode = attrs["interactive_mode"],
                                         combotest=True)

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
    createTestSuite(**_dict)
