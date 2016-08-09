'''
Created on 2010-7-14

@author: cwang@ruckuswireless.com
tea.py create_multi_mgmtipacl te_root=u.zd
'''

import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(number = 16)
    args.update(kwargs)
    mgmt_cnt = args['number']
    mgmt_cfg = {'name':'mgmt-ip-acl-test',
                'type':'single',
                'addr':'192.168.2.33',}
    mgmt_list = []
    for i in range(1, mgmt_cnt +1):
        mgmt_cfg_tmp = mgmt_cfg.copy()
        mgmt_cfg_tmp['name'] = 'mgmt-ip-acl-%d' % i
        mgmt_list.append(mgmt_cfg_tmp)
    
    return mgmt_list

def do_test(zd, mgmt_list):
    for mgmt in mgmt_list:
        mgmt_ip_acl.create_mgmtipacl(zd, mgmt)
        logging.info('mgmt ip acl [%s] created successfully' % mgmt['name'])
    
    return ("PASS", "mgmt ip acl list [%s] created successfully" % mgmt_list)

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        mgmt_list = do_config(**kwargs)
        res = do_test(zd, mgmt_list)
        do_clean_up() 
        return res
    finally:
        pass


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)