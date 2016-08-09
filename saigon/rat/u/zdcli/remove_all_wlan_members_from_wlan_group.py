'''
Created on 2011-1-18
@author: serena.tan@ruckuswireless.com

Description: This script is used to remove all wlan members from a wlan group in ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    wg_name:    name of the wlan group

Examples: 
tea.py u.zdcli.wlan_group.remove_all_wlan_members_from_wlan_group shell_key='!v54! xxx' wg_name=xxx
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups as cwg


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    wg_name = kwargs.get('wg_name','')
    if not wg_name:
        msg = "Please input the name of the WLAN group, using argument: wg_name"
        raise Exception(msg)
    
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    _cfg['zdcli'] = create_zd_cli_by_ip_addr(_cfg['zd_ip_addr'], _cfg['username'], _cfg['password'], _cfg['shell_key'])
    
    return _cfg


def do_test(tcfg):
    res, msg = cwg.remove_all_wlan_members_from_wlan_group(tcfg['zdcli'], tcfg['wg_name'])
    if res:
        return ("PASS", msg)
    
    else:
        return ("Fail", msg)

  
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
