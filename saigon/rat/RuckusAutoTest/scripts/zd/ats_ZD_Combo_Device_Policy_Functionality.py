# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
@Author: An Nguyen - an.nguyen@ruckuswireless.com
@Since: Jun 2013

This testsuite is configure to allow testing follow test cases - which are belong to Device Policy Functionality test cases:


Note:
Please update the upgrade configuration for test case upgrade to new build  
"""
import sys

from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

dvcpcy_for_windows_os = {'name': 'Policy for Window OS', 'mode': 'deny', 
                         'rules': [{'name': '1', 'os_type': 'Windows', 'type': 'allow', 'vlan': '10', 
                                    'uplink': '10', 'downlink': '9'}]}
mod_dvcpcy_for_windows_os = {'name': 'Policy for Window OS', 'mode': 'deny', 
                             'rules': [{'name': '1', 'os_type': 'Windows', 'type': 'allow', 'vlan': '10', 
                                        'uplink': '6', 'downlink': '5'}]}
new_dvcpcy_for_windows_os = {'name': 'New policy for Window OS', 'mode': 'deny', 
                             'rules': [{'name': '1', 'os_type': 'Windows', 'type': 'allow', 'vlan': '10', 
                                        'uplink': '16', 'downlink': '15'}]}
#dvcpcy_for_windows_phone = {'name': 'Policy for Window Phone', 'mode': 'deny', 
#                            'rules': [{'name': '1', 'os_type': 'Windows Mobile', 'type': 'allow', 'vlan': '10', 
#                                       'uplink': '10', 'downlink': '10'}]}
#@author:yuyanan @since:2014-7-29 bug:zf-8417  os_type choice linux, because of os_type:windows usually behavior change
dvcpcy_for_Linux = {'name': 'Policy for Linux', 'mode': 'deny', 
                            'rules': [{'name': '1', 'os_type': 'Linux', 'type': 'allow', 'vlan': '10', 
                                       'uplink': '10', 'downlink': '10'}]}
prece_policy = {'name': 'test precedence', 
                'rules': [{'name': '1', 'order': '"AAA" "Device Policy" "WLAN"'},
                          {'name': '2', 'order': '"Device Policy" "AAA" "WLAN"'}]}
    
aaa_server = {'server_name': 'FreeRADIUS',
              'server_addr': '192.168.0.252',
              'type': 'radius-auth',
              'radius_secret': '1234567890',
              'server_port': '1812',
              'backup': False}

wlan_cfg = {'name': 'DVCPCY-WLAN-TESTING',
            'ssid': 'DVCPCY-WLAN-TESTING',
            'auth': 'dot1x-eap',
            'encryption': 'AES',#@author: yuyanan 2014-7-30 TKIP change to AES,VER:99.1088 do not support TKIP
            'algorithm': 'AES',#@author: yuyanan 2014-7-30 TKIP change to AES
            'wpa_ver': 'WPA2',
            'sta_wpa_ver': 'WPA2',
            'sta_encryption': 'AES',#@author: yuyanan 2014-7-30 TKIP change to AES
            'sta_auth': 'EAP',
            'auth_server': aaa_server['server_name'],
            'username': 'dvcpcy.user.20',
            'password': 'dvcpcy.user.20',
            'key_string': '',
            'use_radius': True,
            'dvlan': True,
            }

aaa_rate_limit =  {'uplink': '20mbps', 'downlink': '19mbps', 'margin_of_error': 0.2}
wlan_rate_limit =  {'uplink': '0.25mbps', 'downlink': '0.5mbps', 'margin_of_error': 0.2}
dvcpcy_rate_limit =  {'uplink': '10.00mbps', 'downlink': '9.00mbps', 'margin_of_error': 0.2}
mod_dvcpcy_rate_limit =  {'uplink': '6.00mbps', 'downlink': '5.00mbps', 'margin_of_error': 0.2}
new_dvcpcy_rate_limit =  {'uplink': '16.00mbps', 'downlink': '15.00mbps', 'margin_of_error': 0.2}

aaa_subnet = '192.168.20.0/255.255.255.0'
wlan_subnet =  '20.0.2.0/255.255.255.0'
dvcpcy_subnet =  '192.168.10.0/255.255.255.0'

def define_test_cfg(cfg):
    test_cfgs = []
    
    tcnames = ['Device policy WLAN for Windows client',
               'Device policy WLAN - Quickly de-associate the re-associate',
               'Device policy WLAN - Disable/Enable during client associate',
               'Device policy WLAN - Modify the policy during client associate',
               'Device policy WLAN - Switching policy during client associate',
               'Device policy WLAN - Reboot AP',
               'Device policy WLAN - Reboot ZD']
    ap_tag = 'AP1'
    sta_tag = 'STA1'
    expected_info = {'ap_tag': ap_tag,
                     'sta_tag': sta_tag}
    radio_mode = cfg['radio_mode']
    #@ZJ 20150331 ZF-10705
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init'}
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
    ###

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create AAA server'
    test_cfgs.append(({'server_cfg_list': [aaa_server]}, test_name, common_name, 0, False))
    
    tcname = tcnames[0]
    test_name = 'CB_ZD_CLI_Configure_Device_Policy'
    common_name = '[%s] Create device policy for Windows OS and Linux client' % tcname
    test_cfgs.append(({'device_policy_list': [dvcpcy_for_Linux, dvcpcy_for_windows_os]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_CLI_Configure_Precedence_Policy'
    common_name = '[%s] Create the precedence policy' % tcname
    test_cfgs.append(({'prece_policy_list': [prece_policy]}, test_name, common_name, 1, False))
    
    test_wlan_cfg = wlan_cfg.copy()
    test_wlan_cfg.update({'dvcpcy_name': dvcpcy_for_Linux['name'],
                          'prece_name': prece_policy['name']})
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '[%s] Create WLAN with Linux policy' % tcname
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg}, test_name, common_name, 1, False))
    
    atest_wlan_cfg = deepcopy(test_wlan_cfg)
    atest_wlan_cfg['auth'] = test_wlan_cfg['sta_auth']
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] Windows client can not access to the WLAN for Linux' % tcname
    test_cfgs.append(({'wlan_cfg': atest_wlan_cfg,
                       'sta_tag': sta_tag,
                       'negative_test': True}, test_name, common_name, 2, False))
    
    test_wlan_cfg1 = wlan_cfg.copy()
    test_wlan_cfg1.update({'dvcpcy_name': dvcpcy_for_windows_os['name'],
                           'prece_name': prece_policy['name']})
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '[%s] Edit WLAN to apply the Windows policy' % tcname
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg1}, test_name, common_name, 1, False))
    
    expected_test_info = expected_info.copy()
    expected_test_info.update({'expected_subnet': aaa_subnet,
                               'wlan_cfg': test_wlan_cfg1, 
                               'rate_limit': dvcpcy_rate_limit})
    
    steps = _define_policy_test_steps(expected_test_info, tcname)
    test_cfgs.extend(list(steps))
    
    tcname = tcnames[1]
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s] Disassociate the client' % tcname
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 1, False))
                    
    steps = _define_policy_test_steps(expected_test_info, tcname)  
    test_cfgs.extend(list(steps))
    
    test_wlan_cfg2 = wlan_cfg.copy()
    test_wlan_cfg2.update({'dvcpcy_name': False,
                           'prece_name': prece_policy['name']})
    tcname = tcnames[2]
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '[%s] Edit WLAN to remove the Windows device policy' % tcname
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg2}, test_name, common_name, 1, False))
    
    wlan_expected_test_info = expected_info.copy()
    wlan_expected_test_info.update({'expected_subnet': aaa_subnet,
                                    'wlan_cfg': test_wlan_cfg2, 
                                    'rate_limit': aaa_rate_limit})             
    steps = _define_policy_test_steps(wlan_expected_test_info, tcname, ' - without policy')
    test_cfgs.extend(list(steps))
    
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '[%s] Edit WLAN to re-add the Windows device policy' % tcname
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg1}, test_name, common_name, 1, False))
      
    steps = _define_policy_test_steps(expected_test_info, tcname, ' - with policy')
    test_cfgs.extend(list(steps))
      
    tcname = tcnames[3]
    test_name = 'CB_ZD_CLI_Configure_Device_Policy'
    common_name = '[%s] Modify the Windows device policy' % tcname
    test_cfgs.append(({'device_policy_list': [mod_dvcpcy_for_windows_os]}, test_name, common_name, 1, False))
    
    mod_expected_test_info = expected_info.copy()
    mod_expected_test_info.update({'expected_subnet': aaa_subnet,
                                   'wlan_cfg': test_wlan_cfg1, 
                                   'rate_limit': mod_dvcpcy_rate_limit})             
    steps = _define_policy_test_steps(mod_expected_test_info, tcname)
    test_cfgs.extend(list(steps))
    
    tcname = tcnames[4]
    test_name = 'CB_ZD_CLI_Configure_Device_Policy'
    common_name = '[%s] Create the new Windows device policy' % tcname
    test_cfgs.append(({'device_policy_list': [new_dvcpcy_for_windows_os]}, test_name, common_name, 1, False))
    
    test_wlan_cfg2 = wlan_cfg.copy()
    test_wlan_cfg2.update({'dvcpcy_name': new_dvcpcy_for_windows_os['name'],
                           'prece_name': prece_policy['name']})
    
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '[%s] Apply the new policy to WLAN' % tcname
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg2}, test_name, common_name, 1, False))
    
    new_expected_test_info = expected_info.copy()
    new_expected_test_info.update({'expected_subnet': aaa_subnet,
                                   'wlan_cfg': test_wlan_cfg1, 
                                   'rate_limit': new_dvcpcy_rate_limit})              
    steps = _define_policy_test_steps(new_expected_test_info, tcname)
    test_cfgs.extend(list(steps))
    
    tcname = tcnames[5]
    test_name = 'CB_ZD_Reboot_AP'
    common_name = '[%s] Reboot active AP' % tcname
    test_cfgs.append(({'ap_tag': ap_tag,
                       'reboot': 'by ap'}, test_name, common_name, 1, False))
    
    steps = _define_policy_test_steps(new_expected_test_info, tcname)
    test_cfgs.extend(list(steps))
    
    tcname = tcnames[6]
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '[%s] Reboot ZD' % tcname
    test_cfgs.append(({}, test_name, common_name, 1, False))
              
    steps = _define_policy_test_steps(new_expected_test_info, tcname)
    test_cfgs.extend(list(steps))
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove All WLANs'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Delete_AAA_Servers'
    common_name = 'Remove All AAA server'
    test_cfgs.append(({'server_name_list': [aaa_server['server_name']]}, test_name, common_name, 0, True))
    
    #@ZJ 20150331 ZF-10705
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    return test_cfgs

def _define_policy_test_steps(expected_test_info, tcname, tag=''):
    test_cfgs = []
    wlan_cfg = deepcopy(expected_test_info['wlan_cfg'])
    wlan_cfg['auth'] = wlan_cfg['sta_auth']

    # Verify client associate
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '[%s] Verify client association%s' % (tcname, tag)
    test_cfgs.append(({'sta_tag': expected_test_info['sta_tag'],
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False))
    
    # Verify client subnet/vlan info
    test_name = 'CB_Station_Verify_IP_Config'
    common_name = '[%s] Verify client ip information%s' % (tcname, tag)
    test_cfgs.append(({'sta_tag': expected_test_info['sta_tag'],
                       'expected_subnet': expected_test_info['expected_subnet']}, test_name, common_name, 2, False))
    
    # Verify limiting
    if expected_test_info.get('rate_limit'):
        test_name = 'CB_Zap_Traffic_Station_LinuxPC'
        common_name = '[%s] Verify Client Uplink traffic%s' % (tcname, tag)
        test_cfgs.append(({'rate_limit': expected_test_info['rate_limit']['uplink'],
                           'margin_of_error': expected_test_info['rate_limit']['margin_of_error'],
                           'link_type': 'up',
                           'sta_tag': expected_test_info['sta_tag'],
                           'ssid': expected_test_info['wlan_cfg']['ssid']}, test_name, common_name, 2, False))
        
        test_name = 'CB_Zap_Traffic_Station_LinuxPC'
        common_name = '[%s] Verify Client Downlink traffic%s' % (tcname, tag)
        test_cfgs.append(({'rate_limit': expected_test_info['rate_limit']['downlink'],
                           'margin_of_error': expected_test_info['rate_limit']['margin_of_error'],
                           'link_type': 'down',
                           'sta_tag': expected_test_info['sta_tag'],
                           'ssid': expected_test_info['wlan_cfg']['ssid']}, test_name, common_name, 2, False))
    
    return test_cfgs
 
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    ap_sym_dict = tbcfg['ap_sym_dict']
    sta_ip_list = tbcfg['sta_ip_list']
    target_sta_radio = 'ng'
    
    active_ap = testsuite.getActiveAp(ap_sym_dict)[0]            
    target_station = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ")
    
    test_cfgs = define_test_cfg({'active_ap': active_ap,
                                 'target_station': target_station,
                                 'radio_mode': target_sta_radio,
                                 })
        
    ts_name = "Device Policy"
    ts = testsuite.get_testsuite(ts_name, "Verify Device Policy feature", combotest=True)
    
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
