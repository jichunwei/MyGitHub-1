'''
Author#jluh@ruckuswireless.com
date#2014-4-9
This file is used for email server information etc.
'''
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

import re
import logging
from string import Template
from pprint import pformat

CONFIG_EMAIL_SERVER_CMD_BLOCK = "email-server\n"


SHOW_EMAIL_SERVER_INFO_CMD_BLOCK = "show\n"

ENABLE_SERVER = 'enable\n'
SET_EMAIL_ADDR = "from '$email_addr'\n"
SET_SMTP_SERVER_NAME = "smtp-server-name '$smtp_server'\n"
SET_SMTP_SERVER_PORT = "smtp-server-port '$server_port'\n"
SET_SMTP_AUTH_NAME = "smtp-auth-name '$username'\n"
SET_SMTP_AUTH_PASSWORD = "smtp-auth-password '$password'\n"
SET_TLS_ENABLED = "tls-smtp-encryption tls\n"
SET_TLS_DISABLED = "no tls-smtp-encryption tls\n"
SET_STARTTLS_ENABLED = "tls-smtp-encryption starttls\n"
SET_STARTTLS_DISABLED = "no tls-smtp-encryption starttls\n"

SAVE_CONFIG= "exit\n"
#=============================================#
#             Access Methods            
#=============================================#
def get_email_server_info(zdcli):
    '''
    Go to config>>email_server,
    and show.
    Issue: after show email_server information, use exist to return,
    it will change email email_server to enabled.    
    Output:
    {'email_server Status': 'Enabled',
     'Email Address': 'cherry.cheng@ruckuswireless.com',
     'E-mail From': '',
     'Encryption Options': 'STARTTLS'/'TLS'/'None',
     'SMTP Authentication Password': '123456789',
     'SMTP Authentication Username': 'CherryTest7v3',
     'SMTP Server Name': 'CherryTest6v3',
     'SMTP Server Port': '587'
   }
    '''
    cmd_block = CONFIG_EMAIL_SERVER_CMD_BLOCK + SHOW_EMAIL_SERVER_INFO_CMD_BLOCK
    res = zdcli.do_cfg(cmd_block)    
    rr = output.parse(res['show'][0])
    rr = _parse_encrypt_options(rr)

    return rr

#===============================================#
#           Protected Constant
#===============================================#
#EMAIL_SERVER_INFO_SHOW = '''
#email_server
#'''

#===============================================#
#           Protected Method
#===============================================#


#Updated by jluh@20140410, just support from 9.8
def _parse_encrypt_options(email_server_info):
    '''
    Input:
    {'email_server': {'Status': 'Enabled',
               'Email Address': 'cherry.cheng@ruckuswireless.com',
               'E-mail From': '',
               'SMTP Encryption Options': {'TLS': 'Enabled',
                                           ['STARTTLS': 'Enabled']
                                          },
               'SMTP Authentication Password': '123456789',
               'SMTP Authentication Username': 'CherryTest7v3',
               'SMTP Server Name': 'CherryTest6v3',
               'SMTP Server Port': '587'
               }
    }
    Output:
    {'email_server Status': 'Enabled',
     'Email Address': 'cherry.cheng@ruckuswireless.com',
     'E-mail From': '',
     'Encryption Options': 'STARTTLS'/'TLS'/'None',
     'SMTP Authentication Password': '123456789',
     'SMTP Authentication Username': 'CherryTest7v3',
     'SMTP Server Name': 'CherryTest6v3',
     'SMTP Server Port': '587'
    }
    '''
    if email_server_info.get('email_server'):
        _info = email_server_info['email_server']
        _info['Email Server Status'] = _info.pop('Status')
    elif email_server_info.get('Email Server'):
        _info = email_server_info['Email Server']
    else:
        raise Exception("No found the email server info from the zd cli")
    
    #SMTP Encryption Options
    if _info.has_key('SMTP Encryption Options'):
        encrytion_options = _info.pop('SMTP Encryption Options')
        tls = encrytion_options['TLS']
        #when 'TLS' is disabled, 'STARTTLS' doesn't show in ZD CLI.
        starttls = encrytion_options.get('STARTTLS')
        
        _opts = 'None'
        if tls == 'Enabled' and starttls == 'Enabled':
            _opts = 'STARTTLS'
        
        elif tls == 'Enabled':
            _opts  = 'TLS'
            
        _info['Encryption Options'] = _opts
        
        #Modified by liang aihua on 2014-9-16 for alignment error, which cause no return value.
        #return _info
    return _info
    
def set_email_server_info(zdcli,conf):
    cmd_block = _construct_configure_email_server_cmd_block(conf)
 
    logging.info('Configure email server with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True

def _construct_configure_email_server_cmd_block(cfg):  
    '''
    Input:
        cfg = {'email_addr': '',#from_server
               'smtp_server': '',
               'server_port': '',
               'username': '',
               'password': '',
               'tls_option': True/False,
               'starttls_option': True/False
               }
    '''    
    cmd_block = CONFIG_EMAIL_SERVER_CMD_BLOCK
    cmd_block += ENABLE_SERVER
    if cfg['email_addr']:
        cmd_block += Template(SET_EMAIL_ADDR).substitute(dict(email_addr = cfg['email_addr']))
    
    if cfg['smtp_server']:
        cmd_block += Template(SET_SMTP_SERVER_NAME).substitute(dict(smtp_server = cfg['smtp_server']))
    
    if cfg.has_key('server_name')and cfg['server_name']:
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