'''
Created on 2010-6-10

@author: cwang@ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    pre_name = 'verify AP Num at the begining'
        
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs are connected including RuckusAP and SIMAP' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    pre_name = 'restore to full CFG'
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD to full configurations' %pre_name
    param_cfg = dict(restore_file_path = cfg['full_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    pre_name = 'remember process ID'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid mark.' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
   
#    
#    #remove dpsk from webui    
#    test_name = 'CB_ZD_Remove_All_DPSK'
#    common_name = 'Clean all dpsk under zd webui'    
#    test_cfgs.append(( {}, test_name, common_name, 0, False))
#   
#    
#    #create dpsk wlan
#    test_name = 'CB_ZD_Create_Wlan'
#    common_name = 'Create dpsk wlan'    
#    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list'], }, test_name, common_name, 0, False))    
#   
#        
#    #create multiple dpsk
#    test_name = 'CB_ZD_Create_Multi_DPSK'
#    common_name = 'Create 5000 dpsk'    
#    test_cfgs.append(( {'number_of_dpsk': 100,
#                        'repeat_cnt': 50,                
#                        'psk_expiration': 'Unlimited',
#                        'expected_response_time': 30,}, test_name, common_name, 0, False))
#    
#    
    #Verify DPSK from WEBUI
    pre_name = 'verify DPSK'
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '[%s]:Verify 5000 dpsk under zd webui after system restore' %pre_name
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    pre_name = 'Station associate with dpsk WLAN'
    test_name = 'CB_ZD_Find_Station'
    common_name = '[%s]:Find an active station' %pre_name
    param_cfg = dict(target_station = cfg['target_sta'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Remove_Wlan_From_Station'
    common_name = '[%s]:Remove WLANs from station for guest access testing' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Associate_Station'
    common_name = '[%s]:Associate station to ssid dpsk-wlan' %pre_name
    param_cfg = dict(wlan_cfg = cfg['wlan_cfg_list'][0])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
#    #remove dpsk from webui
#    test_name = 'CB_ZD_Remove_All_DPSK'
#    common_name = 'Remove all dpsk under zd webui'    
#    test_cfgs.append(( {}, test_name, common_name, 0, True))
#    
#    #remove guest pass wlan
#    test_name = 'CB_ZD_Remove_All_Wlans'
#    common_name = 'Remove all of wlans'
#    
#    test_cfgs.append(({}, test_name, common_name, 0, True))    
    
    pre_name = 'check process ID after operation'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid checking.' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    

    pre_name = 'restore ZD to empty CFG'
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD to empty configurations' %pre_name
    param_cfg = dict(restore_file_path = cfg['empty_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    return test_cfgs 
        

def define_test_params(tbcfg):
    cfg = dict()
    wlan_cfg_list = []
    dpsk_wlan = {
                'ssid': 'wlan-dpsk',
                'auth': 'PSK',
                'wpa_ver': 'WPA',
                'encryption': 'AES',
                'type': 'standard',
                'key_string': '1234567890',
                'key_index': '',
                'auth_svr': '',
                'do_zero_it': True,
                'do_dynamic_psk': True,                 
                }
    wlan_cfg_list.append(dpsk_wlan)
    cfg['wlan_cfg_list'] = wlan_cfg_list
    cfg['timeout'] = 1800 * 3
#    cfg['full_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\full_cfg.bak'
#    cfg['empty_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\empty_cfg.bak'
    import os
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\full_cfg.bak" )    
    cfg['full_config_path'] = file
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\empty_cfg.bak" )    
    cfg['empty_config_path'] = file          
    return cfg
            

def createTestSuite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']   
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)     
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        
    cfg = define_test_params(tbcfg)
    cfg['target_sta'] = target_sta
        
    ts_name = '5000 Dynamic PSK Generation'
    ts = testsuite.get_testsuite(ts_name, 'To verify 5000Dynamic PSKs can be generated successfully and perform correctly under the following circumstances', combotest=True)    
    test_cfgs = define_test_cfg(cfg)
    
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
    _dict['tbtype'] = 'ZD_Scaling'
    createTestSuite(**_dict)