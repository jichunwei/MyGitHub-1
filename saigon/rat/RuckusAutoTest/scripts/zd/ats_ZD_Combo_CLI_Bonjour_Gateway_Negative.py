'''
Created on Mar 25, 2014

@author: lab
'''
import sys
import time
from copy import deepcopy

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils

def define_test_cfg(cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode'] 
    do_tunnel =cfg['enable_tunnel']
    sta_radio_mode = radio_mode

    ap_tag = 'ap%s' % radio_mode

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs'
    test_cfgs.append(({}, test_name, common_name, 0, False)) 

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station1'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station1'],
                       'sta_tag': 'sta1'}, test_name, common_name, 0, False))

    test_name = 'CB_SW_Add_Port_To_Isolate_Group'
    common_name = 'Add station1 to port isolate group 1'
    test_cfgs.append(({'tag': 'sta1','group_id':'1'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station2'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station2'],
                       'sta_tag': 'sta2'}, test_name, common_name, 0, False))

    test_name = 'CB_SW_Add_Port_To_Isolate_Group'
    common_name = 'Add station2 to port isolate group 1'
    test_cfgs.append(({'tag': 'sta2','group_id':'1'}, test_name, common_name, 0, False))

    test_name = 'CB_SW_Add_Port_To_Isolate_Group'
    common_name = 'Add ZD to port isolate group 1'
    test_cfgs.append(({'group_id':'1'}, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station1'
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 0, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove all WlANs from station2'
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = 'Delete all rules.'
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Disable_Bonjour_Gateway'
    common_name = 'Disable bonjour gateway.'
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 0, False)) 
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = 'Check bonjour gateway is disabled.'
    test_params = {'bonjour_gw_value':'disabled'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))    
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Disable WLAN Service'
    test_params = {'cfg_type': 'init',
                   'all_ap_mac_list': cfg['all_ap_mac_list'],}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config active AP Radio %s - Enable WLAN Service' % (radio_mode)
    test_params = {'cfg_type': 'config',
                   'ap_tag': ap_tag,
                   'ap_cfg': {'radio': radio_mode, 'wlan_service': True},
                   }
    test_cfgs.append((test_params, test_name, common_name, 0, False))



#testcase 1
    test_case_name = '[Reboot all APs]'
    
    wlan_cfg_vlan10 = {'ssid': 'Bonjour_Gateway_VLAN10','auth': 'open','encryption': 'none',
                       'type': 'standard','vlan_id': 10, 'do_tunnel': do_tunnel 
                      }
    wlan_cfg_vlan20 = {'ssid': 'Bonjour_Gateway_VLAN20','auth': 'open','encryption': 'none',
                       'type': 'standard','vlan_id': 20, 'do_tunnel': do_tunnel 
                       }
    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate VLAN10 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg_vlan10]}, test_name, common_name, 1, False))

    common_name = '%sCreate VLAN20 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg_vlan20]}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station1 to the VLAN10 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan10,
                       'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station1 status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan10,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station2 to the VLAN20 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan20,
                       'sta_tag': 'sta2'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station2 status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan20,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    #test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '%sAdd a bonjour gateway rule.'% (test_case_name)
    test_params = {'tag_new':True,'service':'AirPlay', 'from_vlan':10, 'to_vlan':20}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Enable_Bonjour_Gateway'
    common_name = '%sTurn on bonjour gateway.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '%sCheck value is enabled'% (test_case_name)
    test_params = {'bonjour_gw_value':'enabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))     

    test_name = 'CB_Station_Register_Bonjour_Service'
    common_name = '%s Register bonjour services on station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1','service_name':'AirPlay'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Browse_Bonjour_Service'
    common_name = '%s Browse bonjour services on station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2','service_name':'AirPlay'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'proc_name': 'dns-sd'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2', 'proc_name': 'dns-sd'}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, False))
#Reboot APs
    
    test_name = 'CB_ZD_Reboot_APs'
    common_name = '%s Reboot all APs' % (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station1 to the VLAN10 WLAN again'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan10,
                       'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station1 status in ZD again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan10,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station2 to the VLAN20 WLAN again'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan20,
                       'sta_tag': 'sta2'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station2 status in ZD again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan20,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Register_Bonjour_Service'
    common_name = '%s Register bonjour services on station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1','service_name':'AirPlay'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Browse_Bonjour_Service'
    common_name = '%s Browse bonjour services on station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2','tag_null':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'proc_name': 'dns-sd'}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2', 'proc_name': 'dns-sd'}, test_name, common_name, 2, True)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs from ZD for the next test'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '%sDelete all rules.'% (test_case_name)
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Disable_Bonjour_Gateway'
    common_name = '%sDisable bonjour gateway.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))    
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '%sCheck bonjour gateway is disabled.'% (test_case_name)
    test_params = {'bonjour_gw_value':'disabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 
#testcase 2
    test_case_name = '[Reboot ZD]'

    test_name = 'CB_ZD_Create_Wlan'
    common_name = '%sCreate VLAN10 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg_vlan10]}, test_name, common_name, 1, False))

    common_name = '%sCreate VLAN20 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg_list':[wlan_cfg_vlan20]}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station1 to the VLAN10 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan10,
                       'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station1 status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan10,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station2 to the VLAN20 WLAN'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan20,
                       'sta_tag': 'sta2'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station2 status in ZD'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan20,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    #test_cfgs.extend(test_process(test_case_name,choice,is_negative,cfg_dict))
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '%sAdd a bonjour gateway rule.'% (test_case_name)
    test_params = {'tag_new':True,'service':'AirPlay', 'from_vlan':10, 'to_vlan':20}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_CLI_Enable_Bonjour_Gateway'
    common_name = '%sTurn on bonjour gateway.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '%sCheck value is enabled'% (test_case_name)
    test_params = {'bonjour_gw_value':'enabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, False))     

    test_name = 'CB_Station_Register_Bonjour_Service'
    common_name = '%s Register bonjour services on station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1','service_name':'AirPlay'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Browse_Bonjour_Service'
    common_name = '%s Browse bonjour services on station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2','service_name':'AirPlay'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'proc_name': 'dns-sd'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2', 'proc_name': 'dns-sd'}, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station1'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station2'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, False))
#Reboot ZD

    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%sReboot zd from zdcli'% (test_case_name)
    test_cfgs.append(( {'timeout':10*60}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station1 to the VLAN10 WLAN again'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan10,
                       'sta_tag': 'sta1'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station1 status in ZD again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan10,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Associate_Station_1'
    common_name = '%sAssociate station2 to the VLAN20 WLAN again'% (test_case_name)
    test_cfgs.append(({'wlan_cfg': wlan_cfg_vlan20,
                       'sta_tag': 'sta2'}, test_name, common_name, 2, False))

    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Verify_Station_Info_V2'
    common_name = '%sVerify station2 status in ZD again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2',
                       'ap_tag': ap_tag,
                       'status': 'Authorized',
                       'wlan_cfg': wlan_cfg_vlan20,
                       'radio_mode':sta_radio_mode,},
                       test_name, common_name, 2, False))

    test_name = 'CB_Station_Register_Bonjour_Service'
    common_name = '%s Register bonjour services on station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1','service_name':'AirPlay'}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Browse_Bonjour_Service'
    common_name = '%s Browse bonjour services on station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2','tag_null':True}, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1', 'proc_name': 'dns-sd'}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Kill_Bonjour_Service'
    common_name = '%s Kill dns-sd on station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2', 'proc_name': 'dns-sd'}, test_name, common_name, 2, True)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station1 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta1'}, test_name, common_name, 2, True))

    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%s Remove all WlANs from station2 again'% (test_case_name)
    test_cfgs.append(({'sta_tag': 'sta2'}, test_name, common_name, 2, True))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = '%sRemove all the WLANs from ZD for the next test'% (test_case_name)
    test_cfgs.append(({}, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Config_Services_Rule'
    common_name = '%sDelete all rules.'% (test_case_name)
    test_params = {'tag_del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True))
    
    test_name = 'CB_ZD_CLI_Disable_Bonjour_Gateway'
    common_name = '%sDisable bonjour gateway.'% (test_case_name)
    test_params = {}
    test_cfgs.append((test_params,test_name, common_name, 2, True))    
    
    test_name = 'CB_ZD_CLI_Verify_Bonjour_Gateway_Value'
    common_name = '%sCheck bonjour gateway is disabled.'% (test_case_name)
    test_params = {'bonjour_gw_value':'disabled'}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 
#clean_up   
    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all the WLANs from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_Scaling_Remove_AAA_Servers'
    common_name = 'Remove all AAA servers from ZD for the next test'
    test_cfgs.append(({}, test_name, common_name, 0, True))

    test_name = 'CB_ZD_Config_AP_Radio'
    common_name = 'Config All APs Radio - Enable WLAN Service'
    test_params = {'cfg_type': 'teardown',
                   'all_ap_mac_list': cfg['all_ap_mac_list']}
    test_cfgs.append((test_params, test_name, common_name, 0, True)) 
    
    test_name = 'CB_SW_Destroy_All_Isolate_Groups'
    common_name = 'Delete all ports from isolate groups.'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, True))

    return test_cfgs

def test_process(test_case_name,cfg,wlan1_cfg,wlan2_cfg):
 
    radio_mode = cfg['radio_mode'] 

    sta_radio_mode = radio_mode

    ap_tag = 'ap%s' % radio_mode

    test_cfgs = []
      
    return test_cfgs

def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')

def check_duplicated_common_name(test_cfgs):
    common_name_list = []
    duplicate_flag = False
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if common_name in common_name_list:
            duplicate_flag = False
            print '####################'
            print common_name
            print '####################'
        else:
            common_name_list.append(common_name)
    return duplicate_flag
  
def createTestSuite(**kwargs):
    ts_cfg = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )    
    ts_cfg.update(kwargs)
        
    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']

    
    if ts_cfg["interactive_mode"]:
        target_sta1 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station1: ")
        target_sta2 = testsuite.getTargetStation(sta_ip_list, "Pick wireless station2: ")
        target_sta_radio = testsuite.get_target_sta_radio()
    else:
        target_sta1 = sta_ip_list[ts_cfg["station"][0]]
        target_sta2 = sta_ip_list[ts_cfg["station"][1]]
        target_sta_radio = ts_cfg["station"][1]

    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    active_ap = active_ap_list[0]
    tunnel_mode = raw_input("\n\
Do you want to enable tunnel to do test?\n\
  1. Yes\n\
  2. No\n\
Default selection is 2.Input your choice:")

    if tunnel_mode != '1':
        enable_tunnel = False
    else: enable_tunnel = True

    tcfg = {
            'vlan10_user': 'finance.user',  
            'vlan20_user': 'marketing.user',
            'target_station1':'%s' % target_sta1,
            'target_station2':'%s' % target_sta2,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list':all_ap_mac_list,
            'enable_tunnel':enable_tunnel
            }         
    test_cfgs = define_test_cfg(tcfg)   

    check_max_length(test_cfgs)
    #check_validation(test_cfgs)
    is_duplicated = check_duplicated_common_name(test_cfgs)
    if is_duplicated:
        return  
    
    if ts_cfg["testsuite_name"]:
        ts_name = ts_cfg["testsuite_name"]
    else:
        ts_name = "Bonjour_Gateway_Negative"

    ts = testsuite.get_testsuite(ts_name, "Bonjour_Gateway_Negative" , combotest=True)

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
    createTestSuite(**_dict)