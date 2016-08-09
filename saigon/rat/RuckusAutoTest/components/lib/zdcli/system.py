'''
Handler for system setting.
    for example:
        hostname <system-name>
Created on 2012-7-4
@author: cwang@ruckuswireless.com
'''
import logging
import traceback
from pprint import pformat

from string import Template

from RuckusAutoTest.components.lib.zdcli import email_server_info
from RuckusAutoTest.components.lib.zdcli import output_as_dict as parser
#Command predefined.
SET_SYSTEM_NAME = """
system
hostname '$sys_name'
"""
DOT11_COUNTRY_CODE = """
system
dot11-country-code '$countrycode'    
"""
DOT11_COUNTRY_CODE_CHANNEL_MODE_INDOOR = """
system
dot11-country-code '$countrycode' channel-mode allow-indoor
"""
SHOW_COUNTRY_CODE = """
system
show
"""

CONFIG_EMAIL_SERVER_CMD_BLOCK = '''
email-server
'''
#Add by Liang Aihua on 2014-9-25 for behavior change: if you want to configure email-server, you should enable it first.
SET_EMAIL_SERVER_ENABLE = "enable\n"

SET_FROM_EMAIL_ADDR = "from '$from_email_addr'\n"
SET_SMTP_SERVER_NAME = "smtp-server-name '$smtp_server'\n"
SET_SMTP_SERVER_PORT = "smtp-server-port '$server_port'\n"
SET_SMTP_AUTH_NAME = "smtp-auth-name '$username'\n"
SET_SMTP_AUTH_PASSWORD = "smtp-auth-password '$password'\n"
SET_TLS_ENABLED = "tls-smtp-encryption tls\n"
SET_TLS_DISABLED = "no tls-smtp-encryption tls\n"
SET_STARTTLS_ENABLED = "tls-smtp-encryption starttls\n"
SET_STARTTLS_DISABLED = "no tls-smtp-encryption starttls\n"

EMAIL_SERVER_KEY_MAP = {'email_addr': 'Email Address',
                        'from_email_addr': 'E-mail From',
                        'smtp_server': 'SMTP Server Name',
                        'server_port': 'SMTP Server Port',
                        'username': 'SMTP Authentication Username',
                        'password': 'SMTP Authentication Password'
                        }

SAVE_CONFIG= "exit\n"

SAVE_SYSTEM_CONFIG = "end\n"

def set_system_name(zdcli, sys_name="Ruckus"):
    try:
        cmd = Template(SET_SYSTEM_NAME).substitute(dict(sys_name=sys_name))
        cmd += SAVE_SYSTEM_CONFIG
        zdcli.do_cfg(cmd)
    except:
        logging.warning(traceback.format_exc())
        msg = '[System name %s could not be set via CLI]' % sys_name        
        raise Exception(msg)


def default_system_name(zdcli):
    set_system_name(zdcli, sys_name="Ruckus")


def dot11_country_code(zdcli, cc="US"):
    try:
        cmd = Template(DOT11_COUNTRY_CODE).substitute(dict(countrycode=cc))
        cmd += SAVE_SYSTEM_CONFIG
        zdcli.do_cfg(cmd)
    except:
        logging.warning(traceback.format_exc())
        msg = '[countrycode %s could not be set via CLI]' % cc        
        raise Exception(msg)
#@ZJ 20150813 ZF-14166   
def dot11_country_code_channel_mode_indoor(zdcli, cc="US"):
    try:
        cmd = Template(DOT11_COUNTRY_CODE_CHANNEL_MODE_INDOOR).substitute(dict(countrycode=cc))
        cmd += SAVE_SYSTEM_CONFIG
        zdcli.do_cfg(cmd)
    except:
        logging.warning(traceback.format_exc())
        msg = '[countrycode %s could not be set via CLI]' % cc        
        raise Exception(msg)   
#@ZJ 20150813 ZF-14166
     
def get_country_code(zdcli):
    """
    {'Bonjour Service': {'Status': 'Enabled'},
     'Country Code': {'Code': 'Bahrain'},
     'FTP Server': {'Anonynous Status': 'Enabled', 'Status': 'Enabled'},
     'FlexMaster': {'Address': '', 'Interval': '15', 'Status': 'Disabled'},
     'Identity': {'Name': 'Ruckus'},
     'Log': {'AP Facility': '',
             'AP Priority': '',
             'Address': '',
             'Facility': '',
             'Priority': '',
             'Status': 'Disabled'},
     'NTP': {'Address': 'ntp.ruckuswireless.com', 'Status': 'Enabled'},
     'Telnet Server': {'Status': 'Disabled'},
     'Tunnel MTU': {'Tunnel MTU': '1500'}}
    """
    try:
        cmd = SHOW_COUNTRY_CODE
        cmd += SAVE_SYSTEM_CONFIG
        data = zdcli.do_cfg_show(cmd)
        _dd = parser.parse(data)
        return _dd['Country Code']['Code']        
    except Exception, e:
        logging.warning(traceback.format_exc())
        raise Exception("Can not do show system command")
    
    
def set_email_server(zdcli, email_cfg):
    '''
    Input: a dict of the alarm configuration.
    '''     
    conf = {'from_email_addr': '',
            'email_addr': '',
            'smtp_server': '',
            'server_port': '',
            'username': '',
            'password': '',
            'tls_option': False, 
            'starttls_option': False}
    conf.update(email_cfg)
    logging.info('Configure email server in ZD CLI with cfg:\n%s' % pformat(email_cfg, 4, 120))
    value = _set_email_server(zdcli, conf)
    if not value:
        return (False, 'Fail to configure email server in ZD CLI!')
    
    res, msg = _verify_email_server_cfg_in_cli(zdcli, conf)
    if res:
        return (True, 'Configure email server in ZD CLI successfully!')
    
    else:
        return (False, msg)
    
    
def _set_email_server(zdcli, cfg):  
    cmd_block = _construct_configure_email_server_cmd_block(cfg)
    logging.info('Configure alarm with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True


def _verify_email_server_cfg_in_cli(zdcli, cfg):
    '''
    Input:
        cfg = {'from_email_addr': '',
               'email_addr': '',
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
    '''
    cli_info = email_server_info.get_email_server_info(zdcli)
    logging.info("The email server information in ZD CLI is: %s" % pformat(cli_info, 4, 120))
    
    expect_info = _define_expect_cli_info(cfg)
    logging.info("The expect email server information in ZD CLI is: %s" % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, cli_info)


def _construct_configure_email_server_cmd_block(cfg):  
    '''
    Input:
        cfg = {'from_email_addr': '',
               'email_addr': '',
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
    ''' 
    
    cmd_block = CONFIG_EMAIL_SERVER_CMD_BLOCK
    cmd_block += SET_EMAIL_SERVER_ENABLE

    if cfg['from_email_addr']:
        cmd_block += Template(SET_FROM_EMAIL_ADDR).substitute(dict(from_email_addr = cfg['from_email_addr']))
    
    if cfg['server_name']:
        cmd_block += Template(SET_SMTP_SERVER_NAME).substitute(dict(smtp_server = cfg['server_name']))
    
    if cfg['server_port']:
        cmd_block += Template(SET_SMTP_SERVER_PORT).substitute(dict(server_port = cfg['server_port']))
    
    if cfg['username']:
        cmd_block += Template(SET_SMTP_AUTH_NAME).substitute(dict(username = cfg['username']))
    
    if cfg['password']:
        cmd_block += Template(SET_SMTP_AUTH_PASSWORD).substitute(dict(password = cfg['password']))   
    
    if cfg['tls_option'] == True:
        cmd_block += SET_TLS_ENABLED
    
    elif cfg['tls_option'] == False:
        cmd_block += SET_TLS_DISABLED
    
    if cfg['starttls_option'] == True:
        cmd_block += SET_STARTTLS_ENABLED
    
    elif cfg['tls_option'] == False:
        cmd_block += SET_STARTTLS_DISABLED

    cmd_block += SAVE_CONFIG
    
    return cmd_block


def _define_expect_cli_info(cfg):
    '''
    Input:
        cfg = {'from_email_addr': '',
               'email_addr': '',
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
               
    Output:
        info = {'FROM Email Address': '',
                'Email Address': '',
                'SMTP Server Name': '',
                'SMTP Server Port': ''
                'SMTP Authentication Username': '',
                'SMTP Authentication Password': '',
                'Encryption Options': 'STARTTLS'/'TLS'/'None'
                }
    '''
    info = dict()
    for key in cfg:
        if key in EMAIL_SERVER_KEY_MAP and cfg[key]:
            info[EMAIL_SERVER_KEY_MAP[key]] = cfg[key]
            
    if cfg['tls_option'] and cfg['starttls_option']:
        info['Encryption Options'] = 'STARTTLS'
    
    elif cfg['tls_option']:
        info['Encryption Options'] = 'TLS'
    
    else:
        info['Encryption Options'] = 'None'
    
    return info


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
        if key in EMAIL_SERVER_KEY_MAP and cli_cfg_dict[key]:
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



        