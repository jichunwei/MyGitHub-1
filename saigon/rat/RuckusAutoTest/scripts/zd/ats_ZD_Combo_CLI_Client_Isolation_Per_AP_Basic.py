"""
enable client isolation and whitelist is none
    [client isolation disabled default]Wlan disable client isolation, verify sta1,sta2 ping, connect web success
    Wlan with VLAN enable client isolation, without whitelist
    [with VLAN, same wlan, same AP]sta1 can not ping sta2
    [with VLAN, same wlan, different AP] sta1 can ping sta2
    [with VLAN, different wlan, same AP] sta1 can not ping sta2
    [with VLAN, different wlan, different AP] sta1 can ping sta2
    Wlan without VLAN enable client isolation, without whitelist
    [without VLAN, same wlan, same AP] sta1 can not ping sta2
    [without VLAN, same wlan, different AP] sta1 can ping sta2
    [without VLAN, different wlan, same AP] sta1 can not ping sta2
    [without VLAN, different wlan, different AP] sta1 can ping sta2
    Sta1,sta2 connect to different radio, repeat step 8 to 11
    Create wlan with tunnel, repeat step 8 to 11
    Sta1,sta2 connect to different radio, repeat step 8 to 11
    Sta1,sta2 in different subnet, repeat step 8 to 11
    
Created on 2013-7-19
@author: Guo.Can@odc-ruckuswireless.com
"""

import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

ci_wlan1_cfg = {"name" : "Rqa-auto-RAT-CI-Per-AP-1",
            "ssid" : "Rqa-auto-RAT-CI-Per-AP-1",
            "auth" : "open",
            "encryption" : "none",
            }

ci_wlan2_cfg = {"name" : "Rqa-auto-RAT-CI-Per-AP-2",
            "ssid" : "Rqa-auto-RAT-CI-Per-AP-2",
            "auth" : "open",
            "encryption" : "none",
            }

def build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2):
    tcs = []    
                
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
  
    tcs.append(({'active_ap': active_ap1,
                 'ap_tag':'AP_01'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP 1',
                0,
                False))

    tcs.append(({'active_ap': active_ap2,
                 'ap_tag':'AP_02'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP 2',
                0,
                False))

    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': sta1_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 1', 
                   0, 
                   False))

    tcs.append(({'sta_tag': 'sta_2', 
                   'sta_ip_addr': sta2_ip_addr}, 
                   'CB_ZD_Create_Station', 
                   'Create the station 2', 
                   0, 
                   False))
    
    test_list = _generate_test_cfg()

    for test_case in test_list:
        tcs.extend(build_stcs_main(test_case))
                
    tcs.append(({}, 
                'CB_ZD_CLI_Remove_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                True))
        
    return tcs

def _generate_test_cfg():
    test_cfg = []
    
    test_cfg.append(({'tc_name' : '[client isolation disabled default]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : None,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : None,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True,}))
    
    test_cfg.append(({'tc_name' : '[with VLAN, same wlan, same AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False}))
    
    test_cfg.append(({'tc_name' : '[with VLAN, same wlan, different AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True}))

    test_cfg.append(({'tc_name' : '[with VLAN, different wlan, same AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : False,
                              'vlan_id' : 10,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False}))

    test_cfg.append(({'tc_name' : '[with VLAN, different wlan, different AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : False,
                              'vlan_id' : 10,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True}))

    test_cfg.append(({'tc_name' : '[without VLAN, same wlan, same AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : False,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False}))
    
    test_cfg.append(({'tc_name' : '[without VLAN, same wlan, different AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : False,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True}))

    test_cfg.append(({'tc_name' : '[without VLAN, different wlan, same AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : False}))

    test_cfg.append(({'tc_name' : '[without VLAN, different wlan, different AP]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_02',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True}))

    test_cfg.append(({'tc_name' : '[with tunnel]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'tunnel_mode' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'tunnel_mode' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11a/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11a/n',
                  'ping_result' : False}))
    
    test_cfg.append(({'tc_name' : '[different radio]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11a/n',
                  #@author: Jane.Guo @since: 2013-09 stations couldn't ping each other when on different radios of same AP
                  'ping_result' : False}))

    test_cfg.append(({'tc_name' : '[different radio, with tunnel]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'tunnel_mode' : True,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : False,
                              'tunnel_mode' : True,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11a/n',
                  #@author: Jane.Guo @since: 2013-09 stations couldn't ping each other when on different radios of same AP
                  'ping_result' : False}))

    test_cfg.append(({'tc_name' : '[different subnet]',
                  'wlan1' : { 'wlan_cfg' : ci_wlan1_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 10,
                            },
                  'wlan2' : { 'wlan_cfg' : ci_wlan2_cfg,
                              'isolation_per_ap' : True,
                              'vlan_id' : 20,
                            },
                  'AP1' : 'AP_01',
                  'AP1_radio' : '802.11g/n',
                  'AP2' : 'AP_01',
                  'AP2_radio' : '802.11g/n',
                  'ping_result' : True}))

    return test_cfg
    
def build_stcs_main(test_case):
    tcs = []
    
    tc_name = test_case['tc_name']
    wlan1 = test_case['wlan1']
    wlan1_cfg = wlan1['wlan_cfg']
    wlan2 = test_case['wlan2']
    wlan2_cfg = wlan2['wlan_cfg']
    AP1 = test_case['AP1']
    AP1_radio = test_case['AP1_radio']
    AP2 = test_case['AP2']
    AP2_radio = test_case['AP2_radio']
    ping_result = test_case['ping_result']
    
    wlan1_default_cfg = deepcopy(wlan1_cfg)
    wlan1_default_cfg.update({'isolation_per_ap': wlan1.get('isolation_per_ap'),
                              'vlan_id': wlan1.get('vlan_id'),
                              'tunnel_mode': wlan1.get('tunnel_mode'),
                              })

    tcs.append(({'wlan_conf':wlan1_default_cfg},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN 1 from CLI' % tc_name,
                1,
                False))
    
    tcs.append(({},
                'CB_ZDCLI_Get_Wlan_By_SSID',
                '%sGet ZD WLAN 1 Info via CLI' % tc_name,
                2,
                False))

    tcs.append(({},
                'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                '%sVerify Wlan 1 Info Between CLI Set and CLI Get' % tc_name,
                2,
                False))
        
    if not wlan2_cfg == wlan1_cfg:
        wlan2_default_cfg = deepcopy(wlan2_cfg)
        wlan2_default_cfg.update({'isolation_per_ap': wlan2.get('isolation_per_ap'),
                                  'vlan_id': wlan2.get('vlan_id'),
                                  'tunnel_mode': wlan2.get('tunnel_mode'),
                                  })
        tcs.append(({'wlan_conf':wlan2_default_cfg},
                    'CB_ZD_CLI_Create_Wlan',
                    '%sCreate WLAN 2 from CLI' % tc_name,
                    2,
                    False))
        
        tcs.append(({},
                    'CB_ZDCLI_Get_Wlan_By_SSID',
                    '%sGet ZD WLAN 2 Info via CLI' % tc_name,
                    2,
                    False))
    
        tcs.append(({},
                    'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get',
                    '%sVerify Wlan 2 Info Between CLI Set and CLI Get' % tc_name,
                    2,
                    False))
        
    else:
        wlan2_default_cfg = wlan1_default_cfg
        
    tcs.append(({'wlan_cfg':wlan1_default_cfg,
                 'ap_tag':AP1,
                 'ap_radio': AP1_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 1st' % tc_name,
                2,
                False
                ))
         
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan1_default_cfg,
                 'wlan_ssid': wlan1_default_cfg['ssid'],
                 'ap_tag': AP1}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 1 to wlan' % tc_name, 
                  2, 
                  False))
        
    tcs.append(({'wlan_cfg':wlan2_default_cfg,
                 'ap_tag':AP2,
                 'ap_radio': AP2_radio},
                'CB_AP_CLI_Get_BSSID',
                '%sGet BSSID for AP 2nd' % tc_name,
                2,
                False
                ))
            
    tcs.append(({'sta_tag': 'sta_2', 
                 'wlan_cfg': wlan2_default_cfg,
                 'wlan_ssid': wlan2_default_cfg['ssid'],
                 'ap_tag': AP2}, 
                 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_BSSID', 
                  '%sAssociate the station 2 to wlan' % tc_name, 
                  2, 
                  False))
    
    if ping_result:
        condition = 'allowed'
    else:
        condition = 'disallowed'
        
    tcs.append(({'src_sta_tag': 'sta_1',
                 'dst_sta_tag': 'sta_2',
                 'condition': condition,
                 'clean_arp_before_ping': True},
                 'CB_ZD_Client_Ping_Another', 
                  '%sStation Ping Another Station is %s' % (tc_name,condition), 
                  2,
                  False))
    
    #ping web,always true    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sStation Ping Dest Linux is Allowed' % tc_name, 
                  2, 
                  False))
    wlan_list = []
    wlan_list.append(wlan1_default_cfg['ssid'])
    if not wlan2_cfg == wlan1_cfg:
        wlan_list.append(wlan2_default_cfg['ssid'])

    tcs.append(({'wlan_name_list':wlan_list}, 
                'CB_ZD_CLI_Remove_Wlans', 
                '%sClean all WLANs for cleanup ENV' % tc_name, 
                2, 
                True)) 
    #web success? no lib,no class
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Client Isolation Per AP Basic"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
        
    ts_name = attrs['testsuite_name']
    sta1_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the first wireless station: ")
    sta2_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose the second wireless station: ")
    
    if not sta1_ip_addr or not sta2_ip_addr:
        raise Exception("Get station fail, sta1: %s, sta2: %s" % (sta1_ip_addr,sta2_ip_addr))

    if sta1_ip_addr == sta2_ip_addr:
        raise Exception("Please select different station")
    
    ap_sym_dict = tbcfg['ap_sym_dict']
        
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    if len(active_ap_list) < 2:
        raise Exception("Need two active AP:%s" % active_ap_list)
    
    active_ap1 = active_ap_list[0]
    active_ap2 = active_ap_list[1]
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Client Isolation Per AP Basic", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta1_ip_addr, sta2_ip_addr, active_ap1, active_ap2)

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
    