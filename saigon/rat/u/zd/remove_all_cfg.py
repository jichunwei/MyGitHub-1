'''
Created on 2010-12-13
@author: serena.tan@ruckuswireless.com

Description: This script is used to remove all configuration from ZD.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'

Examples: 
tea.py u.zd.remove_all_cfg
Updated by cwang@2012-7-4
'''

import logging
import time
import traceback

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components import Helpers


default_cfg = dict(ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   )


def do_config(kwargs):
#    cfg = default_cfg
#    cfg.update(kwargs)
#    
    cnt = 3
    while cnt:
        try:
            # Initialize the DUT component
            zd = create_zd_by_ip_addr(**default_cfg)
            break;
        except Exception, e:
            cnt = cnt-1                    
            logging.debug(traceback.format_exc())

    return zd


def do_test(zd):
    ap_mac_list = Helpers.zd.aps.get_all_ap_mac_list(zd)
    zd.remove_all_cfg(ap_mac_list)

    return ("PASS", "Remove all configuration form ZD successfully")

  
def do_clean_up():
    clean_up_rat_env()


def main(**kwargs):
    zd = do_config(kwargs)
    res = None 
    s_time = time.time() 
    try:
        res = do_test(zd)
    finally:
        do_clean_up()
        logging.info('Elapse time%d' % (time.time() - s_time))
        
    return res
