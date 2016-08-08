"""
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
     This script is verify CPE manual upgrade via CLI.
"""

import sys
import random

import libCPE_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(tcfg, model_name, repeat_times):
    test_cfgs = []
    
    upgrade_config_dict = {'FTP': tcfg['manual_ftp_cfg']}
    
    ap_ip_list = tcfg['ap_ip_list']
    #repeat_times = tcfg['repeat_times'] 
    model_name = tcfg['ap_model']
    
    for i in range(0, repeat_times):
        for ip_addr in ap_ip_list:
            #Add upgrade via tftp, ftp, http.            
            for up_mtd, up_cfg in upgrade_config_dict.items():
                test_cfgs.extend(_define_test_cfg_sub(tcfg, up_mtd, up_cfg, model_name, ip_addr, False))
                test_cfgs.extend(_define_test_cfg_sub(tcfg, up_mtd, up_cfg, model_name, ip_addr, True))

    return test_cfgs

def _define_test_cfg_sub(tcfg, up_mtd, up_cfg, model, mf_ip_addr, up_flag):
    '''
    Define test config for upgrade and downgrade test cases.
    '''
    manual_up_cfg = {}
    manual_up_cfg.update(up_cfg)
    manual_up_cfg['auto'] = False
    
    test_cfgs = []
    
    if up_flag:
        action = 'upgrade'
        version = 'target'
    else:
        action = 'downgrade'
        version = 'baseline'
    
    ap_fw_upgrade_cfg = tcfg['ap_fw_upgrade_cfg']
    
    testcase_name = '[%s Manual %s %s %s]%s-' % (up_mtd, action, model, random.randrange(1, 9999), mf_ip_addr)
    
    param_cfg = {'model': model, 'up_flag': up_flag, 'ap_fw_upgrade_cfg': ap_fw_upgrade_cfg}
    test_name = 'CB_AP_Download_Image'
    common_name = '%sDownload the image %s version for %s' % (testcase_name, version, model)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
        
    test_name = 'CB_AP_Upgrade_Firmware'
    common_name = '%s %s %s firmware to %s version' % (testcase_name, action.capitalize(), model, version)
    test_cfgs.append(({'up_cfg': manual_up_cfg,
                       'ap_fw_upgrade_cfg': ap_fw_upgrade_cfg,
                       'model': model,
                       'ip_addr': mf_ip_addr,
                       'test_type': tcfg['test_type']},
                      test_name, common_name, 2, False))
    
    test_name = 'CB_AP_Verify_Firmware_Version'
    common_name = '%sVerify %s current version is %s' % (testcase_name, model, version)
    test_cfgs.append(({'ip_addr': mf_ip_addr,
                       'ap_fw_upgrade_cfg': ap_fw_upgrade_cfg,
                       'sleep_time': tcfg['sleep_time_before_check_version'],
                       },
                      test_name, common_name, 2, False))
    
    wlan_cfg_list = tcfg['wlan_cfg_list']
    for wlan_cfg in wlan_cfg_list:
        info = '%s_%s_' % (wlan_cfg['auth'], wlan_cfg['encryption'])
        if wlan_cfg.has_key('wpa_ver'):
            info = info + wlan_cfg['wpa_ver']
        else:
            info = info + ''
        
        ssid = '%s_%s_%06d' % (model, info, random.randrange(1, 999999))
        
        wlan_cfg['ssid'] = ssid
        
        test_name = 'CB_AP_Config_Wlans'
        common_name = '%sConfig wlans for %s: %s' % (testcase_name, model,info)
        test_cfgs.append(({'ip_addr': mf_ip_addr,
                           'wlan_cfg_list': [wlan_cfg],
                           'ap_fw_upgrade_cfg': ap_fw_upgrade_cfg
                           },
                          test_name, common_name, 2, False))
                          
        test_name = 'CB_AP_Associate_Station_With_Wlans'
        common_name = '%sVerify the station associate to wlan: %s' % (testcase_name, info)
        test_cfgs.append(({'wlans_cfg_list': [wlan_cfg],
                           'ap_fw_upgrade_cfg': ap_fw_upgrade_cfg,
                           },
                          test_name, common_name, 2, False))
    
    return test_cfgs

def _define_wlan_cfg_list():
    encryp_cfg_list = []

    #Add wpa encryption settings.
    #For 2211, auth is only PSK, for 7211, can be PSK and 802.1x[EAP].
    auth_list = ['PSK'] #,'EAP']
    wpa_ver_list = ['WPA2'] #, 'WPA'] #, 'WPA-Auto']
    cipher_list = ['AES'] #, 'TKIP'] #, 'Auto']
    
    eap_cfg = {'ras_addr': '192.168.0.252',
               'ras_port': '1812',
               'ras_secret': '1234567890',
               'username': 'rad.eap.user',
               'password': 'rad.eap.user'}
    
    #for wpa_ver in wpa_ver_list:
    #   for cipher in cipher_list:
    for auth in auth_list:
        for i in range(0,1):
            wpa_ver = wpa_ver_list[i]
            cipher = cipher_list[i]
            encryp_cfg = dict(auth=auth,wpa_ver=wpa_ver,encryption=cipher,key_string='12345678')
            if auth == 'EAP':                
                encryp_cfg.update(eap_cfg)
            encryp_cfg_list.append(encryp_cfg)    
    
    #Home wlan: wlan_if = 'wlan0', name='home'
    wlan_name_list = ['svcp']  
    
    wlan_cfg_list = []
    for wlan_name in wlan_name_list:
        for cfg in encryp_cfg_list:
            wlan_cfg = {}
            wlan_cfg['wlan_name'] = wlan_name
            wlan_cfg.update(cfg)
            wlan_cfg_list.append(wlan_cfg)
            
    return wlan_cfg_list

def define_upgrade_cfg():
    ap_up_cfg = {'sta_ip_list': ['192.168.1.11'],
                 'target_ip_list': [#'192.168.0.2', 
                                    '192.168.0.10', 
                                    '192.168.0.253', 
                                    '192.168.0.252'],
                 'ap_common_conf': {'username': 'super',
                                    'password': 'sp-admin',
                                    'telnet': True,
                                    },
                 'build_server': 'k2.video54.local',
                 'up_cfg_common': {'server_root_path':'C:/rwqaauto/firmware',
                                   'server_ip':'192.168.0.10',
                                   'ftp_user_name':'cherry',
                                   'ftp_password':'123456',
                                   },
                 'up_cfg': {'ZF7372': {'target_build_stream': 'ZF7372_mainline',
                                       'target_bno': '6',
                                       'baseline_build_stream': 'ZF7372_mainline',
                                       'baseline_bno':'5',
                                       },
                            },
                 }
                
    return ap_up_cfg
    
def define_ap_model_ip_mapping():
    ap_cfg = {'ZF7372': ['192.168.0.200']}
    
    return ap_cfg

def define_test_parameters():
    default_upgrade_cfg = {'proto':'tftp',
                           'auto': False,
                           'firstcheck':'3',
                           'interval':'6',
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
           'test_type': 'cli',
           }
    
    return cfg    

def get_selected_input(depot = [], prompt = ""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select option: "

    selection = []
    id = raw_input(prompt)
    try:
        selection = depot[int(id)]
    except:
        selection = ""

    return selection    
    
def create_test_suite(**kwargs):
    #tb = testsuite.getTestbed(**kwargs)
    #tbcfg = testsuite.getTestbedConfig(tb)
    tcfg = define_test_parameters()
    
    ap_model_ips = define_ap_model_ip_mapping()    
    
    model_list = ap_model_ips.keys()
    model_name = get_selected_input(model_list, "Please select one model:")
    if not model_name:
        raise Exception("Please select one model for test suite.")
    
    repeat_times = raw_input("Pleae input repeat times:")
    if not repeat_times:
        repeat_times = 1
    
    ap_ip_list = ap_model_ips[model_name]
    
    tcfg['ap_ip_list'] = ap_ip_list
    tcfg['ap_model'] = model_name
    tcfg['ap_fw_upgrade_cfg'] = define_upgrade_cfg()
    tcfg['sleep_time_before_check_version'] = 30 #7*60 + 30
    tcfg['repeat_times'] = repeat_times
    
    model_up_cfg_list = tcfg['ap_fw_upgrade_cfg']['up_cfg'][model_name]
    
    if type(model_up_cfg_list) != list:
        model_up_cfg_list = [model_up_cfg_list]
        
    for i in range(0, int(repeat_times)):
        for model_up_cfg in model_up_cfg_list:
            target_build = "%s_%s" % (model_up_cfg['target_build_stream'], model_up_cfg['target_bno'])
            baseline_build = "%s_%s" % (model_up_cfg['baseline_build_stream'], model_up_cfg['baseline_bno'])                                   
                   
            ts_name = 'AP CLI - Manual repeat upgrade %s Baseline %s Target %s-%04d' % (model_name, baseline_build, target_build, random.randrange(1,9999))
            ts = testsuite.get_testsuite(ts_name, 'Verify AP manual upgrade via CLI', combotest=True)
            test_cfgs = define_test_cfg(tcfg, model_name, 8)
        
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
    