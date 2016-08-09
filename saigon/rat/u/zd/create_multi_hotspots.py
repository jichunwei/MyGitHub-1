'''
Created on 2010-7-16

@author: cwang@ruckuswireless.com
tea.py create_multi_hotspots te_root=u.zd
'''
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(num_of_rules = 16,
                num_of_hotspots = 32,
                )
    args.update(kwargs)
    h_cnt = args['num_of_hotspots']
    r_cnt = args['num_of_rules']
    h_cfg = {
        'name': '',
        'login_page': 'http://www.example.net',
        'start_page': None,
        'session_timeout': None,
        'idle_timeout': None,
        'auth_svr': '',
        'acct_svr': '',
        'interim_update_interval': None,
        'radius_location_id': '',
        'radius_location_name': '',
        'walled_garden_list': [],
        'restricted_subnet_list': [],
        'enable_mac_auth': None,
    }
    r_cfg = {'description': '',
              'action': 'Allow',
              'destination_addr': 'Any',
              'application': 'Any',
              'protocol': None,
              'destination_port': None,
              }
    r_list = []
    for i in range(1, r_cnt + 1):
        r_list.append(r_cfg.copy())
        
    h_cfg['restricted_subnet_list'] = r_list
    h_list = []
    for i in range(1, h_cnt + 1):
        h_cfg_tmp = h_cfg.copy()
        h_cfg_tmp['name'] = 'Test_Hotspots_%d' % i
        h_list.append(h_cfg_tmp)
    
    return h_list

def do_test(zd, h_list):
    h_cfg = h_list.pop()
    lib.zd.wispr.create_profile(zd, **h_cfg)
    logging.info('hotspot [%s] created successfully' % h_cfg['name'])
    for h in h_list:
        lib.zd.wispr.clone_profile(zd, h_cfg['name'], h['name'])
        logging.info('hotspot [%s] cloned successfully' % h['name'])        
    
    return ("PASS", "Hotspot service created successfully")

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        h_list = do_config(**kwargs)
        res = do_test(zd, h_list)
        do_clean_up() 
        return res
    finally:
        pass

if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)