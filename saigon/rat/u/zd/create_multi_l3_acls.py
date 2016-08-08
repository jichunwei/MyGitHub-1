'''
Created on 2010-7-14

@author: cwang@ruckuswireless.com
tea.py create_multi_l3_acls te_root=u.zd
'''
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')

def do_config(**kwargs):
    args = dict(num_of_acls = 32,
                num_of_rules = 29,)
    r_cfg = dict(order = '1',
                  description = None,
                  action = '',
                  dst_addr = None,
                  application = None,
                  protocol = None,
                  dst_port = None
                  )    
    args.update(kwargs)
    acl_cnt = args['num_of_acls']
    rule_cnt = args['num_of_rules']
    acl_list = []
    rule_list = []
    for i in range(3, rule_cnt + 3):
        r_cfg_tmp = r_cfg.copy()
        r_cfg_tmp['order'] = '%d' % i
        rule_list.append(r_cfg_tmp)
        
    acl_cfg = {'name':'L3 ACL ALLOW ALL', 'description': '','default_mode': 'allow-all', 'rules': rule_list}
    for i in range(1, acl_cnt + 1):
        acl_cfg_tmp = acl_cfg.copy()
        acl_cfg_tmp['name'] = 'Test_ACLs_%d' % i
        acl_list.append(acl_cfg_tmp)
    
    return acl_list         

def do_test(zd, acl_list):
    acl_cfg = acl_list.pop()
    lib.zd.ac.create_multi_l3_acl_policies(zd, [acl_cfg])
    
    for acl in acl_list:
        acl_tmp = acl.copy()
        acl_tmp['rules'] = None
        lib.zd.ac.clone_l3_acl_policy(zd, acl_cfg['name'], acl_tmp)
        logging.info('L3 ACL [%s] cloned successfully' % acl['name'])
        
    logging.info("all of L3 ACL created successfully")
    return("PASS", "ACL [%s]created successfully" % acl_list)

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        acl_list = do_config(**kwargs)
        res = do_test(zd, acl_list)
        do_clean_up() 
        return res
    finally:
        pass

if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)