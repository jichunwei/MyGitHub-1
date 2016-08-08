'''
Port Base Vlan - Hotspot with Vlan
Created on 2011-11-24
@author: jluh@ruckuswireless.com
'''

import sys
import time

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import lib_Constant as const


'''
'''
user_cfg_kv = {'server_name': 'Local Database',
               'username': 'rat_local_user_pass',
               'password': 'rat_local_user_pass'
               }


wlan_cfg = {'ssid': "open-hotspot-wlan-%s" % (time.strftime("%H%M%S")),
            'auth': "open",
            'encryption': "none",
            'sta_auth': "open",
            'sta_encryption': "none",
            'type': 'hotspot',
            'username': "rat_local_user_pass",
            'password': "rat_local_user_pass",
            'vlan_id': '',
            }


wgs_cfg = {'name': 'Hotspot-WlanGroup', 'description': 'Hotspot-WlanGroup', 'ap_rp': {}}
                                                        

def define_input_cfg():
    test_conf = dict(
        zd_ip_addr='192.168.0.2',

        user_cfg={},

        wlan_cfg={},
        
        guest_policy={},

        ap_radio="",

        connection_timed_out=5 * 1000, # in seconds
    )

    return test_conf


def define_test_configuration(tbcfg, input_cfg):
    test_cfgs = []
    if 'a' in input_cfg['radio']:
        wlan_ssid = 'wlan32'
    else:
        wlan_ssid = 'wlan0'
    
    if input_cfg['expected_subnet'] == "20.0.2.0/255.255.255.0":
        input_cfg['linux_pc_untag_ip'] = "20.0.2.102"
        input_cfg['linux_pc_tag_ip'] = "20.0.2.103" 
    else:
        sub_re = input_cfg['expected_subnet'].split("/")[0]
        sub_list = sub_re.split(".")
        input_cfg['linux_pc_untag_ip'] = sub_list[0] + "." + sub_list[1] + "." + sub_list[2] + ".102"
        input_cfg['linux_pc_tag_ip'] = sub_list[0] + "." + sub_list[1] + "." + sub_list[2] + ".103"
    
    vlan_id = input_cfg['vlan_id']
    vlan_if = input_cfg['pc2_interface'] + '.' + vlan_id

    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Test enviroment default config setting'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Backup AP Mgmt VLAN current settings"
    test_cfgs.append(({'cfg_type': "init"}, test_name, common_name, 0, False))
    
    test_name = 'CB_SW_Change_Interface_Vlan'
    common_name = 'Change AP Port from vlan 301 to 333'
    test_params = {'from_vlan_id':'301',
                    'to_vlan_id':'333',
                    'component':'AP'}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Create_Test_Components'
    common_name = 'Config test env components - ZD, Acitve AP, Station, Linux PC1, Linux PC2'
    test_params = {'Station': {'sta_tag': 'sta1', 'sta_ip_addr': '192.168.1.11'}, 
                   'AP': {'ap_tag': 'active_ap', 'active_ap': input_cfg['active_ap_list'][0]}, 
                   'LinuxPC': [{'lpc_tag': 'LinuxPC1', 'lpc_ip_addr': '192.168.1.101'}, 
                                {'lpc_tag': 'LinuxPC2', 'lpc_ip_addr': '192.168.1.102'},
                                ]}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_LinuxPC_Config_Interface'
    common_name = 'Config Linux PC1 %s interface with untag' % input_cfg['pc1_interface']
    test_params = {'lpc_tag': 'LinuxPC1', 
                   'interface': input_cfg['pc1_interface'], 
                   'ip_addr': input_cfg['linux_pc_untag_ip'], 
                   'vlan_id': ''}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_LinuxPC_Config_Interface'
    common_name = 'Config Linux PC2 %s interface with tag %s' % (vlan_if, vlan_id)
    test_params = {'lpc_tag': 'LinuxPC2', 
                   'interface': input_cfg['pc2_interface'], 
                   'vlan_if_ip_addr': input_cfg['linux_pc_tag_ip'], 
                   'vlan_id': vlan_id}
    test_cfgs.append((test_params, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Config_WISPr_Setting_Combi_Port_Base_Vlan'
    common_name = 'Config the WISPr setting with Local User on ZD'
    test_params = {'ap_tag': 'active_ap',
                   'wlan_cfg': wlan_cfg, 
                   'wgs_cfg': wgs_cfg, 
                   'username': user_cfg_kv['username'],
                   'password': user_cfg_kv['password'],
                   'hotspot_profiles_list': [{'login_page': 'http://192.168.0.250/login.html',
                                              'name': 'wispr_test'}]}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
        
    test_name = 'CB_Station_Hotspot_Auth_Perform_Combi_Port_Base_Vlan'
    common_name = 'Confirm with the normal associated, authorized in STA'
    test_params = {'sta_tag': 'sta1', 
                   'wlan_cfg': wlan_cfg, 
                   'hotspot_perform_cfg': {'username': user_cfg_kv['username'],
                                           'password': user_cfg_kv['password'],
                                           }
                  }
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_Station_Verify_Expected_Subnet'
    common_name = "Verify the STA's wifi interface is got the corrected subnet"
    test_params = {'sta_tag': 'sta1', 'expected_subnet': input_cfg['expected_subnet']}
    test_cfgs.append((test_params, test_name, common_name, 0, False))
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_Trunk 1]:Config Active AP LAN Port to Trunk untag 1'
    test_params = {'ap_tag': 'active_ap', 'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_Trunk 1]:Verify the vlan setting normally in AP side'
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': '1', 'Enabled vlans': 'all'},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': '1', 'Enabled vlans': 'all'},]
                   }           
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_Trunk 1]:Verify STA ping denied %s of Linux PC1 with untag" % input_cfg['pc1_interface']
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_Trunk 1]:Verify STA ping allow %s of Linux PC2 with tag %s"  % (vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_Trunk %s]:Config Active AP LAN Port to Trunk untag %s'  % (vlan_id, vlan_id)
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'trunk',
                                     'lan1_untagged_vlan': vlan_id, 
                                     'lan1_vlan_members': '', 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'trunk',
                                     'lan2_untagged_vlan': vlan_id,  
                                     'lan2_vlan_members': '',
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_Trunk %s]:Verify the vlan setting normally in AP side'  % (vlan_id)
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': vlan_id, 'Enabled vlans': 'all'},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': vlan_id, 'Enabled vlans': 'all'},]
                   }                
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_Trunk %s]:Verify STA ping allow %s of Linux PC1 with untag" % (vlan_id, input_cfg['pc1_interface'])
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_Trunk %s]:Verify STA ping deny %s of Linux PC2 with tag %s"  % (vlan_id, vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_Trunk none]:Config Active AP LAN Port to Trunk untag none'
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'trunk',
                                     'lan1_untagged_vlan': 'none', 
                                     'lan1_vlan_members': '', 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'trunk',
                                     'lan2_untagged_vlan': 'none',  
                                     'lan2_vlan_members': '',
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_Trunk none]:Verify the vlan setting normally in AP side'
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': 'none', 'Enabled vlans': 'all'},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': 'none', 'Enabled vlans': 'all'},]
                   }         
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_Trunk none]:Verify STA ping denied %s of Linux PC1 with untag" % input_cfg['pc1_interface']
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_Trunk none]:Verify STA ping allow %s of Linux PC2 with tag %s"  % (vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
#-----------------------------------------------------------------------------------------------------------------------
    inv_vlanid = str(int(vlan_id)+28)
    vlan_members = vlan_id + ',' + inv_vlanid
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_General %s - tag %s,%s]:Config Active AP LAN Port to General %s - tag %s,%s' \
                  % (vlan_id, vlan_id, inv_vlanid, vlan_id, vlan_id, inv_vlanid)
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'general',
                                     'lan1_untagged_vlan': vlan_id, 
                                     'lan1_vlan_members': vlan_members, 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'general',
                                     'lan2_untagged_vlan': vlan_id,  
                                     'lan2_vlan_members': vlan_members,
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_General %s - tag %s,%s]:Verify the vlan setting normally in AP side'  % (vlan_id, vlan_id, inv_vlanid)
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_members},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_members},]
                   }            
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_General %s - tag %s,%s]:Verify STA ping allow %s of Linux PC1 with untag" \
                  % (vlan_id, vlan_id, inv_vlanid, input_cfg['pc1_interface'])
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General %s - tag %s,%s]:Verify STA ping deny %s of Linux PC with tag %s"  \
                  % (vlan_id, vlan_id, inv_vlanid, vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
#-------------------------------------------------------------------------------------------------------------------------------------- 
    vlan_members = '1-' + vlan_id
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_General %s - tag 1]:Config Active AP LAN Port to General %s - tag 1' % (vlan_id, vlan_id)
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'general',
                                     'lan1_untagged_vlan': vlan_id, 
                                     'lan1_vlan_members': '1', 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'general',
                                     'lan2_untagged_vlan': vlan_id,  
                                     'lan2_vlan_members': '1',
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_General %s - tag 1]:Verify the vlan setting normally in AP side' % vlan_id
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_members},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_members},]
                   } 
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_General %s - tag 1]:Verify STA ping allow %s of Linux PC1 with untag" % (vlan_id, input_cfg['pc1_interface'])
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General %s - tag 1]:Verify STA ping deny %s of Linux PC2 with tag %s"  % (vlan_id, vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    vlan_members = vlan_id + '-' + inv_vlanid + ',' + str(int(inv_vlanid) + 5)
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_General none - tag %s]:Config Active AP LAN Port to General none - tag %s' % (vlan_members, vlan_members)
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'general',
                                     'lan1_untagged_vlan': 'none', 
                                     'lan1_vlan_members': vlan_members, 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'general',
                                     'lan2_untagged_vlan': 'none',  
                                     'lan2_vlan_members': vlan_members,
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_General none - tag %s]:Verify the vlan setting normally in AP side' % vlan_members
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': 'none', 'Enabled vlans': vlan_members},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': 'none', 'Enabled vlans': vlan_members},]
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General none - tag %s]:Verify STA ping deny %s of Linux PC1 with untag" % (vlan_members, input_cfg['pc1_interface'])
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_General none - tag %s]:Verify STA ping allow %s of Linux PC2 with tag %s"  % (vlan_members, vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    vlan_members = '1' + ',' + inv_vlanid
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_General none - tag %s]:Config Active AP LAN Port to General none - tag %s' % (vlan_members, vlan_members)
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'general',
                                     'lan1_untagged_vlan': 'none', 
                                     'lan1_vlan_members': vlan_members, 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'general',
                                     'lan2_untagged_vlan': 'none',  
                                     'lan2_vlan_members': vlan_members,
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_General none - tag %s]:Verify the vlan setting normally in AP side' % vlan_members
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': 'none', 'Enabled vlans': vlan_members},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': 'none', 'Enabled vlans': vlan_members},]
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General none - tag %s]:Verify STA ping deny %s of Linux PC1 with untag" % (vlan_members, input_cfg['pc1_interface'])
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General none - tag %s]:Verify STA ping deny %s of Linux PC2 with tag %s"  % (vlan_members, vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_General 1 - tag 1]:Config Active AP LAN Port to General 1 - tag 1'
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'general',
                                     'lan1_untagged_vlan': '1', 
                                     'lan1_vlan_members': '1', 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'general',
                                     'lan2_untagged_vlan': '1',  
                                     'lan2_vlan_members': '1',
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))

    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_General 1 - tag 1]:Verify the vlan setting normally in AP side'
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': '1', 'Enabled vlans': '1'},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': '1', 'Enabled vlans': '1'},]
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General 1 - tag 1]:Verify STA ping deny %s of Linux PC1 with untag" % input_cfg['pc1_interface']
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General 1 - tag 1]:Verify STA ping deny %s of Linux PC2 with tag %s"  % (vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    vlan_members = '1-' + vlan_id
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = '[Hotspot with vlan_General 1 - tag %s]:Config Active AP LAN Port to General 1 - tag %s' % (vlan_id, vlan_id)
    test_params = {'ap_tag': 'active_ap',  
                   'port_settings': {'lan1_enabled': True, 
                                     'lan1_type': 'general',
                                     'lan1_untagged_vlan': '1', 
                                     'lan1_vlan_members': vlan_id, 
                                     'lan2_enabled': True, 
                                     'lan2_type': 'general',
                                     'lan2_untagged_vlan': '1',  
                                     'lan2_vlan_members': vlan_id,
                                     }
                   }
    test_cfgs.append((test_params, test_name, common_name, 1, False))
    
    test_name = 'CB_AP_Verify_Port_Base_Vlan_Setting'
    common_name = '[Hotspot with vlan_General 1 - tag %s]:Verify the vlan setting normally in AP side' % vlan_id
    test_params = {'ap_tag': 'active_ap',
                   'expected_data_list': [{'Mode': wlan_ssid, 'Untagged vlan': vlan_id, 'Enabled vlans': vlan_id},
                                          {'Mode': input_cfg['lan_port_list'][0], 'Untagged vlan': '1', 'Enabled vlans': vlan_members},
                                          {'Mode': input_cfg['lan_port_list'][1], 'Untagged vlan': '1', 'Enabled vlans': vlan_members},]
                   }
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Denied'
    common_name = "[Hotspot with vlan_General 1 - tag %s]:Verify STA ping deny %s of Linux PC1 with untag" % (vlan_id, input_cfg['pc1_interface'])
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_untag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False))
    
    test_name = 'CB_Station_Ping_Dest_Is_Allowed'
    common_name = "[Hotspot with vlan_General 1 - tag %s]:Verify STA ping allow %s of Linux PC2 with tag %s"  % (vlan_id, vlan_if, vlan_id)
    test_params = {'sta_tag': 'sta1', 'ping_timeout_ms': 10000, 'dest_ip': input_cfg['linux_pc_tag_ip']}
    test_cfgs.append((test_params, test_name, common_name, 2, False)) 
    
    test_name = 'CB_Station_Remove_All_Wlans'
    common_name = 'Remove the wlan from the station'
    test_params = {'sta_tag': 'sta1'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Config_AP_Port_Override'
    common_name = 'Config Active AP all of LAN Port to Trunk untag 1'
    test_params = {'ap_tag': 'active_ap', 'cfg_type': 'init'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = 'Remove all configuration from Zone Director to Cleanup'
    test_params = {}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = 'CB_SW_Change_Interface_Vlan'
    common_name = 'Change AP Port from vlan 333 to 301'
    test_params = {'from_vlan_id':'333',
                    'to_vlan_id':'301',
                    'component':'AP'}
    test_cfgs.append((test_params, test_name, common_name, 0, True))
    
    test_name = "CB_ZD_Config_AP_Policy_Mgmt_VLAN"
    common_name = "Restore AP Mgmt VLAN settings"
    test_cfgs.append(({'cfg_type': "teardown"}, test_name, common_name, 0, True))

    return test_cfgs


def get_selected_input(depot=[], num=1, prompt=""):
    options = []
    for i in range(len(depot)):
        options.append("  %d - %s\n" % (i, depot[i]))

    print "\n\nAvailable values:"
    print "".join(options)

    if not prompt:
        prompt = "Select option: "

    selection = []
    for i in range(num):
        id = raw_input(prompt + '%s/%s: ' % (i + 1, num))
        try:
            val = depot[int(id)]

        except:
            val = ""

        if val:
            selection.append(val)
            
        if num == 1:
            break

    return selection


def create_test_suite(**kwargs):
    attrs = dict(interactive_mode=True,
                 station=(0, "g"),
                 targetap=False,
                 testsuite_name="",
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    active_ap_list = []
    all_aps_mac_list = []
    active_aps_mac_list = []
    conn_mode = ''
    input_cfg = dict()

    
    if attrs["interactive_mode"]:
        target_sta = testsuite.getTargetStation(sta_ip_list, "Pick an wireless station: ") 
        target_sta_radio = testsuite.get_target_sta_radio() 
    else: 
        target_sta = sta_ip_list[attrs["station"][0]] 
        target_sta_radio = attrs["station"][1] 
        
    fit_ap_model = dict() 
    for ap_sym_name, ap_info in ap_sym_dict.items(): 
        if target_sta_radio in const._ap_model_info[ap_info['model'].lower()]['radios']:
            fit_ap_model[ap_sym_name] = ap_info
    
    if attrs["interactive_mode"]:
        try:
            active_ap_list = testsuite.getActiveAp(fit_ap_model)
            print active_ap_list
            if not active_ap_list:
                raise Exception("No found the surpported ap in the testbed env.")
        except:
            raise Exception("No found the surpported ap in the testbed env.")
    else:
        pass
    
    if attrs["interactive_mode"]:       
#        lan_port = None
#        while not lan_port:
#            lan_port = raw_input("Type Active AP's LAN interface(for example: lan1 or lan1 lan2): ").lower()
        lan_port = "lan1 lan2"
        lan_port_list = lan_port.split(" ")                
    else:
        pass
                
    if attrs["interactive_mode"]:
        pc1_eth_port = None
        pc2_eth_port = None
        while not pc1_eth_port:
            pc1_eth_port = raw_input("Type Linux PC1's ethernet interface(for example: eth0): ").lower()
        while not pc2_eth_port:
            pc2_eth_port = raw_input("Type Linux PC2's ethernet interface(for example: eth0): ").lower()
    else:
        pass
       
    if attrs["interactive_mode"]:            
        while True:
            vlan_id = raw_input("Type a vlan number at the hotspot wlan(1-4094)[enter for default value: 2]: ").lower()
            if not vlan_id:
                vlan_id = '2'
                break
            else:
                try:
                    int(vlan_id)
                    break
                except:
                    print "Please choice a vlan number from 1-4094"
                    continue
        wlan_cfg['vlan_id'] = vlan_id
        
        expected_subnet = raw_input("Type the expected subnet of station wifi[enter default:'20.0.2.0/255.255.255.0']: ").lower()
        if not expected_subnet:
            expected_subnet = '20.0.2.0/255.255.255.0'       
    else:
        pass           
         
    for active_ap in active_ap_list:
        for u_ap in ap_sym_dict.keys():
            ap_mac = ap_sym_dict[u_ap]['mac']
            if u_ap == active_ap:
                active_aps_mac_list.append(ap_mac)
            all_aps_mac_list.append(ap_mac)
        
        ap_sub_model = ap_sym_dict[active_ap]['model'].upper()
        
        ts_name = 'Port Base VLAN - Hotspot wlan with Vlan - %s' % (target_sta_radio)

        ts = testsuite.get_testsuite(ts_name, ts_name,
                                     interactive_mode=True,
                                     combotest=True,)
    
        fcfg = {'ts_name': ts.name,
                'sta_ip_list': sta_ip_list,
                'ap_sym_name_list': ap_sym_dict.keys(),
               }
        
        wgs_cfg['ap_rp'][target_sta_radio] = {}
        wgs_cfg['ap_rp'][target_sta_radio].update({'wlangroups': wgs_cfg['name']})
        
        input_cfg.update({            
            'wlan_cfg': wlan_cfg,
            'expected_subnet': expected_subnet,
            'linux_pc_untag_ip': '',
            'linux_pc_tag_ip': '',
            'conn_mode': conn_mode,
            'active_ap_list': active_ap_list,
            'station': target_sta,
            'pc1_interface': pc1_eth_port,
            'pc2_interface': pc2_eth_port,
            'lan_port_list': lan_port_list,
            'vlan_id': vlan_id,
            'radio': target_sta_radio,
            'all_aps_mac_list': all_aps_mac_list,
            'active_aps_mac_list': active_aps_mac_list,
            })
        
        test_cfgs = define_test_configuration(fcfg, input_cfg)
        
        test_order = 1
        test_added = 0
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params,
                                     test_order, exc_level, is_cleanup) > 0:
                test_added += 1
    
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

#----------------------------------#
#     Access Method
#----------------------------------#    

if __name__ == "__main__":    
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
    

