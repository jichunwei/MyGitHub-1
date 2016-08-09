'''
Created on 2011-1-6
@author: serena.tan@ruckuswireless.com

Description: the script is used to delete the aaa servers from ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    server_name_list: a list of the aaa servers' name

Examples: 
tea.py  u.zdcli.aaaservers.delete_aaa_servers shell_key='!v54! xxx' server_name_list="['xxx', 'xxx']"
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cas


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   server_name_list = []
                   )


def do_config(kwargs):
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    if not _cfg['server_name_list']:
        msg = "Please input a list of the aaa servers' name, using the argument: server_name_list"
        raise Exception(msg)
    
    _cfg['zdcli'] = create_zd_cli_by_ip_addr(_cfg['zd_ip_addr'], _cfg['username'], _cfg['password'], _cfg['shell_key'])
    
    return _cfg


def do_test(tcfg):
    res, msg = cas.delete_aaa_servers(tcfg['zdcli'], tcfg['server_name_list'])
    
    if res:
        return ("PASS", msg)
    
    else:
        return ("FAIL", msg)

  
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
