"""
Author: Louis Lou
Email: louis.lou@ruckuswireless.com
"""

import sys
import random
import copy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

    
def define_wlan_cfg(tcfg):
    _wlan_cfgs = dict()
    
    #_wlan_cfgs['open-wpa-mixed-tkip'] = (dict(name = 'open-wpa-mixed-tkip',
    #                       auth = "open", encryption = "wpa-mixed", algorithm =  'TKIP', 
    #                       passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
    #                       ))
    
    _wlan_cfgs['open-wpa-mixed-aes'] = (dict(name = 'open-wpa-mixed-aes',
                           auth = "open", encryption = "wpa-mixed", algorithm = 'AES', 
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           ))
    _wlan_cfgs['open-wpa-mixed-auto'] = (dict(name = 'open-wpa-mixed-auto',
                           auth = "open", encryption = "wpa-mixed", algorithm = 'auto',
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           ))

    return _wlan_cfgs


def define_test_cfg(cfg,wlan_cfg_dict):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    ap_tag = 'ap%s' % radio_mode
    sta_tag = 'sta%s' % radio_mode
    browser_tag = 'browser%s' % radio_mode
    
    target_ip_addr = cfg['target_station']
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
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
    
    for key, wlancfg in wlan_cfg_dict.items():
        wpa_ver_list = ['WPA', 'WPA2']
        if wlancfg.has_key('algorithm') and wlancfg['algorithm'].lower() == 'auto':
            encypt_list = ['AES', 'TKIP']
        else:
            encypt_list= [wlancfg.get('algorithm')]
            
        for wpa_ver in wpa_ver_list:
            for encypt in encypt_list:
                wlan_cfg = copy.deepcopy(wlancfg)
                
                wlan_cfg['sta_wpa_ver'] = wpa_ver
                wlan_cfg['sta_encryption'] = encypt
                wlan_cfg['name'] = '%s-%s' % (wlan_cfg['name'], utils.make_random_string(4,type = 'alnum'))
                
                sta_info = 'STA-%s-%s' % (wpa_ver, encypt)
                test_case_name = "[%s-%s]" % (key, sta_info)                    
                
                test_name = 'CB_ZD_CLI_Create_Wlan'
                common_name = '%sCreate a WLAN on ZD CLI' % (test_case_name,)
                test_cfgs.append(( {'wlan_conf':wlan_cfg,
                                    'check_wlan_timeout':80}, test_name, common_name, 1, False))
                
                test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
                common_name = '%sGet ZD Wlans Info via CLI' % (test_case_name,)
                test_cfgs.append(({}, test_name, common_name, 2, False))
                
                test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get'
                common_name = '%sVerify Wlans Info Between CLI Set and CLI Get' % (test_case_name,)
                test_cfgs.append(( {}, test_name, common_name, 2, False))
                
                test_name = 'CB_ZD_Get_Wlans_Info'
                common_name = '%sGet Wlans Info via GUI' % (test_case_name,)
                test_cfgs.append(( {}, test_name, common_name, 2, False))
                
                test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_CLISet_GUIGet'
                common_name = '%sVerify Wlans Info Between CLI Get and GUI Get' % (test_case_name,)
                test_cfgs.append(( {}, test_name, common_name, 2, False))
                
                #Verify wlan in the AP and associate station to wlan.
                test_cfgs.extend(_define_data_plane_test_cfg(cfg, test_case_name, target_ip_addr, 
                                                             wlan_cfg, sta_tag, browser_tag, ap_tag))
        
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_Station_CaptivePortal_Quit_Browser'
    common_name = 'Quit browser in Station'
    test_cfgs.append(({'sta_tag': sta_tag,
                       'browser_tag':browser_tag}, test_name, common_name, 0, True))
        
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

#def _convert_wlan_cfg(wlan_cfg, username, password):
def _convert_wlan_cfg(wlan_cfg,username = '', password = ''):
    sta_wlan_cfg = {}
    
    sta_wlan_cfg['ssid'] = wlan_cfg['name']
    
    if not wlan_cfg.has_key('auth'):
        sta_wlan_cfg['auth'] = 'open'
    else:
        if wlan_cfg['auth'].lower().find('eap') > -1:
            sta_wlan_cfg['auth'] = 'EAP'
        elif wlan_cfg['auth'].lower() == 'open' and wlan_cfg.has_key('encryption') \
                and wlan_cfg['encryption'].lower().find('wpa') > -1:
            sta_wlan_cfg['auth'] = 'PSK'
        else:
            sta_wlan_cfg['auth'] = wlan_cfg['auth']
            
    if  wlan_cfg.has_key('encryption'):
        if wlan_cfg['encryption'].lower().startswith('wep'):
            sta_wlan_cfg['encryption'] = wlan_cfg['encryption'].upper()
        elif wlan_cfg['encryption'].lower().find('wpa') > -1:
            sta_wlan_cfg['wpa_ver'] = wlan_cfg['encryption'].upper()          
            sta_wlan_cfg['encryption'] = wlan_cfg['algorithm'].upper()
            
            if sta_wlan_cfg['wpa_ver'].lower() == 'wpa-mixed' \
                 or sta_wlan_cfg['wpa_ver'].lower() == 'wpa_mixed' \
                 or sta_wlan_cfg['wpa_ver'].lower() == 'wpa-auto':
                sta_wlan_cfg['wpa_ver'] = 'WPA_Mixed'
        else:
            sta_wlan_cfg['encryption'] = wlan_cfg['encryption']
    else:
        sta_wlan_cfg['encryption'] = 'none'
            
    if wlan_cfg.has_key('key_string'):
        sta_wlan_cfg['key_string'] = wlan_cfg['key_string']
    if wlan_cfg.has_key('passphrase'):
        sta_wlan_cfg['key_string'] = wlan_cfg['passphrase']
    
    if wlan_cfg.has_key('key_index'):
        sta_wlan_cfg['key_index'] = wlan_cfg['key_index']
    else:
        if sta_wlan_cfg.has_key('encryption') and sta_wlan_cfg['encryption'].lower().startswith('wep'):
            sta_wlan_cfg['key_index'] = '1' 
        
    if wlan_cfg.has_key('sta_wpa_ver'):
        sta_wlan_cfg['sta_wpa_ver'] = wlan_cfg['sta_wpa_ver']
        
    if wlan_cfg.has_key('sta_encryption'):
        sta_wlan_cfg['sta_encryption'] = wlan_cfg['sta_encryption']
        
    if username:
        sta_wlan_cfg['username'] = username 
    if password:
        sta_wlan_cfg['password'] = password
    
    return sta_wlan_cfg  

def _define_data_plane_test_cfg(cfg, test_case_name, target_ip_addr, wlan_cfg, sta_tag, browser_tag, ap_tag, is_wpa_auto=False):
    test_cfgs = []
    
    radio_mode = cfg['radio_mode']
    expected_sub_mask = cfg['expected_sub_mask']
    expected_subnet = cfg['expected_subnet']
    #username = cfg['username']
    #password = cfg['password']
    
    sta_wlan_cfg = _convert_wlan_cfg(wlan_cfg)
    
    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    expect_ap_wlan_cfg = _define_expect_wlan_info_in_ap(cfg, sta_wlan_cfg)
    test_name = 'CB_ZD_Verify_Wlan_Info_In_AP'
    common_name = '%sVerify the wlan on the active AP' % (test_case_name)
    test_cfgs.append(({'expect_wlan_info': expect_ap_wlan_cfg,
                       'ap_tag': ap_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate the station to the wlan' % (test_case_name,)
    test_cfgs.append(({'wlan_cfg': sta_wlan_cfg,
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
    common_name = '%sVerify client information in ZD' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'ap_tag': ap_tag,
                       'status': 'authorized',
                       'wlan_cfg': sta_wlan_cfg,
                       'radio_mode':sta_radio_mode,
                       #'username': username
                       },
                       test_name, common_name, 2, False))

    test_name = 'CB_ZD_Client_Ping_Dest'
    common_name = '%sVerify client can ping a target IP' % (test_case_name,)
    test_cfgs.append(({'sta_tag': sta_tag,
                       'condition': 'allowed',
                       'target': target_ip_addr}, test_name, common_name, 2, False))
    
    #Remove this step for tb72 bad test environment
    #test_name = 'CB_Station_CaptivePortal_Download_File'
    #common_name = '%sVerify download file from server' % (test_case_name,)
    #test_cfgs.append(({'sta_tag': sta_tag,
    #                   'browser_tag': browser_tag,
    #                   #'validation_url': "http://%s/authenticated/" % target_ip_addr,
    #                   }, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_On_AP_V2'
    common_name = '%sVerify the station information in AP' % (test_case_name,)
    test_cfgs.append(({'ssid': sta_wlan_cfg['ssid'],
                       'ap_tag': ap_tag,
                       'sta_tag': sta_tag}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove the wlan %s from station' % (test_case_name, sta_wlan_cfg['ssid'])
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove the wlan %s from ZD' % (test_case_name, sta_wlan_cfg['ssid'])
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
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
    all_ap_mac_list = tbcfg['ap_mac_list']
    expected_sub_mask = '255.255.255.0'
    username = 'ras.eap.user'
    password = 'ras.eap.user'
    server_ip_addr = testsuite.getTestbedServerIp(tbcfg)    

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

    if active_ap:
        tcfg = {'target_station':'%s' % target_sta,
                'active_ap':'%s' % active_ap,
                'radio_mode': target_sta_radio,
                'target_sta_radio': target_sta_radio,
                'all_ap_mac_list': all_ap_mac_list,
                'expected_sub_mask': expected_sub_mask,
                'expected_subnet': utils.get_network_address(server_ip_addr, expected_sub_mask),
                'username': username,
                'password': password,
                }
        
        ap_model = ap_sym_dict[active_ap]['model']
        
        wlan_cfg_dict = define_wlan_cfg(tcfg)
        test_cfgs = define_test_cfg(tcfg,wlan_cfg_dict)

        if attrs["testsuite_name"]:
            ts_name = attrs["testsuite_name"]
        else: 
            ts_name = "ZDCLI- Encryption Types-Open-WPA-Mixed - 11%s" %target_sta_radio
            #ts_name = "ZDCLI- Encryption Types-Open-WPA-Mixed - 11%s %s" % (target_sta_radio, ap_model)
        
        ts = testsuite.get_testsuite(ts_name,
                                     "Verify the ability of ZD to deploy WLANs with different encryption types(open-wpa-mixed) properly - 11%s radio" % target_sta_radio,
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
 
    