'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.14
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for wlan_group group information getting/setting/verify methods.
'''

import logging
import copy
import time
import re

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.Ratutils import get_random_string
from RuckusAutoTest.common.utils import compare

from RuckusAutoTest.components.lib.snmp.zd.wlan_list import get_wlan_index_value_mapping

WLAN_CONFIG_MIB = 'RUCKUS-ZD-WLAN-CONFIG-MIB'
WLAN_GROUP_CONFIG_TABLE = 'ruckusZDWLANGroupConfigTable'
WLAN_GROUP_CFG_ATTR_TABLE = 'ruckusZDWLANGroupCfgAttrTable'
WLAN_GROUP_CFG_OID_TEMP = '%s.%s'

#wlan_group config objects abbr and snmp full name mapping.
wlan_group_abbr_name_mapping = {'name':'ruckusZDWLANGroupConfigName',
                                'desc':'ruckusZDWLANGroupConfigDescription',
                                'vlan_override_flag':'ruckusZDWLANGroupVlanOverrideStatus',
                                'row_status':'ruckusZDWLANGroupConfigRowStatus',
                                }

#wlan group attr abr and snmp full name mapping. [mapping of wlan group and wlan]
wlan_group_attr_abbr_name_mapping = {'override_type':'ruckusZDWLANGroupCfgAttrOverrideType', #1: nochange(1), 2: untag(2), 3: tag(3)
                                     'vlan_tag':'ruckusZDWLANGroupCfgAttrWGVlanTag', #Description:    WLAN group vlan tag.
                                     #for set , range is :2-4094. for get , range is :0-4094: 
                                     #1: for node ruckusZDWLANGroupCfgAttrOverrideType is untag;
                                     #0: for node ruckusZDWLANGroupCfgAttrOverrideType is nochange
                                     'row_status':'ruckusZDWLANGroupCfgAttrRowStatus',
                                     }

#The snmp dict config template.
SNMP_CONF = {'name':'-',
             'desc':'-',
             'vlan_override_flag':'-',
             'wlan_member': {}
             }

#Object abbr and convert/format func mapping. 
col_get_func_mapping = {'vlan_override_flag': helper.convert_bool_to_enabled,
                        'override_type': helper.get_name_from_desc,
                        'vlan_tag': helper.get_name_from_desc,
                        }

#Read-write object abbr and data type mapping. 
group_cfg_rw_obj_type_mapping = {'name':'STRING', #1..32
                                 'desc':'STRING', #1..32
                                 'vlan_override_flag':'INTEGER', #
                                 'row_status':'INTEGER', #
                                 }

group_cfg_attr_rw_obj_type_mapping = {'wlan_group_id':'', #1..32
                                      'wlan_id':'', #1..32
                                      'override_type':'INTEGER', #nochange(1), untag(2), tag(3)
                                      'vlan_tag':'INTEGER', #1..4094
                                      'row_status':'INTEGER', #
                                      }

#Read-write object orders list when create a wlan_group. E.g. ssid is the first, rowstatus is the last one.
#Notes: 'vlan_override_flag' is read-only.
rw_group_config_keys_order_list = ['name', 'desc', 'row_status']
rw_group_cfg_attr_keys_order_list = ['override_type', 'vlan_tag', 'row_status']


#=============================================#
#             Access Methods            
#=============================================#

def get_wlan_groups_by_key_value(snmp, key_name = 'name', key_value = '*'):
    '''
    Get wlan_group information by specified column, and the value, default is name.
    If key_value is *, will get all wlan_groups.
    '''
    group_wlan_id_dict = _get_group_wlan_mapping(snmp)
    #Get index and value of key mapping.
    index_key_value_mapping = get_wlan_group_index_value_mapping(snmp, key_name)

    wlan_groups_d = {}
    if index_key_value_mapping:
        for group_id, value in index_key_value_mapping.items():
            if key_value == '*':
                wlan_groups_d[group_id] = get_wlan_group_detail_by_index(snmp, group_id, group_wlan_id_dict)
            else:
                if compare(value, key_value, 'eq'):
                    wlan_groups_d[group_id] = get_wlan_group_detail_by_index(snmp, group_id, group_wlan_id_dict)
                    break #break if find wlan_group

    return wlan_groups_d

def parsing_wlan_group_info(snmp, snmp_original_d, wlan_id_name_mapping):
    '''
    Parsing the result and get servers information. Key is server id, Value is server detail information.
    '''
    #Get all server index.
    wlan_group_id_list = []
    
    for key in snmp_original_d.keys():
        oid_list = key.split('.')
        obj_wlan_group_name = wlan_group_abbr_name_mapping['name']
        if compare(oid_list[0],obj_wlan_group_name, 'eq'):
            wlan_group_id_list.append(oid_list[1])
            
    wg_attr_dict = {}
    for key, value in snmp_original_d.items():
        wg_override = wlan_group_attr_abbr_name_mapping['override_type']
        oid_list = key.split('.')
        if compare(wg_override, oid_list[0], 'eq'):
            wg_attr_dict[key] = value
            
    wlan_groups_d = {}
    if wlan_group_id_list:
        for wlan_group_id in wlan_group_id_list:        
            wlan_group_info = helper.parsing_snmp_result(snmp_original_d, wlan_group_abbr_name_mapping, wlan_group_id, None)
            
            wg_wlan_mapping = _get_group_wlan_mapping(snmp, wg_attr_dict)
            wlan_members_d = {}
            if wg_wlan_mapping.has_key(wlan_group_id):
                wlan_ids_list = wg_wlan_mapping[wlan_group_id]
                for wlan_id in wlan_ids_list:
                    wlan_wg_id = '%s.%s' % (wlan_group_id,wlan_id)
                    wlan_name = wlan_id_name_mapping[wlan_id]
                    wlan_members_d[wlan_name] = helper.parsing_snmp_result(snmp_original_d, wlan_group_attr_abbr_name_mapping, wlan_wg_id, None)                
                    
            wlan_group_info['wlan_member'] = wlan_members_d            
            wlan_group_info = _convert_wlan_group_snmp_values(wlan_group_info)
            wlan_groups_d[wlan_group_id] = wlan_group_info
    
    return wlan_groups_d

def get_wlan_group_index_value_mapping(snmp, key_obj_name = 'name'):
    '''
    Get all wlan_group index and column [obj_abbr] value mapping.
    '''
    oid = wlan_group_abbr_name_mapping[key_obj_name]
    return helper.get_index_value_mapping(snmp, WLAN_CONFIG_MIB, oid)

def get_wlan_group_detail_by_index(snmp, index, group_wlan_id_mapping = {}, keys_list = []):
    '''
    Get one wlan_group detail config based on wlan_group index. 
    '''
    if not group_wlan_id_mapping:
        group_wlan_id_mapping = _get_group_wlan_mapping(snmp)

    wlan_group_d = helper.get_item_detail_by_index(snmp, WLAN_CONFIG_MIB, wlan_group_abbr_name_mapping, index, None, keys_list)

    if not keys_list or 'wlan_member' in keys_list:
        wlan_group_d['wlan_member'] = _get_wlan_group_attr_by_group_index(snmp, index, group_wlan_id_mapping)

    wlan_group_d = _convert_wlan_group_snmp_values(wlan_group_d)

    return wlan_group_d

def verify_wlan_groups_snmp_cli(snmp_wlan_groups_d, cli_wlan_groups_d):
    return _verify_wlan_groups_dict(snmp_wlan_groups_d, cli_wlan_groups_d, _convert_cli_to_snmp_temp)

def verify_wlan_groups_snmp_gui(snmp_wlan_groups_d, gui_wlan_groups_d):
    return _verify_wlan_groups_dict(snmp_wlan_groups_d, gui_wlan_groups_d, _convert_gui_to_snmp_temp)

def verify_one_wlan_group_snmp_cli(snmp_d, cli_d, index):
    all_group_abbr_name_mapping = wlan_group_abbr_name_mapping + wlan_group_attr_abbr_name_mapping
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, all_group_abbr_name_mapping)

    return _verify_one_wlan_group_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, oids_d, index)

def verify_one_wlan_group_snmp_gui(snmp_d, gui_d, index):
    all_group_abbr_name_mapping = wlan_group_abbr_name_mapping + wlan_group_attr_abbr_name_mapping
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, all_group_abbr_name_mapping)

    return _verify_one_wlan_group_config(snmp_d, gui_d, _convert_gui_to_snmp_temp, oids_d, index)

def verify_wlan_groups_test_data_snmp(snmp_wlan_groups_d, test_data_wlan_groups_d):
    '''
    Verify wlan_group information: pre-config data and values from snmp. 
    '''
    all_group_abbr_name_mapping = {}
    all_group_abbr_name_mapping.update(wlan_group_abbr_name_mapping)
    all_group_abbr_name_mapping.update(wlan_group_attr_abbr_name_mapping)
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, all_group_abbr_name_mapping)

    res_wlan_groups_d = {}

    try:
        #Remove default wlan group from snmp.
        snmp_wlan_groups_copy_d = copy.deepcopy(snmp_wlan_groups_d)
        if snmp_wlan_groups_copy_d.has_key('1'):
            snmp_wlan_groups_copy_d.pop('1')

        if len(test_data_wlan_groups_d) != len(snmp_wlan_groups_copy_d):
            res_wlan_groups_d['ALL'] = 'The count of wlan_group from test data and snmp are not same. test_data = %s,snmp = %s' \
                             % (len(test_data_wlan_groups_d), len(snmp_wlan_groups_copy_d))
        else:
            for group_id, snmp_wlan_group_d in snmp_wlan_groups_copy_d.items():
                test_group_d = test_data_wlan_groups_d[group_id]
                res_d = _verify_one_group_test_data_snmp(snmp_wlan_group_d, test_group_d, oids_d, group_id)
                if res_d:
                    res_wlan_groups_d.update({group_id: res_d})
    except Exception, e:
        res_wlan_groups_d = {'Exception':'message = %s' % e}
        logging.warning(res_wlan_groups_d)

    return res_wlan_groups_d

def verify_update_wlan_group(snmp, group_id, update_cfg_list):
    '''
    Update the wlan information, and then verify the value is updated.
    '''
    all_group_abbr_name_mapping = {}
    all_group_abbr_name_mapping.update(wlan_group_abbr_name_mapping)
    all_group_abbr_name_mapping.update(wlan_group_attr_abbr_name_mapping)
     
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, all_group_abbr_name_mapping)

    index = 0
    res_groups_d = {}

    for group_cfg in update_cfg_list:        
        index += 1
        update_wlan_group(snmp, group_cfg, group_id)
        keys_list = []
        keys_list = group_cfg.keys()
        #If we update wlan_member, need to get override flag.        
        if group_cfg.has_key('wlan_member'):
            keys_list.append('vlan_override_flag')
        #When we add new wlan_member, need to update this dict also.    
        group_wlan_id_mapping = _get_group_wlan_mapping(snmp)
        snmp_group_d = get_wlan_group_detail_by_index(snmp, group_id, group_wlan_id_mapping, keys_list)
        res_d = _verify_one_group_test_data_snmp(snmp_group_d, group_cfg, oids_d, group_id)
        if res_d:
            res_groups_d[index] = {'Config': group_cfg, 'Result': res_d}

    return res_groups_d

def update_wlan_group(snmp, group_cfg, group_id):
    '''
    Update aaa server by specified config. 
    '''
    new_group_cfg = {'index': group_id}
    new_group_cfg.update(group_cfg)
    _update_wlan_group_config(snmp, new_group_cfg, 2)

def remove_all_wlan_groups(snmp):
    '''
    Remove all exist wlan_groups. 
    Notes: The wlan_group can't be deleted successfully if it is included in one wlan_group group.     
    '''
    wlan_group_index_list = get_wlan_group_index_value_mapping(snmp).keys()

    #Default group can't be deleted, whose index is 1.
    if '1' in wlan_group_index_list:
        wlan_group_index_list.remove('1')

    #Default wlan group can't be deleted.
    if len(wlan_group_index_list) > 0:
        delete_wlan_groups(snmp, wlan_group_index_list)

def delete_wlan_groups(snmp, wlan_group_index_list):
    '''
    Delete the wlan_groups by index exist in wlan_group_index_list.
    Update row_status as 6, the wlan_group is deleted.
    '''
    error_index_list = []
    
    for group_id in wlan_group_index_list:
        group_cfg = {'index': group_id}
        _update_wlan_group_config(snmp, group_cfg, 3)
        
        result = False
        for i in range(1,5):
            time.sleep(10)
            if not _check_wlan_group_exist_by_index(snmp, group_id):
                result = True
                logging.info('The wlan_group has been deleted successfully. Index = %s' % group_id)
                break
            else:
                logging.info('The wlan_group is not deleted. Index = %s' % group_id)
                
        if not result:
            error_index_list.append(group_id)

    return error_index_list

def create_wlan_groups(snmp, wlan_group_cfg_list = {}, wlan_name_list = {}):
    '''
    Create all wlan_groups based on wlan_group_cfg_list [The list with wlan_group config]
    Return:
        The dict of wlan_group details with key = index.
        {'1': {name='test1',ssid='test1',...} }
    '''
    wlan_group_list_d = {}

    if not wlan_group_cfg_list:
        wlan_group_cfg_list = gen_wlan_group_test_cfg(wlan_name_list)

    for wlan_group_cfg in wlan_group_cfg_list:
        res, index = create_one_wlan_group(snmp, wlan_group_cfg)
        if res: 
            wlan_group_list_d.update({str(index): wlan_group_cfg})

    return wlan_group_list_d

def create_one_wlan_group(snmp, wlan_group_cfg):
    '''
    Create a wlan_group based on specified config. 
    Re-construct to a parameter list based on wlan_group detail config,
    then call snmp method to create wlan_group.
    Notes:    
    When call set_multi_by_name, the parameters is the list of the dict 
    with format {'mib':'','oid': '', 'index': '','type': '', 'value':''}
    '''
    index = _gen_new_index(snmp)
    if index == 0:
        raise Exception("Can't get the index for wlan_group. [Only can create 32 wlan_groups]")

    new_group_cfg = {'index': str(index)}
    new_group_cfg.update(wlan_group_cfg)
    
    result = False

    _update_wlan_group_config(snmp, new_group_cfg, 1)

    if _check_wlan_group_exist_by_index(snmp, index):
        result = True
        logging.info('The wlan_group is created successfully. Index=%s' % index)
    else:
        result = False
        logging.warning('The wlan_group is not created. Index=%s' % index)

    return result, index

def gen_wlan_group_test_cfg(wlan_name_list = {}):
    '''
    Get wlan_group test cfg: some kinds of wlan_group list. The value is same as original from snmp.
    Can't support to create wlan_group with type is Guest account and Hotspot server.
    '''    
    #Get raidius auth and radius accounting server. [If does not exist, will create them.]    
    wlan_groups_list = [dict(name = 'GroupTest-new1', desc = 'GroupTest2 - 123',
                             wlan_member = {}), ]
    
    if wlan_name_list:
        wlan_members = {}
#        wlan_member_cfg = [{'override_type': 'tag(3)', 'vlan_tag': '3'},
#                           {'override_type': 'untag(2)' },
        wlan_member_cfg = [{'override_type': 'tag(2)', 'vlan_tag': '3'},
                           {'override_type': 'nochange(1)'}
                          ]

        for i in range(0, len(wlan_name_list)):
            wlan_name = wlan_name_list[i]
#            cfg_index = i % 3
            cfg_index = i % 2
            wlan_members[wlan_name] = wlan_member_cfg[cfg_index]

        wlan_groups_list.extend([dict(name = 'GroupTest-new2', desc = 'GroupTest1 - 123',
                             wlan_member = wlan_members) ])

    return wlan_groups_list

def gen_wlan_group_update_test_cfg(snmp, wlan_name_list):
    '''
    Get wlan_group test cfg: some kinds of wlan_group list. The value is same as original from snmp.
    Can't support to create wlan_group with type is Guest account and Hotspot server.
    Notes:
        1. vlan_override_flag='false(2)', this node is read-only.
    '''
    #Get raidius auth and radius accounting server. [If does not exist, will create them.]
    create_cfg_list = [dict(name = 'GroupTest', desc = 'GroupTestDescription', wlan_member = {})]
    update_cfg_list = [dict(desc = 'DescriptionUpdateTest.')]
    
    if wlan_name_list:
        wlan_members = {}
#        wlan_member_cfg = [{'override_type': 'tag(3)', 'vlan_tag': '3'},
#                           {'override_type': 'untag(2)' },
        wlan_member_cfg = [{'override_type': 'tag(2)', 'vlan_tag': '3'},
                           {'override_type': 'nochange(1)'}
                          ]

        for i in range(0, len(wlan_name_list)):
            wlan_name = wlan_name_list[i]
#            cfg_index = i % 3
            cfg_index = i % 2
            wlan_members[wlan_name] = wlan_member_cfg[cfg_index]
    
        update_cfg_list.append(dict(wlan_member = wlan_members))
        
        wlan_members_2 = {}
#        wlan_member_cfg_2 = [{'override_type': 'untag(2)' },
#                           {'override_type': 'nochange(1)'},
#                           {'override_type': 'tag(3)', 'vlan_tag': '3'},]
        wlan_member_cfg_2 = [{'override_type': 'nochange(1)'},
                             {'override_type': 'tag(2)', 'vlan_tag': '3'},                          ]
                               
        for i in range(0, len(wlan_name_list)):
            wlan_name = wlan_name_list[i]
#            cfg_index = i % 3
            cfg_index = i % 2
            wlan_members_2[wlan_name] = wlan_member_cfg_2[cfg_index]
        
        update_cfg_list.append(dict(wlan_member = wlan_members_2))

    return create_cfg_list, update_cfg_list


def gen_wlan_group_cfg_negative():
    '''
    Generate negative input for wlan group config.
    '''
    type = 'alpha'
    str_33 = get_random_string(type, 33)
    str_65 = get_random_string(type, 65)
    
    wlan_group_cfg = {}
    
    wlan_group_cfg['name'] = str_33 #1..32
    wlan_group_cfg['desc'] = str_65 #1..64 
       
    wlan_group_cfg['override_type'] = '4' #nochange(1), untag(2), tag(3)
    wlan_group_cfg['vlan_tag'] = '4095'  #1..4094
    
    return wlan_group_cfg

def update_wlan_group_cfg_one_by_one(snmp, index, test_cfg):
    '''
    Update server config items, one by one.
    '''
    res_d = {}
    
    group_id = index
    wlan_id = ''
    
    #Get wlan id for this group.    
    all_group_wlan_mapping = _get_group_wlan_mapping(snmp)
    
    if all_group_wlan_mapping.has_key(group_id):
        group_wlan_mapping = all_group_wlan_mapping[group_id]
        if len(group_wlan_mapping) > 0:
            wlan_id = group_wlan_mapping[0]
            
    for obj_name, value in test_cfg.items():
        #Update wlan group setting.
        if obj_name in rw_group_config_keys_order_list:
            oid = wlan_group_abbr_name_mapping[obj_name]
            obj_type = group_cfg_rw_obj_type_mapping[obj_name]
            new_index = group_id
            
        elif obj_name in rw_group_cfg_attr_keys_order_list:
            oid = wlan_group_attr_abbr_name_mapping[obj_name]
            obj_type = group_cfg_attr_rw_obj_type_mapping[obj_name]
            new_index = '%s.%s' % (group_id, wlan_id)
            
        res = helper.update_single_node_value(snmp, WLAN_CONFIG_MIB, oid, new_index, obj_type, value)
        
        if res:
            res_d.update({obj_name : res})
        
    return res_d

#=============================================#
#             Private Methods            
#=============================================#
def _convert_wlan_group_snmp_values(wlan_group_d):
    '''
    Convert wlan_group values based on col_get_func_mapping dict. 
    '''
    for key, value in wlan_group_d.items():
        new_value = value
        if key == 'wlan_member' and len(new_value) > 0:
            new_value = _convert_wlan_group_wlan_members(new_value)
        elif key in col_get_func_mapping.keys():
            convert_func = col_get_func_mapping[key]
            new_value = convert_func(value)
        wlan_group_d[key] = new_value

    return wlan_group_d

def _convert_wlan_group_wlan_members(wlan_member_dict):
    '''
    Convert wlan group config attribute - wlan members. 
    '''
    ret_wlan_mem_dict = {}
    if wlan_member_dict:
        for name, wlan_d in wlan_member_dict.items():
            for key, value in wlan_d.items():
                new_value = value
                if key in col_get_func_mapping.keys():
                    convert_func = col_get_func_mapping[key]
                    new_value = convert_func(value)
                wlan_d[key] = new_value
            ret_wlan_mem_dict[name] = wlan_d

    return ret_wlan_mem_dict

def _gen_new_index(snmp):
    '''
    Generate new index for create wlan_group. 
    Return the index does not exist in current wlan_group list, range is 2 to 32.
    1 is for default, so start from 2.
    If return as 0, there are 32 wlan_groups exist.
    '''
    start_index = 2
    max_index = 32
    oid = wlan_group_abbr_name_mapping['name']
    new_index = helper.gen_new_index(snmp, WLAN_CONFIG_MIB, oid, start_index, max_index)
    return new_index

def _item_verify_is_pass(value_d, key):
    '''
    Check whether the item is no no need to verify.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''

    if key == 'vlan_override_flag':
        message = 'Do not need to verify vlan override flag. [No value from CLI, GUI is always true]'
        is_pass = True

    return is_pass, message

def _get_expect_override_flag(wlan_members_dict):
    '''
    Get expected override flag.
    If one of wlan member is 'tag', it is true, false if else.
    '''
    expect_override_flag = 'Disabled'
    if wlan_members_dict:
        for wlan_d in wlan_members_dict.values():
            if compare(wlan_d['override_type'], 'tag', 'eq'):
                expect_override_flag = 'Enabled'
                break

    return expect_override_flag

def _convert_cli_to_snmp_temp(cli_wlan_group_d):
    '''
    Convert cli wlan_group dict to same snmp dict structure.
    '''
    #Dict key mapping: snmp and cli. 
    keys_snmp_cli_mapping = {'name': 'Name',
                             'desc':'Description',
                             'vlan_override_flag':'vlan_override'}

    new_cli_wlan_group_d = copy.deepcopy(SNMP_CONF)

    for key, cli_key in keys_snmp_cli_mapping.items():
        new_value = ''
        if cli_wlan_group_d.has_key(cli_key):
            new_value = cli_wlan_group_d[cli_key]
            if compare(key, 'vlan_override_flag', 'eq'):
                new_value = helper.convert_bool_to_enabled(new_value)
        new_cli_wlan_group_d[key] = new_value
                                            
    if cli_wlan_group_d.has_key('WLAN Service'):
        wlan_members = {}
        wlans_dict = cli_wlan_group_d['WLAN Service']
        for wlan_d in wlans_dict.values():
            new_wlan_d = {'vlan_tag': '', 'override_type': ''}
            cli_vlan = wlan_d['VLAN']
            
            ptn = '(?P<vlan_tag>[0-9]+)\((?P<type>[A-Za-z]+)\)' #version 9.3 and before, value: '3(Tag)' or '1(Untag)' or ''
            matcher = re.compile(ptn, re.IGNORECASE).match(cli_vlan)
            
            if matcher:
                vlan_dict = matcher.groupdict()
                new_wlan_d['override_type'] = vlan_dict['type']
                new_wlan_d['vlan_tag'] = vlan_dict['vlan_tag']
            else:
                match2 = re.match('[0-9]+', cli_vlan) #version9.4 and later, value: '3', '1' or ''
                if match2:
                    new_wlan_d['override_type'] = 'tag' 
                    new_wlan_d['vlan_tag'] = cli_vlan
                else:
                    new_wlan_d['override_type'] = 'nochange'
                    new_wlan_d['vlan_tag'] = '0'
           
            wlan_members[wlan_d['NAME']] = new_wlan_d
        new_cli_wlan_group_d['wlan_member'] = wlan_members

    return new_cli_wlan_group_d

def _convert_gui_to_snmp_temp(gui_wlan_group_d):
    '''
    Convert gui wlan_group dict to same snmp dict structure.
    '''
    keys_snmp_gui_mapping = {'name': 'name',
                             'desc':'description',
                             'vlan_override_flag':'vlan_override'}

    new_gui_wlan_group_d = copy.deepcopy(SNMP_CONF)

    for key, gui_key in keys_snmp_gui_mapping.items():
        new_value = ''
        if gui_wlan_group_d.has_key(gui_key):
            new_value = gui_wlan_group_d[gui_key]
        new_gui_wlan_group_d[key] = new_value

    if gui_wlan_group_d.has_key('wlan_member'):
        wlan_members = {}
        wlans_dict = gui_wlan_group_d['wlan_member']
        for wlan_name, wlan_d in wlans_dict.items():
            new_wlan_d = {'vlan_tag': '', 'override_type': ''}
            new_wlan_d['override_type'] = wlan_d['vlan_override']
            if compare(new_wlan_d['override_type'], 'No Change', 'eq'):
                new_wlan_d['override_type'] = 'nochange'
                new_wlan_d['vlan_tag'] = '0'
            elif compare(new_wlan_d['override_type'], 'untag', 'eq'):
                new_wlan_d['vlan_tag'] = '1'
            else:
                new_wlan_d['vlan_tag'] = wlan_d['tag_override']

            wlan_members[wlan_name] = new_wlan_d
        new_gui_wlan_group_d['wlan_member'] = wlan_members

    return new_gui_wlan_group_d

def _check_wlan_group_exist_by_index(snmp, index):
    '''
    Check wether the wlan_group with specified index exist. 
    Return true if exist, false if does not exist.
    '''
    # Check the wlan_group is created successfully.
    index_wlan_group_name_mapping = get_wlan_group_index_value_mapping(snmp)
    if index_wlan_group_name_mapping and index_wlan_group_name_mapping.has_key(str(index)):
        result = True
    else:
        result = False

    return result

def _get_wlan_group_attr_by_group_index(snmp, group_id, group_wlan_id_mapping):
    '''
    Get wlan group attr - wlan members information by wlan group id.
    '''
    wlan_members_dict = {}
    if group_wlan_id_mapping.has_key(group_id):
        wlan_id_list = group_wlan_id_mapping[group_id]
        wlan_name_index_mapping = get_wlan_index_value_mapping(snmp)

        for wlan_id in wlan_id_list:
            wlan_name = wlan_name_index_mapping[wlan_id]
            index = WLAN_GROUP_CFG_OID_TEMP % (group_id, wlan_id)
            wlan_members_d = helper.get_item_detail_by_index(snmp, WLAN_CONFIG_MIB, wlan_group_attr_abbr_name_mapping, index, None)
            wlan_members_dict[wlan_name] = wlan_members_d

    return wlan_members_dict

def _get_group_wlan_mapping(snmp, res_dict = {}):
    '''
    Get group id and wlan id mapping. 
    Output:
      {'1':['1','2'], '2': ['1']}
    '''
    key_obj_name = wlan_group_attr_abbr_name_mapping['override_type']
    if not res_dict:
        res_dict = snmp.walk_by_name(WLAN_CONFIG_MIB, key_obj_name)

    pattern = '.+.(?P<wlan_group_id>[0-9]+).(?P<wlan_id>[0-9]+)'

    group_wlan_dict = {}
    for key in res_dict.keys():
        matcher = re.compile(pattern).match(key)
        if matcher:
            dict = matcher.groupdict()
            wlan_group_id = dict['wlan_group_id']
            wlan_id = dict['wlan_id']
            if group_wlan_dict.has_key(wlan_group_id):
                group_wlan_dict[wlan_group_id].append(wlan_id)
            else:
                group_wlan_dict[wlan_group_id] = [wlan_id]

    return group_wlan_dict

def _update_wlan_group_config(snmp, wlan_group_cfg, flag):
    '''
    Update wlan group: create on wlan group, update some settings, delete the wlan group.
    Input:
        flag: 1 - create
        wlan_group_cfg: include indexs and setting's value dict.
        {index:3, desc='this is test.'...}
    '''
    group_id = wlan_group_cfg['index']

    if flag == 3:
        #group_wlan_id_mapping = _get_group_wlan_mapping(snmp)
        mib = WLAN_CONFIG_MIB
        value = '6'
        #Remove wlan for the group - the nodes in ruckusZDWLANGroupCfgAttrTable.
        '''
        if group_wlan_id_mapping.has_key(group_id):
            wlan_id_list = group_wlan_id_mapping[group_id]
            oid = wlan_group_attr_abbr_name_mapping['row_status']
            oid = WLAN_GROUP_CFG_OID_TEMP % (oid, group_id)
            obj_type = group_cfg_attr_rw_obj_type_mapping['row_status']

            for wlan_id in wlan_id_list:
                helper.update_single_node_value(snmp, mib, oid, wlan_id, obj_type , value)
        '''
        #Remove wlan group in ruckusZDWLANGroupConfigTable.    
        oid = wlan_group_abbr_name_mapping['row_status']
        obj_type = group_cfg_rw_obj_type_mapping['row_status']
        helper.update_single_node_value(snmp, mib, oid, group_id, obj_type , value)

        time.sleep(10)
    else:
        wlan_group_config_list = []
        for key in rw_group_config_keys_order_list:
            item_d = {}
            item_d['mib'] = WLAN_CONFIG_MIB
            item_d['oid'] = wlan_group_abbr_name_mapping[key]
            item_d['type'] = group_cfg_rw_obj_type_mapping[key]
            item_d['index'] = group_id
            if flag == 1 and key == 'row_status':
                #For create, set row status as 4.
                item_d['value'] = '4'
                wlan_group_config_list.append(item_d)
            elif wlan_group_cfg.has_key(key):
                item_d['value'] = helper.get_value_from_desc(wlan_group_cfg[key])
                wlan_group_config_list.append(item_d)

        if len(wlan_group_config_list) > 0:
            snmp.set_multi_by_name(wlan_group_config_list)

        time.sleep(10)

        #Update wlan members under table: ruckusZDWLANGroupCfgAttrTable.
        if wlan_group_cfg.has_key('wlan_member'):
            # Check the server is created successfully.
            index_group_mapping = get_wlan_group_index_value_mapping(snmp)

            if index_group_mapping.has_key(str(group_id)):
                index_wlan_mapping = get_wlan_index_value_mapping(snmp)

                wlan_cfg_dict = wlan_group_cfg['wlan_member']

                if len(wlan_cfg_dict) > 0:
                    for wlan_name, attr_cfg in wlan_cfg_dict.items():
                        #Get wlan id by wlan name.
                        wlan_id = helper.get_dict_key_by_value(index_wlan_mapping, wlan_name)
                        wlan_group_attr_config_list = []
                        for key in rw_group_cfg_attr_keys_order_list:
                            item_d = {}
                            item_d['mib'] = WLAN_CONFIG_MIB
                            item_d['oid'] = wlan_group_attr_abbr_name_mapping[key]
                            item_d['type'] = group_cfg_attr_rw_obj_type_mapping[key]
                            #For attr, index must be format of <group_id>.<wlan_id>.
                            item_d['index'] = WLAN_GROUP_CFG_OID_TEMP % (group_id, wlan_id)
                            if flag == 1 and key == 'row_status':
                                #For create, set row status as 4.
                                item_d['value'] = '4'
                                wlan_group_attr_config_list.append(item_d)
                            elif attr_cfg.has_key(key):
                                item_d['value'] = helper.get_value_from_desc(attr_cfg[key])
                                wlan_group_attr_config_list.append(item_d)

                        if len(wlan_group_attr_config_list) > 0:
                            snmp.set_multi_by_name(wlan_group_attr_config_list)
                            time.sleep(10)

def _verify_one_group_test_data_snmp(snmp_group_d, test_group_d, oids_d, group_id):
    res_d = {}

    test_group_d = _convert_wlan_group_snmp_values(test_group_d)

    # Remove row_status from snmp_wlan_d.            
    if snmp_group_d.has_key('row_status'):
        snmp_group_d.pop('row_status')

    # Generate vlan override flag by wlan_member.
    if snmp_group_d.has_key('wlan_member'):
        test_group_d['vlan_override_flag'] = _get_expect_override_flag(snmp_group_d['wlan_member'])
        #Update vlan_tag in test config.
        wlan_members_d = test_group_d['wlan_member']
        test_group_d['wlan_member'] = _update_vlan_tag(wlan_members_d)

    snmp_keys = snmp_group_d.keys()
    test_data_keys = test_group_d.keys()
    snmp_keys.sort()
    test_data_keys.sort()

    # Verify keys in snmp, cli and gui values dict.
    if not (snmp_keys == test_data_keys):
        res = 'Keys from test data and snmp dict are different. Snmp keys: %s, test_data_keys: %s' % (snmp_keys, test_data_keys)
        res_d['ALL'] = res
        logging.warning(res)

    for key, value in snmp_group_d.items():
        res = ''
        if key == 'wlan_member':
            #res = _verify_group_wlan_members_test_data_snmp(value, test_group_d[key], oids_d, group_id)
            res = helper.verify_items_dict(value, test_group_d[key], None, None, oids_d)
            if res.has_key('ALL'):
                if res['ALL'] == 'WARNING: No item need to be verified.':
                    res.pop('ALL')
        else:
            if compare(value, test_group_d[key], 'eq'):
                '''
                res = 'PASS: col_name = %s, Value = %s, oid = %s, index = %s.' \
                                     % (key, value, oids_d[key], group_id)
                logging.info(res)
                '''            
            else:
                res = 'FAIL: col_name = %s, snmp_value = %s, test_data_value = %s, oid = %s, index = %s'  \
                            % (key, value, test_group_d[key], oids_d[key], group_id)
                logging.warning(res)

        if res:
            res_d[key] = res

    return res_d

def _update_vlan_tag(wlan_members_d):
    '''
    Update vlan tag based on overrride type.
    If type is untag, vlan_tag is 1, if type is nochange, vlan_tag is 0, else vlan_tag is equal specified value.
    '''
    for wlan_name, wlan_d in wlan_members_d.items():
        override_type = wlan_d['override_type']
        if compare(override_type, 'untag', 'eq'):
            wlan_d['vlan_tag'] = '1'
        elif compare(override_type, 'nochange', 'eq'):
            wlan_d['vlan_tag'] = '0'
        wlan_members_d[wlan_name] = wlan_d

    return wlan_members_d

def _verify_wlan_groups_dict(snmp_wlan_groups_d, cli_gui_wlan_groups_d, convert_func):
    '''
    Verify the wlan_groups dict from snmp with cli and gui values. Key is index, value is wlan_group detail dict.
    '''
    all_group_abbr_name_mapping = {}
    all_group_abbr_name_mapping.update(wlan_group_abbr_name_mapping)
    all_group_abbr_name_mapping.update(wlan_group_attr_abbr_name_mapping)
    oids_d = helper.get_item_oids(WLAN_CONFIG_MIB, all_group_abbr_name_mapping)

    res_wlan_groups_d = {}

    if len(snmp_wlan_groups_d) != len(cli_gui_wlan_groups_d):
        res_wlan_groups_d['ALL'] = 'The count of wlan_groups are not same of snmp, cli_gui. snmp = %s,cli_gui = %s'\
                       % (len(snmp_wlan_groups_d), len(cli_gui_wlan_groups_d))
    else:
        if len(snmp_wlan_groups_d) > 0:
            for index, wlan_group_info_d in snmp_wlan_groups_d.items():
                res_d = _verify_one_wlan_group_config(wlan_group_info_d, cli_gui_wlan_groups_d[index], convert_func, oids_d, index)
                if res_d:
                    res_wlan_groups_d[index] = res_d
        else:
            res_wlan_groups_d['ALL'] = 'No wlan group need to be verified.'

    return res_wlan_groups_d

def _verify_one_wlan_group_config(snmp_d, cli_gui_d, convert_func, oids_d = {}, index = None):
    '''
    Verify a wlan_group config: snmp, cli, and gui values.
    '''
    res_d = {}

    try:
        cli_gui_d = convert_func(cli_gui_d)

        snmp_keys = snmp_d.keys()
        cli_gui_keys = cli_gui_d.keys()
        snmp_keys.sort()
        cli_gui_keys.sort()

        # Verify keys in snmp, cli and gui values dict.
        if not (snmp_keys == cli_gui_keys):
            res = 'Keys from snmp, cli, gui dict are different. snmp keys: %s, cli_gui_keys: %s' % (snmp_keys, cli_gui_keys)
            res_d['ALL'] = res
            logging.warning(res)

        for key, value in snmp_d.items():
            try:
                res = ''
                if key == 'wlan_member':
                    #Verify wlan members dict. Key is name.
                    cli_gui_wlan_members_dict = cli_gui_d[key]
                    snmp_wlan_members_dict = value
                    res = helper.verify_items_dict(snmp_wlan_members_dict, cli_gui_wlan_members_dict, None, None, oids_d)
                    if res.has_key('ALL'):
                        if res['ALL'] == 'WARNING: No item need to be verified.':
                            res.pop('ALL')
                else:
                    result = False
                    is_pass, message = _item_verify_is_pass(snmp_d, key)
                    if is_pass:
                        result = True
                    else:
                        if compare(value, cli_gui_d[key], 'eq'):
                            result = True

                    #Output log information for each item.
                    if result:
                        '''
                        if message:
                            res = 'PASS: col_name = %s, value = %s, message = %s, oid = %s, index = %s.' \
                                             % (key, value, message, oids_d[key], index)
                        else:
                            res = 'PASS: col_name = %s, value = %s, oid = %s, index = %s.' \
                                                 % (key, value, oids_d[key], index)
                        logging.info(res)
                        '''
                    else:
                        res = 'FAIL: col_name = %s, snmp_value = %s, cli_gui_value = %s, oid = %s, index = %s'  \
                                    % (key, value, cli_gui_d[key], oids_d[key], index)
                        logging.warning(res)

            except Exception, e:
                res = 'Exception: col_name = %s, message = %s' % (key, e)
                logging.warning(res)

            if res:
                res_d[key] = res

    except Exception, e:
        res_d = {'Exception' : 'Message: %s' % (e,)}

    return res_d
