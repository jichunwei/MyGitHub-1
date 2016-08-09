'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for system snmp information, get, set and verify methods.  
'''
import time
import copy
import logging
import types

from RuckusAutoTest.common.Ratutils import get_random_string, get_random_int
from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.components.lib.snmp import snmphelper as helper


SYSTEM_MIB = 'RUCKUS-ZD-SYSTEM-MIB'
SYSTEM_SNMP_OBJECTS = 'ruckusZDSystemSNMP'
SYSTEM_SNMP_TRAP_OBJECT_NAME_IDNEX = 0
SYSTEM_SNMP_OBJECT_NAME_INDEX = 1
OBJNAME_INDEX_TEMP = '%s.%s'

snmp_trap_obj_abbr_name_mapping = {'trap_enable':'ruckusZDSystemSNMPTrapEnable',
                                   'trap_version':'ruckusZDSystemSNMPTrapVersion',}

v2_trap_table_obj = 'ruckusZDSystemSNMPV2TrapSvrTable'
v3_trap_table_obj = 'ruckusZDSystemSNMPV3TrapSvrTable'
#@Author: chen.tao@odc-ruckuswireless.com Since 2013-9-26 to delete ',' at the end of line 31 and 37
#Updated by cwang@20130529, Just support from 9.5
v2_trap_obj_abbr_name_mapping  = {'v2_trap_server':'ruckusZDSystemSNMPV2TrapServer'}
v3_trap_obj_abbr_name_mapping =  {'v3_trap_user':'ruckusZDSystemSNMPV3TrapUser',
                                    'v3_trap_server':'ruckusZDSystemSNMPV3TrapServer',
                                    'v3_trap_auth':'ruckusZDSystemSNMPV3TrapAuth',
                                    'v3_trap_auth_key':'ruckusZDSystemSNMPV3TrapAuthKey',
                                    'v3_trap_priv':'ruckusZDSystemSNMPV3TrapPrivacy',
                                    'v3_trap_priv_key':'ruckusZDSystemSNMPV3TrapPrivacyKey'}
#@Author: chen.tao@odc-ruckuswireless.com Since 2013-9-26 to delete ',' at the end of line 31 and 37
server_ip = 'Trap Server IP/IPV6 Address'

snmp_agent_v2_obj_abbr_name_mapping = {'v2_enable':'ruckusZDSystemSNMPEnable',
                                       'v2_ro_user':'ruckusZDSystemSNMPROCommunity',
                                       'v2_rw_user':'ruckusZDSystemSNMPRWCommunity',
                                       'v2_contact':'ruckusZDSystemSNMPSysContact',
                                       'v2_location':'ruckusZDSystemSNMPSysLocation',}

snmp_agent_v3_obj_abbr_name_mapping = {'v3_enable':'ruckusZDSystemSNMPV3Enable',
                                       'v3_ro_user':'ruckusZDSystemSNMPV3RoUser',
                                       'v3_ro_auth':'ruckusZDSystemSNMPV3RoAuth',
                                       'v3_ro_auth_key':'ruckusZDSystemSNMPV3RoAuthKey',
                                       'v3_ro_priv':'ruckusZDSystemSNMPV3RoPrivacy',
                                       'v3_ro_priv_key':'ruckusZDSystemSNMPV3RoPrivacyKey',
                                       'v3_rw_user':'ruckusZDSystemSNMPV3RwUser',
                                       'v3_rw_auth':'ruckusZDSystemSNMPV3RwAuth',
                                       'v3_rw_auth_key':'ruckusZDSystemSNMPV3RwAuthKey',
                                       'v3_rw_priv':'ruckusZDSystemSNMPV3RwPrivacy',
                                       'v3_rw_priv_key':'ruckusZDSystemSNMPV3RwPrivacyKey',
                                       }

snmp_obj_abbr_name_mapping = {}
#snmp_obj_abbr_name_mapping.update(snmp_trap_obj_abbr_name_mapping)
snmp_obj_abbr_name_mapping.update(snmp_agent_v2_obj_abbr_name_mapping)
snmp_obj_abbr_name_mapping.update(snmp_agent_v3_obj_abbr_name_mapping)

snmp_obj_abbr_fmtfunc_mapping = {'trap_enable': helper.convert_desc_to_enabled,
                                 'v2_enable': helper.convert_desc_to_enabled,
                                 'v3_enable': helper.convert_desc_to_enabled,
                                 'trap_version': helper.get_name_from_desc,
                                 'v3_trap_auth': helper.get_name_from_desc,
                                 'v3_trap_priv': helper.get_name_from_desc,
                                 'v3_ro_auth': helper.get_name_from_desc,
                                 'v3_ro_priv': helper.get_name_from_desc,
                                 'v3_rw_auth': helper.get_name_from_desc,
                                 'v3_rw_priv': helper.get_name_from_desc,
                                 }

rw_obj_type_mapping = {'trap_enable':'INTEGER',   #enable(1), disable(2)
                       'trap_version':'INTEGER',   #snmpv2(1), snmpv3(2)
                       'v2_trap_server':'STRING',   #(SIZE (2..40))                       
                       'v3_trap_user':'STRING',   #(SIZE(1..32))
                       'v3_trap_server':'STRING',   # (SIZE (2..40))
                       'v3_trap_auth':'INTEGER',   #md5(1), sha(2)
                       'v3_trap_auth_key':'STRING',   #(SIZE(8..32))
                       'v3_trap_priv':'INTEGER',   #des(1), aes(2), none(3)
                       'v3_trap_priv_key':'STRING',   #(SIZE(8..32))
                       'v2_enable':'INTEGER',   #enable(1), disable(2)
                       'v2_ro_user':'STRING',   #(SIZE(2..32))
                       'v2_rw_user':'STRING',   #(SIZE(2..32))
                       'v2_contact':'STRING',   #(SIZE(1..64))
                       'v2_location':'STRING',   #(SIZE(1..64))
                       'v3_enable':'INTEGER',   #enable(1), disable(2)
                       'v3_ro_user':'STRING',   #(SIZE(1..32))
                       'v3_ro_auth':'INTEGER',   #md5(1), sha(2)
                       'v3_ro_auth_key':'STRING',   #SIZE(8..32)
                       'v3_ro_priv':'INTEGER',   #des(1), aes(2), none(3)
                       'v3_ro_priv_key':'STRING',   #SIZE(8..32)
                       'v3_rw_user':'STRING',   #SIZE(1..32)
                       'v3_rw_auth':'INTEGER',   #md5(1), sha(2)
                       'v3_rw_auth_key':'STRING',   #SIZE(8..32)
                       'v3_rw_priv':'INTEGER',   #des(1), aes(2), none(3)
                       'v3_rw_priv_key':'STRING',   #SIZE(8..32)
                       'row_status': 'INTEGER',
                       }

rw_snmp_obj_order_list = ['v2_ro_user','v2_rw_user','v2_contact','v2_location','v2_enable',
                          'v3_ro_user','v3_ro_auth','v3_ro_auth_key','v3_ro_priv','v3_ro_priv_key',
                          'v3_rw_user','v3_rw_auth','v3_rw_auth_key','v3_rw_priv','v3_rw_priv_key','v3_enable']

rw_snmp_trap_obj_order_list = ['trap_version','trap_enable']
rw_snmp_trap_v2_obj_order_list = ['v2_trap_server','row_status']
rw_snmp_trap_v3_obj_order_list = ['v3_trap_user','v3_trap_server', 'v3_trap_auth','v3_trap_auth_key','v3_trap_priv','v3_trap_priv_key','row_status']

default_sys_snmp_info = {'v2_enable':'',
                         'v2_ro_user':'',
                         'v2_rw_user':'',
                         'v2_contact':'',
                         'v2_location':'',
                         'v3_enable':'',
                         'v3_ro_user':'',
                         'v3_ro_auth':'',
                         'v3_ro_auth_key':'',
                         'v3_ro_priv':'',
                         'v3_ro_priv_key':'',
                         'v3_rw_user':'',
                         'v3_rw_auth':'',
                         'v3_rw_auth_key':'',
                         'v3_rw_priv':'',
                         'v3_rw_priv_key':'',
                         }

default_sys_snmp_trap_info = {'trap_enable':'',
                              'v2_trap_server':'',
                              'trap_version':'',
                              'v3_trap_user':'',
                              'v3_trap_server':'',
                              'v3_trap_auth':'',
                              'v3_trap_auth_key':'',
                              'v3_trap_priv':'',
                              'v3_trap_priv_key':'',
                              }
#=============================================#
#             Access Methods            
#=============================================#
def get_sys_snmp_info(snmp, abbr_list = []):
    '''
    Get all system snmp information under system objects by walking system snmp objects.    
    '''
    new_dict = {}
    
    new_dict.update(get_sys_snmp_agent_v2_info(snmp,abbr_list))
    new_dict.update(get_sys_snmp_agent_v3_info(snmp,abbr_list))
    new_dict.update(get_sys_snmp_trap_info(snmp,abbr_list))
    
    return new_dict

def get_sys_snmp_agent_v2_info(snmp, abbr_list = []):
    '''
    Get snmp v2 agent information.
    '''
    agent_v2_dict = helper.get_item_detail_by_index(snmp, SYSTEM_MIB, snmp_agent_v2_obj_abbr_name_mapping, 
                                        SYSTEM_SNMP_OBJECT_NAME_INDEX, _convert_snmp_values_sys_snmp_objs, abbr_list)    
    return agent_v2_dict

def get_sys_snmp_agent_v3_info(snmp, abbr_list = []):
    '''
    Get snmp v3 agent information.
    '''
    agent_v3_dict = helper.get_item_detail_by_index(snmp, SYSTEM_MIB, snmp_agent_v3_obj_abbr_name_mapping, 
                                        SYSTEM_SNMP_OBJECT_NAME_INDEX, _convert_snmp_values_sys_snmp_objs, abbr_list)    
    return agent_v3_dict

#Updated by cwang@20130529, just support from build9.5
def get_sys_snmp_trap_info(snmp, abbr_list = []):
    '''
    Get snmp trap information.
    '''
    #Get trap status and version.
    trap_summary_dict = helper.get_item_detail_by_index(snmp, SYSTEM_MIB, snmp_trap_obj_abbr_name_mapping, 
                                                        SYSTEM_SNMP_TRAP_OBJECT_NAME_IDNEX, 
                                                        _convert_snmp_values_sys_snmp_objs, abbr_list)
    v2_trap_dict = {}
    v3_trap_dict = {}
    
    if helper.is_enabled(trap_summary_dict['trap_enable']):
        if trap_summary_dict['trap_version'].lower() == 'snmpv2':
            v2_trap_dict_original = helper.walking_mib(snmp, SYSTEM_MIB, v2_trap_table_obj)
            v2_trap_dict_original = _parsing_sys_snmp_trap_info(v2_trap_dict_original, v2_trap_obj_abbr_name_mapping)
            
            v2_trap_dict = {}
            for index, trap_info in v2_trap_dict_original.items():
                new_trap_info = _convert_snmp_values_sys_snmp_objs(trap_info)
                v2_trap_dict[index] = new_trap_info
        elif trap_summary_dict['trap_version'].lower() == 'snmpv3':
            v3_trap_dict_original = helper.walking_mib(snmp, SYSTEM_MIB, v3_trap_table_obj)
            v3_trap_dict_original = _parsing_sys_snmp_trap_info(v3_trap_dict_original, v3_trap_obj_abbr_name_mapping)
            
            v3_trap_dict = {}
            for index, trap_info in v3_trap_dict_original.items():
                new_trap_info = _convert_snmp_values_sys_snmp_objs(trap_info)
                v3_trap_dict[index] = new_trap_info
                
    trap_dict = {}
    trap_dict.update(trap_summary_dict)    
    if v2_trap_dict:
        trap_dict.update(v2_trap_dict)
    if v3_trap_dict:
        trap_dict.update(v3_trap_dict)    
        
    return trap_dict

def parsing_sys_snmp_info(res_dict, is_trap_include = True):
    '''
    Parsing the original result from snmp command. Convert key from oid(ruckusZDSystemName) to obj abbr(system_name).
    '''
    new_dict = {}
    if is_trap_include:
        trap_dict = helper.parsing_snmp_result(res_dict, snmp_trap_obj_abbr_name_mapping, SYSTEM_SNMP_TRAP_OBJECT_NAME_IDNEX)
        new_dict.update(trap_dict)
        
    v2_agent_dict = helper.parsing_snmp_result(res_dict, snmp_agent_v2_obj_abbr_name_mapping, SYSTEM_SNMP_OBJECT_NAME_INDEX)
    v3_agent_dict = helper.parsing_snmp_result(res_dict, snmp_agent_v3_obj_abbr_name_mapping, SYSTEM_SNMP_OBJECT_NAME_INDEX)
    
    new_dict.update(v2_agent_dict)
    new_dict.update(v3_agent_dict)
    
    new_dict = _convert_snmp_values_sys_snmp_objs(new_dict)
    
    return new_dict

def get_sys_oids_by_name(snmp):
    '''
    Get system oids for all system objects.
    '''
    return helper.get_item_oids(SYSTEM_MIB, snmp_obj_abbr_name_mapping)    

def get_trap_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'trap_enable')

def get_trap_version(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'trap_version')

def get_v2_trap_server(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_trap_server')

def get_v3_trap_user(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_trap_user')

def get_v3_trap_server(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_trap_server')

def get_v3_trap_auth(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_trap_auth')

def get_v3_trap_auth_key(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_trap_auth_key')

def get_v3_trap_priv(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_trap_priv')

def get_v3_trap_priv_key(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_trap_priv_key')

def get_v2_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_enable')

def get_v2_ro_user(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_ro_user')

def get_v2_rw_user(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_rw_user')

def get_v2_contact(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_contact')

def get_v2_location(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_location')

def get_v3_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_enable')

def get_v3_ro_user(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_ro_user')

def get_v3_ro_auth(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_ro_auth')

def get_v3_ro_auth_key(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_ro_auth_key')

def get_v3_ro_priv(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_ro_priv')

def get_v3_ro_priv_key(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_ro_priv_key')

def get_v3_rw_user(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v2_ro_user')

def get_v3_rw_auth(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_rw_auth')

def get_v3_rw_auth_key(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_rw_auth_key')

def get_v3_rw_priv(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_rw_priv')

def get_v3_rw_priv_key(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'v3_rw_priv_key')

def verify_sys_snmp_info_snmp_cli(snmp_d, cli_d):
    '''
    Verify system snmp info between snmp get and cli get.
    '''
    oids_d = helper.get_item_oids(SYSTEM_MIB, snmp_obj_abbr_name_mapping)
    res = helper.verify_one_item_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, 
                                 _item_verify_is_pass, oids_d, SYSTEM_SNMP_OBJECT_NAME_INDEX)
    
    return res

def verify_sys_snmp_info_snmp_gui(snmp_d, gui_d):
    '''
    Verify system snmp info between snmp get and gui get.
    '''
    oids_d = helper.get_item_oids(SYSTEM_MIB, snmp_obj_abbr_name_mapping)
    res = helper.verify_one_item_config(snmp_d, gui_d, _convert_gui_to_snmp_temp, 
                                 _item_verify_is_pass, oids_d, SYSTEM_SNMP_OBJECT_NAME_INDEX)
    
    return res

def verify_sys_snmp_info_snmp_test_data(snmp_d, test_data_d):
    '''
    Verify system snmp info between snmp get and snmp set.
    '''
    all_snmp_obj_name_mapping = snmp_obj_abbr_name_mapping
    all_snmp_obj_name_mapping.update(snmp_trap_obj_abbr_name_mapping)
    all_snmp_obj_name_mapping.update(v2_trap_obj_abbr_name_mapping)
    all_snmp_obj_name_mapping.update(v3_trap_obj_abbr_name_mapping)
    
    oids_d = helper.get_item_oids(SYSTEM_MIB, snmp_obj_abbr_name_mapping)
    
    new_snmp_d = {}
    
    new_test_data_d = {}
    new_test_data_d.update(test_data_d)
    
    for key in new_test_data_d.keys():
        if snmp_d.has_key(key):
            new_snmp_d[key] = snmp_d[key]
        
    snmp_trap_servers_info = {}
    test_trap_servers_info = {}
    for i in range(1,5):
        if new_snmp_d.has_key(str(i)):
            snmp_trap_servers_info[str(i)] = new_snmp_d.pop(str(i))
            test_trap_servers_info[str(i)] = new_test_data_d.pop(str(i))
            
    res = helper.verify_one_item_config(new_snmp_d, new_test_data_d, _convert_test_data_cfg, 
                                 _item_verify_is_pass, oids_d, SYSTEM_SNMP_OBJECT_NAME_INDEX)
    
    for index, snmp_server_info in snmp_trap_servers_info.items():
        test_server_info = test_trap_servers_info[index]
        for key in snmp_server_info.keys():
            if not test_server_info.has_key(key):
                snmp_server_info.pop(key)
                
        res_trap_server = helper.verify_one_item_config(snmp_server_info, test_server_info, _convert_test_data_cfg, 
                                 _item_verify_is_pass, oids_d, index)
        if res_trap_server:
            res.update(res_trap_server)
        
    return res

def gen_test_data_sys_snmp_info():
    '''
    Generate test value for readwrite object.
    '''    
    test_data_cfg = {}    
    
    type = 'alnum'
    
    test_data_cfg['v2_enable'] = 1 #get_random_int(1,1)
    
    test_data_cfg['v2_ro_user'] = get_random_string(type, 1, 32)
    test_data_cfg['v2_rw_user'] = get_random_string(type, 1, 32)
    test_data_cfg['v2_contact'] = get_random_string(type, 1, 64)
    test_data_cfg['v2_location'] = get_random_string(type, 1, 64) #(SIZE(1..64))
        
    test_data_cfg['v3_enable'] = 1 #get_random_int(1,2)
    test_data_cfg['v3_ro_user'] = get_random_string(type, 1, 31)    
    test_data_cfg['v3_ro_auth'] = get_random_int(1,2)
    test_data_cfg['v3_ro_auth_key'] = get_random_string(type, 8, 32)
    test_data_cfg['v3_ro_priv'] = get_random_int(1,3)
    if test_data_cfg['v3_ro_priv'] in [1,2]:  #If privacy is 3 - None, don't need to set priv key.
        test_data_cfg['v3_ro_priv_key'] = get_random_string(type, 8, 32)
    test_data_cfg['v3_rw_user'] = get_random_string(type, 1, 31)
    test_data_cfg['v3_rw_auth'] = get_random_int(1,2)
    test_data_cfg['v3_rw_auth_key'] = get_random_string(type, 8, 32)
    test_data_cfg['v3_rw_priv'] = get_random_int(1,3)
    if test_data_cfg['v3_rw_priv'] in [1,2]:
        test_data_cfg['v3_rw_priv_key'] = get_random_string(type, 8, 32)
    
    test_data_cfg['trap_enable'] = get_random_int(1,2)
    if test_data_cfg['trap_enable'] == 1:
        test_data_cfg['trap_version'] = get_random_int(1,2)
        
        if test_data_cfg['trap_version'] == 1:   #snmpv2
            test_data_cfg['v2_trap_server'] = helper.get_random_ip_addr()
            #test_data_cfg['v3_trap_user'] = get_random_string(type, 1, 32)
           
        else:
            test_data_cfg['v3_trap_server'] = helper.get_random_ip_addr()
            test_data_cfg['v3_trap_user'] = get_random_string(type, 1, 32)
            test_data_cfg['v3_trap_auth'] = get_random_int(1,2)
            test_data_cfg['v3_trap_auth_key'] = get_random_string(type, 8, 32)
            test_data_cfg['v3_trap_priv'] = get_random_int(1,3)
            test_data_cfg['v3_trap_priv_key'] = get_random_string(type, 8, 32)
    
    return test_data_cfg

def gen_test_data_sys_snmp_info_negative():
    '''
    Generate test value for readwrite object with negative values.
    '''
    type = 'alpha'
    str_65 = get_random_string(type, 65)
    str_33 = get_random_string(type, 33)
    str_32 = get_random_string(type, 32)
    str_41 = get_random_string(type, 41)
    
    test_data_cfg = {}
    
    test_data_cfg['v2_enable'] = '3' #(1,2)
    test_data_cfg['v2_ro_user'] = str_33 #(2,32)
    test_data_cfg['v2_rw_user'] = str_33 #(2,32)
    test_data_cfg['v2_contact'] = str_65 #SIZE(1..64)
    test_data_cfg['v2_location'] = str_65 #(SIZE(1..64))
        
    test_data_cfg['v3_enable'] = 3 #(1,2)
    test_data_cfg['v3_ro_user'] = str_32 #(1,31)
    test_data_cfg['v3_ro_auth'] = '3' #(1,2)
    test_data_cfg['v3_ro_auth_key'] = str_33 #(8,32)
    test_data_cfg['v3_ro_priv'] = '4' #(1,3)
    test_data_cfg['v3_ro_priv_key'] = str_33 #(8,32)
    test_data_cfg['v3_rw_user'] = str_32 #(1,31)
    test_data_cfg['v3_rw_auth'] = '3' #(1,2)
    test_data_cfg['v3_rw_auth_key'] = str_33  #(8,32)
    test_data_cfg['v3_rw_priv'] = '4' #(1,3)
    test_data_cfg['v3_rw_priv_key'] = str_33 #(8,32)    
    
    test_data_cfg['trap_enable'] = '3' #(1,2)
    test_data_cfg['trap_version'] = '3' #(1,2)
    test_data_cfg['v2_trap_server'] = str_41 #
    test_data_cfg['v3_trap_user'] = str_33 #(1,32)
    test_data_cfg['v3_trap_server'] = str_41 #(2..40, ip addr)
    test_data_cfg['v3_trap_auth'] = '3' #(1,2)
    test_data_cfg['v3_trap_auth_key'] = str_33 #(8,32)
    test_data_cfg['v3_trap_priv'] = '4' #(1,3)
    test_data_cfg['v3_trap_priv_key'] = str_33 #(8,32)
    
    return test_data_cfg

def set_sys_snmp_info(snmp, test_cfg, obj_list = [], is_update_snmp_cfg = True):
    '''
    Set value for snmp agent objects by snmp.
    When update snmp agent, need to update snmp configuration for get node value via snmp.
    '''
    rw_keys_mapping = {'v2_rw_user': 'community',
                       'v3_rw_user': 'sec_name',
                       'v3_rw_auth': 'auth_protocol',
                       'v3_rw_auth_key': 'auth_passphrase',
                       'v3_rw_priv': 'priv_protocol',
                       'v3_rw_priv_key': 'priv_passphrase',
                       }

    res_d = {}
    update_obj_list = [] 
    #Remove the setting item which not in obj list.
    if obj_list:
        for name, value in test_cfg.items():
            if name not in obj_list:
                test_cfg.pop(name)
            
    #Set snmp v2 and v3 agent.
    for name in rw_snmp_obj_order_list:
        if test_cfg.has_key(name):
            value = test_cfg[name]            
            oid = snmp_obj_abbr_name_mapping[name]
            index = SYSTEM_SNMP_OBJECT_NAME_INDEX                
            obj_type = rw_obj_type_mapping[name]
            res = helper.update_single_node_value(snmp, SYSTEM_MIB, oid, index, obj_type, value)
            
            if res:
                res_d.update(res)
            else:
                update_obj_list.append(name)
                    
            if is_update_snmp_cfg:
                list_not_wait = []
                list_not_wait.append('v2_contact')
                list_not_wait.append('v2_location')   
                if name not in list_not_wait:
                    # Need to wait sometime for agent update.
                    time.sleep(20)
                    
                #Update snmp conf when update read write config.
                if rw_keys_mapping.has_key(name):
                    if name == 'v3_rw_auth':
                        value = helper.convert_int_to_auth_protocol(value)
                    elif name == 'v3_rw_priv':
                        value = helper.convert_int_to_priv_protocol(value)
                    
                    snmp_conf = {}                    
                    snmp_conf[rw_keys_mapping[name]] = value
                                    
                    snmp.set_config(snmp_conf)     
                    
    res_trap_d, update_trap_obj_list = set_sys_snmp_trap_info(snmp, test_cfg)
    
    if res_trap_d:
        res_d.update(res_trap_d)
    else:
        update_obj_list.extend(update_trap_obj_list)
    
    logging.info("The items %s are updated." % update_obj_list)           
    return res_d


#Updated by cwang@20130529, Just support from 9.5
def set_sys_snmp_trap_info(snmp, test_cfg, obj_list = []):
    '''
    Set value for snmp trap objects by snmp.
    '''
    
    res_d = {}
    update_obj_list = []
    
    #Set trap v2 and v3 information.
    trap_obj_name_mapping = v2_trap_obj_abbr_name_mapping
    trap_obj_name_mapping.update(v3_trap_obj_abbr_name_mapping)
    
    rw_trap_server_obj_order_list = rw_snmp_trap_v2_obj_order_list
    rw_trap_server_obj_order_list.extend(rw_snmp_trap_v3_obj_order_list)
    
    
    logging.debug("Trap set cfg:%s" % test_cfg)
         
    #Remove the setting item which not in obj list.
    for name, value in test_cfg.items():
        if type(value) is types.DictionaryType and name in ['1', '2', '3', '4']:#server info
            for key, val in value.items(): 
                if (obj_list and key not in obj_list) or \
                    (key not in rw_trap_server_obj_order_list and key not in rw_snmp_trap_obj_order_list):
                    value.pop(key)
        else:
            if (obj_list and name not in obj_list) or \
            (name not in rw_trap_server_obj_order_list and name not in rw_snmp_trap_obj_order_list):
                test_cfg.pop(name)
                
    trap_set_cfg = copy.deepcopy(test_cfg)                     
    logging.debug("Trap set cfg - after remove some items:%s" % trap_set_cfg)
    
    #Set trap summary: enable and version.
    for name in rw_snmp_trap_obj_order_list:
        if trap_set_cfg.has_key(name):
            value = trap_set_cfg.pop(name)             
            #test_cfg.pop(name)            
            oid = snmp_trap_obj_abbr_name_mapping[name]
            index = SYSTEM_SNMP_TRAP_OBJECT_NAME_IDNEX
                
            obj_type = rw_obj_type_mapping[name]
            res = helper.update_single_node_value(snmp, SYSTEM_MIB, oid, index, obj_type, value)
            
            if res:
                res_d.update(res)
            else:
                update_obj_list.append(name)
    
    trap_server_info = {}       
    if trap_set_cfg.has_key('v2_trap_server'):
        trap_server_info['v2_trap_server'] = trap_set_cfg.pop('v2_trap_server')
        test_cfg.pop('v2_trap_server')
        
    for name in rw_snmp_trap_v3_obj_order_list:
        if trap_set_cfg.has_key(name):
            trap_server_info[name] = trap_set_cfg.pop(name)
            test_cfg.pop(name)
       
    logging.debug("Trap set cfg - trap servers:%s" % trap_set_cfg)
    #Remove all trap servers information.
    '''
    v2_index_list = _get_trap_server_index_list(snmp, 2)
    
    if v2_index_list:
        for index in v2_index_list:
            trap_server_cfg = {'index':  index}
            helper.update_objects_config(snmp, SYSTEM_MIB, v2_trap_obj_abbr_name_mapping, 
                                  rw_obj_type_mapping, rw_snmp_trap_v2_obj_order_list, trap_server_cfg, 3)
            time.sleep(10)
    
    v3_index_list = _get_trap_server_index_list(snmp, 3)
    for index in v3_index_list:
            trap_server_cfg = {'index':  index}
            helper.update_objects_config(snmp, SYSTEM_MIB, v3_trap_obj_abbr_name_mapping, 
                                  rw_obj_type_mapping, rw_snmp_trap_v3_obj_order_list, trap_server_cfg, 3)
            time.sleep(10)
    '''
             
    if trap_server_info:        
        trap_set_cfg['1'] = trap_server_info
        test_cfg['1'] = trap_server_info
        
    if trap_set_cfg:             
        #Set trap servers information.
        for index, trap_server_cfg in trap_set_cfg.items():
            for name in rw_trap_server_obj_order_list:
                if trap_server_cfg.has_key(name):
                    value = trap_server_cfg[name]            
                    oid = trap_obj_name_mapping[name]
                    index = index
                    obj_type = rw_obj_type_mapping[name]
                    
                    res = helper.update_single_node_value(snmp, SYSTEM_MIB, oid, index, obj_type, value)
                    if res:
                        res_d.update(res)
                    else:
                        update_obj_list.append(name)
                                  
    return res_d, update_obj_list

#=============================================#
#             Private Methods            
#=============================================#
def _get_trap_server_index_list(snmp, trap_version = 2):
    trap_abbr_name_mapping = v2_trap_obj_abbr_name_mapping
    trap_abbr_name_mapping.update(v3_trap_obj_abbr_name_mapping)
    
    oid = trap_abbr_name_mapping['v%s_trap_server' % trap_version]
    index_name_dict = helper.get_index_value_mapping(snmp, SYSTEM_MIB, oid)
    index_list = index_name_dict.keys()
    return index_list

def _get_sys_obj_value(snmp, obj_abbr):
    '''
    Get value for specified snmp name (get object name by obj_abbr).
    '''
    obj_name = snmp_obj_abbr_name_mapping[obj_abbr]
    
    item_value = helper.get_one_object_value_by_name(snmp, SYSTEM_MIB, obj_name, SYSTEM_SNMP_OBJECT_NAME_INDEX)

    if snmp_obj_abbr_fmtfunc_mapping.has_key(obj_abbr):
        value = snmp_obj_abbr_fmtfunc_mapping[obj_abbr](item_value)
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

    trap_version_cfg_list = ['trap_version']
    v2_trap_cfg_list = ['v2_trap_server']
    v3_trap_cfg_list = ['v3_trap_user','v3_trap_server','v3_trap_auth',
                        'v3_trap_auth_key','v3_trap_priv','v3_trap_priv_key']
    
    trap_cfg_list = trap_version_cfg_list + v2_trap_cfg_list + v3_trap_cfg_list
    #'v2_enable'
    #'v3_enable'
    v2_agent_cfg_list = ['v2_ro_user','v2_rw_user','v2_contact','v2_location']
    v3_agent_cfg_list = ['v3_ro_user','v3_ro_auth','v3_ro_auth_key','v3_ro_priv',
                         'v3_ro_priv_key','v3_rw_user','v3_rw_auth',
                         'v3_rw_auth_key','v3_rw_priv','v3_rw_priv_key']
    #The list which is password.
    keys_list = ['v3_trap_auth_key','v3_trap_priv_key','v2_ro_user','v2_rw_user',
                 'v3_ro_auth_key', 'v3_ro_priv_key', 'v3_rw_auth_key', 'v3_rw_priv_key']
    
    if key in  keys_list and _is_str_stars(value_d[key]):
        is_pass = True
        message = "Don't need to verify the field based on value is ******."
    elif key in trap_cfg_list:
        if value_d.has_key('trap_enable') and helper.is_disabled(value_d['trap_enable']):
            is_pass = True
            message = 'Not need to trap config if trap is disabled.'
        elif value_d.has_key('trap_version') and compare(value_d['trap_version'],'snmpv2', 'eq') and key in v3_trap_cfg_list:
            is_pass = True
            message = 'Trap version is 2, not need to verify v3 related config.'
        elif value_d.has_key('trap_version') and compare(value_d['trap_version'],'snmpv3', 'eq') and key in v2_trap_cfg_list:
            is_pass = True
            message = 'Trap version is 3, not need to verify v2 related config.'
    elif key in v2_agent_cfg_list and value_d.has_key('v2_enable') and helper.is_disabled(value_d['v2_enable']):
        is_pass = True
        message = 'V2 agent is disabled, not need to verify v2 related config.'
    elif key in v3_agent_cfg_list and value_d.has_key('v3_enable') and helper.is_disabled(value_d['v3_enable']):
        is_pass = True
        message = 'V3 agent is disabled, not need to verify v3 related config.'
           
    return is_pass, message
    
def _is_str_stars(str):
    '''
    Is the string only contains star char.
    '''
    import re
    
    pattern = '\*+'
    matcher = re.compile(pattern).match(str)
    if matcher:
        return True
    else:
        return False

def _convert_gui_to_snmp_temp(gui_sys_snmp_info_d):
    '''
    Convert system snmp information from gui to snmp temp.
    '''
    gui_sys_snmp_info = copy.deepcopy(default_sys_snmp_info)
    
    trap_enabled = gui_sys_snmp_info_d['trap']['enabled']
    gui_sys_snmp_info['trap_enable'] = helper.convert_bool_to_enabled(trap_enabled)

    if trap_enabled:
        gui_sys_snmp_info['trap_version'] = 'snmpv%s' % gui_sys_snmp_info_d['trap']['version']
        gui_sys_snmp_info['v2_trap_server'] = gui_sys_snmp_info_d['trap']['server_ip']
        gui_sys_snmp_info['v3_trap_user'] = gui_sys_snmp_info_d['trap']['sec_name']
        gui_sys_snmp_info['v3_trap_server'] = gui_sys_snmp_info_d['trap']['server_ip']
        gui_sys_snmp_info['v3_trap_auth'] = gui_sys_snmp_info_d['trap']['auth_protocol']
        gui_sys_snmp_info['v3_trap_auth_key'] = gui_sys_snmp_info_d['trap']['auth_passphrase']
        gui_sys_snmp_info['v3_trap_priv'] = gui_sys_snmp_info_d['trap']['priv_protocol']
        gui_sys_snmp_info['v3_trap_priv_key'] = gui_sys_snmp_info_d['trap']['priv_passphrase']

    v2_agent_enabled = gui_sys_snmp_info_d['v2_agent']['enabled']
    gui_sys_snmp_info['v2_enable'] = helper.convert_bool_to_enabled(v2_agent_enabled)

    if v2_agent_enabled:
        gui_sys_snmp_info['v2_ro_user'] = gui_sys_snmp_info_d['v2_agent']['ro_community']
        gui_sys_snmp_info['v2_rw_user'] = gui_sys_snmp_info_d['v2_agent']['rw_community']
        gui_sys_snmp_info['v2_contact'] = gui_sys_snmp_info_d['v2_agent']['contact']
        gui_sys_snmp_info['v2_location'] = gui_sys_snmp_info_d['v2_agent']['location']

    v3_agent_enabled = gui_sys_snmp_info_d['v3_agent']['enabled']
    gui_sys_snmp_info['v3_enable'] = helper.convert_bool_to_enabled(v2_agent_enabled)

    if v3_agent_enabled:
        gui_sys_snmp_info['v3_ro_user'] = gui_sys_snmp_info_d['v3_agent']['ro_sec_name']
        gui_sys_snmp_info['v3_ro_auth'] = gui_sys_snmp_info_d['v3_agent']['ro_auth_protocol']
        gui_sys_snmp_info['v3_ro_auth_key'] = gui_sys_snmp_info_d['v3_agent']['ro_auth_passphrase']
        gui_sys_snmp_info['v3_ro_priv'] = gui_sys_snmp_info_d['v3_agent']['ro_priv_protocol']
        gui_sys_snmp_info['v3_ro_priv_key'] = gui_sys_snmp_info_d['v3_agent']['ro_priv_passphrase']
        gui_sys_snmp_info['v3_rw_user'] = gui_sys_snmp_info_d['v3_agent']['rw_sec_name']
        gui_sys_snmp_info['v3_rw_auth'] = gui_sys_snmp_info_d['v3_agent']['rw_auth_protocol']
        gui_sys_snmp_info['v3_rw_auth_key'] = gui_sys_snmp_info_d['v3_agent']['rw_auth_passphrase']
        gui_sys_snmp_info['v3_rw_priv'] = gui_sys_snmp_info_d['v3_agent']['rw_priv_protocol']
        gui_sys_snmp_info['v3_rw_priv_key'] = gui_sys_snmp_info_d['v3_agent']['rw_priv_passphrase']
    
    return gui_sys_snmp_info

def _convert_cli_to_snmp_temp(cli_sys_snmp_info_d):
    '''
    Convert system snmp information from gui to snmp temp.
    '''
    new_cli_sys_snmp_info_d = copy.deepcopy(default_sys_snmp_info)
    
    if cli_sys_snmp_info_d.has_key('v2_agent'):
        v2_agent_enabled = cli_sys_snmp_info_d['v2_agent']['Status']
        new_cli_sys_snmp_info_d['v2_enable'] = v2_agent_enabled
    
        if helper.is_enabled(v2_agent_enabled):
            new_cli_sys_snmp_info_d['v2_ro_user'] = cli_sys_snmp_info_d['v2_agent']['RO Community']
            new_cli_sys_snmp_info_d['v2_rw_user'] = cli_sys_snmp_info_d['v2_agent']['RW Community']
            new_cli_sys_snmp_info_d['v2_contact'] = cli_sys_snmp_info_d['v2_agent']['Contact']
            new_cli_sys_snmp_info_d['v2_location'] = cli_sys_snmp_info_d['v2_agent']['Location']
    
    if cli_sys_snmp_info_d.has_key('v3_agent'):
        v3_agent_enabled = cli_sys_snmp_info_d['v3_agent']['status']
        new_cli_sys_snmp_info_d['v3_enable'] = v3_agent_enabled
    
        if helper.is_enabled(v3_agent_enabled):
            new_cli_sys_snmp_info_d['v3_ro_user'] = cli_sys_snmp_info_d['v3_agent']['ro_user']
            new_cli_sys_snmp_info_d['v3_ro_auth'] = cli_sys_snmp_info_d['v3_agent']['ro_auth']
            new_cli_sys_snmp_info_d['v3_ro_auth_key'] = cli_sys_snmp_info_d['v3_agent']['ro_auth_key']
    
            new_cli_sys_snmp_info_d['v3_ro_priv'] = cli_sys_snmp_info_d['v3_agent']['ro_priv']
            new_cli_sys_snmp_info_d['v3_ro_priv_key'] = cli_sys_snmp_info_d['v3_agent']['ro_priv_key']
            new_cli_sys_snmp_info_d['v3_rw_user'] = cli_sys_snmp_info_d['v3_agent']['rw_user']
            new_cli_sys_snmp_info_d['v3_rw_auth'] = cli_sys_snmp_info_d['v3_agent']['rw_auth']
            new_cli_sys_snmp_info_d['v3_rw_auth_key'] = cli_sys_snmp_info_d['v3_agent']['rw_auth_key']
            new_cli_sys_snmp_info_d['v3_rw_priv'] = cli_sys_snmp_info_d['v3_agent']['rw_priv']
            new_cli_sys_snmp_info_d['v3_rw_priv_key'] = cli_sys_snmp_info_d['v3_agent']['rw_priv_key']
            
    if cli_sys_snmp_info_d.has_key('trap'):
        new_cli_sys_snmp_info_d.update(_convert_cli_snmp_temp_trap(cli_sys_snmp_info_d))
            
    #Remove some keys if not used.
    remove_list = []    
    if not cli_sys_snmp_info_d.has_key('trap'):
        remove_list.extend(snmp_trap_obj_abbr_name_mapping.keys())
    if not cli_sys_snmp_info_d.has_key('v2_agent'):
        remove_list.extend(snmp_agent_v2_obj_abbr_name_mapping.keys())
    if not cli_sys_snmp_info_d.has_key('v3_agent'):
        remove_list.extend(snmp_agent_v3_obj_abbr_name_mapping.keys())
    
    for key in remove_list:
        if new_cli_sys_snmp_info_d.has_key(key):
            new_cli_sys_snmp_info_d.pop(key)
            
    return new_cli_sys_snmp_info_d 

def _convert_cli_snmp_temp_trap(cli_sys_snmp_info_d):
    '''
    '''
    
    new_cli_sys_snmp_info_d = {}
    if cli_sys_snmp_info_d.has_key('trap'):
        trap_info = cli_sys_snmp_info_d['trap']
        trap_enabled = trap_info['Status']
        new_cli_sys_snmp_info_d['trap_enable'] = trap_enabled
        
        if helper.is_enabled(trap_enabled):
            version = trap_info['Format'] #Version2, Version3
            if '2' in version:
                new_cli_sys_snmp_info_d['trap_version'] = 'snmpv2'
                for i in range(1,5):
                    key = str(i)
                    if trap_info.has_key(key):
                        single_trap_info = {key: {'v2_trap_server': trap_info[key][server_ip]}}
                        new_cli_sys_snmp_info_d.update(single_trap_info)
            else:
                new_cli_sys_snmp_info_d['trap_version'] = 'snmpv3'
                for i in range(1,5):
                    key = str(i)
                    if trap_info.has_key(key):
                        single_trap_info = {}
                        single_trap_info['v3_trap_user'] = trap_info[key]['User']
                        single_trap_info['v3_trap_server'] = trap_info[key][server_ip]
                        single_trap_info['v3_trap_auth'] = trap_info[key]['Authentication Type']
                        single_trap_info['v3_trap_auth_key'] = trap_info[key]['Authentication Pass Phrase']
                        single_trap_info['v3_trap_priv'] = trap_info[key]['Privacy Type']
                        if trap_info[key].has_key('Privacy Phrase'):
                            single_trap_info['v3_trap_priv_key'] = trap_info[key]['Privacy Phrase']
                        new_cli_sys_snmp_info_d.update({key: single_trap_info})
                        
    return new_cli_sys_snmp_info_d
    
def _convert_snmp_values_sys_snmp_objs(snmp_d):
    '''
    Convert snmp values of system snmp information.
    '''
    for key, value in snmp_d.items():
        if snmp_obj_abbr_fmtfunc_mapping.has_key(key):
            new_value = snmp_obj_abbr_fmtfunc_mapping[key](value)
            snmp_d[key] = new_value
        
    return snmp_d

def _convert_test_data_cfg (test_data_cfg):
    '''
    Convert some values in test data to same format as same format.
    '''
    abbr_fmtfunc_mapping = {'trap_enable': helper.convert_int_to_enabled,
                            'trap_version': helper.convert_int_to_snmp_version,
                            'v2_enable': helper.convert_int_to_enabled,
                            'v3_enable': helper.convert_int_to_enabled,
                            'v3_ro_auth': helper.convert_int_to_auth_protocol,
                            'v3_ro_priv': helper.convert_int_to_priv_protocol,
                            'v3_rw_auth': helper.convert_int_to_auth_protocol,
                            'v3_rw_priv': helper.convert_int_to_priv_protocol,
                            'v3_trap_auth': helper.convert_int_to_auth_protocol,
                            'v3_trap_priv': helper.convert_int_to_priv_protocol}
    
    new_test_data_cfg = copy.deepcopy(test_data_cfg)

    for key, value in new_test_data_cfg.items():
        if abbr_fmtfunc_mapping.has_key(key):
            convert_func = abbr_fmtfunc_mapping[key] 
            new_value = convert_func(value)
            new_test_data_cfg[key] = new_value

    return new_test_data_cfg

def _parsing_sys_snmp_trap_info(trap_dict, obj_abbr_name_mapping):
    '''
    Parsing system snmp trap information.
    '''
    new_trap_dict = {}
    for key,value in trap_dict.items():
        if '.' in key:
            obj_name = key.split('.')[0]
            obj_index = key.split('.')[1]
            obj_abbr = helper.get_dict_key_by_value(obj_abbr_name_mapping, obj_name)
            if obj_abbr:
                if not new_trap_dict.has_key(obj_index):
                    new_trap_dict[obj_index] = {}
                new_trap_dict[obj_index].update({obj_abbr: value})
                
    return new_trap_dict

