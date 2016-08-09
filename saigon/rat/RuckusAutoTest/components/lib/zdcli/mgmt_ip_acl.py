# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This module supports to do the functions under ruckus(config-mgmt-acl) and ruckus(config-mgmt-ipv6-acl).
mode of ZDCLI:

Commands available for :
  no mgmt-acl <WORD>   Deletes a management ACL for IP.
  mgmt-acl <WORD>      Creates a management ACL for IP.


Commands available:
  name <WORD>          Sets the management ACL name.
  restrict-type single ip-addr <IP-ADDR>
                       Sets the management ACL IP address.
  restrict-type range ip-range <IP-ADDR> <IP-ADDR>
                       Sets the a range for management acl IP address. Use a space ( ) to separate
                       Min. IP address and Max. IP address.
  restrict-type subnet ip-subnet <IP-ADDR> <IP-SUBNET>
                       Sets the subnet for management acl IP address. Use a space ( ) to separate IP
                       address and the Netmask(128.0.0.0 to 255.255.255.252).
                       
  restrict-type single ipv6-addr
                       Sets the management ACL IPv6 address.
  restrict-type prefix ipv6-addr <IPv6-ADDR> [<Prefix>]
                       Sets the a range for management acl IP address. Use a space ( )
  show                 Shows the management ACL.
  
  
  


"""

import logging
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common.utils import compare_dict_key_value

#
# GLOBAL DEFINATION
#
CONFIG_SYSTEM = 'system\n'
SAVE_COMMAND = 'exit\n'

SHOW_MGMT_ACL_ALL = 'show mgmt-acl all'
SHOW_MGMT_ACL_NAME = 'show mgmt-acl name "$name"'
DEL_MGMT_ACL_NAME = 'no mgmt-acl name "$name"'

ENTER_MGMT_ACL_CONFIG = 'mgmt-acl "$name"'
SET_MGMT_ACL_NAME = 'name "$name"'
SET_MGMT_ACL_TYPE_SINGLE = 'restrict-type single ip-addr $ip_addr'
SET_MGMT_ACL_TYPE_RANGE = 'restrict-type range ip-range $ip_addr $ip_addr_2'
SET_MGMT_ACL_SUBNET = 'restrict-type subnet ip-subnet $ip_addr $subnet'

#For management ipv6 acl.
SHOW_MGMT_IPV6_ACL_ALL = 'show mgmt-acl-ipv6 all'
SHOW_MGMT_IPV6_ACL_NAME = 'show mgmt-acl-ipv6 name "$name"'
DEL_MGMT_IPV6_ACL_NAME = 'no mgmt-acl-ipv6 name "$name"'

ENTER_MGMT_IPV6_ACL_CONFIG = 'mgmt-acl-ipv6 "$name"'
SET_MGMT_IPV6_ACL_NAME = 'name "$name"'
SET_MGMT_IPV6_ACL_TYPE_SINGLE = 'restrict-type single ipv6-addr $ip_addr'
SET_MGMT_IPV6_ACL_PREFIX = 'restrict-type prefix ipv6-addr $ip_addr $prefix'



setting_success_msg = ['Changes are saved!', '']

########################################################################################
# PUBLIC SECSSION
########################################################################################
def config_mgmt_acl(zdcli, **kwargs):
    """
    Create or edit a acl.
    {'name': 'mgmt ip acl name',
     'new_name': new name for ip acl.
    'type': 'single|range|subnet,
    'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',  
    }
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    logging.info("Create acl %s" % option)
    cmd_block = _define_mgmt_ip_acl_cmd_block(option)
    zdcli.do_cfg(cmd_block)

def create_multi_mgmt_acls(zdcli, acl_cfg_list):
    '''
    Create multi mgmt acls.
    '''
    err_dict = {}
    logging.info("Create multi acls: %s" % acl_cfg_list)
    for acl_cfg in acl_cfg_list:
        res, msg = config_mgmt_acl(zdcli, **acl_cfg)
        if res != 1:
            err_dict[acl_cfg['name']] = msg
            
    return err_dict

def delete_a_mgmt_acl(zdcli, name):
    '''
    Delete a mgmt acl based on name.
    '''
    cmd_block = CONFIG_SYSTEM
    cmd_block += Template(DEL_MGMT_ACL_NAME).substitute(dict(name = name))
    cmd_block += '\n'
    
    zdcli.do_cfg(cmd_block)
    
def show_all_mgmt_acl(zdcli):
    """
    """
    res = zdcli.do_show(SHOW_MGMT_ACL_ALL)
    res = output.parse(res)
    acl_conf = {}
    for key in res.keys():
        acl_conf[key.lower().replace(' ', '_')] = _read_acl_conf(res[key])
    
    acl_conf = _convert_cli_mgmt_acl_dict(acl_conf)        
            
    return acl_conf

def show_mgmt_acl_by_name(zdcli, name):
    cmd = Template(SHOW_MGMT_ACL_NAME).substitute(dict(name = name))
    
    res = zdcli.do_show(cmd)
    res = output.parse(res)
    acl_conf = {}
    for key in res.keys():
        acl_conf[key.lower().replace(' ', '_')] = _read_acl_conf(res[key])
        
    acl_conf = _convert_cli_mgmt_acl_dict(acl_conf)        
            
    return acl_conf
    
#Management ipv6 acl methods.
def config_mgmt_acl_ipv6(zdcli, **kwargs):
    """
    Create or edit a acl.
    {'name': 'mgmt ip acl name',
     'new_name': new name for ip acl.
    'type': 'single|range|subnet,
    'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',  
    }
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    logging.info("Create ipv6 acl %s" % option)
    cmd_block = _define_mgmt_ipv6_acl_cmd_block(option)
    res = zdcli.do_cfg(cmd_block, raw = True)
    
    result = True
    err_list = []
    #Verify error message.\
    err_msg_list = ['invalid', 'fail', 'error']
    if res and type(res) == dict:
        for cmd, res_list in res.items():
            res_str = str(res_list)
            for err_msg in err_msg_list:
                if err_msg in res_str:
                    result = False
                    err_list.append("Cmd=%s, Error=%s" % (cmd, res_str))
    else:
        err_list.append(res)
    
    if err_list:
        logging.debug(err_list)
                                
    return result, str(err_list)

def create_multi_mgmt_acls_ipv6(zdcli, acl_cfg_list):
    '''
    Create multi mgmt acls.
    '''
    err_dict = {}
    logging.info("Create multi ipv6 acls: %s" % acl_cfg_list)
    for acl_cfg in acl_cfg_list:
        result, err_msg = config_mgmt_acl_ipv6(zdcli, **acl_cfg)
        
        if not result:
            err_dict[acl_cfg['name']] = err_msg
            
    return err_dict

def delete_a_mgmt_acl_ipv6(zdcli, name):
    '''
    Delete a mgmt acl based on name.
    '''
    cmd_block = CONFIG_SYSTEM
    cmd_block += Template(DEL_MGMT_IPV6_ACL_NAME).substitute(dict(name = name))
    cmd_block += '\n'
    
    zdcli.do_cfg(cmd_block)
    
def show_all_mgmt_acl_ipv6(zdcli):
    """
    """
    res = zdcli.do_show(SHOW_MGMT_IPV6_ACL_ALL)
    res = output.parse(res)
    acl_conf = {}
    for key in res.keys():
        acl_conf[key.lower().replace(' ', '_')] = _read_acl_conf(res[key])
        
    acl_conf = _convert_cli_mgmt_acl_dict(acl_conf)
        
    return acl_conf

def show_mgmt_acl_by_name_ipv6(zdcli, name):
    cmd = Template(SHOW_MGMT_IPV6_ACL_NAME).substitute(dict(name = name))
    
    res = zdcli.do_show(cmd)
    res = output.parse(res)
    acl_conf = {}
    for key in res.keys():
        acl_conf[key.lower().replace(' ', '_')] = _read_acl_conf(res[key])
            
    acl_conf = _convert_cli_mgmt_acl_dict(acl_conf)
    
    return acl_conf

def compare_mgmt_ipv6_acl_cli_set_get(set_acl_list, get_acl_list):
    set_ipv6_dict = _convert_list_to_dict(set_acl_list, 'name')
    get_ipv6_dict = _convert_list_to_dict(get_acl_list, 'name')
    
    set_get_keys_mapping = {'addr': 'ipv6_address',
                            'type': 'restriction_type'}
    
    for key, acl_cfg in set_ipv6_dict.items():
        if acl_cfg.has_key('addr'):
            acl_cfg['addr'] = acl_cfg['addr'].replace(' / ', '/')
        set_ipv6_dict[key] = _convert_dict_with_new_keys(acl_cfg, set_get_keys_mapping)
            
    res = compare_dict_key_value(set_ipv6_dict, get_ipv6_dict)
    
    return res

def compare_mgmt_ipv6_acl_gui_cli_get(gui_get_acl_list,cli_get_acl_list):
    cli_get_acl_dict = _convert_list_to_dict(cli_get_acl_list, 'name')
    gui_get_acl_dict = _convert_list_to_dict(gui_get_acl_list, 'name')
    
    cli_gui_keys_mapping = {'ipv6_address': 'ipv6_addr'}
    
    for key, acl_cfg in cli_get_acl_dict.items():
        if acl_cfg.has_key('restriction_type'):
            acl_cfg.pop('restriction_type')
        if acl_cfg.has_key('ipv6_address'):
            acl_cfg['ipv6_address'] = acl_cfg['ipv6_address'].replace('/', ' / ')
        cli_get_acl_dict[key] = _convert_dict_with_new_keys(acl_cfg, cli_gui_keys_mapping)
    
    res = compare_dict_key_value(gui_get_acl_dict, cli_get_acl_dict)
    
    
    return res

########################################################################################
# PRIVATE SECSSION
########################################################################################

def _read_acl_conf(conf):
    if type(conf) is not dict:
        return conf
    
    if type(conf) is dict:
        res_conf = {}
        rules = []
        
        if conf.keys() and type(conf[conf.keys()[0]]) is list:
            for idx in range(len(conf[conf.keys()[0]])):
                rule = {}
                for key1 in conf.keys():
                    rule[key1.lower().replace(' ', '_')] = conf[key1][idx]
                rules.append(rule)
            res_conf = rules
        else:
            for key in conf.keys():
                res_conf[key.lower().replace(' ', '_')] = _read_acl_conf(conf[key])
                    
    return res_conf
    

def _define_mgmt_ip_acl_cmd_block(acl_cfg):
    """
           {'name': 'mgmt ip acl name',
            'type': 'single|range|subnet,
            'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',  
            }
    """
    cmd_block = CONFIG_SYSTEM
    
    cmd_block += Template(ENTER_MGMT_ACL_CONFIG).substitute(dict(name = acl_cfg['name']))
    cmd_block += '\n'
    
    if acl_cfg.has_key('new_name'):
        cmd_block += Template(SET_MGMT_ACL_NAME).substitute(dict(name = acl_cfg['new_name']))
        cmd_block += '\n'
        
    if acl_cfg.has_key('type'):
        type = acl_cfg['type'].lower()
        
        if type == 'single':
            ip_addr = acl_cfg['addr']
            cmd_block += Template(SET_MGMT_ACL_TYPE_SINGLE).substitute(dict(ip_addr = ip_addr))
        elif type == 'range':
            addrs = acl_cfg['addr'].split('-')
            range_addr1 = addrs[0].strip()
            range_addr2 = addrs[1].strip()
            cmd_block += Template(SET_MGMT_ACL_TYPE_RANGE).substitute(dict(ip_addr = range_addr1, 
                                                                          ip_addr_2 = range_addr2))
        elif type == 'subnet':
            addrs = acl_cfg['addr'].split('/')
            subnet_addr1 = addrs[0].strip()
            subnet_addr2 = addrs[1].strip()
            cmd_block += Template(SET_MGMT_ACL_SUBNET).substitute(dict(ip_addr = subnet_addr1, subnet = subnet_addr2))
            
        cmd_block += '\n'
    
    cmd_block += SAVE_COMMAND
    
    return cmd_block

def _define_mgmt_ipv6_acl_cmd_block(acl_cfg):
    """
           {'name': 'mgmt ip acl name',
            'type': 'single|range|subnet,
            'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',  
            }
    """
    cmd_block = CONFIG_SYSTEM
    
    cmd_block += Template(ENTER_MGMT_IPV6_ACL_CONFIG).substitute(dict(name = acl_cfg['name']))
    cmd_block += '\n'
    
    if acl_cfg.has_key('new_name'):
        cmd_block += Template(SET_MGMT_IPV6_ACL_NAME).substitute(dict(name = acl_cfg['new_name']))
        cmd_block += '\n'
        
    if acl_cfg.has_key('type'):
        type = acl_cfg['type'].lower()
        
        if type == 'single':
            ip_addr = acl_cfg['addr']
            cmd_block += Template(SET_MGMT_IPV6_ACL_TYPE_SINGLE).substitute(dict(ip_addr = ip_addr))
        elif type == 'prefix':
            addrs = acl_cfg['addr'].split('/')
            subnet_addr1 = addrs[0].strip()
            subnet_addr2 = addrs[1].strip()
            cmd_block += Template(SET_MGMT_IPV6_ACL_PREFIX).substitute(dict(ip_addr = subnet_addr1, prefix = subnet_addr2))
            
        cmd_block += '\n'
    
    cmd_block += SAVE_COMMAND
    
    return cmd_block

def _convert_list_to_dict(cfg_list, key_name):
    '''
    Convert dict list to a dict, will use cfg key_name value as key.
    '''     
    cfg_dict = {}
    
    for cfg in cfg_list:
        cfg_dict[cfg[key_name]] = cfg
    
    return cfg_dict

def _convert_dict_with_new_keys(org_dict, keys_mapping):
    '''
    Convert dict replace key with new key based on keys_mapping.
    '''
    new_dict = {}
    
    if keys_mapping:
        for key, value in org_dict.items():
            if keys_mapping.has_key(key):
                new_key = keys_mapping[key]
            else:
                new_key = key
                
            new_dict[new_key] = value
    else:
        new_dict = org_dict
        
    return new_dict

def _convert_cli_mgmt_acl_dict(cli_get_info):
    '''
    Output of CLI(cli_get_info):
    {'management_acl_for_ipv6': [{'ipv6_address': '2020:db8:1::10',
                              'name': 'allowtestengine',
                              'restriction_type': 'single'},
                             {'ipv6_address': '2020:db8:1::251',
                              'name': 'allowsingleip',
                              'restriction_type': 'single'},
                             {'ipv6_address': '2020:db8:1::251',
                              'name': 'allowprefix',
                              'restriction_type': 'single'}]}

    {'management_acl_for_ipv6': {'ipv6_address': '2020:db8:1::10',
                                 'name': 'allowtestengine',
                                 'restriction_type': 'single'}}
                                 
    Return: 
            [{'ipv6_address': '2020:db8:1::10',
              'name': 'allowtestengine',
              'restriction_type': 'single'}]
        
    '''
    new_cli_mgmt_acl = {}
    if cli_get_info and cli_get_info.has_key('management_acl_for_ipv6'):
        mgmt_acl_cfg = cli_get_info['management_acl_for_ipv6']
        
        if type(mgmt_acl_cfg) == list:
            new_cli_mgmt_acl = mgmt_acl_cfg
        else:
            new_cli_mgmt_acl = [mgmt_acl_cfg]
    else:
        new_cli_mgmt_acl = cli_get_info
        
    return new_cli_mgmt_acl