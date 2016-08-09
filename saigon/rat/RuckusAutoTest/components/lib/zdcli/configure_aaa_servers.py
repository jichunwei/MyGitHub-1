'''
Created on 2010-12-30
@author: serena.tan@ruckuswireless.com
'''

import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import aaa_servers


CONFIG_SERVER_CMD_BLOCK = '''
aaa '$server_name'
'''
SET_SERVER_NAME= "name '$new_server_name'\n"
SET_SERVER_TYPE= "type '$type'\n"
SET_SERVER_IP_ADDR= "ip-addr '$server_addr'\n"
SET_SERVER_PORT= "port '$server_port'\n"
SET_SERVER_WIN_DOMAIN_NAME= "domain-name '$win_domain_name'\n"
SET_SERVER_NO_GLOBAL_CATALOG= "no ad-global-catalog\n"
SET_SERVER_NO_BACKUP= "no backup\n"
SET_SERVER_GLOBAL_CATALOG= "ad-global-catalog\n"
SET_SERVER_ADMIN_DOMAIN_NAME= "admin-dn '$admin_domain_name'\n"
SET_SERVER_ADMIN_PASSWORD= "admin-password '$admin_password'\n"
SET_SERVER_LDAP_KEY_ATTRIBUTE= "key-attribute '$ldap_key_attribute'\n"
SET_SERVER_LDAP_SEARCH_FILTER= "search-filter '$ldap_search_filter'\n"
SET_SERVER_LDAP_ENCRYPTION="encryption-TLS\n"#@author:yuyanan @since:2014-10-29 9.9newfeature:sslldap
SET_SERVER_LDAP_NO_ENCRYPTION="no encryption-SSL/TLS\n"
SET_SERVER_GROUP_SEARCH= "grp-search\n"
SET_SERVER_NO_GROUP_SEARCH= "no grp-search\n"
SET_SERVER_RADIUS_SECRET= "radius-secret '$radius_secret'\n"
SET_SERVER_RADIUS_ENCRYPTION = "radius-encryption tls\n" #@ZJ New feature Radius TLS since 2014-12-26
SET_SERVER_BACKUP= "backup\n"
SET_SERVER_BACKUP_IP_ADDR= "backup-ip-addr '$backup_server_addr'\n"
SET_SERVER_BACKUP_PORT= "backup-port '$backup_server_port'\n" #@author: yuyanan @bug: zf-10015 @since: 2014-10-17
SET_SERVER_BACKUP_SECRET= "backup-radius-secret '$backup_radius_secret'\n"
SET_SERVER_REQUEST_TIMEOUT= "request-timeout '$request_timeout'\n"
SET_SERVER_RETRY_COUNT= "retry-count '$retry_count'\n"
SET_SERVER_RETRY_INTERVAL= "reconnect-primary-interval '$retry_interval'\n"
SET_SERVER_RADIUS_AUTH_METHOD= "auth-method '$radius_auth_method'\n"
SAVE_SERVER_CONFIG= "exit\n"

DELETE_SERVER= "no aaa '$server_name'"

ENTRY_NOT_FOUND_MSG = "The entry '$server_name' could not be found. Please check the spelling, and then try again."

GUI_INFO_KEY_LIST = ['server_name', 'type', 'global_catalog', 'backup', 'server_addr', 'server_port', 
                     'win_domain_name', 'admin_domain_name', 'ldap_key_attribute', 'ldap_search_filter', 
                     'backup_server_addr', 'backup_server_port', 'request_timeout', 'retry_count', 
                     'retry_interval']

#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 

def configure_aaa_servers(zdcli, server_cfg_list):
    '''
    Input:
        cfg_list: a list of aaa server configuration.
    ''' 
    fail_name_list = []
    for cfg in server_cfg_list:        
        res = _configure_aaa_server(zdcli, cfg)
        if not res:
            fail_name_list.append(cfg['server_name'])
            continue
    
    if fail_name_list:
        return (False, 'Fail to configure aaa servers %s in ZD CLI' % fail_name_list)
    
    else:
        return (True, 'Configure all aaa servers in the cfg list in ZD CLI successfully.')
    


def delete_all_servers(zdcli):    
    server_name_list = aaa_servers.get_all_aaa_server_name_list(zdcli)
    if not server_name_list:
        return
    
    try:
        for name in server_name_list:
            cmd = Template(DELETE_SERVER).substitute(dict(server_name = name))
            res = zdcli.do_cfg(cmd)            
    except Exception, e:
        import traceback
        logging.warning(traceback.format_exc())
        
        raise e
    

def delete_aaa_servers(zdcli, server_name_list):
    """
    output:
        True: delete aaa servers successfully.
        False: fail to delete aaa servers.
    """
    fail_name_list = []
    for server_name in server_name_list:
        res = _delete_aaa_server_by_name(zdcli, server_name)
        if not res:
            fail_name_list.append(server_name)
            continue
    
    if fail_name_list:
        return (False, 'Fail to delete aaa servers %s from ZD CLI' % fail_name_list)
    
    else:
        return (True, 'Delete aaa servers %s from ZD CLI successfully.' % server_name_list)
    
    
def get_server_info_by_names(zdcli, server_name_list):
    """
    output:
        a list of the aaa servers' info.
    """
    server_info_list = []    
    for server_name in server_name_list:
        server_info = _get_server_info_by_name(zdcli, server_name)
        if server_info:
            server_info_list.append(server_info)
    
    return server_info_list


def verify_cli_info_with_gui(cli_info_list, gui_info_list):
    '''
    Verify server cfg between cli set and gui get.
    Input:
        cli_info_list: a list of the AAA servers' information shown in ZD CLI.
        gui_info_list: a list of the AAA servers' information shown in ZD GUI.
    '''
    cli_len = len(cli_info_list)
    gui_len = len(gui_info_list)

    if cli_len != gui_len:
        return (False, 'The number of aaa servers in ZD CLI [%s] is not the same as in ZD GUI [%s]!' % (cli_len, gui_len))
    
    for i in range(gui_len):
        for j in range(cli_len):
            if gui_info_list[i]['server_name'] == cli_info_list[j]['Name']:
                res, msg = _verify_cli_info_with_gui(cli_info_list[j], gui_info_list[i])
                if res:
                    break
                else:
                    return (False, msg)
                
            elif j == cli_len - 1:
                return (False, 'The aaa server [%s] exists in ZD GUI, but not in ZD CLI!' % gui_info_list[i]['server_name'])
            
    return (True, "All aaa servers' information shown in ZD GUI is the same as in ZD CLI!")
    

def verify_cli_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    '''
    Verify server cfg between cli set and gui get.
    Input:
        cli_cfg_dict: a dict of configuration used to configure an AAA server in ZD CLI.
        {'server_name': '', 
         'new_server_name': '', 
         'type': 'ad'/'ldap'/'radius-auth'/'radius-acct', 
         'global_catalog': True/False,
         'backup': True/False, 
         'server_addr': '', 
         'server_port': '',
         'win_domain_name': '',
         'admin_domain_name': '', 
         'admin_password': '',
         'ldap_key_attribute': '', 
         'ldap_search_filter': '', 
         'radius_secret': '',
         'backup_server_addr': '', 
         'backup_server_port': '', 
         'backup_radius_secret': '', 
         'request_timeout': '', 
         'retry_count': '', 
         'retry_interval': ''
         'radius_auth_method': 'pap'/'chap'
         }
        gui_info_dict: a dict of an AAA server's information shown in ZD GUI.
        {'server_name': '', 
         'type': 'ad'/'ldap'/'radius-auth'/'radius-acct', 
         'global_catalog': True/False, 
         'backup': True/False, 
         'server_addr': '', 
         'server_port': '', 
         'win_domain_name': '', 
         'admin_domain_name': '',
         'ldap_key_attribute': '', 
         'ldap_search_filter': '', 
         'backup_server_addr': '', 
         'backup_server_port': '',
         'request_timeout': '', 
         'retry_count': '', 
         'retry_interval': ''
         'radius_auth_method': 'pap'/'chap'
        }
    '''
    if cli_cfg_dict.get('new_server_name'):
        cli_cfg_dict['server_name'] = cli_cfg_dict.pop('new_server_name')
    
    expect_gui_info = dict()
    for k in GUI_INFO_KEY_LIST:
        
        value = cli_cfg_dict.get(k, '')
        if value or value == False:
            expect_gui_info[k] = value
        
    res, msg = _expect_is_in_dict(expect_gui_info, gui_info_dict)
    if res:
        return (True, 'The AAA server configuration is correct in ZD GUI')
    
    else:
        return (False, msg)


#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 

def _configure_aaa_server(zdcli, cfg):
    '''
    Input:
       cfg: a dictionary of the server configuration.     
         'type':               type of the server (ad/ldap/radius-auth/radius-acct)
         'global_catalog':     enable global catalog or not (True/False/None)
         'backup':             enable backup or not (True/False/None)
    '''   
    conf = {'server_name': '', 'new_server_name': '', 'type': 'ad', 'global_catalog': None, 
            'backup': None, 'server_addr': '', 'server_port': '', 'win_domain_name': '', 
            'radius_secret': '', 'admin_domain_name': '', 'admin_password': '', 'ldap_key_attribute': '', 
            'ldap_search_filter': '', 'backup_server_addr': '', 'backup_server_port': '', 'backup_radius_secret': '', 
            'request_timeout': '', 'retry_count': '', 'retry_interval': '', 'radius_auth_method': 'pap','ldap_encryption':None,'radius_encryption':None,
           }
    conf.update(cfg)
    logging.info('Configure aaa server in ZD CLI with cfg:\n%s' % pformat(cfg, 4, 120))
    value = _set_aaa_server(zdcli, conf)
    if not value:
        logging.info('Fail to configure aaa server [%s] in ZD CLI!' % cfg['server_name'])
        return False
    
    res = _verify_aaa_server_in_cli(zdcli, conf)
    if res:
        logging.info('Configure aaa server [%s] in ZD CLI successfully!' % cfg['server_name'])
        return True
    
    else:
        logging.info('Fail to configure aaa server [%s] in ZD CLI!' % cfg['server_name'])
        return False
    
    
def _set_aaa_server(zdcli, cfg):  
    cmd_block = _construct_configure_server_cmd_block(cfg)
    logging.info('Configure aaa server with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if res.get('grp-search'):
        if "The AAA server type is not AD or LDAP" in res['grp-search'][0]:
            zdcli.do_cfg('quit', raw=True)
            raise Exception(res['grp-search'][0])
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True


def _verify_aaa_server_in_cli(zdcli, cfg):
    new_server_name = cfg.pop('new_server_name')
    if new_server_name:
        cfg['server_name'] = new_server_name
        
    cli_info = _get_server_info_by_name(zdcli, cfg['server_name'])
    if not cli_info:
        return False
    
    cli_ks = cli_info.keys()
    expect_info = _define_expect_info(cfg)
    expect_ks = expect_info.keys()
    
    result = True
    
    for k in expect_ks:
        if k not in cli_ks:
            logging.info('The parameter [%s] of aaa server [%s] does not configure successfully in ZD CLI' % (k, cfg['server_name']))
            result = False
        else:
            cli_value = cli_info[k]
            exp_value = expect_info[k]
            
            if type(cli_value) == dict and type(exp_value) == dict:
                for key, cli_v in cli_value.items():
                    exp_v = exp_value.get(key)
                    if 'secret' not in key.lower() and 'password' not in key.lower():
                        if exp_v != cli_v:
                            if cli_v == "Disabled" and exp_v == None:
                                result = True
                            else:
                                logging.info('The parameter [%s][%s] of aaa server [%s] does not configure successfully in ZD CLI' % (k, key, cfg['server_name']))
                                result = False
                    else:
                        #@author: chen.tao 2013-12-19, to fix bug ZF-6566
                        #if len(exp_v) != len(cli_v):
                            #For password and secret only verify length.
                        #    logging.info('The parameter [%s][%s] of aaa server [%s] does not configure successfully in ZD CLI' % (k, key, cfg['server_name']))
                        result = True
                        #@author: chen.tao 2013-12-19, to fix bug ZF-6566
            else:
                if 'secret' not in k.lower() and 'password' not in k.lower():
                    if cli_value != exp_value:
                        logging.info('The parameter [%s] of aaa server [%s] does not configure successfully in ZD CLI' % (k, cfg['server_name']))
                        result = False
                else:
                #@author: chen.tao 2013-12-19, to fix bug ZF-6566
                    #For password and secret only verify length.
                    #if len(cli_value) != len(exp_value):
                    #    logging.info('The parameter [%s] of aaa server [%s] does not configure successfully in ZD CLI' % (k, cfg['server_name']))
                    result = True
                #@author: chen.tao 2013-12-19, to fix bug ZF-6566
    return result


def _get_server_info_by_name(zdcli, server_name):
    res_dict = aaa_servers.get_aaa_server_by_name(zdcli, server_name)
    if not res_dict.has_key('AAA'):
        entry_not_found_msg = Template(ENTRY_NOT_FOUND_MSG).substitute(dict(server_name = server_name))
        if entry_not_found_msg in res_dict.keys():
            logging.info('The aaa server [%s] does not exist in ZD CLI!' % server_name)
            return {}
        else:
            raise Exception(str(res_dict))
    
    if res_dict['AAA'].has_key('ID'):  
        info_dict = res_dict['AAA']['ID'].values()[0]
    
    
    return info_dict

            
def _delete_aaa_server_by_name(zdcli, server_name):
    """
    output:
          True: delete aaa server successfully.
          False: fail to delete aaa server.
    """
    info = _get_server_info_by_name(zdcli, server_name)
    if not info:
        return True
    
    cmd = Template(DELETE_SERVER).substitute(dict(server_name = server_name))
    
    logging.info('Delete aaa server [%s] by command [%s].' % (server_name, cmd))
    res = zdcli.do_cfg(cmd)
    logging.info('cmd execution result:\n%s' % pformat(res, 4, 120))
    
    info = _get_server_info_by_name(zdcli, server_name)
    if info:
        logging.info('Fail to delete aaa server [%s]!' % server_name)
        return False
    
    else:
        logging.info('Delete aaa server [%s] successfully!' % server_name)
        return True       


def _verify_cli_info_with_gui(cli_dict, gui_dict):
    logging.info('The aaa server info in CLI is:\n%s' % pformat(cli_dict, 4, 120))
    expect_dict = _define_expect_info(gui_dict)
    res, msg = _expect_is_in_dict(expect_dict, cli_dict)
    if res:
        return (True, '')
    
    else:
        return (False, msg)


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


def _construct_configure_server_cmd_block(cfg):      
    cmd_block = Template(CONFIG_SERVER_CMD_BLOCK).substitute(dict(server_name = cfg['server_name']))
    cmd_block = cmd_block + Template(SET_SERVER_TYPE).substitute(dict(type = cfg['type']))
    
    if cfg['new_server_name']:
        cmd_block = cmd_block + Template(SET_SERVER_NAME).substitute(dict(new_server_name = cfg['new_server_name']))

    if cfg['global_catalog'] == True:
        cmd_block = cmd_block + SET_SERVER_GLOBAL_CATALOG
    
    elif cfg['global_catalog'] == False:
        cmd_block = cmd_block + SET_SERVER_NO_GLOBAL_CATALOG
        
    #@ZJ20141217 New feature Radius TLS
    if cfg['radius_encryption']==True:
        cmd_block=cmd_block + SET_SERVER_RADIUS_ENCRYPTION
        
    if cfg['backup'] == True:
        cmd_block = cmd_block + SET_SERVER_BACKUP
    
    elif cfg['backup'] == False:
        cmd_block = cmd_block + SET_SERVER_NO_BACKUP
    
    if cfg['server_addr']:
        cmd_block = cmd_block + Template(SET_SERVER_IP_ADDR).substitute(dict(server_addr = cfg['server_addr']))
        if cfg['server_port']:
            cmd_block = cmd_block + Template(SET_SERVER_PORT).substitute(dict(server_addr = cfg['server_addr'], server_port = cfg['server_port']))
    
    if cfg['win_domain_name']:
        cmd_block = cmd_block + Template(SET_SERVER_WIN_DOMAIN_NAME).substitute(dict(win_domain_name = cfg['win_domain_name']))
    
    
    if cfg['radius_secret']:
        cmd_block = cmd_block + Template(SET_SERVER_RADIUS_SECRET).substitute(dict(radius_secret = cfg['radius_secret']))
    
    if cfg['admin_domain_name']:
        cmd_block = cmd_block + Template(SET_SERVER_ADMIN_DOMAIN_NAME).substitute(dict(admin_domain_name = cfg['admin_domain_name']))
        
    if cfg['admin_password']:
        cmd_block = cmd_block + Template(SET_SERVER_ADMIN_PASSWORD).substitute(dict(admin_password = cfg['admin_password']))
    
    if cfg['ldap_key_attribute']:
        cmd_block = cmd_block + Template(SET_SERVER_LDAP_KEY_ATTRIBUTE).substitute(dict(ldap_key_attribute = cfg['ldap_key_attribute']))
    
    if cfg.get('grp_search', None) != None:
        if cfg.get('grp_search'):
            cmd_block = cmd_block + Template(SET_SERVER_GROUP_SEARCH).substitute(dict())
        else:
            cmd_block = cmd_block + Template(SET_SERVER_NO_GROUP_SEARCH).substitute(dict())
     
    #@auth:yuyanan @since:2014-10-29 9.9newfeature:sslldap
    if cfg.get('ldap_encryption'):
        cmd_block = cmd_block + Template(SET_SERVER_LDAP_ENCRYPTION).substitute(dict())
    else:
        cmd_block = cmd_block + Template(SET_SERVER_LDAP_NO_ENCRYPTION).substitute(dict())       
            
        
    if cfg['ldap_search_filter']:
        cmd_block = cmd_block + Template(SET_SERVER_LDAP_SEARCH_FILTER).substitute(dict(ldap_search_filter = cfg['ldap_search_filter']))
    
    if cfg['backup_server_addr']:
        cmd_block = cmd_block + Template(SET_SERVER_BACKUP_IP_ADDR).substitute(dict(backup_server_addr = cfg['backup_server_addr']))
        if cfg['backup_server_port']:
            cmd_block = cmd_block + Template(SET_SERVER_BACKUP_PORT).substitute(dict(backup_server_addr = cfg['backup_server_addr'], backup_server_port = cfg['backup_server_port']))
    
    if cfg['backup_radius_secret']:
        cmd_block = cmd_block + Template(SET_SERVER_BACKUP_SECRET).substitute(dict(backup_radius_secret = cfg['backup_radius_secret']))
            
    if cfg['request_timeout']:
        cmd_block = cmd_block + Template(SET_SERVER_REQUEST_TIMEOUT).substitute(dict(request_timeout = cfg['request_timeout']))
        
    if cfg['retry_count']:
        cmd_block = cmd_block + Template(SET_SERVER_RETRY_COUNT).substitute(dict(retry_count = cfg['retry_count']))
        
    if cfg['retry_interval']:
        cmd_block = cmd_block + Template(SET_SERVER_RETRY_INTERVAL).substitute(dict(retry_interval = cfg['retry_interval']))
    
    #radius_auth_method is only for radius_auth.
    if cfg['type'] == 'radius-auth' and cfg['radius_auth_method']:
        cmd_block = cmd_block + Template(SET_SERVER_RADIUS_AUTH_METHOD).substitute(dict(radius_auth_method = cfg['radius_auth_method']))
        
    cmd_block = cmd_block + SAVE_SERVER_CONFIG
    
    return cmd_block


#Updated by cwang@20130529, just support from 9.5
def _define_expect_info(conf):
    cfg = {'server_name': '', 'new_server_name': '', 'type': 'ad', 'global_catalog': None, 
            'backup': None, 'server_addr': '', 'server_port': '', 'win_domain_name': '', 
            'radius_secret': '', 'admin_domain_name': '', 'admin_password': '', 'ldap_key_attribute': '', 
            'ldap_search_filter': '', 'backup_server_addr': '', 'backup_server_port': '', 'backup_radius_secret': '', 
            'request_timeout': '', 'retry_count': '', 'retry_interval': '', 'Max. Number of Consecutive Drop Packets': '1'
           }
    cfg.update(conf)
    
    info = dict()
    info['Name'] = cfg['server_name']
    
    if cfg['type'] == 'radius-auth':
        info['Type'] = 'RADIUS server'
        
    elif cfg['type'] == 'radius-acct':
        info['Type'] = 'RADIUS Accounting server'
        
    elif cfg['type'] == 'ad':
        info['Type'] = 'Active Directory'
        
    elif cfg['type'] == 'ldap':
        info['Type'] = 'LDAP'
    
    if cfg['type'] == 'ad' or cfg['type'] == 'ldap':
        if cfg['server_addr']:
            info['IP Address'] = cfg['server_addr']
        
        if cfg['server_port']:
            info['Port'] = cfg['server_port']
              
        if cfg['admin_domain_name']:
            info['Admin DN'] = cfg['admin_domain_name']
        
        if cfg['admin_password']:
            info['Admin Password'] = cfg['admin_password']
            
        if cfg['type'] == 'ad':
            if cfg['win_domain_name']:
                info['Windows Domain Name'] = cfg['win_domain_name']
            
            if cfg['global_catalog'] == True:
                info['Global Catalog'] = 'Enabled'
            
            elif cfg['global_catalog'] == False:
                info['Global Catalog'] = 'Disabled'
        
        else:
            if cfg['win_domain_name']:
                info['LDAP Base DN'] = cfg['win_domain_name']
                
            if cfg['ldap_key_attribute']:
                info['Key Attribute'] = cfg['ldap_key_attribute']
            
            if cfg['ldap_search_filter']:
                info['Search Filter'] = cfg['ldap_search_filter']
    
    elif cfg['type'] == 'radius-auth' or cfg['type'] == 'radius-acct':
        primary_radius = {}
        secondary_radius = {}
        failover_policy = {}
        if cfg['server_addr']:
            primary_radius['IP Address'] = cfg['server_addr']
        
        if cfg['server_port']:
            primary_radius['Port'] = cfg['server_port']
        
        if cfg['radius_secret']:
            primary_radius['Secret'] = cfg['radius_secret']
        
        if cfg['backup'] == False:
            secondary_radius['Status'] = 'Disabled'
        
        elif cfg['backup'] == True:
            secondary_radius['Status'] = 'Enabled'
            if cfg['backup_server_addr']:
                secondary_radius['IP Address'] = cfg['backup_server_addr']
            
            if cfg['server_port']:
                secondary_radius['Port'] = cfg['backup_server_port']
            
            if cfg['radius_secret']:
                secondary_radius['Secret'] = cfg['backup_radius_secret']
            
            if cfg['Max. Number of Consecutive Drop Packets']:
                failover_policy['Max. Number of Consecutive Drop Packets'] = cfg['Max. Number of Consecutive Drop Packets']
        
        if cfg['request_timeout']:
            failover_policy['Request Timeout'] = "%s Seconds" % cfg['request_timeout']
        
        if cfg['retry_count']:
            failover_policy['Max. Number of Retries'] = "%s Times" % cfg['retry_count']
        
        if cfg['retry_interval']:
            failover_policy['Reconnect Primary'] = "%s Minutes" % cfg['retry_interval']
        
        if cfg['type'] == 'radius-auth':
            info['Primary RADIUS'] = primary_radius
            info['Secondary RADIUS'] = secondary_radius
        else:
            info['Primary RADIUS Accounting'] = primary_radius
            info['Secondary RADIUS Accounting'] = secondary_radius
            
        #Title Change@2012/9/17 by cwang
        if failover_policy:
            info['Retry Policy'] = failover_policy
    
    logging.info('The expect info in ZD CLI is:\n%s' % pformat(info, 4, 120))
    return info

