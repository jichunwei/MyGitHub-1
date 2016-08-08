# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This module supports to do the functions under ruckus(config-hotspot)# and ruckus(config-wlan)#
mode of ZDCLI:

Commands available for ruckus(config-hotspot)#:
  no session-timeout   Disables Session Timeout.
  no idle-timeout      Disables Idle Timeout.
  no acct-server       Disables Accounting Server.
  no restrict-access-order {NUMBER}          Deletes a restrict access order.
  name {WORD}          Sets the Hotspot entry name.
  login-page {WORD}    Sets the Login Page Url.
  start-page original  Redirect to the URL that the user intends to visit..
  start-page url {WORD} Redirect to the following URL.
  session-timeout {NUMBER} Enables and Sets Session Timeout time.
  idle-timeout {NUMBER} Enables and Sets Idle Timeout time.
  auth-server local    Sets Authentication Server into 'Local Database'.
  auth-server name {WORD} Sets Authentication Server.
  auth-server name {WORD} no-mac-bypass Disables MAC authentication bypass(no redirection).
  auth-server name {WORD} mac-bypass Enables MAC authentication bypass(no redirection).
  acct-server {WORD}   Sets Accounting Server.
  acct-server {WORD} interim-update {NUMBER} Sets the time of Sending Interim-Update.
  location-id {WORD}   Sets Location ID.
  location-name {WORD} Sets Location Name.
  wall-garden url1 {WORD} Sets Wall Garden Url1.
  wall-garden url2 {WORD} Sets Wall Garden Url2.
  wall-garden url3 {WORD} Sets Wall Garden Url3.
  wall-garden url4 {WORD} Sets Wall Garden Url4.
  wall-garden url5 {WORD} Sets Wall Garden Url5.
  restrict-access-order {NUMBER}    Creates a new restrict access order or modifies an existing restrict access order.
  show                 Displays Hotspot settings.
  
Commands available for ruckus(config-hotspot-restrict-access)#:
  order {NUMBER}       Sets the Hotspot rule order.
  description {WORD}   Sets the Hotspot rule description.
  type allow           Sets the Hotspot rule type to 'allow'.
  type deny            Sets the Hotspot rule type to 'deny'.
  destination address {IP-ADDR/WORD} Sets the destination address of a Hotspot rule.
  destination port {NUMBER/WORD} Sets the destination port of a Hotspot rule.
  protocol {NUMBER/WORD} Sets the protocol of a Hotspot rule.

"""
import re
import logging
import traceback
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
#@author: chen.tao 2013-12-19, to fix bug ZF-6459
from RuckusAutoTest.components.lib.zdcli import aaa_servers as lib

#
# GLOBAL DEFINATION
#

go_to_config_hotspot_cmd = 'hotspot'
go_to_config_hotspot_restrict_access_cmd = 'restrict-access-order'
config_hotspot_cmd = {
    'name': 'name',
    'login_page_url': 'login-page',
    'start_page': 'start-page',
    'accounting_server': 'acct-server',
    'authentication_server': 'auth-server',
    #zj2013-1-6, ZF-6195 ZF-5976 idle-timeout change to 'grace-period'
    'idle_timeout': 'grace-period',
    'mac_bypass': False,
    'send_interim-update_time': 'interim-update',
    'location_id': 'location-id',
    'location_name': 'location-name',
    'session_timeout': 'session-timeout',
    'wall_garden_1': 'walled-garden 1',
    'wall_garden_2': 'walled-garden 2',
    'wall_garden_3': 'walled-garden 3',
    'wall_garden_4': 'walled-garden 4',
    'wall_garden_5': 'walled-garden 5',
    'isolation_per_ap': 'client-isolation isolation-on-ap',
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8
    'isolation_across_ap':'client-isolation isolation-on-subnet',
    'white_list':'whitelist name',
    }
 
config_hotspot_restrict_access_cmd = {
    'order': 'order',
    'description': 'description',
    'destination_address': 'destination address',
    'destination_port': 'destination port',
    'type': 'type',
    'protocol': 'protocol',
    }
 
delete_a_hotspot_restrict_access_cmd = 'no restrict-access-order'
delete_a_hotspot_cmd = 'no hotspot'
SHOW_ALL_HOTSPOT = "show hotspot"

#Add command for restricted access for ipv6.
go_to_config_hotspot_restrict_access_ipv6_cmd = 'restrict-access-order-ipv6'
delete_a_hotspot_restrict_access_ipv6_cmd = 'no restrict-access-order-ipv6'
config_hotspot_restrict_access_ipv6_cmd = {
    'order': 'order',
    'description': 'description',
    'destination_address': 'destination address',
    'destination_port': 'destination port',
    'type': 'type',
    'protocol': 'protocol',
    'icmp_type': 'icmpv6-type',
    }

go_to_config_walled_garden_cmd = 'walled-garden'
delete_a_walled_garden_cmd = 'no walled-garden'

CONST_KEY = {'title':'Hotspot',
             'name':'Name',
             'id':'ID',
             }

default_hs_name = "Hotsport_Default"


########################################################################################
# PUBLIC SECSSION
########################################################################################
def _adapter_between_gui_and_cli(conf):
    if (not conf.get('login_page_url')) and conf.get('login_page'):
        conf['login_page_url'] = conf['login_page']

    if (not conf.get('authentication_server')):
        if conf.get('auth_svr'):
            conf['authentication_server'] = conf['auth_svr']
        else:
            conf['authentication_server'] = 'Local Database'

    if (not conf.get('accounting_server')):
        if conf.get('acct_svr'):
            conf['accounting_server'] = conf['acct_svr']
        else:
            conf['accounting_server'] = 'Disabled'

    if (not conf.get('send_interim-update_time')) and conf.get('interim_update_interval'):
        conf['send_interim-update_time'] = conf['interim_update_interval']

    if (not conf.get('location_id')) and conf.get('radius_location_id'):
        conf['location_id'] = conf['radius_location_id']

    if (not conf.get('location_name')) and conf.get('radius_location_name'):
        conf['location_name'] = conf['radius_location_name']

    if (not conf.get('mac_bypass')) and conf.get('enable_mac_auth'):
        conf['mac_bypass'] = conf['enable_mac_auth']

    if conf.get('session_timeout') is None:
        conf['session_timeout'] = 'Disabled'

    if conf.get('idle_timeout') is None:
        conf['idle_timeout'] = 'Disabled'

def config_hotspot(zdcli, **kwargs):
    """
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    _adapter_between_gui_and_cli(option)
    #@author: chen.tao 2013-12-19, to fix bug ZF-6459
    all_aaa_servers = lib.get_all_aaa_servers(zdcli)
    target_server = {}
    is_radius_server = False
    if all_aaa_servers and all_aaa_servers.has_key('AAA'):
        aaa = all_aaa_servers['AAA']
        id = aaa['ID']
        svr_list = id.values()
        for server in svr_list:
            if server['Name'] == option.get('auth_svr'):
                target_server = server
                break
            else:
                continue
    if target_server:
        if target_server['Type'] == 'RADIUS server':
            is_radius_server = True 
    option['is_radius_server'] = is_radius_server
    #@author: chen.tao 2013-12-19, to fix bug ZF-6459
    cmd_block = _define_hotspot_cmd_block(option)
    zdcli.do_cfg(cmd_block)
    
    if option.get('walled_garden_list'):
        #delete all existing items first
        info = show_config_hotspot(zdcli, option['name'])
        idx = info['hotspot']['id'].keys()[0]
        
        exist_item_len = 0
        for i in info['hotspot']['id'][idx].keys():
            if 'walled_garden' in i:
                exist_item_len += 1
        
        for j in range(0, exist_item_len):
            delete_a_walled_garden(zdcli, option['name'], (j+1))

        #add new items
        new_len = len(option['walled_garden_list'])
        for k in range(0, new_len):
            param = {'walled_garden_item': option['walled_garden_list'][k]} 
            config_hotspot_walled_garden(zdcli, option['name'], (k+1), **param)

    if option.get('restricted_subnet_list'):
        #delete all existing items first
        info = show_config_hotspot(zdcli, option['name'])
        idx = info['hotspot']['id'].keys()[0]

        exist_dict_len = 0
        if info['hotspot']['id'][idx].has_key('ipv4_rules'):
            exist_dict_len = len(info['hotspot']['id'][idx]['ipv4_rules'])

        for i in range(0, exist_dict_len):
            delete_a_hotspot_restrict_access(zdcli, option['name'], '1')
        
        #add new items
        new_len = len(option['restricted_subnet_list'])
        for j in range(0, new_len):
                if type(option['restricted_subnet_list'][j])is dict:
                    param = option['restricted_subnet_list'][j]
                else:
                    param = {'destination_address': option['restricted_subnet_list'][j],
                        'description': 'subnet%s' % (j+1)}
                config_hotspot_restrict_access(zdcli, option['name'], (j+1), **param)
        #Modified by Liang Aihua on 2014-9-12 for bug zf-10012
         #else:
         #   for j in range(0, new_len):
         #       param = option['restricted_subnet_list'][j]
         #       config_hotspot_restrict_access(zdcli, option['name'], (j+1), **param)
                            
    #added by jluh 2013-12-31        
    if option.get('restricted_ipv6_list'):
        #delete all ipv6 restricted existing items first
        info = show_config_hotspot(zdcli, option['name'])
        idx = info['hotspot']['id'].keys()[0]

        exist_dict_len = 0
        if info['hotspot']['id'][idx].has_key('ipv6_rules'):
            exist_dict_len = len(info['hotspot']['id'][idx]['ipv6_rules'])

        for i in range(0, exist_dict_len):
            delete_a_hotspot_restrict_access_ipv6(zdcli, option['name'], '1')
            
        #added the newly items
        for v6_j in range(len(option['restricted_ipv6_list'])):             
            config_hotspot_restrict_access_ipv6(zdcli, option['name'], (v6_j+1), 
                                                **option['restricted_ipv6_list'][v6_j])           
            

def config_hotspot_walled_garden(zdcli, hotspot_name, order_id, **kwargs):
    """
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    cmd_block = "%s '%s'\n%s %s %s\n" % (go_to_config_hotspot_cmd, hotspot_name,
                                    go_to_config_walled_garden_cmd, order_id, option['walled_garden_item'])
    zdcli.do_cfg(cmd_block)

def config_hotspot_restrict_access(zdcli, hotspot_name, order_id, **kwargs):
    """
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    for key in option:
        cmd_block = _define_hotspot_restrict_access_cmd_block(hotspot_name, order_id, key, option)
        if cmd_block:
            zdcli.do_cfg(cmd_block)


def show_all_hotspots(zdcli):
    cmd_block = SHOW_ALL_HOTSPOT
    data = zdcli.do_cfg(cmd_block, raw=True)    
    data = data.get(SHOW_ALL_HOTSPOT)[0]
    _dd = output.parse(data)
    return _dd


def delete_all_hotspots(zdcli):
    try:
        hotspotinfo = show_all_hotspots(zdcli)
        if not hotspotinfo or not hotspotinfo.get(CONST_KEY['title']):
            return

        if CONST_KEY['title'] in hotspotinfo:            
            profiles = hotspotinfo[CONST_KEY['title']][CONST_KEY['id']]
        else:
            return

    except IndexError:
        logging.warning(traceback.format_exc())
        return
    except KeyError:
        logging.warning(traceback.format_exc())
        return 
    
    cmd_block = ""
    for id, profile in profiles.items():       
        name = profile[CONST_KEY['name']]
        cmd_block += "%s '%s'\n" % (delete_a_hotspot_cmd, name) 

    zdcli.do_cfg(cmd_block)


def delete_a_hotspot(zdcli, name):
    cmd_block = "%s '%s'\n" % (delete_a_hotspot_cmd, name)
    
    zdcli.do_cfg(cmd_block)
    

def delete_a_hotspot_restrict_access(zdcli, hotspot_name, order):
    cmd_block = "%s '%s'\n%s %s\n" % (go_to_config_hotspot_cmd, hotspot_name, delete_a_hotspot_restrict_access_cmd, order)
    
    zdcli.do_cfg(cmd_block)
    
def delete_a_walled_garden(zdcli, hotspot_name, order):
    cmd_block = "%s '%s'\n%s %s\n" % (go_to_config_hotspot_cmd, hotspot_name, delete_a_walled_garden_cmd, order)
    
    zdcli.do_cfg(cmd_block)

def show_config_hotspot(zdcli, hotspot_name, **kwargs):
    """
    """
    res = zdcli.do_cfg_show("%s '%s'" % (go_to_config_hotspot_cmd, hotspot_name))
    res = output.parse(res)
    hotspot_conf = {}
    for key in res.keys():
        hotspot_conf[key.lower().replace(' ', '_')] = _read_hotspot_conf(res[key])        
            
    return hotspot_conf

def show_all_hotspot(zdcli):
    res = zdcli.do_show('hotspot all')
    res = output.parse(res)
    hotspot_conf = {}
    for key in res.keys():
        hotspot_conf[key.lower().replace(' ', '_')] = _read_hotspot_conf(res[key])        
            
    return hotspot_conf

def get_expected_hotspot_config_info(zdcli, hotspot_name):
    res = show_config_hotspot(zdcli, hotspot_name)
    _dd = res['hotspot']['id']
    for _tt in _dd.values():
        if _tt['name'] == hotspot_name:
            return _tt

    raise Exception("Not found hotspot %s" % hotspot_name)

    
########################################################################################
# PRIVATE SECSSION
########################################################################################
def _read_hotspot_conf(conf):
    if type(conf) is not dict:
        return conf
    
    if type(conf) is dict:
        res_conf = {}
        rules = []
        
        if conf.keys() and type(conf[conf.keys()[0]]) is list:
            for idx in range(len(conf[conf.keys()[0]])):
                print idx
                rule = {}
                for key1 in conf.keys():
                    rule[key1.lower().replace(' ', '_')] = conf[key1][idx]
                rules.append(rule)
            res_conf = rules
        else:
            for key in conf.keys():
                res_conf[key.lower().replace(' ', '_')] = _read_hotspot_conf(conf[key])
                    
    return res_conf

def _define_hotspot_cmd_block(option):
    cmd_block = ''
    if option.get('name'):
        cmd_block = "%s '%s'\n" % (go_to_config_hotspot_cmd, option['name'])
    else:
        cmd_block = "%s '%s'\n" % (go_to_config_hotspot_cmd, default_hs_name)
    
    if option.get('start_page'):
        if option['start_page'] == 'redirect to the URL that the user intends to visit.':
            cmd_block += '%s original\n' % config_hotspot_cmd['start_page']
        else:
            cmd_block += '%s url %s\n' % (config_hotspot_cmd['start_page'],
                                          option['start_page'])
     
    if option.get('authentication_server') == 'Local Database':
        cmd_block += '%s local\n' % config_hotspot_cmd['authentication_server']
    #@author: chen.tao 2013-12-19, to fix bug ZF-6459
    # jluh updated by 2013-11-01
    #elif option.get('authentication_server') and option.get('authentication_server_type') \
    #    and option['authentication_server_type'] == 'RADIUS':
    elif option.get('authentication_server') and option['is_radius_server']:
    #@author: chen.tao 2013-12-19, to fix bug ZF-6459
        if option.get('mac_bypass'):
            #@author: chentao since 2013-10-11 to adapt the mac bypass mac-addr-format in 9.8
            cmd_block += '%s name %s mac-bypass\n' % (config_hotspot_cmd['authentication_server'], 
                                                    option['authentication_server'])
            if option.get('mac_bypass_password') is not None:
                cmd_block += '%s name %s mac-bypass password %s\n' % (config_hotspot_cmd['authentication_server'], 
                                                              option['authentication_server'], option['mac_bypass_password'])
            else:
                cmd_block += '%s name %s mac-bypass mac\n' % (config_hotspot_cmd['authentication_server'], 
                                                              option['authentication_server'])
            if option.get('mac_bypass_format') is not None: #802.1X
                if option.get('mac_addr_format') is not None:
                    mac_addr_format = option['mac_addr_format']
                else:
                    mac_addr_format = "AA-BB-CC-DD-EE-FF"    
                cmd_block += '%s name %s mac-bypass  mac-addr-format %s\n' % (config_hotspot_cmd['authentication_server'], 
                                                                              option['authentication_server'],mac_addr_format)
            #@author: chentao since 2013-10-11 to adapt the mac bypass mac-addr-format in 9.8
        else:
            cmd_block += '%s name %s no-mac-bypass\n' % (config_hotspot_cmd['authentication_server'], 
                                                         option['authentication_server'])
    else:
        cmd_block += "%s name '%s'\n" % (config_hotspot_cmd['authentication_server'], 
                                                         option['authentication_server'])
    
    if option.get('accounting_server') and option.get('send_interim-update_time'):
        cmd_block += '%s "%s" interim-update %s\n' % (config_hotspot_cmd['accounting_server'],
                                                    option['accounting_server'],
                                                    option['send_interim-update_time'])
#@author: chentao since 2013-10-11 Some scripts use acc_svr instead of accounting_server        
    elif option.get('acct_svr'):
        cmd_block += '%s "%s"\n' % (config_hotspot_cmd['accounting_server'],
                                                    option['acct_svr'])
#@author: chentao since 2013-10-11 Some scripts use acc_svr instead of accounting_server          
    elif option.get('accounting_server') == 'Disabled':
        cmd_block += 'no %s\n' % config_hotspot_cmd['accounting_server']
    
    if option.get('session_timeout') == 'Disabled':
        cmd_block += 'no %s\n' % config_hotspot_cmd['session_timeout']
    elif option.get('session_timeout'):
        cmd_block += '%s %s\n' % (config_hotspot_cmd['session_timeout'], option['session_timeout'])
    #@author: chen.tao 2013-12-19, to fix bug ZF-6195
    #zj2013-1-6, ZF-6195 ZF-5976 idle-timeout change to 'grace-period'
    #if option.get('idle_timeout') == 'Disabled':
    #    cmd_block += 'no %s\n' % config_hotspot_cmd['idle_timeout']
    #elif option.get('idle_timeout'):
    #    cmd_block += '%s %s\n' % (config_hotspot_cmd['idle_timeout'], option['idle_timeout'])
    #@author: chen.tao 2013-12-19, to fix bug ZF-6195
    
    #@author: chen.tao 2013-12-19, to fix bug ZF-6767
    if not option.get('idle_timeout'):
        cmd_block += 'no %s\n' % config_hotspot_cmd['idle_timeout']
    elif option.get('idle_timeout'):
        if option.get('idle_timeout') == 'Disabled':
            cmd_block += 'no %s\n' % config_hotspot_cmd['idle_timeout']
        else : 
            cmd_block += '%s %s\n' % (config_hotspot_cmd['idle_timeout'], option['idle_timeout'])
    #@author: chen.tao 2013-12-19, to fix bug ZF-6767
    for key in ['login_page_url', 'location_id', 'location_name', 
                'wall_garden_1', 'wall_garden_2', 'wall_garden_3', 'wall_garden_4', 'wall_garden_5']:
        if option.get(key):
            cmd_block += '%s "%s"\n' % (config_hotspot_cmd[key], option[key])
    
    #@author: Jane.Guo @since: 2013-7-30 add for client isolation
    if option.get('isolation_per_ap'):
        if option['isolation_per_ap']:
            cmd_block += '%s enable\n' % config_hotspot_cmd['isolation_per_ap']
        else:
            cmd_block += '%s disable\n' % config_hotspot_cmd['isolation_per_ap']
    if option.get('isolation_across_ap'):
        if option['isolation_across_ap']:
            white_list = option.get('white_list')
            cmd_block += '%s enable\n' % config_hotspot_cmd['isolation_across_ap']
            cmd_block += '%s %s\n' % (config_hotspot_cmd['white_list'],white_list)
        else:
            cmd_block += '%s disable\n' % config_hotspot_cmd['isolation_across_ap']
 
    return cmd_block
 
def _define_hotspot_restrict_access_cmd_block(hotspot_name, order, key, option):
    cmd_block = "%s '%s'\n%s %s\n" % (go_to_config_hotspot_cmd, hotspot_name,
                                    go_to_config_hotspot_restrict_access_cmd, order)
    
    #if key == 'type':
        #value_to_set = option[key].lower()
    if key not in config_hotspot_restrict_access_cmd.keys():
        cmd_block = ''
    else:
        if key == 'type':
            value_to_set = option[key].lower()
        else:
            value_to_set = option[key]
        if key == 'description':
            cmd_block += '%s "%s"\n' % (config_hotspot_restrict_access_cmd[key], value_to_set)
        else:
            cmd_block += '%s %s\n' % (config_hotspot_restrict_access_cmd[key], value_to_set)
    return cmd_block
            
def _verify_execute_cmd_msg(return_info):
    """
    """
    error_cmd = []
    for cmd in return_info.keys():
        if return_info[cmd] not in setting_success_msg:
            error_cmd.append(cmd)
    
    if error_cmd:
        return (0, 'Below command\(s\)  %s did not execute successful' % error_cmd)
    return (1, 'All commands in block executed successfully')

#Add methods for configuration restricted ipv6 access.
def config_hotspot_restrict_access_ipv6(zdcli, hotspot_name, order_id, **kwargs):
    """
    Configure hotspot restricted ipv6 access list.
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    #added by jacky luh, since @2013-12-31
    option = {}
    if kwargs: option.update(kwargs)
    
    destination_address = ''
    type_v = ''
    
    if option.get('destination_addr'):
        destination_address = option['destination_addr']
    elif option.get('destination_address'):
        destination_address = option['destination_address']
            
    if option.get('action'):
        type_v = option['action']
    
    if destination_address:              
        option.update({'destination_address': destination_address})
        
    if type_v:
        option.update({'type': type_v})
    
    cmd_block = _define_hotspot_restrict_access_ipv6_cmd_block(hotspot_name, order_id, option)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    
    result = True
    err_list = []
    #Verify error message.\
    err_msg_list = ['invalid', 'fail', 'error', 'sorry']
    if res and type(res) == dict:
        for cmd, res_list in res.items():
            res_str = str(res_list)
            for err_msg in err_msg_list:
                if err_msg in res_str.lower():
                    result = False
                    err_list.append("Cmd=%s, Error=%s" % (cmd, res_str))
    else:
        err_list.append(res)
    
    if err_list:
        logging.debug(err_list)
                                
    return result, str(err_list)

def delete_a_hotspot_restrict_access_ipv6(zdcli, hotspot_name, order):
    cmd_block = "%s '%s'\n%s %s\n" % (go_to_config_hotspot_cmd, hotspot_name, delete_a_hotspot_restrict_access_ipv6_cmd, order)
    
    zdcli.do_cfg(cmd_block)
    
def compare_hotspot_restrict_ipv6_gui_cli_get(gui_get_acl_list, cli_get_acl):
    res_dict = {}
    
    gui_get_acl = _convert_list_to_dict(gui_get_acl_list, 'order')
    
    cli_gui_keys_mapping = {'destination_address': 'destination_addr',
                            'icmpv6_type': 'icmp_type',
                            'type': 'action',
                            }
    
    if len(gui_get_acl) != len(cli_get_acl):
        res_dict['Count'] = "GUI get: %s, CLI get: %s" % (len(gui_get_acl), len(cli_get_acl))
    else:
        gui_get_keys = gui_get_acl.keys().sort()
        cli_get_keys = cli_get_acl.keys().sort()
        
        if gui_get_keys != cli_get_keys:
            res_dict['Keys'] = "GUI get: %s, CLI get: %s" % (gui_get_keys, cli_get_keys)
        else:
            for order, gui_rule in gui_get_acl.items():
                cli_rule = cli_get_acl[order]
                cli_rule = _convert_dict_with_new_keys(cli_rule, cli_gui_keys_mapping)
                res = _compare_ipv6_rule(gui_rule, cli_rule)
                
                if res:
                    res_dict[order] = res
    
    return res_dict

def compare_hotspot_restrict_ipv6_cli_set_get(cli_set_acl, cli_get_acl):
    res_dict = {}
    
    cli_set_acl = _convert_list_to_dict(cli_set_acl, 'order')
    
    cli_gui_keys_mapping = {'destination_address': 'destination_addr',
                            'icmpv6_type': 'icmp_type',
                            }
    
    if len(cli_set_acl) != len(cli_get_acl):
        res_dict['Count'] = "CLI set: %s, CLI get: %s" % (len(cli_set_acl), len(cli_get_acl))
    else:
        cli_set_keys = cli_set_acl.keys().sort()
        cli_get_keys = cli_get_acl.keys().sort()
        
        if cli_set_keys != cli_get_keys:
            res_dict['Keys'] = "CLI set: %s, CLI get: %s" % (cli_set_keys, cli_get_keys)
        else:
            for order, set_rule in cli_set_acl.items():
                cli_rule = cli_get_acl[order]
                cli_rule = _convert_dict_with_new_keys(cli_rule, cli_gui_keys_mapping)
                res = _compare_ipv6_rule(set_rule, cli_rule)
                
                if res:
                    res_dict[order] = res
    
    return res_dict
    
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
        
def _compare_ipv6_rule(rule_dict_1, rule_dict_2):
    '''
    Compare two rule dicts. Protocol value may be ICMPv6 (58), will convert to 58.
    dict structure is 
        {'application': 'Any',
        'description': 'denytest1',
        'destination_addr': 'Any',
        'destination_port': 'Any',
        'icmp_type': 'Any',
        'order': '1',
        'protocol': 'Any',
        'type': 'Deny'}
    '''
    #Pop order and application if another dict no data.
    if rule_dict_1.has_key('order') and not rule_dict_2.has_key('order'):
        rule_dict_1.pop('order')
    elif rule_dict_2.has_key('order') and not rule_dict_1.has_key('order'):
        rule_dict_2.pop('order')
        
    if rule_dict_1.has_key('application') and not rule_dict_2.has_key('application'):
        rule_dict_1.pop('application')
    elif rule_dict_2.has_key('application') and not rule_dict_1.has_key('application'):
        rule_dict_2.pop('application')
        
    dict_1_keys = rule_dict_1.keys().sort()
    dict_2_keys = rule_dict_2.keys().sort()
    
    res_rule = {}
    if dict_1_keys != dict_2_keys:
        res_rule['Keys'] = "Dict 1: %s, Dict 2: %s" % (dict_1_keys, dict_2_keys)
    else:
        for key, value in rule_dict_1.items():
            value_2 = rule_dict_2.get(key)
            if key.lower() == 'protocol':
                pattern = '.*\((?P<value>[0-9]+)\)'
                matcher = re.compile(pattern).match(value_2)
                if matcher:
                    value_2 = matcher.groupdict()['value']                    
                    
                matcher = re.compile(pattern).match(value)
                if matcher:
                    value = matcher.groupdict()['value']
                        
            if value and value_2 and str(value).lower() != str(value_2).lower():
                fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                res_rule[key] = fail_msg
            elif value != value_2:
                fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                res_rule[key] = fail_msg
    
    if res_rule:
        return "Rule is different: %s" % res_rule
    else:
        return "" 

def _define_hotspot_restrict_access_ipv6_cmd_block(hotspot_name, order, option):
    '''
    Generate hotspot restricted ipv6 access command block.
    '''
    cmd_block = "%s '%s'\n%s %s\n" % (go_to_config_hotspot_cmd, hotspot_name,
                                    go_to_config_hotspot_restrict_access_ipv6_cmd, order)
    
    for key in option.keys():
        if config_hotspot_restrict_access_ipv6_cmd.has_key(key):
            value_to_set = option[key]
            cmd_line = config_hotspot_restrict_access_ipv6_cmd[key]
            if key in ['destination_address','destination_port','protocol','icmp_type']:
                #Only "Any" is valid for this item.
                value_to_set = value_to_set.capitalize()
            if key == 'icmp_type' and option['protocol'] == '58' and value_to_set.lower() != 'any':
                #icmp_type can be edit only when protocol is ICMPV6(58).
                cmd_line = cmd_line + ' number'
            
            if value_to_set.lower() == 'any':  
                temp_cmd = '%s %s\n'
            else:
                temp_cmd = "%s '%s'\n"
                
            cmd_block += temp_cmd % (cmd_line, value_to_set)
            
    return cmd_block     

feature_update = {
    '9.5.0.0': {
        'config_hotspot_cmd': {
            'idle_timeout': 'grace-period',
            }}
    }
