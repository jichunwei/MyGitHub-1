'''
Created on 2010-9-28
@author: cwang@ruckuswireless.com

Update @2011-9-8, by cwang@ruckuswireless.com
Update Content:
    Add TCID for report to testlink.

This test suite is used for setting scaling ENV.
  1)Create 5000 DPSKs 
  2)Create 10000 GuestPasses + Users entities.
  3)32 WLAN Groups
  4)Fully l2 + l3 ACLs
  5)Backup this configurations
'''
import sys
import random

import libZD_TestSuite as testsuite

from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []
    #Clean up all of configurations.
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_Scaling_RemoveZDAllConfig'
    common_name = 'Remove all configuration.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Backup_Config'
    common_name = 'Backup a empty configuration' 
    param_cfg = dict(filename = 'empty_cfg.bak')   
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))    
        
        
    
#    test_name = 'CB_ZD_Create_Wlan_Groups'
#    common_name = 'Create fully wlan groups'    
#    param_cfg = dict(num_of_wgs = 32)    
#    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

    #change to CLI mode.
    wgs_list = []
    for i in range(1, 33):
        wgs_list.append({'wg_name': 'WLAN-GROUP-%d' % i,     
                         'description': 'WLAN-GROUP-%d' % i,
                         'wlan_member': None})

    test_name = 'CB_ZD_CLI_Configure_WLAN_Groups'
    common_name = '[Create Maximum WLAN Groups]Create fully wlan groups'    
    param_cfg = dict(wg_cfg_list = wgs_list)    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_Create_Wlans'
    common_name = '[Create Maximum WLANs]Create 32 WLANs from ZD WebUI'
    param_cfg = dict(wlan_cfg_list=cfg['wlan_cfg_list'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    
    #Create guest pass WLAN
    test_name = 'CB_ZD_Create_Local_User'
    common_name = 'Create local user'
    
    test_cfgs.append(({'username':'rat_guest_pass', 'password':'rat_guest_pass'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Local_User'
    common_name = 'Verify local user'
    
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    #Create multiple DPSK
    test_name = 'CB_ZD_Create_Multi_Guest_Passes'
    common_name = '[Create Maximum Guest Passes + User]Create 9900 guest passes'    
    test_cfgs.append(( {'number_profile': '100',  
                        'duration': '999',                      
                        'repeat_cnt': 99,                                        
                        }, test_name, common_name, 0, False))


    test_name = 'CB_ZD_Create_Multi_Guest_Passes'
    common_name = '[Create Maximum Guest Passes + User]Create 99 guest passes'    
    test_cfgs.append(( {'number_profile': '99',
                        'duration': '999',                        
                        'repeat_cnt': 1,                                        
                        }, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Creat_Guest_Pass_Let_The_Guest_Pass_Number_In_ZD_Reach_To_Targrt_Number'
    common_name = '[Create Maximum Guest Passes + User]let guest pass number reach 9999'    
    test_cfgs.append(( {"total_nums":9999,}, test_name, common_name, 0, False))
        
    #verify DPSK from WEBUI    
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '[Create Maximum Guest Passes + User]Verify 9999 guest passes under ZD WEBUI'    
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 0, False))
    


    #Create multiple DPSK
    test_name = 'CB_ZD_Create_Multi_DPSK'
    common_name = '[Create Maximum DPSK]Create 5000 DPSK'    
    test_cfgs.append(( {'number_of_dpsk': 100,
                        'repeat_cnt': 50,                
                        'psk_expiration': 'Unlimited',
                        'expected_response_time': 30,
                        'wlan_cfg':cfg['dpsk_wlan']}, test_name, common_name, 0, False))
    
    #Verify DPSK from WEBUI    
    test_name = 'CB_ZD_Verify_Multi_DPSK'
    common_name = '[Create Maximum DPSK]Verify 5000 DPSK under ZD WEBUI'    
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
        
    #change to CLI mode so that speed up.
#    test_name = 'CB_ZD_Create_L2_ACLs'
#    common_name = 'Create L2 ACLs from ZD WebUI.'
    test_name = 'CB_Scaling_ZD_CLI_Create_L2_ACLs'
    common_name = '[Create Maximum L2 ACLs]Create L2 ACLs from ZDCLI'
    param_cfg = dict(num_of_acl = cfg['num_of_acl_entries'], target_station = cfg['target_station'])
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    
    #change to CLI mode so that speed up.
    #test_name = 'CB_ZD_Create_L3_ACLs'
    #common_name = 'Create 2 L3 ACLs: "Allow All" and "Deny All"'
    test_name = 'CB_ZD_CLI_Create_L3_ACLs'
    common_name = '[Create Maximum L3 ACLs]Create L3 ACLs configuration from ZDCLI'
    param_cfg = dict(l3acl_conf_list=get_l3acl_conf_list())
#    test_cfgs.append(({'l3_acl_cfgs': cfg['l3_acl_cfgs']},
#                      test_name, common_name, 0, False))    
    
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_Scaling_Backup_Config'
    common_name = 'Backup a full configurations' 
    param_cfg = dict(filename = 'full_cfg.bak')   
    test_cfgs.append(( param_cfg, test_name, common_name, 0, False))
        

    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid checking.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    return test_cfgs    


def get_l3acl_conf_list(num_of_acl=32, rule_cnt=29):
    l3acl_conf_list = []
    r_cfg = dict(
                rule_order = 3,
                rule_description =utils.make_random_string(random.randint(2,32),type = 'alnum'),
                rule_type = 'allow',
                rule_destination_addr =random.choice(['1.1.1.1/24','Any']),
                rule_destination_port =random.choice([random.randint(1,65534),'Any']),
                rule_protocol = random.choice([random.randint(0,254),'Any'])
                )
    rule_list = []
    
    for i in range(3, rule_cnt + 3):
        r_cfg_tmp = r_cfg.copy()
        r_cfg_tmp['rule_order'] = i
        rule_list.append(r_cfg_tmp)    
                       
    for i in range(num_of_acl):
        acl_name = 'Test_ACLs_%d' % i                            
        l3acl_conf_list.append(dict(
                                    acl_name = acl_name,
                                    description = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                    policy = 'allow',
                                    rule_conf_list = rule_list,
                                    ))
        
    return l3acl_conf_list  


def define_test_params(tbcfg, attrs):
    cfg = dict()
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
    
    args = dict(num_of_acls = 32,
                num_of_rules = 29,)
    r_cfg = dict(order = '1',
                  description = None,
                  action = '',
                  dst_addr = None,
                  application = None,
                  protocol = None,
                  dst_port = None
                  )        
    acl_cnt = args['num_of_acls']
    rule_cnt = args['num_of_rules']
    acl_list = []
    rule_list = []
    for i in range(3, rule_cnt + 3):
        r_cfg_tmp = r_cfg.copy()
        r_cfg_tmp['order'] = '%d' % i
        rule_list.append(r_cfg_tmp)
        
    acl_cfg = {'name':'L3 ACL ALLOW ALL', 'description': '','default_mode': 'allow-all', 'rules': rule_list}
    for i in range(1, acl_cnt + 1):
        acl_cfg_tmp = acl_cfg.copy()
        acl_cfg_tmp['name'] = 'Test_ACLs_%d' % i
        acl_list.append(acl_cfg_tmp)    
        
    cfg['l3_acl_cfgs'] = acl_list
    
    
    default_wlan_conf = {'ssid': None, 'description': None, 'auth': '', 'wpa_ver': '', 'encryption': '', 'type': 'standard',
                         'hotspot_profile': '', 'key_string': '', 'key_index': '', 'auth_svr': '',
                         'do_webauth': None, 'do_isolation': None, 'do_zero_it': None, 'do_dynamic_psk': None,
                         'acl_name': '', 'l3_l4_acl_name': '', 'uplink_rate_limit': '', 'downlink_rate_limit': '',
                         'vlan_id': None, 'do_hide_ssid': None, 'do_tunnel': None, 'acct_svr': '', 'interim_update': None}
    
    open_none = default_wlan_conf.copy()
    open_none.update({'ssid':'Open-None', 'auth':'open', 'encryption':'none'})
    set_of_32_open_none_wlans = []
    for idx in range(0, 30):
        wlan = open_none.copy()
        wlan['ssid'] = 'Rat-%s-wlan%2d' % (wlan['ssid'], idx + 1)
        set_of_32_open_none_wlans.append(wlan)
      
    
    
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
        
    set_of_32_open_none_wlans.insert(0, cfg['gp_wlan'])
    set_of_32_open_none_wlans.insert(0, cfg['dpsk_wlan'])
     
    cfg['wlan_cfg_list'] = set_of_32_open_none_wlans
        
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
    
    cfg = define_test_params(tbcfg, attrs)
    
    ts_name = 'Prepare for Scaling or Scaling + SmartRedundancy(new)'
    ts = testsuite.get_testsuite(ts_name, 'Prepare for Scaling or Scaling + SmartRedundancy(new)', combotest=True)
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
    createTestSuite(**_dict)