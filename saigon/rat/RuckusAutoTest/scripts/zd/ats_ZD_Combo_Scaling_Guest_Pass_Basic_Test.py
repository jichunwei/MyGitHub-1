'''
Created on 2010-6-11

@author: cwang@ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    waiting_time=2 #hours
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'apmgr and stamgr daemon pid mark.'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    pre_name = 'make sure aps are all connected at the begining'
    test_name = 'CB_Scaling_Verify_APs'
    common_name = '[%s]:Check all of APs are connected including RuckusAP and SIMAP' %pre_name
    param_cfg = dict(timeout = cfg['timeout'], chk_gui=False)
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    #remove dpsk from webui
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = 'Clean all guest passes under zd webui'
    test_cfgs.append(( {}, test_name, common_name, 0, False))
    
    #create guest pass wlan
    pre_name = 'creat Wlan'
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '[%s]:Create guest pass wlan' %pre_name
    test_cfgs.append(({'wlan_cfg_list':cfg['wlan_cfg_list'], }, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = 'Remove all users from ZD WebUI'
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
        
    #create guest pass wlan
    pre_name = 'creat user'
    test_name = 'CB_ZD_Create_Local_User'
    common_name = '[%s]:Create local user' %pre_name
    
    test_cfgs.append(({'username':'rat_guest_pass', 'password':'rat_guest_pass'}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Verify_Local_User'
    common_name = '[%s]:Verify local user' %pre_name    
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    
    #Create multiple guest passes
    pre_name = 'creat guest pass'
    test_name = 'CB_ZD_Create_Multi_Guest_Passes'
    common_name = '[%s]:Create 9900 guest passes' %pre_name
    test_cfgs.append(( {'number_profile': '100',
                        'repeat_cnt': 100, 
                        'duration': '1',
                        'duration_unit':r'Hours', 
                        'username':r'rat_guest_pass',
                        'password':r'rat_guest_pass'                                                           
                        }, test_name, common_name, 0, False))
    

    test_name = 'CB_ZD_Create_Multi_Guest_Passes'
    common_name = '[%s]:Create 99 guest passes' %pre_name
    test_cfgs.append(( {'number_profile': '99',
                        'repeat_cnt': 1, 
                        'duration': '1',
                        'duration_unit':r'Hours', 
                        'username':r'rat_guest_pass',
                        'password':r'rat_guest_pass'                                                           
                        }, test_name, common_name, 0, False))

    
    test_name = 'CB_ZD_Creat_Guest_Pass_Let_The_Guest_Pass_Number_In_ZD_Reach_To_Targrt_Number'
    common_name = '[%s]let guest pass number reach 9999' %pre_name   
    test_cfgs.append(( {"total_nums":9999,}, test_name, common_name, 0, False))
        
    #verify DPSK from WEBUI    
    test_name = 'CB_ZD_Verify_Multi_Guest_Passes'
    common_name = '[%s]Verify 9999 guest passes under ZD WEBUI'%pre_name    
    test_cfgs.append(( {'total_nums':'9999'}, test_name, common_name, 0, False))

    pre_name = 'download guest pass record'
    test_name = 'CB_ZD_Download_GuestPasses_Record'
    common_name = '[%s]:Download guest pass records.' %pre_name
    test_cfgs.append(({'username':'rat_guest_pass', 'password':'rat_guest_pass'}, test_name, common_name, 1, False))
    

    pre_name = 'parse guest pass record file'
    test_name = 'CB_ZD_Parse_Guest_Passes_Record_File'
    common_name = '[%s]:Parse guest pass records.' %pre_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
        

    pre_name = 'Guest Pass validation'
    test_name = 'CB_ZD_Find_Station'
    common_name = '[%s]:ZD1 Find an active station.' %pre_name
    param_cfg = dict(target_station = cfg['target_sta'])
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))    
    
    test_name = 'CB_Scaling_Verify_Guest_Pass_Auth'
    common_name = '[%s]:Do Guest Pass validation.' %pre_name
    test_cfgs.append(({'wlan_cfg':cfg['wlan_cfg_list'][0]}, test_name, common_name, 1, False))
    
    
    pre_name = 'Guest Pass expire test'
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting for %d hours so that all of GuestPasses are expired.' %(pre_name,waiting_time)
    test_cfgs.append(({'timeout':waiting_time*60*60}, test_name, common_name, 0, False))
        
    
    #verify guest pass from webui    
    test_name = 'CB_Scaling_Verify_Guest_Passes_Empty'
    common_name = '[%s]:Make sure all guest passes are expired' %pre_name
    test_cfgs.append(( {}, test_name, common_name, 1, False))    
    
    #remove Guestpass from webui
    pre_name = 'remove guest pass,user,Wlan'
    test_name = 'CB_ZD_Remove_All_Guest_Passes'
    common_name = '[%s]:Remove all guest passes under zd webui' %pre_name
    test_cfgs.append(( {}, test_name, common_name, 1, True))
    
    test_name = 'CB_ZD_Remove_Local_User'
    common_name = '[%s]:Remove local user' %pre_name
    test_cfgs.append(({}, test_name, common_name, 1, True))
    
    #remove guest pass wlan
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '[%s]:Remove all of wlans' %pre_name
    test_cfgs.append(({}, test_name, common_name, 1, True))
    
    pre_name = 'ps id check'
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = '[%s]:apmgr and stamgr daemon pid checking.' %pre_name
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))     
        
    
    return test_cfgs     

def define_test_params(tbcfg, attrs):
    cfg = dict()
    wlan_cfg_list = []
    guest_wlan = {'ssid': 'wlan-guestpass',
                 'type': 'guest', 
                 'auth': 'open',
                 'encryption' : 'none',                
                }
    wlan_cfg_list.append(guest_wlan)
    cfg['wlan_cfg_list'] = wlan_cfg_list
    cfg['timeout'] = 1800 * 3
    
    #Get station CFG.
    sta_ip_list = tbcfg['sta_ip_list']    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)    
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
        
    cfg['target_sta'] = target_sta
        
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
    
        
    ts_name = '10000 Guest Pass Generation.'
    ts = testsuite.get_testsuite(ts_name,
                                'To verify 10000 guest pass can be generated successfully and perform correctly under the following circumstances.',
                                combotest=True)
    cfg = define_test_params(tbcfg, attrs)
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