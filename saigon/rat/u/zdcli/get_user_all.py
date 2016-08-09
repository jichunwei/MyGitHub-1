'''
Created on 2010-11-5
@author: serena.tan@ruckuswireless.com

Description: This tea program is used to get a dictionary of all users information from zd cli.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'

Examples: 
tea.py u.zdcli.u.zdcli.get_user_all shell_key='!v54! xxx'
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import user


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    zdcli = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    
    return zdcli


def do_test(zdcli):
    info = user.get_user_all(zdcli)

    return ("PASS", "Get all users from ZD CLI successfully: %s" %info)

  
def do_clean_up(zdcli):
    del(zdcli)


def main(**kwargs):
    zdcli = do_config(kwargs)
    res = None  
    try:
        res = do_test(zdcli)
    finally:
        do_clean_up(zdcli)
    return res
