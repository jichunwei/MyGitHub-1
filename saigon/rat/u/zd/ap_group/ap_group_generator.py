'''
How To:
    tea.py u.zd.ap_group.ap_group_generator 
Created on 2011-11-1
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
    return create_zd_by_ip_addr(**default_cfg)


def do_test(zd, **kwargs):
    num = kwargs['num']
    for i in range(num):
        name = 'test_%d' % i
        ap_group.create_ap_group(zd, name)
    
    return ('PASS', '%d AP group created successfully.' % num)

def do_cleanup():
    clean_up_rat_env()

def main(**kwargs):
    #ZD1000:32
    #ZD1100:32
    #ZD3000:256
    #ZD5000:512
    cfg={'num':256,}
    cfg.update(kwargs)
    zd = do_config()
    try:
        return do_test(zd, **cfg)
    except Exception, e:
        return ('ERROR', e)
    finally:
        do_cleanup()

