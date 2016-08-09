'''
Created on 2010-12-21
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify the information of all users in ZD CLI by comparing to GUI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'

Examples: 
tea.py u.zdcli.verify_all_users shell_key='!v54! xxx'
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import user as cli_user
from RuckusAutoTest.components.lib.zd import user as gui_user
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    cfg['zd'] = create_zd_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'])
    
    return cfg


def do_test(tcfg):
    gui_info_list = gui_user.get_all_users(tcfg['zd'])
    cli_info_dict = cli_user.get_user_all(tcfg['zdcli'])
    
    res = cli_user.verify_all_user_by_gui(cli_info_dict, gui_info_list)
    if res:
        return ("PASS", "Verify all users in ZD CLI by GUI successfully!")
    
    else:
        return ("Fail", "Fail to verify all users in ZD CLI by GUI!")

  
def do_clean_up(zdcli):
    del(zdcli)
    clean_up_rat_env()


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res
