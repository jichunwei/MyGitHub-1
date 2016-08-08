'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for system ip information, get and verify methods.
'''

import copy

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.utils import compare


SYSTEM_MIB = 'RUCKUS-ZD-SYSTEM-MIB'
SYSTEM_IP_TABLE = 'ruckusZDSystemIPTable'
SYSTEM_IP_OBJECT_NAME_INDEX = 1
OBJNAME_INDEX_TEMP = '%s.%s'

ip_obj_abbr_name_mapping = {'ip_version':'ruckusZDSystemIPVersion',
                            'ip_addr_mode':'ruckusZDSystemIPAddrMode',
                            'ip_addr':'ruckusZDSystemIPAddress',
                            'ip_addr_mask':'ruckusZDSystemIPAddrNetmask',
                            'ip_gateway':'ruckusZDSystemIPGateway',
                            'ip_pri_dns':'ruckusZDSystemIPPrimaryDNS',
                            'ip_sec_dns':'ruckusZDSystemIPSecondaryDNS',
                            'ipv6_addr_mode':'ruckusZDSystemIPV6AddressModel',
                            'ipv6_addr':'ruckusZDSystemIPV6Address',
                            'ipv6_prefix_len':'ruckusZDSystemIPV6PrefixLen',
                            'ipv6_gateway':'ruckusZDSystemIPV6Gateway',
                            'ipv6_pri_dns':'ruckusZDSystemIPV6PrimaryDNS',
                            'ipv6_sec_dns':'ruckusZDSystemIPV6SecondaryDNS',
                            }

ip_obj_abbr_fmtfunc_mapping = {'ip_version': helper.get_name_from_desc,
                               'ip_addr_mode': helper.get_name_from_desc,
                               'ipv6_addr_mode': helper.get_name_from_desc,
                               }

default_sys_ip_info = {'ip_version':'',
                    'ip_addr_mode':'',
                    'ip_addr':'',
                    'ip_addr_mask':'',
                    'ip_gateway':'',
                    'ip_pri_dns':'',
                    'ip_sec_dns':'',
                    'ipv6_addr_mode':'',
                    'ipv6_addr':'',
                    'ipv6_prefix_len':'',
                    'ipv6_gateway':'',
                    'ipv6_pri_dns':'',
                    'ipv6_sec_dns':'',
                    }

#=============================================#
#             Access Methods            
#=============================================#
def get_sys_ip_info(snmp, abbr_list = []):
    '''
    Get all system ip information under system objects by walking system ip tables.
    '''
    new_dict = helper.get_item_detail_by_index(snmp, SYSTEM_MIB, ip_obj_abbr_name_mapping, 
                                        SYSTEM_IP_OBJECT_NAME_INDEX, _convert_snmp_values_sys_ip_objs, abbr_list)
    return new_dict
            
def parsing_sys_ip_info(snmp_original_d):
    '''
    Parsing the original result from snmp command. Convert key from oid(ruckusZDSystemName) to obj abbr(system_name).
    '''
    snmp_sys_ip_d = helper.parsing_snmp_result(snmp_original_d, ip_obj_abbr_name_mapping, SYSTEM_IP_OBJECT_NAME_INDEX, _convert_snmp_values_sys_ip_objs)
    return snmp_sys_ip_d

def get_sys_oids_by_name(snmp):
    '''
    Get system oids for all system objects.
    '''
    return helper.get_item_oids(SYSTEM_MIB, ip_obj_abbr_name_mapping)
      
def get_ip_version(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_version')

def get_ip_addr_mode(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_addr_mode')

def get_ip_addr(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_addr')

def get_ip_addr_mask(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_addr_mask')

def get_ip_gateway(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_gateway')

def get_ip_pri_dns(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_pri_dns')

def get_ip_sec_dns(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_sec_dns')

def get_ipv6_addr_mode(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ipv6_addr_mode')

def get_ipv6_addr(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ipv6_addr')

def get_ipv6_prefix_len(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ipv6_prefix_len')

def get_ipv6_gateway(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ipv6_gateway')

def get_ipv6_pri_dns(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ipv6_pri_dns')

def get_ipv6_sec_dns(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ipv6_sec_dns')

def verify_sys_ip_info_snmp_cli(snmp_d, cli_d):
    '''
    Verify system information between snmp get and cli get.
    '''
    oids_d = helper.get_item_oids(SYSTEM_MIB, ip_obj_abbr_name_mapping)
    res_d = helper.verify_one_item_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d, SYSTEM_IP_OBJECT_NAME_INDEX)
    return res_d

def verify_sys_ip_info_snmp_gui(snmp_d, gui_d):
    '''
    Verify system ip information between snmp get and gui get.
    '''
    oids_d = helper.get_item_oids(SYSTEM_MIB, ip_obj_abbr_name_mapping)
    res_d = helper.verify_one_item_config(snmp_d, gui_d, _convert_gui_to_snmp_temp, _item_verify_is_pass, oids_d, SYSTEM_IP_OBJECT_NAME_INDEX)
    
    return res_d
#=============================================#
#             Private Methods            
#=============================================#
def _get_sys_obj_value(snmp, obj_abbr):
    '''
    Get value for specified snmp name (get object name by obj_abbr).
    '''
    obj_name = ip_obj_abbr_name_mapping[obj_abbr]

    item_value = helper.get_one_object_value_by_name(snmp, SYSTEM_MIB, obj_name, SYSTEM_IP_OBJECT_NAME_INDEX) 
    
    if ip_obj_abbr_fmtfunc_mapping.has_key(obj_abbr):
        value = ip_obj_abbr_fmtfunc_mapping[obj_abbr](item_value)
    else:
        value = item_value
        
    return value

def _item_verify_is_pass(value_d, key):
    '''
    Weather we need to pass item values.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''
    
    if key in ['ip_addr_mode', 'ip_addr', 'ip_addr_mask', 'ip_gateway', 'ip_pri_dns', 'ip_sec_dns']:
        if value_d['ip_version'] == 'ipv6':
            is_pass = True
            message = "Don't need to verify ipv4 info if version is ipv6."
        elif key in ['ip_addr', 'ip_addr_mask', 'ip_gateway', 'ip_pri_dns', 'ip_sec_dns']:
            if value_d['ip_addr_mode'] == 'dhcp':
                is_pass = True
                message = "Don't need to verify ip addr, mask, gateway, dns if mode is dhcp."
    elif key in ['ipv6_addr_mode', 'ipv6_addr', 'ipv6_prefix_len', 'ipv6_gateway', 'ipv6_pri_dns', 'ipv6_sec_dns']:
        if value_d['ip_version'] == 'ipv4':
            is_pass = True
            message = "Don't need to verify ipv4 info if version is ipv6."
        elif key in ['ipv6_addr', 'ipv6_prefix_len', 'ipv6_gateway', 'ipv6_pri_dns', 'ipv6_sec_dns']:
            if value_d['ipv6_addr_mode'] == 'auto':
                is_pass = True
                message = "Don't need to verify ip addr, mask, gateway, dns if mode is dhcp."
            
    return is_pass, message

def _convert_gui_to_snmp_temp(gui_sys_ip_info_d):
    '''
    Convert gui system ip information to snmp temp.
    '''
    gui_sys_ip_info = copy.deepcopy(default_sys_ip_info)
    
    gui_sys_ip_info['ip_version'] = gui_sys_ip_info_d['ip_version']
    
    ipv4_mode = gui_sys_ip_info_d['ip_alloc']
    if compare(ipv4_mode, 'manual', 'eq'):
        ipv4_mode = 'static'
    gui_sys_ip_info['ip_addr_mode'] = ipv4_mode
    
    gui_sys_ip_info['ip_addr'] = gui_sys_ip_info_d['ip_addr']
    gui_sys_ip_info['ip_addr_mask'] = gui_sys_ip_info_d['netmask']
    gui_sys_ip_info['ip_gateway'] = gui_sys_ip_info_d['gateway']
    gui_sys_ip_info['ip_pri_dns'] = gui_sys_ip_info_d['pri_dns']
    gui_sys_ip_info['ip_sec_dns'] = gui_sys_ip_info_d['sec_dns']
    
    ipv6_mode = gui_sys_ip_info_d['ipv6_alloc']
    if compare(ipv6_mode, 'auto', 'eq'):
        ipv6_mode = 'auto-configuration'
    else:
        ipv6_mode = 'static'
    gui_sys_ip_info['ipv6_addr_mode'] =ipv6_mode
     
    gui_sys_ip_info['ipv6_addr'] = gui_sys_ip_info_d['ipv6_addr']
    gui_sys_ip_info['ipv6_prefix_len'] = gui_sys_ip_info_d['ipv6_prefix_len']
    gui_sys_ip_info['ipv6_gateway'] = gui_sys_ip_info_d['ipv6_gateway']
    gui_sys_ip_info['ipv6_pri_dns'] = gui_sys_ip_info_d['ipv6_pri_dns']
    gui_sys_ip_info['ipv6_sec_dns'] = gui_sys_ip_info_d['ipv6_sec_dns']

    return gui_sys_ip_info

def _convert_cli_to_snmp_temp(cli_sys_ip_info_d):
    '''
    Convert cli system ip information to snmp temp.
    '''
    cli_sys_ip_info = copy.deepcopy(default_sys_ip_info)
    cli_sys_ip_info.update(cli_sys_ip_info_d)
    
    return cli_sys_ip_info        

def _convert_snmp_values_sys_ip_objs(snmp_d):
    '''
    Convert snmp value of system ip information.
    '''
    for key, value in snmp_d.items():
        if ip_obj_abbr_fmtfunc_mapping.has_key(key):
            new_value = ip_obj_abbr_fmtfunc_mapping[key](value)
            if key in ['ipv6_addr_mode', 'ip_addr_mode']:
                if new_value.lower() == 'static':
                    new_value = 'Manual'
            snmp_d[key] = new_value
        
        #For dns, invalid ip 255.255.255.255 is default value in snmp. In CLI, it is empty. 
        if key in ['ip_pri_dns', 'ip_sec_dns']:
            if value == '255.255.255.255':
                snmp_d[key] = ''
            
    return snmp_d                  