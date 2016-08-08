'''
1. Create Wlans with different authentication and encrytion types
authentication type : open/shared/802.1X EAP
encryption type:wpa/wpa2/wpa mixed/wep-64/wep-128/none
2. Verify station can ping success if the station with static ip equal to DHCP ip


Created on 2013-5-13
@author: Guo.Can@odc-ruckuswireless.com
'''

import sys
import random

import libZD_TestSuite as testsuite

from copy import deepcopy
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant
from RuckusAutoTest.common import Ratutils as utils

ip_cfg = {"static_cfg" : dict(source = 'Static', addr = '192.168.0.231', mask = '255.255.255.0', gateway = '192.168.0.253'),
          "dhcp_cfg" : dict(source = 'dhcp', addr = '', mask = '', gateway = '')}

def build_tcs(target_station, all_aps_mac_list, ap_radio, active_ap, active_ap_mac, ras_ip_addr):
    tcs = [] 
    #@ZJ ZF-10187 Disable dhcp relay setting on l3 switch**************************************************
    target_vlan = ['301']
    tcs.append(({'dhcp_relay_conf': {'enable': False,
                                    'vlans': target_vlan}}, 
                'CB_L3Switch_Configure_DHCP_Relay', 
                'Modify the configuration on L3 switch: disable DHCP Relay', 
                0, 
                False))  
                      
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
  
    tcs.append(({'active_ap': active_ap,
                 'ap_tag':'active_ap'},                                       
                'CB_ZD_Create_Active_AP',
                'Create the Active AP',
                0,
                False))
    
    tcs.append(({'cfg_type': 'init', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Config All APs Radio - Disable WLAN Service', 
                 0, 
                 False))
    
   
    tcs.append(({'ap_tag': 'active_ap',                      
                 'cfg_type': 'config',
                 'ap_cfg': {'wlan_service': True, 'radio': ap_radio}},
                 'CB_ZD_Config_AP_Radio',
                 'Config active AP Radio %s - Enable WLAN Service' % ap_radio,
                 0, 
                 False))    

    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': target_station}, 
                   'CB_ZD_Create_Station', 
                   'Create the station', 
                   0, 
                   False))
              
    ras_server_name = 'radius_force_dhcp'
    
    tcs.append(({'auth_ser_cfg_list': [{'radius_auth_secret': '1234567890', 
                                        'server_name':  ras_server_name, 
                                        'server_port': '1812', 
                                        'server_addr':  ras_ip_addr, 
                                        'radius_auth_method': 'pap'}]}, 
                   'CB_ZD_Create_Authentication_Server', 
                   'Create Radius Authentication Server', 
                   0, 
                   False))
                         
    wlan_list = _generate_wlan_list(ras_ip_addr, ras_server_name)
    for wlan_cfg in wlan_list:
        tc_name = "[%s]" % wlan_cfg['ssid']
        tcs.extend(build_stcs_wlan(wlan_cfg, ip_cfg, tc_name))  
           
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
    
    tcs.append(({'server_name_list': [ras_server_name]},
                'CB_ZD_CLI_Delete_AAA_Servers',
                'Remove AAA server',
                0,
                True))
    
    tcs.append(({'cfg_type': 'teardown', 
                 'all_ap_mac_list': all_aps_mac_list}, 
                 'CB_ZD_Config_AP_Radio', 
                 'Restore all WLAN Services', 
                 0, 
                 True))
    
    #**********************************************************
    tcs.append(({'dhcp_relay_conf': {'enable': True,
                                    'vlans': target_vlan}}, 
                'CB_L3Switch_Configure_DHCP_Relay', 
                'Restoring the configuration on switch: enable DHCP Relay', 
                0, 
                True))
                    
    return tcs

def _generate_wlan_list(ras_ip_addr, ras_server_name):
    
    wlan_config_list = []
    wlan_list = []
    # Open
    wlan_list.append(dict(auth = "open", encryption = "none"))

    # Shared-WEP-64 Shared-WEP-128 don't support from 9.7

    # WPA-PSK-TKIP is not supported

    # WPA2-PSK-AES
    wlan_list.append(dict(auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                  sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                  key_string = utils.make_random_string(random.randint(8, 63), "hex")))
    
    # WPA-Mixed-PSK-Auto
    wlan_list.append(dict(auth = "PSK", wpa_ver = "WPA-Mixed", encryption = "Auto",
                  sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                  key_string = utils.make_random_string(random.randint(8, 63), "hex")))

    key_string_wep64_0  = utils.make_random_string(10, "hex"),
    key_string_wep128_0 = utils.make_random_string(26, "hex"),

    if type(key_string_wep64_0) == type((1,2)):
        key_string_wep64 = key_string_wep64_0[0]
    else:
        key_string_wep64 = key_string_wep64_0
    
    if type(key_string_wep128_0) == type((1,2)):
        key_string_wep128 = key_string_wep128_0[0]
    else:
        key_string_wep128 = key_string_wep128_0
    
    # open-WEP-64    
    wlan_list.append(dict(auth = "open", encryption = "WEP-64",key_index = "1",
                  sta_auth = "open", sta_wpa_ver = "", sta_encryption = "WEP-64",
                  key_string = key_string_wep64))
    
    # open-WEP-128   
    wlan_list.append(dict(auth = "open", encryption = "WEP-128",key_index = "1",
                  sta_auth = "open", sta_wpa_ver = "", sta_encryption = "WEP-128",
                  key_string = key_string_wep128))
    #eap+wpa2+tkip is not supported
    #eap+wpa+aes is not supported 
    #eap+wpa2+aes    
    wlan_list.append(dict(auth = "dot1x-eap", encryption = "AES", algorithm = 'AES',
                   wpa_ver = "WPA2", sta_encryption = "AES",sta_auth = 'EAP',
                   auth_server = ras_server_name,
                   username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                   ras_secret = "1234567890", use_radius = True))
    
    #eap+wpa-mixed+auto
    wlan_list.append(dict(auth = "dot1x-eap", encryption = "auto", algorithm = 'auto',
                   wpa_ver = "WPA-Mixed", sta_encryption = "TKIP",sta_auth = 'EAP',
                   auth_server = ras_server_name,
                   username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                   ras_secret = "1234567890", use_radius = True))
    
    # dot1x-eap none doesn't support in our client

    wlan_list.append(dict(auth = "dot1x-eap", encryption = "wep-64",
                   sta_encryption = "WEP64",sta_auth = 'EAP',
                   auth_server = ras_server_name,
                   username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                   ras_secret = "1234567890", use_radius = True))

    wlan_list.append(dict(auth = "dot1x-eap", encryption = "wep-128",
                   sta_encryption = "WEP128",sta_auth = 'EAP',
                   auth_server = ras_server_name,
                   username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                   ras_secret = "1234567890", use_radius = True))
    
    index = 0
    for wlan_cfg in wlan_list:
        index += 1
        wlan_cfg['ssid'] = _defineWlanName(wlan_cfg)
        wlan_cfg['name'] = wlan_cfg['ssid']
        wlan_config_list.append(wlan_cfg)
        
    return wlan_config_list
        
def _defineWlanName(wlan_cfg):
    wlan_name = '%s'
    info = ''
    if wlan_cfg.has_key('wpa_ver'):
        info = '%s_%s_%s' % (wlan_cfg['wpa_ver'], wlan_cfg['auth'], wlan_cfg['encryption'])
    else:
        info = '%s_%s' % (wlan_cfg['auth'].upper(), wlan_cfg['encryption'])
    return wlan_name % info
        
def build_stcs_wlan(wlan_cfg, ip_cfg, tc_name):
    tcs = [] 
    default_cfg = deepcopy(wlan_cfg)
    default_cfg['name'] = default_cfg['ssid']
    default_cfg['force_dhcp'] = True
    default_cfg['force_dhcp_timeout'] = 15
          
    tcs.append(({'wlan_conf':default_cfg, 
                 'check_wlan_timeout' : 30},
                'CB_ZD_CLI_Create_Wlan',
                '%sCreate WLAN from CLI' % tc_name,
                1,
                False))
    
    #The CLI parameters are different between association, so we need to convert it
    get_cfg = deepcopy(default_cfg)
    if get_cfg['auth'] == "dot1x-eap":
        get_cfg['auth'] = get_cfg['sta_auth']
        get_cfg['encryption'] = get_cfg['sta_encryption']
        if get_cfg.has_key('wpa_ver') and get_cfg['wpa_ver'] == 'WPA-Mixed':
            get_cfg['wpa_ver'] = 'WPA'
    
    #Station associate
    tcs.append(({'sta_tag': 'sta_1', 
             'wlan_cfg': get_cfg,
             'wlan_ssid': get_cfg['ssid']}, 
             'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2', 
              '%sAssociate the station' % tc_name, 
              2, 
              False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing station' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg' : '',
             'sta_tag' : 'sta_1'},
            'CB_Station_Config_Static_Wifi_Addr',
            '%sSet Station IP to static equal dhcp ip'% tc_name,
            2,
            False))
    
    tcs.append(({'sta_tag': 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Allowed', 
                  '%sPing Dest is Allowed after change IP to Static equal DHCP' % tc_name, 
                  2, 
                  False))

    tcs.append(({'ip_cfg' : ip_cfg['static_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_Static_Wifi_Addr',
                '%sSet Station IP to static not equal dhcp ip'% tc_name,
                2,
                False
                ))
    
    tcs.append(({'sta_tag' : 'sta_1'}, 
                 'CB_Station_Ping_Dest_Is_Denied', 
                  '%sPing Dest is Denied' % tc_name, 
                  2, 
                  False))
    
    tcs.append(({'ip_cfg':ip_cfg['dhcp_cfg'],
                 'sta_tag' : 'sta_1'},
                'CB_Station_Config_DHCP_Wifi_Addr',
                '%sSet Station IP to DHCP'% tc_name,
                2,
                True))
    return tcs

def create_test_suite(**kwargs):    
    attrs = dict(testsuite_name = "Force DHCP with different authentication and encryption types"
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
            
    ts_name = attrs['testsuite_name']
    sta_ip_addr = testsuite.getTargetStation(sta_ip_list, "Choose an wireless station: ")
    target_sta_radio = testsuite.get_target_sta_radio()
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg) 
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            active_ap_mac = ap_info['mac']           
            break
          
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    ts = testsuite.get_testsuite(ts_name, 
                                 "Force DHCP with different authentication and encryption types", 
                                 combotest=True)
                
    test_cfgs = build_tcs(sta_ip_addr, all_aps_mac_list, target_sta_radio, active_ap, active_ap_mac, ras_ip_addr)

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
    