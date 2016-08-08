'''
Created on Dec 15, 2014

@author: chen.tao@odc-ruckuswireless.com
'''
import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def define_test_cfg():
    test_cfgs = []

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = 'Try to del all vlan pools.'
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

#############################################################################
 
    test_case_name = '[VLAN POOL Name max length 64]'
    num = 0
    idx = '1.%s'
   
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with name over 64 characters.'%(test_case_name + idx%(num))
    vlan_pool_cfg_max_len_name = {'name':'12345678901234567890123456789012345678901234567890123456789012345','vlan':'1,2'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_max_len_name,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))       

    test_case_name = '[VLAN POOL Name can contain special characters]'
    num = 0
    idx = '2.%s'
        
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with name using special characters.'%(test_case_name + idx%(num))
    vlan_pool_cfg_special_chars_name = {'name':"""~!@#$%^&*()_+-={}[]""",'vlan':'1,2'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_special_chars_name}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    test_case_name = '[VLAN POOL Name cannot contain angle brackets]'
    num = 0
    idx = '3.%s'
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with name using angle brackets should fail.'%(test_case_name + idx%(num))
    vlan_pool_cfg_angle_brackets_name = {'name':"<>",'vlan':'1,2'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_angle_brackets_name,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
 
#    num += 1    
#    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
#    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
#    test_params = {'del_all':True,}
#    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL Option min value]'
    num = 0
    idx = '4.%s'
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with option 0.'%(test_case_name + idx%(num))
    vlan_pool_cfg_option_0 = {'name':"vlan_pool_option_0",'vlan':'1,2','option':'0'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_option_0,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Option max value]'
    num = 0
    idx = '5.%s'
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with option 4.'%(test_case_name + idx%(num))
    vlan_pool_cfg_option_4 = {'name':"vlan_pool_option_4",'vlan':'1,2','option':'4'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_option_4,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

#    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
#    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
#    test_params = {'del_all':True,}
#    test_cfgs.append((test_params, test_name, common_name, 2, False))
#############################################################################
    
    test_case_name = '[VLAN POOL Vlan range min]'
    num = 0
    idx = '6.%s'
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan 0.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_0 = {'name':"vlan_pool_vlan_0",'vlan':'0'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_0,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan range max]'
    num = 0
    idx = '7.%s'
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan 4095.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_4095 = {'name':"vlan_pool_vlan_4095",'vlan':'4095'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_4095,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan number max]'
    num = 0
    idx = '8.%s'

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with 17 vlans.'%(test_case_name + idx%(num))
    vlan_pool_cfg_17_vlan = {'name':"vlan_pool_17_vlans",'vlan':'1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_17_vlan,'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan format 10-10]'
    num = 0
    idx = '9.%s'

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan format 10-10.'%(test_case_name + idx%(num))
    vlan_pool_cfg_10_10 = {'name':"vlan_pool_10-10",'vlan':'10-10'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_10_10}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan format 1,2,3,4]'
    num = 0
    idx = '10.%s'
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan format 1,2,3,4.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_1_2_3_4 = {'name':"vlan_pool_vlan_1_2_3_4",'vlan':'1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_1_2_3_4}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan format 4,3,2,1]'
    num = 0
    idx = '11.%s'
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan format 4,3,2,1.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_4_3_2_1 = {'name':"vlan_pool_vlan_4_3_2_1",'vlan':'16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_4_3_2_1}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan format 1-16]'
    num = 0
    idx = '12.%s'
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan format 1-16.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_1_16 = {'name':"vlan_pool_vlan_1-16",'vlan':'1-16'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_1_16}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan format 16-1]'
    num = 0
    idx = '13.%s'
    num += 1 
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with vlan format 16-1.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_16_1 = {'name':"vlan_pool_vlan_16-1",'vlan':'16-1'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_16_1}
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_case_name = '[VLAN POOL Vlan format mixed]'
    num = 0
    idx = '14.%s'
    num += 1 
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool with mixed vlan format.'%(test_case_name + idx%(num))
    vlan_pool_cfg_vlan_mixed = {'name':"vlan_pool_mixed_vlan",'vlan':'1,2,4-6,8,7,10,13-12,16,15'}
    test_params = {'vlan_pool_cfg':vlan_pool_cfg_vlan_mixed}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
#    num += 1    
#    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
#    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
#    test_params = {'del_all':True,}
#    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL Conflicts with Device Policy]'
    num = 0
    idx = '4.%s'
    num += 1
    
    dvcpcy_for_windows_os = {'name': 'Policy for Window OS', 'mode': 'deny', 
                             'rules': [{'name': '1', 'os_type': 'Windows', 'type': 'allow', 'vlan': '10', 
                                        'uplink': '10', 'downlink': '9'}]}    
    
    test_name = 'CB_ZD_CLI_Configure_Device_Policy'
    common_name = '%sAdd a device policy.'%(test_case_name + idx%(num))
    test_cfgs.append(({'device_policy_list': [dvcpcy_for_windows_os]}, test_name, common_name, 1, False))

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_device_policy",'vlan':'1,2'}}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    wlan_cfg = {'name': 'vlan_pool_test',
                'ssid': 'vlan_pool_test',
                'auth': 'open',
                'encryption': 'none',
            }
    test_wlan_cfg = wlan_cfg.copy()
    test_wlan_cfg.update({'dvcpcy_name': dvcpcy_for_windows_os['name'],
                          'vlanpool':'vlan_pool_device_policy',
                          })
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate WLAN with vlanpool and device policy' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg,'negative':True}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))

#############################################################################

    test_case_name = '[VLAN POOL Conflicts with Access Vlan]'
    num = 0
    idx = '5.%s'    

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_access_vlan",'vlan':'1,2'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 
    
    test_wlan_cfg1 = {'name': 'vlan_pool_access_vlan_test',
                      'ssid': 'vlan_pool_access_vlan_test',
                      'auth': 'open',
                      'encryption': 'none',
                      'vlanpool':'vlan_pool_access_vlan',
                      'dvlan':True,
                      'vlan_id':'100',
                      }    
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate WLAN with vlanpool and access vlan' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg1,'negative':True}, test_name, common_name, 2, False))

#    num += 1
#    test_name = 'CB_ZDCLI_Get_Wlan_By_SSID'
#    common_name = '%sGet WLAN info.' %(test_case_name + idx%(num))
#    test_cfgs.append(({'ssid': 'vlan_pool_access_vlan_test'}, test_name, common_name, 2, False))
#
#    num += 1
#    test_name = 'CB_ZDCLI_Verify_Wlan'
#    common_name = '%sVerify access vlan is not set successfully.' %(test_case_name + idx%(num))
#    test_cfgs.append(({'wlan_cfg': {'vlan_id':'100'}}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL Conflicts with WEP]'
    num = 0
    idx = '6.%s'   
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_wep",'vlan':'1,2'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    test_wlan_cfg2 = wlan_cfg.copy()
    test_wlan_cfg2.update({'vlanpool':'vlan_pool_wep',
                           'dvlan':True,
                           'encryption': 'WEP-64',
                           'key_index' : "1",
                           'key_string': 'A3718A9204'
                           })
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate WLAN with vlanpool and wep encryption' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg2,'negative':True}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL Conflicts with Autonomous WLAN]'
    num = 0
    idx = '7.%s'   

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_autonomous",'vlan':'1,2'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    test_wlan_cfg3 = wlan_cfg.copy()
    test_wlan_cfg3.update({'vlanpool':'vlan_pool_autonomous',
                           'dvlan':True,
                           'type':'autonomous'
                           })
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate an autonomous WLAN with vlanpool' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg2,'negative':True}, test_name, common_name, 2, False))


    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL enabled, dvlan must be enabled]'
    num = 0
    idx = '8.%s'    
  
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_with_dvlan",'vlan':'1,2'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    test_wlan_cfg3 = wlan_cfg.copy()
    test_wlan_cfg3.update({'vlanpool':'vlan_pool_with_dvlan',
                           'dvlan':False,
                           })
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a WLAN with vlanpool enabled and dvlan disabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg3,'negative':True}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL enabled, wlan group vlan not configurable]'
    num = 0
    idx = '9.%s'    
  
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_normal",'vlan':'1,2'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_All_WLAN_Groups'
    common_name = '%sRemove all WLAN groups from ZD CLI' %(test_case_name + idx%(num))  
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_wlan_cfg4 = wlan_cfg.copy()
    test_wlan_cfg4.update({'name':'vp_enabled_verify_group_vlan',
                           'ssid':'vp_enabled_verify_group_vlan',
                           'vlanpool':'vlan_pool_normal',
                           'dvlan':True,
                           })
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': test_wlan_cfg4}, test_name, common_name, 2, False)) 


    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete vlan pool should fail.'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_normal",'vlan':'1,2'},'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 2, True))

    wg_cfg_list = [{'wg_name': 'Default', 
                    'wlan_member': {
                                'vp_enabled_verify_group_vlan': {'vlan_override': 'tag', 'tag_override': '302'}
                                }
                }]

    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN_Groups'
    common_name = '%sConfigure WLAN groups in ZD CLI'%(test_case_name + idx%(num))
    test_cfgs.append(( {'wg_cfg_list':wg_cfg_list,'negative':True}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    num += 1    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
#############################################################################

    test_case_name = '[VLAN POOL MAX]'
    num = 0
    idx = '10.%s'

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 1, False))  
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pools'
    common_name = '%sTry to add max number of vlan pools.'%(test_case_name + idx%(num))
    test_params = {'specified_num':64,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd another vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_extra",'vlan':'1,2'},'negative':True}
    test_cfgs.append((test_params, test_name, common_name, 2, False))        
   
    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sTry to del all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))  

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs'
    test_cfgs.append(({}, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = 'Try to del all vlan pools after test.'
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    return test_cfgs
def make_test_suite(**kwargs):

    attrs = dict(interactive_mode = True,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)
        
    test_cfgs = define_test_cfg()
#----------------------------------------------------------------------------------------------------------
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "VLAN_POOL_Configurations" 
            
    ts = testsuite.get_testsuite(ts_name,'VLAN_POOL_Configurations',combotest=True)
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



