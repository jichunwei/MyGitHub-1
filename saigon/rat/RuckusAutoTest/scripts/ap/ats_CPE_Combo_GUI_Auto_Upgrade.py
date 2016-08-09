"""
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
     This script is verify CPE auto upgrade via GUI.
"""

import sys
import random

import libCPE_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg, model_name):
    test_cfgs = []
    
    test_name = 'CB_CPE_Read_Upgrade_Config_File'
    common_name = 'Read setting from config file'
    test_cfgs.append(({'cfg_file_name': tcfg['cfg_file_name']},test_name, common_name, 0, False))
    
    mf_ip_dict = tcfg['mf_ip_dict']
    
    upgrade_config_dict = {'TFTP': tcfg['manual_tftp_cfg'],
                           'FTP': tcfg['manual_ftp_cfg'],
                           'HTTP': tcfg['manual_http_cfg'],
                           }
    #Add upgrade/downgrade test cases, for each model, each component[IP].
    for model,ip_list in mf_ip_dict.items():
        if model.lower() == model_name:
            for ip_addr in ip_list:
                #Add upgrade via tftp, ftp, http.            
                for up_mtd, up_cfg in upgrade_config_dict.items():
                    test_cfgs.extend(_define_test_cfg_sub(tcfg, up_mtd, up_cfg, model, ip_addr, False))
                    test_cfgs.extend(_define_test_cfg_sub(tcfg, up_mtd, up_cfg, model, ip_addr, True))
    
    return test_cfgs

def _define_test_cfg_sub(tcfg, up_mtd, up_cfg, model, mf_ip_addr, up_flag):
    '''
    Define test config for upgrade and downgrade test cases.
    '''
    manual_up_cfg = {}
    manual_up_cfg.update(up_cfg)
    
    test_cfgs = []
    
    if up_flag:
        action = 'upgrade'
        version = 'target'
        manual_up_cfg['auto'] = True
    else:
        action = 'downgrade'
        version = 'baseline'
        manual_up_cfg['auto'] = False
    
    testcase_name = '[%s Auto %s %s]IP=%s-' % (up_mtd, action, model, mf_ip_addr)
    
    param_cfg = {'model': model, 'up_flag': up_flag}
    test_name = 'CB_AP_Download_Image'
    common_name = '%sDownload the image %s version for %s' % (testcase_name, version, model)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_CPE_Upgrade_Firmware_GUI'
    common_name = '%s %s %s firmware to %s version' % (testcase_name, action.capitalize(), model, version)
    test_cfgs.append(({'up_cfg': manual_up_cfg,
                       'model': model,
                       'ip_addr': mf_ip_addr,
                       'test_type': tcfg['test_type']},
                      test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Firmware_Version'
    common_name = '%sVerify %s current version is %s' % (testcase_name, model, version)
    test_cfgs.append(({'ip_addr': mf_ip_addr,
                       'sleep_time': tcfg['sleep_time_before_check_version'],},
                      test_name, common_name, 1, False)) 
    
    wlan_cfg_list = tcfg['wlan_cfg_list']
    for wlan_cfg in wlan_cfg_list:
        info = '%s_%s_' % (wlan_cfg['auth'], wlan_cfg['encryption'])
        if wlan_cfg.has_key('wpa_ver'):
            info = info + wlan_cfg['wpa_ver']
        else:
            info = info + ''
        
        ssid = '%s_%s_%03d' % (model, info, random.randrange(1, 999))
        
        wlan_cfg['ssid'] = ssid
                
        test_name = 'CB_AP_Config_Wlans'
        common_name = '%sConfig wlans for %s: %s' % (testcase_name, model,info)
        test_cfgs.append(({'ip_addr': mf_ip_addr,
                           'wlan_cfg_list': [wlan_cfg]},
                          test_name, common_name, 1, False))
                          
        test_name = 'CB_AP_Associate_Station_With_Wlans'
        common_name = '%sVerify the station associate to wlan: %s' % (testcase_name, info)
        test_cfgs.append(({'wlans_cfg_list': [wlan_cfg]},
                          test_name, common_name, 1, False))
    
    return test_cfgs

def _define_wlan_cfg_list():
    encryp_cfg_list = []
    
    #Code for all posible encryption.
    '''
    #Add wpa encryption settings.
    auth_list = ['PSK','EAP']
    wpa_ver_list = ['WPA2', 'WPA', 'WPA-Auto']
    cipher_list = ['AES', 'TKIP', 'Auto']
    
        
    eap_cfg = {'ras_addr': '192.168.0.252',
               'ras_port': '1812',
               'ras_secret': '1234567890',
               'username': 'rad.eap.user',
               'password': 'rad.eap.user'}
        
    for wpa_ver in wpa_ver_list:
       for cipher in cipher_list:
           for auth in auth_list:
                encryp_cfg = dict(auth=auth,wpa_ver=wpa_ver,encryption=cipher,key_string='123456789')
                if auth == 'EAP':                
                    encryp_cfg.update(eap_cfg)
                encryp_cfg_list.append(encryp_cfg)   
    '''
    
    #Code for some encryption. PSK-WPA-TKIP, EAP-WPA2-AES
    auth_list = ['PSK','EAP']
    wpa_ver_list = ['WPA', 'WPA2']
    cipher_list = ['TKIP', 'AES']
    
    for i in range(0,len(auth_list)):
        auth = auth_list[i]
        wpa_ver = wpa_ver_list[i]
        cipher = cipher_list[i]
        encryp_cfg = dict(auth=auth,wpa_ver=wpa_ver,encryption=cipher,key_string='123456789')
        if auth == 'EAP':                
            encryp_cfg.update(eap_cfg)
        encryp_cfg_list.append(encryp_cfg)
    
    #Home wlan: wlan_if = 'wlan0', name='home'
    wlan_name_list = ['home']  
    
    wlan_cfg_list = []
    for wlan_name in wlan_name_list:
        for cfg in encryp_cfg_list:
            wlan_cfg = {}
            wlan_cfg['wlan_name'] = wlan_name
            wlan_cfg.update(cfg)
            wlan_cfg_list.append(wlan_cfg)
            
    return wlan_cfg_list

def define_test_parameters(tbcfg):
    cfg_file_name = tbcfg['cfg_file_name']
    mf_ip_dict = tbcfg['mf_ip_dict']
    
    default_upgrade_cfg = {'proto':'tftp',
                           'auto': True,
                           'firstcheck':'3',
                           'interval':'60',
                           }
    
    manual_tftp_cfg = {}
    manual_tftp_cfg.update(default_upgrade_cfg)
    manual_tftp_cfg['proto'] = 'tftp'
    
    manual_ftp_cfg = {}
    manual_ftp_cfg.update(default_upgrade_cfg)
    manual_ftp_cfg['proto'] = 'ftp'
    
    manual_http_cfg = {}
    manual_http_cfg.update(default_upgrade_cfg)
    manual_http_cfg['proto'] = 'http'
    
    cfg = {'manual_tftp_cfg': manual_tftp_cfg,
           'manual_ftp_cfg': manual_ftp_cfg,
           'manual_http_cfg': manual_http_cfg,
           'wlan_cfg_list': _define_wlan_cfg_list(),
           'test_type': 'gui',
           'cfg_file_name': cfg_file_name,
           'mf_ip_dict': mf_ip_dict,
           }
    
    return cfg 

def create_test_suite(**kwargs):
    tb = testsuite.getTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    tcfg = define_test_parameters(tbcfg)
    
    tcfg['sleep_time_before_check_version'] = 7*60 + 30
    
    model_id_name_map = {'1': 'mf2211',
                         '2': 'mf7211',}
    model_id = raw_input("Please input model[1-mf2211,2-mf7211, Default is 1]:")
    if not model_id:
        model_id = '1'
        
    model_name = model_id_name_map[model_id]
    
    key = 'up_cfg_%s' % model_name
    baseline = "%s %s" % (tbcfg[key]['baseline_build_stream'],tbcfg[key]['baseline_bno'])
    target = "%s %s" % (tbcfg[key]['target_build_stream'],tbcfg[key]['target_bno'])
        
    ts_name = 'CPE GUI - Auto upgrade firmware %s to %s' % (baseline, target)
    ts = testsuite.get_testsuite(ts_name, 'Verify CPE auto upgrade via GUI', combotest=True)
    test_cfgs = define_test_cfg(tcfg, model_name)

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
    create_test_suite(**_dict)
    