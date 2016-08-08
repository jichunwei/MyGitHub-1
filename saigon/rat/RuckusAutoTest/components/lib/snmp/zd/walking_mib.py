'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.05.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    The document is support snmp aaa servers information.
'''
from RuckusAutoTest.components.lib.snmp.zd.sys_info import SYSTEM_MIB, parsing_sys_info
from RuckusAutoTest.components.lib.snmp.zd.sys_ip_info import parsing_sys_ip_info
from RuckusAutoTest.components.lib.snmp.zd.sys_snmp_info import parsing_sys_snmp_info
from RuckusAutoTest.components.lib.snmp.zd.aaa_servers import AAA_SERVER_MIB, parsing_server_info, get_all_servers_id_name_mapping
from RuckusAutoTest.components.lib.snmp.zd.wlan_list import WLAN_CONFIG_MIB, parsing_wlan_info
from RuckusAutoTest.components.lib.snmp.zd.wlan_group_list import parsing_wlan_group_info
from RuckusAutoTest.components.lib.snmp.zd.aps_info import ZD_AP_MIB, parsing_ap_info

#SYSTEM_MIB = 'RUCKUS-ZD-SYSTEM-MIB'
SYSTEM_MIB_TOP_OBJECT_NAME = 'ruckusZDSystemMIB'
SYSTEM_OBJECT_NAME_INDEX = '0'
#AAA_SERVER_MIB = 'RUCKUS-ZD-AAA-MIB'
AAA_SERVER_MIB_TOP_OBJECT_NAME = 'ruckusZDAAAMIB'
#ZD_AP_MIB = 'RUCKUS-ZD-AP-MIB'
ZD_AP_MIB_TOP_OBJECT_NAME = 'ruckusZDAPMIB'
#WLAN_CONFIG_MIB = 'RUCKUS-ZD-WLAN-CONFIG-MIB'
WLAN_CONFIG_MIB_TOP_OBJECT_NAME = 'ruckusZDWLANConfigMIB'

OBJNAME_INDEX_TEMP = '%s.%s'
#=============================================#
#             Access Methods            
#=============================================#
def walking_system_mib(snmp):
    '''
    Walking the whole system mib and parsing system information.
    '''
    res_value = snmp.walk_by_name(SYSTEM_MIB, SYSTEM_MIB_TOP_OBJECT_NAME)
    sys_info_d = parsing_sys_info(res_value)
    sys_ip_info_d = parsing_sys_ip_info(res_value)
    sys_snmp_info_d = parsing_sys_snmp_info(res_value, False)
    
    all_sys_info_d = {}
    all_sys_info_d['sys_info'] = sys_info_d
    all_sys_info_d['sys_ip_info'] = sys_ip_info_d
    all_sys_info_d['sys_snmp_info'] = sys_snmp_info_d
    
    return all_sys_info_d

def walking_aaa_mib(snmp):
    '''
    Walking the whole aaa server mib and parsing aaa servers information.
    '''
    res_value = snmp.walk_by_name(AAA_SERVER_MIB, AAA_SERVER_MIB_TOP_OBJECT_NAME)
    
    return parsing_server_info(res_value)

def walking_wlan_config_mib(snmp):
    '''
    Walking the whole wlan mib and parsing wlan, wlan group information.
    '''
    res_value = snmp.walk_by_name(WLAN_CONFIG_MIB, WLAN_CONFIG_MIB_TOP_OBJECT_NAME)
    
    server_id_name_mapping = get_all_servers_id_name_mapping(snmp)
    
    wlan_info = parsing_wlan_info(res_value, server_id_name_mapping)
    
    wlan_id_name_mapping ={}
    for key, wlan_d in wlan_info.items():
        wlan_id_name_mapping[key] = wlan_d['name']
                
    wlan_group_info = parsing_wlan_group_info(snmp, res_value, wlan_id_name_mapping)
    
    wlan_mib_info = {}
    wlan_mib_info['wlan_info'] = wlan_info
    wlan_mib_info['wlan_group_info'] = wlan_group_info
    
    return wlan_mib_info

def walking_ap_mib(snmp):
    '''
    Walking the whole zd ap mib and parsing zd ap information.
    '''
    res_value = snmp.walk_by_name(ZD_AP_MIB, ZD_AP_MIB_TOP_OBJECT_NAME)
    
    return parsing_ap_info(res_value)
#=============================================#
#             Private Methods            
#=============================================#
