'''
Created on 2010-7-16

@author: cwang@ruckuswireless.com
'''
from contrib.wlandemo import defaultWlanConfigParams as wlan_param_helper
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(num_of_wlans = 32,
                num_of_wgs = 31)
    args.update(kwargs)
    w_cnt = args['num_of_wlans']
    wgs_cnt = args['num_of_wgs']
    wlan_cfg = wlan_param_helper.get_cfg('open-none')
    wlan_list = []
    for i in range(1, w_cnt + 1):
        wlan_cfg_tmp = wlan_cfg.copy()
        wlan_cfg_tmp['ssid'] = 'open-none-%d' % i
        wlan_list.append(wlan_cfg_tmp)
     
    return (wlan_list, wgs_cnt)

def do_test(zd, wlan_list, wgs_cnt):
    lib.zd.wgs.create_multi_wlan_groups(zd, 'wlan_groups_test', wlan_list, num_of_wgs = wgs_cnt)
    return ("PASS", "All of WLANs and WGS created successfully")

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        (wlan_list, wgs_cnt) = do_config(**kwargs)
        res = do_test(zd, wlan_list, wgs_cnt)
        do_clean_up() 
        return res
    finally:
        pass


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)