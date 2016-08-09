'''
Description:
  This testsuite is used to test the feature 'not removing WLANs'on single band AP and dual bind AP when mesh is enabled.
  'not removing WLANs' is first added in version 9.5, so this testsuite only can be tested in 9.5 version and the versions after 9.5.
  
  How to test:
   1. Remove all confiure in ZD
   2. Create 12 WLANs wish SSID and WLAN groups as below:

			WLAN: 
			-----------------------------------
			openWlan1,openWlan2,...,openWlan5,openWlan6,
			openWlan7,openWlan8,...,openWlan11,openWlan12
			
			WLAN group:
			-----------------------------------
			Default: openWlan1,openWlan2,...,openWlan5,openWlan6
			
			wlan_grp0: no WLAN
			
			2.4G wlan group:
			wlan_bgn_grp1: openWlan1
			wlan_bgn_grp2: openWlan1,openWlan2
			...
			wlan_bgn_grp5: openWlan1,openWlan2,...,openWlan5
			wlan_bgn_grp6: openWlan1,openWlan1,...,openWlan6
			
			5G wlan group:
			wlan_na_grp1: openWlan7
			wlan_na_grp2: openWlan7,openWlan8
			...
			wlan_na_grp6: openWlan7,openWlan8,...,openWlan12

   3. Create 6 AP groups as below:
			System Default: Default
			AP_group1: WLAN Group: 2.4G wlan_bgn_grp1,5G wlan_na_grp1
			AP_group2: WLAN Group: 2.4G wlan_bgn_grp2,5G wlan_na_grp2
			AP_group3: WLAN Group: 2.4G wlan_bgn_grp3,5G wlan_na_grp3
			...
			AP_group5: WLAN Group: 2.4G wlan_bgn_grp5,5G wlan_na_grp5
			AP_group6: WLAN Group: 2.4G wlan_bgn_grp6,5G wlan_na_grp6
			
	 4. Test on single band AP through modifying parameters on AP, wlan group and AP group
	 5. Test on dual band AP through modifying parameters on AP, wlan group and AP group
	 6. Disconnect AP port on switch and make a root AP to mesh AP
	 7. Reconnect the AP port on switch and make the mesh AP to Root
	 8. Disconnect AP port on switch to make a root ap to mesh ap, and then change the uplink of this ap to another root AP
	 9. Forming the mesh tree: root ap:1 hot mesh ap:2 hops mesh ap, and then change the uplink of the 2 hops ap to root Ap to make it to 1 hop ap.     
Created on 2012-10-25
@author: zoe.huang@ruckuswireless.com

'''

import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as libCons

input_seq = ['single_band_ap', 'dual_band_ap1', 'dual_band_ap2', 'dual_band_ap3']

def define_test_cfg_for_singleband(tcfg):
    test_cfgs = []
    sta_tag = 'STA1'
#-------------------------------configuration----------------------------------------------------------------    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configurations on ZD at config'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    param_cfg = {'sta_tag': sta_tag, 'sta_ip_addr': tcfg['target_station']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the station at configuration'
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the Single Band AP'
    param_cfg = {'ap_tag': 'AP1', 'active_ap': tcfg['aps_to_be_tested']['single_band_ap']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure Single Band AP Radio - Enable WLAN Service at config'
    param_cfg = {'ap_tag': 'AP1', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlans'
    common_name = "Create the expected WLANs for test on ZD"
    param_cfg = {'wlan_cfg_list': tcfg['wlan_cfg_list']}
    test_cfgs.append((param_cfg , test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_WLANGroups_with_WLANs'
    common_name = 'Create expected wlan groups for test on ZD'
    param_cfg = {'wlangroups_map': tcfg['wgs_cfg_list']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
    common_name = "Remove wlans from the default wlan group"
    param_cfg = {'wgs_cfg': {'name':'Default'},
                 'wlan_list': [wlan['ssid'] for wlan in tcfg['wlan_cfg_list']][6:]
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Multi_AP_Groups'
    common_name = 'Create expected AP groups for test on ZD'
    param_cfg = {'numbers': 6, 'apg_cfg' : tcfg['apgroup_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Delete_APs_Rejoin'
    common_name = 'Delete the single band AP and wait it rejoin ZD'  
    param_cfg = {'ap_tags':['AP1']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

#------------------------------------Single Band AP(7 cases)-------------------------------------------
#----------1.Mesh Enable - Single Band AP - join ZD with default setting-----------------------

    test_case_name = '[Mesh Enable-Single Band AP-join ZD with default setting] '
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default group are up' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group info and wlan status in AP via ZD WebUI' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with each wlan in default wlan group' % test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in range(0, 6)]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#------------2.Mesh Enable - Single Band AP - overwrite different WLAN groups in AP setting---------------
    test_case_name = '[Mesh Enable-Single Band AP-overwrite different WLAN groups in AP setting] '
    
    wlan_group = 'wlan_grp0'
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '%sAssign the WLAN group of radio %s to %s' % (test_case_name,tcfg['singlebandAPtestcfg']['radio'], wlan_group)  
    param_cfg = {'active_ap': tcfg['aps_to_be_tested']['single_band_ap'],
                 'wlan_group_name': wlan_group, 
                 'radio_mode': tcfg['singlebandAPtestcfg']['radio']}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in wlan group %s are down' % (test_case_name, wlan_group)
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status when wlan group is %s' % (test_case_name, wlan_group)
    param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: wlan_group}}                    
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
   
    for i in  [2,4,6]:       
        wlan_group = '%s%d' % (tcfg['singlebandAPtestcfg']['wlangrp_pre'],i)
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = '%sAssign WLAN group of radio %s to %s' % (test_case_name,tcfg['singlebandAPtestcfg']['radio'], wlan_group)  
        param_cfg = {'active_ap': tcfg['aps_to_be_tested']['single_band_ap'],
                     'wlan_group_name': wlan_group, 
                     'radio_mode': tcfg['singlebandAPtestcfg']['radio']} 
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans in wlan group %s are up and others are down' % (test_case_name, wlan_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            if i!=6:
                param_cfg = {'ap_tag': 'AP1', 
                             'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:]},
                             'up':{'5g': tcfg['wgs_cfg_list'][wlan_group]}
                             }
            else:
               param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list'][wlan_group]} } 
        else:
            if i!=6:
                param_cfg = {'ap_tag': 'AP1',
                          'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:]},
                         'up':{'24g': tcfg['wgs_cfg_list'][wlan_group]}
                          }
            else:
               param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list'][wlan_group]} } 
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan group and status when wlan group is %s' % (test_case_name, wlan_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            param_cfg = {'ap_tag': 'AP1', 
                         'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: wlan_group},
                         'up':{'5g': tcfg['wgs_cfg_list'][wlan_group]}
                         }
        else:
            param_cfg = {'ap_tag': 'AP1',
                          'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: wlan_group},
                          'up':{'24g': tcfg['wgs_cfg_list'][wlan_group]}
                          }                     
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Associate_Station_With_Wlans'
        common_name = '%sVerify station can associate with wlans in %s' % (test_case_name, wlan_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            param_cfg = {'sta_tag': sta_tag, 
                     'wlans_cfg_list':[tcfg['wlan_cfg_list'][j] for j in range(6, i+6)][-2:]} 
        else:
             param_cfg = {'sta_tag': sta_tag, 
                     'wlans_cfg_list':[tcfg['wlan_cfg_list'][j] for j in range(0, i)][-2:]}                  
        
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove all wlans from station when %s' % (test_case_name,wlan_group)
        param_cfg = {'sta_tag': sta_tag}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    wlan_group = 'Default'
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '%sAssign WLAN group of radio %s to %s' % (test_case_name,tcfg['singlebandAPtestcfg']['radio'], wlan_group)  
    param_cfg = {'active_ap': tcfg['aps_to_be_tested']['single_band_ap'],
                 'wlan_group_name': wlan_group, 
                 'radio_mode': tcfg['singlebandAPtestcfg']['radio']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % (test_case_name)
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#----------------3.Mesh Enable - Single Band AP - Disable or Enable for WLAN service on radio in AP setting--------------
    test_case_name = '[Mesh Enable-Single Band AP-Disable or Enable for WLAN service on radio in AP setting] '
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sDisable WLAN Service at config' % test_case_name
    param_cfg = {'ap_tag': 'AP1', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': False}}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are down' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status after disable wlan service' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sEnable WLAN Service' % test_case_name
    param_cfg = {'ap_tag': 'AP1', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status after enable wlan service' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with each wlan in default' % test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in [1,3,5]]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % (test_case_name)
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sEnable WLAN Service at cleanup' % test_case_name
    param_cfg = {'ap_tag': 'AP1', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#---------------------4.Mesh Enable - Single Band AP - Move AP from AP group 1 to 6 in AP setting--------------
    test_case_name = '[Mesh Enable-Single Band AP-Move AP from AP group 1 to 6 in AP setting] '
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associate the wlan and get wifi address' % test_case_name
    param_cfg = {'wlan_cfg': tcfg['wlan_cfg_list'][0], 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Linux_Server_Ping_Station'
    common_name = '%sLinux server starts to ping the wifi addr of station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    for i in [1,3,5]:
        ap_group = '%s%d' % (tcfg['apgroup_cfg']['apg_prefix_name'], i)
        
        test_name = 'CB_ZD_Configure_AP_General_Info'
        common_name = '%sSet AP group of single band AP to %s' % (test_case_name,ap_group)
        param_cfg = {'general_info': {'device_name': 'RuckusAP',
                                      'description': '',
                                      'device_location': 'Lab',
                                      'gps_latitude': '',
                                      'gps_longitude': '',
                                      'ap_group': ap_group,
                                     }, 
                    'ap_tag': 'AP1'}
        test_cfgs.append((param_cfg,test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans are up when AP group is %s' % (test_case_name, ap_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        else:
            param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan group and status when AP group is %s' % (test_case_name, ap_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                         'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        else:
            param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                         'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Linux_Server_Stop_Ping_Station_Verify_Results'
    common_name = '%sLinux server stops ping the wifi addr of station and verify the results' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Configure_AP_General_Info'
    common_name = '%sSet AP group of single band AP back to System Default' % test_case_name
    param_cfg = {'general_info': {'device_name': 'RuckusAP',
                                      'description': '',
                                      'device_location': 'Lab',
                                      'gps_latitude': '',
                                      'gps_longitude': '',
                                      'ap_group': 'System Default',
                                     }, 
                    'ap_tag': 'AP1'}
    test_cfgs.append((param_cfg,test_name, common_name, 2, True)) 

#----------------5.Mesh Enable - Single Band AP - Change WLANs group in AP group-------------------------
    test_case_name = '[Mesh Enable-Single Band AP-Change WLANs group in AP group] '
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associate the wlan and get wifi address' % test_case_name
    param_cfg = {'wlan_cfg': tcfg['wlan_cfg_list'][1], 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Linux_Server_Ping_Station'
    common_name = '%sLinux server starts to ping the wifi addr of station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    wlan_group = 'wlan_grp0'    
    test_name = 'CB_ZD_Configure_AP_Group_Radio_Info'
    common_name = '%sAssign the WLAN group in System Default AP Group to wlan group %s' % (test_case_name, wlan_group)  
    param_cfg = {'apgroup_name' : 'System Default',
                 'bgn': {'wlangroups': wlan_group},
                 'na': {'wlangroups': wlan_group} }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans are up when set wlan group %s in AP group' % (test_case_name, wlan_group)
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status when set wlan group %s in AP group'\
     % (test_case_name, wlan_group)
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']},
                 }                    
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    for i in [1,3,5]:
        wlan_24g_group = '%s%d' % (tcfg['apgroup_cfg']['gn_wg_prefix_name'], i)
        wlan_5g_group = '%s%d' % (tcfg['apgroup_cfg']['an_wg_prefix_name'], i)
        
        test_name = 'CB_ZD_Configure_AP_Group_Radio_Info'
        common_name = '%sAssign WLAN group in System Default AP Group to 2.4g: %s, 5g:%s' \
        % (test_case_name, wlan_24g_group, wlan_5g_group) 
        param_cfg = {'apgroup_name' : 'System Default',
                 'bgn': {'wlangroups': wlan_24g_group},
                 'na': {'wlangroups': wlan_5g_group} }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans are up when set wlan group %s for 2.4g %s for 5g'\
         % (test_case_name, wlan_24g_group, wlan_5g_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        else:
            param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan status when set wlan group 2.4g %s 5g %s' \
        % (test_case_name, wlan_24g_group, wlan_5g_group)
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                         'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        else:
            param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                         'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Linux_Server_Stop_Ping_Station_Verify_Results'
    common_name = '%sLinux server stops ping wifi addr and verify results' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Configure_AP_Group_Radio_Info'
    common_name = '%sAssign WLAN group to Default' % test_case_name  
    param_cfg = {'apgroup_name' : 'System Default',
                 'bgn': {'wlangroups': 'Default'},
                 'na': {'wlangroups': 'Default'} }
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#------------------6.Mesh Enable - Single Band AP - WLANs can be changed in WLAN group-----------------------
    test_case_name = '[Mesh Enable-Single Band AP-WLANs can be changed correctly in WLAN group] '
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group info and wlan status in AP via ZD WebUI' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))       
    
    for i in [2,4,6]:
        test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
        common_name = "%sRemove WLAN '%s'" % \
        (test_case_name, str(tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i-1]))
        param_cfg = {'wgs_cfg': {'name':'Default'},
                     'wlan_list': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans status when remove wlan%s' % \
                             (test_case_name,str(tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i-1]))
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            if i!=6:
                param_cfg = {'ap_tag': 'AP1', 
                         'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6]},
                         'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
                         }
            else:
                param_cfg = {'ap_tag': 'AP1',
                         'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
                         }
        else:
            if i!= 6:
                param_cfg = {'ap_tag': 'AP1', 
                             'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6]},
                             'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
                             }
            else:
                 param_cfg = {'ap_tag': 'AP1',
                              'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
                              }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan group and status after remove wlan%s'\
         % (test_case_name,str(tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i-1]))
        if tcfg['singlebandAPtestcfg']['radio'] == 'na':
            if i!=6:
                param_cfg = {'ap_tag': 'AP1', 
                         'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                         'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6]}}
            else:
                param_cfg = {'ap_tag': 'AP1', 
                         'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},}
        else:
            if i!=6:
                param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                         'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6]}}
            else:
                param_cfg = {'ap_tag': 'AP1', 
                         'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))   
   
    test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
    common_name = '%sAssign wlans back to Default' % test_case_name  
    param_cfg = {'wlangroup_name': 'Default', 
                 'wlan_name_list': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:6]}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up at cleanup' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group info and wlan status in AP via ZD WebUI at cleanup' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
#----------------------7.Mesh Enable - Single Band AP - Modify WLAN parameters in WLAN-----------------------
    test_case_name = '[Mesh Enable-Single Band AP-Modify WLAN parameters in WLAN] '
    
    wlan_to_modify = tcfg['wlan_cfg_list'][0]['ssid']
    new_wlan_cfg = {'sta_wpa_ver': 'WPA', 'sta_auth': 'PSK', 'encryption': 'AES', 'auth': 'PSK', 
                    'sta_encryption': 'AES', 'key_string': 'f4b65bafb19f8f38d2ba', 'wpa_ver': 'WPA'}
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '%sModify parameters of WLAN %s' % (test_case_name,wlan_to_modify)
    param_cfg = {'wlan_ssid': wlan_to_modify, 'new_wlan_cfg': new_wlan_cfg}   
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associate the wlan %s and get wifi address' % (test_case_name,wlan_to_modify)
    new_wlan_cfg['ssid'] = wlan_to_modify
    param_cfg = {'wlan_cfg':new_wlan_cfg , 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status in AP via ZD WebUI' % test_case_name
    if tcfg['singlebandAPtestcfg']['radio'] == 'na':
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    else:
        param_cfg = {'ap_tag': 'AP1', 'wlan_group':{tcfg['singlebandAPtestcfg']['radio']: 'Default'},
                     'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '%sChange the parameters back for WLAN %s' % (test_case_name,wlan_to_modify)
    param_cfg = {'wlan_ssid': wlan_to_modify, 
                 'new_wlan_cfg': dict(auth="open", wpa_ver="", encryption="none",
                                sta_auth="open", sta_wpa_ver="", sta_encryption="none",key_index="" , key_string="")}   
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))     
    
#-----------------------------------------cleanup-------------------------------------------------------------
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the station at cleanup'
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove All AP Groups at cleanup'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all wlan groups at cleanup'
    param_cfg = {}   
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD at cleanup'
    param_cfg = {}   
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    return test_cfgs

def define_test_cfg_for_dualband(tcfg):
    test_cfgs = []
    sta_tag = 'STA1'
#-------------------------------configuration----------------------------------------------------------------    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configurations on ZD at config'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    param_cfg = {'sta_tag': sta_tag, 'sta_ip_addr': tcfg['target_station']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the station at configuration'
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the first Dual Band AP'
    param_cfg = {'ap_tag': 'AP2', 'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure the first Dual Band AP Radio - Enable WLAN Service'
    param_cfg = {'ap_tag': 'AP2', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
      
    test_name = 'CB_ZD_Create_Wlans'
    common_name = "Create the expected WLANs for test on ZD"
    param_cfg = {'wlan_cfg_list': tcfg['wlan_cfg_list']}
    test_cfgs.append((param_cfg , test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_WLANGroups_with_WLANs'
    common_name = 'Create expected wlan groups for test on ZD'
    param_cfg = {'wlangroups_map': tcfg['wgs_cfg_list']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
    common_name = "Remove wlans from the default wlan group"
    param_cfg = {'wgs_cfg': {'name':'Default'},
                 'wlan_list': [wlan['ssid'] for wlan in tcfg['wlan_cfg_list']][6:]
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Multi_AP_Groups'
    common_name = 'Create expected AP groups for test on ZD'
    param_cfg = {'numbers': 6, 'apg_cfg' : tcfg['apgroup_cfg']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Delete_APs_Rejoin'
    common_name = 'Delete the first dual band AP and wait it rejoin ZD'  
    param_cfg = {'ap_tags':['AP2']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))

   
#------------------------------------Dual Band AP(7 cases)------------------------------------------------
    
#-----------------------8.Mesh Enable - Dual Band AP - join ZD with default setting-----------------------

    test_case_name = '[Mesh Enable-Dual Band AP-join ZD with default setting] '
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group info and wlan status' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'wlan_group':{'ng': 'Default','na': 'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
   
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with wlans in default group' % test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in range(0, 6)]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#---------------------9.Mesh Enable - Dual Band AP - Overwrite different WLAN group in AP setting----------------
    test_case_name = '[Mesh Enable-Dual Band AP-Overwrite different WLAN group in AP setting] '
    
    wlan_group = 'wlan_grp0'
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '%sAssign WLAN group of radio %s to %s' % (test_case_name,'ng', wlan_group)  
    param_cfg = {'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1'],
                 'wlan_group_name': wlan_group, 
                 'radio_mode': 'ng'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '%sAssign WLAN group of radio %s to %s' % (test_case_name,'na', wlan_group)  
    param_cfg = {'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1'],
                 'wlan_group_name': wlan_group, 
                 'radio_mode': 'na'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans are down when wlan group is %s' % (test_case_name, wlan_group)
    param_cfg = {'ap_tag': 'AP2', 
                 'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                         '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status when wlan group is %s' % (test_case_name, wlan_group)
    param_cfg = {'ap_tag': 'AP2', 
                 'wlan_group':{'ng': wlan_group,
                               'na': wlan_group}}                    
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
   
    for i in [2,4,6]:        
        wlan_24g_group = '%s%d' % (tcfg['apgroup_cfg']['gn_wg_prefix_name'], i)
        wlan_5g_group = '%s%d' % (tcfg['apgroup_cfg']['an_wg_prefix_name'], i)
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = '%sAssign WLAN group of radio %s to %s' % (test_case_name,'ng', wlan_24g_group)  
        param_cfg = {'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1'],
                     'wlan_group_name': wlan_24g_group, 
                     'radio_mode': 'ng'} 
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
        common_name = '%sAssign WLAN group of radio %s to %s' % (test_case_name,'na', wlan_5g_group)  
        param_cfg = {'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1'],
                     'wlan_group_name': wlan_5g_group, 
                     'radio_mode':'na'} 
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans in %s and %s up others down' %\
         (test_case_name, wlan_24g_group,wlan_5g_group)       
        if i!=6:
            param_cfg = {'ap_tag': 'AP2', 
                         'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:],
                                 '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:]},
                         'up':{'5g': tcfg['wgs_cfg_list'][wlan_5g_group],
                               '24g':tcfg['wgs_cfg_list'][wlan_24g_group]}
                         }
        else:
           param_cfg = {'ap_tag': 'AP2', 
                        'up':{'5g': tcfg['wgs_cfg_list'][wlan_5g_group],
                               '24g':tcfg['wgs_cfg_list'][wlan_24g_group]}
                        }  
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan status when %s and %s'\
         % (test_case_name, wlan_24g_group,wlan_5g_group)   
        param_cfg = {'ap_tag': 'AP2', 
                     'wlan_group':{'na': wlan_5g_group,'ng': wlan_24g_group},
                     'up':{'5g': tcfg['wgs_cfg_list'][wlan_5g_group],
                           '24g': tcfg['wgs_cfg_list'][wlan_24g_group]}
                    }                   
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Associate_Station_With_Wlans'
        common_name = '%sVerify station can associate with wlans in %s and %s'\
         % (test_case_name,wlan_24g_group,wlan_5g_group)
        param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][j] for j in range(0, i)][-2:]+ [tcfg['wlan_cfg_list'][k] for k in range(6, i+6)][-2:]}          
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_Station_Remove_All_Wlans'
        common_name = '%sRemove all wlans from the station %d' % (test_case_name, i)
        param_cfg = {'sta_tag': sta_tag}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    wlan_group = 'Default'
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '%sAssign WLAN group of radio %s to %s at cleanup' % \
    (test_case_name,'ng', wlan_group)  
    param_cfg = {'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1'],
                 'wlan_group_name': wlan_group, 
                 'radio_mode': 'ng'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Assign_AP_To_Wlan_Groups'
    common_name = '%sAssign WLAN group of radio %s to %s at cleanup' % \
    (test_case_name,'na', wlan_group)  
    param_cfg = {'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1'],
                 'wlan_group_name': wlan_group, 
                 'radio_mode': 'na'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#---------------------10.Mesh Enable - Dual Band AP - Disable or Enable for WLAN service on radio in AP setting---------------
    test_case_name = '[Mesh Enable-Dual Band AP-Disable or Enable for WLAN service on radio in AP setting] '
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associates with the wlan and get wifi address' % test_case_name
    param_cfg = {'wlan_cfg': tcfg['wlan_cfg_list'][0], 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Linux_Server_Ping_Station'
    common_name = '%sLinux server starts to ping the wifi addr of station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure Radio 2.4g - Disable WLAN Service' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 'cfg_type': 'config', 'ap_cfg': {'radio':'ng','wlan_service': False}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default group are down under 2.4g and up under 5g' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']},
                 'down': {'24g':tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status after disable 2.4g wlan service' % test_case_name    
    param_cfg = {'ap_tag': 'AP2', 
                 'wlan_group':{'na': 'Default',
                               'ng': 'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']},
                 'down':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure 2.4g - Enable WLAN Service ' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 'cfg_type': 'config', 'ap_cfg': {'radio':'ng','wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure 5g - Disable WLAN Service' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 'cfg_type': 'config', 'ap_cfg': {'radio':'na','wlan_service': False}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans are up under 2.4g and down under 5g after disable 5g' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']},
                 'down': {'5g':tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status after disable 5g wlan service' % test_case_name    
    param_cfg = {'ap_tag': 'AP2', 
                 'wlan_group':{'na': 'Default',
                               'ng': 'Default'},
                 'up':{'24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']},
                 'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
         
    test_name = 'CB_ZD_Linux_Server_Stop_Ping_Station_Verify_Results'
    common_name = '%sLinux server stops ping wifi addr of station and verify results' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = '%sConfigure - Enable WLAN Service at cleanup' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#----------------------11.Mesh Enable - Dual Band AP - Move AP from AP group 1 to 6 in AP setting------------------
    test_case_name = '[Mesh Enable-Dual Band AP-Move AP from AP group 1 to 6 in AP setting] '
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associate the wlan and get wifi address' % test_case_name
    param_cfg = {'wlan_cfg': tcfg['wlan_cfg_list'][0], 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Linux_Server_Ping_Station'
    common_name = '%sLinux server starts to ping the wifi addr of station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    for i in [1,3,5]:
        ap_group = '%s%d' % (tcfg['apgroup_cfg']['apg_prefix_name'], i)
        
        test_name = 'CB_ZD_Configure_AP_General_Info'
        common_name = '%sSet AP group of Dual band AP to %s' % (test_case_name,ap_group)
        param_cfg = {'general_info': {'device_name': 'RuckusAP',
                                      'description': '',
                                      'device_location': 'Lab',
                                      'gps_latitude': '',
                                      'gps_longitude': '',
                                      'ap_group': ap_group,
                                     }, 
                    'ap_tag': 'AP2'}
        test_cfgs.append((param_cfg,test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans are up when AP group is %s' % (test_case_name, ap_group)
        param_cfg = {'ap_tag': 'AP2',
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                           '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']},
                    }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan group and status when AP group is %s' % (test_case_name, ap_group)
        param_cfg = {'ap_tag': 'AP2', 
                     'wlan_group':{'na': 'Default', 'ng':'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                           '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                     }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Linux_Server_Stop_Ping_Station_Verify_Results'
    common_name = '%sLinux server stops ping wifi addr of station and verify results' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Configure_AP_General_Info'
    common_name = '%sSet AP group of Dual band AP back to System Default' % test_case_name
    param_cfg = {'general_info': {'device_name': 'RuckusAP',
                                      'description': '',
                                      'device_location': 'Lab',
                                      'gps_latitude': '',
                                      'gps_longitude': '',
                                      'ap_group': 'System Default',
                                     }, 
                    'ap_tag': 'AP2'}
    test_cfgs.append((param_cfg,test_name, common_name, 2, True)) 

#--------------12.Mesh Enable - Dual Band AP - Change WLANs group in AP group------------------
    test_case_name = '[Mesh Enable-Dual Band AP-Change WLANs group in AP group] '
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associates the wlan and get wifi address' % test_case_name
    param_cfg = {'wlan_cfg': tcfg['wlan_cfg_list'][1], 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Linux_Server_Ping_Station'
    common_name = '%sLinux server starts to ping the wifi addr of station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    wlan_group = 'wlan_grp0'    
    test_name = 'CB_ZD_Configure_AP_Group_Radio_Info'
    common_name = '%sAssign WLAN group in System Default AP Group to wlan group %s' % (test_case_name, wlan_group)  
    param_cfg = {'apgroup_name' : 'System Default',
                 'bgn': {'wlangroups': wlan_group},
                 'na': {'wlangroups': wlan_group} }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans are up when set wlan group %s in AP group' % (test_case_name, wlan_group)
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and status when set wlan group %s in AP group' \
    % (test_case_name, wlan_group)
    param_cfg = {'ap_tag': 'AP2',
                'wlan_group':{'ng': 'Default','na': 'Default'},
                'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                      '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                }             
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))  
    
    for i in [1,3,5]:
        wlan_24g_group = '%s%d' % (tcfg['apgroup_cfg']['gn_wg_prefix_name'], i)
        wlan_5g_group = '%s%d' % (tcfg['apgroup_cfg']['an_wg_prefix_name'], i)
        
        test_name = 'CB_ZD_Configure_AP_Group_Radio_Info'
        common_name = '%sAssign WLAN groupto 2.4g %s 5g %s' \
        % (test_case_name, wlan_24g_group, wlan_5g_group)  
        param_cfg = {'apgroup_name' : 'System Default',
                 'bgn': {'wlangroups': wlan_24g_group},
                 'na': {'wlangroups': wlan_5g_group} }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans are up when %s for 2.4g %s for 5g in AP group' \
        % (test_case_name, wlan_24g_group, wlan_5g_group)
        param_cfg = {'ap_tag': 'AP2', 
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                           '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                    }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan status when %s for 2.4g %s for 5g' \
        % (test_case_name, wlan_24g_group, wlan_5g_group)
        param_cfg = {'ap_tag': 'AP2', 
                     'wlan_group':{'ng': 'Default','na':'Default'},
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                           '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                    }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Linux_Server_Stop_Ping_Station_Verify_Results'
    common_name = '%sLinux server stops ping wifi addr of station and verify results' % test_case_name
    param_cfg = {}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Configure_AP_Group_Radio_Info'
    common_name = '%sAssign WLAN group in System Default AP Group to Default' % test_case_name  
    param_cfg = {'apgroup_name' : 'System Default',
                 'bgn': {'wlangroups': 'Default'},
                 'na': {'wlangroups': 'Default'} }
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#-----------------13.Mesh Enable - Dual Band AP - WLANs can be changed correctly in WLAN group-----------------
    test_case_name = '[Mesh Enable-Dual Band AP-WLANs can be changed correctly in WLAN group] '
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status in AP via ZD WebUI' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))   
    
    for i in [2,4,6]:
        test_name = 'CB_ZD_Remove_Wlan_On_Wlan_Group'
        common_name = "%sRemove WLAN '%s' from the default wlan group" % \
        (test_case_name, str(tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i-1]))
        param_cfg = {'wgs_cfg': {'name':'Default'},
                     'wlan_list': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
        common_name = '%sVerify wlans stauts when remove wlan %s' \
                             % (test_case_name,str(tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i-1]))
        if i!=6:
            param_cfg = {'ap_tag': 'AP2', 
                     'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6],
                           '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6]},
                     'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i],
                             '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
                     }
        else:
            param_cfg = {'ap_tag': 'AP2',
                     'down':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i],
                             '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:i]}
                     }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
        test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
        common_name = '%sVerify wlan group and status after remove wlan %s'\
         % (test_case_name,str(tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i-1]))
        if i!=6:
            param_cfg = {'ap_tag': 'AP2', 
                         'wlan_group':{'na': 'Default', 'ng':'Default'},
                         'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6],
                               '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][i:6]}
                        }
        else:
            param_cfg = {'ap_tag': 'AP2', 
                         'wlan_group':{'na': 'Default','ng':'Default'}
                        }
        test_cfgs.append((param_cfg, test_name, common_name, 2, False))   
   
    test_name = 'CB_ZD_Assign_Wlan_To_Wlangroup'
    common_name = '%sAssign wlans back to Default' % test_case_name  
    param_cfg = {'wlangroup_name': 'Default', 
                 'wlan_name_list': tcfg['wgs_cfg_list']['wlan_bgn_grp6'][0:6]}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up at cleanup' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status at cleanup' % test_case_name
    param_cfg = {'ap_tag':'AP2', 
                 'wlan_group':{'na':'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
#-------------------14.Mesh Enable - Dual Band AP - Modify WLAN parameters in WLAN----------------------
    test_case_name = '[Mesh Enable-Dual Band AP-Modify WLAN parameters in WLAN] '
    
    wlan_to_modify = tcfg['wlan_cfg_list'][0]['ssid']
    new_wlan_cfg = {'sta_wpa_ver': 'WPA', 'sta_auth': 'PSK', 'encryption': 'AES', 'auth': 'PSK', 
                    'sta_encryption': 'AES', 'key_string': 'f4b65bafb19f8f38d2ba', 'wpa_ver': 'WPA'}
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '%sModify parameters of WLAN %s' % (test_case_name,wlan_to_modify)
    param_cfg = {'wlan_ssid': wlan_to_modify, 'new_wlan_cfg': new_wlan_cfg}   
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr'
    common_name = '%sStation associate the wlan %s and get wifi address' % (test_case_name,wlan_to_modify)
    new_wlan_cfg['ssid'] = wlan_to_modify
    param_cfg = {'wlan_cfg':new_wlan_cfg , 'sta_tag': sta_tag}
    test_cfgs.append((param_cfg,test_name, common_name, 2, False))
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    param_cfg = {'ap_tag': 'AP2', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group info and wlan status' % test_case_name
    param_cfg = {'ap_tag':'AP2', 
                 'wlan_group':{'na':'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Edit_Wlan'
    common_name = '%sChange the parameters back for WLAN %s' % (test_case_name,wlan_to_modify)
    param_cfg = {'wlan_ssid': wlan_to_modify, 
                 'new_wlan_cfg': dict(auth="open", wpa_ver="", encryption="none",
                                sta_auth="open", sta_wpa_ver="", sta_encryption="none",key_index="" , key_string="")}   
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))         


#-----------------------------------------cleanup-------------------------------------------------------------
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the station at cleanup'
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove All AP Groups at cleanup'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all wlan groups at cleanup'
    param_cfg = {}   
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD at cleanup'
    param_cfg = {}   
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    return test_cfgs

def define_test_cfg_for_mesh(tcfg):
    test_cfgs = []
    sta_tag = 'STA1'
#-------------------------------configuration----------------------------------------------------------------    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configurations on ZD at config'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    param_cfg = {'sta_tag': sta_tag, 'sta_ip_addr': tcfg['target_station']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the station at configuration'
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    #*********it always stays as Root AP****************
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the first Dual Band AP'
    param_cfg = {'ap_tag': 'AP2', 'active_ap': tcfg['aps_to_be_tested']['dual_band_ap1']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
        
    #*********it maybe become mesh AP with 1 hop****************
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the second Dual Band AP'
    param_cfg = {'ap_tag': 'AP3', 'active_ap': tcfg['aps_to_be_tested']['dual_band_ap2']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    #*********it maybe become mesh AP with 2 hops****************
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Get the third Dual Band AP'
    param_cfg = {'ap_tag': 'AP4', 'active_ap': tcfg['aps_to_be_tested']['dual_band_ap3']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure the second Dual Band AP Radio - Enable WLAN Service'
    param_cfg = {'ap_tag': 'AP3', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Wlans'
    common_name = "Create the expected WLANs for test on ZD"
    param_cfg = {'wlan_cfg_list': tcfg['wlan_cfg_list'][0:6]}
    test_cfgs.append((param_cfg , test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Delete_APs_Rejoin'
    common_name = 'Delete the first dual band AP and wait it rejoin ZD'  
    param_cfg = {'ap_tags':['AP3','AP4']}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
#------------------------------------Mesh AP(4 cases)------------------------------------------------

#------------------15.Mesh Enable - Disconnect AP cable to make it from root AP to Mesh AP-----------------    
    test_case_name = '[Mesh Enable - Disconnect AP cable to make it from root AP to Mesh AP] '
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status in AP via ZD WebUI' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sRoot AP becomes Mesh with mesh ACL' % test_case_name
    param_cfg = {'root_ap': 'AP2',
                 'mesh_ap': 'AP3',
                 'test_option': 'form_mesh_mesh_acl'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up after Root Ap becomes Mesh' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status after Root AP becomes Mesh' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with each wlan after Root AP becomes Mesh' % test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in [0,2,4]]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sReconnect the Mesh AP as Root' % test_case_name
    param_cfg = {'ap_list': ['AP3'],
                 'test_option': 'reconnect_as_root'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#----------------16.Mesh Enable - Reconnect AP cable to make it from mesh AP to root AP---------------------    
    test_case_name = '[Mesh Enable-Reconnect AP cable to make it from mesh AP to root AP] '
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sRoot AP becomes Mesh with mesh ACL' % test_case_name
    param_cfg = {'root_ap': 'AP2',
                 'mesh_ap': 'AP3',
                 'test_option': 'form_mesh_mesh_acl'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
      
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up in the Mesh Ap' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status in Mesh AP via ZD WebUI' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sReconnect the Mesh AP as Root' % test_case_name
    param_cfg = {'ap_list': ['AP3'],
                 'test_option': 'reconnect_as_root'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up after it becomes Root AP' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status after Mesh AP becomes Root' % test_case_name
    param_cfg = {'ap_tag': 'AP3', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with each wlan after Mesh AP becomes Root' % test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in [1,3,5]]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sReconnect the Mesh AP as Root at cleanup' % test_case_name
    param_cfg = {'ap_list': ['AP3'],
                 'test_option': 'reconnect_as_root'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#----------------------17.Mesh Enable - Move one mesh AP between two root APs--------------    
      
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure the third Dual Band AP Radio - Enable WLAN Service'
    param_cfg = {'ap_tag': 'AP4', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': True}}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Configure the second Dual Band AP Radio - Disable WLAN Service'
    param_cfg = {'ap_tag': 'AP3', 'cfg_type': 'config', 'ap_cfg': {'wlan_service': False}}
    test_cfgs.append((param_cfg, test_name, common_name, 0, False))
    
    test_case_name = '[Mesh Enable - Move one mesh AP between two root APs] '
          
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up' % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status via ZD WebUI' % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
        
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sRoot AP becomes Mesh with mesh ACL for the first time' % test_case_name
    param_cfg = {'root_ap': 'AP2',
                 'mesh_ap': 'AP4', 
                 'test_option': 'form_mesh_mesh_acl'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default group are up after it becomes Mesh AP for the first time' % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status after it becomes Mesh AP for the second time' % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sRoot AP becomes Mesh with mesh ACL for the second time' % test_case_name
    param_cfg = {'root_ap': 'AP3',
                 'mesh_ap': 'AP4', 
                 'test_option': 'form_mesh_mesh_acl'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up after it changes the uplink'  % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status after it changes the uplink'% test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with each wlan after Mesh AP changes uplink AP'% test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in [0,2,4]]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from  station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sReconnect the Mesh AP as Root at cleanup' % test_case_name
    param_cfg = {'ap_list': ['AP4'],
                 'test_option': 'reconnect_as_root'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))

#---------------18.Mesh Enable - Move mesh AP between one hop mesh AP and one root AP-----------------
    test_case_name = '[Mesh Enable-Move mesh AP between one hop mesh AP and one root AP] '
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sSetting up a 2 hops eMesh network' % test_case_name
    param_cfg = {'root_ap': 'AP2',
                   'mesh_ap': 'AP3',
                   'emesh_ap': 'AP4',
                   'test_option': 'form_emesh_mesh_acl'}
    test_cfgs.append((param_cfg, test_name, common_name, 1, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up after it becomes eMesh AP' % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status after it becomes eMesh AP' % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}
                 }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Configure_AP_Mesh'
    common_name = '%sConfigure the uplink of third dual band AP to the first' % test_case_name
    param_cfg = {'ap_tag': 'AP4',
                 'mesh_cfg': {'mesh_mode':'auto',
                              'uplink_option': {'uplink_mode': 'manual',
                                                'uplink_aps': [tcfg['firstdualbandAPMac']]}
                                }
                }
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sMesh AP becomes root AP' % test_case_name
    param_cfg = {'ap_list': ['AP3'],
                 'test_option': 'reconnect_as_root'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_Status'
    common_name = '%seMesh AP becomes Mesh AP with 1 hop' % test_case_name
    param_cfg = {'ap_tag':'AP4',
                 'status': 'Connected (Mesh AP, 1 hop)',
                 'uplink_ap': tcfg['firstdualbandAPMac']}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Wlan_Status_In_AP'
    common_name = '%sVerify wlans in default wlan group are up after it becomes Mesh'  % test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr'
    common_name = '%sVerify wlan group and wlan status after it becomes Mesh'% test_case_name
    param_cfg = {'ap_tag': 'AP4', 
                 'wlan_group':{'na': 'Default','ng':'Default'},
                 'up':{'5g': tcfg['wgs_cfg_list']['wlan_bgn_grp6'],
                       '24g': tcfg['wgs_cfg_list']['wlan_bgn_grp6']}}
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_With_Wlans'
    common_name = '%sVerify station can associate with each wlan after it becomes Mesh' % test_case_name   
    param_cfg = {'sta_tag': sta_tag, 
                 'wlans_cfg_list':[tcfg['wlan_cfg_list'][i] for i in [1,3,5]]}  
    test_cfgs.append((param_cfg, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sRemove all wlans from the station at cleanup' % test_case_name
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_Mesh_Provisioning'
    common_name = '%sReconnect the Mesh AP as Root at cleanup' % test_case_name
    param_cfg = {'ap_list': ['AP3','AP4'],
                 'test_option': 'reconnect_as_root'}
    test_cfgs.append((param_cfg, test_name, common_name, 2, True))
#-----------------------------------------cleanup-------------------------------------------------------------
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all wlans from the station at cleanup'
    param_cfg = {'sta_tag': sta_tag}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_AP_Groups'
    common_name = 'Remove All AP Groups at cleanup'
    param_cfg = {}
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlan_Groups'
    common_name = 'Remove all wlan groups at cleanup'
    param_cfg = {}   
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all wlans from ZD at cleanup'
    param_cfg = {}   
    test_cfgs.append((param_cfg, test_name, common_name, 0, True))
    
    return test_cfgs


def define_apgroup_cfg():   
    apgroup_cfg = {'apg_prefix_name':'AP_group',
                    'an_wg_prefix_name': 'wlan_na_grp',
                    'gn_wg_prefix_name': 'wlan_bgn_grp',
                    'an': {'channel': '36',
                           'channelization': '20',
                           'mode': 'Auto',
                           'tx_power': 'Full',
                           },
                    'gn': {'channel': '11',
                            'channelization': '40',
                            'mode': 'N/AC-only',
                            'tx_power': '-1dB',
                          },
                  }

    return apgroup_cfg

def define_wlangroup_cfg(wlan_cfgs):
    wlangroup_cfg = {}
    wlangroup_cfg['wlan_grp0'] = []
    
    wlangroup_cfg['wlan_bgn_grp1'] = [wlan_cfgs[0]['ssid']]    
    wlangroup_cfg['wlan_bgn_grp2'] = [wlan_cfgs[i]['ssid'] for i in range(0, 2)]
    wlangroup_cfg['wlan_bgn_grp3'] = [wlan_cfgs[i]['ssid'] for i in range(0, 3)]
    wlangroup_cfg['wlan_bgn_grp4'] = [wlan_cfgs[i]['ssid'] for i in range(0, 4)]
    wlangroup_cfg['wlan_bgn_grp5'] = [wlan_cfgs[i]['ssid'] for i in range(0, 5)]    
    wlangroup_cfg['wlan_bgn_grp6'] = [wlan_cfgs[i]['ssid'] for i in range(0, 6)]
    
    wlangroup_cfg['wlan_na_grp1'] = [wlan_cfgs[6]['ssid']]    
    wlangroup_cfg['wlan_na_grp2'] = [wlan_cfgs[i]['ssid'] for i in range(6, 8)]
    wlangroup_cfg['wlan_na_grp3'] = [wlan_cfgs[i]['ssid'] for i in range(6, 9)]
    wlangroup_cfg['wlan_na_grp4'] = [wlan_cfgs[i]['ssid'] for i in range(6, 10)]
    wlangroup_cfg['wlan_na_grp5'] = [wlan_cfgs[i]['ssid'] for i in range(6, 11)]    
    wlangroup_cfg['wlan_na_grp6'] = [wlan_cfgs[i]['ssid'] for i in range(6, 12)]
    
    return wlangroup_cfg

def define_wlan_cfg():
    wlan_cfgs = []
    for i in range(1, 13):                          
        wlan_cfgs.append(dict(ssid="openWlanZ%d" % i, auth="open", wpa_ver="", encryption="none",
                           sta_auth="open", sta_wpa_ver="", sta_encryption="none",
                           key_index="" , key_string=""))   
    return wlan_cfgs   
    
def define_test_parameters(target_station, aps_to_be_tested, singlebandAP_radio, firstdualbandAPMac, wlan_cfg_list, wlangroup_cfg, apgroup_cfg):
     
    singlebandAPtestcfg = {}
    singlebandAPtestcfg['radio'] = singlebandAP_radio
    if singlebandAP_radio == 'na':
        singlebandAPtestcfg['wlangrp_pre'] = 'wlan_na_grp'
    else:
        singlebandAPtestcfg['wlangrp_pre'] = 'wlan_bgn_grp'
        
    tcfg = {'target_station':'%s' % target_station,
            'aps_to_be_tested': aps_to_be_tested,
            'singlebandAPtestcfg': singlebandAPtestcfg,
            'firstdualbandAPMac': firstdualbandAPMac,
            'wlan_cfg_list': wlan_cfg_list,
            'wgs_cfg_list': wlangroup_cfg,
            'apgroup_cfg': apgroup_cfg,
            }
    
    return tcfg

def get_aps_from_user_input(ap_sym_dict, expected_aps):
    ap_info_list = ap_sym_dict.copy()
       
    for param in input_seq:
        if not param in expected_aps.keys():
            continue
        
        for ap in sorted(ap_info_list):
            print ap, ap_info_list[ap]
            
        if type(expected_aps[param]) is list:
            msg = 'Please select %s, separated by space/[ALL] to select all/[ENTER] to pass: '
            msg = msg % param.upper().replace('_', ' ')
            rinput = raw_input(msg).lower().strip().split()
            if not rinput:
                continue      
            if 'all' in rinput:
                expected_aps[param] = ap_info_list.keys()
                ap_info_list = {}
                continue               
            for ap in rinput:
                if ap in ap_info_list.keys():
                    expected_aps[param].append(ap)
                    del ap_info_list[ap]
        else:
            msg = 'Please select %s: ' % param.upper().replace('_', ' ')
            rinput = raw_input(msg).strip()
            expected_aps[param] = rinput
            del ap_info_list[rinput]

    return expected_aps

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 150:
            raise Exception('common_name[%s] in case [%s] is too long, more than 150 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')


def create_test_suite(**kwargs):
	    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
        
    wlan_cfg_list = define_wlan_cfg()
    wlangroup_cfg = define_wlangroup_cfg(wlan_cfg_list)
    apgroup_cfg = define_apgroup_cfg()
    
    print 'Please configure the APs to be tested(please select the current root aps only):'
    ap_to_be_tested_conf = {'single_band_ap': '',
    	             'dual_band_ap1': '',
                     'dual_band_ap2': '',
                     'dual_band_ap3': '', }
    aps_to_be_tested = get_aps_from_user_input(ap_sym_dict, ap_to_be_tested_conf)
    
    single_band_ap_model = ap_sym_dict[aps_to_be_tested['single_band_ap']]['model']
    
    single_band_ap_radiolist = libCons._ap_model_info[single_band_ap_model.lower()]['radios']
    
    if len(single_band_ap_radiolist)>1:
        raise Exception("the single band AP configured is not single band")
    
    radio = single_band_ap_radiolist[0]
    firstdualbandAPMac = str(ap_sym_dict[aps_to_be_tested['dual_band_ap1']]['mac'])
    #ts_name = 'Not Removing WLANs---mesh enabled'
    #ts = testsuite.get_testsuite(ts_name, 'Not removing WLANs with mesh enabled', combotest=True)
    sta_ip_addr = target_sta_01 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station 1: ")            
    tcfg = define_test_parameters(sta_ip_addr, aps_to_be_tested, radio, firstdualbandAPMac, wlan_cfg_list, wlangroup_cfg, apgroup_cfg)         
    
    ts_name_list = [('Xian Not Removing Wlans-Mesh Enable-Singleband', define_test_cfg_for_singleband),
                    ('Xian Not Removing Wlans-Mesh Enable-Dualband', define_test_cfg_for_dualband),
                    ('Xian Not Removing Wlans-Mesh Enable-Mesh', define_test_cfg_for_mesh),                    
                    ]
    
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(tcfg)
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
    
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
    create_test_suite(**_dict)
    
