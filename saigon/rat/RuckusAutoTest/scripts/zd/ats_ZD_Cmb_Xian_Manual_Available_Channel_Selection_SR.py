'''
By West
verify when SR enabled,channel can deploy to ap correctly after failover or active zd switch port disable
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_configuration(tcfg):
    test_cfgs = []    
    
    ap_tag = tcfg['active_ap']
    country_para = tcfg['country_para']
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = 'both ZD enable SR and ready to do test'
    test_cfgs.append(({},test_name,common_name,0,False))
    
    test_name = 'CB_ZD_Set_Country_Code'
    common_name = 'set country code to %s'%country_para['name']
    param_cfg = {'country_code':country_para['name'],'allow_indoor_channel':True}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Set_AP_Channel_Range'
    common_name = 'set ap channel range'
    param_cfg = {'ng_channel_idx_list':country_para['ng_channel_idx_list'],'na_channel_idx_list':country_para['na_channel_idx_list'],'ap_tag':ap_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Verify_AP_Channel_Deploy'
    common_name = 'verify the channel range in ap'
    param_cfg = {'ng_channel_list':country_para['ng_channels'],'na_channel_list':country_para['na_channels'],'ap_tag':ap_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_case_name = '[Failover]'
    test_name = 'CB_ZD_SR_Failover'
    common_name = '%sFailover active ZD' % (test_case_name)
    param_cfg = dict()
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting ap connect to new active zd %s seconds ' % (test_case_name,tcfg['waiting_time'])
    test_cfgs.append(({'timeout':tcfg['waiting_time']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Channel_Deploy'
    common_name = '%sverify the channel range in ap'%test_case_name
    param_cfg = {'ng_channel_list':country_para['ng_channels'],'na_channel_list':country_para['na_channels'],'ap_tag':ap_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_case_name = '[Disable Active ZD Switch Port]'
    test_name = 'CB_ZD_SR_Get_Lower_Mac_ZD' 
    common_name = '%sGet Lower Mac ZD' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False))
        
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '%sDisable switch port connected standby zd' % test_case_name
    test_cfgs.append(({'zd':'active_zd_mac','device':'zd'},test_name, common_name, 2, False))   
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '%sWaiting ap connect to new active zd %s seconds ' % (test_case_name,tcfg['waiting_time'])
    test_cfgs.append(({'timeout':tcfg['waiting_time']}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Channel_Deploy'
    common_name = '%sverify the channel range in ap'%test_case_name
    param_cfg = {'ng_channel_list':country_para['ng_channels'],'na_channel_list':country_para['na_channels'],'ap_tag':ap_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%s Enable sw port connected to all zds' % test_case_name
    test_cfgs.append(({'device':'zd'},test_name, common_name, 2, True)) 
    
    test_name = 'CB_ZD_SR_Get_Active_ZD'
    common_name = '%sGet the Active ZD' % test_case_name
    test_cfgs.append(({},test_name,common_name,2,True))
    
    test_name = 'CB_ZD_Clear_Env_For_Manual_Available_Channel_Selection_test'
    common_name = 'clear AP %s ap group override' % ap_tag
    test_cfgs.append(({'ap_tag_list':[ap_tag]},test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD after test'
    test_cfgs.append(({},test_name, common_name, 0, True))
    
    return test_cfgs
    

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    ap_sym_dict = tb_cfg['ap_sym_dict']
    
    if attrs["interactive_mode"]:
        testsuite.showApSymList(ap_sym_dict)
        active_ap = raw_input("Choose an active AP: ")
        if active_ap not in ap_sym_dict:
            print "AP[%s] doesn't exist." % active_ap
            
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="Manual Available Channel Selection SR"
    
    country_para={'name':'United States',
                  'na_channels':[36,40,44,48],
                  'ng_channels':[1,2,3,4],
                  'na_channel_idx_list':[1,2,3,4],
                  'ng_channel_idx_list':[1,2,3,4],
                  }

    
    tcfg = dict(active_ap = active_ap,
                country_para = country_para,
                waiting_time = 2*60
                )
    test_cfgs = define_test_configuration(tcfg)
    ts = testsuite.get_testsuite(ts_name, "Manual Available Channel Selection SR", interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
