'''
Author#cwang@ruckuswireless.com
date#2010-10-20
This file is used for aaa servers getting/setting/searching etc.
'''

import re
import logging
from string import Template
from RuckusAutoTest.common import utils
from pprint import pformat
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#################################################
#command line
#################################################
CONFIG_AAA_CMD="aaa $name\n"
CONFIG_AAA_TYPE = "type $type\n" #ad/ldap/radius-auth/tacplus-auth
CONFIG_AAA_IP = "ip-addr $ip\n"
CONFIG_AAA_PORT = "port $port\n"
CONFIG_AAA_SECRET = "tacplus-secret $secret\n"
CONFIG_AAA_NAME = "name $name\n"
CONFIG_AAA_SERVICE = "tacplus-service $service\n"
SAVE_AAA_CONFIG = "end\n"

DELETE_AAA_SERVER = "no aaa $name"

####################################
#method to configure AAA Server
####################################
def remove_aaa_server(zdcli,server_name):
    cmd_block = Template(DELETE_AAA_SERVER).substitute(dict(name = server_name))
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    return (True, "")

def cfg_aaa_server(zdcli,aaa_cfg):
    '''
    input:
    {
        'name':'',#old name
        'server_name':'',#new name
        'server_type':'',#ad/ldap/radius-auth/tacacs_plus
        'server_addr':'',
        'server_port':'',
        'tacacs_auth_secret':'',
        'tacacs_service':''
    }
    '''

    if aaa_cfg['server_type']=='tacacs_plus':
        return _cfg_tacplus_server(zdcli,aaa_cfg)
    else:
        logging.info('aaa type not support currently')

def _cfg_tacplus_server(zdcli,tacplus_cfg):
    if not tacplus_cfg.has_key('name'):
        tacplus_cfg['name'] = tacplus_cfg['server_name']
    cmd_block = Template(CONFIG_AAA_CMD).substitute(dict(name = tacplus_cfg['name']))
    if tacplus_cfg.get('server_name'):
        cmd_block+=Template(CONFIG_AAA_NAME).substitute(dict(name = tacplus_cfg['server_name']))
    if tacplus_cfg.get('server_type'):
        cmd_block+=Template(CONFIG_AAA_TYPE).substitute(dict(type = 'tacplus-auth'))
    if tacplus_cfg.get('server_addr'):
        cmd_block+=Template(CONFIG_AAA_IP).substitute(dict(ip = tacplus_cfg['server_addr']))
    if tacplus_cfg.get('server_port'):
        cmd_block+=Template(CONFIG_AAA_PORT).substitute(dict(port = tacplus_cfg['server_port']))
    if tacplus_cfg.get('tacacs_auth_secret'):
        cmd_block+=Template(CONFIG_AAA_SECRET).substitute(dict(secret = tacplus_cfg['tacacs_auth_secret']))
    if tacplus_cfg.get('tacacs_service'):
        cmd_block+=Template(CONFIG_AAA_SERVICE).substitute(dict(service = tacplus_cfg['tacacs_service']))
    cmd_block+=SAVE_AAA_CONFIG
    logging.info('config tacacs plus command like this:%s'%cmd_block)    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    if "Your changes have been saved." not in res['end'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return (False, res)
    
    return (True, "")


CONST_KEY={'title':'AAA',
           'id':'ID',
           'name':'Name',
           'type':'Type',
           }
#=============================================#
#             Access Methods            
#=============================================#
def get_all_aaa_servers(zdcli):
    '''
    Get all of aaa servers by show command, return result as dict.
    '''
    cmd_block = SHOW_SERVERS_ALL
    logging.info("======get aaa servers all==========")

    aaa_servers_res = zdcli.do_show(cmd_block)
    
    logging.info('The aaa servers result\n:%s', aaa_servers_res)
    aaa_servers_dict = output.parse(aaa_servers_res)
    
#    logging.info('The l2 ACL dict result:\n%s',l2acl_data)
    return aaa_servers_dict

def get_all_aaa_server_name_list(zdcli):
    aaa_dd = get_all_aaa_servers(zdcli)
    if not aaa_dd.has_key('AAA'):
        return []
    
    svrs = aaa_dd[CONST_KEY['title']][CONST_KEY['id']]
    name_list = []
    for id, svr in svrs.items():
        if svr.get(CONST_KEY['type']) in ['Guest', 'Local']:
            continue
        else:
            name_list.append(svr.get(CONST_KEY['name']))
    
    return name_list



def get_aaa_server_by_name(zdcli, server_name):
    '''
    Get one of aaa server by server name, return result as dict.
    '''
    cmd_block = Template(SHOW_SERVER_BY_NAME).substitute(dict(name = server_name))
    
    logging.info( "=======show aaa server by name=========")

    aaa_server_res = zdcli.do_show(cmd_block)
    
    logging.info('The aaa server result\n%s:' % aaa_server_res)
    aaa_server_dict = output.parse(aaa_server_res)
    
    return aaa_server_dict


def verify_aaa_server_by_type(zdcli, gui_d, cli_d, type):
    '''
    Validate aaa server information via different type.
    '''
    if type == AD:
        return _verify_ad_server(gui_d, cli_d)
    elif type == LDAP:
        return _verify_ldap_server(gui_d, cli_d)
    elif type == RADIUS:
        return _verify_radius_server(gui_d, cli_d)
    elif type == RADIUS_ACC:
        return _verify_radius_acc_sever(gui_d, cli_d)
    else:
        raise Exception('Unsupport type [%d]' % type)


def decode_type(aaa_type):
    if aaa_type == 'radius-auth':
        return RADIUS
    elif aaa_type == 'radius-acct':
        return RADIUS_ACC
    elif aaa_type == 'ldap':
        return LDAP
    elif aaa_type == 'ad':
        return AD
    else:
        raise Exception('Can not decode type [%s], make sure type in [radius-auth, raduis-acct, ldap, ad]' % aaa_type)

#===============================================#
#           Protected Constant
#===============================================#
SHOW_SERVERS_ALL = 'show aaa all'
SHOW_SERVER_BY_NAME = 'show aaa name \'$name\''

#----------------------------------------------
AD = 1
LDAP = 2
RADIUS = 3
RADIUS_ACC = 4


LDAP_KV_MAP = {'Admin DN':'ldap_admin_dn',
               'Admin Password':'ldap_admin_pwd',
               'IP Address':'server_addr',
               'Port':'server_port',
               'Name':'server_name',
               'Type':'type',
               'LDAP Base DN':'ldap_search_base',
               }
RADIUS_KV_MAP = {
        'Name'      :'server_name',
        'IP Address':'server_addr',
        'Secret'    :'radius_auth_secret',
        'Type'      :'type',
    }

RADIUS_ACC_KV_MAP = {
        'Name'        :'server_name',
        'IP Address'  :'server_addr',
        'Secret'      :'radius_acct_secret',
        'Port'        :'server_port',
        'Type'        :'type',
    }

AD_KV_MAP = {'NAME':'server_name',
            'IP Address':'server_addr',            
            'Port':'server_port',
            'Windows Domain Name':'win_domain_name',
            'Type':'type',          
             }

#gui and cli get keys mapping.
SERVER_GUI_CLI_MAP = {'Name': 'server_name',
                      'IP Address': 'server_addr',
                      'Port': 'server_port',
                      'Type': 'type',
                      'Key Attribute': 'ldap_key_attribute',
                      'Search Filter': 'ldap_search_filter',
                      'LDAP Base DN': 'win_domain_name',
                      'Windows Domain Name': 'win_domain_name',
                      'Admin DN': 'admin_domain_name',
                      'Global Catalog': 'global_catalog',
                      'Auth Method': 'radius_auth_method',
                      }

#----------------------------------------------


#===============================================#
#           Protected Method
#===============================================#
def _verify_radius_acc_sever(gui_d, cli_d):
    '''
    GUI:
        {'server_name': 'RADIUS Accounting',
         'server_addr': '192.168.0.252',
         'radius_acct_secret': '1234567890',
         'server_port': '1813'
        }
        
    CLI:
        {'Name': 'RADIUS',
         'Primary RADIUS': {'IP Address': '192.168.0.252',
                            'Port': '1812',
                            'Secret': '1234567890'},
         'Secondary RADIUS': {'Status': 'Disabled'},
         'Type': 'radius-acct'}
    '''
    #mapping
    if cli_d.has_key('Primary RADIUS'):
        info = cli_d.pop('Primary RADIUS')
        cli_d.update(info)
    gui_d['type'] = 'radius-acct'
    if cli_d['Type'] == 'RADIUS Accounting server':
        cli_d['Type'] = 'radius-acct'
    chk_gui_d = _map_k_d(gui_d, cli_d, RADIUS_ACC_KV_MAP)
    return  _validate_dict_value(chk_gui_d, cli_d)    

def _verify_radius_server(gui_d, cli_d):
    """
        CLI:
         {'Name': 'RADIUS',
          'Primary RADIUS': {'IP Address': '192.168.0.252',
                             'Port': '1812',
                             'Secret': '1234567890'},
          'Secondary RADIUS': {'Status': 'Disabled'},
          'Type': 'radius-auth'},
          
        GUI:    
         {'server_addr': '192.168.0.252', 'server_port': '1812', 'server_name': 'radius_server',
          'win_domain_name': '', 'ldap_search_base': '',
          'ldap_admin_dn': '', 'ldap_admin_pwd': '',
          'radius_auth_secret': '1234567890', 'radius_acct_secret': ''
         }
    """
    #mapping
    if cli_d.has_key('Primary RADIUS'):
        info = cli_d.pop('Primary RADIUS')
        cli_d.update(info)
    gui_d['type'] = 'radius-auth'
    if cli_d['Type'] == 'RADIUS server':
        cli_d['Type'] = 'radius-auth'
    chk_gui_d = _map_k_d(gui_d, cli_d, RADIUS_KV_MAP)
    return  _validate_dict_value(chk_gui_d, cli_d)       

def _verify_ad_server(gui_d, cli_d):
    """
    GUI:
    {'server_name': 'ACTIVE_DIRECTORY',
     'server_addr': '192.168.0.250',
     'server_port': '389',
     'win_domain_name': 'rat.ruckuswireless.com',
    }
    
    CLI:
     {'Admin DN': '',
      'Admin Password': '',
      'Global Catalog': 'Disabled',
      'IP Address': '192.168.0.250',
      'Name': 'ACTIVE_DIRECTORY',
      'Port': '389',
      'Type': 'ad',
      'Windows Domain Name': 'rat.ruckuswireless.com'}
    """
    if cli_d['Type'] in ['ACTIVE DIRECTORY', 'Active Directory']:
        cli_d['Type'] = 'ad'
    gui_d['type'] = 'ad'
    #@author: tanshixiong #@since: 2015-1-12 @bug: ZF-11605
    chk_gui_d = _map_k_d(gui_d, cli_d, AD_KV_MAP)
    return  _validate_dict_value(chk_gui_d, cli_d)  


                
def _verify_ldap_server(gui_d, cli_d):
    '''
       CLI:
                          {Admin DN': 'cn=Manager,dc=example,dc=net',
                          'Admin Password': 'lab4man1',
                          'IP Address': '192.168.0.252',
                          'Key Attribute': '',
                          'LDAP Base DN': 'dc=example,dc=net',
                          'Name': 'LDAP',
                          'Port': '389',
                          'Search Filter': 'objectClass=*',
                          'Type': 'ldap'},
    
       GUI:
    
                         {'server_name': 'LDAP',
                          'server_addr':'192.168.0.252',
            	          'server_port':'389',
                          'ldap_search_base':'dc=example,dc=net',
                          'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
                          'ldap_admin_pwd': 'lab4man1'},
   '''
   
    gui_d['type'] = 'ldap'
    if cli_d['Type'] == 'LDAP':
        cli_d['Type'] = 'ldap'
    chk_gui_d = _map_k_d(gui_d, cli_d, LDAP_KV_MAP)
    return  _validate_dict_value(chk_gui_d, cli_d)

def _map_k_d(gui_d, cli_d, k_map):
    r_d = {}
    for key in gui_d.keys():
        for k, v in k_map.items():
            if key == v:
                r_d[k] = gui_d[v]
                
    return r_d


def _validate_dict_value(gui_d, cli_d):
    for g_k, g_v in gui_d.items():
        for c_k, c_v in cli_d.items():
            if g_k == c_k:
                if re.match(r'^\*+$', c_v):
                    break
                elif g_v == c_v:
                    continue
                else:
                    return (False, 'value of key [%s] is not equal' % g_k)
                            
    return (True, 'All of value are matched')

def verify_server_cfg_gui_cli_get(gui_get_servers_list, cli_get_servers_list):
    '''
    GUI get:
    [{   'admin_domain_name': u'admin@domain.ruckuswireless.com',
      'global_catalog': True,
      'server_addr': u'2020:db8:1::249',
      'server_name': u'ad_server_2',
      'server_port': u'389',
      'type': 'ad',
      'win_domain_name': u'domain.ruckuswireless.com'}]
                                      
    CLI get:
     [{   'Admin DN': 'admin@domain.ruckuswireless.com',
      'Admin Password': '1234567890',
      'Global Catalog': 'Enabled',
      'IP Address': '2020:db8:1::249',
      'Name': 'ad_server_2',
      'Port': '389',
      'Type': 'Active Directory',
      'Windows Domain Name': 'domain.ruckuswireless.com'}]
    '''
    #Convert cli server configuration structure.
    new_cli_get_servers_list = []
    for cli_server_cfg in cli_get_servers_list:
        new_cli_get_servers_list.append(_convert_cli_server_cfg(cli_server_cfg))
        
    err_dict = {}
    if len(gui_get_servers_list) != len(new_cli_get_servers_list):
        err_dict['Count'] = "GUI get: %s, CLI get: %s" % (len(gui_get_servers_list), len(new_cli_get_servers_list))
    else:
        new_gui_servers_cfg = _convert_list_to_dict(gui_get_servers_list)
        new_cli_servers_cfg = _convert_list_to_dict(new_cli_get_servers_list)
        
        logging.debug("GUI get: %s" % new_gui_servers_cfg)
        logging.debug("CLI get: %s" % new_cli_servers_cfg)
        
        for server_name, gui_get_server_cfg in new_gui_servers_cfg.items():
            cli_get_server_cfg = new_cli_servers_cfg[server_name]
            res = _compare_server_cfg_gui_cli_get(gui_get_server_cfg, cli_get_server_cfg)
            if res:
                err_dict[server_name] = res
                    
    return err_dict

def _convert_cli_server_cfg(cli_get_server_cfg):
    '''
    Convert CLI dict to gui dict structure.
    '''
    cli_gui_keys_mapping = SERVER_GUI_CLI_MAP
    
    values_mapping = {'Active Directory': 'ad',
                      'RADIUS Accounting server': 'radius-acct',
                      'RADIUS server': 'radius-auth',
                      'LDAP': 'ldap',
                      'Enabled': True,
                      'Disabled': False,
                      }
    
    new_cli_server_cfg = {}
    
    for key, value in cli_get_server_cfg.items():
        if cli_gui_keys_mapping.has_key(key):
            new_key = cli_gui_keys_mapping[key]
            if values_mapping.has_key(value):
                new_value = values_mapping[value]
            else:
                new_value = value
                
            new_cli_server_cfg[new_key] = new_value
    
    type = new_cli_server_cfg['type']
    
    failover_cfg = {}
    
    if cli_get_server_cfg.has_key('Failover Policy'):
        failover_cfg = cli_get_server_cfg['Failover Policy']
    if type == 'radius-acct':
        pri_ras_acct_cfg = cli_get_server_cfg['Primary RADIUS Accounting']
        sec_ras_acct_cfg = cli_get_server_cfg['Secondary RADIUS Accounting']
        
        new_cli_server_cfg.update(_convert_radius_cfgs(pri_ras_acct_cfg, sec_ras_acct_cfg, failover_cfg))
    elif type == 'radius-auth':
        pri_ras_cfg = cli_get_server_cfg['Primary RADIUS']
        sec_ras_cfg = cli_get_server_cfg['Secondary RADIUS']
            
        new_cli_server_cfg.update(_convert_radius_cfgs(pri_ras_cfg, sec_ras_cfg, failover_cfg))
        
    return new_cli_server_cfg

def _compare_server_cfg_gui_cli_get(gui_get_server_cfg, cli_get_server_cfg):
    new_cli_get_server_cfg = {}
    new_cli_get_server_cfg.update(cli_get_server_cfg)
    
    #For ad, if global category is False, remove admin_domain_name from cli result.
    if new_cli_get_server_cfg.has_key('admin_domain_name') and \
         not new_cli_get_server_cfg.get('global_catalog') and \
         new_cli_get_server_cfg.get('type') == 'ad':
        new_cli_get_server_cfg.pop('admin_domain_name')
        
    err_dict = utils.compare_dict_key_value(gui_get_server_cfg, new_cli_get_server_cfg)
                
    return err_dict

def _convert_list_to_dict(server_cfg_list, key_name = ''):
    '''
    Convert server cfg list to dict, key is server name.
    '''
    if not key_name:
        key_name = 'server_name'
        
    servers_cfg_dict = {}
    
    for server_cfg in server_cfg_list:
        servers_cfg_dict[server_cfg[key_name]] = server_cfg
    
    return servers_cfg_dict

def _convert_radius_cfgs(pri_ras_cfg, sec_ras_cfg, failover_cfg):
    '''
    Convert radius servers configuration.
    '''
    new_ras_server_cfg = {}
    new_ras_server_cfg['server_addr'] = pri_ras_cfg['IP Address']
    new_ras_server_cfg['server_port'] = pri_ras_cfg['Port']
    
    if sec_ras_cfg['Status'] == 'Enabled':
        new_ras_server_cfg['backup'] = True
        
        new_ras_server_cfg['backup_server_addr'] = sec_ras_cfg['IP Address']
        new_ras_server_cfg['backup_server_port'] = sec_ras_cfg['Port']
        
        new_ras_server_cfg['request_timeout'] = failover_cfg['Request Timeout'].split(' ')[0]
        new_ras_server_cfg['retry_count'] = failover_cfg['Max. Number of Retries'].split(' ')[0]
        new_ras_server_cfg['retry_interval'] = failover_cfg['Reconnect Primary'].split(' ')[0]
    elif sec_ras_cfg['Status'] == 'Disabled':
        new_ras_server_cfg['backup'] = False
        
    return new_ras_server_cfg

#*********************************************************************************
#@ZJ 2015017 NEW FEATURE: Radius over TLS
SHOW_RADIUS_STATISTICS_SERVER_NAME = 'show radius-statistics server-name \'$name\''
RESET_RADIUS_STATISTICS_SERVER_NAME = 'reset radius-statistics  server-name \'$name\''

def reset_radius_statistics(zdcli,server_name):
    cmd_block = Template(RESET_RADIUS_STATISTICS_SERVER_NAME).substitute(dict(name = server_name))
    logging.info("======reset radius statistics servers by name==========")
    radius_statistics_res = zdcli.do_cmd(cmd_block)
    expect_res = 'Reset RADIUS server %s statistics successfully' % server_name
    if radius_statistics_res == expect_res:
        radius_statistics_res = None
        return radius_statistics_res
    else:
        return radius_statistics_res
    
def get_radius_statistics(zdcli,server_name):
    '''
    {'RADIUS statistics(SVR)': 
      {'ID': 
        {'3': 
          {'Primary Server': 
            {'IP Address': '192.168.0.232', 
             'Statistics': 
               {'Access Requests': '0', 
                'Access Timeouts': '0', 
                'Access Retries': '0', 
                'Access Rejecs': '0'}, 
                'Port': '2083'}, 
          'Type': 'RADIUS server',
          'Name': 'abc', 
          'Period': 'from power on'}, 
         }
    '''
    cmd_block = Template(SHOW_RADIUS_STATISTICS_SERVER_NAME).substitute(dict(name = server_name))
    logging.info("======get radius statistics servers by name==========")
    radius_statistics_res = zdcli.do_cmd(cmd_block) 
    
    logging.info('The radius statistics server result\n:%s', radius_statistics_res)    
    radius_statistics_res = radius_statistics_res.replace("\r\r\n      Name=",":\r\r\n      Name=")
    
    radius_statistics_dict = output.parse(radius_statistics_res)  
     
    return radius_statistics_dict

def verify_info_radius_statistics(zdcli,radius_statistics_dict,server_type,expeceted_value):
    
    server_info = radius_statistics_dict['RADIUS statistics(SVR)']['ID'].values()[0]
    logging.info(server_info)
    statistics_server_info = server_info['Primary Server']['Statistics']
    
    errmsg = ''
    if server_type == "radius-acct":
        request_value = statistics_server_info['Accounting Requests']
    elif server_type == "radius-auth":
        request_value = statistics_server_info['Access Requests']
    else :
        errmsg = "The type of server is neither radius nor accounting "
        return False,errmsg
    
    if int(request_value) == int(expeceted_value):
        return True,''
    else:
        return False,'access request number inconsistent, expected %s,actual %s'%(expeceted_value,request_value)