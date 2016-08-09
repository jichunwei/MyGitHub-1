'''
1) Verify dhcp option82 contents in a dhcp client request from wlan interface.
2) Change dhcp option 82 from enabled to disabled, verify dhcp request and reply.
3) Verify dhcp option 82 when it's in default mode [disabled].

Created on 2012-2-15
@author: cwang@ruckuswireless.com
'''


import time
import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

wlan_cfg = {"name" : "RAT-Open-None-Option82-Testing",
            "ssid" : "RAT-Open-None-Option82-Testing",
            "auth" : "open",
            "encryption" : "none",
            "option82":None,
            "vlan_id":None,
            }

vlan_cfg = {}

'''
vlan_cfg = {"1":{"server_ip_addr":"192.168.0.252",
                 "if":"eth1"},
            "2":{"server_ip_addr":"20.0.2.253",
                 "if":"eth1.2"
                 },                    
            }
'''

def build_tcs(target_station, all_aps_mac_list, ap_radio, active_ap):
    tcs = []    
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Remove All WLAN Groups',
                0,
                False))
    
                  
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Remove all WLANs', 
                0, 
                False))
    
    tcs.append(({'cfg_type': 'teardown', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Reset all WLAN Services', 
                 0, 
                 False))
       
    #@author: yuyanan @since: 2015-1-13 @change:optimize:  capture package will contain opt82 infor on sta if enable dhcp relay on l3 SW
    tcs.append(({'dhcp_relay_conf': {'vlans': ['301'], 'enable': False}} ,
                 'CB_L3Switch_Configure_DHCP_Relay', 
                 'Disable Dhcp Relay on L3 Switch', 
                 0, 
                 False)) 
   
    
    default_cfg = deepcopy(wlan_cfg)
    default_cfg['option82'] = None
    tc_name = '[Verify dhcp option82 contents in default]'
    tcs.extend(build_stcs(default_cfg, target_station, tc_name, all_aps_mac_list))
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                '%sRemove all WLANs' % tc_name, 
                0, 
                False))
    
    enable_cfg = deepcopy(wlan_cfg)
    enable_cfg['option82'] = True
    tc_name = '[Verify dhcp option82 enabled contents]'
    tcs.extend(build_stcs(enable_cfg, target_station, tc_name, all_aps_mac_list, ap_radio, active_ap))
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                '%sRemove all WLANs' % tc_name, 
                0, 
                False))
    
    disable_cfg = deepcopy(wlan_cfg)
    disable_cfg['option82'] = False
    tc_name = '[Verify dhcp option82 disabled contents]'
    tcs.extend(build_stcs(disable_cfg, target_station, tc_name, all_aps_mac_list))
    
    #@author: yuyanan @since: 2015-1-13 @change:optimize enable dhcp relay on l3 sw
    tcs.append(({'dhcp_relay_conf': {'vlans': ['301'], 'enable': True}} ,
                 'CB_L3Switch_Configure_DHCP_Relay', 
                 'Enable Dhcp Relay on L3 Switch', 
                 0, 
                 True))
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlan_Groups', 
                'Clean All WLAN Groups',
                0,
                True))
    
                  
    tcs.append(({}, 
                'CB_ZD_Remove_All_Wlans', 
                'Clean all WLANs for cleanup ENV', 
                0, 
                True))
    
    tcs.append(({'cfg_type': 'teardown', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Restore all WLAN Services', 
                 0, 
                 True))
        
    return tcs


def build_stcs(wlan_cfg, target_station, tc_name, all_aps_mac_list = None, ap_radio = None, active_ap = None):
    tcs = []
    tcs.append(({'wlan_cfg_list':[wlan_cfg]},
                'CB_ZD_Create_Wlan',
                '%sCreate WLAN from GUI' % tc_name,
                0,
                False
                )) 
    
    if active_ap:
        
        tcs.append(({'active_ap':active_ap,
                     'ap_tag':'active_ap'},                                        
                    'CB_ZD_Create_Active_AP',
                    '%sFind the Active AP' % tc_name,
                    1,
                    False
                    ))
        
        tcs.append(({
                     'cfg_type': 'init', 
                     'all_ap_mac_list': all_aps_mac_list}, 
                     'CB_ZD_Config_AP_Radio', 
                     '%sDisable WLAN Service' % tc_name, 
                     2, 
                     False))
        
       
        tcs.append(({'ap_tag': 'active_ap',                      
                     'cfg_type': 'config',
                     'ap_cfg': {'wlan_service': True, 'radio': ap_radio}},
                     'CB_ZD_Config_AP_Radio',
                     '%sEnable WLAN Service' % tc_name,
                     2, 
                     False
                    ))
    else:
        tcs.append(({'cfg_type': 'teardown', 
                     'all_ap_mac_list': all_aps_mac_list}, 
                     'CB_ZD_Config_AP_Radio', 
                     '%sReset all WLAN Services' % tc_name, 
                     1, 
                     False))
    
    tcs.append(({'sta_tag': 'sta_1', 
                       'sta_ip_addr': target_station}, 
                       'CB_ZD_Create_Station', 
                       '%sGet the station' % tc_name, 
                       2, 
                       False))
    
    if wlan_cfg['vlan_id']:        
        params = ' -i %s -f "udp port 67 and udp port 68"' % vlan_cfg[wlan_cfg['vlan_id']]['if']
    else:
        params = ' -i %s -f "udp port 67 and udp port 68"' % vlan_cfg["1"]['if']
    
    tcs.append(({'params': params},
                'CB_Server_Start_Tshark',
                '%sStart Tshark from DHCP Server' % tc_name,
                2,
                False
                ))
    
    tcs.append(({'params': ' -f "udp port 67 and udp port 68" -p',
                 'sta_tag': 'sta_1'
                 },
                'CB_Station_Start_Tshark',
                '%sStart Tshark from station' % tc_name,
                2,
                False
                ))
    
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg}, 
                 'CB_ZD_Associate_Station_1', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))    

    
    tcs.append(({'sta_tag': 'sta_1'}, 
                  'CB_ZD_Get_Station_Wifi_Addr_1', 
                  '%sGet wifi address' % tc_name, 
                  2, 
                  False))
    
    
    tcs.append(({},
                'CB_Server_Stop_Tshark',
                '%sStop Tshark from DHCP Server' % tc_name,
                2,
                False
                ))
    
    tcs.append(({'sta_tag': 'sta_1'},
                'CB_Station_Stop_Tshark',
                '%sStop Tshark from station' % tc_name,
                2,
                False
                ))
    
    if wlan_cfg['vlan_id']:        
        server_ip_addr = vlan_cfg[wlan_cfg['vlan_id']]['server_ip_addr']
    else:
        server_ip_addr = vlan_cfg["1"]['server_ip_addr']
        
    tcs.append(({'sta_tag': 'sta_1',
                 'option82':wlan_cfg['option82'],
                 'server_ip_addr': server_ip_addr,
                 },
                'CB_Server_Verify_Option82',
                '%sVerify package from DHCP Server' % tc_name,
                2, 
                False
                ))
    
    tcs.append(({'sta_tag': 'sta_1',
                 'option82':wlan_cfg['option82'],
                 'src_ip_addr':server_ip_addr
                 },
                'CB_Station_Verify_Option82',
                '%sVerify package from station' % tc_name,
                2, 
                False
                ))
    
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Valencia DHCP option82 Basic",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    
    server_ip_1 = raw_input("Please input server ip addr for vlan 1[Default is 192.168.0.252]")
    if not server_ip_1:
        server_ip_1 = '192.168.0.252'
    server_if_1 = raw_input("Plase input server interface for vlan 1[Default is eth1]")
    
    if not server_if_1:
        server_if_1 = 'eth1'
    server_ip_2 = raw_input("Please input server ip addr for vlan 2[Default is 20.0.2.253]")
    if not server_ip_2:
        server_ip_2 = '20.0.2.253'
        
    server_if_2 = raw_input("Plase input server interface for vlan 2[Default is %s.2]" % server_if_1)
    if not server_if_2:
        server_if_2 = '%s.2' % server_if_1
        
    vlan_cfg.update({"1":{"server_ip_addr": server_ip_1,
                          "if": server_if_1},
                     "2":{"server_ip_addr": server_ip_2,
                          "if": server_if_2},
                     })
        
    if attrs["interactive_mode"]:
        ts_name = "Valencia DHCP option82 Basic"
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:
        ts_name = attrs["testsuite_name"]
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name            
            break
        
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Valencia DHCP option82 Basic", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta_ip_addr, all_aps_mac_list, target_sta_radio, active_ap)

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
    