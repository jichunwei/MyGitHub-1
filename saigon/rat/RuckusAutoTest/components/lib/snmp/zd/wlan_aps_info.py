'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2012.11.19
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for verify ap information in ruckusZDWLANMIB.
    Refer to ER140 UniL - 9.4.0.0.110 - OID ruckusZDWLANAPDescription does not return any value. 
    
    Get snmp information in MIB: RUCKUS-ZD-WLAN-MIB, this MIB is read-only.
    Nodes:
        Verify some nodes in this MIB instead of all nodes information.
        1: ruckusZDWLANAPMacAddr - MacAddress(4 - octets)
        2: ruckusZDWLANAPDescription - DisplayString(4 - octets)
        10: ruckusZDWLANAPIPAddr - IpAddress(64 - IP address)
        62: ruckusZDWLANAPNetmask - IpAddress(64 - IP address)
        63: ruckusZDWLANAPGateway - IpAddress(64 - IP address)
        64: ruckusZDWLANAPDNS1 - IpAddress(64 - IP address)
        65: ruckusZDWLANAPDNS2 - IpAddress(64 - IP address)
        
Notes:
For the nodes in MIB RUCKUS-ZD-WLAN-MIB, ruckusZDWLANAPTable, the index of node is the following format:
6.<mac address convert to hex string>.
For example: AP mac is: 74:91:1a:12:28:50, index is: 6.116.145.26.18.40.80

Command example:
    Command:snmpget -v 2c -c private -t 20 -r 3 192.168.0.2 RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPMacAddr.6.116.145.26.18.40.80
    Result: RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPMacAddr.'.t`..('.80 = STRING: 74:91:1a:12:28:50
'''
import copy

from RuckusAutoTest.common.lib_Constant import get_radio_mode_by_ap_model
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.common import lib_Constant as const

ZD_WLAN_MIB = 'RUCKUS-ZD-WLAN-MIB'
OBJNAME_INDEX_TEMP = '%s.%s'

#zd_ap objects abbr and snmp full name mapping.
zd_ap_abbr_name_mapping = {'mac_addr':'ruckusZDWLANAPMacAddr',
                           'desc':'ruckusZDWLANAPDescription',
                           'ip_addr':'ruckusZDWLANAPIPAddr',
                           'ip_addr_mask':'ruckusZDWLANAPNetmask',
                           'ip_gateway':'ruckusZDWLANAPGateway',
                           'ip_pri_dns':'ruckusZDWLANAPDNS1',
                           'ip_sec_dns':'ruckusZDWLANAPDNS2',
                           }

zd_ap_eth_info_abbr_name_mapping = {'mac_addr':'ruckusZDWLANAPMacAddress',
                           'port_id':'ruckusZDWLANAPEthPortId',
                           'if_name':'ruckusZDWLANAPEthIfname',
                           'logical_status':'ruckusZDWLANAPEthLogicalStatus',
                           'physical_status':'ruckusZDWLANAPEthPhyStatus',
                           }

#The snmp dict config template.
SNMP_CONF = {'mac_addr':'-',
             'desc':'-',
             'ip_addr':'0.0.0.0',
             'ip_addr_mask':'0.0.0.0',
             'ip_gateway':'0.0.0.0',
             'ip_pri_dns':'0.0.0.0',
             'ip_sec_dns':'0.0.0.0',             
             }

#Object abbr and convert/format func mapping. 
col_get_func_mapping = {'mac_addr': helper.format_mac_address}

#=============================================#
#             Access Methods            
#=============================================#

def get_zd_aps_by_mac_addr(snmp, ap_mac_list):
    '''
    Get ZD ap information based on mac addr list.
    If ap_mac_list is empty, then get all ap information.
    '''
    aps_dict = {}
    
    if type(ap_mac_list) != list:
        ap_mac_list = [ap_mac_list]
        
    for mac_addr in ap_mac_list:
        snmp_index = _get_snmp_index_by_mac(mac_addr)
        ap_info_dict = get_zd_ap_info_by_index(snmp, snmp_index) 
        
        aps_dict[mac_addr.upper()] = ap_info_dict
                        
    return aps_dict         

def get_zd_ap_info_by_index(snmp, index, keys_list = []):
    '''
    Get zd_ap detail config based on zd_ap index.
    Input:
        index: 6.116.145.26.18.40.80
    Command:snmpget -v 2c -c private -t 20 -r 3 192.168.0.2 RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPMacAddr.6.116.145.26.18.40.80
    Result: RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPMacAddr.'.t`..('.80 = STRING: 74:91:1a:12:28:50
    '''
    item_d = {}
        
    for abbr, name in zd_ap_abbr_name_mapping.items():
        if not keys_list or (abbr in keys_list):
            obj_dict = snmp.get_single_by_name(ZD_WLAN_MIB, name, index)
            
            obj_value = None
            is_match = False
            for key,value in obj_dict.items():
                if name in key:
                    is_match = True
                    obj_value = value
                    break                
            
            if is_match: item_d[abbr] = obj_value
            else: item_d[abbr] = "No value"
            
        item_d = _convert_zd_ap_snmp_values(item_d)
        
    print("SNMP Values:%s" % item_d)
        
    return item_d



def get_zd_ap_eth_info_by_mac_and_index(snmp, ap_mac, index):
    '''
    Get ZD ap information based on specified mac addr and ap port index(0,1,2,...).
    '''
    aps_dict = {}
    
    snmp_index = _get_snmp_index_by_mac_and_index(ap_mac, index)
    ap_info_dict = get_zd_ap_eth_info_by_index(snmp, snmp_index) 
    
    return ap_info_dict         

def get_zd_ap_eth_info_by_index(snmp, index, keys_list = []):
    '''
    Get AP Ethernet config based on zd_ap index.
    Input:
        index: 6.116.145.26.18.40.80.0
    Command:snmpget -v 2c -c private -t 20 -r 3 192.168.0.2 RUCKUS-ZD-AP-MIB::ruckusZDWLANAPMacAddress.6.116.145.26.18.40.80.0
    Result: RUCKUS-ZD-WLAN-MIB::ruckusZDWLANAPMacAddress.'.t`..('.80 = STRING: 74:91:1a:12:28:50
    '''
    item_d = {}
        
    for abbr, name in zd_ap_eth_info_abbr_name_mapping.items():
        if not keys_list or (abbr in keys_list):
            obj_dict = snmp.get_single_by_name(ZD_WLAN_MIB, name, index)
            
            obj_value = None
            is_match = False
            for key,value in obj_dict.items():
                if name in key:
                    is_match = True
                    obj_value = value
                    break                
            
            if is_match: item_d[abbr] = obj_value
            else: item_d[abbr] = "No value"
            
        item_d = _convert_zd_ap_snmp_values(item_d)
        
    print("SNMP Values:%s" % item_d)
        
    return item_d
    
def verify_aps_dict_snmp_cli(snmp_aps_d, cli_aps_d):
    '''
    Verify the aps dict from snmp with cli values. Key is index, value is ap detail dict.
    '''  
    oids_d = helper.get_item_oids(ZD_WLAN_MIB, zd_ap_abbr_name_mapping)    
    res_d = helper.verify_items_dict(snmp_aps_d, cli_aps_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_one_ap_snmp_cli(snmp_d, cli_d, oids_d = {}, index = None):
    '''
    Verify a ap config: snmp and cli values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(ZD_WLAN_MIB, zd_ap_abbr_name_mapping)    
    res_d = helper.verify_one_item_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d, index)

    return res_d

#=============================================#
#             Private Methods            
#=============================================#
def _get_snmp_index_by_mac(ap_mac_addr):
    """
    Convert ap mac address to hex string.
    Input: 74:91:1a:12:28:50
    Output: 116.145.26.18.40.80
    """
    mac_list = ap_mac_addr.split(':')
    
    hex_str = ""
    for value in mac_list:
        hex_value = int(value.upper(), 16)
        hex_str += ".%s" % hex_value
    
    snmp_index = "6%s" % (hex_str)
    
    return snmp_index   

def _get_snmp_index_by_mac_and_index(ap_mac_addr, index):
    """
    Convert ap mac address to hex string.
    Input: 74:91:1a:12:28:50
    Output: 116.145.26.18.40.80
    """
    mac_list = ap_mac_addr.split(':')
    
    hex_str = ""
    for value in mac_list:
        hex_value = int(value.upper(), 16)
        hex_str += ".%s" % hex_value
    
    snmp_index = "6%s.%s" % (hex_str, index)
    
    return snmp_index   

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
    new_cli_zd_ap_d['desc'] = cli_zd_ap_d['Description']
    
    network_dict = cli_zd_ap_d['Network Setting']
    
    ip_addr = network_dict.get('IP Address')
    if ip_addr: new_cli_zd_ap_d['ip_addr'] = ip_addr 
    netmask = network_dict.get('Netmask')
    if netmask: new_cli_zd_ap_d['ip_addr_mask'] = netmask 
    gateway = network_dict.get('Gateway')
    if gateway: new_cli_zd_ap_d['ip_gateway'] = gateway
    pri_dns = network_dict.get('Primary DNS Server')
    if pri_dns: new_cli_zd_ap_d['ip_pri_dns'] = pri_dns     
    sec_dns = network_dict.get('Secondary DNS Server')
    if sec_dns: new_cli_zd_ap_d['ip_sec_dns'] = sec_dns 
    
    return new_cli_zd_ap_d

def _item_verify_is_pass(value_d, key):
    '''
    Check whether the item is no no need to verify.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''
    
    return is_pass, message