"""
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

import logging
import random
import time
import copy
import sys
from pprint import pformat

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def define_wlan_cfg_list(ras_ip_addr):
    logging.info('Generate a list of 32 wlan configuration')
    
    _wlan_cfgs = []
    _wlan_cfgs.append(dict(ssid = "", auth = "open", wpa_ver = "", encryption = "none",
                          key_index = "" , key_string = "",
                          username = "", password = "", auth_svr = ""))
    
    _wlan_cfgs.append(dict(ssid = "", auth = "open", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))
    
    _wlan_cfgs.append(dict(ssid = "", auth = "open", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = ""))
    
    _wlan_cfgs.append(dict(ssid = "", auth = "shared", wpa_ver = "", encryption = "WEP-64",
                          key_index = "" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "shared", wpa_ver = "", encryption = "WEP-128",
                          key_index = "" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))
    
    wlan_cfgs = []
    number = 1
    key_index = 1
    
    while True:
        for i in range(len(_wlan_cfgs)):
            if number > 32:
                for j in range(len(wlan_cfgs)):
                    logging.info('[%s]\n%s' % (wlan_cfgs[j]['ssid'], pformat(wlan_cfgs[j], 4, 120)))
                return wlan_cfgs
            
            conf = copy.deepcopy(_wlan_cfgs[i])
            conf['ssid'] = "zdcli-wlan-%s-%d" % (time.strftime("%H%M%S"), number)
            
            if _wlan_cfgs[i]['auth'] == 'shared':
                if key_index < 5:
                    conf['key_index'] = "%d" % key_index
                    wlan_cfgs.append(conf)
                    key_index += 1
                    number += 1                  
            else:
                wlan_cfgs.append(conf)
                number += 1


def define_test_cfg(cfg):
    test_cfgs = []
   
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = '1.remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Get_All_Wlan'
    common_name = '2.get all wlan information from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Verify_All_Wlan'
    common_name = '3.verify all wlan information shown in ZD CLI'   
    test_cfgs.append(({'gui_wlan_cfg_list': None}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = '4.create the authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[cfg['ras_cfg']]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '5.create 32 wlans via ZD GUI'
    test_cfgs.append(( {'wlan_cfg_list':cfg['wlan_cfg_list']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Get_All_Wlan'
    common_name = '6.get all wlan information from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Verify_All_Wlan'
    common_name = '7.verify all wlan information shown in ZD CLI'   
    test_cfgs.append(({'wlan_cfg_list': cfg['wlan_cfg_list']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
    common_name = '8.get the wlan information by ssid from ZD CLI'   
    test_cfgs.append(({'ssid': cfg['wlan_cfg_list'][31]['ssid']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Verify_Wlan'
    common_name = '9.verify the wlan information shown in ZD CLI'   
    test_cfgs.append(({'wlan_cfg': cfg['wlan_cfg_list'][31]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '10.Open_None: remove all wlans from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Get_All_Wlan'
    common_name = '11.get all wlan information from ZD CLI'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Verify_All_Wlan'
    common_name = '12.verify all wlan information shown in ZD CLI'   
    test_cfgs.append(({'wlan_cfg_list': None}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
    common_name = '13.get the wlan information by ssid from ZD CLI'   
    test_cfgs.append(({'ssid': cfg['wlan_cfg_list'][31]['ssid']}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZDCLI_Verify_Wlan'
    common_name = '14.verify the wlan information shown in ZD CLI'   
    test_cfgs.append(({'wlan_cfg': None}, test_name, common_name, 1, False))
       
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = '15.remove all configuration from ZD to clean up'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def createTestSuite(**kwargs):
    attrs = {'testsuite_name': ''}
    attrs.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)
  
    wlan_cfg_list = define_wlan_cfg_list(ras_ip_addr)

    ras_cfg = dict(server_addr = ras_ip_addr,
                   server_port = '1812',
                   server_name = '',
                   radius_auth_secret = '1234567890'
                   )
    
    tcfg = {'ras_cfg': ras_cfg,
            'wlan_cfg_list': wlan_cfg_list,
            }
    
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "ZD CLI Get Wlan - Combo" 
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify whether the wlan information shown is ZD CLI is correct" ,
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
    