'''
Restricted Access:
    2020:db8:1::2/64

Created on 2011-12-14
@author: cwang@ruckuswireless.com
'''

import sys
import random

import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
#from RuckusAutoTest.common import Ratutils as utils


def build_hotspot_cfg_list():
    return [{'login_page': 'http://[2020:db8:1::249]/vlogin.html',
             'name': 'Wispr_Restricted_Access_IPv6',
                          
             'restricted_ipv6_list':[
                                      {'description': '2020:db8:10::251/64',
                                      'action': 'Deny',
                                      'destination_addr': '2020:db8:10::251/64',
                                      'application': 'Any',
                                      'protocol': 'Any',
                                      'destination_port': 'Any',
                                      },
                                      {'description': '2020:db8:20::251/64',
                                      'action': 'Allow',
                                      'destination_addr': '2020:db8:20::251/64',
                                      'application': 'Any',
                                      'protocol': 'Any',
                                      'destination_port': 'Any',
                                      },                     
                                      ],                                    
             'target_ip_list':[
                               ('2020:db8:10::251', False),
                               ('2020:db8:20::251', True),  
                               ],
             }
            ]

def build_wlan_cfg(**kwargs):    
    ssid = 'rat-open-none-hotspot'    
    wlan_cfg = dict(ssid=ssid, name="", auth="open", 
                    wpa_ver="", encryption="none", 
                    key_index="", key_string="",
                    username="", password="",
                    type = "hotspot",
                    hotspot_profile = None,              
                    )
    
    wlan_cfg.update(kwargs)
    
    ssid = '%s-%04d' % (ssid, (random.randrange(1, 99)))
    wlan_cfg['ssid'] = ssid
    wlan_cfg['name'] = ssid
    
    return wlan_cfg


def fnd_hotspot_cfg(hotspot_cfg_list, hotspot_name):
    for cfg in hotspot_cfg_list:
        if cfg['name'] == hotspot_name:
            return cfg
    
    raise Exception("Haven't found it by hotspot name %s" % hotspot_name)

def build_expect_wlan_info_in_ap(tcfg, wlan_cfg):
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


def build_station_test_cfg(cfg, test_case_name, wlan_cfg, sta_tag, browser_tag, ap_tag, zd_ip_version, auth_info, hotspot_cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']
    target_ip_addr = cfg['server_ip_addr']
    netmask = cfg['netmask']
    target_ipv6_addr = cfg['server_ipv6_addr']
    prefix_len = cfg['prefix_len']
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    ipv4_expected_sub_mask = netmask
    ipv4_expected_subnet_ip_addr = target_ip_addr
    ipv6_expected_prefix_len = prefix_len
    ipv6_expected_subnet_ip_addr = target_ipv6_addr
        
    target_ip_list = hotspot_cfg.pop('target_ip_list')
#    target_ip_list = []
#    if zd_ip_version==const.DUAL_STACK:
#        target_ip_list.append(target_ip_addr)
#        target_ip_list.append(target_ipv6_addr)
#        
#    if zd_ip_version == const.IPV6:
#        target_ip_list.append(target_ipv6_addr)
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg': wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%sStart browser in station' % test_case_name
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Get_Wifi_Addr_Verify_Expect_Subnet_IPV6'
    common_name = '%sGet station Wifi IPV4 and IPV6 address and verify expect subnet' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ip_version': zd_ip_version,
                       'expected_subnet': '%s/%s' % (ipv4_expected_subnet_ip_addr, ipv4_expected_sub_mask),
                       'expected_subnet_ipv6': '%s/%s' % (ipv6_expected_subnet_ip_addr, ipv6_expected_prefix_len)
                       }, test_name, common_name, 2, False))
    
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information before auth' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'unauthorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       },
                       test_name, common_name, 2, False))
    
    allow_l = [ip for ip, allow in target_ip_list if allow]
    deny_l = [ip for ip, allow in target_ip_list if not allow]
    
    test_name = 'CB_Station_Ping_Targets_IPV6'
    common_name = '%sVerify client can ping target IPs before auth' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'allow': False,
                       'target_ip_list': allow_l + deny_l,
                       'ping_timeout_ms':30 * 1000
                       }, test_name, common_name, 2, False))

    
    param_cfgs = {'sta_tag':sta_tag,
                  'browser_tag':browser_tag,                  
                  }
    param_cfgs.update(auth_info)    
    param_cfgs.update({'original_url':"http://[2020:db8:50::251]"})
        
    test_cfgs.append((param_cfgs, 
                      'CB_Station_CaptivePortal_Perform_HotspotAuth', 
                      '%sPerform Hotspot authentication' % test_case_name, 
                      1, 
                      False))
    
    test_cfgs.append(({'sta_tag':sta_tag,
                       'browser_tag':browser_tag
                       },
                     'CB_Station_CaptivePortal_Download_File',
                     '%sDownload files from server' % test_case_name,
                     2,
                     False
                     )) 
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information after auth' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': auth_info['username']},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Targets_IPV6'
    common_name = '%sVerify client can not ping target IPs after auth' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'allow': False,
                       'target_ip_list': deny_l,
                       'ping_timeout_ms':30 * 1000,
                       }, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_Ping_Targets_IPV6'
    common_name = '%sVerify client can ping target IPs after auth' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'allow': True,
                       'target_ip_list': allow_l,
                       'ping_timeout_ms':30 * 1000,
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name,)
    test_cfgs.append(({'ssid': wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = '%sQuit browser in Station' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))
        
    return test_cfgs


def build_tcs(cfg):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']        
    zd_ip_version = cfg['zd_ip_version']
    ap_ip_version = cfg['ap_ip_version']    
    
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

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))    
    
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
    
    auth_info = {'username': 'local.username',
                'password': 'local.username'}
    test_cfgs.append((auth_info,
                      'CB_ZD_Create_Local_User',
                      'Create a local user',
                      0, 
                      False,
                      ))
    
    hotspot_cfg_list = build_hotspot_cfg_list()    
    hotspot_cfg_name_list = [x['name'] for x in hotspot_cfg_list]
    
    
    _l2s = lambda x: ",".join(x)
    test_cfgs.append(({'hotspot_profiles_list': hotspot_cfg_list},
                      'CB_ZD_Create_Hotspot_Profiles',
                      'Create HOTSPOT %s' % _l2s(hotspot_cfg_name_list),
                      0, 
                      False,                      
                      ))
        
    #Create WLANs with Hotspot services
    wlan_list = []    
    for name in hotspot_cfg_name_list:
        wlan_list.append(build_wlan_cfg(**{'ssid':'RAT_%s' % name,
                                           'hotspot_profile': name
                                         }))
    
      
    for wlan in wlan_list:
        test_case_name = "[%s]" % wlan['hotspot_profile']
        test_cfgs.append(({'wlan_cfg_list':[wlan],
                           'enable_wlan_on_default_wlan_group': True,
                           'check_wlan_timeout': 80
                           },
                          'CB_ZD_Create_Wlan',
                          '%sCreate wlan %s' % (test_case_name, wlan['ssid']),
                          0, 
                          False,
                          ))
            
        expect_ap_wlan_cfg = build_expect_wlan_info_in_ap(cfg, wlan)
        test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
        common_name = '%sVerify the wlan on the active AP' % (test_case_name)
        test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                           'ap_tag': ap_tag}, test_name, common_name, 1, False))
        
        
        hotspot_cfg = fnd_hotspot_cfg(hotspot_cfg_list, wlan['hotspot_profile'])
       
        test_cfgs.extend(build_station_test_cfg(cfg, test_case_name, 
                                                wlan, sta_tag, 
                                                browser_tag, ap_tag, 
                                                zd_ip_version, auth_info, 
                                                hotspot_cfg))
                
       
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove the wlan %s from station' % (test_case_name, wlan['ssid'],)
        test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, True))
            
        
        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = '%sRemove WLAN %s from ZD' % (test_case_name, wlan['ssid'])
        test_cfgs.append(({}, test_name, common_name, 0, True))
    
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
                 testsuite_name = "WISPr Restricted Access Testing in IPV6",
                 )

    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    
    server_ip_addr = testsuite.get_server_ip(tbcfg)   
    server_ipv6_addr = testsuite.get_server_ipv6(tbcfg)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    #zd_ipv6_addr = testsuite.get_zd_ipv6_addr(tbcfg)
    #zd_ipv4_addr = testsuite.get_zd_ipv4_addr(tbcfg)
        
    netmask = '255.255.255.0'
    prefix_len = '64'
    
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
    
    zd_ip_version = testsuite.get_zd_ip_version(tbcfg)
    ap_ip_version = testsuite.get_ap_ip_version(tbcfg)
        
    if ts_cfg['interactive_mode']:
        ts_name = "WISPr Restricted Access Testing in IPV6 - ZD %s AP %s 11%s" % (zd_ip_version, ap_ip_version, target_sta_radio)                        
    else:
        ts_name = ts_cfg['testsuite_name']   
            
    if active_ap:
        active_ap_cfg = ap_sym_dict[active_ap]        
        active_ap_mac = active_ap_cfg['mac']        
        
        tcfg = {'target_station':'%s' % target_sta,
                'radio_mode': target_sta_radio,
                'active_ap': active_ap,
                'active_ap_mac': active_ap_mac,
                'all_ap_mac_list': all_ap_mac_list,                                
                'prefix_len': prefix_len,
                'netmask':netmask,
                'zd_ip_version': zd_ip_version,
                'ap_ip_version': ap_ip_version, 
                'server_ip_addr':server_ip_addr,
                'server_ipv6_addr':server_ipv6_addr                                                
                }

        test_cfgs = build_tcs(tcfg)
            
            
        ts = testsuite.get_testsuite(ts_name, "WISPr Restricted Access Testing in IPV6", combotest = True)

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
        