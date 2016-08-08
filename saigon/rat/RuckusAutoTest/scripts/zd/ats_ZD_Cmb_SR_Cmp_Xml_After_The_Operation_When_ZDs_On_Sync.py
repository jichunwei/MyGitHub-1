'''
create @2011/12/05, by west.li@ruckuswireless.com
compare xml file after the operation when zds on sync
'''

import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def defineTestConfiguration(active_ap_list):
    
    test_cfgs = [] 
    data_sync_time=2 #minutes
    cmd_prompt_wait=30 #seconds
    dual_stak_ip_cfg = {'ip_version': const.DUAL_STACK,
                        const.IPV4: {'ip_alloc': 'dhcp',},
                        const.IPV6: {'ipv6_alloc': 'auto',},
                        'vlan': '',
                        }
####################################################
#Case 1: on sync, add xml files by add configuration
#after the operation of add configuration,cmp files
####################################################
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Get_Lower_Mac_ZD' 
    common_name = 'Get Lower Mac ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = 'lower mac ZD set Factory'
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'lower_mac_zd'},test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = 'Set lower mac ZD device IP settings via GUI'
    param_cfg = {'zd':'lower_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = 'higher mac ZD set Factory'
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'higher_mac_zd'},test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = 'Set higher mac ZD device IP settings via GUI' 
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = 'add every configuration item to lower mac(active) ZD to add cfg files'
    test_cfgs.append(({'zd':'lower_mac_zd'},test_name, common_name, 0, False))
    
##############################################################################
    test_case_name='case1:add xml files by add configuration'
    
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[%s]Disable switch port connectet to all ap' % test_case_name
    test_cfgs.append(({'ap_tag':'all','device':'ap'},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR and ready to do test' % test_case_name
    test_cfgs.append(({},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
           
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to 1 ap' % test_case_name
    test_cfgs.append(({'device':'ap','number':1},test_name, common_name, 2, False))  

    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Add'},test_name,common_name,2,False)) 
    
####################################################
#Case 2: on sync, Mod xml files by add configuration
#after the operation of add configuration,cmp files
####################################################   
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = 'add every configuration item to lower mac(active) ZD to edit cfg files'
    test_cfgs.append(({'zd':'lower_mac_zd','second':'Y'},test_name, common_name, 0, False))  

    test_case_name='case2:,mod xml files by add configuration'
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR and ready to do test' % test_case_name
    test_cfgs.append(({},test_name,common_name,1,False))
           
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to all aps' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 2, False))  

    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
 
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod'},test_name,common_name,2,False)) 

####################################################    
#Case 3: on sync, Mod xml files by edit configuration
#after the operation of add configuration,cmp files
####################################################       
    test_case_name='case3:,mod xml files by edit configuration' 
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR and ready to do test' % test_case_name
    test_cfgs.append(({},test_name,common_name,1,False))
    
    test_name = 'CB_ZD_Edit_All_Exist_Configure'
    common_name = '[%s]edit all exist configure on low mac(active) zd' % test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd'}, test_name, common_name, 2, False))  

    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod'},test_name,common_name,2,False))    

#######################################################    
#Case 4: on sync, Mod xml files by delete configuration
#after the operation of delete configuration,cmp files
########################################################

    test_case_name='case4:,mod xml files by delete configuration' 
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR and ready to do test' % test_case_name
    test_cfgs.append(({},test_name,common_name,1,False))
   
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[%s]Disable switch port connectet 1 ap' % test_case_name
    test_cfgs.append(({'ap_tag':active_ap_list[0],'device':'ap'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Delete_One_Item_From_Each_Configuration'
    common_name = '[%s]delete one item from each configuration' % test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd','ap_tag':active_ap_list[0]},test_name, common_name, 2, False))

    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))

    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod'},test_name,common_name,2,False))  
    
#######################################################    
#Case 5: on sync, Mod or del xml files by clear configuration
#after the operation of add configuration,cmp files
########################################################   

    test_case_name='case5:,mod or del xml files by clear configuration' 
    
           
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to all aps' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 1, False)) 
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting command prompt for %d seconds ' % (test_case_name,cmd_prompt_wait)
    test_cfgs.append(({'timeout':cmd_prompt_wait}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[%s]Disable switch port connectet to all ap' % test_case_name
    test_cfgs.append(({'ap_tag':'all','device':'ap'},test_name, common_name, 2, False)) 
     
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = '[%s]clear ZD configuration' % test_case_name
    test_cfgs.append(({'ap_cfg':True,'zd':'lower_mac_zd'},test_name, common_name, 2, False)) 

    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))

    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Del'},test_name,common_name,2,False))  
    
#######################################################    
#Case 6: restore environment
#enable switch ports connected to aps
########################################################      
    
    test_case_name='restore environment' 
            
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%s-Enable sw port connected to all aps' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True)) 
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '%s-Enable sw port connected to all zds' % test_case_name
    test_cfgs.append(({'device':'zd'},test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '%s-Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 0, True))
    
    return test_cfgs        
            
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="compare after operation when ZDs on synchronization"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    active_ap_list = tb_cfg['ap_sym_dict'].keys()
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="compare after operation when ZDs on synchronization"
    test_cfgs = defineTestConfiguration(active_ap_list)
    ts = testsuite.get_testsuite(ts_name, 'compare after operation when ZDs on synchronization', interactive_mode = attrs["interactive_mode"], combotest=True)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)
    
        
 
if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
       
        
    

