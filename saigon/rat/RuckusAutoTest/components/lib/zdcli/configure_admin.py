'''
Created on 2011-3-2
@author: serena.tan@ruckuswireless.com
'''

import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import admin


CONFIG_ADMIN_CMD_BLOCK = '''
admin
'''
SET_ADMIN_NAME = "name '$admin_name'\n"
SET_ADMIN_PASSWORD = "name $admin_name password $admin_pass\n"
SET_NO_AUTH_SERVER = "no auth-server\n"
SET_AUTH_SERVER_WITHOUT_FALLBACK = "auth-server '$auth_server'\n"
SET_AUTH_SERVER_WITH_FALLBACK= "auth-server '$auth_server' with-fallback\n"
SAVE_ADMIN_CONFIG= "exit\n"

EXPECT_GUI_INFO_KEYS = ['admin_name', 'auth_method', 'auth_server', 'fallback_local']

#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 

def configure_admin(zdcli, admin_cfg):
    '''
    Input: a dict of the admin configuration:
           admin_name: admin name
           admin_pass: admin password
           auth_method: 'local'/'external'
           auth_server: name of the authenticate server, doesn't need when auth_method is 'local'
           fallback_local: True/False, doesn't need when auth_method is 'local'
    '''     
    conf = {'admin_name': '', 
            'admin_pass': '', 
            'auth_method': '',
            'auth_server': '', 
            'fallback_local': True
           }
    conf.update(admin_cfg)
    logging.info('Configure admin in ZD CLI with cfg:\n%s' % pformat(admin_cfg, 4, 120))
    value = _set_admin(zdcli, conf)
    if not value:
        return (False, 'Fail to configure admin in ZD CLI!')
    
    res, msg = _verify_admin_cfg_in_cli(zdcli, conf)
    if res:
        return (True, 'Configure admin in ZD CLI successfully!')
    
    else:
        return (False, msg)
    

def verify_cli_admin_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    '''
    cli_cfg_dict = {'admin_name': '',
                    'admin_pass': '',
                    'auth_method': 'local'/'external',
                    'auth_server': '',  #doesn't need when auth_method is 'local'
                    'fallback_local': True/False, #doesn't need when auth_method is 'local'
                    }
    gui_info_dict = {'admin_name': u'admin',
                     'admin_old_pass': '',
                     'admin_pass1': '',
                     'auth_method': 'local'/'external',
                     'auth_server': u'', #doesn't need when auth_method is 'local'
                     'fallback_local': True/False, #doesn't need when auth_method is 'local'
                    }
    '''
    expect_info_dict = _define_expect_gui_info(cli_cfg_dict)
        
    res, msg = _expect_is_in_dict(expect_info_dict, gui_info_dict)
    if res:
        return (True, 'The admin configuration in CLI is showed correctly in GUI!')
    
    else:
        return (False, msg)


#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 
    
def _set_admin(zdcli, cfg):  
    cmd_block = _construct_configure_admin_cmd_block(cfg)
    logging.info('Configure admin with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True


def _verify_admin_cfg_in_cli(zdcli, cfg):
    cli_info = admin.get_admin_info(zdcli)
    logging.info('The admin information in ZD CLI is:\n%s' % pformat(cli_info, 4, 120))
    expect_info = _define_expect_cli_info(cfg)
    logging.info('The expected admin information in ZD CLI is:\n%s' % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, cli_info)


def _construct_configure_admin_cmd_block(cfg):  
    '''
    Input:
        cfg = {'admin_name': '',
               'admin_pass': '',
               'auth_method': 'local'/'external',
               'auth_server': '',
               'fallback_local': True/False,
              }
    '''    
    cmd_block = CONFIG_ADMIN_CMD_BLOCK
    if cfg['admin_name']:
        if cfg['admin_pass']:
            cmd_block += Template(SET_ADMIN_PASSWORD).substitute(dict(admin_name = cfg['admin_name'], admin_pass = cfg['admin_pass']))
        
        else:
            cmd_block += Template(SET_ADMIN_NAME).substitute(dict(admin_name = cfg['admin_name']))
    
    if cfg['auth_method'] == 'local':
        cmd_block += SET_NO_AUTH_SERVER
    
    elif cfg['auth_method'] == 'external':
        if cfg['auth_server'] == '':
            raise Exception("")
        
        if cfg['fallback_local'] == False:
            cmd_block += Template(SET_AUTH_SERVER_WITHOUT_FALLBACK).substitute(dict(auth_server = cfg['auth_server']))
        
        else:
            cmd_block += Template(SET_AUTH_SERVER_WITH_FALLBACK).substitute(dict(auth_server = cfg['auth_server']))

    cmd_block += SAVE_ADMIN_CONFIG
    
    return cmd_block


def _define_expect_cli_info(cfg):
    '''
    Input:
    cfg = {'admin_name': '',
           'admin_pass': '',
           'auth_method': 'local'/'external',
           'auth_server': '',
           'fallback_local': True/False,
          }
    Output:
    info = {'Name': '',
            'Password': '',
            'Authenticate': {'Mode': "Authenticate using the admin name and password"
                                    /"Authenticate with authentication server ''",
                             ['Fallback': 'Enabled'/'Disabled']
                            }
           }
    '''
    info = dict()
    if cfg['admin_name']:
        info['Name'] = cfg['admin_name']
    
    if cfg['admin_pass']:
        info['Password'] = cfg['admin_pass']
        
    info['Authenticate'] = {}
    if cfg['auth_method'] == 'local':
        info['Authenticate']['Mode'] = "Authenticate using the admin name and password"
    
    elif cfg['auth_method'] == 'external':
        info['Authenticate']['Mode'] = "Authenticate with authentication server '%s'" % cfg['auth_server']
        if cfg['fallback_local'] == False:
            info['Authenticate']['Fallback'] = 'Disabled'
        
        else:
            info['Authenticate']['Fallback'] = 'Enabled'
    
    return info


def _define_expect_gui_info(cli_cfg_dict):
    expect_info = cli_cfg_dict
    keys = expect_info.keys()
    for k in keys:
        if k not in EXPECT_GUI_INFO_KEYS:
            expect_info.pop(k)
    
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
        
        elif original_dict[k] != expect_dict[k]:
            return (False, 'The value [%s] of parameter [%s] is not correct in dict: %s ' % (expect_dict[k], k, original_dict))         

    return (True, '')

