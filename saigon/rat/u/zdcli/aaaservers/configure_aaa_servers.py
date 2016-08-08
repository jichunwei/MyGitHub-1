'''
Created on 2011-1-4
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure aaa servers in ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    server_cfg_list: a list of the servers cfg

Examples: 
tea.py u.zdcli.aaaservers.configure_aaa_servers shell_key='!v54! xxx'
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


server_cfg_list = [{'server_name': 'ruckus_ad_1', 'type': 'ad', 'global_catalog': False, 'server_addr': '192.168.0.252',
                    'server_port': '389', 'win_domain_name': 'domain.ruckuswireless.com'},
                    
                   {'server_name': 'ruckus_ad_2', 'type': 'ad', 'global_catalog': True, 'server_addr': '192.168.0.252',
                    'server_port': '389', 'win_domain_name': 'domain.ruckuswireless.com', 
                    'admin_domin_name': 'admin@domain.ruckuswireless.com', 'admin_password': '1234567890'},
                    
                    {'server_name': 'ruckus_ldap', 'type': 'ldap', 'server_addr': '192.168.0.252', 'server_port': '389',
                     'win_domain_name': 'domain.ruckuswireless.com', 'admin_domin_name': 'admin@domain.ruckuswireless.com',
                     'admin_password': '1234567890', 'ldap_key_attribute': 'uid', 'ldap_search_filter': 'objectClass=*', },
                     
                    {'server_name': 'ruckus_radius_auth', 'type': 'radius-auth', 'backup': False,
                     'server_addr': '192.168.0.252', 'server_port': '1812', 'radius_secret': '1234567890', },
                     
                    {'server_name': 'ruckus_radius_acct', 'type': 'radius-acct', 'backup': True,
                     'server_addr': '192.168.0.252', 'server_port': '1813', 'radius_secret': '1234567890',
                     'backup_server_addr': '192.168.0.250', 'backup_server_port': '1813', 'backup_radius_secret': '1234567890',
                     'request_timeout': '3', 'retry_count': '2', 'retry_interval': '5'}
                    ]

default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   server_cfg_list = server_cfg_list
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    
    return cfg


def do_test(tcfg):
    res, msg = cas.configure_aaa_servers(tcfg['zdcli'], tcfg['server_cfg_list'])
    
    if res:
        return ("PASS", msg)
    
    else:
        return ("Fail", msg)

  
def do_clean_up(zdcli):
    del(zdcli)


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res
