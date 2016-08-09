# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This module supports to do the functions under ruckus(config-guest-access)# and ruckus(config-guest-restrict-access)#
mode of ZDCLI:

Commands available for :
  no authentication    Disables Authentication.
  no term-of-use       Do not show terms of use.
  no restrict-access-order {NUMBER}
                       Deletes a restrict access order.
  authentication guest-pass shared Allow multiple users to share a single guest pass.
  authentication guest-pass no-shared Disallow multiple users to share a single guest pass.
  term-of-use {WORD}   Enables and Sets the terms of use.
  redirect original    Redirect to the URL that the user intends to visit.
  redirect url {WORD}  Redirect to the following URL.
  auth-server local    Sets the authentication server to 'Local Database'.
  auth-server name {WORD} Sets the authentication server to specifed name from AAA.
  guestpass-effective now Set Effective from the creation time.
  guestpass-effective first-use-expired {NUMBER} Effective from first use, Expire new guest passes if not used within xx days.
  welcome-text {WORD}  Sets the Title.
  show                 Displays Guest Access settings.
  restrict-access-order {NUMBER}
                       Creates a new restrict access order or modifies an existing restrict access
                       order.

Commands available:
  order {NUMBER}       Sets the Guest Access rule order.
  description {WORD}   Sets the Guest Access rule description.
  type allow           Sets the Guest Access rule type to 'allow'.
  type deny            Sets the Guest Access rule type to 'deny'.
  destination address {IP-ADDR/WORD} Sets the destination address of a Guest Access rule.
  destination port {NUMBER/WORD} Sets the destination port of a Guest Access rule.
  protocol {NUMBER/WORD} Sets the protocol of a Guest Access rule.

"""
import re
import logging
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#
# GLOBAL DEFINATION
#
go_to_config_guest_access_cmd = 'guest-access'
configure_guest_access_cmd = {
    'authentication': 'authentication',
    'terms_of_use': 'term-of-use',
    'redirection': 'redirect',
    'authentication_server': 'guest-access-auth-server',
    'validity_period': 'guest-access-guestpass-effective',
    'title': 'welcome-text',
    'restricted_subnet_access': 'restrict-access-order',
    'restricted_subnet_access_ipv6': 'restrict-access-order-ipv6',
    'self_service':'self-service',
    'guestpass_share_number':'guestpass-share-number',
    'guestpass_notification':'guestpass-notification',
    'guestpass_duration':'guestpass-duration day 1',
    'guestpass_terms_and_conditions':'guestpass-terms-and-conditions',
    'guestpass_sponsor':'guestpass-sponsor',
    'guestpass_sponsor_number':'guestpass-sponsor-number',
    'guestpass_sponsor_auth_server':'guestpass-sponsor-auth-server',
    'guestpass_reauth':'guestpass-reauth',
     }

go_to_config_guest_restrict_access_cmd = 'restrict-access-order'
delete_a_guest_restrict_access_cmd = 'no restrict-access-order'
configure_guest_restrict_access_cmd = {
    'order': 'order',
    'description': 'description',
    'type': 'type',
    'destination_address': 'destination address',
    'destination_port': 'destination port',
    'protocol': 'protocol'}

#Add command for restricted access for ipv6.
go_to_config_guest_restrict_access_ipv6_cmd = 'restrict-access-order-ipv6'
delete_a_guest_restrict_access_ipv6_cmd = 'no restrict-access-order-ipv6'
configure_guest_restrict_access_ipv6_cmd = {
    'order': 'order',
    'description': 'description',
    'action': 'type',
    'dst_addr': 'destination address',
    'dst_port': 'destination port',
    'protocol': 'protocol',
    'icmp_type': 'icmpv6-type',
    }

#author: Jacky.Luh @since: 2014-1-6
show_all_guest_service_profile_cmd = 'show guest-access-service'
delete_guest_service_profile_cmd = "no guest-access '%s'"

setting_success_msg = ['Changes are saved!', '']
#@author: Jane.Guo @since: 2013-09 adapt to 9.8 Guest Access improvement
default_gc_name = "Guest_Access_Default"

########################################################################################
# PUBLIC SECSSION
########################################################################################
def config_guest_access(zdcli, **kwargs):
    """
    """
    #@author: Tansx, @change: adapt to Behavior change of 9.10,9.12
    option = {'flag':''}
    if kwargs: option.update(kwargs)
    Version_info = zdcli.get_system_info()
    Version = Version_info['Version'][:4]
    option['Version'] = Version
    cmd_block = _define_guest_access_cmd_block(option)
    zdcli.do_cfg(cmd_block)
    
def config_guest_restrict_access(zdcli, order_id, **kwargs):
    """
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    cmd_block = _define_guest_restrict_access_cmd_block(order_id, option)
    zdcli.do_cfg(cmd_block)


def delete_all_guest_restrict_access(zdcli):
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 Guest Access improvement    
    cmd_block = 'no %s %s\n' % (go_to_config_guest_access_cmd,default_gc_name)
    zdcli.do_cfg(cmd_block)
#    ginfos = show_config_guest_access(zdcli)
#    v4restricted = ginfos['guest_access']['restricted_subnet_access']
##    v6restricted = ginfos['guest_access']['restricted_ipv6_access']
#    for order_id in v4restricted['rules'].keys():
#        if order_id=="1":
#            continue
#        else:
#            delete_a_guest_restrict_access(zdcli, order_id)

def default_guest_access_setting(zdcli):
     cfg = {#'authentication': 'No Authentication.',
            #@author: li.pingping@odc-ruckuswireless.com 2013.06.05 to set guest access policy as "Use guest pass authentication" when remove all configuration on ZD.
            'authentication': 'Use guest pass authentication.',
            'authentication_server': 'Local Database',
            'redirection': 'To the URL that the user intends to visit.',                 
            'terms_of_use': 'Disabled',
            'title': 'Welcome to the Guest Access login page.',
            'validity_period': 'Effective from the creation time.'}
     
     
     config_guest_access(zdcli, **cfg)



def delete_a_guest_restrict_access(zdcli, order):
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 Guest Access improvement  
    cmd_block = '%s %s\n%s %s\n' % (go_to_config_guest_access_cmd, default_gc_name, delete_a_guest_restrict_access_cmd, order)
    
    zdcli.do_cfg(cmd_block)
    
    
def show_config_guest_access(zdcli,guest_name=default_gc_name, **kwargs):
    """
    """
    #@author: yuyanan @since:2015-3-24 @change:9.10 new feature: show guest access according to guest name
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8 Guest Access improvement  
    res = zdcli.do_cfg_show('%s %s'%(go_to_config_guest_access_cmd,guest_name), raw=True)
    
    res = output.parse(res)
    guest_conf = _read_guest_conf_lower_keys(res)
            
    return guest_conf


def show_all_guest_access_name_list(zdcli):
    """
    """
    #@author: Jacky.Luh @since: 2014-1-6 added the function of show all guest access name
    cmd_block = show_all_guest_service_profile_cmd
    res = zdcli.do_cfg(cmd_block)[show_all_guest_service_profile_cmd][0]
    #@author: chen.tao @since 2015-02-12, to skip parsing TOU info.
    #because it will cause "data not in order" error, which was introduced by ZF-11793
    term_of_use_pos = res.find('\r\r\n    Terms =')
    if term_of_use_pos != -1:
        redirection_pos = res.find('\r\r\n  Redirection:')
        if redirection_pos > term_of_use_pos:
            res = res[:term_of_use_pos]+res[redirection_pos:]

    if res == 'Guest Access:':
        return []
     
    res = output.parse(res)['Guest Access']['Name']
    if type(res) is str:
        res = [res]
    
    return res


def delete_guest_access_profile(zdcli, guest_access_profile_name, checking=False, **kwargs):
    #@author: Jacky.Luh @since: 2014-1-6 added the function of delete one guest access name
    #if checking is True, the function will return True or False.
    cmd_block = delete_guest_service_profile_cmd % guest_access_profile_name
    zdcli.do_cfg(cmd_block)

    if checking:
        guest_name_list = show_all_guest_access_name_list(zdcli)
        if guest_access_profile_name not in guest_name_list:
            return True
        else:
            return False


def delete_all_guest_access_profiles(zdcli, checking=False, **kwargs):
    #@author: Jacky.Luh @since: 2014-1-6 added the function of delete all guest access name
    #if checking is True, the function will return True or False.
    guest_name_list = show_all_guest_access_name_list(zdcli)
    for guest_name in guest_name_list:
        delete_guest_access_profile(zdcli, guest_name)
        
    if checking:
        check_guest_name_list = show_all_guest_access_name_list(zdcli)
        if check_guest_name_list == []:
            return True
        else:
            return False


def get_restricted_access(zdcli):
    '''
    Get restricted_access[ipv4 and ipv6] from all guest access information.
    {'restricted_subnet_access': {},
     'restricted_ipv6_access': {}
    }
    Notes: When term-of-use is enabled, detail information is displayed in the result.
    dict of parsing is a little different.
    '''
    new_res_access_cfg = {}
    
    all_guest_access_info = show_config_guest_access(zdcli)
    
    if all_guest_access_info.has_key('restricted_ipv6_access'):
        new_res_access_cfg['restricted_ipv6_access'] = all_guest_access_info['restricted_ipv6_access']
    if all_guest_access_info.has_key('restricted_subnet_access'):
        new_res_access_cfg['restricted_subnet_access'] = all_guest_access_info['restricted_subnet_access']
     
    if all_guest_access_info.has_key('guest_access'):
        all_guest_access_info = all_guest_access_info['guest_access']
    
        if all_guest_access_info.has_key('restricted_ipv6_access'):
            new_res_access_cfg['restricted_ipv6_access'] = all_guest_access_info['restricted_ipv6_access']
            
        if all_guest_access_info.has_key('restricted_subnet_access'):
            res_access_cfgs = all_guest_access_info['restricted_subnet_access']
            if type(res_access_cfgs) == list:
                #In 9.3, has different structure for guest access restricted access list.
                for res_access_cfg_dict in res_access_cfgs:
                    if res_access_cfg_dict.has_key('Ipv4'):
                        new_res_access_cfg['restricted_subnet_access'] = res_access_cfg_dict['Ipv4'] 
                    if res_access_cfg_dict.has_key('Ipv6'):
                        new_res_access_cfg['restricted_ipv6_access'] = res_access_cfg_dict['Ipv6']
            else:
                if type(res_access_cfgs) == dict:
                    new_res_access_cfg['restricted_subnet_access'] = res_access_cfgs
            
    new_res_access_cfg = _read_guest_conf_lower_keys(new_res_access_cfg)
    return new_res_access_cfg

########################################################################################
# PRIVATE SECSSION
########################################################################################

def _read_guest_conf(conf):
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
                res_conf[key.lower().replace(' ', '_')] = _read_guest_conf(conf[key])
                    
    return res_conf
    

def _define_guest_access_cmd_block(option):
    """
    {'guest_access': {'authentication': 'No Authentication.',
                      'authentication_server': 'Local Database',
                      'redirection': 'To the URL that the user intends to visit.',                 
                      'terms_of_use': 'Disabled',
                      'title': 'Welcome to the Guest Access login page.',
                      'validity_period': 'Effective from the creation time.'
                      'self_service_registration':{'status':'Enabled',
                                                   'share_number':'1',
                                                   'duration':'1 days', #'guestpass-duration day 1',
                                                   're-auth_time': '5 mins', #guestpass-reauth min 5
                                                   'notification_method':'Device Screen', #Mobile,Email,Mobile and Email
                                                   'terms_and_conditions':'this is test',
                                                   'sponsor_approval':{'status':'Enabled',
                                                                        'sponsor_auth_server': 'Local Database', 
                                                                        'sponsor_number': '5'}
                                                   }
                      }
    }
    """
    #@author: Anzuo, @change: config auth-ser independently
    cmd_block = ''
    #@author: Tansx, @change: adapt to behavior change of 9.10,9.12
    version_list = ['9.10','9.12']
    Flag = option['flag']
    if option.get('Version') not in version_list:
        Flag = False
    else:
        Flag = True
    if  not Flag:
        if option.get('authentication_server'):
            if option['authentication_server'] == 'Local Database':
                cmd_block += '%s local\n' % configure_guest_access_cmd['authentication_server']
            else:
                cmd_block += '%s name "%s"\n' % (configure_guest_access_cmd['authentication_server'],
                                                 option['authentication_server'])
                                                             
        if option.get('validity_period') in ['Effective from first use.', 'Effective from first use'] and option.get('expire_days'):
            cmd_block += '%s first-use-expired %s\n' % (configure_guest_access_cmd['validity_period'],
                                                        option['expire_days'])
        elif option.get('validity_period') in ['Effective from the creation time.', 'Effective from the creation time']:
            cmd_block += '%s now\n' % configure_guest_access_cmd['validity_period']                    
                                                    
        if option.get('name'):
            cmd_block += '%s %s\n' % (go_to_config_guest_access_cmd,option.get('name'))
        else:
            cmd_block += '%s %s\n' % (go_to_config_guest_access_cmd,default_gc_name) 
        
    else:
        if option.get('authentication_server'):
            if option['authentication_server'] == 'Local Database':
                cmd_block += '%s local\n' % configure_guest_access_cmd['authentication_server']
            else:
                cmd_block += '%s name "%s"\n' % (configure_guest_access_cmd['authentication_server'],
                                                 option['authentication_server'])
        if option.get('name'):
            cmd_block += '%s %s\n' % (go_to_config_guest_access_cmd,option.get('name'))
        else:
            cmd_block += '%s %s\n' % (go_to_config_guest_access_cmd,default_gc_name)                                                      
        if option.get('validity_period') in ['Effective from first use.', 'Effective from first use'] and option.get('expire_days'):
            cmd_block += '%s first-use-expired %s\n' % (configure_guest_access_cmd['validity_period'],
                                                        option['expire_days'])
        elif option.get('validity_period') in ['Effective from the creation time.', 'Effective from the creation time']:
            cmd_block += '%s now\n' % configure_guest_access_cmd['validity_period']          
                                           
                                  
   
    #@author: Anzuo, @change: no default restrict subnet access
    list = range(5,2,-1)
    for i in list:
        cmd_block += 'no %s %s\n' % (configure_guest_access_cmd['restricted_subnet_access'], i)
        
    if option.get('authentication') in ['No Authentication.', 'No Authentication']:
        cmd_block += 'no %s\n' % configure_guest_access_cmd['authentication']
    elif option.get('authentication') in ['Use guest pass authentication.', 'Use guest pass authentication']:
        if option.get('multiple_users_to_share_a_single_guest_pass') == 'Allowed':
            cmd_block += '%s guest-pass shared\n' % configure_guest_access_cmd['authentication']
        else:
            cmd_block += '%s guest-pass no-shared\n' % configure_guest_access_cmd['authentication']
    
    #@author: Anzuo, @change: add "onboarding" option
    if option.get('onboarding') in ['key-and-zeroit', 'zeroit']:
        cmd_block += 'onboarding %s\n' % option.get('onboarding')
    else:
        cmd_block += 'no onboarding\n'
    
    if option.get('terms_of_use') == 'Enabled' and option.get('terms'):
        cmd_block += '%s "%s"\n' % (configure_guest_access_cmd['terms_of_use'], option['terms'])
    elif option.get('terms_of_use') == 'Disabled':
        cmd_block += 'no %s\n' % configure_guest_access_cmd['terms_of_use']
    
    if option.get('redirection') in ['To the URL that the user intends to visit.', 'To the URL that the user intends to visit']:
        cmd_block += '%s original\n' % configure_guest_access_cmd['redirection']
    elif option.get('redirection') in ['To the following URL.', 'To the following URL'] and option.get('url'):
        cmd_block += '%s url "%s"\n' % (configure_guest_access_cmd['redirection'], option['url'])
    
    if option.get('title'):
        cmd_block += '%s "%s"\n' % (configure_guest_access_cmd['title'], option['title'])
    
    if Flag:    
        #@author:yuyanan @since: 2014-12-22 @change:adapt to 9.10 self-service guestpass
        notification_map = {'Device Screen':'1','Mobile':'2','Email':'3','Mobile and Email':'4'}
        if option.get('self_service_registration'):
            self_param = option.get('self_service_registration')
            if self_param.get('status') == 'Enabled':
                cmd_block += '%s\n'%configure_guest_access_cmd['self_service']
            
                if self_param.get('share_number'):
                    cmd_block += '%s %s\n'%(configure_guest_access_cmd['guestpass_share_number'], self_param.get('share_number'))       
                else:
                    cmd_block += '%s 1\n'%configure_guest_access_cmd['guestpass_share_number']
                
                if self_param.get('notification_method'):
                    cmd_block += '%s %s\n'%(configure_guest_access_cmd['guestpass_notification'] ,notification_map[self_param.get('notification_method')])       
                else:
                    cmd_block += '%s 1\n'%configure_guest_access_cmd['guestpass_notification']
                
                if self_param.get('duration'):#'1 days' transfer to 'day 1'
                    duration_list = self_param.get('duration')[0:-1].split( )
                    duration = duration_list[1]+' '+duration_list[0]
                    cmd_block += 'guestpass-duration %s\n'%duration      
                else:
                    cmd_block += '%s\n'%configure_guest_access_cmd['guestpass_duration']
                   
                if self_param.get('sponsor_approval'):
                    if self_param.get('sponsor_approval').get('status') == 'Enabled': 
                        cmd_block += '%s\n'%configure_guest_access_cmd['guestpass_sponsor'] 
                
                        if self_param.get('sponsor_approval').get('sponsor_number'):
                            cmd_block += '%s %s\n'%(configure_guest_access_cmd['guestpass_sponsor_number'],self_param.get('sponsor_approval').get('sponsor_number'))
                    
                        if self_param.get('sponsor_approval').get('sponsor_auth_server'):
                            cmd_block += '%s name "%s"\n' % (configure_guest_access_cmd['guestpass_sponsor_auth_server'],self_param.get('sponsor_approval').get('sponsor_auth_server'))
                        else:
                            cmd_block += '%s local\n'% (configure_guest_access_cmd['guestpass_sponsor_auth_server'])
                    else:
                        cmd_block += 'no %s\n'%configure_guest_access_cmd['guestpass_sponsor']       
                      
                if self_param.get('terms_and_conditions'):
                    cmd_block += '%s "%s"\n' % (configure_guest_access_cmd['guestpass_terms_and_conditions'], self_param.get('terms_and_conditions'))
                else:
                    cmd_block += 'no %s\n'%configure_guest_access_cmd['guestpass_terms_and_conditions']
            
                if self_param.get('re-auth_time'):# 5 mins transfer to  min 5
                    reauth_list = self_param.get('re-auth_time')[0:-1].split( )
                    reauth = reauth_list[1]+' '+reauth_list[0]
                    cmd_block += '%s %s\n'%(configure_guest_access_cmd['guestpass_reauth'],reauth)
                else:
                    cmd_block += 'no %s\n'%configure_guest_access_cmd['guestpass_reauth']         
            else:#match if self_param.get('status') == 'Enabled':
                cmd_block += 'no %s\n'%configure_guest_access_cmd['self_service']
            #@author:yuyanan @since: 2014-12-22 @change:9.10 new feature

    logging.info(cmd_block)
    return cmd_block

def _define_guest_restrict_access_cmd_block(order, option):
    """
    'rules': [{'description': '',
               'destination_address': 'local',
               'destination_port': 'Any',
               'order': '1',
               'protocol': 'Any',
               'type': 'Deny'},]},
    """
    cmd_block = '%s %s\n%s %s\n' % (go_to_config_guest_access_cmd, default_gc_name, go_to_config_guest_restrict_access_cmd, order)
    
    for key in option.keys():
        if key == 'type':
            value_to_set = option[key].lower()
        if key not in configure_guest_restrict_access_cmd.keys():
            continue
        else:
            value_to_set = option[key]
        
        cmd_block += '%s \"%s\"\n' % (configure_guest_restrict_access_cmd[key],
                                    value_to_set)
    logging.info(cmd_block)
    return cmd_block

# Add methods for restrict guest access ipv6 list.
def config_guest_restrict_access_ipv6(zdcli, order_id, **kwargs):
    """
    """
    option = {}
    if kwargs: option.update(kwargs)
    
    cmd_block = _define_guest_restrict_access_ipv6_cmd_block(order_id, option)
    res = zdcli.do_cfg(cmd_block)
    
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
        
    return result, err_list
    
    
def delete_a_guest_restrict_access_ipv6(zdcli, order):
    cmd_block = '%s %s\n%s %s\n' % (go_to_config_guest_access_cmd, default_gc_name, delete_a_guest_restrict_access_ipv6_cmd, order)
    
    zdcli.do_cfg(cmd_block)
    
def verify_restricted_ipv6_access_cli_set_get(cli_set_access_list, cli_get_access_dict):
    '''
    Verify restricted ipv6 access list between gui get and cli get.
    '''
    res_access_list = {}
       
    cli_set_access_dict = _convert_list_to_dict(cli_set_access_list, 'order')
    
    if len(cli_set_access_dict) != len(cli_get_access_dict):
        res_access_list['Count'] = "CLI Set: %s, CLI Get: %s" % (len(cli_set_access_dict), len(cli_get_access_dict))
    else:
        for order_id, cli_set_access in cli_set_access_dict.items():
            cli_get_access = cli_get_access_dict[order_id]
            
            res_access = _compare_ipv6_rule(cli_set_access, cli_get_access)
            
            if res_access:
                res_access_list[order_id] = res_access
                
    return res_access_list
    
def verify_restricted_ipv6_access_gui_cli_get(gui_get_access_list, cli_get_access_dict):
    '''
    Verify restricted ipv6 access list between gui get and cli get.
    '''
    res_access_list = {}
    
    gui_get_access_dict = _convert_list_to_dict(gui_get_access_list, 'order')
    
    if len(gui_get_access_dict) != len(cli_get_access_dict):
        res_access_list['Count'] = "GUI Get:%s, CLI Get: %s" % (len(gui_get_access_dict), len(cli_get_access_dict))
    else:
        for order_id, gui_get_access in gui_get_access_dict.items():
            cli_get_access = cli_get_access_dict[order_id]
            
            res_access = _compare_ipv6_rule(gui_get_access, cli_get_access)
            
            if res_access:
                res_access_list[order_id] = res_access
                
    return res_access_list

def _convert_list_to_dict(cfg_list, key_name):
    '''
    Convert server cfg list to dict, key is server name.
    And convert keys to new keys.
    '''    
    cfg_dict = {}
    
     
    old_new_keys_mapping ={'dst_addr': 'destination_address',
                           'dst_port': 'destination_port',
                           'icmp_type': 'icmpv6_type',
                           'action': 'type',
                           }
    
    for cfg in cfg_list:
        new_cfg = {}
        for old_key, value in cfg.items():
            if old_new_keys_mapping.has_key(old_key):
                new_key = old_new_keys_mapping[old_key]
            else:
                new_key = old_key
            
            if old_key != 'order':
                new_cfg[new_key] = value
        
        cfg_dict[cfg[key_name]] = new_cfg
    
    return cfg_dict
        
def _compare_ipv6_rule(rule_dict_1, rule_dict_2):
    '''
    Compare rule.
    dict structure is 
        {'order': '', 'description': '', 'action': '', 
         'dst_addr': '', 'application': '', 'protocol': '', 
         'dst_port': '', 'icmp_type': ''}
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
    
def _define_guest_restrict_access_ipv6_cmd_block(order, option):
    """
    'rules': [{'description': '',
               'dst_addr': 'local',
               'dst_port': 'Any',
               'order': '1',
               'protocol': 'Any',
               'action': 'Deny',
               'icmp_type': 'Any'},]},
        
    For type, Deny/Allow and deny/allow can be accepted.
    For destination address, port and protocol, "Any" or number is accepted.    
    For icmp_type, set it as "Any" or number [icmpv6-type number <?>]
    """
    cmd_block = '%s %s\n%s %s\n' % (go_to_config_guest_access_cmd, default_gc_name, go_to_config_guest_restrict_access_ipv6_cmd, order)
    
    for key in option.keys():
        if configure_guest_restrict_access_ipv6_cmd.has_key(key):
            value_to_set = option[key]
            cmd_line = configure_guest_restrict_access_ipv6_cmd[key]
            if key in ['dst_addr','dst_port','protocol','icmp_type']:
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
                
    logging.info(cmd_block)
    return cmd_block

def _read_guest_conf_lower_keys(dict):
    '''
    Convert access configuration, lower all keys.
    '''
    new_dict = {}
    for key in dict.keys():
        new_dict[key.lower().replace(' ', '_')] = _read_guest_conf(dict[key])
        
    return new_dict
