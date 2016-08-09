'''
Author: Serena Tan
Email: serena.tan@ruckuswireless.com

Description: To get all wlan group information from ZD GUI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username: default value is 'admin'
    password: default value is 'admin'

Examples: 
tea.py u.zd.get_all_wlan_group
'''

from pprint import pformat
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wgs

default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin')


def do_config(kwargs):
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    zd = create_zd_by_ip_addr(_cfg.pop('zd_ip_addr'), _cfg.pop('username'), _cfg.pop('password'))
    
    return zd


def do_test(zd):
    wlan_group_all = wgs.get_all_wlan_group_cfgs_2(zd)
    
    logging.info('All WLAN group information got from ZD GUI is:\n%s' % pformat(wlan_group_all))
    return ('PASS', 'Get all WLAN group information from ZD GUI successfully!')

  
def do_clean_up():
    clean_up_rat_env()


def main(**kwargs):
    zd = do_config(kwargs)
    res = None  
    try:
        res = do_test(zd)
    finally:
        do_clean_up()
    return res