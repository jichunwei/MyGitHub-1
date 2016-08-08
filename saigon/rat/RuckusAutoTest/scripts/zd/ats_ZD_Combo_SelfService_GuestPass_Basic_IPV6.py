"""
Verify self-service guest pass basic function under ipv6 only.

    Pre-condition:
       AP joins ZD
    Test Data:
        
    expect result: All steps should result properly.
    
    How to:
    
        1) Disable all wlan service
        2) Enable active ap wlan service
        3) Case1:[ap reboot]
        4) Enable all ap wlan service
    ps: This ats needs zd,ap,sta support ipv6
    
Created on 2015-2-9
@author: Yu.yanan@odc-ruckuswireless.com
"""

import sys
from random import randint
import libZD_TestSuite_IPV6 as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as CONST

def define_test_cfg(cfg):
 
    test_cfgs = [] 
    idx = 0
    
    active_ap_tag = cfg['active_ap_tag']
    
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all the WLANs from ZDCLI'
    test_cfgs.append(({}, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_sta_1'],'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station'
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Remove all GuestService from ZDCLI'
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active %s' % active_ap_tag 
    test_cfgs.append(({'active_ap': active_ap_tag,'ap_tag': active_ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Disable All WLAN Service'
    test_cfgs.append(({'cfg_type': 'init'}, test_name, common_name, 0, False))
     
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable Active AP WLAN Service'
    test_cfgs.append(({'ap_tag': active_ap_tag, 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True, 'radio': cfg['active_radio']}}, test_name, common_name, 0, False))
 

    #****************************************case (1) ap reboot ***************************************************
    idx +=1
    step = 0
    tc_common_name = "ap reboot"
    
    test_name = 'CB_ZD_CLI_Create_Wlan' 
    step += 1
    common_name = '[%s]%s.%s create guest wlan with self service' % (tc_common_name,idx, step)
    test_cfgs.append(({'wlan_conf':cfg['guest_wlan_cfg']}, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_Get_Wifi_Addr_Verify_Expect_Subnet_IPV6'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'ip_version': 'ipv6', 'expected_subnet_ipv6': '2020:db8:1::151/64',}, test_name, common_name, 2, False))
        
    
    test_name = 'CB_Station_SelfService_Generate_Guestpass_On_Web'
    step += 1
    common_name = '[%s]%s.%s sta generate key with name and default mobile' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'target_url': CONST.TARGET_IPV6_URL}, test_name, common_name, 2, False))
    
    
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform authorize with key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1', 'target_url': CONST.TARGET_IPV6_URL} , test_name, common_name, 2, False))
      
 
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg': cfg['guest_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': CONST.TARGET_IPV6, 'condition': 'allowed'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Reboot_AP'
    step += 1
    common_name = '[%s]%s.%s reboot active ap via CLI' % (tc_common_name,idx, step)
    test_cfgs.append(({'ap_tag': active_ap_tag, 'reboot': 'by ap'}, test_name, common_name, 2, False))
 
 
    test_name = 'CB_ZD_Associate_Station_1'
    step += 1
    common_name = '[%s]%s.%s Associate client to WLAN' % (tc_common_name,idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','wlan_cfg': cfg['guest_wlan_cfg']}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Get_Wifi_Addr_Verify_Expect_Subnet_IPV6'
    step += 1
    common_name = '[%s]%s.%s get client wifi address' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1', 'ip_version': 'ipv6', 'expected_subnet_ipv6': '2020:db8:1::151/64',}, test_name, common_name, 2, False))
   
    test_name = 'CB_Station_CaptivePortal_Perform_SelfService_GuestAuth'
    step += 1
    common_name = '[%s]%s.%s sta perform authorize with key' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag':'sta_1', 'target_url': CONST.TARGET_IPV6_URL} , test_name, common_name, 2, False))
      
 
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    step += 1
    common_name = '[%s]%s.%s verify client status on zd' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','use_guestpass_auth':True,'guest_name':'test.user','wlan_cfg':  cfg['guest_wlan_cfg'],'status': 'Authorized'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Client_Ping_Dest'
    step += 1
    common_name = '[%s]%s.%s verify client can ping target ip' % (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1','target': CONST.TARGET_IPV6, 'condition': 'allowed'}, test_name, common_name, 2, False))

 
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove the WLANs from ZDCLI'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Remove_All_SelfService_Guest_Passes'
    step += 1
    common_name = '[%s]%s.%s Remove all Generated Guest Passes from ZD'% (tc_common_name, idx, step)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    
    test_name = 'CB_Station_Remove_All_Wlans'
    step += 1
    common_name = '[%s]%s.%s Remove all WlANs from station'% (tc_common_name, idx, step)
    test_cfgs.append(({'sta_tag': 'sta_1'}, test_name, common_name, 2, True))
    
             
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = 'Remove GuestService from ZDCLI'
    test_cfgs.append(({'cleanup':True}, test_name, common_name, 0, False))
    
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Enable All WLAN Service'
    test_cfgs.append(({'cfg_type': 'teardown'}, test_name, common_name, 0, False))
    
    
    return test_cfgs


def gen_random_int():
    return randint(1,10000)
    
    
def define_test_parameters(tbcfg):

    random_num = gen_random_int()
    guest_wlan_name = 'guest_wlan'+str(random_num)
    
    guest_access_conf = {'terms_of_use': 'Disabled',
                         'self_service_registration':{
                                                      'status':'Enabled',
                                                      'duration':'1 days',
                                                      'share_number':'1',
                                                      'notification_method':'Device Screen',  
                                                      'sponsor_approval':{'status':'Disabled'},}                  
                         }
    
    
    guest_wlan_cfg = { "name" :guest_wlan_name,
                       'ssid': guest_wlan_name,
                       'auth': 'open',
                       'encryption' : 'none',     
                       'type':'guest-access',
                       'guest_access_service':guest_access_conf,}
    
  
    tcfg = {'guest_access_conf':guest_access_conf,
            'guest_wlan_cfg':guest_wlan_cfg,
            }
    
    return tcfg
    
def _select_ap(ap_sym_dict):
    select_tips = """This suite only need one AP, Enter symbolic AP from above list: """ 
    while (True):
        testsuite.show_ap_sym_list(ap_sym_dict)
        active_ap = raw_input(select_tips)
        
        if active_ap:
            return active_ap
        
    
def create_test_suite(**kwargs):
    ts_cfg = dict(interactive_mode = True,
                  station=(0, "g"),
                 )
    
    tb = testsuite.get_test_bed(**kwargs)
    tbcfg = testsuite.get_testbed_config(tb)
    
    ap_sym_dict = tbcfg['ap_sym_dict'] 
    sta_ip_list = tbcfg['sta_ip_list']  
    
    if ts_cfg["interactive_mode"]:
        target_sta_1 = testsuite.get_target_station(sta_ip_list, "Pick a wireless station: ")
        if len(sta_ip_list)< 1:
            print "Sorry,this ats needs 1 station at least.please check your testbed"
            return
        active_radio = testsuite.get_target_sta_radio()
    else:
        target_sta_1 = sta_ip_list[ts_cfg["station"][0]]
        active_radio = 'na'
       

    all_ap_tag_list = []
    for ap_tag in ap_sym_dict:
        all_ap_tag_list.append(ap_tag)
    
    if ts_cfg["interactive_mode"]:
        active_ap_tag = _select_ap(ap_sym_dict)
    
    all_ap_tag_list.remove(active_ap_tag)
 
    tcfg = {'target_sta_1':target_sta_1,  
            'active_radio':active_radio,
            'ap_tag_list':all_ap_tag_list,
            'active_ap_tag':active_ap_tag,
            }
    
    ts_name = 'Selfservice Guest Pass Basic Function under Ipv6'
    ts = testsuite.get_testsuite(ts_name, 'Verify Selfservice Guest Pass Basic Function under Ipv6', combotest=True)
    
    dcfg = define_test_parameters(tbcfg)
    tcfg.update(dcfg)
    
    test_cfgs = define_test_cfg(tcfg)
    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.add_test_case(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
            test_order += 1
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)