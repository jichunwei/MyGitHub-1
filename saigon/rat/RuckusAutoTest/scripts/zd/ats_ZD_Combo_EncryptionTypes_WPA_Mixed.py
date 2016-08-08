"""
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn 
"""

import sys
import random
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def define_Wlan_cfg(ssid, ras_ip_addr):
    wlan_cfgs = []    
    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))
    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA_Mixed", encryption = "Auto",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "", auth_svr = "",
                           ras_secret = "", use_radius = False))
    
    return wlan_cfgs


def define_test_cfg(cfg):
    test_cfgs = []
    ras_cfg = dict(server_addr = cfg['ras_ip_addr'],
                   server_port = cfg['ras_port'],
                   server_name = cfg['ras_name'],
                   radius_auth_secret = cfg['radius_auth_secret']
                   )
    
    test_name = 'CB_ZD_Find_Station'
    common_name = 'get the station'    
    test_cfgs.append(( {'target_station':cfg['target_station'],}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Find_Active_AP'
    common_name = 'get the active AP' 
    test_cfgs.append(({'active_ap':cfg['active_ap'],}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'create the authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    for wlan_cfg in cfg['wlan_cfg_list']:
        test_name = 'CB_ZD_Create_Wlan'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: create a wlan on ZD' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(( {'wlan_cfg_list':[wlan_cfg]}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Verify_Wlan_On_APs'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: verify the wlan on the active AP' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])   
        test_cfgs.append(( {'ssid':cfg['ssid']}, test_name, common_name, 0, False))    
        
        test_name = 'CB_ZD_Associate_Station'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: associate the station' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])   
        test_cfgs.append(( {'wlan_cfg':wlan_cfg}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Get_Station_Wifi_Addr'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: get wifi address of the station' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(({}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Client_Ping_Dest_Is_Allowed'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: the station ping a target ip' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(({'target_ip':cfg['ras_ip_addr']}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Verify_Station_Info'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: verify the station information on ZD' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(({'radio_mode':cfg['radio_mode'],'wlan_cfg':wlan_cfg}, test_name, common_name, 1, False))
        
        test_name = 'CB_ZD_Verify_Station_Info_On_AP'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: verify the station information on the active AP' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(({'ssid':cfg['ssid']}, test_name, common_name, 1, False))
    
        test_name = 'CB_ZD_Remove_All_Wlans'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: remove all wlans from ZD' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(({}, test_name, common_name, 0, False))
        
        test_name = 'CB_ZD_Remove_Wlan_From_Station'
        common_name = 'WPA-Mixed %s %s - Station %s-%s: remove all wlans from the station' % (wlan_cfg['auth'], wlan_cfg['encryption'], 
                                                                                wlan_cfg['sta_auth'], wlan_cfg['sta_encryption'])
        test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'remove all configuration from ZD to clean up'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = 'remove all wlans from the station to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
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
    ap_sym_dict = tbcfg['ap_sym_dict']
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)

    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta = sta_ip_list[attrs["station"][0]]
        target_sta_radio = attrs["station"][1]

    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            active_ap = ap_sym_name
            break

    if active_ap :
        ssid = "rat-encryptions-11%s-%s" % (target_sta_radio, time.strftime("%H%M%S"))
        wlan_cfg_list = define_Wlan_cfg(ssid, ras_ip_addr)
        tcfg = {'ras_ip_addr':ras_ip_addr,
                'ras_port' : '1812',
                'ras_name' : '',
                'radius_auth_secret': '1234567890',
                'target_station':'%s' % target_sta,
                'active_ap':'%s' % active_ap,
                'radio_mode': target_sta_radio,
                'target_sta_radio': target_sta_radio,
                'wlan_cfg_list': wlan_cfg_list,
                'ssid': ssid,
                }
        test_cfgs = define_test_cfg(tcfg)

        if attrs["testsuite_name"]:
            ts_name = attrs["testsuite_name"]
        else: 
            ts_name = "Encryption Types WPA Mixed - 11%s - Combo" % target_sta_radio
        
        ts = testsuite.get_testsuite(ts_name,
                                     "Verify the ability of ZD to deploy WLANs with WPA Mixed encryption types properly - 11%s radio" % target_sta_radio,
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
    