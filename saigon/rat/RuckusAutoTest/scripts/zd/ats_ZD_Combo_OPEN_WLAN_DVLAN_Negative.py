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
    batch_files['test_dpsk_invalid_format'] = working_path + batches_dir + 'test_dpsk_invalid_format.csv'
     
    for value in batch_files.values():
        if not os.path.isfile(value):
            raise Exception('Please check "%s" is not a file' % value)
        
    return batch_files

def define_wlan_cfg():
    wlan_cfgs = []    

    wlan_cfgs.append(dict(ssid = 'OPEN-WPA2-DVLAN', auth = "PSK", wpa_ver = "WPA2", encryption = "AES",#Chico, 2015-5-5, WPA to WPA2
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = "",
                          do_zero_it = True, do_dynamic_psk = True, dvlan = True))
    
    wlan_cfgs.append(dict(ssid = 'OPEN-MAC-AUTH', auth = "open", wpa_ver = "mac", encryption = "none",
                          key_index = "" , key_string = "",
                          username = "", password = "", auth_svr = ""))   
    return wlan_cfgs

def define_test_cfg(cfg):
    test_cfgs = []
    wlan_cfg = cfg['wlan_cfg_list'][0]
    mac_wlan_cfg = cfg['wlan_cfg_list'][1]
    
    #@author:yuyanan @since:2014-7-24 bug:zf-9305 optimize: get dpsk profile path according to filename after script run 
    invalid_vid_cfg = {'file_name': 'test_dpsk_for_invalid_vlan_id.csv', 'wlan': wlan_cfg['ssid']}
    invalid_format_cfg = {'file_name': 'test_dpsk_invalid_format.csv', 'wlan': wlan_cfg['ssid']}
    
    invalid_manual_cfg = {'wlan': wlan_cfg['ssid'], 'number_of_dpsk': '5', 'vlan': ''}
    
    tc1_name = 'OPEN WLAN - DVLAN with profile including invalid VID'
    tc2_name = 'OPEN WLAN - DVLAN with profile including invalid format'
    tc3_name = 'OPEN WLAN - DVLAN manual set with invalid VID'
    tc4_name = 'OPEN MAC AUTH WLAN - can not configure DVLAN option'
    
    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create WLAN "%s" on ZD' % wlan_cfg['ssid']   
    test_cfgs.append(({'wlan_cfg_list': [wlan_cfg]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: fail to keep the invalid VLAN ID info' % tc1_name   
    test_cfgs.append(({'dpsk_conf': invalid_vid_cfg, 'negative': True}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: fail by rejecting the file' % tc2_name 
    test_cfgs.append(({'dpsk_conf': invalid_format_cfg, 'negative': True}, test_name, common_name, 1, False))
    

    #@author: Tanshixiong @since: 2015-1-30 bug: zf-11870
    vlan_set_to_0 = dict(invalid_manual_cfg)
    vlan_set_to_0.update({'vlan':'0'})
    vlan_set_to_4095 = dict(invalid_manual_cfg)
    vlan_set_to_4095.update({'vlan':'4095'})
    vlan_set_to_char = dict(invalid_manual_cfg)
    vlan_set_to_char.update({'vlan':'a'})
    vlan_set_to_string = dict(invalid_manual_cfg)
    vlan_set_to_string.update({'vlan':'abc'}) 
    
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: fail to set vlan id to 0' % tc3_name 
    test_cfgs.append(({'dpsk_conf': vlan_set_to_0, 'negative': True}, test_name, common_name, 1, False))      
    
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: fail to set vlan id to 4095' % tc3_name 
    test_cfgs.append(({'dpsk_conf': vlan_set_to_4095, 'negative': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: fail to set vlan id by char' % tc3_name 
    test_cfgs.append(({'dpsk_conf': vlan_set_to_char, 'negative': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '[%s]: fail to set vlan id by string' % tc3_name 
    test_cfgs.append(({'dpsk_conf': vlan_set_to_string, 'negative': True}, test_name, common_name, 2, False))

    enable_dvlan_cfg = {'do_zero_it': True,
                        'do_dynamic_psk': True,
                        'dvlan': True}
    
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s]: create WLAN "%s" on ZD' % (tc4_name, mac_wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_cfg_list': [mac_wlan_cfg]}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '[%s]: enable DPSK on WLAN "%s"' % (tc4_name, mac_wlan_cfg['ssid'])   
    test_cfgs.append(({'wlan_ssid': mac_wlan_cfg['ssid'], 'new_wlan_cfg': enable_dvlan_cfg, 'negative_test': True}, 
                      test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = 'Remove all DPSK from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD'
    test_cfgs.append(({}, test_name, common_name, 0, True))    
       
    return test_cfgs

def createTestSuite(**kwargs):
    attrs = dict(interactive_mode = True,
                 station = (0,"g"),
                 targetap = False,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    batch_files = define_psk_batch_file_paths()

    wlan_cfg_list = define_wlan_cfg()
    tcfg = {'wlan_cfg_list': wlan_cfg_list,
            'batch_files': batch_files,
            }
    test_cfgs = define_test_cfg(tcfg)

    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "Open WLAN - DVLAN Negative"
    
    ts = testsuite.get_testsuite(ts_name,
                                 "Verify the negative setting option for OPEN WLAN with DVLAN support",
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
    