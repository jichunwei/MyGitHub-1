'''
Created on 2010-7-14

@author: cwang@ruckuswireless.com
tea.py create_multi_l2_acls te_root=u.zd
'''
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')

def do_config(**kwargs):
    args = dict(num_of_acl_entries = 32,
                num_of_mac = 128,
                acl_policy = True)
    args.update(kwargs)
    acl_list = []
    acl_cnt = args['num_of_acl_entries']
    mac_cnt = args['num_of_mac']
    mac_list = _generate_mac_addr(mac_cnt)
    for i in range(1, acl_cnt+1):        
        acl_cfg = dict(acl_name = 'Test_ACLs_%d' % i, acl_policy = args['acl_policy'], mac_list = mac_list)
        acl_list.append(acl_cfg)
    
    return acl_list

        
def do_test(zd, acl_list):
    acl_cfg = acl_list.pop()
    acl_name = acl_cfg['acl_name']
    zd.create_acl_rule([acl_name], acl_cfg['mac_list'], acl_cfg['acl_policy'])
    logging.info("ACL [%s] create successfully" % acl_cfg['acl_name'])
    
    for acl_cfg in acl_list:
        #just clone rules, don't create new rules
        acl_cfg['rules'] = None
        zd.clone_acl_rule(acl_name, acl_cfg)
        logging.info("ACL [%s] clone successfully" % acl_cfg['acl_name'])
    
    return ("PASS", "ACLs [%s]create successfully" % acl_list)


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


def _generate_mac_addr(num=128):
    mac_list = []
    for i in range(num):            
        mac = [0, 0, 0, 0, 0, i+1]
        mac = ':'.join(map(lambda x: "%02x" % x, mac))
#            if not mac_list.__contains__(mac):
        mac_list.append(mac)
            
    return mac_list

    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)