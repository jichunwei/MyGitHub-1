'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.26
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    This document is to config snmp agent and trap. Include enable, disable snmp v2 and v3 agent and trap.
'''

import logging
from string import Template
from pprint import pformat

#============================================#
#             Access Methods            
#=============================================#
def config_snmp_agent(zdcli, agent_cfg):
    '''
    Config snmp agent based on specified config, enable and disable agent v2 and v3.
    Input: 
        agent_cfg format:
         {'version': 2,
         'enabled': True,
         #agent 2 parameters
         'ro_community': 'public',
         'rw_community': 'private',
         'contact': 'support@ruckuswireless.com',
         'location': 'Shenzhen',
         #agent 3 parameters
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
         }    
    Return:
        True if success.
        False if fail.
    '''
    snmp_agent_cfg = default_agent_cfg
    snmp_agent_cfg.update(agent_cfg)

    version = int(snmp_agent_cfg['version'])
    if snmp_agent_cfg['enabled']:    
        result, res_dict = _enable_snmp_agent(zdcli, snmp_agent_cfg, version)
    else:
        result, res_dict = _disable_snmp_agent(zdcli, version)

    return result, res_dict

def enable_snmp_agent_v2(zdcli, agent_v2_cfg = {}):
    '''
    Enable snmp agent for version 2, with specified config.
    Input agent_v2_cfg:
           {'ro_community': 'public',
            'rw_community': 'private',
            'contact': 'support@ruckuswireless.com',
            'location': 'Shenzhen',}
    Return:
        True if success.
        False if fail.
    '''
    return _enable_snmp_agent(zdcli, agent_v2_cfg, 2)

def enable_snmp_agent_v3(zdcli, agent_v3_cfg = {}):
    '''
    Enable snmp agent for version 3, with specified config.
    Input agent_v3_cfg:
           {'ro_sec_name': 'ruckus-read',            
            'ro_auth_protocol': 'MD5',
            'ro_auth_passphrase': '12345678',
            'ro_priv_protocol': 'DES',
            'ro_priv_passphrase': '12345678',
            'rw_sec_name': 'ruckus-write',
            'rw_auth_protocol': 'MD5',
            'rw_auth_passphrase': '12345678',
            'rw_priv_protocol': 'DES',
            'rw_priv_passphrase': '12345678',}
    Return:
        True if success.
        False if fail.
    '''
    return _enable_snmp_agent(zdcli, agent_v3_cfg, 3)

def config_snmp_trap(zdcli, trap_cfg):
    '''
    Config snmp agent based on specified config.
    Input trap_cfg, if version is 2, only server_ip is required.
       {'version': 2,
        'enabled': True,
        #For version 2:
        '1': {'server_ip': '192.168.0.2',},
        #For version 3:        
        '1': {'sec_name': 'ruckus-read',
              'server_ip': '192.168.0.2',
              'auth_protocol': 'MD5',
              'auth_passphrase': '12345678',
              'priv_protocol': 'DES',
              'priv_passphrase': '12345678',
              }
        }
    Return:
        True if success.
        False if fail.
    '''
    snmp_trap_cfg = default_trap_cfg
    snmp_trap_cfg.update(trap_cfg)
    
    if snmp_trap_cfg.has_key('server_ip'):
        trap_server_info = {}
        trap_server_info['server_ip'] = snmp_trap_cfg.pop('server_ip')
            
        if snmp_trap_cfg.has_key('sec_name'):
            trap_server_info['sec_name'] = snmp_trap_cfg.pop('sec_name')
        if snmp_trap_cfg.has_key('auth_protocol'):
            trap_server_info['auth_protocol'] = snmp_trap_cfg.pop('auth_protocol')
        if snmp_trap_cfg.has_key('auth_passphrase'):
            trap_server_info['auth_passphrase'] = snmp_trap_cfg.pop('auth_passphrase')
        if snmp_trap_cfg.has_key('priv_protocol'):
            trap_server_info['priv_protocol'] = snmp_trap_cfg.pop('priv_protocol')
        if snmp_trap_cfg.has_key('priv_passphrase'):
            trap_server_info['priv_passphrase'] = snmp_trap_cfg.pop('priv_passphrase')
            
        snmp_trap_cfg['1'] = trap_server_info

    version = int(snmp_trap_cfg['version'])

    if snmp_trap_cfg['enabled']:
        return _enable_snmp_trap(zdcli, snmp_trap_cfg, version)
    else:
        return _disable_snmp_trap(zdcli)


def enable_snmp_trap_v2(zdcli, trap_v2_cfg = {}):
    '''
    Enable snmp trap and set trap format as snmpv2.
    Input:
      {'server_ip': '192.168.0.2'}
    Return:
        True if success.
        False if fail.
    '''
    return _enable_snmp_trap(zdcli, trap_v2_cfg, 2)

def enable_snmp_trap_v3(zdcli, trap_v3_cfg = {}):
    '''
    Enable snmp trap and set trap format as snmpv3.
    Input:
       {'sec_name': 'ruckus-read',
       'server_ip': '192.168.0.2',
       'auth_protocol': 'MD5',
       'auth_passphrase': '12345678',
       'priv_protocol': 'DES',
       'priv_passphrase': '12345678',}
    Return:
        True if success.
        False if fail.
    '''
    return _enable_snmp_trap(zdcli, trap_v3_cfg, 3)

def disable_snmp_agent_v2(zdcli):
    '''
    Disable snmp agent for version 2.
    Return:
        True if success.
        False if fail.
    '''
    return _disable_snmp_agent(zdcli, 2)

def disable_snmp_agent_v3(zdcli):
    '''
    Disable snmp agent for version 3.
    Return:
        True if success.
        False if fail.
    '''
    return _disable_snmp_agent(zdcli, 3)

def disable_snmp_trap(zdcli):
    '''
    Disable snmp trap. 
    Return:
        True if success.
        False if fail.
    '''
    return _disable_snmp_trap(zdcli)

def config_snmp_trap_format(zdcli,version=2):
    '''
    Configure the format of snmp trap 
    Return:
        True if success.
        False if fail.
    '''
    return _config_snmp_trap_format(zdcli,version)

def remove_snmpv2_trap(zdcli):
    '''
    Delete all snmpv2 trap settings 
    Return:
        True if success.
        False if fail.
    '''
    return _remove_snmpv2_trap(zdcli)


def remove_snmpv3_trap(zdcli):
    '''
    Delete all SNMPv3 trap settings 
    Return:
        True if success.
        False if fail.
    '''
    return _remove_snmpv3_trap(zdcli)
#===============================================#
#           Protected Constant
#===============================================#
CONFIG_SYSTEM = '''
system
'''

CONFIG_SNMP_AGENT_V2_CMD_BLOCK = '''
system
    snmpv2
'''

CONFIG_SNMP_AGENT_V3_CMD_BLOCK = '''
system
    snmpv3
'''

DISABLE_SNMP_AGENT_V2 = '''
system
    no snmpv2
'''

DISABLE_SNMP_AGENT_V3 = '''
system
    no snmpv3
'''

DISABLE_SNMP_TRAP = '''
system
    no snmp-trap
'''

#commands for snmp v2 agent setting.
SET_AGENT_V2_RO_COMMUNITY = "ro-community '$ro_community'\n"
SET_AGENT_V2_RW_COMMUNITY = "rw-community '$rw_community'\n"
SET_AGENT_V2_CONTACT = "contact '$contact'\n"
SET_AGENT_V2_LOCATION = "location '$location'\n"

#commands for snmp v3 agent setting.
SET_AGENT_V3_RO_USER = "ro-user '$ro_sec_name' $ro_auth_protocol '$ro_auth_passphrase' $ro_priv_setting\n"
SET_AGENT_V3_RW_USER = "rw-user '$rw_sec_name' $rw_auth_protocol '$rw_auth_passphrase' $rw_priv_setting\n"

#commands for snmp trap setting: v2 and v3.
SET_TRAP_V2_FORMAT = 'snmp-trap-format SNMPv2\n'
SET_TRAP_V3_FORMAT = 'snmp-trap-format SNMPv3\n'
#@Author: chen.tao@odc-ruckuswireless.com Since 2013-9-26 to delete the ',' at the end of line 265 and 267
SET_TRAP_V2_CONFIG = "snmpv2-trap $number '$server_ip'\n"

SET_TRAP_V3_CONFIG = "snmpv3-trap $number '$sec_name' '$server_ip' $auth_protocol '$auth_passphrase' $priv_setting\n"
#@Author: chen.tao@odc-ruckuswireless.com Since 2013-9-26 to delete the ',' at the end of line 265 and 267
DISABLE_SNMPv2_TRAP = "no snmpv2-trap %s\n"
DISABLE_SNMPv3_TRAP = "no snmpv3-trap %s\n"
#save setting command.
SAVE_SERVER_CONFIG = "exit\n"

#default config for snmp agent v2 setting.                    
default_agent_v2_cfg = {'ro_community': 'public',
                        'rw_community': 'private',
                        'contact': 'support@ruckuswireless.com',
                        'location': 'Shenzhen',
                        }

#default config for snmp agent v3 setting.
default_agent_v3_cfg = {'ro_sec_name': 'ruckus-read',
                        'ro_auth_protocol': 'MD5',
                        'ro_auth_passphrase': '12345678',
                        'ro_priv_protocol': 'DES',
                        'ro_priv_passphrase': '12345678',
                        'rw_sec_name': 'ruckus-write',
                        'rw_auth_protocol': 'MD5',
                        'rw_auth_passphrase': '12345678',
                        'rw_priv_protocol': 'DES',
                        'rw_priv_passphrase': '12345678',
                         }

default_agent_cfg = {'version': 2,
                     'enabled': True,
                     'ro_community': 'public',
                     'rw_community': 'private',
                     'contact': 'support@ruckuswireless.com',
                     'location': 'Shenzhen',
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
                     }

default_trap_cfg = {'version': 2,
                    'enabled': True,
                    #'1': {'server_ip': '192.168.0.10'}
                    }

def _disable_snmp_agent(zdcli, version):
    '''
    Disable snmp agent based on version.
    '''
    if version == 2:
        cmd_block = DISABLE_SNMP_AGENT_V2
    else:
        cmd_block = DISABLE_SNMP_AGENT_V3

    cmd_block = cmd_block + SAVE_SERVER_CONFIG
    return _execute_config_snmp_cmd(zdcli, cmd_block)

def _disable_snmp_trap(zdcli):
    '''
    Disable snmp trap.
    '''
    cmd_block = DISABLE_SNMP_TRAP
    cmd_block = cmd_block + SAVE_SERVER_CONFIG
    return _execute_config_snmp_cmd(zdcli, cmd_block)

def _config_snmp_trap_format(zdcli, version = 2):
    '''
    Configure snmp trap format
    '''
    cmd_block = CONFIG_SYSTEM
    if version == 2:
        cmd_block = cmd_block + SET_TRAP_V2_FORMAT
    else:
        cmd_block = cmd_block + SET_TRAP_V3_FORMAT
    cmd_block = cmd_block + SAVE_SERVER_CONFIG
    return _execute_config_snmp_cmd(zdcli, cmd_block)

def _remove_snmpv2_trap(zdcli):
    '''
    Delete all SNMPv2 trap settings
    '''
    cmd_block = CONFIG_SYSTEM
    
    for i in range(1,5):
        cmd_block = cmd_block + (DISABLE_SNMPv2_TRAP % i)

    cmd_block = cmd_block + SAVE_SERVER_CONFIG

    return _execute_config_snmp_cmd(zdcli, cmd_block)

def _remove_snmpv3_trap(zdcli):
    '''
    Delete all SNMPv3 trap settings
    '''
    cmd_block = CONFIG_SYSTEM    
    for i in range(1,5):
        cmd_block = cmd_block + (DISABLE_SNMPv3_TRAP % i)

    cmd_block = cmd_block + SAVE_SERVER_CONFIG

    return _execute_config_snmp_cmd(zdcli, cmd_block)


def _enable_snmp_agent(zdcli, cfg, version = 2):
    '''
    Enable snmp agent. Contruct cmd block based on version, then execute.
    '''
    if version == 2:
        agent_cfg = default_agent_v2_cfg
        agent_cfg.update(cfg)
        cmd_block = _construct_agent_cmd_v2(agent_cfg)
    else:
        agent_cfg = default_agent_v3_cfg
        agent_cfg.update(cfg)
        cmd_block = _construct_agent_cmd_v3(agent_cfg)

    logging.info('Enable snmp agent:\nConfig:%s,\nCmd block:%s', pformat(agent_cfg, 2, 20), cmd_block)

    result,res_dict = _execute_config_snmp_cmd(zdcli, cmd_block)

    return result, res_dict

def _enable_snmp_trap(zdcli, cfg, version = 2):
    '''
    Enable snmp trap, set as snmpv2 or v3 based on version. 
    '''
    trap_cfg = cfg
    if version == 2:
        cmd_block = _construct_trap_cmd_v2(trap_cfg)
    else:
        cmd_block = _construct_trap_cmd_v3(trap_cfg)

    logging.info('Enable snmp trap:\nConfig:%s,\nCmd block:%s', pformat(trap_cfg, 2, 20), cmd_block)

    result,res_dict = _execute_config_snmp_cmd(zdcli, cmd_block)

    return result, res_dict

def _construct_agent_cmd_v2(cfg):
    '''
    Construct commands for enable snmp agent v2.
    '''
    cmd_block = CONFIG_SNMP_AGENT_V2_CMD_BLOCK
    cmd_block = cmd_block + Template(SET_AGENT_V2_RO_COMMUNITY).substitute(dict(ro_community = cfg['ro_community']))
    cmd_block = cmd_block + Template(SET_AGENT_V2_RW_COMMUNITY).substitute(dict(rw_community = cfg['rw_community']))
    cmd_block = cmd_block + Template(SET_AGENT_V2_CONTACT).substitute(dict(contact = cfg['contact']))
    cmd_block = cmd_block + Template(SET_AGENT_V2_LOCATION).substitute(dict(location = cfg['location']))

    cmd_block = cmd_block + SAVE_SERVER_CONFIG

    return cmd_block

def _construct_agent_cmd_v3(cfg):
    '''
    Construct commands for enable snmp agent v3.
    '''
    cmd_block = CONFIG_SNMP_AGENT_V3_CMD_BLOCK
    
    if cfg['ro_priv_protocol'].lower() == 'none':
        ro_priv_setting = 'None'
    else:
        ro_priv_setting = "%s '%s'" % (cfg['ro_priv_protocol'],cfg['ro_priv_passphrase'])
        
    if cfg['rw_priv_protocol'].lower() == 'none':
        rw_priv_setting = 'None'
    else:
        rw_priv_setting = "%s '%s'" % (cfg['rw_priv_protocol'],cfg['rw_priv_passphrase'])

    ro_user_cfg = dict (ro_sec_name = cfg['ro_sec_name'],
                   ro_auth_protocol = cfg['ro_auth_protocol'],
                   ro_auth_passphrase = cfg ['ro_auth_passphrase'],
                   ro_priv_setting = ro_priv_setting,
                   )
    rw_user_cfg = dict (rw_sec_name = cfg['rw_sec_name'],
                   rw_auth_protocol = cfg['rw_auth_protocol'],
                   rw_auth_passphrase = cfg ['rw_auth_passphrase'],
                   rw_priv_setting = rw_priv_setting,
                   )

    cmd_block = cmd_block + Template(SET_AGENT_V3_RO_USER).substitute(ro_user_cfg)
    cmd_block = cmd_block + Template(SET_AGENT_V3_RW_USER).substitute(rw_user_cfg)

    cmd_block = cmd_block + SAVE_SERVER_CONFIG

    return cmd_block


def _construct_trap_cmd_v2(cfg):
    '''
    Construct commands for enable snmp trap for v2.
    '''
    cmd_block = CONFIG_SYSTEM
    cmd_block = cmd_block + SET_TRAP_V2_FORMAT
    
    for i in range(1,5):
        if cfg.has_key(str(i)):
            trap_cfg = cfg[str(i)]
            cmd_block = cmd_block + Template(SET_TRAP_V2_CONFIG).substitute(dict(number = str(i),
                                                                                 server_ip = trap_cfg['server_ip']))

    cmd_block = cmd_block + SAVE_SERVER_CONFIG

    return cmd_block

def _construct_trap_cmd_v3(cfg):
    '''
    Construct commands for enable snmp trap for v2.
    '''
    cmd_block = CONFIG_SYSTEM
    cmd_block = cmd_block + SET_TRAP_V3_FORMAT
    
    for i in range(1,5):
        if cfg.has_key(str(i)):
            trap_cfg = cfg[str(i)]
            
            if trap_cfg['priv_protocol'].lower() == 'none':
                priv_setting = 'None'
            else:
                priv_setting = "%s '%s'" % (trap_cfg['priv_protocol'],trap_cfg['priv_passphrase'])
        
            trap_v3_cfg = dict (number = str(i),
                                sec_name = trap_cfg['sec_name'],
                                server_ip = trap_cfg['server_ip'],
                                auth_protocol = trap_cfg['auth_protocol'],
                                auth_passphrase = trap_cfg['auth_passphrase'],
                                priv_setting = priv_setting,
                                )
            
            cmd_block = cmd_block + Template(SET_TRAP_V3_CONFIG).substitute(trap_v3_cfg)
        
    cmd_block = cmd_block + SAVE_SERVER_CONFIG
    
    return cmd_block

def _execute_config_snmp_cmd(zdcli, cmd_block):
    '''
    Execute the commands related to snmp configure.
    #Notes: result of command:    
    # for snmp trap: The SNMP trap settings have been updated.
    # For no snmpv3: The SNMP v3 agent settings have been updated.
    # For no snmpv2: The SNMP v2 agent settings have been updated.
    # For snmp trap setting: The command was executed successfully.
    # for enable snmp trap v3: The command was executed successfully.
    # for snmpv2,v3 agent: The SNMP v3 agent settings have been updated.\n Your changes have been saved.
    '''
    #result = True
    res = zdcli.do_cfg(cmd_block, print_out = True)
    
    result = False
    
    if res.has_key('exit'):        
        if "Your changes have been saved." in res['exit'][0]:
            save_succ = True
        else:
            save_succ = False
            
        cmd_exec_succ = True
        for key, res_list in res.items():
            key = key.strip().lower()
            if key and key not in ['config','system','snmpv2','snmpv3','exit','']:
                res_str = "".join(res_list)
                if not (res_str.find('settings have been updated.')>-1 or res_str.find('The command was executed successfully.')>-1 \
                        or res_str.find('settings have been deleted.')>-1):
                    cmd_exec_succ = False
                    logging.warning('Cmd=%s, Err=%s' % (key, res_str))
                    break;
        
        if save_succ and cmd_exec_succ:
            result = True
        else:
            result = False
    else:
        result = False
    
    if not result:
        logging.warning('Fail to execute commands in ZD CLI! Cmd block:\n%s\nResult:\n%s' % (cmd_block, res))

    return result, res


