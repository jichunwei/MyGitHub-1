'''
Created on 2010-7-14

@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(number = 40, map_path = 'D:\\p4\\tools\\rat-branches\\saigon\\rat\\RuckusAutoTest\\scripts\\zd\\maps\\map_test.png')
    args.update(kwargs)
    map_cnt = args['number']
    map_cfg = dict(name  = '', map_path = '')
    map_cfg['map_path'] = args['map_path']
    map_list = []
    for i in range(1, map_cnt + 1):
        map_cfg_tmp = map_cfg.copy()
        map_cfg_tmp['name'] = 'Test_Maps_%d' % i
        map_list.append(map_cfg_tmp)
    
    return map_list
    
def do_test(zd, map_list):
    for map in map_list:
        zd.create_map(map['name'], map['map_path'])
        logging.info('map [%s]create successfully' % map['name'])
        
    return ("PASS", "Maps [%s]create successfully" % map_list)

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        map_list = do_config(**kwargs)
        res = do_test(zd, map_list)
        do_clean_up() 
        return res
    finally:
        pass


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)