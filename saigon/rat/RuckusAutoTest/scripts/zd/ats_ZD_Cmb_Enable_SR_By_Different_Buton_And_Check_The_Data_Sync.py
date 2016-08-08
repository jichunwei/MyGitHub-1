'''
create @2011/12/19, by west.li@ruckuswireless.com
compare xml file after the steps below:
1. two zd have different configuration ,and SR not enabled
2. enable SR by click the button "sync to peer" "sync from peer" of the two zds
3. after the sync,check the data sync(by compare xml file)
'''


import sys
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant as const

def defineTestConfiguration():
    test_cfgs = [] 
    data_sync_time=2 #minutes
    dual_stak_ip_cfg = {'ip_version': const.DUAL_STACK,
                        const.IPV4: {'ip_alloc': 'dhcp',},
                        const.IPV6: {'ipv6_alloc': 'auto',},
                        'vlan': '',
                        }
    ###################################################
    #case 1,click 'sync to peer' in low mac zd
    ###################################################
    test_case_name='case1:click \'sync to peer\' in low mac zd'
    
    test_name = 'CB_ZD_SR_Init_Env' 
    common_name = 'Initial Test Environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))
           
    test_name = 'CB_ZD_SR_Get_Lower_Mac_ZD' 
    common_name = 'Get Lower Mac ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))
        
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
        
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
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]higher mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'higher_mac_zd'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set higher mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to lower mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to high mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[%s]Adjust the 2 ZDs to have the same APs'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '[%s]download the xmls from the zd which is the source of the data sync' % test_case_name
    test_cfgs.append(({'zdcli':'lower_mac_zdcli'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(low-mac-zd(a)->high-mac-zd(s))' % test_case_name
    test_cfgs.append(({'zd1':'lower_mac_zd','zd2':'higher_mac_zd'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Check_AP_Num_In_Active_Zd'
    common_name = '[%s]:check the aps all reconnect to active zd' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
        
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod','bakfile':'Y','zdcli1':'lower_mac_zdcli','zdcli2':'higher_mac_zdcli'},test_name,common_name,2,False)) 

    ###################################################
    #case 2,click 'sync from peer' in low mac zd
    ###################################################
    test_case_name='case2:click \'sync from peer\' in low mac zd'
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
        
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
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]higher mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'higher_mac_zd'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set higher mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to lower mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to high mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[%s]Adjust the 2 ZDs to have the same APs'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '[%s]download the xmls from the zd which is the source of the data sync' % test_case_name
    test_cfgs.append(({'zdcli':'higher_mac_zdcli'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SR(low-mac-zd(a)<-high-mac-zd(s))' % test_case_name
    test_cfgs.append(({'zd1':'lower_mac_zd','zd2':'higher_mac_zd','direction':'from'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Check_AP_Num_In_Active_Zd'
    common_name = '[%s]:check the aps all reconnect to active zd' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
        
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod','bakfile':'Y','zdcli1':'higher_mac_zdcli','zdcli2':'lower_mac_zdcli'},test_name,common_name,2,False)) 

    ###################################################
    #case 3,click 'sync to peer' in high mac zd
    ###################################################
    test_case_name='case3:click \'sync to peer\' in high mac zd'
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
        
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
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]higher mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'higher_mac_zd'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set higher mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to lower mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to high mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[%s]Adjust the 2 ZDs to have the same APs'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '[%s]download the xmls from the zd which is the source of the data sync' % test_case_name
    test_cfgs.append(({'zdcli':'higher_mac_zdcli'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SRhigh-mac-zd(s)->(low-mac-zd(a))' % test_case_name
    test_cfgs.append(({'zd1':'higher_mac_zd','zd2':'lower_mac_zd','direction':'to'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Check_AP_Num_In_Active_Zd'
    common_name = '[%s]:check the aps all reconnect to active zd' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
        
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod','bakfile':'Y','zdcli1':'higher_mac_zdcli','zdcli2':'lower_mac_zdcli'},test_name,common_name,2,False)) 
    

    ###################################################
    #case 4,click 'sync from peer' in high mac zd
    ###################################################
    test_case_name='case4:click \'sync from peer\' in high mac zd'
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = '[%s]Disable Smart Redundancy on both ZD' % test_case_name
    test_cfgs.append(({},test_name, common_name, 1, False))    
        
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
    
    test_name = 'ZD_SetupWizardConfiguration'
    common_name = '[%s]higher mac ZD set Factory' % test_case_name
    test_cfgs.append(({'language':'English', 'dhcp':False, 'system_name':'ruckus', 'country_code':'United States',
                         'mesh_enabled':False, 'wireless1_enabled':True, 'wireless1_name':'Ruckus-Wireless-1',
                         'authentication_open':True, 'guest_wlan_enabled':False,
                         'guest_wlan_name':'Ruckus-Guest', 'admin_name':'admin',
                         'admin_password':'', 'create_user_account_is_checked':False,
                         'zd':'higher_mac_zd'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Set_Device_IP_Settings'
    common_name = '[%s]Set higher mac ZD device IP settings via GUI' % (test_case_name,)
    param_cfg = {'zd':'higher_mac_zd','ip_cfg': dual_stak_ip_cfg}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))    
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to lower mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'lower_mac_zd'},test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Add_Every_Configuration_Item'
    common_name = '[%s]add every configuration item to high mac ZD to add cfg files' % test_case_name
    test_cfgs.append(({'zd':'higher_mac_zd'},test_name, common_name, 2, False))   
    
    test_name = 'CB_ZD_SR_Adjust_To_Same_AP'
    common_name = '[%s]Adjust the 2 ZDs to have the same APs'% test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Download_File_From_Zd'
    common_name = '[%s]download the xmls from the zd which is the source of the data sync' % test_case_name
    test_cfgs.append(({'zdcli':'lower_mac_zdcli'},test_name, common_name, 2, False))  
    
    test_name = 'CB_ZD_SR_Enable'
    common_name = '[%s]both ZD enable SRhigh-mac-zd(s)<-(low-mac-zd(a))' % test_case_name
    test_cfgs.append(({'zd1':'higher_mac_zd','zd2':'lower_mac_zd','direction':'from'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Check_Lower_Mac_State'
    common_name = '[%s]make sure low mac ZD is active' % test_case_name
    test_cfgs.append(({'except_state':'active'},test_name,common_name,2,False))
    
    test_name = 'CB_Scaling_Waiting'
    common_name = '[%s]:Waiting data sync for %d mins ' % (test_case_name,data_sync_time)
    test_cfgs.append(({'timeout':data_sync_time*60}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_SR_Check_AP_Num_In_Active_Zd'
    common_name = '[%s]:check the aps all reconnect to active zd' % test_case_name
    test_cfgs.append(({}, test_name, common_name, 2, False))
        
    test_name = 'CB_SR_Compare_Xml_Files'
    common_name = '[%s]compare xml files' % test_case_name
    test_cfgs.append(({'action':'Mod','bakfile':'Y','zdcli1':'lower_mac_zdcli','zdcli2':'higher_mac_zdcli'},test_name,common_name,2,False)) 
    
    test_name = 'CB_ZD_SR_Disable'
    common_name = 'Disable Smart Redundancy after test'
    test_cfgs.append(({},test_name, common_name, 0, True))    
    
    return test_cfgs
    
def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = 0,
        targetap = False,
        testsuite_name="enable SR by clicking different button-and then check the data sync is right"
    )
    attrs.update(kwargs)
    tbi = testsuite.getTestbed(**kwargs)
    tb_cfg = testsuite.getTestbedConfig(tbi)
    sta_ip_list = tb_cfg['sta_ip_list']
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = sta_ip_list[attrs["sta_id"]]
    
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name ="enable SR by clicking different button"
    test_cfgs = defineTestConfiguration()
    ts = testsuite.get_testsuite(ts_name, "enable SR by clicking different button-and then check the data sync is right", interactive_mode = attrs["interactive_mode"], combotest=True)

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
           
    
    
    
    
    