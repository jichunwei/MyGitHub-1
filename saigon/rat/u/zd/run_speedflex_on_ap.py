# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
   Description: Go to Monitor -> Access Points page to run SpeedFlex test for specific AP
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2010
   
   tea.py u.zd.run_speedflex_on_ap |[ap_ip=target AP IP address - Required]
                                   |[ip_addr=ZD IP address][username=ZD login user name][password=ZD login password]
   
   Ex: tea.py u.zd.run_speedflex_on_ap ip_addr=192.168.0.2
"""

import copy
from pprint import pformat

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components import Helpers as lib

zdcfg = dict(
    ip_addr = '192.168.0.2',
    username = 'admin',
    password = 'admin',
)

apcfg = dict(ap_ip = '',
             )

def get_default_cfg():
    conf = {}
    conf.update(zdcfg)
    conf.update(apcfg)    
    return conf

def do_config(cfg):
    _cfg = get_default_cfg()
    _cfg.update(cfg)
    _cfg['zd'] = create_zd_by_ip_addr(_cfg.pop('ip_addr'))

    return _cfg

def do_test(cfg):
    # Unit test for Dashboard management
    zd = cfg['zd']
    ap_ip = cfg['ap_ip']
    ap_mac = ''
    ap_info_list = lib.zd.ap.get_all_ap_info(zd)
    for ap_info in ap_info_list.values():
        if ap_info['ip_address'] == ap_ip:
            ap_mac = ap_info['mac_address']
            print 'Found the AP on ZoneDirector:\n %s' % pformat(ap_info, 4, 20)
            break
        
    if not ap_mac:
        cfg['result'] = 'FAIL' 
        cfg['message'] = '[TEST BROKEN]Could not find the AP[%s] in ZoneDirector' % ap_ip
        return cfg
        
    res = lib.zd.sp.run_monitor_speedflex_performance(zd, ap_ip, ap_mac)
    print 'SpeedFlex result on AP[%s]:\n %s' % (ap_ip, pformat(res, 4, 20)) 
    
    cfg['result'] = 'PASS'
    cfg['message'] = 'SpeedFlex result on AP[%s]: %s' % (ap_ip, res)    
    return cfg

def do_clean_up(cfg):
    clean_up_rat_env()

def main(**kwa):
    tcfg = do_config(kwa)

    res = None
    try:
        res = do_test(tcfg)

    except Exception, ex:
        print ex.message

    do_clean_up(tcfg)

    return res