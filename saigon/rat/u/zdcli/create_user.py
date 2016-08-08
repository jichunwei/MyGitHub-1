'''
Created on 2010-11-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to create users in ZD via CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    zd_username:   default value is 'admin'
    zd_password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    name:
    fullname:
    role: 
    password:
    number:

Examples: 
tea.py u.zdcli.create_user shell_key='!v54! xxx' name=xxx password=xxx
tea.py u.zdcli.create_user shell_key='!v54! xxx' name=xxx password=xxx number=xxx
tea.py u.zdcli.create_user shell_key='!v54! xxx' name=xxx fullname=xxx role=xxx password=xxx number=xxx
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import user


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   zd_username = 'admin', 
                   zd_password = 'admin', 
                   shell_key = '!v54!',
                   name = '',
                   fullname = '',
                   role = '',
                   password = '',
                   number = 1,
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    if cfg['name'] == '':
        msg = "Please input the name of the user, using 'name=xxx'."
        raise Exception(msg)
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['zd_username'], cfg['zd_password'], cfg['shell_key'])
    
    return cfg


def do_test(tcfg):
    res = user.create_user(tcfg['zdcli'], tcfg['name'], tcfg['fullname'], tcfg['role'], tcfg['password'], tcfg['number'])
    
    if res:
        return ("PASS", "Create users in ZD CLI successfully")
    
    else:
        return ("Fail", "Fail to create users in ZD CLI")

  
def do_clean_up(tcfg):
    del(tcfg['zdcli'])


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res
