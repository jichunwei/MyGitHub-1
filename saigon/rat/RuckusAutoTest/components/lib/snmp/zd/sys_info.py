'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This file is used for system information getting/setting/verify methods.
'''

import logging
import copy

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.common.Ratutils import get_random_int, get_random_string
from RuckusAutoTest.common.utils import compare

SYSTEM_MIB = 'RUCKUS-ZD-SYSTEM-MIB'
SYSTEM_OBJECTS = 'ruckusZDSystemObjects'
# Default index of system object is 0.
SYSTEM_OBJECT_NAME_INDEX = 0
# Format of object name and index. <object name>.<index>
OBJNAME_INDEX_TEMP = '%s.%s'

#System object abbr and full name(snmp) mapping.
sys_obj_abbr_name_mapping = {'system_name':'ruckusZDSystemName',
                             'mac_addr':'ruckusZDSystemMacAddr',
                             'uptime':'ruckusZDSystemUptime',
                             'model':'ruckusZDSystemModel',
                             'licensed_aps':'ruckusZDSystemLicensedAPs',
                             'serial_number':'ruckusZDSystemSerialNumber',
                             'version':'ruckusZDSystemVersion',
                             'country_code':'ruckusZDSystemCountryCode',
                             'ntp_enable':'ruckusZDSystemTimeWithNTP',
                             'ntp_server':'ruckusZDSystemTimeNTPServer',
                             'syslog_enable':'ruckusZDSystemLogWithSysLog',
                             'syslog_server':'ruckusZDSystemSysLogServer',
                             'fm_enable':'ruckusZDSystemFlexMasterEnable',
                             'fm_server':'ruckusZDSystemFlexMasterServer',
                             'fm_interval':'ruckusZDSystemFlexMasterInterval',
                             'email_enable':'ruckusZDSystemEmailTriggerEnable',
                             'email_addr':'ruckusZDSystemEmailAddress',
                             'smtp_server':'ruckusZDSystemSMTPServerName',
                             'smtp_server_port':'ruckusZDSystemSMTPServerPort',
                             'smtp_auth_username':'ruckusZDSystemSMTPAuthUsername',
                             'smtp_auth_pwd':'ruckusZDSystemSMTPAuthPassword',
                             'smtp_encrypt_options':'ruckusZDSystemSMTPEncryptionOptions',}

#Object abbr and func[convert/format value] mapping.
col_get_func_mapping = {'mac_addr': helper.format_mac_address,
                        'uptime': helper.format_uptime,
                        'country_code': helper.get_country_name_by_code,
                        'ntp_enable': helper.convert_desc_to_enabled,
                        'syslog_enable': helper.convert_desc_to_enabled,
                        'fm_enable': helper.convert_desc_to_enabled,
                        'email_enable': helper.convert_desc_to_enabled,
                        'smtp_encrypt_options': helper.convert_encrypt_opts_desc_to_name,
                        }

#Read-write object and data type mapping.
rw_obj_type_mapping = {'system_name':'STRING', #1..32
                       'country_code':'STRING', #country code in the list, e.g. FR.
                       'ntp_enable':'INTEGER', #enable(1), disable(2)
                       'ntp_server':'STRING', #1..128
                       'syslog_enable':'INTEGER', #enable(1), disable(2)
                       'syslog_server':'STRING', #1..128
                       'fm_enable':'INTEGER', #enable(1), disable(2)
                       'fm_server':'STRING', #1..128
                       'fm_interval':'INTEGER', #1..60
                       'email_enable':'INTEGER', #enable(1), disable(2)
                       'email_addr':'STRING', #1..64
                       'smtp_server':'STRING', #1..128
                       'smtp_server_port':'INTEGER', #1..65535
                       'smtp_auth_username':'STRING', #1..128
                       'smtp_auth_pwd':'STRING', #1..128
                       'smtp_encrypt_options':'INTEGER', #none(1), tls(2), starttls(3), only 2,3 is valid.
                    }

rw_sys_obj_order_list = ['system_name','country_code','ntp_server', 'ntp_enable','syslog_server','syslog_enable',
                         'fm_server','fm_interval','fm_enable','smtp_server','smtp_server_port','email_addr',
                          'smtp_auth_username', 'smtp_auth_pwd', 'smtp_encrypt_options','email_enable',]

SNMP_TEMP = {'system_name':'',
             'country_code':'',
             'ntp_enable':'',
             'ntp_server':'',
             'syslog_enable':'',
             'syslog_server':'',
             'fm_enable':'',
             'fm_server':'',
             'fm_interval':'',
             'email_enable':'',
             'email_addr':'',
             'smtp_server':'',
             'smtp_server_port':'',
             'smtp_auth_username':'',
             'smtp_auth_pwd':'',
             'smtp_encrypt_options':'',
             }
#=============================================#
#             Access Methods            
#=============================================#
def get_sys_info_by_walking(snmp):
    '''
    Get system informatin by call snmpwalk.
    '''
    res_value = snmp.walk_by_name(SYSTEM_MIB, SYSTEM_OBJECTS)
    new_dict = helper.parsing_snmp_result(res_value, sys_obj_abbr_name_mapping, SYSTEM_OBJECT_NAME_INDEX, _convert_snmp_values_sys_objs)    
    
    return new_dict

def parsing_sys_info(snmp_original_d):
    '''
    Parsing the original result from snmp command. Convert key from oid(ruckusZDSystemName) to obj abbr(system_name).
    '''
    snmp_sys_info_d = helper.parsing_snmp_result(snmp_original_d, sys_obj_abbr_name_mapping, SYSTEM_OBJECT_NAME_INDEX, _convert_snmp_values_sys_objs)
    return snmp_sys_info_d
    
def get_sys_info(snmp, abbr_list = []):
    '''
    Get all the values under system objects except ruckusZDSystemSNMP and ruckusZDSystemIPTable. 
    [The objects in sys_obj_abbr_name_mapping.].
    ''' 
    new_dict = helper.get_item_detail_by_index(snmp, SYSTEM_MIB, sys_obj_abbr_name_mapping, 
                                        SYSTEM_OBJECT_NAME_INDEX, _convert_snmp_values_sys_objs, abbr_list)
    return new_dict

def get_sys_oids_by_name(snmp):
    '''
    Get system oids for all system objects.
    '''
    return helper.get_item_oids(SYSTEM_MIB, sys_obj_abbr_name_mapping)

def get_system_name(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'system_name')

def get_ip_addr(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ip_addr')

def get_mac_addr(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'mac_addr')

def get_uptime(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'uptime')

def get_model(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'model')

def get_licensed_aps(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'licensed_aps')

def get_serial_number(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'serial_number')

def get_version(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'version')

def get_country_code(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'country_code')

def get_ntp_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ntp_enable')

def get_ntp_server(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'ntp_server')

def get_syslog_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'syslog_enable')

def get_syslog_server(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'syslog_server')

def get_fm_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'fm_enable')

def get_fm_server(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'fm_server')

def get_fm_interval(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'fm_interval')

def get_email_enable(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'email_enable')

def get_email_addr(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'email_addr')

def get_smtp_server(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'smtp_server')

def get_smtp_server_port(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'smtp_server_port')

def get_smtp_auth_username(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'smtp_auth_username')

def get_smtp_auth_pwd(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'smtp_auth_pwd')

def get_smtp_encrypt_options(snmp):
    '''
    '''
    return _get_sys_obj_value(snmp, 'smtp_encrypt_options')

def verify_sys_info(dict_1, dict_2, max_diff = 5):
    '''
    max_diff: maximum difference between two uptime values, default is 5 minutes.
    '''
    return _verify_all_sys_info(dict_1, dict_2, max_diff)
    
def verify_sys_info_snmp_cli(snmp_d, cli_d):
    '''
    Verify sys information between snmp and cli values.
    '''
    cli_d = _convert_cli_to_snmp_temp(cli_d)
    res = _verify_all_sys_info(snmp_d, cli_d)
    return res

def verify_sys_info_snmp_gui(snmp_d, gui_d):
    '''
    Verify sys information between snmp and gui values.    
    '''
    gui_d = _convert_gui_to_snmp_temp(gui_d)
    res = _verify_all_sys_info(snmp_d, gui_d)
    return res    

def verify_sys_info_snmp_test_data(snmp_d, test_data_d):
    new_snmp_d = {}
    
    for key in test_data_d.keys():
        if snmp_d.has_key(key):
            new_snmp_d[key] = snmp_d[key]
    
    test_data_d = _convert_test_data_cfg(test_data_d)
    res = _verify_all_sys_info(new_snmp_d, test_data_d)    
    return res
    

def verify_system_name(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('system_name', snmp_value, gui_cli_value)
    return res

def verify_ip_addr(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('ip_addr', snmp_value, gui_cli_value)
    return res

def verify_mac_addr(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('mac_addr', snmp_value, gui_cli_value)
    return res

def verify_uptime(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('uptime', snmp_value, gui_cli_value)
    return res

def verify_model(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('model', snmp_value, gui_cli_value)
    return res

def verify_licensed_aps(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('licensed_aps', snmp_value, gui_cli_value)
    return res

def verify_serial_number(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('serial_number', snmp_value, gui_cli_value)
    return res

def verify_version(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('version', snmp_value, gui_cli_value)
    return res

def verify_country_code(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('country_code', snmp_value, gui_cli_value)
    return res

def verify_ntp_enable(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('ntp_enable', snmp_value, gui_cli_value)
    return res

def verify_ntp_server(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('ntp_server', snmp_value, gui_cli_value)
    return res

def verify_syslog_enable(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('syslog_enable', snmp_value, gui_cli_value)
    return res

def verify_syslog_server(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('syslog_server', snmp_value, gui_cli_value)
    return res

def verify_fm_enable(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('fm_enable', snmp_value, gui_cli_value)
    return res

def verify_fm_server(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('fm_server', snmp_value, gui_cli_value)
    return res

def verify_fm_interval(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('fm_interval', snmp_value, gui_cli_value)
    return res

def verify_email_enable(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('email_enable', snmp_value, gui_cli_value)
    return res

def verify_email_addr(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('email_addr', snmp_value, gui_cli_value)
    return res

def verify_smtp_server(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('smtp_server_port', snmp_value, gui_cli_value)
    return res

def verify_smtp_server_port(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('smtp_server_port', snmp_value, gui_cli_value)
    return res

def verify_smtp_auth_username(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('smtp_auth_username', snmp_value, gui_cli_value)
    return res

def verify_smtp_auth_pwd(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('smtp_auth_pwd', snmp_value, gui_cli_value)
    return res

def verify_smtp_encrypt_options(snmp_value, gui_cli_value):
    '''
    '''
    res = _verify_item_value('smtp_encrypt_options', snmp_value, gui_cli_value)
    return res

def update_sys_info(snmp, test_cfg, obj_list = []):
    '''
    Set value to object by snmp.
    '''
    if not obj_list:
        obj_list = test_cfg.keys()

    res_d = {}
    for name in rw_sys_obj_order_list:
        if name in obj_list and test_cfg.has_key(name):
            oid = sys_obj_abbr_name_mapping[name]
            index = SYSTEM_OBJECT_NAME_INDEX
            obj_type = rw_obj_type_mapping[name]
            value = test_cfg[name]
            res = helper.update_single_node_value(snmp, SYSTEM_MIB, oid, index, obj_type, value)
            
            if res:
                res_d.update({name:res})
        
    return res_d
            
def gen_test_data_sys_info():
    '''
    Genrate test value for readwrite object.
    '''
    test_data_cfg = {}    
    type = 'alpha'
    
    test_data_cfg['system_name'] = get_random_string(type,1,32)
    
    test_data_cfg['country_code'] = helper.get_random_country_code()
    test_data_cfg['ntp_enable'] = get_random_int(1, 2)
    if test_data_cfg['ntp_enable'] == 1:
        test_data_cfg['ntp_server'] = get_random_string(type,1,128)
    
    test_data_cfg['syslog_enable'] = get_random_int(1, 2)
    if test_data_cfg['syslog_enable'] == 1:
        test_data_cfg['syslog_server'] = helper.get_random_ip_addr()
    
    test_data_cfg['fm_enable'] = get_random_int(1, 2)
    if test_data_cfg['fm_enable'] == 1:
        test_data_cfg['fm_server'] = get_random_string(type,1,128)
        test_data_cfg['fm_interval'] = get_random_int(1, 60)
    
    test_data_cfg['email_enable'] = get_random_int(1, 2)
    if test_data_cfg['email_enable'] == 1:
        test_data_cfg['email_addr'] = helper.get_random_email_addr()
        test_data_cfg['smtp_server'] = get_random_string(type,1,64)
        test_data_cfg['smtp_server_port'] = get_random_int(1, 65535)
        test_data_cfg['smtp_auth_username'] = get_random_string(type,1,128)
        test_data_cfg['smtp_auth_pwd'] = get_random_string(type,1,128)
        test_data_cfg['smtp_encrypt_options'] = get_random_int(1, 3)
        
    return test_data_cfg   

def gen_test_data_sys_info_negative():
    '''
    Genrate negative input values for readwrite object.
    '''
    type = 'alpha'
    
    str_129 = get_random_string(type, 129)
    str_33 = get_random_string(type, 33)
    str_65 = get_random_string(type, 65)
    str_3 = get_random_string(type, 3)
    
    test_data_cfg = {}    
    test_data_cfg['system_name'] = str_33
    test_data_cfg['country_code'] = str_3
    test_data_cfg['ntp_enable'] = 3
    test_data_cfg['ntp_server'] = str_129
    test_data_cfg['syslog_enable'] = 3     
    test_data_cfg['syslog_server'] = str_129
    test_data_cfg['fm_enable'] = 3
    test_data_cfg['fm_enable'] = 3
    test_data_cfg['fm_interval'] = 61
    test_data_cfg['email_enable'] = 3    
    test_data_cfg['email_addr'] = str_65
    test_data_cfg['smtp_server'] = str_129
    test_data_cfg['smtp_server_port'] = 65536
    test_data_cfg['smtp_auth_username'] = str_129
    test_data_cfg['smtp_auth_pwd'] = str_129
    test_data_cfg['smtp_encrypt_options'] = 4
        
    return test_data_cfg   

#=============================================#
#             Private Methods            
#=============================================#
def _get_sys_obj_value(snmp, obj_abbr):
    '''
    Get value for specified snmp name (get object name by obj_abbr).
    ''' 
    obj_name = sys_obj_abbr_name_mapping[obj_abbr]
    item_value = helper.get_one_object_value_by_name(snmp, SYSTEM_MIB, obj_name, SYSTEM_OBJECT_NAME_INDEX)
    
    if col_get_func_mapping.has_key(obj_abbr):
        value = col_get_func_mapping[obj_abbr](item_value)
    else:
        value = item_value

    return value

def _verify_all_sys_info(snmp_d, item_d, max_diff = 5):
    '''
    Verify all system object information.
    ''' 
    res_d = {}
    oids_d = helper.get_item_oids(SYSTEM_MIB, sys_obj_abbr_name_mapping)

    try:
        snmp_keys = snmp_d.keys()
        item_keys = item_d.keys()        
        snmp_keys.sort()
        item_keys.sort() 
        #Modified by Liang Aihua for email behavior change on 2014-9-22 
        for key, value in item_d.items():
            try:
                res = ''
                if snmp_d.has_key(key):
                    is_pass, message = _item_verify_is_pass(snmp_d, key)
                    
                    if not is_pass:
                        if key == "smtp_auth_pwd":
                            continue
                        else:
                            res = _verify_item_value(key,value, item_d[key], oids_d[key], max_diff)                    
                else:
                    res = 'No value for key %s in dict.' % key     
        # Verify keys in snmp, cli and gui values dict.
        #if not (snmp_keys == item_keys):
        #    res = 'FAIL: Keys in snmp and dict are different. snmp keys: %s, dict_keys: %s' % (snmp_keys, item_keys)
        #    res_d['ERROR'] = res
            #logging.warning(res)
        
        #for key, value in snmp_d.items():
        #    try:
        #        res = ''
        #        if item_d.has_key(key):
        #            is_pass, message = _item_verify_is_pass(item_d, key)
        #            
        #            if not is_pass:
        #                res = _verify_item_value(key,value, item_d[key], oids_d[key], max_diff)                    
        #        else:
        #            res = 'No value for key %s in dict.' % key
    
            except Exception, e:
                res = 'Exception: col_name = %s, message = %s' % (key, e)
                #logging.warning(res)
            finally:
                if res: 
                    res_d[key] = res
                    
    except Exception, e:
        res_d = {'Exception':'message = %s' % e}
        #logging.warning(res_wlans_d)
                    
    return res_d
    
    
def _verify_item_value(obj_abbr, snmp_value, cli_gui_value, oid = None, max_diff = 5):
    '''
    Verify system objects: snmp value and cli or gui value.
    '''
    result = False
    addition_msg = ''

    try:
        res = ''
        if sys_obj_abbr_name_mapping.has_key(obj_abbr):
            obj_name = sys_obj_abbr_name_mapping[obj_abbr]
        else:
            obj_name = obj_abbr
        
        if not oid:
            oid_dict = helper.get_item_oids(SYSTEM_MIB, {obj_abbr: obj_name})
            oid = oid_dict[obj_abbr]   
        
        snmp_value = str(snmp_value)
        cli_gui_value = str(cli_gui_value)
        
        #Verify the values.
        if obj_abbr == 'uptime':            
            if helper.verify_sys_uptime(snmp_value, cli_gui_value, max_diff):
                result = True
                addition_msg = addition_msg + '5 mins different is acceptable.'
        elif obj_abbr == 'smtp_auth_pwd':
            if snmp_value:
                if len(snmp_value) == snmp_value.count('*') or len(cli_gui_value) == cli_gui_value.count('*'):                
                    result = True
            elif snmp_value == cli_gui_value:
                result = True  
        elif obj_abbr== 'country_code':
            #For country code, if only space in the value is different, ignore it.
            if compare(snmp_value, cli_gui_value, 'in'):
                result = True
            elif compare(cli_gui_value, snmp_value, 'in'):
                result = True
        else:
            if compare(snmp_value, cli_gui_value, 'eq'):
                result = True  
                    
        #Output log information for each item.
        if result:
            '''
            res = 'PASS: obj_name = %s,value = %s,' % (obj_name, cli_gui_value)
            if addition_msg:
                res =  res + 'message = %s,' % addition_msg
            res = res + 'OID = %s' % oid
            logging.info(res)
            '''            
        else:
            res = 'FAIL: obj_name = %s,snmp_value = %s,item_value= %s,' \
                         % (obj_name, snmp_value, cli_gui_value)
            if addition_msg:                
                res = res + 'message = %s,'  % addition_msg
            res = res + ('OID = %s'  % oid)            
            
            logging.warning(res)
    except Exception, e:
        res = 'Exception: obj_name = %s,message = %s' % (obj_name, e)
        logging.warning(res)
    
    return res

def _item_verify_is_pass(value_d, key):
    '''
    Weather we need to pass item values.
    Return:
        is_pass: true/false.
        message: description reason we pass the verification.     
    '''
    is_pass = False
    message = ''
            
    if key in ['fm_server','fm_interval'] and helper.is_disabled(value_d['fm_enable']):
        is_pass = True
        message = 'Not need to verify fm server if fm is disabled.'                
    elif key == 'ntp_server' and helper.is_disabled(value_d['ntp_enable']):
        is_pass = True
        message = 'Not need to verify ntp server if ntp is disabled.'
    elif key == 'syslog_server' and helper.is_disabled(value_d['syslog_enable']):
        is_pass = True
        message = 'Not need to verify syslog server if syslog is disabled.'
    elif key in ['email_addr', 'smtp_server','smtp_server_port','smtp_auth_username','smtp_auth_pwd','smtp_encrypt_options'] \
            and helper.is_disabled(value_d['email_enable']):
        is_pass = True
        message = 'Not need to verify email information if email is disabled.'
    elif key in ['fm_server','fm_interval','fm_enable']:
        if value_d[key] == 'N/A':
            is_pass = True
            message = 'Not need to verify the nodes based on the value is not returned.'
        
    return is_pass, message

def _convert_snmp_values_sys_objs(dict):
    '''
    Convert snmp values. 
    '''
    for key,value in dict.items():        
        if col_get_func_mapping.has_key(key):            
            dict[key] = col_get_func_mapping[key](value)
            
        if key == 'ntp_enable':
            #Cherry updated: For ntp, the value need to be converted. 
            #E.g. of result {'ruckusZDSystemTimeWithNTP.0': 'Wrong Type (should be INTEGER): Gauge32: 1'}
            if 'Wrong Type' in value: value = value.split(':')[-1]            
            if value.strip() == '1':
                dict[key] = 'Enabled'
            elif value.strip() == '2':
                dict[key] = 'Disabled'
            else:
                dict[key] = "Invalid value"
                
    return dict

def _convert_test_data_cfg (test_data_cfg):
    '''
    Convert some values in test data to same format as same format.
    '''    
    new_test_data_cfg = copy.deepcopy(test_data_cfg)

    for key, value in new_test_data_cfg.items():
        new_value = _convert_test_data_cfg_one_item(key, value)
        new_test_data_cfg[key] = new_value

    return new_test_data_cfg

def _convert_test_data_cfg_one_item(key, value):
    col_get_func_mapping = {'country_code': helper.get_country_name_by_code,
                            'ntp_enable': helper.convert_int_to_enabled,
                            'syslog_enable': helper.convert_int_to_enabled,
                            'fm_enable': helper.convert_int_to_enabled,
                            'email_enable': helper.convert_int_to_enabled,
                            'smtp_encrypt_options': helper.convert_encrypt_ops_int_to_name,
                            }
    
    if col_get_func_mapping.has_key(key):
        new_value = col_get_func_mapping[key](value)
    else:
        new_value = value        
            
    return new_value

def _convert_cli_to_snmp_temp(cli_sys_info):
    '''
    Convert cli system information to snmp temp.
    '''
    new_cli_sys_info = copy.deepcopy(SNMP_TEMP)
    
    new_cli_sys_info['system_name'] = cli_sys_info['Name']
    new_cli_sys_info['mac_addr'] = cli_sys_info['MAC Address']
    new_cli_sys_info['uptime'] = cli_sys_info['Uptime']
    new_cli_sys_info['model'] = cli_sys_info['Model']
    new_cli_sys_info['licensed_aps'] = cli_sys_info['Licensed APs']
    new_cli_sys_info['serial_number'] = cli_sys_info['Serial Number']
    new_cli_sys_info['version'] = cli_sys_info['Version']
    new_cli_sys_info['country_code'] = cli_sys_info['Country Code']['Code']
    if cli_sys_info.has_key('NTP'):
        if cli_sys_info['NTP'].has_key('Status'):
            new_cli_sys_info['ntp_enable'] = cli_sys_info['NTP']['Status']
        if cli_sys_info['NTP'].has_key('Address'):
            new_cli_sys_info['ntp_server'] = cli_sys_info['NTP']['Address']

    if cli_sys_info.has_key('Log'):
        if cli_sys_info['Log'].has_key('Status'):
            new_cli_sys_info['syslog_enable'] = cli_sys_info['Log']['Status']
        if cli_sys_info['Log'].has_key('Address'):
            new_cli_sys_info['syslog_server'] = cli_sys_info['Log']['Address']
    
    if cli_sys_info.has_key('FlexMaster'):
        fm_dict = cli_sys_info['FlexMaster']
        if fm_dict.has_key('Status'):
            new_cli_sys_info['fm_enable'] = fm_dict['Status']
        else:
            #Default is disabled.
            new_cli_sys_info['fm_enable'] = 'Disabled'
            
        new_cli_sys_info['fm_server'] = fm_dict['Address']
        new_cli_sys_info['fm_interval'] = fm_dict['Interval']

    if cli_sys_info.has_key('Alarm Status'):
        new_cli_sys_info['email_enable'] = cli_sys_info['Alarm Status']
    if cli_sys_info.has_key('Email Address'):
        new_cli_sys_info['email_addr'] = cli_sys_info['Email Address']
    if cli_sys_info.has_key('SMTP Server Name'):
        new_cli_sys_info['smtp_server'] = cli_sys_info['SMTP Server Name']
    if cli_sys_info.has_key('SMTP Server Port'):
        new_cli_sys_info['smtp_server_port'] = cli_sys_info['SMTP Server Port']
    if cli_sys_info.has_key('SMTP Authentication Username'):
        new_cli_sys_info['smtp_auth_username'] = cli_sys_info['SMTP Authentication Username']
    if cli_sys_info.has_key('SMTP Authentication Password'):
        new_cli_sys_info['smtp_auth_pwd'] = cli_sys_info['SMTP Authentication Password']
    if cli_sys_info.has_key('Encryption Options'):
        new_cli_sys_info['smtp_encrypt_options'] = cli_sys_info['Encryption Options']
        
    return new_cli_sys_info
        
def _convert_gui_to_snmp_temp(gui_sys_info):
    '''
    Convert gui system information to snmp temp.
    '''
    new_gui_sys_info = copy.deepcopy(SNMP_TEMP)
    
    new_gui_sys_info['system_name'] = gui_sys_info['System Name']    
    new_gui_sys_info['mac_addr'] = gui_sys_info['MAC Address']
    new_gui_sys_info['uptime'] = gui_sys_info['Uptime']
    new_gui_sys_info['model'] = gui_sys_info['Model']
    new_gui_sys_info['licensed_aps'] = gui_sys_info['Licensed APs']
    new_gui_sys_info['serial_number'] = gui_sys_info['Serial Number']
    new_gui_sys_info['version'] = gui_sys_info['Version']
    new_gui_sys_info['country_code'] = gui_sys_info['Country Code']['label']

    if(gui_sys_info['NTP'].has_key('Enabled')):
        new_gui_sys_info['ntp_enable'] = helper.convert_bool_to_enabled(gui_sys_info['NTP']['Enabled'])

    if gui_sys_info['NTP'].has_key('Address'):
        new_gui_sys_info['ntp_server'] = gui_sys_info['NTP']['Address']

    if gui_sys_info['Log'].has_key('enable_remote_syslog'):
        new_gui_sys_info['syslog_enable'] = helper.convert_bool_to_enabled(gui_sys_info['Log']['enable_remote_syslog'])
    if gui_sys_info['Log'].has_key('remote_syslog_ip'):
        new_gui_sys_info['syslog_server'] = gui_sys_info['Log']['remote_syslog_ip']

    if gui_sys_info['FM'].has_key('enabled'):
        new_gui_sys_info['fm_enable'] = helper.convert_bool_to_enabled(gui_sys_info['FM']['enabled'])
    if gui_sys_info['FM'].has_key('url'):
        new_gui_sys_info['fm_server'] = gui_sys_info['FM']['url']
    if gui_sys_info['FM'].has_key('interval'):
        new_gui_sys_info['fm_interval'] = gui_sys_info['FM']['interval']

    if gui_sys_info['Alarm'].has_key('enabled'):
        new_gui_sys_info['email_enable'] = helper.convert_bool_to_enabled(gui_sys_info['Alarm']['enabled'])
    if gui_sys_info['Alarm'].has_key('email_addr'):
        new_gui_sys_info['email_addr'] = gui_sys_info['Alarm']['email_addr']
    if gui_sys_info['Alarm'].has_key('smtp_server'):
        new_gui_sys_info['smtp_server'] = gui_sys_info['Alarm']['smtp_server']
    if gui_sys_info['Alarm'].has_key('server_port'):
        new_gui_sys_info['smtp_server_port'] = gui_sys_info['Alarm']['server_port']
    if gui_sys_info['Alarm'].has_key('username'):
        new_gui_sys_info['smtp_auth_username'] = gui_sys_info['Alarm']['username']
    if gui_sys_info['Alarm'].has_key('password'):
        new_gui_sys_info['smtp_auth_pwd'] = gui_sys_info['Alarm']['password']
    if gui_sys_info['Alarm'].has_key('encrypt'):
        new_gui_sys_info['smtp_encrypt_options'] = gui_sys_info['Alarm']['encrypt']
        
    return new_gui_sys_info         
