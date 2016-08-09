'''
create @2011/11/24, by west.li@ruckuswireless.com
compare xml file after first sync or after operations on sync
'''

import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


def defineTestConfiguration():
    
    test_cfgs = [] 
    data_sync_time=2 #minutes
    dual_stak_ip_cfg = {'ip_version': const.DUAL_STACK,
                        const.IPV4: {'ip_alloc': 'dhcp',},
                        const.IPV6: {'ipv6_alloc': 'auto',},
                        'vlan': '',
                        }
#############################################################################
#Case 1: first sync, all of the xml files exist in active ZD, 
#no file exist in standby ZD, 
#after sync(sync configuration in active ZD to standby ZD ) compare
#############################################################################  
     
    test_case_name='Case 1:first Sync,add all xml files,a to s'
    
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
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = 'Set higher mac ZD device IP settings via GUI'
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = 'add every configuration item to high mac ZD to add cfg files'
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD'
    common_name = '[%s]make all ap connect to high mac ZD' % test_case_name
    test_cfgs.append(({'to_zd':'higher_mac_zd', 'from_zd':'lower_mac_zd'},\
                      test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(high-mac-zd(a)->low-mac-zd(s))' % test_case_name
    test_cfgs.append(({'zd1':'higher_mac_zd','zd2':'lower_mac_zd'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is standby' % test_case_name
    test_cfgs.append(({'except_state':'standby'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Add'},test_name,common_name,2,False))   
    
#############################################################################
#Case 2: first sync, standby ZD has all of the xml files, active has none, 
#after sync(sync configuration in active ZD to standby ZD ) compare
#############################################################################
    test_case_name='Case 2:first Sync,del all xml files,a to s'
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[%s]Disable switch port connectet to all ap' % test_case_name
    test_cfgs.append(({'ap_tag':'all','device':'ap'},test_name, common_name, 2, False))
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]lower mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'lower_mac_zd'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set lower mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'lower_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(low-mac-zd(a)->high-mac-zd(s))' % test_case_name
    test_cfgs.append(({'zd1':'lower_mac_zd','zd2':'higher_mac_zd'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Del'},test_name,common_name,2,False)) 

#############################################################################
#Case 3: first sync, standby ZD has all of the xml files, active has none, 
#after sync(sync configuration in standby ZD to active ZD ) compare
#############################################################################
    test_case_name='Case 3:first Sync,add all xml files,s to a'
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to all aps' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 2, False))

    test_name = 'CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD'
    common_name = '[%s]make all ap connect to high mac ZD' % test_case_name
    test_cfgs.append(({'to_zd':'higher_mac_zd', 'from_zd':'lower_mac_zd'},\
                      test_name, common_name, 2, False))

    test_name = 'CB_ZD_Disable_Given_Mac_Switch_Port'
    common_name = '[%s]Disable switch port connectet to all ap' % test_case_name
    test_cfgs.append(({'ap_tag':'all','device':'ap'},test_name, common_name, 2, False))       

    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]lower mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'lower_mac_zd'},test_name, common_name, 2, False))     
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set lower mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'lower_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
       
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(high-mac-zd(s)->low-mac-zd(a))' % test_case_name
    test_cfgs.append(({'zd1':'higher_mac_zd','zd2':'lower_mac_zd'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Del'},test_name,common_name,2,False)) 
    
#############################################################################    
#Case 4: first sync, active ZD has all of the xml files, standby has none, 
#after sync(sync configuration in standby ZD to active ZD ) compare         
#############################################################################    
    test_case_name='Case 4:first Sync,del all xml files,s to a'

    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = '[%s]Enable sw port connected to all aps' % test_case_name
    test_cfgs.append(({'device':'ap'},test_name, common_name, 2, False))   

    test_name = 'CB_ZD_SR_Make_All_Ap_Connect_To_One_ZD'
    common_name = '[%s]make all ap connect to high mac ZD' % test_case_name
    test_cfgs.append(({'to_zd':'higher_mac_zd', 'from_zd':'lower_mac_zd'},\
                      test_name, common_name, 2, False))

    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]lower mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'lower_mac_zd'},test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set lower mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'lower_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
      
     
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(low-mac-zd(s)->high-mac-zd(a))' % test_case_name
    test_cfgs.append(({'zd1':'lower_mac_zd','zd2':'higher_mac_zd'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is standby' % test_case_name
    test_cfgs.append(({'except_state':'standby'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Del'},test_name,common_name,2,False)) 
    
#############################################################################    
#Case 5: first sync, both ZD has all of the xml files, 
#after sync(sync configuration in active ZD to standby ZD ) compare    
#############################################################################
    test_case_name='Case 5:first Sync,Mod all xml files,a to s'
 
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy on both ZD before case 5'
    test_cfgs.append(({},test_name, common_name, 0, False))
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = 'lower mac ZD set Factory case 5'
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'lower_mac_zd'},test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = 'Set lower mac ZD device IP settings via GUI case 5'
    param_cfg = {'zd':'lower_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
 
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = 'higher mac ZD set Factory case 5'
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = 'Set higher mac ZD device IP settings via GUI case 5'
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))  
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = 'add every configuration item to high mac ZD to add cfg files case 5'
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = 'add every configuration item to lower mac ZD to add cfg files case 5'
    test_cfgs.append(({'zd':'lower_mac_zd'},test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[%s]Adjust the 2 ZDs to have the same APs'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 1, False)) 
     
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(low-mac-zd(a)->high-mac-zd(s))' % test_case_name
    test_cfgs.append(({'zd1':'lower_mac_zd','zd2':'higher_mac_zd'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod'},test_name,common_name,2,False)) 
        
#############################################################################   
#Case 6: first sync, both ZD has all of the xml files, 
#after sync(sync configuration in standby ZD to active ZD ) compare    
#############################################################################
    test_case_name='Case 6:first Sync,Mod all xml files,s to a'

    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[%s]Adjust the 2 ZDs to have the same APs'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))   
        
    test_name = 'CB_ZD_Edit_All_Exist_Configure'
    common_name = '[%s]edit all exist configure on low mac zd,to make the two zd have different cfg'% test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd'}, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SRhigh-mac-zd(s)->(low-mac-zd(a))' % test_case_name
    test_cfgs.append(({'zd1':'higher_mac_zd','zd2':'lower_mac_zd'},test_name,common_name,2,False))   
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
       
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod'},test_name,common_name,2,False))
    
    test_name = 'CB_ZD_Enable_Sw_Port_Connect_To_Given_Device'
    common_name = 'restore Env-Enable sw port connected to all aps'
    test_cfgs.append(({'device':'ap'},test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy after test'
    test_cfgs.append(({},test_name, common_name, 0, True))
    
    return test_cfgs 
             
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="cmp xml files after first sync"
    )
    attrs.update(kwargs)
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="cmp xml files after first sync"
    test_cfgs = defineTestConfiguration()
    ts = testsuite.get_testsuite(ts_name, 'compare xml files after first sync', interactive_mode = attrs["interactive_mode"], combotest=True)

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
    
