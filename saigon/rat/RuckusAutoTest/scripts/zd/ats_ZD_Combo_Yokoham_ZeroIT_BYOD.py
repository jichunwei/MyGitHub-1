"""
Verify wlan with open shared encryption types and zero-it works well for dualstack and ipv6

    Verify wlan with open shared works well when ZD is dual stack and ipv6 only.
    Encryption type coverage:
        Open-none
        Open-WEP-64
        PSK-WPA-TKIP
    expect result: All steps should result properly.
    
    How to:
        1) Get ZD and AP IP version from testbed config
        2) Disable all AP's wlan service
        3) Enable active AP's wlan service based on radio   
        4) Create a wlan and make sure it is in default wlan group
        5) Station associate the guest wlan and enable onboarding portal option.
        6) Download zero-it to station
        7) Station associate to the wlan via zero-it
        8) Get station wifi ipv4 and ivp6 address and verify they are in expected subnet
        9) Verify station can ping target ipv4 and ipv6
        10) Verify station can download a file from server
        11) Verify station information in ZD, status is authorized
        12) Verify station information in AP side
    
Created on 2012-02-12
@author: cwang@ruckuswireless.com
"""

import sys
import random
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils

guest_wlan_cfg = {
        'ssid': "rat-wlan-guestaccess-%s" % (time.strftime("%H%M%S")),
        'auth': "open",
        'encryption': "none",
        'type': 'guest',
        'do_tunnel': False,
    }

def _get_wlan_cfg(ssid, wlan_params):
    wlanCfg = dict(ssid=ssid, auth="open", wpa_ver="", encryption="none", key_index="", key_string="",  
                   username="", password="",)    
    wlanCfg.update(wlan_params)    
    return wlanCfg

def _define_wlan_cfg(ssid, username, password):
    wlan_cfgs = []

    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="open", encryption="none",username = username, password = password)))
    
    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="PSK", wpa_ver="WPA", encryption="AES",username = username, password = password,
                                             key_string=utils.make_random_string(random.randint(8, 63), "hex"))))

    for wlan_cfg in wlan_cfgs:
        wlan_cfg['do_zero_it'] = True
   
    return wlan_cfgs

def define_test_cfg(cfg):
    test_cfgs = []

    ras_cfg = cfg['ras_cfg']
    target_ip_addr = ras_cfg['server_addr']
    radio_mode = cfg['radio_mode']
    
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode
        
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create Radius authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = 'Select authentication server'
    test_cfgs.append(({'zero_it_auth_serv':ras_cfg['server_name']}, test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    wlans_cfg_list = cfg['wlan_cfg_list']
    for wlan_cfg in wlans_cfg_list:
        if wlan_cfg.has_key('wpa_ver') and wlan_cfg['wpa_ver']:
            is_wpa_auto = False
            wpa_ver = wlan_cfg['wpa_ver']
            if wpa_ver.lower().find('auto') > -1 or wpa_ver.lower().find('mixed') > -1:
                is_wpa_auto = True                
                wpa_ver_list = ['WPA', 'WPA2']
            else:
                wpa_ver_list = [wpa_ver]
            #If encryption is auto for wpa, verify TKIP and AES.
            if wlan_cfg['encryption'].lower() == 'auto':
                is_wpa_auto = True
                encrypt_list = ['TKIP', 'AES']                    
            else:
                encrypt_list = [wlan_cfg['encryption']]
            #Associate to wlans with different wpa version and encryption.
            for wpa_version in wpa_ver_list:
                wlan_cfg['sta_wpa_ver'] = wpa_version
                for encrypt in encrypt_list:
                    wlan_cfg['sta_encryption'] = encrypt
                    test_cfgs.extend(_define_test_case_cfg(cfg, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_wpa_auto))
        else:
            test_cfgs.extend(_define_test_case_cfg(cfg, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag))
       
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = 'Select authentication server to original value'
    test_cfgs.append(({'zero_it_auth_serv': 'Local Database'}, test_name, common_name, 0, False))    
        
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD GUI after test'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    return test_cfgs


def _define_test_case_cfg(cfg, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_wpa_auto=False):
    test_cfgs = []
    
    new_wlan_cfg = deepcopy(wlan_cfg)
    
    radio_mode = cfg['radio_mode']    
    auth = new_wlan_cfg['auth']
    encryption = new_wlan_cfg['encryption']
    wpa_ver = new_wlan_cfg['wpa_ver']
    key_index = new_wlan_cfg['key_index']
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    wlan_encrypt = '%s_%s' % (auth, encryption)
    if wpa_ver:
        wlan_encrypt = wlan_encrypt + '_%s' % (wpa_ver,)
    if key_index:
        wlan_encrypt = wlan_encrypt + '_%s' % (key_index,)
    
    ssid = "%s-%05d" % (wlan_encrypt, random.randrange(1, 99999))  
    new_wlan_cfg['ssid'] = ssid    
    
    new_wlan_cfg['use_radius'] = False
        
    if wpa_ver and is_wpa_auto:
        wlan_encrypt = wlan_encrypt + '_STA_%s_%s' % (new_wlan_cfg['sta_wpa_ver'], new_wlan_cfg['sta_encryption'])
        
    test_case_name = '[%s]' % (wlan_encrypt,)

    test_name = 'CB_ZD_Set_GuestAccess_Policy'
    common_name = '%sSet the guest-access policy' % test_case_name
    test_params = dict(use_guestpass_auth=True,
                       use_tou=True,
                       onboarding_portal = True,
                       redirect_url='')
    test_cfgs.append((test_params, test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg, guest_wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 1, False))
      
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the target station' % test_case_name
    test_params = {'sta_tag': sta_tag, 'wlan_cfg': guest_wlan_cfg}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet target station Wifi addresses' % test_case_name
    test_params = {'sta_tag': sta_tag}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
   
    test_name = 'CB_ZD_Station_Config_ZeroIT_Wlan_With_DeviceRegister'
    common_name = '%sConfigure zero it in station' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       #'ip_type': 'ipv4',
                       'wlan_cfg': new_wlan_cfg}, test_name, common_name, 2, False))    
           
    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan %s from station' % (test_case_name, 
                                                         new_wlan_cfg['ssid'])
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all WLANs from ZD' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 0, False))

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

def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    ts_cfg.update(kwargs)

    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    username = 'ras.local.user'
    password = 'ras.local.user'
    expected_sub_mask = '255.255.255.0'

    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
        
    ras_ip_addr = testsuite.getTestbedServerIp(tbcfg)
    
    if ts_cfg["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
        target_sta_radio = testsuite.get_target_sta_radio()
    else:        
        target_sta = sta_ip_list[ts_cfg["station"][0]]
        target_sta_radio = ts_cfg["station"][1]
        
    active_ap = None
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = const._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name
            break
                
    ssid = ""
    ras_name = 'ruckus-radius-%s' % (time.strftime("%H%M%S"),)
    
    wlan_cfg_list = _define_wlan_cfg(ssid, username, password)
    
    tcfg = {'ras_cfg': {'server_addr': ras_ip_addr,
                        'server_port' : '1812',
                        'server_name' : ras_name,
                        'radius_auth_secret': '1234567890',
                        'radius_auth_method': 'chap',
                        },
            'target_station':'%s' % target_sta,
            'active_ap':'%s' % active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            'radio_mode': target_sta_radio,
            'wlan_cfg_list': wlan_cfg_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': utils.get_network_address(ras_ip_addr, 
                                                         expected_sub_mask),
            'username': username,
            'password': password,
            }
            
    test_cfgs = define_test_cfg(tcfg)
    
    check_max_length(test_cfgs)
    check_validation(test_cfgs)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Zero IT - 11%s - ZeroIT BYOD" % (target_sta_radio,)

    ts = testsuite.get_testsuite(ts_name, "Verify ZeroIT BYOD - 11%s radio" % target_sta_radio, combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1

            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')    

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)