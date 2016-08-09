'''
Created on 2013-8-5
@author: cwang@ruckuswireless.com
'''
import time
import sys
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant

def define_wlan_cfg():    
    wlan_cfg = dict(ssid = "RAT-WLAN-statistic-%s" % (time.strftime("%H%M%S")),
                    auth = "open", wpa_ver = "", encryption = "none",
                    key_index = "" , key_string = "",
                    username = "", password = "", auth_svr = "", 
                    web_auth = None, do_service_schedule=None,)    
    return wlan_cfg

#ZD-28924:Both AP->sum of VAPs and radio stats 
#should be reset when AP rejoins ZD after heartbeat loss
#def _test_sum_vap(cfg):
#    target_station = cfg['target_station']
#    all_aps_mac_list = cfg['all_aps_mac_list']
#    ap_radio = cfg['ap_radio']
#    active_ap = cfg['active_ap']
#    wlan_cfg = define_wlan_cfg() 
#    tcs = []
#    tcs.append(({},
#                'CB_ZD_Remove_All_Wlans',
#                'Remove All WLANs',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_ZD_Get_AP_Info',
#                'Get AP information from AP monitor.',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_ZD_Pull_XML_File',
#                'Pull data from ZD interface.',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_ZD_Verify_Data_Indices',
#                '[Compare XML and GUI w/o WLANs]verify indices xml attribute',
#                1,
#                False
#                ))
#       
#    tcs.append((dict(wlan_cfg_list=[wlan_cfg]),
#                'CB_ZD_Create_Wlans',
#                'Create WLANs',
#                0,
#                False
#                ))
#    tc_name = "[Compare XML and GUI with WLANs]"    
#    tcs.extend(_build_sta_tcs(wlan_cfg, 
#                              target_station, 
#                              tc_name,
#                              all_aps_mac_list,
#                              ap_radio,
#                              active_ap
#                              ))
#    
#    tcs.append(({},
#                'CB_ZD_Get_AP_Info',
#                '%sGet AP information after auth.' % tc_name,
#                0,
#                False
#                ))
#    tcs.append(({},
#                'CB_ZD_Pull_XML_File',
#                '%sPull data from ZD interface after auth.' % tc_name,
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_ZD_Verify_Data_Indices',
#                '%sverify indices xml attribute' % tc_name,
#                1,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_ZD_Reboot',
#                'Reboot ZD',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#               'CB_Statistic_Pull_XML_Next',
#               'Pull data from ZD interface after reboot',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_Statistic_Compare_XML_Next',
#                '[Compare XML LAST and CUR DATA]verify xml pre and next.',
#                1,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_ZD_Remove_All_Wlans',
#                'Remove all of WLANs after testing.',
#                0,
#                True,
#                ))
#    return tcs

#ZD-28919:Enhance ZD to support AP heartbeat loss 
#and reboot counters-MAP sole-run reboot
#Tested by ats_ZD_Mesh_Recovery_SSID_Testing.py
#def _test_counters_map_reboot(cfg):
#    tcs = []
#    tcs.append(({},
#                'CB_ZD_Pull_XML_File',
#                'Pull ZD xml file with python script',
#                0,
#                False
#                ))
#    tcs.append(({},
#               'CB_AP_Set_Auto_Recovery',
#               "Set auto recovery interval to 10 min",
#               0,
#               False
#               ))
#    tcs.append(({},
#               'CB_AP_Shutdown_Port',
#               "Power down the MAP's RAP that make MAP lost connect with RAP",               
#               0,
#               False
#               ))
#    tcs.append(({},
#               'CB_AP_Wait_For',
#               "MAP reboots when lost connect with RAP for 10 mins",
#               0,
#               False
#               ))
#    tcs.append(({},
#                'CB_AP_Startup_Port',
#                'Power on RAP to let MAP rejoin to ZD',
#                0,
#                False
#               ))
#    
#    tcs.append(({},
#                'CB_Statistic_Pull_XML_Next',
#                'Pull ZD xml file then write down step2 listed attributes value',
#                0,
#                False
#                ))
#    tcs.append(({},
#                'CB_Statistic_Compare_XML_Next',
#                '[ZD-28919]reboot counters-MAP',
#                1,
#                False
#                ))
#    
#    return tcs


#ZD-28917:Enhance ZD to support AP heartbeat
#loss and reboot counters-AP watchdog timeout
def _test_watchdog_time(cfg):
    tcs = []
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    active_ap = cfg['active_ap']
    tcs.append(({'active_ap':active_ap,
                 'ap_tag':active_ap,
                 },
                'CB_ZD_Create_Active_AP',
                'Find an active AP.',
                0,
                False
                ))
    
    tcs.append(({'ap_tag':active_ap},
                'CB_AP_Generate_Big_Tmp_File',
                'Upload file to AP that make it occupy all AP memory',
                0,
                False
                ))
    
    tcs.append(({'ap_tag':active_ap},
                'CB_ZD_Verify_AP_Status',
                'Wait for AP re-join',
                0,
                False
                ))
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Test to wait for trigger.',
                0,
                False
                ))    
    
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file again after AP rejoins to ZD',
                0,
                False
                ))
    
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('watchdog')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                          'testaps':[cfg['ap_sym_dict'][active_ap]['mac']],
                         'sys':{'total-hb-loss':1,#+1 per AP.
                                 'hb-loss-day':1,#+1 per AP.
                                 'ap-reboot-day':1,#+1 per AP.
                                 'total-ap-reboot':1#+1 per AP.
                                 }                               
                        }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28917]reboot counters-AP watchdog timeout',
                1,
                False
                )) 
    
    return tcs

#ZD-28916:Enhance ZD to support AP heartbeat loss 
#and reboot counters-Enable DFS channel under US countrycode
def _test_dfs_us(cfg):
    tcs = []
    tcs.append((dict(cc='US',
                     option='compatibility'
                     ),
                'CB_ZD_CLI_Config_DFS',
                'Initialize AP DFS channel as US-->compatibility',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Make sure all of APs are connected.',
                0,
                False
                )) 

    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
        
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    
    tcs.append((dict(cc='US',
                     option='performance'
                     ),
                'CB_ZD_CLI_Config_DFS',
                'Enable AP DFS channel under US countrycode',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join after DFS change == > performance',
                0,
                False
                ))    
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Pause for 90 seconds, wait for statistic reporting trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull XML data after AP re-join',
                0,
                False
                ))
        
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('application')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                         'sys':{'total-hb-loss':0,#+0
                                 'hb-loss-day':0,#+0,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 }                               
                               }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28916]XML attribute verify',
                1,
                False
                ))
    
    tcs.append((dict(cc='US',
                     option='compatibility'
                     ),
                'CB_ZD_CLI_Config_DFS',
                'Restore AP DFS channel under US countrycode',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join after DFS change to compatibility',
                0,
                True
                ))  
    
    return tcs

#ZD-28913:Enhance ZD to support AP heartbeat loss 
#and reboot counters-Change AP mgmt vlan
def _test_ap_mgmt_vlan(cfg):
    tcs = []
    tcs.append(({'vlan_id' : '302'},
                'CB_ZD_CLI_Enable_AP_MgmtVlan',
                'Initialize AP management VLAN from ZD CLI',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Make sure all of APs are connected',
                0,
                False
                ))

    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
        
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    
    tcs.append(({'vlan_id' : '1'},
                'CB_ZD_CLI_Enable_AP_MgmtVlan',
                'Change AP management vlan from ZD CLI',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join after update zd mgmt to VLAN#1',
                0,
                False
                ))
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Pause for 90 seconds, wait for statistic reporting trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file when AP rejoin ZD after mgmt vlan change',
                0,
                False
                ))
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('application')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                          'sys':{'total-hb-loss':0,#+0
                                 'hb-loss-day':0,#+0,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 }
                               }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28913]XML attribute verify',
                1,
                False
                ))

    tcs.append(({'vlan_id' : '302'},
                'CB_ZD_CLI_Enable_AP_MgmtVlan',
                'Restore AP management VLAN from ZD CLI',
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join after mgmt vlan change to VLAN#302',
                0,
                True
                ))
       
    return tcs




def get_reboot_chkkeys(key='user'):
    return {'user':([('user-reboot-counter', 1)],
                    ['application-reboot-counter',
                     'reset-button-reboot-counter',
                     'kernel-panic-reboot-counter',
                     'watchdog-reboot-counter',
                     'powercycle-reboot-counter'],
                    []
                    ),
            'application':([('application-reboot-counter', 1)],
                            ['user-reboot-counter',
                             'reset-button-reboot-counter',
                             'kernel-panic-reboot-counter',
                             'watchdog-reboot-counter',
                             'powercycle-reboot-counter'],
                            []
                            ),
            'reset':([('reset-button-reboot-counter', 1)],
                    ['user-reboot-counter',
                     'application-reboot-counter',
                     'kernel-panic-reboot-counter',
                     'watchdog-reboot-counter',
                     'powercycle-reboot-counter'],
                    []
                    ), 
            'kernel':([('kernel-reboot-counter', 1)],
                    ['user-reboot-counter',
                     'application-reboot-counter',
                     'reset-button-reboot-counter',
                     'watchdog-reboot-counter',
                     'powercycle-reboot-counter'],
                    []
                    ),
            'watchdog':([('watchdog-reboot-counter', 1)],
                    ['user-reboot-counter',
                     'application-reboot-counter',
                     'reset-button-reboot-counter',
                     'kernel-panic-reboot-counter',
                     'powercycle-reboot-counter'],
                    []
                    ), 
            'powercycle':([('powercycle-reboot-counter', 1)],
                    ['user-reboot-counter',
                     'application-reboot-counter',
                     'reset-button-reboot-counter',
                     'kernel-panic-reboot-counter',
                     'watchdog-reboot-counter'],
                    []
                    ), 
            'delete':([('application-reboot-counter', 1)],                         
                            [],
                            ['user-reboot-counter',
                             'reset-button-reboot-counter',
                             'kernel-panic-reboot-counter',
                             'watchdog-reboot-counter',
                             'powercycle-reboot-counter'],                            
                            ),                                                                                                   
                    }[key]
# ZD-28912:Enhance ZD to support AP heartbeat loss 
# and reboot counters-Change AP ip mode
def _test_ap_ip_mode(cfg):
    tcs = []
    tcs.append(({'network_setting': {'ip_version': lib_Constant.IPV4}},
                'CB_ZD_CLI_Config_APs_IPmode',
                'initialize all of APs mode to %s' % lib_Constant.IPV4,
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Make sure all of AP are connected.',
                0,
                False
                ))     
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    
    tcs.append(({'network_setting': {'ip_version': lib_Constant.DUAL_STACK}},
                'CB_ZD_CLI_Config_APs_IPmode',
                'Change all of APs mode to %s' % lib_Constant.DUAL_STACK,
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join',
                0,
                False
                ))   
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Test to wait for trigger.',
                0,
                False
                ))    
         
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file when AP rejoin ZD after ip mode change',
                0,
                False
                ))
    
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('application')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                         'sys':{'total-hb-loss':0,#+0
                                 'hb-loss-day':0,#+0,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 }                               
                               }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28912]XML attribute verify',
                1,
                False
                )) 
    
    tcs.append(({'network_setting': {'ip_version': lib_Constant.IPV4}},
                'CB_ZD_CLI_Config_APs_IPmode',
                'Restore all of APs mode to %s' % lib_Constant.IPV4,
                0,
                True
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Check for all AP re-join',
                0,
                True
                )) 
           
    return tcs

#ZD-28911:Enhance ZD to support AP heartbeat loss 
#and reboot counters-Band switch on 7321
#def _test_band_switch(cfg):
#    tcs = []
#    tcs.append(({},
#                'CB_ZD_Pull_XML_File',
#                'Pull ZD xml file with python script',
#                0,
#                False
#                ))
#    tcs.append(({},
#                'CB_ZD_CLI_Change_AP_RadioBand',
#                'Switch 7321 radio to another band(2.4G->5G/5G->2.4G)',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_Statistic_Pull_XML_Next',
#                'Pull ZD xml file when 7321 rejoin ZD after band switch',
#                0,
#                False
#                ))
#    
#    tcs.append(({},
#                'CB_Statistic_Compare_XML_Next',
#                '[ZD-28911]XML attribute verify',
#                1,
#                False
#                ))
#    return tcs

#ZD-28909:Enhance ZD to support AP heartbeat loss 
#and reboot counters-delete AP from ZD GUI
def _test_delete_all_ap_from_zdcli(cfg):
    tcs = []
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    tcs.append(({},
                'CB_ZD_CLI_Delete_All_AP',
                'Delete all connected AP from ZD CLI',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join',
                0,
                False
                ))
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Pause for 90 seconds, wait for statistic reporting trigger.',
                0,
                False
                ))
        
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file when AP rejoin ZD after being deleted',
                0,
                False
                ))
    
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('delete')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                         'sys':{'total-hb-loss':0,#+0
                                 'hb-loss-day':0,#+0,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 },                                                           
                               },
                 'action':'delete'
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28909]XML attribute verify',
                1,
                False
                ))
    return tcs
#ZD-28907:Enhance ZD to support AP heartbeat loss 
#and reboot counters-Reboot ap via AP CLI
def _test_reboot_from_ap_cli(cfg):
    tcs = []
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_AP_CLI_Reboot_All_AP',
                'Reboot all AP via AP CLI',
                0,
                False
                ))
    
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join after reboot from AP',
                0,
                False
                ))
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Pause for 90 seconds, wait for statistic reporting trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file when AP rejoin to ZD after reboot',
                0,
                False
                ))
    
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('user')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                         'sys':{'total-hb-loss':1,#+1 per AP,
                                 'hb-loss-day':1,#+1 per AP,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 }                                    
                               }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28907]XML attribute verify',
                1,
                False
                ))
    return tcs
#ZD-28906:Enhance ZD to support AP heartbeat loss 
#and reboot counters-Reboot ap via ZD GUI
def _test_reboot_from_zd_cli(cfg):
    tcs = []
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    tcs.append(({},
                'CB_ZD_CLI_Reboot_All_AP',
                'Reboot all AP from ZD CLI via remote_ap_cli.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_ZD_Verify_All_AP_Join',
                'Wait for all AP re-join after reboot from ZD',
                0,
                False
                ))    
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Pause for 90 seconds, wait for statistic reporting trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file when AP rejoin to ZD after reboot',
                0,
                False
                ))
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('user')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                         'sys':{'total-hb-loss':1,#+1
                                 'hb-loss-day':1,#+1,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 }                                    
                               }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28906]XML attribute verify',
                1,
                False
                ))
    return tcs
#ZD-28904:Enhance ZD to support AP heartbeat loss 
#and reboot counters-Change AP country code
def _test_change_country_code(cfg):
    tcs = []
    tcs.append(({'cc':'US',
                 'ccalias':'United States', 
                 'chk_ap':True                
                 },
                'CB_ZD_CLI_Set_AP_CountryCode',
                'Initialize AP CountryCode',
                0,
                False
                )) 
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Initialize to wait for trigger.',
                0,
                False
                ))    
    
    tcs.append(({},
                'CB_ZD_Pull_XML_File',
                'Pull ZD xml file with python script',
                0,
                False
                ))
    tcs.append(({'cc':'FR',
                 'ccalias':'France', 
                 'chk_ap':True                
                 },
                'CB_ZD_CLI_Set_AP_CountryCode',
                'Update CountryCode',
                0,
                False
                ))
    
    tcs.append(({'timeout':90},
                'CB_AP_Wait_For',
                'Pause for 90 seconds, wait for statistic reporting trigger.',
                0,
                False
                ))
    
    tcs.append(({},
                'CB_Statistic_Pull_XML_Next',
                'Pull ZD xml file when AP rejoin to ZD after reboot',
                0,
                False
                ))
    
    (incrkeys, keepkeys, zerokeys) = get_reboot_chkkeys('application')
    tcs.append(({'func':'_test_reboot_counter',
                 'args':{'ap':{'incrkeys':incrkeys,
                               'keepkeys':keepkeys,
                               'zerokeys':zerokeys,
                               },
                         'sys':{'total-hb-loss':0,#+0
                                 'hb-loss-day':0,#+0,
                                 'ap-reboot-day':1,#+1 per AP,
                                 'total-ap-reboot':1#+1 per AP
                                 }                                    
                               }
                 },
                'CB_Statistic_Compare_XML_Next',
                '[ZD-28904]XML attribute verify',
                1,
                False
                ))
    
    tcs.append(({'cc':'US',
                 'ccalias':'United States', 
                 'chk_ap':True                
                 },
                'CB_ZD_CLI_Set_AP_CountryCode',
                'Restore CountryCode',
                0,
                True
                ))    
    return tcs

def _build_sta_tcs(wlan_cfg, target_station, 
                   tc_name, all_aps_mac_list = None, 
                   ap_radio = None, active_ap = None):

    tcs = []
    tcs.append(({'sta_tag': 'sta_1', 
                   'sta_ip_addr': target_station}, 
                   'CB_ZD_Create_Station', 
                   '%sGet the station' % tc_name, 
                   0, 
                   False))    
    if active_ap:        
        tcs.append(({'active_ap':active_ap,
                     'ap_tag':'active_ap'},                                        
                    'CB_ZD_Create_Active_AP',
                    '%sFind the Active AP' % tc_name,
                    1,
                    False
                    ))
        
        tcs.append(({
                     'cfg_type': 'init', 
                     'all_ap_mac_list': all_aps_mac_list}, 
                     'CB_ZD_Config_AP_Radio', 
                     '%sDisable WLAN Service' % tc_name, 
                     2, 
                     False))
        
       
        tcs.append(({'ap_tag': 'active_ap',                      
                     'cfg_type': 'config',
                     'ap_cfg': {'wlan_service': True, 'radio': ap_radio}},
                     'CB_ZD_Config_AP_Radio',
                     '%sEnable WLAN Service' % tc_name,
                     2, 
                     False
                    ))
    else:
        tcs.append(({'cfg_type': 'teardown', 
                     'all_ap_mac_list': all_aps_mac_list}, 
                     'CB_ZD_Config_AP_Radio', 
                     '%sReset all WLAN Services' % tc_name, 
                     1, 
                     False))
          
    tcs.append(({'sta_tag': 'sta_1', 
                 'wlan_cfg': wlan_cfg}, 
                 'CB_ZD_Associate_Station_1', 
                  '%sAssociate the station' % tc_name, 
                  2, 
                  False))    

    
    tcs.append(({'sta_tag': 'sta_1'}, 
                  'CB_ZD_Get_Station_Wifi_Addr_1', 
                  '%sGet wifi address' % tc_name, 
                  2, 
                  False))          
    return tcs
    

def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,                                  
                 testsuite_name = "Statistic Reporting-Basic",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    
    if attrs["interactive_mode"]:        
        sta_ip_addr = testsuite.getTargetStation(sta_ip_list, 
                                                 "Choose an wireless station: ")
        target_sta_radio = testsuite.get_target_sta_radio()        
    else:
        ts_name = attrs["testsuite_name"]
        sta_ip_addr = sta_ip_list[attrs["target_station"][0]]
        target_sta_radio = attrs["target_station"][1]
    
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    
    active_ap = None    
    for ap_sym_name, ap_info in ap_sym_dict.items():
        ap_support_radio_list = lib_Constant._ap_model_info[ap_info['model'].lower()]['radios']
        if target_sta_radio in ap_support_radio_list:
            active_ap = ap_sym_name            
            break
    
    
    if not active_ap:
        raise Exception("Have't found any valid AP in test bed can support station radio %s" % target_sta_radio)
    
    
    ts_name_list = [
#                    ("AP radio and sum of VAP counters after AP HB lost", _test_sum_vap), 
#                    ('AP HB loss and RB counter when MAP RB due to enter sole-run for a period', _test_counters_map_reboot),
                    ('AP HB loss and RB counter when AP watchdog timeout', _test_watchdog_time),
                    ('AP HB loss and RB counter when enable AP DFS under US Country', _test_dfs_us),
                    ('AP HB loss and RB counter when changing AP mgmt vlan', _test_ap_mgmt_vlan),
                    ('AP HB loss and RB counter when changing AP ip mode',_test_ap_ip_mode),
#                    ('AP HB loss and RB counter when changing band switch radio',_test_band_switch),
                    ('AP HB loss and RB counter if deleting AP from ZD', _test_delete_all_ap_from_zdcli), 
                    ('AP HB loss and RB counter if reboot AP via AP',_test_reboot_from_ap_cli),
                    ('AP HB loss and RB counters if reboot ap via ZD',_test_reboot_from_zd_cli),
                    ('AP HB loss and RB counters when changing AP country code',_test_change_country_code),                                                                          
                    ]
    cfg = {}
    cfg['target_station'] = sta_ip_addr
    cfg['all_aps_mac_list'] = tbcfg['ap_mac_list']
    cfg['ap_radio'] = target_sta_radio
    cfg['active_ap'] = active_ap
    cfg['ap_sym_dict'] = ap_sym_dict
        
    for ts_name, fn in ts_name_list:
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        test_cfgs = fn(cfg)
    
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name) 
            
def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) >120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')
        
          
if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)