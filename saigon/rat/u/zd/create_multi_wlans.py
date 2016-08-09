'''
Created on 2010-7-16

@author: cwang@ruckuswireless.com
tea.py create_multi_wlans te_root=u.zd
'''
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from contrib.wlandemo import defaultWlanConfigParams as wlan_param_helper

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(num_of_wlans = 32)
    args.update(kwargs)
    w_cnt = args['num_of_wlans']
    wlan_cfg = wlan_param_helper.get_cfg('open-none')
    wlan_list = []
    for i in range(1, w_cnt + 1):
        wlan_cfg_tmp = wlan_cfg.copy()
        wlan_cfg_tmp['ssid'] = 'open-none-%d' % i
        wlan_list.append(wlan_cfg_tmp)
    
    return wlan_list

def do_test(zd, wlan_list):
    for wlan in wlan_list:
        zd.cfg_wlan(wlan)
        logging.info('WLAN [%s] created successfully' % wlan['ssid'])
        
    return ('PASS', "All of WLANs created successfully")

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        wlan_list = do_config(**kwargs)
        res = do_test(zd, wlan_list)
        do_clean_up() 
        return res
    finally:
        pass

if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)