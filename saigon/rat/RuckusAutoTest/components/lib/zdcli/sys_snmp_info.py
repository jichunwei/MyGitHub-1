'''
Author#cwang@ruckuswireless.com
date#2010-10-28
This file is used for system SNMPv2 Agent/Trap information getting/setting/searching etc.
'''

import re
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common.utils import compare_dict_key_value
#from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt

#=============================================#
#             Access Methods            
#=============================================#
def get_sys_snmpv2_info(zdcli):
    '''
    Get snmp v2 agent information.    
    'SNMP Agent': {'Contact': 'cherry.cheng@ruckuswireless.com',
                   'Location': 'shenzhen',
                   'RO Community': 'public',
                   'RW Community': 'private',
                   'Status': 'Enabled'}
    '''
    
    res = zdcli.do_cfg_show(SHOW_SYS_SNMP_V2)
            
    rr = output.parse(res)
    rr = rr['SNMP Agent']
    
    #rr = _refind_dict(rr)
    
    return rr

def get_sys_snmpv3_info(zdcli):
    '''
    Get snmp v3 agent information.   
    '''  
    res = zdcli.do_cfg_show(SHOW_SYS_SNMP_V3) 
    
    rr = output.parse(res)
    rr = rr['SNMPV3 Agent']
    
    rr = _parse_v3_agent(rr)
    
    return rr    

def get_sys_snmp_trap_info(zdcli):
    '''
    Get snmp trap information.
    'SNMP Trap': Version 2:
               {'Format': 'Version2',
                'Status': 'Enabled',
                'Trap Server IP/IPV6 Address': '192.168.30.252'},
                 Version 3:
               {'Authentication Pass Phrase': '12345678',
                'Authentication Type': 'MD5',
                'Format': 'Version3',
                'Privacy Type': 'None',
                'Privacy Phrase':'12345678',
                'Status': 'Enabled',
                'Trap Server IP/IPV6 Address': '192.168.0.10',
                'User': 'ruckus-read'}
    '''    
    res = zdcli.do_cfg_show(SHOW_SYS_SNMP_V2)
    rr = output.parse(res)
    
    rr = rr ['SNMP Trap']
    rr = _refind_dict(rr)
    
    _convert_snmp_trap_info(rr)
    
    return rr

def get_sys_snmp_trap_v3_info(zdcli):
    '''
    Get snmp trap information.
    'SNMP Trap': Version 3:
               {'Authentication Pass Phrase': '12345678',
                'Authentication Type': 'MD5',
                'Format': 'Version3',
                'Privacy Type': 'None',
                'Privacy Phrase':'12345678',
                'Status': 'Enabled',
                'Trap Server IP/IPV6 Address': '192.168.0.10',
                'User': 'ruckus-read'}
    '''
    res = zdcli.do_cfg_show(SHOW_SYS_SNMP_V3)
    rr = output.parse(res)
    
    rr = rr ['SNMP Trap']
    rr = _refind_dict(rr)
    
    _convert_snmp_trap_info(rr)
    
    return rr

def verify_snmpv2_agent(gui_d, cli_d):
    '''
    Checking snmpv2 agent information, between GUI and CLI.
    '''
    return _verify_snmpv2_agent(gui_d, cli_d)

def verify_snmpv3_agent(gui_d, cli_d):
    '''
    Checking snmpv3 agent information, between GUI and CLI.
    '''
    return _verify_snmpv3_agent(gui_d, cli_d)

def verify_snmp_trap(gui_d, cli_d):
    '''
    Checking snmpv2 trap information, between GUI and CLI.
    '''
    return _verify_snmp_trap(gui_d, cli_d)

def verify_snmp_trap_set_get(set_d, cli_d):
    return _verify_snmp_trap(set_d, cli_d)

def check_snmpd_process(zdcli):    
    '''
    Check snmpd process in the result of 'ps'.
    '''
    #cmd_check_snmpd_process = "ps -aux|grep 'snmpd'"
    cmd_check_snmpd_process = "ps aux|grep snmpd |grep -v grep"
    
    res = zdcli.do_shell_cmd(cmd_check_snmpd_process)
    snmpd_process_str = '/usr/sbin/snmpd udp:161,udp6:161'
    matcher = re.compile(snmpd_process_str).search(res)
        
    if matcher:
        return True
    else:        
        return False 

#===============================================#
#           Protected Constant
#===============================================#
SHOW_SYS_SNMP_V2 = '''
system
    snmpv2
'''

SHOW_SYS_SNMP_V3 = '''
system
    snmpv3
'''

SNMPV2_AGENT_K_MAP = {'contact': 'Contact',
                      'enabled': 'Status',
                      'location': 'Location',
                      'ro_community':'RO Community',
                      'rw_community': 'RW Community',
                      }

SNMPV3_AGENT_K_MAP = {'enabled': 'status',
                      'ro_auth_passphrase': 'ro_auth_key',
                      'ro_auth_protocol': 'ro_auth',
                      'ro_priv_passphrase': 'ro_priv_key',
                      'ro_priv_protocol': 'ro_priv',
                      'ro_sec_name': 'ro_user',
                      'rw_auth_passphrase': 'rw_auth_key',
                      'rw_auth_protocol': 'rw_auth',
                      'rw_priv_passphrase': 'rw_priv_key',
                      'rw_priv_protocol': 'rw_priv',
                      'rw_sec_name': 'rw_user',           
                      }

SNMP_TRAP_K_MAP = {'enabled':'Status',
                   'version': 'Format',
                   }

SNMP_TRAP_SERVER_K_MAP = {'server_ip': 'Trap Server IP/IPV6 Address',
                          'auth_passphrase': 'Authentication Pass Phrase',
                          'auth_protocol': 'Authentication Type',
                          'priv_protocol': 'Privacy Type',
                          'priv_passphrase': 'Privacy Phrase',
                          'sec_name': 'User'
                          }

#===============================================#
#           Protected Method
#===============================================#
def _verify_snmpv2_agent(gui_d, cli_d):
    '''
    GUI:
    { 'enabled': False,
      'server_ip': u'192.168.0.252',
      'version': u'2'}
    CLI:
    { 'Format': 'Version2',
      'Status': 'Disabled',
      'Trap Server IP/IPV6 Address': '192.168.0.252'}
    '''
    
    if gui_d['enabled']:
        gui_d['enabled'] = 'Enabled'
    else:
        gui_d['enabled'] = 'Disabled'    
        
    r_d = _map_k_d(gui_d, cli_d, SNMPV2_AGENT_K_MAP)
    return _validate_dict_value(r_d, cli_d)

def _verify_snmpv3_agent(gui_d, cli_d):
    '''
    GUI:
        {'enabled': True,
         'ro_auth_passphrase': u'12345678',
         'ro_auth_protocol': u'MD5',
         'ro_priv_passphrase': u'12345678',
         'ro_priv_protocol': u'DES',
         'ro_sec_name': u'ruckus-read',
         'rw_auth_passphrase': u'12345678',
         'rw_auth_protocol': u'MD5',
         'rw_priv_passphrase': u'12345678',
         'rw_priv_protocol': u'DES',
         'rw_sec_name': u'ruckus-write'}
         
    CLI:
        {'ro_auth_key': '',
         'ro_auth': '',
         'ro_priv': '',
         'ro_priv_key': '',
         'ro_user': '',
         'rw_auth': '',
         'rw_auth_key': '',
         'rw_priv': '',
         'rw_priv_key': '',
         'rw_user': '',
         'status': 'Enabled',
    '''
    
    enable = gui_d.pop('enabled')
    if enable:
        gui_d['enabled'] = 'Enabled'
    else:
        gui_d['enabled'] = 'Disabled'
        
    r_d = _map_k_d(gui_d, cli_d, SNMPV3_AGENT_K_MAP)
    return _validate_dict_value(r_d, cli_d)


def _verify_snmp_trap(gui_or_set_d, cli_d):
    '''
    GUI:
        {'enabled': True,
        '1': {'sec_name': u'ruckus-read',
         'server_ip': u'192.168.0.2',
         'server_ip': u'192.168.0.2',
         'auth_protocol': u'MD5',
         'auth_passphrase': u'12345678',
         'priv_protocol': u'DES',         
         'priv_passphrase': u'12345678',         
         'version': u'2'},
         }
    CLI:
     {'Format': 'Version2',
      'Status': 'Enabled',
      '1': {'Trap Server IP/IPV6 Address': '192.168.0.252'},
      }    
    '''
    _convert_set_d(gui_or_set_d)
    
    status = False
    
    if gui_or_set_d.has_key('enabled'):
        if gui_or_set_d['enabled']:
            gui_or_set_d['enabled'] = 'Enabled'
            status = True
        else:
            gui_or_set_d['enabled'] = 'Disabled'
            status = False
        
    if gui_or_set_d.has_key('version'):
        if '2' in str(gui_or_set_d['version']):
            gui_or_set_d['version'] = 'Version2'
        else:
            gui_or_set_d['version'] = 'Version3'
    
    res_trap = {}
    
    if gui_or_set_d['enabled'] == 'Enabled':
        #Get trap servers information.
        gui_servers_info = {}
        cli_servers_info = {}
        for i in range(1,5):
            key = str(i)
            if gui_or_set_d.has_key(key):
                gui_server_info = _map_k_d(gui_or_set_d.pop(key), {}, SNMP_TRAP_SERVER_K_MAP)
                #Remove privacy phrase when privacy type is none.
                privacy_type = gui_server_info.get("Privacy Type")     
                if privacy_type and privacy_type.lower() == 'none':
                    if gui_server_info.has_key("Privacy Phrase"):
                        gui_server_info.pop("Privacy Phrase")
                
                gui_servers_info[key] = gui_server_info
                
            if cli_d.has_key(key):
                cli_server_info = cli_d.pop(key)
                #Remove privacy phrase when privacy type is none.
                privacy_type = cli_server_info.get("Privacy Type")     
                if privacy_type and privacy_type.lower() == 'none':
                    if cli_server_info.has_key("Privacy Phrase"):
                        cli_server_info.pop("Privacy Phrase")
                
                cli_servers_info[key] = cli_server_info
                
        res_trap_servers = compare_dict_key_value(cli_servers_info, gui_servers_info)
    
        if res_trap_servers:
            res_trap['server'] = res_trap_servers
        
    gui_d_convert = _map_k_d(gui_or_set_d, {}, SNMP_TRAP_K_MAP)
    
    if not status:
        #If status is disabled, remove version and other items.
        for key in cli_d.keys():
            if key != 'Status':
                cli_d.pop(key)
            
        for key in gui_d_convert.keys():
            if key != 'Status':
                gui_d_convert.pop(key)
        
        for i in range(1,5):
            if cli_d.has_key(str(i)):
                cli_d.pop(str(i))
            if gui_d_convert.has_key(str(i)):
                gui_d_convert.pop(str(i))
        
    res_trap_summary = compare_dict_key_value(gui_d_convert, cli_d)
    if res_trap_summary:
        res_trap['summary'] = res_trap_summary
        
    if res_trap:
        res = False
    else:
        res = True
        
    return res, res_trap 

def _convert_set_d(set_d):
    if set_d.get('server_ip') != None:
        #For only snmpv2, and pass server_ip.
        trap_server_info = {}
        trap_server_info['server_ip'] = set_d.pop('server_ip')
        if set_d.has_key('sec_name'):
            trap_server_info['sec_name'] = set_d.pop('sec_name')
        if set_d.has_key('auth_protocol'):
            trap_server_info['auth_protocol'] = set_d.pop('auth_protocol')
        if set_d.has_key('auth_passphrase'):
            trap_server_info['auth_passphrase'] = set_d.pop('auth_passphrase')
        if set_d.has_key('priv_protocol'):
            trap_server_info['priv_protocol'] = set_d.pop('priv_protocol')
        if set_d.has_key('priv_passphrase'):
            trap_server_info['priv_passphrase'] = set_d.pop('priv_passphrase')
                
        set_d['1'] = trap_server_info
            
def _map_k_d(gui_d, cli_d, k_map):
    '''
    Mapping GUI key to CLI key.
    '''
    gui_d_convert = {}
    
    for key,value in gui_d.items():
        if k_map.has_key(key):
            gui_d_convert[k_map[key]] = value
            
    return gui_d_convert

def _refind_dict(dict):
    '''    
    Refind the dict: 
        For key is like AAAA:BBB, will refine as a item "AAA": "BBB"
    '''
    colon = ':'
    for key in dict.keys():
        if key.find(colon)>0:
            new_key = key.split(colon)[0].strip()
            new_value = key.split(colon)[1].strip()
            dict.pop(key)            
            dict.update({new_key:new_value})
    return dict

def _validate_dict_value(gui_d, cli_d):
    '''
    #Verify keys of dicts.
    gui_keys = gui_d.keys()
    cli_keys = cli_d.keys()
    
    gui_keys.sort()
    cli_keys.sort()
    
    if not gui_keys == cli_keys:
        return (False, 'Keys of dicts are different. GUI keys: %s, CLI keys: %s' % (gui_keys, cli_keys))
    '''
    for g_k, g_v in gui_d.items():
        for c_k, c_v in cli_d.items():
            if g_k == c_k:
                if g_v == c_v:
                    continue
                else:
                    return (False, 'value of key [%s] is not equal' % g_k)
                            
    return (True, 'All of value are matched')


def _parse_v3_agent(agent_dict):
    new_agent_dict = {'status': '',
                      'ro_user': '',
                      'ro_auth': '',
                      'ro_auth_key': '',
                      'ro_priv': '',
                      'ro_priv_key': '',
                      'rw_user': '',
                      'rw_auth': '',
                      'rw_auth_key': '',
                      'rw_priv': '',
                      'rw_priv_key': '',
                      }
    
    new_agent_dict['status'] = agent_dict['Status']
    
    if agent_dict.has_key('Ro'):
        ro_cfg = agent_dict['Ro']
        new_agent_dict['ro_user'] = ro_cfg['User']
        new_agent_dict['ro_auth'] = ro_cfg['Authentication Type']
        new_agent_dict['ro_auth_key'] = ro_cfg['Authentication Pass Phrase']
        new_agent_dict['ro_priv'] = ro_cfg['Privacy Type']
        new_agent_dict['ro_priv_key'] = ro_cfg['Privacy Phrase']
        
    if agent_dict.has_key('Rw'):
        rw_cfg = agent_dict['Rw']
        new_agent_dict['rw_user'] = rw_cfg['User']
        new_agent_dict['rw_auth'] = rw_cfg['Authentication Type']
        new_agent_dict['rw_auth_key'] = rw_cfg['Authentication Pass Phrase']
        new_agent_dict['rw_priv'] = rw_cfg['Privacy Type']
        new_agent_dict['rw_priv_key'] = rw_cfg['Privacy Phrase']
    
    return new_agent_dict

def _convert_snmp_trap_info(rr):
    '''
    Convert snmp trap information based on old output structure.
    '''
    trap_users_list = []
    trap_auth_type_list = []
    trap_auth_pass_list = []
    trap_priv_type_list = []
    trap_priv_pass_list = []
    
    server_ip_key = SNMP_TRAP_SERVER_K_MAP['server_ip']
    
    if rr['Status'].lower() == 'enabled':
        servers_dict = {}
        if rr.has_key('Index'):
            indexs_list = rr.pop('Index')            
            trap_server_list = rr.pop(server_ip_key)
            if '3' in rr['Format']:
                trap_users_list = rr.pop('User')
                trap_auth_type_list = rr.pop('Authentication Type')
                trap_auth_pass_list = rr.pop('Authentication Pass Phrase')
                trap_priv_type_list = rr.pop('Privacy Type')
                trap_priv_pass_list = rr.pop('Privacy Phrase')
                
                if type(trap_users_list) != list:
                    trap_users_list = [trap_users_list]
                if type(trap_auth_type_list) != list:
                    trap_auth_type_list = [trap_auth_type_list]
                if type(trap_auth_pass_list) != list:
                    trap_auth_pass_list = [trap_auth_pass_list]
                if type(trap_priv_type_list) != list:
                    trap_priv_type_list = [trap_priv_type_list]
                if type(trap_priv_pass_list) != list:
                    trap_priv_pass_list = [trap_priv_pass_list]
            
            if type(indexs_list) != list:
                indexs_list = [indexs_list]
            if type(trap_server_list) != list:
                trap_server_list = [trap_server_list]
            
            for index in indexs_list:
                trap_server_info = {}
                i = int(index)-1
                trap_server_info[server_ip_key] = trap_server_list[i]
                if '3' in rr['Format']:
                    trap_server_info['User']= trap_users_list[i]
                    trap_server_info['Authentication Type']= trap_auth_type_list[i]
                    trap_server_info['Authentication Pass Phrase']= trap_auth_pass_list[i]
                    trap_server_info['Privacy Type']= trap_priv_type_list[i]
                    trap_server_info['Privacy Phrase']= trap_priv_pass_list[i]
                    
                servers_dict[index] = trap_server_info
        
        rr.update(servers_dict)      


