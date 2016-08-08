'''
Created on 2011-6-30
@author: cherry.cheng@ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg):
    test_cfgs = []
    
    test_name = 'CB_ZD_Load_Upgrade_Config'
    common_name = 'Load setting from config file'
    test_cfgs.append(({'cfg_file_name': tcfg['cfg_file_name']},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Find_Station'
    common_name = 'Get target station'
    test_cfgs.append(( {'target_station': tcfg['target_station']}, test_name, common_name, 0, False))
    
    #Add downgrade to base line test cases.
    test_cfgs.extend(define_sub_test_cfg(tcfg, False))
    #Add upgrade to base line test cases.
    test_cfgs.extend(define_sub_test_cfg(tcfg, True))
    
    return test_cfgs
    
    
def define_sub_test_cfg(tcfg, up_flag):
    test_cfgs = []
    
    if up_flag: 
        action = 'upgrade'
        version = 'target'
    else:
        action = 'downgrade'
        version = 'baseline'
        
    test_case_name = 'ZD %s' % (action.capitalize())
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '[%s]Verify AP approved and connected' % (test_case_name,)
    test_cfgs.append(( {'is_need_approval': False}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[%s]Associate station to wlan before %s' % (test_case_name, action)
    test_cfgs.append(( {'wlan_cfg': tcfg['wlan_cfg']}, test_name, common_name, 1, False))
    
    '''
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '[%s]Associate station to wlans before %s' % (test_case_name, action)
    test_cfgs.append(( {'wlan_cfg_list': tcfg['wlan_cfg_list']}, test_name, common_name, 1, False))
    '''
    
    param_cfg = {'up_flag': up_flag}
    test_name = 'CB_ZD_Download_Image'
    common_name = '[%s]Download %s version firmware for ZD' % (test_case_name, version)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Upgrade'
    common_name = '[%s]%s ZD Firmware to %s version' % (test_case_name, action.capitalize(), version)
    param_cfg = dict(force_upgrade = True)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Check_Firmware_Version'
    common_name = '[%s]Verify ZD version is %s version' % (test_case_name, version)
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Join'
    common_name = '[%s]Verify AP approved and connected after %s' % (test_case_name, action)
    test_cfgs.append(( {'is_need_approval': True}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Get_Support_AP_Versions'
    common_name = '[%s]Get ZD support AP firmware versions' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Versions'
    common_name = '[%s]Verify AP firmware versions' % (test_case_name,)
    test_cfgs.append(( {}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[%s]Associate station to wlan after %s' % (test_case_name, action)
    test_cfgs.append(( {'wlan_cfg': tcfg['wlan_cfg']}, test_name, common_name, 2, False))
    
    return test_cfgs

def define_test_params(tbcfg):
    '''
    Please set parameter to what you want, test cases will fetch parameters from it directly.
    '''
    tcfg = dict()
    
    tcfg['timeout'] = 1200
    tcfg['cfg_file_name'] = "./RuckusAutoTest/common/ZD_Upgrade_Info_Default.inf"
    
    #Note: When Open + WPA/WPA2, auth is PSK.
    wlan_cfg_list = []
    wlan_cfg = dict(ssid = 'TikonaWlanWithRootAP', auth = "PSK", wpa_ver = "WPA2", 
                            encryption = "AES", key_string = "1234567890")
    wlan_cfg_list.append(wlan_cfg)
    
    wlan_cfg = dict(ssid = 'TikonaWlanWithMeshAP', auth = "PSK", wpa_ver = "WPA2", 
                            encryption = "AES", key_string = "1234567890")
    wlan_cfg_list.append(wlan_cfg)
    
    wlan_cfg = dict(ssid = 'TikonaWlanWithEMAP', auth = "PSK", wpa_ver = "WPA2", 
                            encryption = "AES", key_string = "1234567890")
    wlan_cfg_list.append(wlan_cfg)
    
    wlan_cfg = dict(ssid = 'TikonaWlanWithMAPNoEmap', auth = "PSK", wpa_ver = "WPA2", 
                            encryption = "AES", key_string = "1234567890")
    wlan_cfg_list.append(wlan_cfg)
    
    tcfg['wlan_cfg'] = wlan_cfg_list[0]
    tcfg['wlan_cfg_list'] = wlan_cfg_list
    
    if tbcfg['sta_ip_list']:
        tcfg['target_station'] = tbcfg['sta_ip_list'][0]
    else:
        tcfg['target_station'] = '192.168.1.11'
    
    '''
    - wlan_conf['ssid']: a string represents the SSID of the WLAN
        - wlan_conf['auth']: authentication method, can be "open", "shared", "PSK", or "EAP"
        - wlan_conf['wpa_ver']: WPA version, can be "WPA" or "WPA2"
        - wlan_conf['encryption']: encryption method, can be "WEP64", "WEB128", "TKIP" or "AES"
        - wlan_conf['key_string']: key material, can be a string of ASCII characters or string of hexadecimal characters
        - wlan_conf['key_index']: WEP key index, can be 1, 2, 3 or 4
        - wlan_conf['username'] and wlan_conf['password']: Radius username/password
    '''
    
    return tcfg

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD GUI - Upgrade ZD Firmware for Tikona'
    ts = testsuite.get_testsuite(ts_name, 'Verify ZD is upgraded', combotest=True)
    
    param_cfgs = define_test_params(tbcfg)        
    test_cfgs = define_test_cfg(param_cfgs)
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
    _dict['tbtype'] = 'ZD_Stations'
    createTestSuite(**_dict)
