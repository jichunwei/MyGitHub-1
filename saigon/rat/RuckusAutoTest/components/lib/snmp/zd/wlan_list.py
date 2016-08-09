'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.14
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for wlan information getting/setting/verify methods.
'''

import logging
import copy
import time

from RuckusAutoTest.common.Ratutils import get_random_string
from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.components.lib.snmp import snmphelper as helper

WLAN_CONFIG_MIB = 'RUCKUS-ZD-WLAN-CONFIG-MIB'
WLAN_CONFIG_TABLE = 'ruckusZDWLANConfigTable'
OBJNAME_INDEX_TEMP = '%s.%s'

#Wlan objects abbr and snmp full name mapping.
wlan_abbr_name_mapping = {'ssid':'ruckusZDWLANConfigSSID',
                     'desc':'ruckusZDWLANConfigDescription',
                     'name':'ruckusZDWLANConfigName',
                     'service_type':'ruckusZDWLANConfigWLANServiceType',
                     'auth':'ruckusZDWLANConfigAuthentication',
                     'encrypt':'ruckusZDWLANConfigEncryption',
                     'wep_key_index':'ruckusZDWLANConfigWEPKeyIndex',
                     'wep_key':'ruckusZDWLANConfigWEPKey',
                     'wpa_cipher_type':'ruckusZDWLANConfigWPACipherType',
                     'wpa_key':'ruckusZDWLANConfigWPAKey',
                     'auth_server_id':'ruckusZDWLANConfigAuthenticationServerID',
                     'wireless_client':'ruckusZDWLANConfigWirelessClientIsolation',
                     'zero_it_activation':'ruckusZDWLANConfigZeroITActivation',
                     #chentao 08-19 2013
                     'hotspot_profile_id':'ruckusZDWLANConfigWLANHotspotID',
                     #chentao 08-19 2013
                     'service_priority':'ruckusZDWLANConfigWLANServicePriority',
                     'accounting_server_id':'ruckusZDWLANConfigAccountingServerID',
                     'accounting_update_interval':'ruckusZDWLANConfigAccountingUpdateInterval',
                     'uplink_rate':'ruckusZDWLANConfigUplinkRate',
                     'downlink_rate':'ruckusZDWLANConfigDownlinkRate',
                     'vlan_id':'ruckusZDWLANConfigVlanID',
                     'dynamic_vlan':'ruckusZDWLANConfigDynamicVLAN',
                     'hide_ssid':'ruckusZDWLANConfigHideSSID',
                     'tunnel_mode':'ruckusZDWLANConfigTunnelMode',
                     'bg_scanning':'ruckusZDWLANConfigBackgroundScanning',
                     #chentao 08-19 2013
                     #'max_clients_per_ap':'ruckusZDWLANConfigMaxClientsPerAP',
                     'max_clients_per_ap':'ruckusZDWLANConfigMaxClients',
                     #chentao 08-19 2013
                     'web_auth':'ruckusZDWLANConfigWebAuthentication',
                     'row_status':'ruckusZDWLANConfigRowStatus', #row status is only for create wlan.
                    }

#Dict key mapping: snmp and cli. 
snmp_cli_dict_key_mapping = {'name':'NAME',
                             'ssid':'SSID',
                             'desc':'Description',
                             'service_type':'Type',
                             'auth':'Authentication',
                             'encrypt':'Encryption',
                             'wep_key_index': 'WEP Key Index',
                             'wep_key': 'WEP Key', #= 0F90CA5790512AAE970190A31B
                             'wpa_cipher_type': 'Algorithm',
                             'wpa_key':'Passphrase',
                             'web_auth':'Web Authentication',
                             'auth_server_id': 'Authentication Server', #= testAAA
                             'tunnel_mode':'Tunnel Mode',
                             'bg_scanning':'Background Scanning',
                             'max_clients_per_ap':'Max. Clients',
                             #chen.tao @2013-11-18 to fix ZF-5874
                             #'wireless_client':'Client Isolation',
                             'wireless_client':'Isolation per AP',
                             #chen.tao @2013-11-18 to fix ZF-5874
                             'zero_it_activation':'Zero-IT Activation',
                             'service_priority':'Priority',
                             'uplink_rate':'Rate Limiting Uplink',
                             'downlink_rate':'Rate Limiting Downlink',
                             'vlan_id': 'VLAN-ID', #VLAN= Enabled; VLAN-ID= 3
                             'dynamic_vlan':'Dynamic VLAN',
                             'hide_ssid':'Closed System',
                             'accounting_server_id':'Accounting Server', #= testAAA3
                             'accounting_update_interval':'Interim-Update',
                             }

#Dict key mapping: snmp and gui.
snmp_gui_dict_key_mapping = {'name':'name',
                             'ssid':'ssid',
                             'desc':'description',
                             'service_type':'type',
                             'auth':'auth',
                             'encrypt':'encryption',
                             'wep_key_index':'wep_key_index',
                             'wep_key':'wep_key',
                             'wpa_cipher_type': 'algorithm',
                             'wpa_key': 'passphrase',
                             'web_auth':'web_auth',
                             'auth_server_id': 'auth_server',
                             'tunnel_mode':'tunnel_mode',
                             'bg_scanning':'bgscan',
                             'max_clients_per_ap':'max_clients',
                             'wireless_client':'client_isolation',
                             'zero_it_activation':'zero_it',
                             'service_priority':'priority',
                             'uplink_rate':'rate_limit_uplink',
                             'downlink_rate':'rate_limit_downlink',
                             'vlan_id':'vlan_id',
                             'dynamic_vlan':'dvlan',
                             'hide_ssid':'hide_ssid',
                             'accounting_server_id':'acc_server',
                             'accounting_update_interval': 'interim',
                             }
#The snmp dict config template.
SNMP_CONF = {'name':'-',
             'ssid':'-',
             'desc':'-',
             'service_type':'-',
             'auth':'-',
             'encrypt':'-',
             'wep_key_index': '-',
             'wep_key': '-',
             'wpa_cipher_type': '-',
             'wpa_key':'-',
             'web_auth':'-',
             'auth_server_id': '-',
             'tunnel_mode':'-',
             'bg_scanning':'-',
             'max_clients_per_ap':'-',
             'wireless_client':'-',
             'zero_it_activation':'-',
             'hotspot_profile_id':'-',
             'service_priority':'-',
             'uplink_rate':'-',
             'downlink_rate':'-',
             'vlan_id': '-',
             'dynamic_vlan':'-',
             'hide_ssid':'-',
             'accounting_server_id':'-',
             'accounting_update_interval':'-',
             }

#Object abbr and convert/format func mapping. 
col_get_func_mapping = {'auth': helper.get_name_from_desc,
                        'bg_scanning': helper.convert_bool_to_enabled,
                        'downlink_rate': helper.convert_link_rate,
                        'uplink_rate': helper.convert_link_rate,
                        'dynamic_vlan': helper.convert_desc_to_enabled, 
                        'encrypt': helper.convert_encrypt_opts_desc_to_name,
                        'hide_ssid': helper.convert_bool_to_enabled,
                        'service_priority': helper.get_name_from_desc,
                        'service_type': helper.convert_wlan_service_type,
                        'tunnel_mode': helper.convert_bool_to_enabled,
                        'web_auth': helper.convert_desc_to_enabled,
                        'wireless_client': helper.get_name_from_desc,
                        'wpa_cipher_type': helper.get_name_from_desc,
                        'zero_it_activation': helper.convert_desc_to_enabled,
                        }

#Read-write object abbr and data type mapping. 
rw_obj_type_mapping = {'name':'STRING', #size is 2..32
                       'ssid':'STRING', #size is 2..32
                       'desc':'STRING', #size is 1..64
                       'service_type':'INTEGER', #standardUsage(1),guestAccess(2), hotSpotService(3)
                       'auth':'INTEGER', #open(1), shared(2), eap(3), mac-address(4), eap-mac-mix(5)
                       'encrypt':'INTEGER', #wpa(1), wpa2(2), wpa-Mixed(3), wep-64(4), wep-128(5), none-enc(6)
                       'wep_key_index': 'INTEGER', #1..4
                       'wep_key': 'STRING', #10|26
                       'wpa_cipher_type': 'INTEGER', #tkip(1)not support on ZDWeb2014, aes(2), auto(3), none(0)
                       'wpa_key':'STRING', #size is 8..63|64
                       'web_auth':'INTEGER', #enable(1), disable(2)
                       'auth_server_id': 'INTEGER',
                       'tunnel_mode':'INTEGER', #true(1), false(2)
                       'bg_scanning':'INTEGER', #true(1), false(2)
                       'max_clients_per_ap':'INTEGER', #1..100
                       'wireless_client':'INTEGER', #none(1), local(2), full(3)
                       'zero_it_activation':'INTEGER', #enable(1), disable(2)
                       ## chentao 8-20 2013 to support hotspot configuration
                       'hotspot_profile_id':'INTEGER',
                       ## chentao 8-20 2013 to support hotspot configuration
                       'service_priority':'INTEGER', #high(1), low(2)
                       'uplink_rate':'STRING', #size is 1..10. disable, 0.25mbps ~ 20.00mbps
                       'downlink_rate':'STRING', #same as uplink_rate
                       'vlan_id': 'INTEGER', #1..4094
                       'dynamic_vlan':'INTEGER', #enable(1), disable(2)
                       'hide_ssid':'INTEGER', #true(1), false(2)
                       'accounting_server_id':'INTEGER', #disable(0)..
                       'accounting_update_interval':'INTEGER', #1..60
                       'row_status':'INTEGER', #4 for create.
                    }
#Read-write object orders list when create a wlan. E.g. ssid is the first, rowstatus is the last one.
rw_obj_keys_order_list = ['ssid', 'desc', 'name', 'service_type', 'auth', 'encrypt',
                 'wep_key_index', 'wep_key', 'wpa_cipher_type', 'wpa_key',
                 'auth_server_id', 'wireless_client', 'zero_it_activation','hotspot_profile_id',
                 'service_priority', 'accounting_server_id', 'accounting_update_interval',
                 'uplink_rate', 'downlink_rate', 'vlan_id', 'dynamic_vlan', 'hide_ssid',
                 'tunnel_mode', 'bg_scanning', 'max_clients_per_ap', 'web_auth', 'row_status']

#=============================================#
#             Access Methods            
#=============================================#
def get_wlans_by_key_value(snmp, server_id_name_mapping = {}, key_obj_name = 'name', key_value = '*'):
    '''
    Get wlan information by specified column, and the value, default is name.
    If key_value is *, will get all wlans.
    '''
    wlans_dict = helper.get_items_by_key_value(snmp, WLAN_CONFIG_MIB, wlan_abbr_name_mapping, 
                                        key_obj_name, key_value, convert_wlan_snmp_values)
    
    if server_id_name_mapping:   
        for index, wlan_d in wlans_dict.items():
            wlan_d = _update_wlan_server_id(wlan_d, server_id_name_mapping)
            wlans_dict[index] = wlan_d
            
    return wlans_dict
            
def parsing_wlan_info(snmp_original_d, server_id_name_mapping):
    '''
    Parsing the result and get servers information. Key is server id, Value is server detail information.
    '''
    #Get all server index.
    wlan_id_list = []
    
    for key in snmp_original_d.keys():
        oid_list = key.split('.')
        obj_wlan_name = wlan_abbr_name_mapping['name']
        if compare(oid_list[0],obj_wlan_name, 'eq'):
            wlan_id_list.append(oid_list[1])            
    
    wlans_d = {}
    if wlan_id_list:
        for wlan_id in wlan_id_list:        
            wlan_info = helper.parsing_snmp_result(snmp_original_d, wlan_abbr_name_mapping, wlan_id, convert_wlan_snmp_values)
            wlans_d[wlan_id] = wlan_info
            
    if server_id_name_mapping:
        for index, wlan_d in wlans_d.items():
            wlan_d = _update_wlan_server_id(wlan_d, server_id_name_mapping)
            wlans_d[index] = wlan_d
    
    return wlans_d

def get_wlan_index_value_mapping(snmp, key_obj_name = 'name'):
    '''
    Get all wlan index and column [obj_abbr] value mapping.    
    '''
    oid = wlan_abbr_name_mapping[key_obj_name]
    return helper.get_index_value_mapping(snmp, WLAN_CONFIG_MIB, oid)     

def get_wlan_detail_by_index(snmp, index, server_id_name_mapping, keys_list = []):
    '''
    Get wlan detail config based on wlan index. 
    Need to pass server_id_name_mapping, based on we need to convert server id to name.
    '''
    wlan_dict = helper.get_item_detail_by_index(snmp, WLAN_CONFIG_MIB, wlan_abbr_name_mapping, 
                                         index, convert_wlan_snmp_values, keys_list)
    wlan_dict = _update_wlan_server_id(wlan_dict, server_id_name_mapping)
    
    return wlan_dict
    
def verify_wlans_dict_snmp_cli(snmp_wlans_d, cli_wlans_d):
    '''
    Verify the wlans dict from snmp with cli values. Key is index, value is wlan detail dict.
    '''  
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, wlan_abbr_name_mapping)    
    res_d = helper.verify_items_dict(snmp_wlans_d, cli_wlans_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_wlans_dict_snmp_gui(snmp_wlans_d, gui_wlans_d):
    '''
    Verify the wlans dict from snmp with gui values. Key is index, value is wlan detail dict.
    '''  
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, wlan_abbr_name_mapping)
    res_d = helper.verify_items_dict(snmp_wlans_d, gui_wlans_d, _convert_gui_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_one_wlan_snmp_cli(snmp_d, cli_d, oids_d = {}, index = None):
    '''
    Verify a wlan config: snmp and cli values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, wlan_abbr_name_mapping)
    res_d = helper.verify_one_item_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, 
                                          _item_verify_is_pass, oids_d, index)

    return res_d

def verify_one_wlan_snmp_gui(snmp_d, gui_d, oids_d = {}, index = None):
    '''
    Verify a wlan config: snmp and gui values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, wlan_abbr_name_mapping)
    res_d = helper.verify_one_item_config(snmp_d, gui_d, _convert_gui_to_snmp_temp, 
                                          _item_verify_is_pass, oids_d, index)

    return res_d

def verify_wlans_test_data_snmp(snmp_wlans_d, test_data_wlans_d):
    '''
    Verify wlan information: pre-config data and values from snmp. 
    '''
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, wlan_abbr_name_mapping)
    res_wlans_d = helper.verify_items_dict(snmp_wlans_d, test_data_wlans_d, 
                                           None, _item_verify_is_pass, oids_d)
    
    return res_wlans_d

def convert_wlan_test_data_cfg(wlan_dict, server_id_name_mapping):
    '''
    Convert test data config, and get server name based on server id.
    '''
    wlan_dict = convert_wlan_snmp_values(wlan_dict)
    wlan_dict = _update_wlan_server_id(wlan_dict, server_id_name_mapping)
    return wlan_dict
        
def verify_update_wlan(snmp, wlan_id, update_cfg_list, server_id_name_mapping):
    '''
    Update the wlan information, and then verify the value is updated.
    '''
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, wlan_abbr_name_mapping)
    
    index = 0
    res_wlans_d = {}
    for wlan_cfg in update_cfg_list:
        index +=1
        update_wlan(snmp, wlan_cfg, wlan_id)
        time.sleep(2)
        keys_list = wlan_cfg.keys()
        
        snmp_wlan_d = get_wlan_detail_by_index(snmp, wlan_id, server_id_name_mapping, keys_list)        
        test_wlan_d = convert_wlan_test_data_cfg(wlan_cfg, server_id_name_mapping)
        
        res_d = helper.verify_one_item_config(snmp_wlan_d, test_wlan_d, None, None, oids_d, index)
         
        if res_d:
            res_wlans_d[index] = {'Config': wlan_cfg, 'Result': res_d}
        
    return res_wlans_d

def remove_all_wlans(snmp):
    '''
    Remove all exist wlans. 
    Notes: The wlan can't be deleted successfully if it is included in one wlan group.     
    '''
    wlan_index_list = get_wlan_index_value_mapping(snmp).keys()
    
    if len(wlan_index_list) > 0:
        delete_wlans(snmp, wlan_index_list)

def delete_wlans(snmp, wlan_index_list):
    '''
    Delete the wlans by index exist in wlan_index_list.
    Update row_status as 6, the wlan is deleted.
    '''
    error_index_list = []
    for index in wlan_index_list:
        wlan_cfg = {'index':  index}
        helper.update_objects_config(snmp, WLAN_CONFIG_MIB, wlan_abbr_name_mapping, 
                              rw_obj_type_mapping, rw_obj_keys_order_list, wlan_cfg, 3)        
       
        time.sleep(10)        

        if not _check_wlan_exist_by_index(snmp, index):            
            logging.info('The wlan has been deleted successfully. Index = %s' % index)
        else:
            error_index_list.append(index)
            logging.warning('The wlan is not deleted. Index = %s' % index)

    return error_index_list

def create_wlans(snmp, wlan_cfg_list = None):
    '''
    Create all wlans based on wlan_cfg_list [The list with wlan config]
    Return:
        The dict of wlan details with key = index.
        {'1': {name='test1',ssid='test1',...} }
    '''
    wlan_list_d = {}
    if not wlan_cfg_list:
        wlan_cfg_list = gen_wlan_test_cfg()
        
    for wlan_cfg in wlan_cfg_list:
        res, index = create_one_wlan(snmp, wlan_cfg)
        if res:
            wlan_list_d.update({str(index): wlan_cfg})

    return wlan_list_d
    
def create_one_wlan(snmp, wlan_cfg):
    '''
    Create a wlan based on specified config. 
    Re-construct to a parameter list based on wlan detail config,
    then call snmp method to create wlan.
    Notes:    
    When call set_multi_by_name, the parameters is the list of the dict 
    with format {'mib':'','oid': '', 'index': '','type': '', 'value':''}
    '''
    index = _gen_new_index(snmp)

    if index == 0:
        raise Exception("Can't get the index for wlan. [Only can create 32 wlans]")
    
    new_wlan_cfg = {'index' : index}
    new_wlan_cfg.update(wlan_cfg)
    
    helper.update_objects_config(snmp, WLAN_CONFIG_MIB, wlan_abbr_name_mapping, 
                          rw_obj_type_mapping, rw_obj_keys_order_list, new_wlan_cfg, 1)
    
    time.sleep(10)
    
    result = True

    if _check_wlan_exist_by_index(snmp, index):
        result = True
        logging.info('The wlan is created successfully. Index=%s' % index)
    else:        
        result = False
        logging.warning('The wlan is not created. Index=%s' % index)

    return result, index

def update_wlan(snmp, wlan_cfg, index):
    '''
    Update a wlan with specified setting (wlan_cfg).
    '''
    new_wlan_cfg = {'index' : index}
    new_wlan_cfg.update(wlan_cfg)
    
    helper.update_objects_config(snmp, WLAN_CONFIG_MIB, wlan_abbr_name_mapping,
                          rw_obj_type_mapping, rw_obj_keys_order_list, new_wlan_cfg, 2)

def convert_wlan_snmp_values(wlan_d):
    '''
    Convert wlan values based on col_get_func_mapping dict. 
    '''
    for key, value in wlan_d.items():
        new_value = value
        if key in col_get_func_mapping.keys():
            convert_func = col_get_func_mapping[key]
            new_value = convert_func(value)        
        
        wlan_d[key] = new_value
        
    return wlan_d
#@author:yuyanan @since:2014-8-13 zf-8512 behavior-change: wpa change to wpa2
def gen_wlan_test_cfg(aaa_auth_server_id = None, aaa_acct_server_id = None, size = None):
    '''
    Get wlan test cfg: some kinds of wlan list. The value is same as original from snmp.
    Can't support to create wlan with type is Guest account and Hotspot server.
    '''
    aaa_auth_server_id = str(aaa_auth_server_id)
    aaa_acct_server_id = str(aaa_acct_server_id)
    
    wlans_list = [dict(ssid = 'Standard-Open-None', desc = 'Standard open and no encryption', name = 'Standard-Open-None', service_type = 'standardUsage(1)',
                       auth = 'open(1)', encrypt = 'none-enc(6)', wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                       auth_server_id = '1', wireless_client = 'enable(1)', 
                       #zero_it_activation = 'enable(1)', #@ZJ When enable Webauth,zero_it is gray.ZF-10117
                       service_priority = 'high(1)',
                       accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable', downlink_rate = 'disable',
                       vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                       max_clients_per_ap = '100', web_auth = 'enable(1)'),
                  dict(ssid = 'Standard-Shared-WEP', desc = 'Standard shared and WEP encryption', name = 'Standard-Shared-WEP',
                       service_type = 'standardUsage(1)', auth = 'shared(2)', encrypt = 'wep-64(4)', wep_key_index = '2', wep_key = '6D1E046A8D',
                       wpa_cipher_type = 'none(0)', wpa_key = '1234567890', auth_server_id = '0', wireless_client = 'enable(1)',
                       zero_it_activation = 'enable(1)', service_priority = 'low(2)', accounting_server_id = '0', accounting_update_interval = '20',
                       uplink_rate = '0.25mbps', downlink_rate = '0.25mbps', 
                       vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)',
                       tunnel_mode = 'false(2)', bg_scanning = 'true(1)', max_clients_per_ap = '100', web_auth = 'disable(2)'),
                  dict(ssid = 'Standard-802.1xEAP-WPA2', desc = 'Standard 802.1x EAP and WPA2 encryption', name = 'Standard-802.1xEAP-WPA2',
                       service_type = 'standardUsage(1)', auth = 'eap(3)', encrypt = 'wpa2(2)', wep_key_index = '1', wep_key = '1234567890',
                       wpa_cipher_type = 'aes(2)', wpa_key = '1234567890', auth_server_id = '1', wireless_client = 'enable(1)', zero_it_activation = 'enable(1)',
                       service_priority = 'high(1)', accounting_server_id = '0', accounting_update_interval = '20', 
                       uplink_rate = '0.25mbps', downlink_rate = '0.25mbps', 
                       vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)',
                       bg_scanning = 'true(1)', max_clients_per_ap = '100', web_auth = 'disable(2)'),
                  ]
    
    if aaa_auth_server_id:
        wlans_list.extend([dict(ssid = 'Standard-802.1xEAP+Macaddr', desc = 'Standard 802.1x EAP+Mac addr and no encryption',
                       name = 'Standard-802.1xEAP+Macaddr', service_type = 'standardUsage(1)', auth = 'eap-mac-mix(5)', encrypt = 'none-enc(6)',
                       wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890', auth_server_id = aaa_auth_server_id,
                       wireless_client = 'enable(1)', 
                       #zero_it_activation = 'disable(2)',  #@ZJ 20141209 ZF-11072
                       service_priority = 'high(1)', accounting_server_id = '0',
                       accounting_update_interval = '20', uplink_rate = '0.25mbps', downlink_rate = '0.25mbps', 
                       vlan_id = '1', dynamic_vlan = 'disable(2)',
                       hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)', max_clients_per_ap = '100', web_auth = 'disable(2)'),
                       dict(ssid = 'Standard-MacAddress-WEP', desc = 'Standard Mac Address, WEP-64', name = 'Standard-MacAddress-WEP',
                       service_type = 'standardUsage(1)', auth = 'mac-address(4)', encrypt = 'wep-64(4)', wep_key_index = '3',
                       wep_key = 'B574A471A0', wpa_cipher_type = 'none(0)', wpa_key = '1234567890', auth_server_id = aaa_auth_server_id,
                       wireless_client = 'enable(1)', zero_it_activation = 'disable(2)', service_priority = 'high(1)',
                       accounting_server_id = '0', accounting_update_interval = '20', 
                       uplink_rate = '0.25mbps', downlink_rate = '0.25mbps',
                       vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                       max_clients_per_ap = '100', web_auth = 'disable(2)')]
                       )
    
    if aaa_auth_server_id and aaa_acct_server_id:
        wlans_list.extend([dict(ssid = 'Standard-Open-WEP', desc = 'Standard open and WEP encryption - advanced options', name = 'Standard-Open-WEP',
                       service_type = 'standardUsage(1)', auth = 'open(1)', encrypt = 'wep-64(4)', wep_key_index = '4', wep_key = 'CA5A545C5C',
                       #wpa_cipher_type = 'none(0)', wpa_key = '1234567890', #@ZJ Parameters giving wrong
                       auth_server_id = aaa_auth_server_id, wireless_client = 'enable(1)', 
                       #zero_it_activation = 'disable(2)',#@ZJ When enable Webauth,zero_it is gray.ZF-10117
                       service_priority = 'high(1)', accounting_server_id = aaa_acct_server_id, accounting_update_interval = '20',
                       uplink_rate = '0.25mbps', downlink_rate = '0.25mbps', 
                       vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)',
                       bg_scanning = 'true(1)', max_clients_per_ap = '100', web_auth = 'enable(1)'),
                  dict(ssid = 'Standard-Open-WPA2', desc = 'Standard open and WPA2 encryption - advanced options', name = 'Standard-Open-WPA2',
                       service_type = 'standardUsage(1)', auth = 'open(1)', encrypt = 'wpa2(2)', wep_key_index = '1', wep_key = '1234567890',
                       wpa_cipher_type = 'aes(2)', wpa_key = '1234567890', auth_server_id = aaa_auth_server_id, wireless_client = 'enable(1)', 
                       #zero_it_activation = 'disable(2)',#@ZJ When enable Webauth,zero_it is gray.ZF-10117
                       service_priority = 'low(2)', accounting_server_id = aaa_acct_server_id, accounting_update_interval = '20', 
                       uplink_rate = '8.00mbps', downlink_rate = '20.00mbps', 
                       vlan_id = '2', dynamic_vlan = 'disable(2)', hide_ssid = 'true(1)', tunnel_mode = 'true(1)',
                       bg_scanning = 'false(2)', max_clients_per_ap = '100', web_auth = 'enable(1)')]
                     )
        
    wlans_list = wlans_list[0:size]
    
    return wlans_list
#@author:yuyanan @since:2014-8-13 zf-8512 behavior-change: wpa change to wpa2

def gen_wlan_update_cfg(aaa_auth_server_id = None, aaa_acct_server_id = None):
    '''
    Generate test config for update wlan: detail config to update it.    
    Notes:
    1. For update dynamic_vlan, auth is 802.1x or mac, and encrpyt is wpa, and auth server id is radius server.
    '''
    update_cfg_list = []
 
    #@ZJ @since:20141113 ZF-9942 fix all the error parameters:
    #1)When enable Webauth,zero_it is gray.ZF-9942; 2)When disnable Webauth,zero_it can be set; 3)'tkip(1)' not be supported on ZDWeb,change to 'aes(2)' 
    update_cfg_list.append(dict(desc = 'Standard open and no encryption', service_type = 'standardUsage(1)',
                                auth = 'open(1)', encrypt = 'none-enc(6)', auth_server_id = '1', 
                                wireless_client = 'enable(1)', #zero_it_activation = 'enable(1)', 
                                service_priority = 'high(1)', accounting_server_id = '0', accounting_update_interval = '10', 
                                uplink_rate = 'disable', downlink_rate = 'disable', 
                                vlan_id = '1', dynamic_vlan = 'disable', 
                                hide_ssid = 'false(2)', tunnel_mode = 'false(2)', 
                                bg_scanning = 'true(1)', max_clients_per_ap = '100', web_auth = 'enable(1)'))
    update_cfg_list.append(dict(desc = 'Updated Standard shared and WEP encryption',wireless_client = 'enable(1)',
                                ##zero_it_activation = 'disable(2)',
                                service_priority = 'low(2)',
                                uplink_rate = '1.25mbps',downlink_rate = '10.75mbps',
                                hide_ssid = 'true(1)',tunnel_mode = 'true(1)',bg_scanning = 'false(2)',
                                max_clients_per_ap = '34'))
    update_cfg_list.append(dict(wireless_client = 'enable(1)', uplink_rate = '3.75mbps',downlink_rate = '5.00mbps'))
    update_cfg_list.append(dict(dict(uplink_rate = '20.00mbps', downlink_rate = '10.00mbps')))
    update_cfg_list.append(dict(dict(uplink_rate = '19.75mbps', downlink_rate = '0.50mbps')))
    update_cfg_list.append(dict(dict(uplink_rate = 'disable', downlink_rate = 'disable')))    
    update_cfg_list.append(dict(web_auth = 'disable(2)', auth_server_id = '0', zero_it_activation = 'enable(1)'))
    update_cfg_list.append(dict(auth = 'open(1)', encrypt = 'wep-64(4)', wep_key_index = '4', wep_key = 'CA5A545C5C'))
    update_cfg_list.append(dict(auth = 'open(1)', encrypt = 'wpa2(2)', wpa_cipher_type = 'aes(2)', wpa_key = '1234567890'))
    update_cfg_list.append(dict(auth = 'shared(2)', encrypt = 'wep-64(4)', wep_key_index = '3', wep_key = '6D1E046A8D'))
    update_cfg_list.append(dict(auth = 'eap(3)', encrypt = 'none-enc(6)', auth_server_id = '1'))
    update_cfg_list.append(dict(vlan_id = '1', dynamic_vlan = 'disabled(2)'))
    update_cfg_list.append(dict(vlan_id = '4094'))

    if aaa_auth_server_id:
        update_cfg_list.append(dict(auth = 'open(1)', web_auth = 'enable(1)', auth_server_id = aaa_auth_server_id))
        update_cfg_list.append(dict(auth = 'eap(3)', encrypt = 'wpa2(2)', wpa_cipher_type = 'aes(2)', wpa_key = '1234567890',
                                      auth_server_id = aaa_auth_server_id, dynamic_vlan = 'enable(1)'))
        update_cfg_list.append(dict(auth = 'mac-address(4)', encrypt = 'wep-64(4)', wep_key_index = '2', wep_key = 'B574A471A0', 
                                     auth_server_id = aaa_auth_server_id, dynamic_vlan = 'disable(2)'))  
        update_cfg_list.append(dict(auth = 'eap-mac-mix(5)', encrypt = 'none-enc(6)', auth_server_id = aaa_auth_server_id))
        
    if aaa_acct_server_id:
        update_cfg_list.append(dict(accounting_server_id = aaa_acct_server_id, accounting_update_interval = '60'))
    
    return update_cfg_list   

def gen_wlan_test_cfg_negative():
    '''
    Generate negative input for wlan config.
    '''
    wlan_cfg = {}
    
    type = 'alpha'
    str_65 = get_random_string(type, 65)    
    str_33 = get_random_string(type, 33)
    str_11 = get_random_string(type, 11)
    
    wlan_cfg['name'] = str_33 #size is 2..32
    wlan_cfg['ssid'] = str_33 #size is 2..32
    wlan_cfg['desc'] = str_65  #size is 1..64
    wlan_cfg['service_type'] = '4' #standardUsage(1),guestAccess(2), hotSpotService(3)
    wlan_cfg['auth'] = '6' #open(1), shared(2), eap(3), mac-address(4), eap-mac-mix(5)
    wlan_cfg['encrypt'] = '7' #wpa(1), wpa2(2), wpa-Mixed(3), wep-64(4), wep-128(5), none-enc(6)
    wlan_cfg['wep_key_index'] = '5' #1..4
    wlan_cfg['wep_key'] = '12345678' #10|26
    wlan_cfg['wpa_cipher_type'] = '4' #tkip(1), aes(2), auto(3), none(0)
    wlan_cfg['wpa_key'] = str_65 #size is 8..63|64
    wlan_cfg['web_auth'] = '3' #enable(1), disable(2)
    #wlan_cfg['auth_server_id'] = '3'
    wlan_cfg['tunnel_mode'] = '3' #true(1), false(2)
    wlan_cfg['bg_scanning'] = '3' #true(1), false(2)
    wlan_cfg['max_clients_per_ap'] = '101' #1..100
    wlan_cfg['wireless_client'] = '4' #none(1), local(2), full(3)
    wlan_cfg['zero_it_activation'] = '3' #enable(1), disable(2)
    wlan_cfg['service_priority'] = '3' #high(1), low(2)
    wlan_cfg['uplink_rate'] = str_11 #size 1..10
    wlan_cfg['downlink_rate'] = '10' #same as uplink_rate
    wlan_cfg['vlan_id'] = '4095' #1..4094
    wlan_cfg['dynamic_vlan'] = '3' #enable(1), disable(2)
    wlan_cfg['hide_ssid'] = '3' #true(1), false(2)
    #wlan_cfg['accounting_server_id'] = '10' #disable(0)..
    wlan_cfg['accounting_update_interval'] = '61' #1..60
    
    return wlan_cfg
    
def update_wlan_cfg_one_by_one(snmp, index, test_cfg):
    '''
    Update wlan config items, one by one.
    '''
    res_d = {}
    for obj_name, value in test_cfg.items():
        oid = wlan_abbr_name_mapping[obj_name]
        obj_type = rw_obj_type_mapping[obj_name]
        res = helper.update_single_node_value(snmp, WLAN_CONFIG_MIB, oid, index, obj_type, value)
        
        if res:
            res_d.update({obj_name : res})
        
    return res_d

#=============================================#
#             Private Methods            
#=============================================#
def _gen_new_index(snmp):
    '''
    Generate new index for create wlan. 
    Return the index does not exist in current wlan list, range is 1 to 32.
    If return as 0, there are 32 wlans exist.
    '''
    start_index = 1
    max_index = 32
    oid = wlan_abbr_name_mapping['name']
    new_index = helper.gen_new_index(snmp, WLAN_CONFIG_MIB, oid, start_index, max_index) 
    return new_index

def _update_wlan_server_id(wlan_d, server_id_name_mapping):
    '''
    Update wlan server_id as name.
    '''
    server_id_keys = ['auth_server_id','accounting_server_id']
    for key in server_id_keys:
        if wlan_d.has_key(key):
            if wlan_d[key] not in server_id_name_mapping.values():
                wlan_d[key] = server_id_name_mapping[wlan_d[key]]
            
    return wlan_d
        
def _convert_cli_to_snmp_temp(cli_wlan_d):
    '''
    Convert cli wlan dict to same snmp dict structure.
    '''
    cli_snmp_value_mapping = {'auth': {'802.1x-eap': 'eap', 'mac-auth': 'mac-address', 'mac-eap': 'eap-mac-mix'},
                              'encrypt': {'wep64': 'wep-64'},
                              'wireless_client': {'Disabled': 'None'}
                             }

    new_cli_wlan_d = copy.deepcopy(SNMP_CONF)

    for key, cli_key in snmp_cli_dict_key_mapping.items():
        new_value = ''
        if cli_wlan_d.has_key(cli_key):
            new_value = cli_wlan_d[cli_key]
            if key == 'accounting_update_interval':
                new_value = new_value.replace('Minutes', '').strip()
                
            if cli_snmp_value_mapping.has_key(key):
                value_mapping = cli_snmp_value_mapping[key]
                if value_mapping.has_key(new_value):
                    new_value = cli_snmp_value_mapping[key][new_value]
        else:
            #Set default values for some objects.
            new_value = ''
            if key == 'accounting_server_id':
                new_value = 'Disabled'
            elif key == 'service_priority':
                new_value = 'High'
            elif key in ['uplink_rate', 'downlink_rate', 'bg_scanning']:
                new_value = 'Disabled'                
            elif key in ['vlan_id']:
                new_value = '1'
                
        new_cli_wlan_d[key] = new_value
                
    return new_cli_wlan_d

def _convert_gui_to_snmp_temp(gui_wlan_d):
    '''
    Convert gui wlan dict to same snmp dict structure.
    '''
    gui_snmp_value_mapping = {'service_type': {'standard-usage': 'Standard Usage',
                                               'guest-access': 'Guest Access',
                                               'hotspot': 'Hotspot Service(WISPr)', },
                              'auth':{'dot1x-eap': 'eap', 'mac': 'mac-address', 'maceap':'eap-mac-mix'},
                              }
    new_gui_wlan_d = copy.deepcopy(SNMP_CONF)

    for key, gui_key in snmp_gui_dict_key_mapping.items():
        new_value = ''
        if gui_wlan_d.has_key(gui_key):
            new_value = gui_wlan_d[gui_key]
            if gui_snmp_value_mapping.has_key(key):
                if gui_snmp_value_mapping[key].has_key(new_value):
                    new_value = gui_snmp_value_mapping[key][new_value]
        elif key == 'vlan_id':
            new_value = '1'
        new_gui_wlan_d[key] = new_value
        
    return new_gui_wlan_d

def _item_verify_is_pass(value_d, key):
    '''
    Check whether the item is no no need to verify.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''

    if key == 'accounting_update_interval':
        if helper.is_disabled(value_d['accounting_server_id']):
            message = 'Do not need to verify interval if no accounting server.'
            is_pass = True
    elif key in ['wep_key_index', 'wep_key', 'wpa_cipher_type', 'wpa_key']:        
        if compare(value_d['auth'],'eap-mac-mix', 'eq'):
            message = 'Do not need to verify wep and wpa when auth type is eap-mac-mix.'
            is_pass = True
        elif key in ['wep_key_index', 'wep_key']:
            if value_d['encrypt'].lower() not in ['wep-64', 'wep-128']:
                message = 'Do not need to verify wep key index and key if encrypt is not wep and auth is 802.1x eap.'
                is_pass = True
            else:
                if key == 'wep_key' and compare(value_d['auth'], 'eap', 'eq'):
                    is_pass = True
                    message = 'Do not need to verify wep key when auth is eap.'
        elif key in ['wpa_cipher_type', 'wpa_key']:
            if compare(value_d['auth'],'shared', 'eq'):
                is_pass = True
                message = 'Do not need to verify wpa setting if auth is shared.'
            else:
                if value_d['encrypt'].lower() not in ['wpa', 'wpa2', 'wpa-Mixed']:
                    message = 'Do not need to verify wpa setting if encrypt is not wpa related.'
                    is_pass = True
                elif key == 'wpa_key' and compare(value_d['auth'], 'eap', 'eq'):
                    message = 'Do not need to verify wpa key if auth type is eap.'
                    is_pass = True
    elif key in ['wireless_client']:
        if compare(value_d['service_type'], 'Hotspot Service(WISPr)', 'eq'):
            is_pass = True
            message = 'Do not need to verify wireless client if service type is hot sport service.'
    elif key in ['auth_server_id', 'web_auth']:
        if not compare(value_d['service_type'], 'Standard Usage', 'eq'):
            is_pass = True
            message = 'Do not need to verify web auth setting if type is not standard usage.'
        elif key == 'auth_server_id' and helper.is_disabled(value_d['web_auth']):
            is_pass = True
            message = 'Do not need to verify auth server when web auth is disabled.'

    return is_pass, message

def _check_wlan_exist_by_index(snmp, index):
    '''
    Check wether the wlan with specified index exist. 
    Return true if exist, false if does not exist.
    '''
    # Check the wlan is created successfully.
    index_wlan_name_mapping = get_wlan_index_value_mapping(snmp)
    result = False
    if index_wlan_name_mapping and index_wlan_name_mapping.has_key(str(index)):
        result = True

    return result

