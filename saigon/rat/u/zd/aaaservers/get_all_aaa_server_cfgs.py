'''
Created on Jan 8, 2011
@author: serena.tan@ruckuswireless.com

Description: the script is used to get a list of all aaa servers' cfg from ZD GUI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'

Examples: 
tea.py u.zd.aaaservers.get_all_aaa_server_cfgs
'''


from RuckusAutoTest.components.lib.zd import aaa_servers_zd
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   )


def do_config(kwargs):
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg.pop('zd_ip_addr'), _cfg.pop('username'), _cfg.pop('password'))
    
    return _cfg


def do_test(tcfg):
    print "Get the cfg of all aaa servers from ZD GUI."
    
    server_cfg_list = aaa_servers_zd.get_all_server_cfg_list(tcfg['zd'])
    
    print "The cfg of all aaa servers is %s" % server_cfg_list
    
    return ('PASS', 'Get the cfg of all aaa servers successfully')

  
def do_clean_up():
    clean_up_rat_env()


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up()
    return res
