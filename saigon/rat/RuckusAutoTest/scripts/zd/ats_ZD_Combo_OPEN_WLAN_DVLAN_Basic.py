"""
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def define_wlan_cfg():
    wlan_cfgs = []    

    wlan_cfgs.append(dict(ssid = 'OPEN-WPA2-DVLAN', auth = "PSK", wpa_ver = "WPA2", encryption = "AES",#Chico, 2015-5-5, Change WPA to WPA2
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "", use_radius = ""))    
    return wlan_cfgs


def define_test_cfg(cfg):
    test_cfgs = []
    ras_cfg = dict(server_addr = cfg['ras_ip_addr'],
                   server_port = cfg['ras_port'],
                   server_name = cfg['ras_name'],
                   radius_auth_secret = cfg['radius_auth_secret']
                   )
    vlan10_info = {'vlan': '10',
                   'expected_network': '192.168.10.252/255.255.255.0',
                   'target_ping_ip': '192.168.10.252',
                   'username': 'finance.user',
                   'password': 'finance.user'}
    default_info = {'vlan': '',
                   'expected_network': '192.168.0.252/255.255.255.0',
                   'target_ping_ip': '192.168.0.252',
                   'username': '',
                   'password': ''}
    wlan_cfg = cfg['wlan_cfg_list'][0]
    enable_zeroit_cfg = {'do_zero_it': True}
    disable_zeroit_cfg = {'do_zero_it': False}
    enable_dpsk_cfg = {'do_dynamic_psk': True}    
    disable_dpsk_cfg = {'do_dynamic_psk': False}
    enable_dvlan_cfg = {'dvlan': True}
    disable_dvlan_cfg = {'dvlan': False}
    
    
    tc1_name = 'Enable/Disable DVLAN with ZeroIT enabled'
    tc2_name = 'Cannot enable DVLAN with ZeroIT disabled'
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Configure the station %s' % cfg['target_station']    
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station'],}, test_name, common_name,  0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create the authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s]: create WLAN "%s" on ZD' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: enable ZeroIT on WLAN "%s"' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': enable_zeroit_cfg}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: enable DPSK on WLAN "%s"' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': enable_dpsk_cfg}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: enable DVLAN on WLAN "%s"' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': enable_dvlan_cfg}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = '[%s]: set the authentication server for Zero IT' % tc1_name
    test_cfgs.append(({'zero_it_auth_serv': ras_cfg['server_name']}, test_name, common_name, 2, False))
    
    wlan_cfg_for_zeroit_dvlan_user = {'ssid': wlan_cfg['ssid'],
                                      'auth': wlan_cfg['auth'],
                                      'use_radius': None,
                                      'username':vlan10_info['username'],
                                      'password':vlan10_info['password']}
    
    test_name = 'CB_ZD_Station_Config_Wlan_With_ZeroIT'
    common_name = '[%s]: associate the station with DVLAN' % tc1_name
    test_cfgs.append(({'sta_tag': 'sta1', 
                       'wlan_cfg': wlan_cfg_for_zeroit_dvlan_user}, test_name, common_name, 2, False))    
        
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]: verify the station information on ZD with DVLAN info' % tc1_name
    test_cfgs.append(({'sta_tag': 'sta1',
                       'expected_network': vlan10_info['expected_network'], 
                       'expected_station_info': {'wlan': wlan_cfg['ssid'],
                                                 'status': 'Authorized',
                                                 'vlan': vlan10_info['vlan'],
                                                 'ip': wlan_cfg_for_zeroit_dvlan_user['username']}
                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '[%s]: the station ping a target ip %s' % (tc1_name, vlan10_info['target_ping_ip'])
    test_cfgs.append(({'sta_tag': 'sta1',
                       'dest_ip': vlan10_info['target_ping_ip']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]: remove all wlans from the station 1 before disable DVLAN' % tc1_name
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: disable DVLAN on WLAN "%s"' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': disable_dvlan_cfg}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Station_Config_Wlan_With_ZeroIT'
    common_name = '[%s]: associate the station without DVLAN' % tc1_name
    test_cfgs.append(({'sta_tag': 'sta1', 
                       'wlan_cfg': wlan_cfg_for_zeroit_dvlan_user}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]: verify the station information on ZD without DVLAN' % tc1_name
    test_cfgs.append(({'sta_tag': 'sta1',
                       'expected_network': default_info['expected_network'], 
                       'expected_station_info': {'wlan': wlan_cfg['ssid'],
                                                 'status': 'Authorized',
                                                 'ip': wlan_cfg_for_zeroit_dvlan_user['username']}
                       }, test_name, common_name, 2, False))  
        
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '[%s]: the station ping a target ip %s' % (tc1_name, default_info['target_ping_ip'])
    test_cfgs.append(({'sta_tag': 'sta1',                       
                       'dest_ip': default_info['target_ping_ip']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]: remove all wlans from the station 1' % tc1_name
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: disable DPSK on WLAN "%s"' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': disable_dpsk_cfg}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: fail to enable DVLAN on WLAN "%s"' % (tc1_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': enable_dvlan_cfg, 'negative_test': True}, 
                      test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: disable ZeroIT on WLAN "%s"' % (tc2_name, wlan_cfg['ssid'])
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': disable_zeroit_cfg}, 
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: fail to enable DPSK on WLAN "%s"' % (tc2_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': enable_dpsk_cfg, 'negative_test': True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: fail to enable DVLAN on WLAN "%s"' % (tc2_name, wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg['ssid'], 'new_wlan_cfg': enable_dvlan_cfg, 'negative_test': True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = 'Remove all DPSK from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = 'Set Local Database for Zero IT'
    test_cfgs.append(({'zero_it_auth_serv': 'Local Database'}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA server setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
           
    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']    
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]

    wlan_cfg_list = define_wlan_cfg()
    tcfg = {'ras_ip_addr':ras_ip_addr,
            'ras_port' : '1812',
            'ras_name' : ras_ip_addr,
            'radius_auth_secret': '1234567890',
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'target_sta_radio': target_sta_radio,
            'wlan_cfg_list': wlan_cfg_list,
            }
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "Open WLAN - DVLAN Basic functions"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the basic setting option for OPEN WLAN with DVLAN support",
                                 interactive_mode = attrs["interactive_mode"],
                                 combotest=True)
    
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
    createTestSuite(**_dict)
    