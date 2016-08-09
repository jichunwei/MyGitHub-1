'''
Description:
    Scaling basic testing.
    
update info:
    update_date:2010-8-30
    author_info:cwang@ruckuswireless.com
    
'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_configuration(cfg):
    test_cfgs = []

#    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
#    common_name = '[%s]:apmgr and stamgr daemon pid mark.'%pre_name
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    pre_name = 'check 500 aps all connect'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs are connected including RuckusAP and SIMAP' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    pre_name = 'restore to full CFG'    
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD to full configurations' %pre_name
    param_cfg = dict(restore_file_path = cfg['full_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
      
    pre_name = 'check 500 aps all connect after restore'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs after restoring' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
                
    #Verify DPSK from WEBUI    
    pre_name = 'verify Guess pass'
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '[%s]:Verify 9999 guest passes under zd webui after system restore'  %pre_name
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 1, False))
        
    
    #Verify DPSK from WEBUI
    pre_name = 'verify DPSK'
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '[%s]:Verify 5000 dpsk under zd webui after system restore' %pre_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))
        
    
    pre_name = 'verify ap total number from web UI'
    test_name = 'CB_Scaling_Check_APs_Basic_INFO'
    common_name = '[%s]:Check the total number is correct from Dashboard|Monitor|Configure tab' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
  
       
    pre_name = 'verify WLAN from zdcli' 
    test_name = 'CB_Scaling_Verify_AP_Side_WLANs_From_ZDCLI'
    common_name = '[%s]:Verify all of WLANs are deployed to APs correctly' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
            
    wlan_cfg_list = cfg['wlan_cfg_list']
    wlan_cfg_list.append(cfg['gp_wlan'])
    wlan_cfg_list.append(cfg['dpsk_wlan'])
    
    pre_name = 'verify L2 acl' 
    test_name = 'CB_ZD_Verify_L2_ACLs'
    common_name = '[%s]:Verify L2 ACLs via station with WLAN' %pre_name
    param_cfg = dict(target_station = cfg['target_station'],
                     ip = cfg['ip'],
                     wlan_cfg_list = wlan_cfg_list
                     )
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    
    pre_name = 'check 500 aps are all connected again'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Re-check all of APs are connected including RuckusAP and SIMAP' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
            
          
    pre_name = 'restore zd to empty cfg'  
    test_name = 'CB_ZD_Restore'
    common_name = '[%s]:Restore ZD to empty configurations' %pre_name
    param_cfg = dict(restore_file_path = cfg['empty_config_path'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    pre_name = 'verify aps all connect after restore empty CFG'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Re-check all of APs after restoring' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))   
    
#    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
#    common_name = '[%s]:apmgr and stamgr daemon pid checking.' %pre_name
#    param_cfg = dict()
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))     
        
    return test_cfgs

def create_test_parameters(tbcfg, attrs, cfg):
    sta_ip_list = tbcfg['sta_ip_list']    
       
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
#        active_ap_list = getActiveAp(ap_sym_dict)        
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
    cfg['target_station'] = target_sta
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
        
    else:
        ts_name = "Scaling - basic test"
    
    cfg['testsuite_name'] = ts_name
    
    cfg['ip'] = '192.168.0.252'
    cfg['num_of_acl_entries'] = 32
    
    #Check SIMAP timeout
    cfg['timeout'] = 1800 * 3

    default_wlan_conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
                         'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
                         'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
                         'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '',
                         'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    
    open_none = default_wlan_conf.copy()
    open_none.update({'ssid':'Open-None', 'auth':'open', 'encryption':'none'})
    set_of_30_open_none_wlans = []
    for idx in range(0, 30):
        wlan = open_none.copy()
        wlan['ssid'] = 'Rat-%s-wlan%2d' % (wlan['ssid'], idx + 1)
        set_of_30_open_none_wlans.append(wlan)
    cfg['wlan_cfg_list'] = set_of_30_open_none_wlans   
    
    
    cfg['gp_wlan'] = {'ssid': 'wlan-guestpass',
                      'type': 'guest', 
                      'auth': 'open',
                      'encryption' : 'none',                
                      }
    
    cfg['dpsk_wlan'] = {'ssid': 'wlan-dpsk',
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

#    import os
#    file = os.path.join(os.path.expanduser('~'), r"Desktop\full_cfg.bak")
#    cfg['full_config_path'] = file
#    file = os.path.join(os.path.expanduser('~'), r"Desktop\empty_cfg.bak")
#    cfg['empty_config_path'] = file    
            
#    cfg['full_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\full_cfg.bak'
#    cfg['empty_config_path'] = 'C:\\Documents and Settings\\lab\\Desktop\\empty_cfg.bak'

    import os
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\full_cfg.bak" )    
    cfg['full_config_path'] = file
    file = os.path.join(os.path.expanduser('~'), r"My Documents\Downloads\empty_cfg.bak" )    
    cfg['empty_config_path'] = file  
        

def create_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    cfg = {}
        
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    
    create_test_parameters(tbcfg, attrs, cfg)
    ts_name = '500 APs Support - Basic Function'
    ts = testsuite.get_testsuite(ts_name, '500 APs Support - Basic Function', combotest=True)
    test_cfgs = define_test_configuration(cfg)

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
    create_test_suite(**_dict)
    