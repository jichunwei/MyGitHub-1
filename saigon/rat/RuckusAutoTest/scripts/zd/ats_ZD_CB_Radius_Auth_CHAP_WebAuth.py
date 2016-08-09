"""   
Created on 2012-02-11
@author: 
"""

import sys
import time
import random
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common import Ratutils as utils


def _get_wlan_cfg(ssid, wlan_params):
    wlanCfg = dict(ssid=ssid, auth="open", wpa_ver="", encryption="none", key_index="", key_string="",
                   do_webauth=True, #auth_svr = "", #Default is local database. 
                   #username and password is for client to associate.
                   username="", password="",)
    wlanCfg.update(wlan_params)
    return wlanCfg

def _define_wlan_cfg(ssid, ras_name):
    wlan_cfgs = []

    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="open", encryption="none",auth_svr = ras_name)))
    
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="open", encryption="WEP-64",
#                                             key_index="1" , key_string=utils.make_random_string(10, "hex"))))
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="open", encryption="WEP-128",auth_svr = ras_name,
#                                             key_index="1" , key_string=utils.make_random_string(26, "hex"))))
#    
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="shared", encryption="WEP-64",
#                                             key_index="1" , key_string=utils.make_random_string(10, "hex"))))
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="shared", encryption="WEP-128",auth_svr = ras_name,
#                                             key_index="3" , key_string=utils.make_random_string(26, "hex"))))
#    
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="PSK", wpa_ver="WPA", encryption="TKIP",
#                                             key_string=utils.make_random_string(random.randint(8, 63), "hex"))))
#     wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="PSK", wpa_ver="WPA", encryption="AES",auth_svr = ras_name,
#                                             key_string=utils.make_random_string(random.randint(8, 63), "hex"))))
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="PSK", wpa_ver="WPA2", encryption="TKIP",
#                                             key_string=utils.make_random_string(random.randint(8, 63), "hex"))))
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="PSK", wpa_ver="WPA2", encryption="AES",auth_svr = ras_name,
#                                             key_string=utils.make_random_string(random.randint(8, 63), "hex"))))
#    wlan_cfgs.append(_get_wlan_cfg(ssid, dict(auth="PSK", wpa_ver="WPA_Mixed", encryption="Auto",
#                                             key_string=utils.make_random_string(random.randint(8, 63), "hex"))))
   
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

    test_name = 'CB_ZD_Verify_Radius_Server_Auth_Method'
    common_name = 'Test Radius Authentication Server'
    param_cfg = {'server_name': ras_cfg['server_name'], 
                 'user': cfg['username'], 'password':cfg['password'], 
                 'invalid_user': 'rad.cisco', 'invalid_password':'rad.cisco',
                 'radius_auth_method': ras_cfg['radius_auth_method'],}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))                  
  
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from station'
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = 'Start browser in station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, False))
    
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
    wg_cfg = dict(name=wg_name, description=None, ap_rp={radio_mode: {'wlangroups': wg_name}},)
    test_name = 'CB_ZD_Config_Wlan_Group_On_AP'
    common_name = 'Assign %s to wlan group %s' % (cfg['active_ap'], wg_name)
    test_cfgs.append(({'wgs_cfg': wg_cfg,
                       'ap_tag': ap_tag, },
                  test_name, common_name, 0, False))
    
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
                
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLAN from ZD at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all Authentication Server at last'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
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

def _define_test_case_cfg(cfg, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_wpa_auto=False):
    test_cfgs = []
    
    new_wlan_cfg = deepcopy(wlan_cfg)
    
    radio_mode = cfg['radio_mode']
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    username = cfg['username']
    password = cfg['password']
    
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
        
    if wpa_ver and is_wpa_auto:
        wlan_encrypt = wlan_encrypt + '_STA_%s_%s' % (new_wlan_cfg['sta_wpa_ver'], new_wlan_cfg['sta_encryption'])
        
    test_case_name = '[%s]' % (wlan_encrypt,)

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate a wlan on ZD' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg_list':[new_wlan_cfg],
                       'enable_wlan_on_default_wlan_group': True}, test_name, common_name, 1, False))
    
    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, new_wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg': new_wlan_cfg,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet wifi address of the station' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = '%sVerify station wifi ip address in expected subnet' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'expected_subnet': '%s/%s' % (expected_subnet, expected_sub_mask)},
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client is unauthorized in ZD' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'unauthorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': username},
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client should not ping a target IP' % (test_case_name)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'disallowed',
                       'target': target_ip_addr},
                      test_name, common_name, 2, False))
    
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    common_name = '%sConfigure station to perform web authentication' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag': browser_tag,
                       'username': username,
                       'password': password,
                       #'target_url': 'http://%s/' % target_ip_addr
                       },test_name, common_name, 2, False))

    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify client information in ZD' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': new_wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       'username': username},
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
    
#    test_name = 'CB_Station_CaptivePortal_Download_File'
#    common_name = '%sVerify download file from server' % (test_case_name,)
#    test_cfgs.append(({'sta_tag': sta_tag,
#                       'browser_tag': browser_tag,
#                       #'validation_url': "http://%s/authenticated/" % target_ip_addr,
#                       }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name,)
    test_cfgs.append(({'ssid': new_wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove the wlan %s from station' % (new_wlan_cfg['ssid'])
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
#    test_name = 'CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group'
#    common_name = 'Remove wlan %s from default wlan group' % (new_wlan_cfg['ssid'])        
#    test_cfgs.append(({'wlan_name_list': [new_wlan_cfg['ssid']]}, test_name, common_name, 1, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove WLAN %s from ZD' % (new_wlan_cfg['ssid'])
    test_cfgs.append(({}, test_name, common_name, 2, True))
        
    return test_cfgs

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
    
    wlan_cfg_list = _define_wlan_cfg(ssid, ras_name)
    
    
    tcfg = {'ras_cfg': {'server_addr': ras_ip_addr,
                        'server_port' : '1812',
                        'server_name' : ras_name,
                        'radius_auth_secret': '1234567890',
                        'radius_auth_method': 'chap',
                        },
            'target_station':'%s' % target_sta,
            'active_ap':'%s' % active_ap,
            'radio_mode': target_sta_radio,
            'wlan_cfg_list': wlan_cfg_list,
            'expected_sub_mask': expected_sub_mask,
            'expected_subnet': utils.get_network_address(ras_ip_addr, expected_sub_mask),
            'username': username,
            'password': password,
            }
    
    #ap_model = ap_sym_dict[active_ap]['model']
    
    test_cfgs = define_test_cfg(tcfg)
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Web Auth - 11%s - Radius Auth CHAP" % (target_sta_radio,)

    ts = testsuite.get_testsuite(ts_name, "Verify deploy WLANs with different encryption types properly - 11%s radio" % target_sta_radio, combotest=True)

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
