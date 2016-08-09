#encoding:utf-8

"""
@author: Calvin.ye - ye.songnan@odc-ruckuswireless.com
@since: May 2013

This testsuite is configure to allow testing follow test cases :
1.Get ap number connected to zd
2.Restore full cfg to zd 
3.Remember Process id (web/stamgr/apmgr/emfd)
4.Add 27 wlans in default wlan group
5.Continuously do the following operation(how many times to do controlled by parameter)
  5.1 Delete all wlans in wlan group
  5.2 Verify wlan group member
  5.3 Add all wlans back 
  5.4 Verify wlan group member
6.Randomly select 2 real aps to check the wlan deployment is correct(in ap cli)
7.Let sta associate the 27 wlans one by one, and ping. 
8.Compare process id(web/stamgr/apmgr/emfd)
9.Verify ap number
10.Restore ZD to empty cfg



Note:
Need at least two dual band ap.(In my script i used zf7363)

"""

import sys
import copy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []
    test_name = 'CB_ZD_Get_APs_Number'
    common_name = 'Get ap number connected with zd'
    test_params = {'timeout':cfg['timeout'], 'chk_gui':False}
    test_cfgs.append((test_params, test_name, common_name, 0, False))   
 
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore full configuration to ZD'
    test_params = {'restore_type':'restore_everything_except_ip','restore_file_path':cfg['full_cfg'], 'reboot_timeout':cfg['reboot_timeout']}
    test_cfgs.append((test_params,test_name, common_name, 0, False))
    
    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'PID(web/stamgr/apmgr) mark'
    test_cfgs.append(({},test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_CLI_Add_Remove_Wlan_From_Wlangroup'
    common_name = 'Continuously add and remove wlan from wlangroup'
    test_params = {'wlan_list':cfg['wlan_list'],'times':cfg['times']}
    test_cfgs.append((test_params,test_name, common_name, 0, False))

    test_name = 'CB_AP_CLI_Random_AP_Check_Wlan'
    common_name = 'Randomly select 3 aps to check the wlan deployment is correct'
    test_params = {'wlan_list':cfg['wlan_list']}
    test_cfgs.append((test_params,test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create the target station'
    test_params = {'sta_tag': 'sta1', 'sta_ip_addr': cfg['target_station']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_Station_Associate_Wlan_And_Ping'
    common_name = 'Let sta associate the 27 wlans one by one, and ping'
    test_params = {'wlan_list':cfg['wlan_list'], 'sta_tag':'sta1', 'ping_timeout_ms': 15 * 1000}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_Scaling_ZD_CLI_Process_Check'
    common_name = 'PID(web/stamgr/apmgr) compare'
    test_cfgs.append(({},test_name, common_name, 0, False))    
    
    test_name = 'CB_Scaling_Verify_APs_Num'
    common_name = 'Check all of APs are connected including RuckusAP and SIMAP' 
    test_params = {'timeout':cfg['timeout'], 'chk_gui':False}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Restore'
    common_name = 'Restore ZD to empty cfg'
    param_cfg = {'restore_type':'restore_everything_except_ip','restore_file_path':cfg['empty_cfg'], 'reboot_timeout':cfg['reboot_timeout']}
    test_cfgs.append((param_cfg,test_name, common_name, 0, False))

    return test_cfgs

def make_test_suite(**kwargs):

    ts_name = 'Add and remove wlans from default wlan group'
    ts = testsuite.get_testsuite(ts_name, 'Add and remove wlans from default wlan group', combotest=True)
 
#--------------------------------------------------------------------------------------------------------   
    prompt = '''
    Please Input the ZD mode index:
        1) ZD3000
        2) ZD5000 
    For example: 1-->ZD3000 and this is by default.
    '''
    model_index = int(raw_input(prompt))
    if model_index not in range(1, 3):
        model_index = 1  
        
    cfg = {
           1:'ZD3000',
           2:'ZD5000',
           }
    zd_type=cfg[model_index]
    print "ZD mode:%s" % zd_type 
    full_cfg='C:\\Documents and Settings\\lab\\My Documents\\Downloads\\full_cfg.bak'
    empty_cfg='C:\\Documents and Settings\\lab\\My Documents\\Downloads\\empty_cfg.bak'    
    if zd_type=='ZD5000':
        full_cfg='C:\\Documents and Settings\\lab\\My Documents\\Downloads\\full_cfg_5k.bak'
        empty_cfg='C:\\Documents and Settings\\lab\\My Documents\\Downloads\\empty_cfg_5k.bak'   
 
#----------------------------------------------------------------------------------------------------------  
    wlan_cfg = {
        'ssid': "WLAN-%d" ,
        'auth': "open", 
        'wpa_ver': "", 
        'encryption': "none",
        'key_index': "", 
        'key_string': "",
        'do_webauth': False, 
        }
        
    wlan_list=[]
    for i in range(3,30):
        wlan_cfg_2 = copy.deepcopy(wlan_cfg) 
        wlan_cfg_2['ssid']=wlan_cfg['ssid']%i
        wlan_list.append(wlan_cfg_2)
        
#---------------------------------------------------------------------------------------------------------- 
    times = 10
    prompt = '''
    Please input how many times do you want to repeat,default is 10:
    '''
    t1=raw_input(prompt)
    if t1:
        times = int(t1)

#---------------------------------------------------------------------------------------------------------- 
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg["ap_sym_dict"]
    
    cfg = {
           'full_cfg':full_cfg,
           'empty_cfg':empty_cfg,
           'wlan_list':wlan_list,
           'times':times,
           'timeout':120,
           'reboot_timeout':240,
           'zd_type':zd_type,
           'is_restart_adapter': True,
           'sta_tag': 'sta1',
           'ping_timeout_ms': 15 * 1000,
           'target_ip_list': ['192.168.0.252'],
           'target_station':sta_ip_list[0]
           }    
    
    test_cfgs = define_test_cfg(cfg)

#----------------------------------------------------------------------------------------------------------
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
    make_test_suite(**_dict)


