"""
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com
"""

import os
import sys
import random

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_KwList as kwlist

def define_psk_batch_file_paths():
    batch_files = {}
    working_path = os.getcwd().split('\\rat')[0]
    batches_dir = '\\rat\\RuckusAutoTest\\common\\dpsk_batches\\'
    batch_files['test_dpsk_for_invalid_vlan_id'] = working_path + batches_dir + 'test_dpsk_for_invalid_vlan_id.csv'
    batch_files['test_dpsk_for_vlan_10'] = working_path + batches_dir + 'test_dpsk_for_vlan_10.csv'
     
    for value in batch_files.values():
        if not os.path.isfile(value):
            raise Exception('Please check "%s" is not a file' % value)
        
    return batch_files

def define_wlan_cfg():
    wlan_cfgs = []    
   
    wlan_cfgs.append(dict(ssid = 'OPEN-WPA2-DVLAN', auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          do_zero_it = True, do_dynamic_psk = True))
        
    wlan_cfgs.append(dict(ssid = 'MAC-WPA2-DVLAN', auth = "MAC", wpa_ver = "WPA2", encryption = "AES",#Chico, 2015-5-5, remove WPA and add MAC auth WLAN
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          do_zero_it = True, do_dynamic_psk = True))    
    return wlan_cfgs


def define_test_cfg(cfg):
    test_cfgs = []
    ras_cfg = dict(server_addr = cfg['ras_ip_addr'],
                   server_port = cfg['ras_port'],
                   server_name = cfg['ras_name'],
                   radius_auth_secret = cfg['radius_auth_secret']
                   )
    wlan_cfg1 = cfg['wlan_cfg_list'][0]
    wlan_cfg2 = cfg['wlan_cfg_list'][1]
    local_username = 'local.user'
    local_password = 'local.user'
    vlan10_info = {'vlan': '10',
                   'expected_network': '192.168.10.252/255.255.255.0',
                   'target_ping_ip': '192.168.10.252',
                   'username': 'finance.user',
                   'password': 'finance.user'}
    vlan20_info = {'vlan': '20',
                   'expected_network': '192.168.20.252/255.255.255.0',
                   'target_ping_ip': '192.168.20.252',
                   'username': 'marketing.user',
                   'password': 'marketing.user'}
    vlan2_info =  {'vlan': '2',
                   'expected_network': '20.0.2.252/255.255.255.0',
                   'target_ping_ip': '20.0.2.252',
                   'username': '',
                   'password': ''}
    
    default_info = {'vlan': '',
                   'expected_network': '192.168.0.252/255.255.255.0',
                   'target_ping_ip': '192.168.0.252',
                   'username': '',
                   'password': ''}
    
    attached_vlan_cfg = {'vlan_id': '2'}
    
    dpsk_vlan_set_to_10 = {'wlan': wlan_cfg1['ssid'], 'number_of_dpsk': '1', 'vlan': '10'}
    dpsk_vlan_set_to_20 = {'wlan': wlan_cfg2['ssid'], 'number_of_dpsk': '1', 'vlan': '20'}
    
    #@author:yuyanan @since:2014-7-24 bug:zf-9305 optimize get profile from run but not test suite 
    dpsk_with_profile_vlan_10 = {'file_name': 'test_dpsk_for_vlan_10.csv', 'wlan': wlan_cfg1['ssid']}
    dpsk_with_profile_vlan_0 = {'file_name': 'test_dpsk_for_invalid_vlan_id.csv', 'wlan': wlan_cfg1['ssid']}
    
    testcases = ['OPEN WLAN - DVLAN ZeroIT authenticate by vlan user',
                 'OPEN WLAN - DVLAN ZeroIT authenticate by non-vlan user',                 
                 'OPEN WLAN - DVLAN ZeroIT VLAN attached authenticate by vlan user',
                 'OPEN WLAN - DVLAN ZeroIT VLAN attached authentication by non-vlan user',
                 'OPEN WLAN - DVLAN ZeroIT authenticate by local user',
                 'OPEN WLAN WPA2 - DVLAN with manual DPSK generation',
                 'MAC WLAN WPA2 - DVLAN with manual DPSK generation',
                 'OPEN WLAN - DVLAN client association with original key',
                 'OPEN WLAN - DVLAN - DPSK Profile upload with VID',
                 'OPEN WLAN - DVLAN - DPSK Profile upload with VID is NULL',
                 ]
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Configure the station %s' % cfg['target_station']    
    test_cfgs.append(({'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station'],}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Authentication_Server'
    common_name = 'Create the authentication server'
    test_cfgs.append(({'auth_ser_cfg_list':[ras_cfg]}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create local user "%s" on ZD' % local_username   
    test_cfgs.append(({'username': local_username,
                       'password': local_password}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlan'
    common_name = 'Create WLAN "%s" and "%s"on ZD' % (wlan_cfg1['ssid'], wlan_cfg2['ssid'])
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg1, wlan_cfg2]}, test_name, common_name, 0, False))
    
    enable_dvlan_cfg = {'dvlan': True}
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = 'Enable DVLAN on WLAN "%s"' % wlan_cfg1['ssid']   
    test_cfgs.append(({'wlan_ssid': wlan_cfg1['ssid'], 'new_wlan_cfg': enable_dvlan_cfg}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = 'Enable DVLAN on WLAN "%s"' % wlan_cfg2['ssid']   
    test_cfgs.append(({'wlan_ssid': wlan_cfg2['ssid'], 'new_wlan_cfg': enable_dvlan_cfg}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = 'Set authentication server for Zero IT'
    test_cfgs.append(({'zero_it_auth_serv': ras_cfg['server_name']}, test_name, common_name, 0, True))
    
    # test with vlan user  
    wlan_cfg_for_zeroit_dvlan_user = {'ssid': wlan_cfg1['ssid'],
                                      'auth': wlan_cfg1['auth'],
                                      'use_radius': None,
                                      'username':vlan10_info['username'],
                                      'password':vlan10_info['password']}
    _define_test_associate_by_zeroit(test_cfgs, wlan_cfg_for_zeroit_dvlan_user, vlan10_info, testcases[0])
    
    # test with normal user
    info = dict(default_info)
    info.update({'username': 'ras.local.user',
                 'password': 'ras.local.user'})
    wlan_cfg_for_zeroit_non_dvlan_user = {'ssid': wlan_cfg1['ssid'],
                                          'auth': wlan_cfg1['auth'],
                                          'use_radius': None,
                                          'username': info['username'],
                                          'password': info['password']}    
    _define_test_associate_by_zeroit(test_cfgs, wlan_cfg_for_zeroit_non_dvlan_user, info, testcases[1])
     
    # attached VLAN
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: attach VLAN 2 on WLAN "%s"' % (testcases[2], wlan_cfg1['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg1['ssid'], 'new_wlan_cfg': attached_vlan_cfg}, 
                      test_name, common_name, 1, False))    
    _define_test_associate_by_zeroit(test_cfgs, wlan_cfg_for_zeroit_dvlan_user, vlan10_info, testcases[2])
    
    # attached VLAN - normal user  
    info2 = dict(vlan2_info)
    info2.update({'username': 'ras.local.user',
                  'password': 'ras.local.user'})
    _define_test_associate_by_zeroit(test_cfgs, wlan_cfg_for_zeroit_non_dvlan_user, info2, testcases[3])
    
    recover_dpsk_cfg = {'vlan_id': '1'}
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: recover VLAN setting on WLAN "%s"' % (testcases[3], wlan_cfg1['ssid'])   
    test_cfgs.append(({'wlan_ssid': wlan_cfg1['ssid'], 'new_wlan_cfg': recover_dpsk_cfg}, 
                      test_name, common_name, 1, True))
    
    # test with local user
    test_name = 'CB_ZD_ZeroIT_Select_Auth_Server'
    common_name = '[%s]: set Local Database for Zero IT' % testcases[4]
    test_cfgs.append(({'zero_it_auth_serv': 'Local Database'}, test_name, common_name, 0, True))
    
    info1 = dict(default_info)
    info1.update({'username': local_username,
                  'password': local_password})
    wlan_cfg_for_zeroit_local_user = {'ssid': wlan_cfg1['ssid'],
                                      'auth': wlan_cfg1['auth'],
                                      'use_radius': None,
                                      'username': local_username,
                                      'password': local_username}
    _define_test_associate_by_zeroit(test_cfgs, wlan_cfg_for_zeroit_local_user, info1, testcases[4])
        
    # WPA manual DPSK generation vlan 10
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: manual generate dpsk with vlan 10' % testcases[5] 
    test_cfgs.append(({'dpsk_conf': dpsk_vlan_set_to_10}, test_name, common_name, 1, False))      
    
    _define_test_associate_by_key(test_cfgs, wlan_cfg1['ssid'], 'dpsk', vlan10_info, testcases[5])
    
    # WPA2 manual DSPK generation vlan 20
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: manual generate dpsk with vlan 20' % testcases[6] 
    test_cfgs.append(({'dpsk_conf': dpsk_vlan_set_to_20}, test_name, common_name, 1, False))
    
    _define_test_associate_by_key(test_cfgs, wlan_cfg2['ssid'], 'dpsk', vlan20_info, testcases[6])
    
    # Association with original key
    
    _define_test_associate_by_key(test_cfgs, wlan_cfg1['ssid'], 'non-dpsk', default_info, testcases[7])
    
    # upload file with VID is 10
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: generate dpsk by profile with vlan 10' % testcases[8] 
    test_cfgs.append(({'dpsk_conf': dpsk_with_profile_vlan_10}, test_name, common_name, 1, False))
    
    _define_test_associate_by_key(test_cfgs, wlan_cfg1['ssid'], 'dpsk', vlan10_info, testcases[8])
    
    # upload file with VID is 0 (null)
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: generate dpsk by profile with vlan 0' % testcases[9] 
    test_cfgs.append(({'dpsk_conf': dpsk_with_profile_vlan_0}, test_name, common_name, 1, False))
    
    _define_test_associate_by_key(test_cfgs, wlan_cfg1['ssid'], 'dpsk', default_info, testcases[9])
    
    # clean up
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = 'Remove all DPSK from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))    
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Authentication_Server'
    common_name = 'Remove all AAA server setting on ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
       
    return test_cfgs

def _define_test_associate_by_zeroit(test_cfgs, wlan_cfg, info, tc_name):
    expect_sta_info =  {'wlan': wlan_cfg['ssid'],
                        'status': 'Authorized',
                        'ip': wlan_cfg['username']}
    if info['vlan']:
        expect_sta_info['vlan'] = info['vlan']
        
    test_name = 'CB_ZD_Station_Config_Wlan_With_ZeroIT'
    common_name = '[%s]: associate the station' % tc_name
    test_cfgs.append(({'sta_tag': 'sta1', 
                       'wlan_cfg': wlan_cfg}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]: verify the station information on ZD' % tc_name
    test_cfgs.append(({'sta_tag': 'sta1',
                       'expected_network':  info['expected_network'], 
                       'expected_station_info': expect_sta_info}, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '[%s]: the station ping a target ip %s' % (tc_name, info['target_ping_ip'])
    test_cfgs.append(({'sta_tag': 'sta1',
                       'dest_ip': info['target_ping_ip']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '[%s]: remove all wlans from the station' % tc_name
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))

def _define_test_associate_by_key(test_cfgs, wlan_ssid, key_type, info, tc_name):
    if key_type == 'dpsk':
        test_name = 'CB_Station_Association_WLAN_With_DPSK'
    else:
        test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    
    common_name = '[%s]: associate the station' % tc_name
    test_cfgs.append(({'sta_tag': 'sta1', 'wlan_ssid': wlan_ssid}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Station_Info'
    common_name = '[%s]: verify the station information on ZD' % tc_name
    test_cfgs.append(({'sta_tag': 'sta1',
                       'expected_network': info['expected_network'], 
                       'wlan_ssid': wlan_ssid,
                       }, test_name, common_name, 2, False))
        
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = '[%s]: the station ping a target ip %s' % (tc_name, info['target_ping_ip'])
    test_cfgs.append(({'sta_tag': 'sta1',
                       'dest_ip': info['target_ping_ip']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s - remove all wlans from the station' % tc_name
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))

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
        
    batch_files = define_psk_batch_file_paths()
    wlan_cfg_list = define_wlan_cfg()    
    
    tcfg = {'ras_ip_addr':ras_ip_addr,
            'ras_port' : '1812',
            'ras_name' : ras_ip_addr,
            'radius_auth_secret': '1234567890',
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'target_sta_radio': target_sta_radio,
            'wlan_cfg_list': wlan_cfg_list,
            'batch_files': batch_files
            }
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "Open WLAN - DVLAN Functionality"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the functionality of OPEN WLAN with DVLAN support",
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
    