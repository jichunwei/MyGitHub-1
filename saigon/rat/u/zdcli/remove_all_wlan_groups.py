'''
Created on 2011-1-18
@author: serena.tan@ruckuswireless.com

Description: the script is used to remove all wlan groups from ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'

Examples: 
tea.py u.zdcli.remove_all_wlan_groups shell_key='!v54! xxx' 
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups as cwg


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    _cfg['zdcli'] = create_zd_cli_by_ip_addr(_cfg['zd_ip_addr'], _cfg['username'], _cfg['password'], _cfg['shell_key'])
    
    return _cfg


def do_test(tcfg):
    res, msg = cwg.remove_all_wlan_groups(tcfg['zdcli'])
    
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
