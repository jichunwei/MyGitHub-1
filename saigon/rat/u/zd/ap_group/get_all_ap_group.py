'''

How to:
    tea.py u.zd.ap_group.get_all_ap_group 

Created on 2011-10-20
@author: cwang@ruckuswireless.com
'''
import copy
import logging
from pprint import pprint as pp

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components.lib.zd import ap_group

default_cfg = dict(ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin')


def do_config():
    zd = create_zd_by_ip_addr(**default_cfg)
    return zd

def do_test(zd):
    info = ap_group.get_all_ap_group_cfg(zd)
    return ('PASS', info)

def do_cleanup():
    clean_up_rat_env()

def main(**kwargs):
    zd = do_config()
    try:        
        return do_test(zd)
    except:
        pass
    finally:
        do_cleanup()
