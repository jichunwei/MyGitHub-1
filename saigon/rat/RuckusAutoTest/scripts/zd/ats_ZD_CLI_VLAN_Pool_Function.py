'''
Created on Dec 15, 2014

@author: chen.tao@odc-ruckuswireless.com
'''
import sys
from copy import deepcopy
import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def define_test_cfg(cfg):
    test_cfgs = []

    radio_mode = cfg['radio_mode']

    sta_radio_mode = radio_mode
    if sta_radio_mode == 'bg':
        sta_radio_mode = 'g'
    
    sta_tag = 'sta%s' % radio_mode
    ap_tag = 'ap%s' % radio_mode

    aaa_server = {'server_name': 'FreeRADIUS',
                  'server_addr': '192.168.0.252',
                  'type': 'radius-auth',
                  'radius_secret': '1234567890',
                  'server_port': '1812',
                  'backup': False}

    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = 'Remove all WLANs before test'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = 'Try to del all vlan pools.'
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Remove_All_AAA_Servers'
    common_name = 'Remove all AAA Servers.'
    test_cfgs.append(({},test_name, common_name, 0, False))

    test_name = 'CB_ZD_CLI_Configure_AAA_Servers'
    common_name = 'Create AAA server'
    test_cfgs.append(({'server_cfg_list': [aaa_server]}, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Active_AP'
    common_name = 'Create active AP'
    test_cfgs.append(({'active_ap':cfg['active_ap'],
                       'ap_tag': ap_tag}, test_name, common_name, 0, False))
   
    test_name = 'CB_ZD_Create_Station'
    common_name = 'Create target station'
    test_cfgs.append(({'sta_ip_addr':cfg['target_station'],
                       'sta_tag': sta_tag}, test_name, common_name, 0, False))
#############################################################################
    test_case_name = '[AAA has higher priority than VLAN pool]'

    num = 0
    idx = '1.%s'    
  
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_eap_test",'vlan':'302'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    wlan_cfg = {'name': 'VLAN_POOL_WITH_EAP_WLAN',
                'ssid': 'VLAN_POOL_WITH_EAP_WLAN',
                'auth': 'dot1x-eap',
                'encryption': 'AES',
                'algorithm': 'AES',
                'wpa_ver': 'WPA2',
                'sta_wpa_ver': 'WPA2',
                'sta_encryption': 'AES',
                'sta_auth': 'EAP',
                'auth_server': aaa_server['server_name'],
                'username': 'finance.user',
                'password': 'finance.user',
                'key_string': '',
                'use_radius': True,
                'vlanpool':'vlan_pool_eap_test',
                'dvlan': True,
                }
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate an EAP WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': wlan_cfg}, test_name, common_name, 2, False)) 

    wlan_cfg_tmp = deepcopy(wlan_cfg)
    wlan_cfg_tmp.update({
                        'auth':'EAP',
                        'username': 'ras.eap.user',
                        'password': 'ras.eap.user',
                         })
    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association with non-vlan user' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg_tmp}, test_name, common_name, 2, False))
    
####verify station vlan is in vlan pool

    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 302' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['302']}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    wlan_cfg_tmp2 = deepcopy(wlan_cfg)
    wlan_cfg_tmp2.update({
                        'auth':'EAP',}
                         )

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association with vlan 10 user' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg_tmp2}, test_name, common_name, 2, False))

####verify station vlan is not in vlan pool, it's 10

    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Edit_Vlan_Pool'
    common_name = '%sEdit vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_eap_test",'add_vlan':'20','del_vlan':'302',}}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association with vlan 10 user' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': wlan_cfg_tmp2}, test_name, common_name, 2, False))
    
####verify station vlan is not in vlan pool, it's 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

#############################################################################
    test_case_name = '[RBAC has higher priority than VLAN pool]'

    num = 0
    idx = '2.%s' 

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_rbac_test",'vlan':'20'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = '%sRemove all Users from ZD'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = '%sRemove all Roles from ZD'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    roles_cfg = [{"role_name":"role_with_vlan",
                  "enable_rbac" : True,
                  "allow_all_wlans":True,
                  "group_attr":"role_with_vlan",
                  "vlan_policy":"302"}]

    num += 1
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = '%sCreate roles'%(test_case_name + idx%(num))
    test_cfgs.append(({'role_cfg_list':roles_cfg}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Server_Del_STA_MAC_As_Radius_User'                
    common_name = "%sDelete station mac info in Radius"%(test_case_name + idx%(num))
    test_cfgs.append(({'mac_format_type': 'all_formats',
                       'sta_tag':sta_tag}, test_name, common_name, 2, False))

    user_role_policy_vlan = [(sta_tag,sta_tag,True,None,None,"role_with_vlan",None)]

    num += 1
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '%sCreate Radius Users'%(test_case_name + idx%(num))
    test_cfgs.append(({'add_user':user_role_policy_vlan}, test_name, common_name, 2, False))
    
    vlan_pool_wlan_cfg = {'name': 'VLAN_POOL_WITH_MAC_WLAN_RBAC',
                          'ssid': 'VLAN_POOL_WITH_MAC_WLAN_RBAC',
                          'auth': 'mac',
                          'encryption': 'AES',
                          'algorithm': 'AES',
                          'wpa_ver': 'WPA2',
                          'sta_wpa_ver': 'WPA2',
                          'sta_encryption': 'AES',
                          'passphrase':'11111111',
                          'sta_auth': 'mac',
                          'auth_server': aaa_server['server_name'],
                          'key_string': '11111111',
                          'use_radius': True,
                          'vlanpool':'vlan_pool_rbac_test',
                          'dvlan': True,
                     }
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a MAC auth WLAN with vlanpool and rbac enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': vlan_pool_wlan_cfg}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': vlan_pool_wlan_cfg}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool, it's 20
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    rbac_wlan_cfg = deepcopy(vlan_pool_wlan_cfg)
    rbac_wlan_cfg.update({'enable_rbac':True})
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sEnable rbac in the WLAN' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': rbac_wlan_cfg}, test_name, common_name, 2, False)) 


    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': rbac_wlan_cfg}, test_name, common_name, 2, False))
    
####verify station vlan is in not vlan pool, it's 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 302' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['302']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = '%sRemove all Roles from ZD'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1 
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '%sDelete Radius Users'%(test_case_name + idx%(num))
    test_cfgs.append(({'del_user':user_role_policy_vlan}, test_name, common_name, 2, True))

#############################################################################
    test_case_name = '[DPSK has higher priority than VLAN pool]'

    num = 0
    idx = '3.%s' 

    num += 1
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = '%sRemove all DPSK'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 1, False))
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_dpsk_test",'vlan':'10'}}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    standard_open_wpa2_dpsk_wlan = {
             "name" : "VLAN_POOL_WITH_DPSK",
             "ssid" : "VLAN_POOL_WITH_DPSK",
             "type" : "standard-usage",
             "auth" : "PSK",
             "wpa_ver" : "WPA2",
             "encryption" : "AES",
             "key_string" : "12345678",
             "zero_it" : "True",
             'vlanpool':'vlan_pool_dpsk_test',
             "dvlan" : "True",
             "enable_dpsk" : "True"}
    
    num += 1
    test_name = 'CB_ZD_CLI_Create_Wlans'
    common_name = '%sCreate a dpsk WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg_list': [standard_open_wpa2_dpsk_wlan]}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association with psk' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': standard_open_wpa2_dpsk_wlan}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool, it's 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    dpsk_conf = {'wlan' : "VLAN_POOL_WITH_DPSK",
                 'number_of_dpsk' : 1,
                 'role' :None,
                 'vlan':"20"}

    num += 1
    test_name = 'CB_ZD_Generate_DPSK'
    common_name = '%sGet the Dynamic PSK' %(test_case_name + idx%(num))
    test_cfgs.append(({'dpsk_conf': dpsk_conf,"check_webui":False,"check_cli":False}, test_name, common_name, 2, False))

    num += 1        
    test_name = 'CB_Station_Association_WLAN_With_DPSK'
    common_name = '%sSTA connect to the wlan with DPSK' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag, 'wlan_ssid': standard_open_wpa2_dpsk_wlan['name']}, test_name, common_name, 2, False))
    
####verify station vlan is in not vlan pool, it's 20
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Remove_All_DPSK'
    common_name = '%sCleanup - Remove all DPSK'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

#############################################################################
    test_case_name = '[RBAC has highest priority]'

    num = 0
    idx = '4.%s' 

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_mixed_test",'vlan':'10'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Remove_All_Users'
    common_name = '%sRemove all Users from ZD'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1    
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = '%sRemove all Roles from ZD'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    roles_cfg_tmp = [{"role_name":"role_policy_vlan",
                      "enable_rbac" : True,
                      "allow_all_wlans":True,
                      "group_attr":"role_policy_vlan",
                      "vlan_policy":"302"}]

    num += 1
    test_name = 'CB_ZD_CLI_Configure_Roles'
    common_name = '%sCreate roles'%(test_case_name + idx%(num))
    test_cfgs.append(({'role_cfg_list':roles_cfg_tmp}, test_name, common_name, 2, False))

    user_role_policy_vlan = [('vlan.pool.test','vlan.pool.test',None,None,'20',"role_policy_vlan",True)]

    num += 1
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '%sCreate Radius Users'%(test_case_name + idx%(num))
    test_cfgs.append(({'add_user':user_role_policy_vlan}, test_name, common_name, 2, False))
    
    vlan_pool_mixed_cfg = {'name': 'VLAN_POOL_WITH_AAA_AND_RBAC',
                          'ssid': 'VLAN_POOL_WITH_AAA_AND_RBAC',
                          'auth': 'dot1x-eap',
                          'encryption': 'AES',
                          'algorithm': 'AES',
                          'wpa_ver': 'WPA2',
                          'sta_wpa_ver': 'WPA2',
                          'sta_encryption': 'AES',
                          'sta_auth': 'EAP',
                          'auth_server': aaa_server['server_name'],
                          'key_string': '',
                          'use_radius': True,
                          'vlanpool':'vlan_pool_mixed_test',
                          'dvlan': True,
                          'enable_rbac':True,
                          'username':'vlan.pool.test',
                          'password':'vlan.pool.test'
                     }
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': vlan_pool_mixed_cfg}, test_name, common_name, 2, False)) 

    vlan_pool_mixed_cfg_tmp = deepcopy(vlan_pool_mixed_cfg)
    vlan_pool_mixed_cfg_tmp.update({'auth':'EAP'})
    
    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': vlan_pool_mixed_cfg_tmp}, test_name, common_name, 2, False))

####verify station vlan is in rbac vlan, it's 50, instead of 10 or 20
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 302' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['302']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_Remove_All_Roles'
    common_name = '%sRemove all Roles from ZD'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1 
    test_name = 'CB_Server_Add_And_Delete_Radius_Users'
    common_name = '%sDelete Radius Users'%(test_case_name + idx%(num))
    test_cfgs.append(({'del_user':user_role_policy_vlan}, test_name, common_name, 2, True))

#############################################################################
    test_case_name = '[VLAN pool in web auth WLAN]'

    num = 0
    idx = '5.%s' 

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_web_auth",'vlan':'20'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    web_auth_wlan_cfg = {
             "name" : "VLAN_POOL_WEB_AUTH",
             "ssid" : "VLAN_POOL_WEB_AUTH",
             "type" : "standard-usage",
             'web_auth' : True, 
             'auth_server': aaa_server['server_name'],
             "auth" : "open",
             "encryption" : "none",
             'vlanpool':'vlan_pool_web_auth',
             "dvlan" : "True",
             'username': 'finance.user',
             'password': 'finance.user',}
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a web auth WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': web_auth_wlan_cfg}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': web_auth_wlan_cfg}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool, it's 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%sStart browser in station'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                      'browser_tag':'firefox'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_CaptivePortal_Perform_WebAuth'
    common_name = '%sPerform Web authentication for client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag':sta_tag, 
                        'browser_tag': 'firefox',
                        'username': web_auth_wlan_cfg['username'], 
                        'password': web_auth_wlan_cfg['password'],},
                        test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool, it's 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

#############################################################################
    test_case_name = '[VLAN pool in hotspot WLAN]'

    num = 0
    idx = '6.%s' 
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_hotspot",'vlan':'20'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    hotspot_cfg = {
                   'name': 'hotspot_vlan_pool',
                   'login_page': 'http://192.168.0.250/login.html',
                   'idle_timeout': None,
                   'auth_svr': aaa_server['server_name']
    }

    num += 1
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    common_name = '%sConfigure Hotspot from CLI' %(test_case_name + idx%(num))
    test_cfgs.append(({'hotspot_conf':hotspot_cfg}, test_name, common_name, 2, False))

    hotspot_auth_wlan_cfg = {
             "name" : "VLAN_POOL_HOTSPOT",
             "ssid" : "VLAN_POOL_HOTSPOT",
             "type" : "hotspot",
             'hotspot_profile' : hotspot_cfg['name'], 
             "auth" : "open",
             "encryption" : "none",
             'vlanpool':'vlan_pool_hotspot',
             "dvlan" : "True",
             'username': 'finance.user',
             'password': 'finance.user',}
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a hotspot WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': hotspot_auth_wlan_cfg}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': hotspot_auth_wlan_cfg}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%sStart browser in station'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                      'browser_tag':'firefox'}, test_name, common_name, 2, False))

    num += 1      
    test_name = 'CB_Station_CaptivePortal_Perform_HotspotAuth'
    common_name = '%sPerform Hotspot authentication for client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag':sta_tag, 
                      'browser_tag': 'firefox',
                      'username': hotspot_auth_wlan_cfg['username'], 
                      'password': hotspot_auth_wlan_cfg['password'],},
                      test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool, it's 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Configure_Hotspot'
    common_name = '%sDelete Hotspot from CLI' %(test_case_name + idx%(num))
    test_cfgs.append(({'hotspot_conf':hotspot_cfg}, test_name, common_name, 2, True))


    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

#############################################################################
    test_case_name = '[VLAN pool in guest access WLAN]'

    num = 0
    idx = '7.%s' 
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_guest_access",'vlan':'20'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    guest_access_wlan_cfg = {
             "name" : "VLAN_POOL_GUEST",
             "ssid" : "VLAN_POOL_GUEST",
             "type" : "guest",
             "auth" : "open",
             "encryption" : "none",
             'vlanpool':'vlan_pool_guest_access',
             "dvlan" : "True",
             'username': 'finance.user',
             'password': 'finance.user',}

    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate a guest WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': guest_access_wlan_cfg}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_ZD_Generate_Guest_Pass'
    common_name = '%s Generate a guest pass automatically for wlan1' %(test_case_name + idx%(num))
    test_params = {'username': 'ras.eap.user', 
                   'password': 'ras.eap.user', 
                   'auth_ser': aaa_server['server_name'], 
                   'wlan': guest_access_wlan_cfg['ssid'],
                   'guest_fullname': 'vlan_pool_test'}
    test_cfgs.append((test_params, test_name, common_name,2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': guest_access_wlan_cfg}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_CaptivePortal_Start_Browser'
    common_name = '%sStart browser in station'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                      'browser_tag':'firefox'}, test_name, common_name, 2, False))

    num += 1      
    test_name = 'CB_Station_CaptivePortal_Perform_GuestAuth'
    common_name = "%sPerform guest authentication in station"%(test_case_name + idx%(num))
    test_params = {'sta_tag': sta_tag, 
                   'browser_tag': 'firefox',
                   'use_tou': False, 
                   'redirect_url': '',
                   'target_url': 'http://172.16.10.252/',
                   'no_auth': False}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    num += 1
    test_name = 'CB_ZD_Get_Station_Wifi_Addr_1'
    common_name = '%sGet WiFi address of station1'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool, it's vlan 10
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 20' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['20']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    guest_access_conf = {'authentication_server':'Local Database'}
    num += 1
    test_name = 'CB_ZD_CLI_Configure_Guest_Access'
    common_name = '%sSet guest access authentication server' %(test_case_name + idx%(num))
    test_cfgs.append(({'guest_access_conf': guest_access_conf}, test_name, common_name, 2, True))
    
############################################################
    test_case_name = '[backup_restore_reboot_zd]'
    num = 0
    idx = '8.%s' 

    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_bkup_restore",'vlan':'10'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    open_none_wlan_1 = {
             "name" : "VLAN_POOL_REBOOT_ZD",
             "ssid" : "VLAN_POOL_REBOOT_ZD",
             "type" : "standard-usage",
             "auth" : "open",
             "encryption" : "none",
             'vlanpool':'vlan_pool_bkup_restore',
             "dvlan" : "True"}
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate an open none WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': open_none_wlan_1}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_ZD_Backup'
    common_name = '%sBackup the current configuration'%(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Reboot_ZD'
    common_name = '%sReboot zd from zdcli'%(test_case_name + idx%(num))
    test_cfgs.append(( {'timeout':10*60}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sVerify AP status changed to connected' %(test_case_name + idx%(num))
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': open_none_wlan_1}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools.'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Restore'
    common_name = '%s restore zd config' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association again' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': open_none_wlan_1}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))
    
#####################################################################
    test_case_name = '[reboot_ap]'
    num = 0
    idx = '9.%s' 
    
    num += 1
    test_name = 'CB_ZD_CLI_Add_Vlan_Pool'
    common_name = '%sAdd a vlan pool'%(test_case_name + idx%(num))
    test_params = {'vlan_pool_cfg':{'name':"vlan_pool_reboot_ap",'vlan':'10'}}
    test_cfgs.append((test_params, test_name, common_name, 1, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs before test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, False))

    open_none_wlan_2 = {
             "name" : "VLAN_POOL_REBOOT_AP",
             "ssid" : "VLAN_POOL_REBOOT_AP",
             "type" : "standard-usage",
             "auth" : "open",
             "encryption" : "none",
             'vlanpool':'vlan_pool_reboot_ap',
             "dvlan" : "True"}
    
    num += 1
    test_name = 'CB_ZD_CLI_Configure_WLAN'
    common_name = '%sCreate an open none WLAN with vlanpool enabled' %(test_case_name + idx%(num))
    test_cfgs.append(({'wlan_cfg': open_none_wlan_2}, test_name, common_name, 2, False)) 

    num += 1
    test_name = 'CB_ZD_CLI_Reboot_All_AP'
    common_name = '%sReboot all AP'%(test_case_name + idx%(num))
    test_cfgs.append(({'ap_tag': ap_tag,},test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_Wait_AP_Status'
    common_name = '%sVerify AP status changed to connected'%(test_case_name + idx%(num))
    test_cfgs.append(({'ap_tag': ap_tag, 'expected_status':'connected'}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_Station_Associate_Wlan_And_Get_Wifi_Addr_V2'
    common_name = '%sVerify client association again' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'wlan_cfg': open_none_wlan_2}, test_name, common_name, 2, False))

####verify station vlan is in vlan pool
    num += 1
    test_name = 'CB_ZD_CLI_Verify_Station_Info'
    common_name = '%sVerify client vlan is 10' %(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag,
                       'vlan': ['10']}, test_name, common_name, 2, False))

    num += 1
    test_name = 'CB_ZD_CLI_Remove_Wlans'
    common_name = '%sRemove all WLANs after test' %(test_case_name + idx%(num))
    test_cfgs.append(({}, test_name, common_name, 2, True))

    num += 1
    test_name = 'CB_ZD_CLI_Del_Vlan_Pool'
    common_name = '%sDelete all vlan pools after test'%(test_case_name + idx%(num))
    test_params = {'del_all':True,}
    test_cfgs.append((test_params, test_name, common_name, 2, True)) 

    num += 1
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = '%sDisassociate the client after test'%(test_case_name + idx%(num))
    test_cfgs.append(({'sta_tag': sta_tag}, test_name, common_name, 2, True))

    return test_cfgs
def make_test_suite(**kwargs):

    attrs = dict(interactive_mode = True,
                 testsuite_name = "",
                 )
    attrs.update(kwargs)

    mtb = testsuite.getMeshTestbed(**kwargs)
    tbcfg = testsuite.getTestbedConfig(mtb)
    
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    all_ap_mac_list = tbcfg['ap_mac_list']
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)
    target_sta = testsuite.getTargetStation(sta_ip_list, "Pick wireless station: ") 
    target_sta_radio = testsuite.get_target_sta_radio()    
    active_ap = active_ap_list[0]   
    tcfg = {
            'target_station':'%s' % target_sta,
            'radio_mode': target_sta_radio,
            'active_ap':active_ap,
            'all_ap_mac_list': all_ap_mac_list,
            }
    test_cfgs = define_test_cfg(tcfg)
#----------------------------------------------------------------------------------------------------------
    
    if attrs["testsuite_name"]:
        ts_name = attrs["testsuite_name"]
    else: 
        ts_name = "VLAN_POOL_Functions" 
            
    ts = testsuite.get_testsuite(ts_name,'VLAN_POOL_Functions',combotest=True)
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



