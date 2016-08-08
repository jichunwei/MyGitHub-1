'''
Created on 2011-1-28
@author: serena.tan@ruckuswireless.com

Description: This script is used to get the detail configuration of all APs from ZD WebUI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'

Examples: 
tea.py u.zd.get_all_ap_cfg
'''


from pprint import pformat
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd.access_points_zd import get_all_ap_cfg


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin')


def do_config(kwargs):
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    zd = create_zd_by_ip_addr(_cfg.pop('zd_ip_addr'), _cfg.pop('username'), _cfg.pop('password'))
    
    return zd


def do_test(zd):
    all_ap_cfg = get_all_ap_cfg(zd)
    
    logging.info('All AP configuration got from ZD WebUI is:\n%s' % pformat(all_ap_cfg))
    return ('PASS', 'Get all AP configuration from ZD WebUI successfully!')

  
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
