'''
@author: serena.tan@ruckuswireless.com
'''

import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import alarm_info
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.components.lib.zdcli import email_server_info  
    
CONFIG_ALARM_CMD_BLOCK = '''
alarm
'''
SET_ALARM_EMAIL_ADDR = "e-mail '$email_addr'\n"
SET_ALARM_SMTP_SERVER_NAME = "smtp-server-name '$smtp_server'\n"
SET_ALARM_SMTP_SERVER_PORT = "smtp-server-port '$server_port'\n"
SET_ALARM_SMTP_AUTH_NAME = "smtp-auth-name '$username'\n"
SET_ALARM_SMTP_AUTH_PASSWORD = "smtp-auth-password '$password'\n"
SET_ALARM_TLS_ENABLED = "tls-smtp-encryption tls\n"
SET_ALARM_TLS_DISABLED = "no tls-smtp-encryption tls\n"
SET_ALARM_STARTTLS_ENABLED = "tls-smtp-encryption starttls\n"
SET_ALARM_STARTTLS_DISABLED = "no tls-smtp-encryption starttls\n"

SAVE_CONFIG= "exit\n"

ALARM_KEY_MAP = {'email_addr': 'Email Address',
                 'smtp_server': 'SMTP Server Name',
                 'server_port': 'SMTP Server Port',
                 'username': 'SMTP Authentication Username',
                 'password': 'SMTP Authentication Password'
                 }

CONFIG_ALARM_EVENT_CMD_BLOCK='''
alarm-event
'''
ENABLE_ALARM_EVENT="event '$event_name'\n"
DISABLE_ALARM_EVENT="no event '$event_name'\n"
SHOW_ALARM_EVENT="show"
    
#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 

def configure_alarm(zdcli, alarm_cfg):
    '''
    Input: a dict of the alarm configuration.
    '''     
    conf = {'email_addr': 'lab@example.net',
            'smtp_server': '192.168.0.252',
            'server_port': '25',
            'username': '',
            'password': '',
            'tls_option': False, 
            'starttls_option': False}
    conf.update(alarm_cfg)
    logging.info('Configure alarm in ZD CLI with cfg:\n%s' % pformat(alarm_cfg, 4, 120))
    value = _set_alarm(zdcli, conf)
    value_set_email= email_server_info.set_email_server_info(zdcli, conf)
    if not value:
        return (False, 'Fail to configure alarm in ZD CLI!')
    if not value_set_email:
        return (False, 'Fail to configure email server in ZD CLI!')

    res, msg = _verify_alarm_cfg_in_cli(zdcli, conf)
    res_set_email, msg_set_email = _verify_email_server_cfg_in_cli(zdcli, conf)
    if res and res_set_email:
        return (True, 'Configure alarm and email server in ZD CLI successfully!')
    
    else:
        return (False, msg+msg_set_email)

def verify_cli_alarm_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    '''
    Input:
        cli_cfg_dict = {'email_addr': '',
                        'smtp_server': '',
                        'server_port': '',
                        'username': '',
                        'password': '',
                        'tls_option': True/False,
                        'starttls_option': True/False}
                        
        gui_info_dict = {'enabled': True/False,
                         'email_addr': '',
                         'smtp_server': '',
                         'server_port': '',
                         'username': '',
                         'password': '',
                         'encrypt': 'Starttls'/'tls'/'None'
                         }
    '''
    logging.info("The alarm information in ZD GUI is:\n %s" % pformat(gui_info_dict, 4, 120))
    
    expect_info_dict = _define_expect_gui_info(cli_cfg_dict)
    logging.info("The expect alarm information in ZD GUI is:\n %s" % pformat(expect_info_dict, 4, 120))
    logging.info('expect info %s'%expect_info_dict)
    logging.info('gui info %s'%gui_info_dict)
    res, msg = _expect_is_in_dict(expect_info_dict, gui_info_dict)
    if res:
        return (True, 'The alarm configuration in CLI is showed correctly in GUI!')
    
    else:
        return (False, msg)

def enable_alarm_event(zdcli,alarm_list):
    all_alarm_list=['all','rogue-ap-detected','rogue-device-detected','ap-lost-contacted',
                    'ssid-spoofing-ap-detected','mac-spoofing-ap-detected','rogue-dhcp-server-detected',
                    'temporary-license-expired','temporary-license-will-expire',
                    'lan-rogue-ap-detected','aaa-server-unreachable','ap-has-hardware-problem',
                    'sensor-has-problem','uplink-ap-lost','incomplete-primary/secondary-ip-settings',
                    'smart-redundancy-state-changed','smart-redundancy-state-changed',
                    'smart-redundancy-active-connected','smart-redundancy-standby-connected',
                    'smart-redundancy-active-disconnected','smart-redundancy-standby-disconnected']
    for event in alarm_list:
        if event not in all_alarm_list:
            msg='alarm %s not a recognizable event'%event
            logging.info(msg)
            return False,msg
        cmd_block = CONFIG_ALARM_EVENT_CMD_BLOCK+\
                    Template(ENABLE_ALARM_EVENT).substitute(dict(event_name = event))+\
                    SAVE_CONFIG
        logging.info('let us enable alarm event %s'%event)
        res = zdcli.do_cfg(cmd_block, raw = True)
        logging.info('cmd_block execution result:\n%s' % res)
    
        if "Your changes have been saved." not in res['exit'][0]:
            zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
            return False,"'Your changes have been saved.' not found in the returned str,when set event %s"%event
    return True,'all the event have been set successfully'


def disable_alarm_event(zdcli,alarm_list):
    all_alarm_list=['all','rogue-ap-detected','rogue-device-detected','ap-lost-contacted',
                    'ssid-spoofing-ap-detected','mac-spoofing-ap-detected','rogue-dhcp-server-detected',
                    'temporary-license-expired','temporary-license-will-expire',
                    'lan-rogue-ap-detected','aaa-server-unreachable','ap-has-hardware-problem',
                    'sensor-has-problem','uplink-ap-lost','incomplete-primary/secondary-ip-settings',
                    'smart-redundancy-state-changed','smart-redundancy-state-changed',
                    'smart-redundancy-active-connected','smart-redundancy-standby-connected',
                    'smart-redundancy-active-disconnected','smart-redundancy-standby-disconnected']
    for event in alarm_list:
        if event not in all_alarm_list:
            msg='alarm %s not a recognizable event'%event
            logging.info(msg)
            return False,msg
        cmd_block = CONFIG_ALARM_EVENT_CMD_BLOCK+\
                    Template(DISABLE_ALARM_EVENT).substitute(dict(event_name = event))+\
                    SAVE_CONFIG
        logging.info('let us disable alarm event %s'%event)
        res = zdcli.do_cfg(cmd_block, raw = True)
        logging.info('cmd_block execution result:\n%s' % res)
    
        if "Your changes have been saved." not in res['exit'][0]:
            zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
            return False,"'Your changes have been saved.' not found in the returned str,when set event %s"%event
    return True,'all the event have been set successfully'        

#input a list of event name,for example ['rogue-ap-detected','ap-lost-contacted','rogue-dhcp-server-detected']
#return a list of status according to the events in the input list,for example['enable','disable','enable']        
def get_alarm_event_status(zdcli,event_name_list):
    event_dictionary={'rogue-ap-detected':'MSG_rogue_AP_detected',
                      'rogue-device-detected':'MSG_ad_hoc_network_detected',
                      'ap-lost-contacted':'MSG_AP_lost',
                        'ssid-spoofing-ap-detected':'MSG_SSID_spoofing_AP_detected',
                        'mac-spoofing-ap-detected':'MSG_MAC_spoofing_AP_detected',
                        'rogue-dhcp-server-detected':'MSG_admin_rogue_dhcp_server',
                        'temporary-license-expired':'',
                        'temporary-license-will-expire':'MSG_admin_templic_oneday',
                        'lan-rogue-ap-detected':'MSG_lanrogue_AP_detected',
                        'aaa-server-unreachable':'MSG_RADIUS_service_outage',
                        'ap-has-hardware-problem':'MSG_AP_hardware_problem',
                        'sensor-has-problem':'',
                        'uplink-ap-lost':'MSG_AP_no_mesh_uplink',
                        'incomplete-primary/secondary-ip-settings':'MSG_AP_keep_no_AC_cfg',
                        'smart-redundancy-state-changed':'MSG_cltr_change_to_active',
                        'smart-redundancy-active-connected':'MSG_cltr_active_connected',
                        'smart-redundancy-standby-connected':'MSG_cltr_standby_connected',
                        'smart-redundancy-active-disconnected':'MSG_cltr_active_disconnected',
                        'smart-redundancy-standby-disconnected':'MSG_cltr_standby_disconnected'}
    status_list=[]
    
    res = zdcli.do_cfg_show(CONFIG_ALARM_EVENT_CMD_BLOCK)    
    rr = output.parse(res)  
    for event_name in event_name_list:
        if event_name not in event_dictionary:
            msg='event %s not recognizable'%event_name
            logging.info(msg)
            raise(msg)
        event_str=event_dictionary[event_name]
        status=rr['Alarm Events Notify By Email'][event_str]
        status_list.append(status)
    return status_list

def all_alarm_event_disable(zdcli):    
    event_dictionary={'rogue-ap-detected':'MSG_rogue_AP_detected',
                      'rogue-device-detected':'MSG_ad_hoc_network_detected',
                      'ap-lost-contacted':'MSG_AP_lost',
                        'ssid-spoofing-ap-detected':'MSG_SSID_spoofing_AP_detected',
                        'mac-spoofing-ap-detected':'MSG_MAC_spoofing_AP_detected',
                        'rogue-dhcp-server-detected':'MSG_admin_rogue_dhcp_server',
                        'temporary-license-expired':'',
                        'temporary-license-will-expire':'MSG_admin_templic_oneday',
                        'lan-rogue-ap-detected':'MSG_lanrogue_AP_detected',
                        'aaa-server-unreachable':'MSG_RADIUS_service_outage',
                        'ap-has-hardware-problem':'MSG_AP_hardware_problem',
                        'sensor-has-problem':'',
                        'uplink-ap-lost':'MSG_AP_no_mesh_uplink',
                        'incomplete-primary/secondary-ip-settings':'MSG_AP_keep_no_AC_cfg',
                        'smart-redundancy-state-changed':'MSG_cltr_change_to_active',
                        'smart-redundancy-active-connected':'MSG_cltr_active_connected',
                        'smart-redundancy-standby-connected':'MSG_cltr_standby_connected',
                        'smart-redundancy-active-disconnected':'MSG_cltr_active_disconnected',
                        'smart-redundancy-standby-disconnected':'MSG_cltr_standby_disconnected'}
    res = zdcli.do_cfg_show(CONFIG_ALARM_EVENT_CMD_BLOCK)    
    rr = output.parse(res)
    for event_name in event_dictionary:
        event_str=event_dictionary[event_name]
        status=rr['Alarm Events Notify By Email'][event_str]
        if not status=='disabled':
            msg='event %s status is %s'%(event_name,status)
            logging.info(msg)
            return False
    return True

def all_alarm_event_enable(zdcli):    
    event_dictionary={'rogue-ap-detected':'MSG_rogue_AP_detected',
                      'rogue-device-detected':'MSG_ad_hoc_network_detected',
                      'ap-lost-contacted':'MSG_AP_lost',
                        'ssid-spoofing-ap-detected':'MSG_SSID_spoofing_AP_detected',
                        'mac-spoofing-ap-detected':'MSG_MAC_spoofing_AP_detected',
                        'rogue-dhcp-server-detected':'MSG_admin_rogue_dhcp_server',
                        'temporary-license-expired':'',
                        'temporary-license-will-expire':'MSG_admin_templic_oneday',
                        'lan-rogue-ap-detected':'MSG_lanrogue_AP_detected',
                        'aaa-server-unreachable':'MSG_RADIUS_service_outage',
                        'ap-has-hardware-problem':'MSG_AP_hardware_problem',
                        'sensor-has-problem':'',
                        'uplink-ap-lost':'MSG_AP_no_mesh_uplink',
                        'incomplete-primary/secondary-ip-settings':'MSG_AP_keep_no_AC_cfg',
                        'smart-redundancy-state-changed':'MSG_cltr_change_to_active',
                        'smart-redundancy-active-connected':'MSG_cltr_active_connected',
                        'smart-redundancy-standby-connected':'MSG_cltr_standby_connected',
                        'smart-redundancy-active-disconnected':'MSG_cltr_active_disconnected',
                        'smart-redundancy-standby-disconnected':'MSG_cltr_standby_disconnected'}
    res = zdcli.do_cfg_show(CONFIG_ALARM_EVENT_CMD_BLOCK)
    rr = output.parse(res)
    for event_name in event_dictionary:
        event_str=event_dictionary[event_name]
        status=rr['Alarm Events Notify By Email'][event_str]
        if not status=='enabled':
            msg='event %s status is %s'%(event_name,status)
            logging.info(msg)
            return False
    return True
#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 
    
def _set_alarm(zdcli, cfg):  
    cmd_block = _construct_configure_alarm_cmd_block(cfg)
    logging.info('Configure alarm with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True

def _verify_alarm_cfg_in_cli(zdcli, cfg):
    '''
    Input:
        cfg = {'email_addr': '',
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
    ''' 
    cli_info = alarm_info.get_alarm_info(zdcli)
    logging.info("The alarm information in ZD CLI is: %s" % pformat(cli_info, 4, 120))
    
    expect_info = _define_expect_cli_info(cfg)
    logging.info("The expect alarm information in ZD CLI is: %s" % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, cli_info)

def _construct_configure_alarm_cmd_block(cfg):  
    '''
    Input:
        cfg = {'email_addr': ''}
    '''    
    cmd_block = CONFIG_ALARM_CMD_BLOCK
    if cfg['email_addr']:
        cmd_block += Template(SET_ALARM_EMAIL_ADDR).substitute(dict(email_addr = cfg['email_addr']))

    cmd_block += SAVE_CONFIG
    
    return cmd_block

def _define_expect_cli_info(cfg):
    '''
    Input:
        cfg = {'email_addr': '',
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
               
    Output:
        info = {'Alarm Status': 'Enabled'/'Disabled',
                'Email Address': ''
                }
    '''
    info = dict()
    info['Email Address'] = cfg.get('email_addr')
    info['Alarm Status'] = 'Enabled'
    
    return info


def _define_expect_email_server_cli_info(cfg):
    info = dict()
    for key in cfg:
        if key in ALARM_KEY_MAP and cfg[key]:
            info[ALARM_KEY_MAP[key]] = cfg[key]
            
    if cfg['tls_option'] and cfg['starttls_option']:
        info['Encryption Options'] = 'STARTTLS'
    
    elif cfg['tls_option']:
        info['Encryption Options'] = 'TLS'
    
    else:
        info['Encryption Options'] = 'None'
        
    info['Email Server Status'] = 'Enabled'
    
    return info

def _verify_email_server_cfg_in_cli(zdcli, cfg):
    '''
    Input:
        cfg = {'email_addr': '',
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
    ''' 
    cli_info = email_server_info.get_email_server_info(zdcli)
    if cli_info.get('E-mail From'):
        cli_info['Email Address'] = cli_info.pop('E-mail From')
    if cli_info.get('Status'):
        cli_info['Email Server Status'] = cli_info.pop('Status')
    for key in cli_info.keys():
        if not cli_info[key]:
            cli_info.pop(key)
    logging.info("The email server information in ZD CLI is: %s" % pformat(cli_info, 4, 120))
    
    expect_info = _define_expect_email_server_cli_info(cfg)
    logging.info("The expect email server information in ZD CLI is: %s" % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, cli_info)

def _define_expect_gui_info(cli_cfg_dict):
    '''
    Input:
        cli_cfg_dict = {'email_addr': '',
                        'smtp_server': '',
                        'server_port': '',
                        'username': '',
                        'password': '',
                        'tls_option': True/False,
                        'starttls_option': True/False}
                        
    Output:
        expect_info = {'enabled': True/False,
                       'email_addr': '',
                       'smtp_server': '',
                       'server_port': '',
                       'username': '',
                       'password': '',
                       'encrypt': 'Starttls'/'tls'/'None'
                       }
    '''
    expect_info = {}
    for key in cli_cfg_dict:
        if key in ALARM_KEY_MAP and cli_cfg_dict[key]:
            expect_info[key] = cli_cfg_dict[key]
    
    if cli_cfg_dict.has_key('tls_option') and cli_cfg_dict['tls_option'] and cli_cfg_dict['starttls_option']:
        expect_info['encrypt'] = 'Starttls'
    
    elif cli_cfg_dict.has_key('tls_option') and cli_cfg_dict['tls_option']:
        expect_info['encrypt'] = 'tls'
    
    else:
        expect_info['encrypt'] = 'None'
    
    expect_info['enabled'] = True
            
    return expect_info


def _expect_is_in_dict(expect_dict, original_dict):
    expect_ks = expect_dict.keys()
    orignal_ks = original_dict.keys()
    for k in expect_ks:
        if k not in orignal_ks:
            return (False, 'The parameter [%s] does not exist in dict: %s' % (k, original_dict))
        
        if type(expect_dict[k]) is dict:
            res, msg = _expect_is_in_dict(expect_dict[k], original_dict[k])
            if not res:
                return (False, msg)
        
        elif k!='SMTP Authentication Password' and str(original_dict[k]) != str(expect_dict[k]):
            return (False, 'The value [%s] of parameter [%s] is not correct in dict: %s ' % (expect_dict[k], k, original_dict))         

    return (True, '')

