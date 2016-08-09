'''
Created on 2011-1-19
@author: serena.tan@ruckuswireless.com

Description: This tea program is used to get all wlan name from ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'

Examples: 
tea.py u.zdcli.get_all_wlan_name shell_key='!v54! xxx' 
'''


import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi


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
    logging.info('Get all wlan name from ZD CLI.')
    wlan_name_list = gwi.get_all_wlan_name_list(zdcli)

    return ("PASS", "Get all wlan name from ZD CLI successfully: %s" % wlan_name_list)

  
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

