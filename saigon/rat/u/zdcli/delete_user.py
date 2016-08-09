'''
Created on 2010-11-23
@author: serena.tan@ruckuswireless.com

Description:

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    name:       name of the user

Examples: 
tea.py u.zdcli.delete_user shell_key='!v54! xxx' name=xxx
'''  


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import user


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   name = ''
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    if cfg['name'] == '':
        msg = 'Please input the name, using: tea.py u.zdcli.delete_user name=xxx'
        raise Exception(msg)
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    
    return cfg


def do_test(tcfg):
    user.delete_user(tcfg['zdcli'], tcfg['name'])

    return ("PASS", "Delete the user [%s] from ZD CLI successfully" % tcfg['name'])

  
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
