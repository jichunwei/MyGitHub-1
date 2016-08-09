"""
Author: Louis Lou
Email: louis.lou@ruckuswireless.com
"""

import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const

    
def define_wlan_cfg(tcfg):
    
    _wlan_cfgs = dict()
        
    _wlan_cfgs['open-none'] = (dict(name = 'web-auth-open-none-' + utils.make_random_string(random.randint(2,12),type = 'alpha'),
                               type = 'standard-usage',
                               web_auth = True,auth_server = ''
                               ))
    
    _wlan_cfgs['open-none-local'] = (dict(name = 'web-auth-open-none-local-' + utils.make_random_string(random.randint(2,5),type = 'alpha'),
                               type = 'standard-usage',
                               web_auth = True, auth_server = 'local'
                               ))
    return _wlan_cfgs


def define_test_cfg(cfg,wlan_cfg_dict):
    test_cfgs = []
    ras_cfg = dict(server_addr = cfg['ras_ip_addr'],
                   server_port = cfg['ras_port'],
                   server_name = cfg['ras_name'],
                   radius_auth_secret = cfg['radius_auth_secret']
                   )
    
    local_user = dict(username = 'admin',password = 'admin')
    
    test_name = 'CB_ZD_Find_Station'
    common_name = 'Get the station'    
    test_cfgs.append(( {'target_station':cfg['target_station'],}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Find_Active_AP'
    common_name = 'Get the active AP' 
    test_cfgs.append(({'active_ap':cfg['active_ap'],}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from ZD'   
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create the authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create the Local User for Authentication'
    test_cfgs.append(({'username':local_user['username'], 'password':local_user['password']}, test_name, common_name, 0, False))
    
#    WLAN1: Web-Auth-Open-None
    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = '[ZDCLI:WebAuth]: 1. Create a WLAN on ZDCLI'
    wlan_cfg_dict['open-none'].update(auth_server=ras_cfg['server_name'])
    test_cfgs.append(( {'wlan_conf':wlan_cfg_dict['open-none']}, test_name, common_name, 1, False))

    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
    common_name = '[ZDCLI:WebAuth]: 2. Get ZD WLAN Info via CLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get'
    common_name = '[ZDCLI:WebAuth]: 3. Verify WLAN Info Between CLI Set and CLI get'
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Wlans_Info'
    common_name = '[ZDCLI:WebAuth]: 4. Get WLAN Info'
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_CLISet_GUIGet'
    common_name = '[ZDCLI:WebAuth]: 5. Verify WLAN Info Between CLI Get and GUI Get'
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Wlan_On_APs'
    common_name = '[ZDCLI:WebAuth]: 6. Verify the WLAN on the active AP' 
    test_cfgs.append(( {'ssid': wlan_cfg_dict['open-none']['name'] }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[ZDCLI:WebAuth]: 7. Associate the station'
    wlan_cfg_dict['open-none'].update(ssid = wlan_cfg_dict['open-none']['name'],auth = "open",encryption = "none") 
    test_cfgs.append(( {'wlan_cfg':wlan_cfg_dict['open-none']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '[ZDCLI:WebAuth]: 8. Get WiFi address of the station'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Denied'
    common_name = '[ZDCLI:WebAuth]: 9. Verify Client Should not Ping a target IP'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Verify_Client_Unauthorized'
    common_name = '[ZDCLI:WebAuth]: 10. Verify ZD Client is Unauthorized'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Perform_Web_Auth'
    common_name = '[ZDCLI:WebAuth]: 11. Configure Station Perform Authentication'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    common_name = '[ZDCLI:WebAuth]: 12. Verify ZD Client is Authorized'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Allowed'
    common_name = '[ZDCLI:WebAuth]: 13. The station ping a target IP'
    test_cfgs.append(({'target_ip':cfg['ras_ip_addr']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[ZDCLI:WebAuth]: 14. Verify the station information on ZD'
    test_cfgs.append(({'radio_mode':cfg['radio_mode'],'wlan_cfg': wlan_cfg_dict['open-none'],'username':'ras.local.user'}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[ZDCLI:WebAuth]: 15. Remove all WLAN from ZD'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[ZDCLI:WebAuth]: 16. Remove all WLAN from the station'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
#    WLAN1: Web-Auth-Open-None-local
    
    test_name = 'CB_ZD_CLI_Create_Wlan'
    common_name = '[ZDCLI:WebAuth-Local]: 1. Create a WLAN on ZDCLI'
    test_cfgs.append(( {'wlan_conf':wlan_cfg_dict['open-none-local']}, test_name, common_name, 1, False))

    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
    common_name = '[ZDCLI:WebAuth-Local]: 2. Get ZD WLAN Info via CLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get'
    common_name = '[ZDCLI:WebAuth-Local]: 3. Verify WLAN Info Between CLI Set and CLI get'
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Wlans_Info'
    common_name = '[ZDCLI:WebAuth-Local]: 4. Get WLAN Info'
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Verify_Wlan_Info_Between_CLISet_GUIGet'
    common_name = '[ZDCLI:WebAuth-Local]: 5. Verify WLAN Info Between CLI Get and GUI Get'
    test_cfgs.append(( {}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Wlan_On_APs'
    common_name = '[ZDCLI:WebAuth-Local]: 6. Verify the WLAN on the active AP' 
    test_cfgs.append(( {'ssid': wlan_cfg_dict['open-none-local']['name'] }, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[ZDCLI:WebAuth-Local]: 7. Associate the station'
    wlan_cfg_dict['open-none-local'].update(ssid = wlan_cfg_dict['open-none-local']['name'],auth = "open",encryption = "none") 
    test_cfgs.append(( {'wlan_cfg':wlan_cfg_dict['open-none-local']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Get_Station_Wifi_Addr'
    common_name = '[ZDCLI:WebAuth-Local]: 8. Get WiFi address of the station'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Denied'
    common_name = '[ZDCLI:WebAuth-Local]: 9. Verify Client Should not Ping a target IP'
    test_cfgs.append(({'condition':'disallowed'}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Verify_Client_Unauthorized'
    common_name = '[ZDCLI:WebAuth-Local]: 10. Verify ZD Client is Unauthorized'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Perform_Web_Auth'
    common_name = '[ZDCLI:WebAuth-Local]: 11. Configure Station Perform Authentication'
    test_cfgs.append(({'username':local_user['username'], 'password':local_user['password']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Station_Verify_Client_Authorized'
    common_name = '[ZDCLI:WebAuth-Local]: 12. Verify ZD Client is Authorized'
    test_cfgs.append(({'username':local_user['username']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest_Is_Allowed'
    common_name = '[ZDCLI:WebAuth-Local]: 13. The station ping a target IP'
    test_cfgs.append(({'target_ip':cfg['ras_ip_addr']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[ZDCLI:WebAuth-Local]: 14. Verify the station information on ZD'
    test_cfgs.append(({'radio_mode':cfg['radio_mode'],'wlan_cfg': wlan_cfg_dict['open-none-local'],'username':local_user['username']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[ZDCLI:WebAuth-Local]: 15. Remove all WLAN from ZD'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[ZDCLI:WebAuth-Local]: 16. Remove all WLAN from the station'
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    
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
        
        tcfg = {'ras_ip_addr':ras_ip_addr,
                'ras_port' : '1812',
                'ras_name' : 'rat-radius',
                'radius_auth_secret': '1234567890',
                'target_station':'%s' % target_sta,
                'active_ap':'%s' % active_ap,
                'radio_mode': target_sta_radio,
                'target_sta_radio': target_sta_radio,
                }
        wlan_cfg_dict = define_wlan_cfg(tcfg)
        
        test_cfgs = define_test_cfg(tcfg,wlan_cfg_dict)

        if attrs["testsuite_name"]:
            ts_name = attrs["testsuite_name"]
        else: 
            ts_name = "ZDCLI: Web Authentication -Open None - 11%s Client" % target_sta_radio
        
        ts = testsuite.get_testsuite(ts_name,
                                     "Verify the Web Authentication with Open-None Encryption type - 11%s radio" % target_sta_radio,
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
 
    