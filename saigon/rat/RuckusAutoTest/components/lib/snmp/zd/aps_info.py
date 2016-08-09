'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.14
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for zd_ap information getting/setting/verify methods.
'''

import logging
import copy
import time

from RuckusAutoTest.common.Ratutils import get_random_string
from RuckusAutoTest.common.lib_Constant import get_radio_mode_by_ap_model
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.common import lib_Constant as const

ZD_AP_MIB = 'RUCKUS-ZD-AP-MIB'
ZD_AP_CONFIG_TABLE = 'ruckusZDAPConfigTable'
OBJNAME_INDEX_TEMP = '%s.%s'

#zd_ap objects abbr and snmp full name mapping.
zd_ap_abbr_name_mapping = {'mac_addr':'ruckusZDAPConfigMacAddress',
                           'device_name':'ruckusZDAPConfigDeviceName',
                           'desc':'ruckusZDAPConfigDescription',
                           'location':'ruckusZDAPConfigLocation',
                           'gps_latitude':'ruckusZDAPConfigGpsLatitude',
                           'gps_longitude':'ruckusZDAPConfigGpsLongitude',
                           'ip_version': 'ruckusZDAPConfigIPVersion',
                           'ip_addr_mode':'ruckusZDAPConfigIpAddressSettingMode',
                           'ip_addr':'ruckusZDAPConfigIpAddress',
                           'ip_addr_mask':'ruckusZDAPConfigIpAddressMask',
                           'ip_gateway':'ruckusZDAPConfigGatewayIpAddress',
                           'ip_pri_dns':'ruckusZDAPConfigPrimaryDnsIpAddress',
                           'ip_sec_dns':'ruckusZDAPConfigSecondaryDnsIpAddress',
                           'ipv6_mode': 'ruckusZDAPConfigIpV6AddressSettingMode',
                           'ipv6_addr':'ruckusZDAPConfigIpV6Address',
                           'ipv6_prefix_len':'ruckusZDAPConfigIpV6PrefixLen',
                           'ipv6_gateway':'ruckusZDAPConfigGatewayIpV6Address',
                           'ipv6_pri_dns':'ruckusZDAPConfigPrimaryDnsIpV6Address',
                           'ipv6_sec_dns':'ruckusZDAPConfigSecondaryDnsV6IpAddress',
                           'radio_type':'ruckusZDAPConfigRadioType',
                           'radio_24_channel':'ruckusZDAPConfigRadioChannel24',
                           'radio_24_tx_power':'ruckusZDAPConfigRadioTxPowerLevel24',
                           'radio_24_wlan_group':'ruckusZDAPConfigRadioWlanGroup24',
                           'radio_5_channel':'ruckusZDAPConfigRadioChannel5',
                           'radio_5_tx_power':'ruckusZDAPConfigRadioTxPowerLevel5',
                           'radio_5_wlan_group':'ruckusZDAPConfigRadioWlanGroup5',
                           'mesh_mode':'ruckusZDAPConfigMeshConfigurationMode',
                           'uplink_mode':'ruckusZDAPConfigUplinkSelectionMode',
                           'approve_mode':'ruckusZDAPConfigApproveMode',
                           'admin':'ruckusZDAPConfigManagementAdmin',}

#The snmp dict config template.
SNMP_CONF = {'mac_addr':'-',
             'device_name':'-',
             'desc':'-',
             'location':'-',
             'gps_latitude':'-',
             'gps_longitude':'-',
             'ip_version': '-',
             'ip_addr_mode':'-',
             'ip_addr':'-',
             'ip_addr_mask':'-',
             'ip_gateway':'-',
             'ip_pri_dns':'-',
             'ip_sec_dns':'-',
             'ipv6_mode': '-',
             'ipv6_addr':'-',
             'ipv6_prefix_len':'-',
             'ipv6_gateway':'-',
             'ipv6_pri_dns':'-',
             'ipv6_sec_dns':'-',
             'radio_type':'-',
             'radio_24_channel':'-',
             'radio_24_tx_power':'-',
             'radio_24_wlan_group':'-',
             'radio_5_channel':'-',
             'radio_5_tx_power':'-',
             'radio_5_wlan_group':'-',
             'mesh_mode':'-',
             'uplink_mode':'-',
             'approve_mode':'-',
             'admin':'-',
             }

#Object abbr and convert/format func mapping. 
col_get_func_mapping = {'mac_addr': helper.format_mac_address,
                        'radio_type': helper.get_name_from_desc,
                        'ip_version': helper.get_name_from_desc,
                        'ip_addr_mode': helper.convert_ip_addr_mode,
                        'ipv6_mode': helper.convert_ip_addr_mode,
                        'radio_24_channel': helper.convert_channel_to_name,
                        'radio_5_channel': helper.convert_channel_to_name,
                        'radio_24_tx_power': helper.get_name_from_desc,
                        'radio_5_tx_power': helper.get_name_from_desc,
                        'mesh_mode': helper.get_name_from_desc,
                        'uplink_mode': helper.get_name_from_desc,
                        'approve_mode': helper.get_name_from_desc,
                        'admin': helper.get_name_from_desc,
                        'radio_5_tx_power': helper.convert_channel_tx_power,
                        'radio_24_tx_power': helper.convert_channel_tx_power,
                        }

#Read-write object abbr and data type mapping. 
rw_obj_type_mapping = {#'mac_addr':'STRING', #
                       'device_name':'STRING', #1..64
                       'desc':'STRING', #1..64
                       'location':'STRING', #1..64
                       'gps_latitude':'STRING', #1..16
                       'gps_longitude':'STRING', #1..16
                       'ip_version': 'INTEGER', #1: ipv4(1), 2: ipv6(2), 3: dualstack(3)
                       'ip_addr_mode':'INTEGER', #1: admin-by-zd(1) 2: admin-by-dhcp(2) 3: admin-by-ap(3)
                       'ip_addr':'IPAddress', #
                       'ip_addr_mask':'IPAddress', #
                       'ip_gateway':'IPAddress', #
                       'ip_pri_dns':'IPAddress', #
                       'ip_sec_dns':'IPAddress', #
                       'ipv6_mode': 'INTEGER', #1: admin-by-zd(1), 2: admin-by-autoconfig(2), 3: admin-by-ap(3)                       
                       'ipv6_addr':'STRING', #2..40
                       'ipv6_prefix_len':'INTEGER', #3..128
                       'ipv6_gateway':'STRING', #2..40
                       'ipv6_pri_dns':'STRING', #2..40
                       'ipv6_sec_dns':'STRING', #2..40
                       #'radio_type':'INTEGER', #1: ieee80211bg(1)  2: ieee80211na(2) 3: ieee80211a(3) 4: ieee80211n(4) 5: ieee80211ng(5)
                       'radio_24_channel':'INTEGER', #0..11  The AP Channel selection on the 2.4 GHz radio.                       #  The AP radio channel, selectable 0, 1-11,   0    : auto channel selection,  1-11 : specific channel selection.
                       'radio_24_tx_power':'INTEGER', #1: auto(1)  2: full(2) 3: half-full(3) 4: quarter-full(4) 5: one-eighth-full(5) 6: one-tenth-full(6)
                       'radio_24_wlan_group':'STRING', #1..63
                       'radio_5_channel':'INTEGER', #0, 36..165  The AP Channel selection on the 5 GHz radio.  The AP radio channel, selectable 0, 36-165,
                                #  0    : auto channel selection,  36-165 : specific channel selection. It is ruled by country c
                       'radio_5_tx_power':'INTEGER', #1: auto(1) 2: full(2) 3: half-full(3) 4: quarter-full(4) 5: one-eighth-full(5) 6: one-tenth-full(6)
                       'radio_5_wlan_group':'STRING', #1..63
                       'mesh_mode':'INTEGER', #1: auto(1) 2: root-ap(2) 3: mesh-ap(3) 4: disabled(4)
                       'uplink_mode':'INTEGER', #1: smart(1) 2: manual(2)
                       'approve_mode':'INTEGER', #1: approved(1) 2: not-approved(2)
                       'admin':'INTEGER', #1: delete(1) 2: associated(2)
                       }
#Read-write object orders list when create a zd_ap. E.g. ssid is the first, rowstatus is the last one.
rw_obj_keys_order_list = ['device_name', 'desc', 'location', 'gps_latitude', 'gps_longitude','ip_version',
                          'ip_addr_mode', 'ip_addr', 'ip_addr_mask', 'ip_gateway', 'ip_pri_dns', 'ip_sec_dns',
                          'ipv6_mode', 'ipv6_addr', 'ipv6_prefix_len', 'ipv6_gateway', 'ipv6_pri_dns', 'ipv6_sec_dns',
                          'radio_24_channel', 'radio_24_tx_power', 'radio_24_wlan_group',
                          'radio_5_channel', 'radio_5_tx_power', 'radio_5_wlan_group',
                          'mesh_mode', 'uplink_mode', 'approve_mode', 'admin']

#=============================================#
#             Access Methods            
#=============================================#
def get_zd_aps_by_mac_addr(snmp, ap_mac_list = []):
    '''
    Get ZD ap information based on mac addr list.
    If ap_mac_list is empty, then get all ap information.
    '''
    aps_dict = {}
    
    if not ap_mac_list:
        ap_index_mac_mapping = get_zd_ap_index_value_mapping(snmp)
        ap_mac_list = ap_index_mac_mapping.values()
        
    for mac_addr in ap_mac_list:        
        ap_info_dict = get_zd_aps_by_key_value(snmp, 'mac_addr', helper.format_mac_address(mac_addr))
        aps_dict.update(ap_info_dict)
                        
    return aps_dict         

def parsing_ap_info(snmp_original_d):
    '''
    Parsing the result and get servers information. Key is server id, Value is server detail information.
    '''
    #Get all server index.
    zd_ap_id_list = []
    for key in snmp_original_d.keys():
        oid_list = key.split('.')
        zd_ap_mac_addr = zd_ap_abbr_name_mapping['mac_addr']
        if compare(oid_list[0],zd_ap_mac_addr,'eq'):
            zd_ap_id_list.append(oid_list[1])
    
    zd_aps_d = {}
    if zd_ap_id_list:
        for ap_id in zd_ap_id_list:        
            zd_ap_info = helper.parsing_snmp_result(snmp_original_d, zd_ap_abbr_name_mapping, ap_id, _convert_zd_ap_snmp_values)
            zd_aps_d[ap_id] = zd_ap_info
    
    return zd_aps_d 

def get_zd_aps_by_key_value(snmp, key_obj_name = 'mac_addr', key_value = '*'):
    '''
    Get zd_ap information by specified column, and the value, default is name.
    If key_value is *, will get all zd_aps.
    '''
    return helper.get_items_by_key_value(snmp, ZD_AP_MIB, zd_ap_abbr_name_mapping, 
                                  key_obj_name, key_value, _convert_zd_ap_snmp_values)

def get_zd_ap_index_value_mapping(snmp, key_obj_name = 'mac_addr'):
    '''
    Get all zd_ap index and column [obj_abbr] value mapping.
    '''
    oid = zd_ap_abbr_name_mapping[key_obj_name]
    zd_ap_index_value_mapping = helper.get_index_value_mapping(snmp, ZD_AP_MIB, oid)
    
    if zd_ap_index_value_mapping and key_obj_name == 'mac_addr':
        for key,value in zd_ap_index_value_mapping.items():
            zd_ap_index_value_mapping[key] = helper.format_mac_address(value)
            
    return zd_ap_index_value_mapping

def get_zd_ap_info_by_index(snmp, index, keys_list = []):
    '''
    Get zd_ap detail config based on zd_ap index. 
    '''
    return helper.get_item_detail_by_index(snmp, ZD_AP_MIB, zd_ap_abbr_name_mapping, 
                                    index, _convert_zd_ap_snmp_values, keys_list)
    
def verify_aps_dict_snmp_cli(snmp_aps_d, cli_aps_d):
    '''
    Verify the aps dict from snmp with cli values. Key is index, value is ap detail dict.
    '''  
    oids_d = helper.get_item_oids(ZD_AP_MIB, zd_ap_abbr_name_mapping)    
    res_d = helper.verify_items_dict(snmp_aps_d, cli_aps_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_aps_dict_snmp_gui(snmp_aps_d, gui_aps_d):
    '''
    Verify the aps dict from snmp with gui values. Key is index, value is ap detail dict.
    '''  
    oids_d = helper.get_item_oids(ZD_AP_MIB, zd_ap_abbr_name_mapping)
    res_d = helper.verify_items_dict(snmp_aps_d, gui_aps_d, _convert_gui_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_one_ap_snmp_cli(snmp_d, cli_d, oids_d = {}, index = None):
    '''
    Verify a ap config: snmp and cli values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(ZD_AP_MIB, zd_ap_abbr_name_mapping)    
    res_d = helper.verify_one_item_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d, index)

    return res_d

def verify_one_ap_snmp_gui(snmp_d, gui_d, oids_d = {}, index = None):
    '''
    Verify a ap config: snmp and gui values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(ZD_AP_MIB, zd_ap_abbr_name_mapping)
    res_d = helper.verify_one_item_config(snmp_d, gui_d, _convert_gui_to_snmp_temp, _item_verify_is_pass, oids_d, index)

    return res_d

def verify_aps_test_data_snmp(snmp_aps_d, test_data_aps_d):
    '''
    Verify ap information: pre-config data and values from snmp. 
    '''
    oids_d = helper.get_item_oids(ZD_AP_MIB, zd_ap_abbr_name_mapping)
    res_aps_d = helper.verify_items_dict(snmp_aps_d, test_data_aps_d, _convert_zd_ap_snmp_values, None, oids_d)
    
    return res_aps_d

def verify_update_zd_ap(snmp, zd_ap_id, update_cfg_list):
    '''
    Update the zd_ap information, and then verify the value is updated.
    '''
    oids_d = helper.get_item_oids(ZD_AP_MIB, zd_ap_abbr_name_mapping)

    index = 0
    res_zd_aps_d = {}
    
    need_restart_ap = False
    for zd_ap_cfg in update_cfg_list:
        index += 1
        
        update_zd_ap(snmp, zd_ap_cfg, zd_ap_id)
        keys_list = zd_ap_cfg.keys()
        
        time.sleep(15)
        ip_setting_list = ['ip_version', 'ip_addr_mode', 'ip_mode','ip_addr', 'ip_addr_mask', 'ip_gateway', 'ip_pri_dns', 'ip_sec_dns',
                           'ipv6_mode', 'ipv6_addr', 'ipv6_gateway', 'ipv6_prefix_len', 'ipv6_pri_dns', 'ipv6_sec_dns']
        
        #need_restart_ap = False
        ap_restarted = False
        for key in ip_setting_list:
            if zd_ap_cfg.has_key(key):
                need_restart_ap = True
                ap_restarted = True
                break
        #if configure in "ip_setting_list", ap will reboot.
        if ap_restarted:
            time.sleep(20)
        
        snmp_zd_ap_d = get_zd_ap_info_by_index(snmp, zd_ap_id, keys_list)
        
        res_d = helper.verify_one_item_config(snmp_zd_ap_d, zd_ap_cfg, _convert_zd_ap_snmp_values, None, oids_d, index)
        
        if res_d:
            res_zd_aps_d[index] = {'Config': zd_ap_cfg, 'Result': res_d}

    return res_zd_aps_d, need_restart_ap

def verify_delete_aps(snmp, ap_mac_addr_list, is_wait_ap_join = True):
    '''
    Delete a ap and verify it is deleted. 
    '''
    err_mac_addr_list = []
    
    #Format mac addr.
    i=1
    for i in range(0, len(ap_mac_addr_list)):
        ap_mac_addr = ap_mac_addr_list[i]
        ap_mac_addr_list[i] = helper.format_mac_address(ap_mac_addr)
    
    original_index_mac_addr_mapping = get_zd_ap_index_value_mapping(snmp)
    for ap_mac_addr in ap_mac_addr_list:
        index = helper.get_dict_key_by_value(original_index_mac_addr_mapping, ap_mac_addr)
        delete_ap_by_index(snmp,index)
        
        #Wait 20 seconds, and check the ap is deleted.
        time.sleep(5)
        index_mac_addr_mapping = get_zd_ap_index_value_mapping(snmp)
        current_ap_mac_addr_list = index_mac_addr_mapping.values()
    
        if ap_mac_addr in current_ap_mac_addr_list:
            err_mac_addr_list.append(ap_mac_addr)
            
    #Wait for some time till the ap join automatically.
    if is_wait_ap_join:
        wait_4_ap_join(snmp, ap_mac_addr_list)
    
    return err_mac_addr_list

def wait_4_ap_join(snmp, ap_mac_addr_list, retries = 10, delay = 20):
    '''
    Wait for the ap in ap mac addr list is joined automatically.
    '''
    err_ap_mac_list = []
    
    for ap_mac in ap_mac_addr_list:
        i = 1
        result = False
        for i in range(0,retries):
            index_mac_addr_mapping = get_zd_ap_index_value_mapping(snmp)
            current_ap_mac_addr_list = index_mac_addr_mapping.values()
            if ap_mac not in current_ap_mac_addr_list:
                time.sleep(delay)
            else:
                result = True
                break
        if not result:
            err_ap_mac_list.append(ap_mac)
            
    if err_ap_mac_list:
        logging.warning('The aps are not joined successfully: %s' % err_ap_mac_list)
        
    return err_ap_mac_list
    
def update_zd_ap(snmp, zd_ap_cfg, index):
    '''
    Update ap information. 
    '''
    new_zd_ap_cfg = {'index' : index}
    new_zd_ap_cfg.update(zd_ap_cfg) 

    _update_zd_ap_config(snmp, new_zd_ap_cfg, 2)
    

def delete_ap_by_index(snmp, index):
    '''
    Delete a ap by specified index.
    '''
    zd_ap_cfg = {'index' : index}
    return _update_zd_ap_config(snmp, zd_ap_cfg, 3)
    
def delete_ap_by_mac_addr(snmp, mac_addr):
    '''
    Delete the ap with specified mac address.
    '''
    index_mac_addr_mapping = get_zd_ap_index_value_mapping(snmp)    
    index = helper.get_dict_key_by_value(index_mac_addr_mapping, mac_addr)
    
    return delete_ap_by_index(snmp, index)

def gen_zd_ap_update_cfg(wg_name = None):
    '''
    Generate test config for update zd_ap: zd_ap config for a new one, and detail config to update it.
    Notes:
        1. Can't set radio_5_channel if zd radio don't include 5G.
        2. Can't set uplink_mode to 'manual(2)', it is always smart and no value in GUI and CLI.
        3. Can't set approve_mode to 'not-approved(2)'.        
        4. After set admin as 'delete(1)', the ap is deleted from zd.
    '''
    update_cfg_list = [dict(device_name = 'RuckusAPName', desc = 'RuckusDescription', location = 'Shenzhen',
                            gps_latitude = '26.2888', gps_longitude = '-120.02333',),
                       dict(device_name = 'RuckusAP-Test', desc = 'UpdateDescForTest', location = 'Seattle',
                            gps_latitude = '25.2888', gps_longitude = '-123.02333',),
                       #If change ip address,  may cause ap has same ip address.
                       dict(ip_addr_mode = 'admin-by-zd(1)', #ip_addr = '192.168.0.201', 
                            ip_addr_mask = '255.255.255.0',ip_gateway = '192.168.32.253', ip_pri_dns = '192.168.0.252', ip_sec_dns = '192.168.0.251',
                            ),
                       dict(ip_addr_mode = 'admin-by-dhcp(2)'),
                            
                       dict(ip_addr_mode = 'admin-by-ap(3)'),
                       #dict(ipv6_addr='',ipv6_prefix_len='0',ipv6_gateway='',ipv6_pri_dns='',ipv6_sec_dns='',),

                       #chen.tao @2013-11-18, to fix ZF-5873                       
                       #dict(radio_24_channel = '0', radio_24_tx_power = 'auto(1)', radio_24_wlan_group = 'Default',),  
                       #dict(radio_24_channel = '4', radio_24_tx_power = 'one-tenth-full(6)', radio_24_wlan_group = 'Default',),
                       #dict(radio_24_channel = '11', radio_24_tx_power = 'full(2)', radio_24_wlan_group = 'Default',),

                       dict(radio_24_channel = '0', radio_24_tx_power = 'auto(25)', radio_24_wlan_group = 'Default',),  
                       dict(radio_24_channel = '4', radio_24_tx_power = 'one-tenth-full(24)', radio_24_wlan_group = 'Default',),
                       dict(radio_24_channel = '11', radio_24_tx_power = 'full(0)', radio_24_wlan_group = 'Default',),
                      
                       #chen.tao @2013-11-18, to fix ZF-5873                       
                       
                       
                       #dict(radio_5_channel = '0', radio_5_tx_power = 'half-full(3)', radio_5_wlan_group = 'Default',),
                       #dict(radio_5_channel = '43', radio_5_tx_power = 'quarter-full(4)', radio_5_wlan_group = 'Default',),
                       #dict(radio_5_channel = '165', radio_5_tx_power = 'one-eighth-full(5)', radio_5_wlan_group = 'Default',),
                       #dict(mesh_mode = 'auto(1)',),
                       #dict(mesh_mode = 'root-ap(2)',),
                       #dict(mesh_mode = 'mesh-ap(3)',),
                       #dict(mesh_mode = 'disabled(4)',),
                       #dict(uplink_mode = 'smart(1)'),
                       dict(approve_mode = 'approved(1)',),
                       dict(admin = 'associated(2)',),
                       ]
    
    if wg_name:
        update_cfg_list.append(dict(radio_24_wlan_group = wg_name))
        update_cfg_list.append(dict(radio_24_wlan_group = 'Default'))
        #update_cfg_list.append(dict(radio_5_wlan_group = wg_name))
        #update_cfg_list.append(dict(radio_5_wlan_group = 'Default'))
    
    return update_cfg_list

def gen_ap_cfg_negative():
    '''
    Generate negative input for wlan group config.
    '''
    type = 'alpha'
    str_17 = get_random_string(type,17)
    str_41 = get_random_string(type,41)
    str_65 = get_random_string(type,65)
    
    ap_cfg = {}
    
    ap_cfg['device_name'] = str_65 #STRING', #1..64
    ap_cfg['desc'] = str_65 #STRING', #1..64
    ap_cfg['location'] = str_65 #STRING', #1..64
    ap_cfg['gps_latitude'] = str_17 #STRING', #1..16
    ap_cfg['gps_longitude'] = str_17 #STRING', #1..16
    ap_cfg['ip_addr_mode'] = '4' #INTEGER', #1: admin-by-zd(1) 2: admin-by-dhcp(2) 3: admin-by-ap(3)
    ap_cfg['ip_addr'] = '256.255.255.255' #IPAddress', #
    ap_cfg['ip_addr_mask'] = '256.255.255.255' #IPAddress', #
    ap_cfg['ip_gateway'] = '256.255.255.255' #IPAddress', #
    ap_cfg['ip_pri_dns'] = '256.255.255.255' #IPAddress', #
    ap_cfg['ip_sec_dns'] = '256.255.255.255' #IPAddress', #                       
    ap_cfg['ipv6_addr'] = str_41 #STRING', #2..40
    ap_cfg['ipv6_prefix_len'] = '129' #INTEGER', #3..128
    ap_cfg['ipv6_gateway'] = str_41 #STRING', #2..40
    ap_cfg['ipv6_pri_dns'] = str_41 #STRING', #2..40
    ap_cfg['ipv6_sec_dns'] = str_41 #STRING', #2..40    
    ap_cfg['radio_24_channel'] = '12' #INTEGER', #0..11  The AP Channel selection on the 2.4 GHz radio.                       #  The AP radio channel, selectable 0, 1-11,   0    : auto channel selection,  1-11 : specific channel selection.
    #zj 2013_10_23 The AP Tx Power level selection on the 2.4 GHz radio
    #ap_cfg['radio_24_tx_power'] = '7' #INTEGER', #1: auto(1)  2: full(2) 3: half-full(3) 4: quarter-full(4) 5: one-eighth-full(5) 6: one-tenth-full(6)
    ap_cfg['radio_24_tx_power'] = '26' #INTEGER', # auto(25) | 0 to 24 corresponding to 0 to -24dB from max power.Now to be compatible with web, if txpower is more than 10, txpower will be set to 24(Min).
    ap_cfg['radio_24_wlan_group'] = str_65 #STRING', #1..63
    ap_cfg['radio_5_channel'] = '30' #INTEGER', #0, 36..165  The AP Channel selection on the 5 GHz radio.  The AP radio channel, selectable 0, 36-165,
                                    #  0    : auto channel selection,  36-165 : specific channel selection. It is ruled by country c
    #zj 2013_10_23
    ap_cfg['radio_5_tx_power'] = '26' #INTEGER', #same with radio_24_tx_power
    ap_cfg['radio_5_wlan_group'] = str_65 #STRING', #1..63
    ap_cfg['mesh_mode'] = '5'  #INTEGER', #1: auto(1) 2: root-ap(2) 3: mesh-ap(3) 4: disabled(4)
    ap_cfg['uplink_mode'] = '3' #INTEGER', #1: smart(1) 2: manual(2)
    ap_cfg['approve_mode'] = '3' #INTEGER', #1: approved(1) 2: not-approved(2)
    ap_cfg['admin'] = '3' #INTEGER', #1: delete(1) 2: associated(2)
        
    return ap_cfg

def update_ap_cfg_one_by_one(snmp, index, test_cfg):
    '''
    Update server config items, one by one.
    '''
    res_d = {}
    for obj_name, value in test_cfg.items():
        oid = zd_ap_abbr_name_mapping[obj_name]
        obj_type = rw_obj_type_mapping[obj_name]
        
        
        res = helper.update_single_node_value(snmp, ZD_AP_MIB, oid, index, obj_type, value)
        
        if res:
            res_d.update({obj_name : res})
        
    return res_d
#=============================================#
#             Private Methods            
#=============================================#
def _convert_zd_ap_snmp_values(zd_ap_d):
    '''
    Convert zd_ap values based on col_get_func_mapping dict. 
    '''
    for key, value in zd_ap_d.items():
        new_value = value
        if key in col_get_func_mapping.keys():
            convert_func = col_get_func_mapping[key]
            new_value = convert_func(value)
            
        if key.find('wlan_group')  > -1:
            if new_value == '':
                new_value = 'Default'

        zd_ap_d[key] = new_value

    return zd_ap_d

def _convert_cli_to_snmp_temp(cli_zd_ap_d):
    '''
    Convert cli zd_ap dict to same snmp dict structure.
    '''
    new_cli_zd_ap_d = copy.deepcopy(SNMP_CONF)

    new_cli_zd_ap_d['mac_addr'] = cli_zd_ap_d['MAC Address']
    new_cli_zd_ap_d['device_name'] = cli_zd_ap_d['Device Name']
    new_cli_zd_ap_d['desc'] = cli_zd_ap_d['Description']
    new_cli_zd_ap_d['location'] = cli_zd_ap_d['Location']
    gps = cli_zd_ap_d['GPS']

    if gps and gps.find(',') > 0:
        new_cli_zd_ap_d['gps_latitude'] = gps.split(',')[0]
        new_cli_zd_ap_d['gps_longitude'] = gps.split(',')[1]
    else:
        new_cli_zd_ap_d['gps_latitude'] = ''
        new_cli_zd_ap_d['gps_longitude'] = ''
        
    network_dict = cli_zd_ap_d['Network Setting']
    
    ip_version = network_dict['Protocol mode'].lower() #ipv4 and ipv6
    #ip_type = network_dict['IP Type']  #static or dhcp
    if 'ipv4' in ip_version:
        if 'ipv6' in ip_version:
            new_ip_version = const.DUAL_STACK
        else:
            new_ip_version = const.IPV4
    elif 'ipv6' in ip_version:
        new_ip_version = const.IPV6
    else:
        #chen.tao 2014-01-15 to fix ZF-6530
        new_ip_version = 'useparentsetting'
        #chen.tao 2014-01-15 to fix ZF-6530
    new_cli_zd_ap_d['ip_version'] = new_ip_version
    #chen.tao 2014-01-15 to fix ZF-6530
    if new_ip_version in [const.DUAL_STACK, const.IPV4,'useparentsetting']:
    #chen.tao 2014-01-15 to fix ZF-6530
        new_cli_zd_ap_d['ip_addr_mode'] = network_dict['Device IP Settings']
                                  
        if compare(new_cli_zd_ap_d['ip_addr_mode'], "Keep AP's Setting",'eq'):
            new_cli_zd_ap_d['ip_addr_mode'] = 'as_is'
        
        new_cli_zd_ap_d['ip_addr'] = network_dict['IP Address']
        new_cli_zd_ap_d['ip_addr_mask'] = network_dict['Netmask']
        new_cli_zd_ap_d['ip_gateway'] = network_dict['Gateway']
        new_cli_zd_ap_d['ip_pri_dns'] = network_dict['Primary DNS Server']
        new_cli_zd_ap_d['ip_sec_dns'] = network_dict['Secondary DNS Server']
    #chen.tao 2014-01-15 to fix ZF-6530
    if new_ip_version in [const.DUAL_STACK, const.IPV6,'useparentsetting']:
    #chen.tao 2014-01-15 to fix ZF-6530
        ipv6_addr_mode = network_dict['Device IPv6 Settings']  #Keep AP's Setting
        if ipv6_addr_mode == "Keep AP's Setting":
            new_cli_zd_ap_d['ipv6_mode'] = 'as_is'
        elif 'auto' in ipv6_addr_mode.lower():
            new_cli_zd_ap_d['ipv6_mode'] = 'auto'
        else:
            new_cli_zd_ap_d['ipv6_mode'] = ipv6_addr_mode
        
        new_cli_zd_ap_d['ipv6_addr'] = network_dict['IPv6 Address']
        new_cli_zd_ap_d['ipv6_prefix_len'] = network_dict['IPv6 Prefix Length']
        new_cli_zd_ap_d['ipv6_gateway'] = network_dict['IPv6 Gateway']
        new_cli_zd_ap_d['ipv6_pri_dns'] = network_dict['IPv6 Primary DNS Server']
        new_cli_zd_ap_d['ipv6_sec_dns'] = network_dict['IPv6 Secondary DNS Server']

    radio_24g_key = 'Radio b/g/n'
    radio_5g_key = 'Radio a/n'
    #@ZJ 20150121 ZF-11742 behavior change of AP radio: ac  on 9.5.0.5.110
    radio_5g_key_new = 'Radio a/n/ac'
    
    if cli_zd_ap_d.has_key(radio_24g_key):       
        radio_24g_dict = cli_zd_ap_d[radio_24g_key]  
        #radio_24g_channelization = radio_24g_dict['Channelization']
        #radio_24g_wlan_service = radio_24g_dict['WLAN Services enabled']
        radio_24g_channel = radio_24g_dict['Channel']
        radio_24g_power = radio_24g_dict['Tx. Power']
        radio_24g_wlan_group = radio_24g_dict['WLAN Group Name']
        
        new_cli_zd_ap_d['radio_24_channel'] = radio_24g_channel
        new_cli_zd_ap_d['radio_24_tx_power'] = radio_24g_power
        new_cli_zd_ap_d['radio_24_wlan_group'] = radio_24g_wlan_group
        
    if cli_zd_ap_d.has_key(radio_5g_key):
        radio_5g_dict = cli_zd_ap_d[radio_5g_key]
        #radio_5g_channelization = radio_5g_dict['Channelization']
        #radio_5g_wlan_service = radio_5g_dict['WLAN Services enabled']
        radio_5g_channel = radio_5g_dict['Channel']
        radio_5g_power = radio_5g_dict['Tx. Power']
        radio_5g_wlan_group = radio_5g_dict['WLAN Group Name']
        
        new_cli_zd_ap_d['radio_5_channel'] = radio_5g_channel
        new_cli_zd_ap_d['radio_5_tx_power'] = radio_5g_power
        new_cli_zd_ap_d['radio_5_wlan_group'] = radio_5g_wlan_group
    #@ZJ 20150121 ZF-11742 behavior change of AP radio: ac  on 9.5.0.5.110     
    if cli_zd_ap_d.has_key(radio_5g_key_new):
        radio_5g_dict = cli_zd_ap_d[radio_5g_key_new]
        radio_5g_channel = radio_5g_dict['Channel']
        radio_5g_power = radio_5g_dict['Tx. Power']
        radio_5g_wlan_group = radio_5g_dict['WLAN Group Name']
        
        new_cli_zd_ap_d['radio_5_channel'] = radio_5g_channel
        new_cli_zd_ap_d['radio_5_tx_power'] = radio_5g_power
        new_cli_zd_ap_d['radio_5_wlan_group'] = radio_5g_wlan_group    
       
  
    ap_model = cli_zd_ap_d['Model']    
    radio_type_list = get_radio_mode_by_ap_model(ap_model)
    radio_type = ''
    for type in radio_type_list:
        if radio_type:
            radio_type = radio_type + ','
        radio_type = radio_type + 'ieee80211%s' % type
    
    new_cli_zd_ap_d['radio_type'] = radio_type

    mesh_key = 'Mesh'    
    new_cli_zd_ap_d['uplink_mode'] = 'smart'
    if cli_zd_ap_d.has_key(mesh_key):
        mesh_enabled = cli_zd_ap_d[mesh_key]['Status']
        new_cli_zd_ap_d['mesh_mode'] = mesh_enabled
        if helper.is_enabled(mesh_enabled) and cli_zd_ap_d[mesh_key].has_key('Mode'):
            mesh_mode = cli_zd_ap_d[mesh_key]['Mode']
            #Convert mesh mode values.
            mesh_mode_mapping = {'Root AP': 'root-ap', 'Mesh AP': 'mesh-ap', 'Auto': 'auto', 'Disabled': 'disabled'}
            if mesh_mode_mapping.has_key(mesh_mode):
                mesh_mode = mesh_mode_mapping[mesh_mode]
                
            new_cli_zd_ap_d['mesh_mode'] = mesh_mode
            
            #Update uplink mode value.
            if compare(mesh_mode, 'auto','eq') or compare(mesh_mode, 'mesh-ap','eq'):
                if cli_zd_ap_d.has_key('Uplink'):
                    new_cli_zd_ap_d['uplink_mode'] = cli_zd_ap_d['Uplink']['Status']                

    if compare(cli_zd_ap_d['Approved'], 'yes', 'eq'):
        new_cli_zd_ap_d['approve_mode'] = 'approved'
    else:
        new_cli_zd_ap_d['approve_mode'] = 'not-approved'

    #TBU: no value in cli and gui now. 
    new_cli_zd_ap_d['admin'] = 'associated'    

    return new_cli_zd_ap_d

def _convert_gui_to_snmp_temp(gui_zd_ap_d):
    '''
    Convert gui zd_ap dict to same snmp dict structure.
    '''
    new_gui_zd_ap_d = copy.deepcopy(SNMP_CONF)
    
    new_gui_zd_ap_d['mac_addr'] = gui_zd_ap_d['mac_addr']

    #new_gui_zd_ap_d.update(gui_zd_ap_d)
    if gui_zd_ap_d.has_key('general_info'):
        general_info_dict = gui_zd_ap_d['general_info']
        
        new_gui_zd_ap_d['device_name'] = general_info_dict['device_name']
        new_gui_zd_ap_d['desc'] = general_info_dict['description']
        new_gui_zd_ap_d['location'] = general_info_dict['device_location']
        new_gui_zd_ap_d['gps_latitude'] = general_info_dict['gps_latitude']
        new_gui_zd_ap_d['gps_longitude'] = general_info_dict['gps_longitude']
        
    if gui_zd_ap_d.has_key('ip_config'):
        ip_config_dict = gui_zd_ap_d['ip_config']
        
        new_gui_zd_ap_d['ip_addr_mode'] = ip_config_dict['ip_mode']
        
        if compare(ip_config_dict['ip_mode'], 'manual', 'eq'):
            new_gui_zd_ap_d['ip_addr'] = gui_zd_ap_d['ip_param']['ip_addr']
            new_gui_zd_ap_d['ip_addr_mask'] = gui_zd_ap_d['ip_param']['net_mask']
            new_gui_zd_ap_d['ip_gateway'] = gui_zd_ap_d['ip_param']['gateway']
            new_gui_zd_ap_d['ip_pri_dns'] = gui_zd_ap_d['ip_param']['pri_dns']
            new_gui_zd_ap_d['ip_sec_dns'] = gui_zd_ap_d['ip_param']['sec_dns']
            
        '''
        new_gui_zd_ap_d['ipv6_mode'] = ip_config_dict['ipv6_mode']
        if compare(ip_config_dict['ipv6_mode'], 'manual', 'eq'):
            new_gui_zd_ap_d['ipv6_addr'] = gui_zd_ap_d['ip_param']['ipv6_addr']
            new_gui_zd_ap_d['ipv6_prefix_len'] = gui_zd_ap_d['ip_param']['ipv6_prefix_len']
            new_gui_zd_ap_d['ipv6_gateway'] = gui_zd_ap_d['ip_param']['ipv6_gateway']
            new_gui_zd_ap_d['ipv6_pri_dns'] = gui_zd_ap_d['ip_param']['ipv6_pri_dns']
            new_gui_zd_ap_d['ipv6_sec_dns'] = gui_zd_ap_d['ip_param']['ipv6_sec_dns']            
        '''
    
    radio_config_dict = gui_zd_ap_d['radio_config']
    
    radio_24g_dict = {}
    radio_5g_dict = {}
    
    radio_type = ''
    if radio_config_dict.has_key('bg'):
        radio_type = 'ieee80211bg'
        radio_24g_dict = radio_config_dict['bg']        
    
    if radio_config_dict.has_key('ng'):
        if radio_type:
            radio_type = radio_type + ','
            
        radio_type = radio_type + 'ieee80211ng'
        radio_24g_dict = radio_config_dict['ng']
    
    if radio_config_dict.has_key('na'):
        if radio_type:
            radio_type = radio_type + ','

        radio_type = radio_type + 'ieee80211na'
        radio_5g_dict = radio_config_dict['na']
    
    #1: ieee80211bg(1) 2: ieee80211na(2) 3: ieee80211a(3) 4: ieee80211n(4) 5: ieee80211ng(5)
    new_gui_zd_ap_d['radio_type'] = radio_type
        
    group_cfg_str = 'Group Config'
    
    if radio_24g_dict:
        radio_24g_channel = radio_24g_dict['channel']
        radio_24g_power = radio_24g_dict['power']
        radio_24g_wlan_group = radio_24g_dict['wlangroups']
        
        if compare(radio_24g_channel, group_cfg_str, 'eq'):
            radio_24g_channel = 'auto'
        if compare(radio_24g_power, group_cfg_str, 'eq'):
            radio_24g_power = 'auto'
        if compare(radio_24g_wlan_group, group_cfg_str, 'eq'):
            radio_24g_wlan_group = ''
    else:
        radio_24g_channel = 'auto'
        radio_24g_power = 'auto'
        radio_24g_wlan_group = ''
        
    new_gui_zd_ap_d['radio_24_channel'] = radio_24g_channel
    new_gui_zd_ap_d['radio_24_tx_power'] = radio_24g_power
    new_gui_zd_ap_d['radio_24_wlan_group'] = radio_24g_wlan_group
        
    if radio_5g_dict: 
        radio_5g_channel = radio_5g_dict['channel']
        radio_5g_power = radio_5g_dict['power']
        radio_5g_wlan_group = radio_5g_dict['wlangroups']
        
        if compare(radio_5g_channel, group_cfg_str, 'eq'):
            radio_5g_channel = 'auto'
        if compare(radio_5g_power, group_cfg_str, 'eq'):
            radio_5g_power = 'auto'
        if compare(radio_5g_wlan_group, group_cfg_str, 'eq'):
            radio_5g_wlan_group = ''
    else:
        radio_5g_channel = 'auto'
        radio_5g_power = 'auto'
        radio_5g_wlan_group = ''
            
    new_gui_zd_ap_d['radio_5_channel'] = radio_5g_channel
    new_gui_zd_ap_d['radio_5_tx_power'] = radio_5g_power
    new_gui_zd_ap_d['radio_5_wlan_group'] = radio_5g_wlan_group       
    
    if gui_zd_ap_d.has_key('mesh_config'):
        mesh_mode = gui_zd_ap_d['mesh_config']['mesh_mode']
        
        mesh_mapping = {'root':'root-ap','mesh':'mesh-ap', 'Auto':'auto', 'Disabled': 'disabled'}
        if mesh_mapping.has_key(mesh_mode):
            mesh_mode = mesh_mapping[mesh_mode]
        
        new_gui_zd_ap_d['mesh_mode'] = mesh_mode
        
        new_gui_zd_ap_d['uplink_mode'] = 'smart'
        if gui_zd_ap_d['mesh_config'].has_key('mesh_param'):
            mesh_param = gui_zd_ap_d['mesh_config']['mesh_param']
            if mesh_param.has_key('uplink_mode'):
                new_gui_zd_ap_d['uplink_mode'] =  mesh_param['uplink_mode']
    
    #Temp set the value for approve mode and admin. 
    new_gui_zd_ap_d['approve_mode'] = 'approved'
    new_gui_zd_ap_d['admin'] = 'associated'
    '''
    new_gui_zd_ap_d['approve_mode'] = gui_zd_ap_d['Approved']    
    if compare(gui_zd_ap_d['Approved'], 'yes', 'eq'):
        new_gui_zd_ap_d['approve_mode'] = 'approved'
    else:
        new_gui_zd_ap_d['approve_mode'] = 'not-approved'    
        
    new_gui_zd_ap_d['admin'] = gui_zd_ap_d['']    
    '''
        
    return new_gui_zd_ap_d

def _item_verify_is_pass(value_d, key):
    '''
    Check whether the item is no no need to verify.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''
    
    radio_24_keys_list = ['radio_24_channel', 'radio_24_tx_power', 'radio_24_wlan_group']    
    radio_5_keys_list = ['radio_5_channel', 'radio_5_tx_power', 'radio_5_wlan_group']
    radio_24_list = ['ieee80211bg', 'ieee80211n', 'ieee80211ng']
    radio_5_list = ['ieee80211na', 'ieee80211a']
    
    ipv4_keys_list = ['ip_addr_mode', 'ip_addr', 'ip_addr_mask', 'ip_gateway', 'ip_pri_dns', 'ip_sec_dns']
    ipv6_keys_list = ['ipv6_mode', 'ipv6_addr', 'ipv6_gateway', 'ipv6_prefix_len', 'ipv6_pri_dns', 'ipv6_sec_dns'] 
    
    if key == 'admin':
        is_pass = True
        message = "Don't need to verify admin, no value in CLI and GUI."
    elif key == 'uplink_mode':
        if compare(value_d['mesh_mode'], 'disabled', 'eq') or compare(value_d['mesh_mode'], 'root-ap', 'eq'):
            #Notes: If ap is root-ap or mesh is disabled, uplink mode is not displayed in cli.
            is_pass = True
            message = "Don't need to verify uplink mode when mesh is not enabled."
    elif key in radio_24_keys_list and value_d['radio_type'].lower() not in radio_24_list:
        is_pass = True
        message = "Don't need to verify 2.4G setting if radio type is %s" % radio_24_list
        logging.info("Key=%s, Message=%s" % (key, message))
    elif key in radio_5_keys_list and value_d['radio_type'].lower() not in radio_5_list:
        is_pass = True
        message = "Don't need to verify 5G setting if radio type is %s" % radio_5_list
        logging.info("Key=%s, Message=%s" % (key, message))
    else:
        if key in ipv4_keys_list and value_d['ip_version'] in [const.IPV6]:
            is_pass = True
            message = "Don't need to verify ipv4 information if version is ipv6"
        if key in ipv6_keys_list and value_d['ip_version'] in [const.IPV4]:
            is_pass = True
            message = "Don't need to verify ipv6 information if version is ipv4"
        else:
            if key in ipv4_keys_list and not compare(value_d['ip_addr_mode'], 'manual', 'eq'):
                is_pass = True
                message = "Don't need to verify ipv4 information if mode is not manual."
            elif key in ipv6_keys_list and not compare(value_d['ipv6_mode'], 'manual', 'eq'):
                is_pass = True
                message = "Don't need to verify ipv6 information if mode is not manual."        

    return is_pass, message

def _check_zd_ap_exist_by_index(snmp, index):
    '''
    Check wether the zd_ap with specified index exist. 
    Return true if exist, false if does not exist.
    '''
    # Check the zd_ap is created successfully.
    index_zd_ap_name_mapping = get_zd_ap_index_value_mapping(snmp)
    result = False
    if index_zd_ap_name_mapping and index_zd_ap_name_mapping.has_key(str(index)):
        result = True

    return result

def _update_zd_ap_config(snmp, zd_ap_cfg, flag):
    '''
    Update zd_ap: create on zd_ap, update some settings, delete the zd_ap.
    For ap information, only can update.        
    '''
    index = zd_ap_cfg['index']
    
    if flag == 3:
        #Delete the ap, set admin as 1.
        key = 'admin'        
        oid = zd_ap_abbr_name_mapping[key]
        obj_type = rw_obj_type_mapping[key]                
        value = '1'
        helper.update_single_node_value(snmp, ZD_AP_MIB, oid, index, obj_type, value)
    else:
        helper.update_objects_config(snmp, ZD_AP_MIB, zd_ap_abbr_name_mapping, 
                              rw_obj_type_mapping, rw_obj_keys_order_list, zd_ap_cfg, flag)        
