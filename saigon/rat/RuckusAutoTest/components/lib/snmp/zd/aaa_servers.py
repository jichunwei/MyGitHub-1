'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.14
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    The document is support snmp aaa servers information.
'''

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.Ratutils import get_random_string
from RuckusAutoTest.common.utils import compare

import logging
import copy
import time

AAA_SERVER_MIB = 'RUCKUS-ZD-AAA-MIB'
AAA_CONFIG_OBJECTS = 'ruckusZDAAAObjects' #ruckusZDAAAObjects(1).ruckusZDAAAConfig(1)

server_abbr_name_mapping = {'server_name':'ruckusZDAAAConfigName',
                     'type':'ruckusZDAAAConfigServiceType',
                     'row_status':'ruckusZDAAAConfigRowStatus',
                     'server_addr':'ruckusZDAAARadiusPrimarySvrIpAddress',
                     'server_port':'ruckusZDAAARadiusPrimarySvrPort',
                     'radius_secret':'ruckusZDAAARadiusPrimarySvrPasswd',
                     'backup':'ruckusZDAAARadiusBackupControl',
                     'backup_server_addr':'ruckusZDAAARadiusSecondarySvrIpAddress',
                     'backup_server_port':'ruckusZDAAARadiusSecondarySvrPort',
                     'backup_radius_secret':'ruckusZDAAARadiusSecondarySvrPasswd',
                     'request_timeout':'ruckusZDAAARadiusFailoverTimeout',
                     'retry_count':'ruckusZDAAARadiusFailoverRetry',
                     'retry_interval':'ruckusZDAAARadiusFailoverReconnectPrimary',
                    }

SNMP_CONF = {'server_name':'-',
             'type':'-',
             'server_addr':'-',
             'server_port':'-',
             'radius_secret':'-',
             'backup':'-',
             'backup_server_addr':'-',
             'backup_server_port':'-',
             'backup_radius_secret':'-',
             'request_timeout':'-',
             'retry_count':'-',
             'retry_interval':'-',
             }


rw_obj_type_mapping = {'server_name':'STRING', #1..63
                       'type':'INTEGER', #active-directory(1), ldap-directory(2), aaa-authentication(3), accounting(4)
                       'row_status':'INTEGER', #only for create, value is 4.                       
                       'server_addr':'STRING', #2..40
                       'server_port':'INTEGER', #
                       'radius_secret':'STRING', #1..32
                       'backup':'INTEGER', #enable(1), disable(2)
                       'backup_server_addr':'STRING', #2..40
                       'backup_server_port':'INTEGER', #
                       'backup_radius_secret':'STRING', #1..32
                       'request_timeout':'INTEGER', #3..30
                       'retry_count':'INTEGER', #2..10
                       'retry_interval':'INTEGER', #2..10
                       }
col_get_func_mapping = {'type': helper.convert_aaa_server_service_type,
                        'backup': helper.convert_desc_to_enabled,
                        }

rw_aaa_config_keys_order_list = ['server_name', 'type', 'row_status']
rw_aaa_server_keys_order_list = ['server_addr', 'server_port', 'radius_secret', 
                                 'backup','backup_server_addr', 'backup_server_port', 'backup_radius_secret',
                                 'request_timeout', 'retry_count', 'retry_interval', ]

OBJNAME_INDEX_TEMP = '%s.%s'
#=============================================#
#             Access Methods            
#=============================================#

def get_all_servers_id_name_mapping(snmp):
    '''
    Return all aaa servers index and name mapping, 
    include id is 0,1,2[which can't get from snmp].
    '''
    index_name_mapping = {}
    
    index_name_mapping.update({'0': 'Disabled'})
    index_name_mapping.update({'1': 'Local Database'})
    index_name_mapping.update({'2': 'Guest Accounts'})
    
    index_name_mapping.update(get_server_index_value_mapping(snmp))
    
    return index_name_mapping;

def get_server_id_by_name(snmp, server_name):
    '''
    Get server id/index by server name.
    '''
    server_id_name_mapping = get_server_index_value_mapping(snmp)
    server_id = helper.get_dict_key_by_value(server_id_name_mapping, server_name)
    
    return server_id

def get_auth_server_id(snmp):
    '''
    Get auth server id, if does not exist, create one.
    '''
    auth_server_id = str(get_server_index_by_type(snmp, 'aaa-authentication'))
    
    if not auth_server_id:
        res, auth_server_id = create_specified_type_server(snmp, 'aaa-authentication')
        if not res:
            auth_server_id = 0
        
    return auth_server_id

def get_acct_server_id(snmp):
    '''
    Get accounting server id, if does not exist, create one.
    '''
    acct_server_id = str(get_server_index_by_type(snmp, 'aaa-accounting'))
    
    if not acct_server_id:
        res, acct_server_id = create_specified_type_server(snmp, 'aaa-accounting')
        if not res:
            acct_server_id = 0
    
    return acct_server_id

def get_servers_by_key_value(snmp, key_obj_name = 'server_name', key_value = '*'):
    '''
    Get server information by specified column, and the value, default is name.
    If key_value is *, will get all servers.
    '''
    return helper.get_items_by_key_value(snmp, AAA_SERVER_MIB, server_abbr_name_mapping, key_obj_name, key_value, _convert_server_snmp_values)

def parsing_server_info(snmp_original_d):
    '''
    Parsing the result and get servers information. Key is server id, Value is server detail information.
    '''
    server_id_name_mapping = {}
    
    for key,value in snmp_original_d.items():
        oid_list = key.split('.')
        obj_server_name = server_abbr_name_mapping['server_name']
        if compare(oid_list[0],obj_server_name,'eq'):
            server_id_name_mapping[oid_list[1]] = value
    
    servers_d = {}
    if server_id_name_mapping:
        for server_id,name in server_id_name_mapping.items():        
            server_info = helper.parsing_snmp_result(snmp_original_d, server_abbr_name_mapping, server_id, _convert_server_snmp_values)
            servers_d[name] = server_info
    
    return servers_d

def get_server_by_name(snmp, server_name_list):
    '''
    Get server information by server name, return the dict with the key is server_name.
    if server_name_list is null, get all servers.
    '''
    server_id_name_mapping = get_server_index_value_mapping(snmp)
    
    servers_dict = {}
    
    if not server_name_list:
        for index, name in server_id_name_mapping.items():
            server_d = get_server_detail_by_index(snmp, index)
            servers_dict[name] = server_d
    else:
        for server_name in server_name_list:
            index = helper.get_dict_key_by_value(server_id_name_mapping, server_name)
            server_d = get_server_detail_by_index(snmp, index)
            
            servers_dict[server_name] = server_d
        
    return servers_dict
    
def get_server_index_value_mapping(snmp, key_obj_name = 'server_name'):
    '''
    Get all server information, index and value for specified field(obj_abbr).
    '''
    oid = server_abbr_name_mapping[key_obj_name]
    return helper.get_index_value_mapping(snmp, AAA_SERVER_MIB, oid)

def get_server_detail_by_index(snmp, index, keys_list = []):
    '''
    Get server config information based on index. 
    '''
    return helper.get_item_detail_by_index(snmp, AAA_SERVER_MIB, server_abbr_name_mapping, index, _convert_server_snmp_values, keys_list)

def verify_servers_dict_snmp_cli(snmp_servers_d, cli_servers_d):
    '''
    Verify the servers dict from snmp with cli values. Key is index, value is server detail dict.
    '''  
    oids_d = helper.get_item_oids(AAA_SERVER_MIB, server_abbr_name_mapping)    
    res_d = helper.verify_items_dict(snmp_servers_d, cli_servers_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_servers_dict_snmp_gui(snmp_servers_d, gui_servers_d):
    '''
    Verify the servers dict from snmp with gui values. Key is index, value is server detail dict.
    '''  
    oids_d = helper.get_item_oids(AAA_SERVER_MIB, server_abbr_name_mapping)
    res_d = helper.verify_items_dict(snmp_servers_d, gui_servers_d, _convert_gui_to_snmp_temp, _item_verify_is_pass, oids_d)
    
    return res_d

def verify_one_server_snmp_cli(snmp_d, cli_d, oids_d = {}, index = None):
    '''
    Verify a server config: snmp and cli values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(AAA_SERVER_MIB, server_abbr_name_mapping)        
    res_d = helper.verify_one_item_config(snmp_d, cli_d, _convert_cli_to_snmp_temp, _item_verify_is_pass, oids_d, index)

    return res_d

def verify_one_server_snmp_gui(snmp_d, gui_d, oids_d = {}, index = None):
    '''
    Verify a server config: snmp and gui values.
    '''
    if not oids_d:
        oids_d = helper.get_item_oids(AAA_SERVER_MIB, server_abbr_name_mapping)
    res_d = helper.verify_one_item_config(snmp_d, gui_d, _convert_gui_to_snmp_temp, _item_verify_is_pass, oids_d, index)

    return res_d

def verify_servers_test_data_snmp(snmp_servers_d, test_data_servers_d):
    '''
    Verify server information: pre-config data and values from snmp. 
    '''
    oids_d = helper.get_item_oids(AAA_SERVER_MIB, server_abbr_name_mapping)
    res_servers_d = helper.verify_items_dict(snmp_servers_d, test_data_servers_d, _convert_server_snmp_values, _item_verify_is_pass, oids_d)
    
    return res_servers_d

def verify_update_server(snmp, server_id, update_cfg_list):
    '''
    Update the server information, and then verify the value is updated.
    '''    
    oids_d = helper.get_item_oids(AAA_SERVER_MIB, server_abbr_name_mapping)
    
    index = 0
    res_servers_d = {}
    for server_cfg in update_cfg_list:
        index +=1        
        update_server(snmp, server_cfg, server_id)
        keys_list = server_cfg.keys()
        
        if server_cfg.has_key('type'):
            time.sleep(60)
            
        snmp_server_d = get_server_detail_by_index(snmp, server_id, keys_list)
        res_d = helper.verify_one_item_config(snmp_server_d, server_cfg, _convert_server_snmp_values, None, oids_d, index)
        
        if res_d:
            res_servers_d[index] = {'Config': server_cfg, 'Result': res_d}
        
    return res_servers_d

def update_server(snmp, server_cfg, index):
    '''
    Update aaa server informat based on specified config (server_cfg).
    '''
    new_server_cfg = {'index': index}
    new_server_cfg.update(server_cfg)    
    _update_server_config(snmp, new_server_cfg, 2)  

def remove_all_servers(snmp):
    '''
    Remove all aaa servers.
    '''    
    server_index_list = get_server_index_value_mapping(snmp).keys()
    if len(server_index_list) > 0:
        delete_servers_by_index(snmp, server_index_list)
        
def verify_delete_servers(snmp, server_name_list):
    '''
    Verify delete aaa servers based on server name list.
    '''
    server_id_name_mapping = get_server_index_value_mapping(snmp)
    
    err_server_name_list = []

    for server_name in server_name_list:
        server_id = helper.get_dict_key_by_value(server_id_name_mapping, server_name)
        
        if not server_id:
            raise Exception("Can't find index for server: %s." % server_name)
        
        res = delete_one_server_by_index(snmp, server_id)
        
        time.sleep(15)

        if not _check_server_index_exist(snmp, server_id):            
            logging.info('The server has been deleted successfully. Index = %s' % server_id)
        else:
            err_server_name_list.append(server_name)
            logging.info('The server is not deleted successfully. Index = %s' % server_id)
            
    return err_server_name_list

def delete_servers_by_index(snmp, server_index_list):
    '''
    Delete the servers by index exist in server_index_list.
    '''
    error_index_list = []
    
    for index in server_index_list:
        res = delete_one_server_by_index(snmp, index)
                
        time.sleep(10)

        if not _check_server_index_exist(snmp, index):            
            logging.info('The server has been deleted successfully. Index = %s' % index)
        else:
            error_index_list.append(index)
            logging.info('The server is not deleted successfully. Index = %s' % index)

    return error_index_list

def delete_one_server_by_index(snmp, server_id):
    '''
    Delete one server by specified server id/index.
    '''
    server_cfg = {'index': server_id}
    return _update_server_config(snmp, server_cfg, 3)

def get_server_index_by_type(snmp, service_type):
    '''
    Get server index by specified type, if does not exist, then create one.
    '''
    index_type_mapping = get_server_index_value_mapping(snmp, 'type')
    r_index = ''

    if index_type_mapping:
        for index, type_value in index_type_mapping.items():
            if type_value.find(service_type) >= 0:
                r_index = index
                break
            
    return r_index


def create_aaa_servers(snmp, server_cfg_list):
    '''
    Create all servers in server_cfg_list.
    Return:
        err_server_name_list is [] if all servers created successfully.
        servers name list which are not created if some servers are not created successfully.
    '''
    err_server_name_list = []
    
    if not server_cfg_list:        
        server_cfg_list = gen_server_test_cfg()

    for server_cfg in server_cfg_list:
        server_name = server_cfg['server_name']
        
        #Cherry updated: If can't create server then try 10 times.
        index = 0
        for i in range(0,10):        
            res, index = create_one_server(snmp, server_cfg)            
            if index != 0: break
        if index == 0:        
            err_server_name_list.append(server_name)        

    return err_server_name_list


def create_servers(snmp, server_cfg_list):
    '''
    Create all servers in server_cfg_list.
    Return:
        The dict of server details with key = index.
        
    This will be deleted later. It is used by tea now.
    '''
    server_list_d = {}
    
    if not server_cfg_list:
        server_cfg_list = gen_server_test_cfg()

    for server_cfg in server_cfg_list:
        res, index = create_one_server(snmp, server_cfg)
        if res:
            server_list_d.update({str(index): server_cfg})        

    return res, server_list_d

def create_one_server(snmp, server_cfg):
    '''
    Create a aaa server based on specified config. 
    Re-construct to a parameter list based on config,
    then call snmp method to create server.
    '''
    index = _gen_new_index(snmp)
    
    new_server_cfg = {'index': index}
    new_server_cfg.update(server_cfg) 
    
    _update_server_config(snmp, new_server_cfg, 1)

    time.sleep(10)
    
    # Check the server is created successfully.
    index_server_mapping = get_server_index_value_mapping(snmp)

    if index_server_mapping.has_key(str(index)):
        result = True
        logging.info('Create AAA server successfully. Index=%s' % index)
    else:
        logging.warning('The aaa server is not created successfully.')
        result = False
        index = 0

    return result, index

def create_specified_type_server(snmp, service_type):
    '''
    Create specified type server and return index.
    '''
    test_cfg_list = gen_server_test_cfg()
    new_server_cfg = {}

    for server_cfg in test_cfg_list:
        if server_cfg['type'].find(service_type) >= 0:
            new_server_cfg = server_cfg

    result, index = create_one_server(snmp, new_server_cfg)
    
    return result,index

def gen_server_test_cfg():
    servers_list = [ dict(server_name = 'Radius-Auth-Server', type = 'aaa-authentication(3)',
                          server_addr = '192.168.30.252', server_port = '1812', radius_secret = '123456789', 
                          backup = 'disable(2)', backup_server_addr = '192.168.30.252', 
                          backup_server_port = '0', backup_radius_secret = '123456789', 
                          request_timeout = '3', retry_count = '2', retry_interval = '5',),
                     dict(server_name = 'Radius-Account-Server', type = 'aaa-accounting(4)',
                          server_addr = '192.168.30.252', server_port = '1813', radius_secret = '123456789', 
                          backup = 'enable(1)', backup_server_addr = '192.168.30.253', 
                          backup_server_port = '1813', backup_radius_secret = '123456789', 
                          request_timeout = '3', retry_count = '2', retry_interval = '5',)
                   ]

    return servers_list

def gen_server_update_test_cfg():
    create_servers_list = [ dict(server_name = 'Radius-Auth-Server', type = 'aaa-authentication(3)',
                                 server_addr = '192.168.30.252', server_port = '1812', radius_secret = '123456789', 
                                 backup = 'disable(2)', backup_server_addr = '192.168.30.252', 
                                 backup_server_port = '0', backup_radius_secret = '123456789',
                                 request_timeout = '3', retry_count = '2', retry_interval = '5',),
                          ]
    update_server_cfg_list = [dict(server_addr = '192.168.0.10', server_port = '1812', radius_secret = '8756423975'),
                              dict(backup = 'enable(1)', backup_server_addr = '192.168.30.252', backup_server_port = '1112',
                                   backup_radius_secret = '987654321', request_timeout = '10', retry_count = '10', retry_interval = '10',),
                              dict(request_timeout = '6', retry_count = '7', retry_interval = '8'),
                              dict(backup = 'disable(2)'),
                              dict(type = 'aaa-accounting(4)'),
                              dict(server_addr = '192.168.10.33', server_port = '1813', radius_secret = '123466890'),
                              dict(backup = 'enable(1)', backup_server_addr = '192.168.22.253', backup_server_port = '1034',
                                   backup_radius_secret = '987654321', request_timeout = '4', retry_count = '6', retry_interval = '10',),
                              dict(request_timeout = '5', retry_count = '5', retry_interval = '5'),
                              dict(backup = 'disable(2)')
                              ]

    return create_servers_list, update_server_cfg_list

def gen_server_test_cfg_negative():
    '''
    Generate negative input for server config.
    '''
    type = 'alpha'
    str_64 = get_random_string(type,64)    
    str_41 = get_random_string(type,41)
    str_33 = get_random_string(type,33)
    
    server_cfg = {}
    
    server_cfg['server_name'] = str_64  #1..63
    server_cfg['type'] = '5' #active-directory(1), ldap-directory(2), aaa-authentication(3), accounting(4)
    server_cfg['server_addr'] = str_41  #2..40
    #server_cfg['server_port'] = '65536'  #for auth    : the value should be : 1812; for account : the value should be : 1813.
    server_cfg['radius_secret'] = str_33 #1..32
    server_cfg['backup'] = '3' #enable(1), disable(2)
    server_cfg['backup_server_addr'] = str_41 #2..40
    #server_cfg['backup_server_port'] = '65536'
    server_cfg['backup_radius_secret'] = str_33 #1..32
    server_cfg['request_timeout'] = '21'  #2..20  #@ZJ 20141103 fix error  {(2..20) 
    server_cfg['retry_count'] = '11' #2..10  ##@ZJ "Max Number of Retries"
    server_cfg['retry_interval'] = '86401' ##@ZJ 20141103ZF-10639 fix error  {(1..86400)} "Reconnect Primary"
    
    return server_cfg

def update_server_cfg_one_by_one(snmp, index, test_cfg):
    '''
    Update server config items, one by one.
    '''
    res_d = {}
    for obj_name, value in test_cfg.items():
        oid = server_abbr_name_mapping[obj_name]
        obj_type = rw_obj_type_mapping[obj_name]
        res = helper.update_single_node_value(snmp, AAA_SERVER_MIB, oid, index, obj_type, value)
        
        if res:
            res_d.update({obj_name : res})
        
    return res_d

#=============================================#
#             Private Methods            
#=============================================#
def _gen_new_index(snmp):
    '''
    Generate new index for create server. 
    Return the index does not exist in current server list, range is 3 to 32.    
    '''
    start_index = 3
    max_index = 32
    oid = server_abbr_name_mapping['server_name']
    new_index = helper.gen_new_index(snmp, AAA_SERVER_MIB, oid, start_index, max_index) 
    return new_index

def _convert_server_snmp_values(server_d):
    '''
    Convert server snmp values.
    '''
    for key, value in server_d.items():
        new_value = value
        if key in col_get_func_mapping.keys():
            convert_func = col_get_func_mapping[key]
            new_value = convert_func(value)
        
        server_d[key] = new_value
        
    return server_d

def _convert_cli_to_snmp_temp(cli_server_d):
    '''
    Convert cli server dict to same snmp dict structure. Not support ad and ldap now.
    '''
    new_cli_server_d = copy.deepcopy(SNMP_CONF)

    new_cli_server_d['server_name'] = cli_server_d['Name']
    
    service_type = cli_server_d['Type']
    type_cli_snmp_mapping = {'RADIUS Accounting server': 'radius-acct',
                             'RADIUS server':'radius-auth',
                             #'':'ad',
                             #'':'ldap'
                            }
    
    new_cli_server_d['type'] = type_cli_snmp_mapping[service_type]
    
    if new_cli_server_d['type'] == 'radius-acct':
        primary_key = 'Primary RADIUS Accounting'
        second_key = 'Secondary RADIUS Accounting'
    elif new_cli_server_d['type'] == 'radius-auth':
        primary_key = 'Primary RADIUS'
        second_key = 'Secondary RADIUS'
    else:
        #TODO:
        primary_key = ''
        second_key = ''
        
    if cli_server_d.has_key(primary_key):
        new_cli_server_d['server_addr'] = cli_server_d[primary_key]['IP Address']
        new_cli_server_d['server_port'] = cli_server_d[primary_key]['Port']
        new_cli_server_d['radius_secret'] = cli_server_d[primary_key]['Secret']
    
    if cli_server_d.has_key(second_key):
        new_cli_server_d['backup'] = cli_server_d[second_key]['Status']
        if not helper.is_disabled(new_cli_server_d['backup']):
            new_cli_server_d['backup_server_addr'] = cli_server_d[second_key]['IP Address']
            new_cli_server_d['backup_server_port'] = cli_server_d[second_key]['Port']
            new_cli_server_d['backup_radius_secret'] = cli_server_d[second_key]['Secret']
            
            failover_key = 'Retry Policy'
            if cli_server_d.has_key(failover_key):
                failover_dict = cli_server_d[failover_key]
                if failover_dict.has_key('Request Timeout'):
                    new_cli_server_d['request_timeout'] = failover_dict['Request Timeout'].split(' ')[0]
                if failover_dict.has_key('Max. Number of Retries'):
                    new_cli_server_d['retry_count'] = failover_dict['Max. Number of Retries'].split(' ')[0]
                if failover_dict.has_key('Reconnect Primary'):
                    new_cli_server_d['retry_interval'] = failover_dict['Reconnect Primary'].split(' ')[0]
    else:
        new_cli_server_d['backup'] = 'Disabled'

    return new_cli_server_d

def _convert_gui_to_snmp_temp(gui_server_d):
    '''
    Convert gui server dict to same snmp dict structure.
    '''
    new_gui_server_d = copy.deepcopy(SNMP_CONF)
    new_gui_server_d.update(gui_server_d)
    
    backup_key = 'backup'
    
    if new_gui_server_d.has_key(backup_key):
        value = new_gui_server_d[backup_key]
        new_value = helper.convert_bool_to_enabled(value)
        new_gui_server_d[backup_key] = new_value
        
    return new_gui_server_d

def _item_verify_is_pass(value_d, key):
    '''
    Weather we need to pass item values.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''

    if key in rw_aaa_server_keys_order_list:
        if value_d['type'] in ['ad','ldap']:
            message = 'Do not need to verify radius config if type is active directory and ldap.'
            is_pass = True
        elif key in ['backup_server_addr', 'backup_server_port', 'backup_radius_secret', 'request_timeout', 'retry_count', 'retry_interval']:
            if helper.is_disabled(value_d['backup']):
                message = 'Do not need to verify secondary radius and failover setting when backup is disabled.'
                is_pass = True

    return is_pass, message

def _check_server_index_exist(snmp, index):
    '''
    Check wether the server with specified index exist. 
    Return true if exist, false if does not exist.
    '''
    # Check the server is created successfully.
    index_server_name_mapping = get_server_index_value_mapping(snmp)
    result = False
    if index_server_name_mapping and index_server_name_mapping.has_key(str(index)):
            result = True

    return result

def _update_server_config(snmp, server_cfg, flag):
    '''
    Update aaa server: create an aaa server, update some settings, delete the server.
    Input:
        flag: 1 - create
        server_cfg: include indexs and setting's value dict.
        {index:3, desc='this is test.'...}
    '''
    index = server_cfg['index']
    
    if flag == 3:
        helper.update_objects_config(snmp, AAA_SERVER_MIB, server_abbr_name_mapping, 
                              rw_obj_type_mapping, rw_aaa_config_keys_order_list, server_cfg, 3)
    else:
        #Add/update server configs.
        helper.update_objects_config(snmp, AAA_SERVER_MIB, server_abbr_name_mapping, 
                              rw_obj_type_mapping, rw_aaa_config_keys_order_list, server_cfg, flag)
        
        time.sleep(10)
        
        # Check the server is created successfully, add/update ruckusZDAAAConfigTable.
        index_server_mapping = get_server_index_value_mapping(snmp)

        if index_server_mapping.has_key(str(index)):            
            #Update config in ruckusZDAAASvrTable
            helper.update_objects_config(snmp, AAA_SERVER_MIB, server_abbr_name_mapping, 
                                  rw_obj_type_mapping, rw_aaa_server_keys_order_list, server_cfg, flag)