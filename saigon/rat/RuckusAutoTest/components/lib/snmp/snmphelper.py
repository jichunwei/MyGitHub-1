'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary: 
    The document is support some common methods for snmp.
'''

import re,copy
import logging
from RuckusAutoTest.common.Ratutils import get_random_int, get_random_string
from RuckusAutoTest.common.utils import compare, compare_dict_key_value
from RuckusAutoTest.components.SNMP import SNMP as snmp_com
from RuckusAutoTest.components.SNMPTrap import SNMPTrap as trap


country_code_name_mapping = {'AE':'United Arab Emirates',
                             'AR':'Argentina',
                             'AT':'Austria',
                             'AU':'Australia',
                             'BE':'Belgium',
                             'BG':'Bulgaria',
                             'BR':'Brazil',
                             'CA':'Canada',
                             'CH':'Switzerland',
                             'CL':'Chile',
                             'CN':'China',
                             'CO':'Colombia',
                             'CY':'Cyprus',
                             'CZ':'Czech Republic',
                             'DE':'Germany',
                             'DK':'Denmark',
                             'EC':'Ecuador',
                             'EE':'Estonia',
                             'EG':'Egypt',
                             'ES':'Spain',
                             'FI':'Finland',
                             'FR':'France',
                             'GB':'United Kingdom',
                             'GR':'Greece',
                             'HK':'Hong Kong',
                             'HU':'Hungary',
                             'ID':'Indonesia',
                             'IE':'Ireland',
                             'IL':'Israel',
                             'IN':'India',
                             'IS':'Iceland',
                             'IT':'Italy',
                             'JP':'Japan',
                             'KR':'Korea, Republic of',
                             'LK':'Sri Lanka',
                             'LT':'Lithuania',
                             'LU':'Luxembourg',
                             'LV':'Latvia',
                             'MX':'Mexico',
                             'MY':'Malaysia',
                             'NL':'Netherlands',
                             'NO':'Norway',
                             'NZ':'New Zealand',
                             'PH':'Philippines',
                             'PK':'Pakistan',
                             'PL':'Poland',
                             'PT':'Portugal',
                             'R1':'Reserved_1',
                             'RO':'Romania',
                             'RU':'Russian Federation',
                             'SA':'Saudi Arabia',
                             'SE':'Sweden',
                             'SG':'Singapore',
                             'SI':'Slovenia',
                             'SK':'Slovakia (Slovak Republic)',
                             'TH':'Thailand',
                             'TR':'Turkey',
                             'TW':'Taiwan',
                             'US':'United States',
                             'UY':'Uruguay',
                             'VN':'Viet Nam',
                             'ZA':'South Africa',
                             }

wlan_service_type_mapping = {'standardUsage': 'Standard Usage',
                             'guestAccess': 'Guest Access',
                             'hotSpotService': 'Hotspot Service(WISPr)',
                            }

aaa_server_type_mapping = {'active-directory': 'ad',
                           'ldap-directory': 'ldap',
                           'aaa-authentication': 'radius-auth',
                           'aaa-accounting': 'radius-acct',
                           }

ENABLE = 'ENABLE'
ENABLED = 'ENABLED'
DISABLE = 'DISABLE'
DISABLED = 'DISABLED'

enable_value_mapping = {ENABLE : ENABLED,
                        DISABLE : DISABLED}

OBJNAME_INDEX_TEMP = "%s.%s"
#=============================================#
#             Access Methods            
#=============================================#
def create_snmp(snmp_cfg):
    '''
    Create a snmp object based on specified snmp_cfg.
    '''
    default_cfg = {'ip_addr': '192.168.0.2',
                   'version': 3,
                   'sec_name': 'ruckus-read',                   
                   'auth_protocol': 'MD5',
                   'auth_passphrase': '12345678',
                   'priv_protocol': 'DES',
                   'priv_passphrase': '12345678',
                   'timeout': 20,
                   'retries': 3,
                   }
    
    agent_cfg = {}
    agent_cfg.update(default_cfg)
    agent_cfg.update(snmp_cfg)
    
    return snmp_com(agent_cfg)

def create_snmp_trap(trap_cfg):
    '''
    Create SNMPTrap object.
    '''
    trap_obj = trap(trap_cfg)
    
    return trap_obj
    
def walking_mib(snmp, mib_name, object_name):
    '''
    Walking the object under mib.
    '''
    res_value = snmp.walk_by_name(mib_name, object_name)
    return res_value

def get_dict_key_by_value(dict, value):
    '''
    Get key from a dict by value.
    '''
    ret_key = ''
    if dict: 
        for key,d_value in dict.items():
            if compare(d_value, value, 'eq'):
                ret_key = key
                break
    return ret_key

def get_update_snmp_cfg(agent_cfg, user_type = 'rw'):
    '''
    Get snmp config with the updated items based on agent_cfg, will get read only(ro)
    or read write settings based on type.    
    Input agent_cfg format:
    agent_config = {'ro_community': 'public',
                    'rw_community': 'private',
                    'ro_sec_name': 'ruckus-read',
                    'ro_auth_protocol': 'MD5',
                    'ro_auth_passphrase': '12345678',
                    'ro_priv_protocol': 'DES',
                    'ro_priv_passphrase': '12345678',
                    'rw_sec_name': 'ruckus-write',
                    'rw_auth_protocol': 'MD5',
                    'rw_auth_passphrase': '12345678',
                    'rw_priv_protocol': 'DES',
                    'rw_priv_passphrase': '12345678',
                    'version': '2'}
    Output: {'community': 'private',
             'sec_name': 'ruckus-write',             
             'auth_protocol': 'MD5',
             'auth_passphrase': '12345678',
             'priv_protocol': 'DES',
             'priv_passphrase': '12345678',
             'version':'2'}        
    ''' 
    new_snmp_cfg = {}
    new_snmp_cfg['version'] = agent_cfg['version']
    
    obj_list = ['community', 'sec_name','auth_protocol','auth_passphrase','priv_protocol','priv_passphrase']
    
    list_len = len(obj_list)
    for i in range(0, list_len):
        obj_list[i] = '%s_%s' % (user_type, obj_list[i])
    
    for key in agent_cfg.keys():
        if key in obj_list:
            new_key = key[3:]
            new_snmp_cfg[new_key] = agent_cfg[key]
    
    return new_snmp_cfg

def is_disabled(str):
    '''
    Check the string is disabled.     
    '''
    if compare(str,DISABLED, 'eq'):
        return True 
    else:
        return False

def is_enabled(str):
    '''
    Check the string is disabled.     
    '''
    if compare(str,ENABLED, 'eq'):
        return True 
    else:
        return False

def convert_link_rate(value):
    '''
    Convert link rate.
    Input:
        disable, 20.00mbps
    Output:
        disabled, 20.00mbps
    '''
    new_value = value
    value = get_name_from_desc(value)
    if compare(value, DISABLE, 'eq'):
        new_value = DISABLED
    
    return new_value

def convert_ip_addr_mode(value):
    '''
    Convert ip addr mode. [zd-ap info]
    '''
    mapping = {'admin-by-dhcp': 'dhcp',
               'admin-by-zd': 'manual',
               'admin-by-ap': 'as_is',
               'admin-by-autoconfig': 'auto'}
    
    value = get_name_from_desc(value)
    
    if mapping.has_key(value):
        value = mapping[value]    
    
    return value
    
def convert_int_to_snmp_version(value):
    '''
    Convert snmp version information.
    Input:
        Version2, Version3, 2, 3.
    Return:
        for version 2, snmpv2, for version 3, snmpv3.
    '''
    if type(value) != str:
        value = str(value)
        
    if value.find('1')> -1:
        value = 'snmpv2'
    else:
        value = 'snmpv3'
    
    return value

def convert_int_to_auth_protocol(value):
    ''' 
    Convert int to auth protocol type.
    Input: 1,2
    Output: 1 = MD5, 2 = SHA        
    '''
    if type(value) != str:
        value = int(value)
        if value == 1:
            value = 'MD5'
        else:
            value= 'SHA'
    
    return value

def convert_int_to_priv_protocol(value):
    ''' 
    Convert int to auth protocol type.
    Input: 1,2,3
    Output: 1: des(1) 2: aes(2) 3: none(3)        
    '''
    if type(value) != str:
        value = int(value)
        if value == 1:
            value = 'DES'
        elif value == 2:
            value= 'AES'
        else:
            value = 'NONE'
    
    return value
    
def convert_desc_to_enabled(value):
    '''
    Convert enable/disable description:
    Input: enable(1), disable(2)
    Output:  enabled, disabled.
    '''
    value = get_name_from_desc(value)
    
    if value.upper() in enable_value_mapping.keys():
        value = enable_value_mapping[value.upper()]

    return value

def convert_bool_to_enabled(value):
    '''
    Convert bool value or string 'True','False' to enabled/disabled,
    Input: True, "True", False, "False", true(1), false(1).
    Output: If true, enabled, else disabled.
    '''
    if type(value) != str:
        value = str(value)
        
    value = get_name_from_desc(value)    
    if compare(value, 'True', 'eq'):
        value = ENABLED
    else:
        value = DISABLED
    
    return value

def convert_int_to_enabled(value):
    '''
    Convert int value to enabled/disabled,
    Input: 1, 2
    Output: If 1, enabled, else disabled.
    '''
    if value == 1:
        result = ENABLED
    else:
        result = DISABLED

    return result

def convert_encrypt_opts_desc_to_name(desc):
    '''
    Convert encrption. 
    Input: none-enc(1), tls(2):  starttls(3)
    Output: none/tls/starttls
    '''
    result = get_name_from_desc(desc)

    if result.upper() == 'NONE-ENC':
        result = 'none'

    return result

def convert_encrypt_ops_int_to_name(value):
    '''
    Convert encrypt options from int to name.
    1 - none, 2 - tls, 3 - starttls. 
    '''
    if value == 3:
        result = 'starttls'
    elif value == 2:
        result = 'tls'
    else:
        result = 'none'
        
    return result

def convert_wlan_service_type(desc):
    '''
    Convert service type. 
    Input: 'standardUsage(1)', 'guestAccess(2)', 'hotSpotService(3)'
    Output: 'Standard Usage',: 'Guest Access', 'Hotspot Service(WISPr)'
    '''
    result = get_name_from_desc(desc)

    if result in wlan_service_type_mapping.keys():
        result = wlan_service_type_mapping[result]
    return result

def convert_aaa_server_service_type(desc):
    '''
    Convert service type. 
    Input: active-directory(1), ldap-directory(2), aaa-authentication(3), accounting(4)
    Output: 'Active Directory', 'LDAP Directory', 'AAA Authentication', 'Accounting'
    CLI: 'radius-auth','radius-acct','ad'
    '''
    result = get_name_from_desc(desc)
    
    if result in aaa_server_type_mapping.keys():
        result = aaa_server_type_mapping[result]
        
    return result

def convert_channel_to_name(channel):
    '''
    Convert channel int value to name. 
    If it is 0, it should be 'auto'.
    '''
    if str(channel) == '0':
        channel = 'auto'
        
    return channel
    

def convert_channel_tx_power(desc):
    '''
    Convert radio tx power.  
    Input: auto(1) full(2) half-full(3) quarter-full(4) one-eighth-full(5) one-tenth-full(6)
    Output: auto, full, 1/2, 1/4, 1/8, mini
    '''
    #value_mapping = {'half-full':'1/2',
    #                 'quarter-full':'1/4',
    #                 'one-eighth-full': '1/8',
    #                 'one-tenth-full': 'mini',
    #                 '0': 'auto'}
    #chen.tao @2013-11-18, to fix ZF-5873

    value = get_name_from_desc(desc)
    value_mapping = {'half-full':'3 dB',
                     'quarter-full':'6 dB',
                     'one-eighth-full': '9 dB',
                     'one-tenth-full': '24 dB',
                     '0': '0 dB',
                     '1': '1 dB',
                     '2': '2 dB',
                     '3': '3 dB',
                     '4': '4 dB',
                     '5': '5 dB',
                     '6': '6 dB',
                     '7': '7 dB',
                     '8': '8 dB',
                     '9': '9 dB',
                     '10': '10 dB',
                     'auto':'25 dB',
                     'full':'0 dB',
                     'mini':'24 dB',
                     'min':'24 dB'}  
    
    #chen.tao @2013-11-18, to fix ZF-5873  
    if value_mapping.has_key(value):
        value = value_mapping[value]
        
    return value
    
def get_country_name_by_code(code):
    '''
    Get country name by specified code. 'FR' to 'France'.
    Input: FR
    Output: France
    '''
    name = code
    if code.upper() in country_code_name_mapping.keys():
        name = country_code_name_mapping[code.upper()]
    else:
        name = code
    return name

def format_mac_address(value):
    '''
    Format mac address, format is 00:22:7F:1F:35:70.
    Input: 0:2:7F:1F:35:70.
    Output: 00:02:7F:1F:35:70.
    '''    
    value_list = value.split(':')

    for i in range(0, len(value_list)):
        v = value_list[i]
        if len(v) == 1:
            value_list[i] = '0%s' % (v,)

    new_value = ':'.join(v for v in value_list)

    return new_value

def format_uptime(value):
    '''
    Format uptime, format is 10d 18h 4m. 
    Input: [9.2](92909300) 10 days, 18:04:53.00, [9.1](515800) 1:25:58.00
    Output: '10d 18h 4m', '18h 4m', '1m 2s'.
    '''
    patterns = ['.*\s+(?P<day>[0-9]+)\s+day[s]?,\s+(?P<hour>[0-9]+):(?P<min>[0-9]+):(?P<second>[0-9]+)\.[0-9]+',
                #'\([0-9]+\)\s+(?P<day>[0-9]+)\s+days,\s+(?P<hour>[0-9]+):(?P<min>[0-9]+):(?P<second>[0-9]+)\.[0-9]+',
                '\((?P<time>[0-9]+)\)\s+(?P<hour>[0-9]+):(?P<min>[0-9]+):(?P<second>[0-9]+)\.[0-9]+',
               ]
        
    is_match = False
    for pattern in patterns:
        matcher = re.compile(pattern).match(value)
        if matcher:
            is_match = True
            result = matcher.groupdict()
            break  #break if match        

    if not is_match:
        result = value
    else:
        day = ''
        hour = ''
        min = ''
        if not result.has_key('day') and result.has_key('time'): 
            # computer days
            time = int(result['time']) if result['time'] else 0
            one_day_ms = 100 * 60 * 60 * 24
            result['day'] = time / one_day_ms
        
        if result.has_key('day'):
            if int(result['day']) > 0:
                day = '%sd' % (result['day'])            
        if result.has_key('hour'):
            if int(result['hour']) > 0:
                hour = '%sh' % (result['hour'])
        if result.has_key('min'):
            if int(result['min']) > 0:
                min = '%sm' % (result['min'])
            
        #if int(result['second']) > 0: second = '%ss' % (result['second'])
        #2d 0h 2m,
        
        result = '%s %s %s' % (day, hour, min)
        result = result.strip()

    return result

def verify_sys_uptime(uptime1, uptime2, max_diff = 5):
    '''
    Compare two value of system uptime, format is 1h 2m 3s.
    Allow some minutes different less than the specified value. Default is 5 mins.
    '''
    default_uptime_d = {'day': '0',
                        'hour': '0',
                        'min': '0'}
    
    uptime1 = format_uptime(uptime1.strip())
    uptime2 = format_uptime(uptime2.strip())
    
    patterns = ['(?P<day>[0-9]+)d\s+(?P<hour>[0-9]+)h\s+(?P<min>[0-9]+)m',
                '(?P<day>[0-9]+)d\s+(?P<hour>[0-9]+)h',
                '(?P<day>[0-9]+)d\s+(?P<min>[0-9]+)m',
                '(?P<day>[0-9]+)d',
                '(?P<hour>[0-9]+)h\s+(?P<min>[0-9]+)m',
                '(?P<hour>[0-9]+)h',
                '(?P<min>[0-9]+)m',]
    
    #Get day, hour, min information from the value.
    uptime1_d = copy.deepcopy(default_uptime_d) 
    for pattern in patterns:
        matcher = re.compile(pattern).match(uptime1)
        if matcher:
            uptime1_d.update(matcher.groupdict())
            break
        
    uptime2_d = copy.deepcopy(default_uptime_d)
    for pattern in patterns:
        matcher = re.compile(pattern).match(uptime2)
        if matcher:
            uptime2_d.update(matcher.groupdict())
            break
        
    time1_in_mins = int(uptime1_d['min']) + int(uptime1_d['hour']) * 60 + int(uptime1_d['day']) * 60 * 24
    time2_in_mins = int(uptime2_d['min']) + int(uptime2_d['hour']) * 60 + int(uptime2_d['day']) * 60 * 24
    
    if abs(time1_in_mins - time2_in_mins) > max_diff:
        result = False
    else:
        result = True

    return result    

def get_name_from_desc(desc):
    '''
    Get name from the description.
    Input: true(1)
    Output: true
    '''
    return _get_name_value_desc(desc)['name']

def get_value_from_desc(desc):
    '''
    Get value from the description.
    Input: true(1)
    Output: 1
    '''
    return _get_name_value_desc(desc)['value']

def get_random_web_site_string(min_len, max_len):
    '''
    Get random web site string, format is http://<website name>.<org>.
    The string length is between min_len and max_len. 
    '''
    fmt = 'http://%s.%s'    
#    site_name = "".join(sample(str_chars,site_len))
    type = 'alnum'
    site_name = get_random_string(type, 1, max_len-11)
    
    type = 'alnum'
    site_org = get_random_string(type, 3, 3)
    
    ret_str =  fmt % (site_name, site_org)
    
    return ret_str

def get_random_ip_addr():
    '''
    Get random ip address, format is xxx.xxx.xxx.xxx.
    Each value is between 1, and 255.
    '''
    ips = []
    ips.append(str(get_random_int(1, 223)))
    for i in range(1,4):
        ips.append(str(get_random_int(1, 255)))
    
    ip_addr = ".".join(ips)
    
    return ip_addr
    
def get_random_country_code(): 
    '''
    Get random country code in mapping dict. 
    '''   
    min = 0
    max = len(country_code_name_mapping) - 1    
    index = get_random_int(min, max)
    
    code = country_code_name_mapping.keys()[index]
    
    return code

def get_random_email_addr(min = 6, max = 64):
    '''
    Get random email address. Format is <name>@<website>.<org>.
    Notes: <org> is 2 to 3.
    '''
    email_fmt = '%s@%s.%s'
    
    type = 'alpha'
    org = get_random_string(type, 2, 3)
    webname = get_random_string(type, 1, 20)
    account_len = max - len(org) - len(webname)
    
    account = get_random_string(type, min-5, account_len)
    
    return email_fmt % (account, webname, org)

def get_items_by_key_value(snmp, mib, abbr_name_mapping, key_obj_name, key_value, convert_snmp_dict_func):
    '''
    Get items dict by primary key value, key_name is the key column name, key_value is specified value, 
    if it is *, will get all items.
    Output:
        Dict with all items or item with specified key value, key is index/id, value is item dict.
    '''
    #Get index and value of key mapping.
    oid = abbr_name_mapping[key_obj_name]
    index_key_value_mapping = get_index_value_mapping(snmp, mib, oid)
    
    #If primary key is mac addr, need to format mac addr.
    if key_obj_name == 'mac_addr':
        for key, value in index_key_value_mapping.items():
            index_key_value_mapping[key] = format_mac_address(value)
   
    items_d = {}
    if index_key_value_mapping:
        for index, value in index_key_value_mapping.items():
            if key_value == '*':
                items_d[index] = get_item_detail_by_index(snmp, mib, abbr_name_mapping, index, convert_snmp_dict_func)
            else:
                if compare(value, key_value, 'eq'):
                    items_d[index] = get_item_detail_by_index(snmp, mib, abbr_name_mapping, index, convert_snmp_dict_func)
                    break #break if find item
    return items_d

def get_index_value_mapping(snmp, mib, oid):
    '''
    Get all index and value of key_obj_name mapping for specified mib.
    '''    
    res_list = snmp.walk_by_name(mib, oid)
    index_key_mapping = {}
    pattern = '(?P<name>ruckus.+)\.(?P<index>[0-9]+)'    
    index = 0
    
    for key, value in res_list.items():
        matcher = re.compile(pattern).match(key)
        if matcher:
            dict = matcher.groupdict()
            if compare(dict['name'], oid, 'eq'):
                index = dict['index']
            index_key_mapping[index] = value
  
    return index_key_mapping

def parsing_snmp_result(snmp_dict, obj_abbr_name_mapping, object_name_index = 0, convert_func = None):
    '''
    Parsing the original result from snmp command.
    1. Convert the key from oid (ruckusZDSystemName) to object abbr (system_name).
    2. Convert the value by calling convert function.
    '''    
    new_dict = {}
    for key, value in obj_abbr_name_mapping.items():
        if key != 'row_status':
            original_dict_key = OBJNAME_INDEX_TEMP % (value, object_name_index)
            if snmp_dict.has_key(original_dict_key):
                item_value = snmp_dict[original_dict_key]            
            else:
                logging.warning("%s is not in res dict: %s" % (original_dict_key, snmp_dict))
                if snmp_dict.has_key('error'):
                    error_value = "".join(snmp_dict.values())
                    if len(value) < 300:
                        item_value = error_value
                    else:
                        item_value = 'Error message is too large. Get detail from log.'                        
                else:
                    item_value = "The key %s is not in result dict." % (original_dict_key)
                            
            new_dict[key] = item_value
    
    if convert_func:
        new_dict = convert_func(new_dict)    

    return new_dict

def get_item_detail_by_index(snmp, mib, abbr_name_mapping, index, convert_snmp_dict_func, keys_list = []):
    '''
    Get item detail config based on item index. 
    '''
    
    item_d = {}    
    
    for abbr, name in abbr_name_mapping.items():
        #Don't get row_status value.
        if abbr != 'row_status' and (not keys_list or (abbr in keys_list)):
            obj_value = get_one_object_value_by_name(snmp, mib, name, index)
            item_d[abbr] = obj_value
            
    if convert_snmp_dict_func:
        item_d = convert_snmp_dict_func(item_d)
    
    return item_d

def get_one_object_value_by_name(snmp, mib, name, index):
    '''
    Get one object value by mib,name and index.
    '''
    obj_dict = snmp.get_single_by_name(mib, name, index)
    key = OBJNAME_INDEX_TEMP % (name, index)
    if obj_dict.has_key(key):
        obj_value = obj_dict[key]
    else:
        obj_value = 'No value: OID = %s, res = %s' % (key, obj_dict)
    
    return obj_value

def verify_items_dict(items_dict_1, items_dict_2, convert_item_func = None, item_is_pass_func = None, oids_d = {}):
    '''
    Verify the items dict from snmp with other dict. Key is index, value is item detail dict.
    '''
    res_items_d = {}
    
    if items_dict_1 and items_dict_2:
        if len(items_dict_1) != len(items_dict_2):
            res_items_d['ALL'] = 'FAIL: The count of items are not same. dict1 = %s, dict2 = %s'\
                           % (len(items_dict_1), len(items_dict_2))
        else:
            if len(items_dict_1)>0:
                for index, item_info_d in items_dict_1.items():
                    res_d = verify_one_item_config(item_info_d, items_dict_2[index], convert_item_func, item_is_pass_func, oids_d, index,)
                    if res_d:
                        res_items_d[index] = res_d
            else:
                res_items_d['ALL'] = 'WARNING: No item need to be verified.'
    else:
        if not items_dict_1 == items_dict_2:
            res_items_d['ALL'] = "One items dict is none. Dict1: %s, Dict2: %s" % (items_dict_1, items_dict_2)

    return res_items_d

def verify_one_item_config(item_dict_1, item_dict_2, convert_item_func = None, item_is_pass_func = None, oids_d = {}, index = None):
    '''
    Verify a item config: snmp, cli, and gui values.
    '''
    res_d = {}

    try:
        if convert_item_func:
            new_item_dict_2 = convert_item_func(item_dict_2)
        else:
            new_item_dict_2 = item_dict_2

        dict1_keys = item_dict_1.keys()
        dict2_keys = new_item_dict_2.keys()        
        dict1_keys.sort()
        dict2_keys.sort()       
        # Verify keys in snmp, cli and gui values dict.
        #Chico@2014-6-24, ingore key hotspot_profile_id comparing temporarily ZF-8848
        if not (dict1_keys == dict2_keys):
            if 'hotspot_profile_id' in dict1_keys:
                logging.info('dict1 has key "hotspot_profile_id", remove it.')
                dict1_keys.remove('hotspot_profile_id')
            if 'hotspot_profile_id' in dict2_keys:
                logging.info('dict2 has key "hotspot_profile_id", remove it.')
                dict2_keys.remove('hotspot_profile_id')
            #@ZJ 20141022 ZF-10369
            if 'zero_it_activation' in dict1_keys and 'zero_it_activation' not in dict2_keys:
                logging.info('"zero_it_activation" no need in wlan of this type, remove it.')
                dict1_keys.remove('zero_it_activation')
            if 'wpa_cipher_type' in dict1_keys and 'wpa_cipher_type' not in dict2_keys:
                logging.info('"wpa_cipher_type" no need in wlan of this type, remove it.')
                dict1_keys.remove('wpa_cipher_type')
            if 'wpa_key' in dict1_keys and 'wpa_key' not in dict2_keys:
                logging.info('"wpa_key" no need in wlan of this type, remove it.')
                dict1_keys.remove('wpa_key')
            #@ZJ 20141022 ZF-10369           
            if not (dict1_keys == dict2_keys):
                res = 'FAIL: Keys in two dicts are different. dict1 keys: %s, dict2 keys: %s' % (dict1_keys, dict2_keys)
                res_d['ALL'] = res
        #Chico@2014-6-24, ingore key hotspot_profile_id comparing temporarily ZF-8848
        #logging.warning(res)
        
        for key, value in item_dict_1.items():
            try:
                res = ''
                res_value = ''
                if new_item_dict_2.has_key(key):
                    result = False
                    if item_is_pass_func:
                        is_pass, message = item_is_pass_func(item_dict_1, key)
                    else:
                        is_pass, message = False, ''
                        
                    if is_pass:
                        result = True
                    else:
                        if type(value) == dict:
                            value_2 = new_item_dict_2[key]
                            res_value = compare_dict_key_value(value, value_2)
                            if res_value:
                                result = False    
                            else:
                                result = True              
                        else:
                            value = str(value).strip()
                            value_2 = str(new_item_dict_2[key]).strip()
                            
                            if key.lower() == 'radio_type':   
                                if compare(value, value_2, 'in'):
                                    result = True
                                elif compare(value_2, value, 'in'):
                                    result = True
                            elif 'wireless_client' in key.lower() and (compare(value, value_2, 'in') or compare(value_2, value, 'in')):
                                result = True
                            elif 'secret' in key.lower() or 'password' in key.lower():
                                result = True
                            elif key.lower() == 'hotspot_profile_id':
                                result = True
                            elif key.lower() == 'ip_version' and value == 'dualstack' and value_2 == 'parent':
                                result = True                            
                            elif key.lower() == 'radio_5_tx_power' or key.lower() == 'radio_24_tx_power':
                                if compare(value.split(' ')[0].lower(), value_2.split(' ')[0].lower(), 'eq'):
                                    result = True 
                                else:
                                    if value.split(' ')[0] == '0' or value_2.lower() == 'full':
                                        result = True
                                    elif value.split(' ')[0] == '24' and value_2.lower() == 'min':
                                        result = True
                                    elif value.split(' ')[0] == '25' and value_2.lower() == 'auto':
                                        result = True 
                            else:   
                                if compare(value.lower(), value_2.lower(), 'eq'):
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
                        if oids_d and oids_d.has_key(key):
                            res = 'FAIL: col_name = %s, dict1_value = %s, dict2_value = %s, oid = %s, index = %s'  \
                                        % (key, value, new_item_dict_2[key], oids_d[key], index)
                        else:
                            if res_value:
                                res = 'FAIL: col_name = %s, index = %s, error = %s'  \
                                            % (key, index, res_value)
                            else:       
                                res = 'FAIL: col_name = %s, dict1_value = %s, dict2_value = %s, index = %s'  \
                                            % (key, value, new_item_dict_2[key], index)
                            
                        logging.warning(res)
    
            except Exception, e:
                res = 'Exception: col_name = %s, message = %s' % (key, e)
                logging.warning(res)
            finally:
                if res: 
                    res_d[key] = res
                    
    except Exception, e:
        res_d = {'Exception':'message = %s' % e}
        #logging.warning(res_wlans_d)
                    
    return res_d

def get_item_oids(mib, abbr_name_mapping):
    '''
    Get oids for all objects.
    '''
    snmp = snmp_com()
    max_length = 500    
    oids_d = {}
    for abbr, name in abbr_name_mapping.items():
        oid_list = snmp.translate_name(mib, name, True)
        oid = "".join(oid_list)
        if len(oid) > max_length:
            logging.warning('Error during get oid: %s' % oid)
            oid = 'Error during get oid.'
        oids_d[abbr] = oid

    return oids_d

def gen_new_index(snmp, mib, oid, start_index, max_index):
    '''
    Generate new index for create a new item. 
    Return the index does not exist in current item list, range is start_index to max_index.
    If return as 0, can't create the item.
    '''    
    #Get index and value of key mapping.
    index_key_mapping = get_index_value_mapping(snmp, mib, oid) 
    
    index = 0
    
    if index_key_mapping:
        index_list = index_key_mapping.keys()        
        for i in range(start_index, max_index):
            if not ((i in index_list) or (str(i) in index_list)):
                index = i
                break
    else:
        index = start_index

    return index

def update_single_node_value(snmp, mib, oid, index, type, value):
    '''
    Update one objects based on mib, oid, index, and type, value.
    '''
    res = snmp.set_single_by_name(mib, oid, index, type , value)
    
    return res
    
def delete_an_item(snmp, mib, index, row_status_oid, row_status_type, delete_value):
    '''
    Delete an item. Normal is set row_status as 6.
    '''
    return update_single_node_value(snmp, mib, row_status_oid, index, type , delete_value)

def update_objects_config(snmp, mib, abbr_name_mapping, rw_obj_type_mapping, rw_obj_keys_order_list, update_cfg, flag):
    '''
    Update a item(wlan, aaa server...): create on item, update some settings, delete the item.
    Input:
        flag: 1 - create
        update_cfg: include indexs and setting's value dict.
        {index:3, desc='this is test.'...}
    '''
    update_cfg_copy = copy.deepcopy(update_cfg)
    
    if not update_cfg_copy.has_key('index'):
        raise Exception('Need to set index for the objects will be updated. Config:%s' % update_cfg)
    
    index = update_cfg_copy.pop('index')
    
    if flag == 3:
        #For delete, update row status as 6.        
        oid = abbr_name_mapping['row_status']
        obj_type = rw_obj_type_mapping['row_status']
        value = '6'
        update_single_node_value(snmp, mib, oid, index, obj_type , value)
    else:
        wlan_config_list = []
        for key in rw_obj_keys_order_list:
            item_d = {}
            item_d['mib'] = mib
            item_d['oid'] = abbr_name_mapping[key]
            item_d['type'] = rw_obj_type_mapping[key]
            item_d['index'] = index
            if flag == 1 and key == 'row_status':
                #For create, set row status as 4.
                item_d['value'] = '4'            
                wlan_config_list.append(item_d)
            elif update_cfg_copy.has_key(key):
                item_d['value'] = get_value_from_desc(update_cfg_copy[key])
                wlan_config_list.append(item_d)
        
        if len(wlan_config_list) >0:
            snmp.set_multi_by_name(wlan_config_list)

def verify_error_for_negative(res_d):
    '''
    Verify errors for negative input.
    '''
    error_ptn_list = ['.+wrongValue \(The set value is illegal or unsupported in some way\).+',
                      '\(Bad string length :: {\([0-9]+.+\)}\)',
                      '\(Bad string length :: {\([0-9]+\)}\)',   #(Bad string length :: {(2)})
                      '\([0-9]+ :: {.+}\)',
                      '.+Value does not match DISPLAY-HINT :: {\([0-9]+\.\.[0-9]+\)}',
                      '.+wrongType \(The set data type does not match the data type the agent expects\).+',
                      '.+inconsistentValue \(The set value is illegal or unsupported in some way\).+',
                      '\([0-9]+ :: {\([0-9]+\.\.[0-9]+\)}\)', #(65536 :: {(1..65535)})
                      '\([0-9]+\.\.[0-9]+\)',  #(1..32)
                      '\([0-9]+\)', #(26)
                      '\([0-9\.]+\)'  #[A-Z-]+::[a-zA-Z]+\.[1-9]+:\s+
                      #For invalid ip address, result is lik RUCKUS-ZD-AP-MIB::ruckusZDAPConfigIpAddress.1:  (256.255.255.255)
                     ]
    
    pass_d = {}
    fail_d = {}
    
    for key,value in res_d.items():
        is_macth = False
        if type(value) == dict:
            actual_error = "".join(value.values())
        else:
            actual_error = value
                
        for err_ptn in error_ptn_list:
            regex = re.compile(err_ptn, re.DOTALL)
            r = regex.search(actual_error)
            
            if r:
                is_macth = True
                
        if is_macth:
            pass_d.update({key: '%s' % (actual_error,)})                                
        else:
            fail_d.update({key: '%s' % (actual_error,)})
            
    return pass_d, fail_d

#=============================================#
#             Private Methods            
#=============================================#

def _get_name_value_desc(desc):
    '''
    Get name and value from description. Format is <name>(<value>).
    E.g. enable(1), name is enable, value is 1.
    '''
    pattern = '(?P<name>.+)\((?P<value>[0-9]+)\)'
    
    matcher = re.compile(pattern).match(desc)
    if matcher:
        result = matcher.groupdict()
    else:
        result = {'name':desc, 'value': desc}

    return result
