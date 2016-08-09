'''
Created on 2010-7-14
@author: cwang@ruckuswireless.com
tea.py create_multi_roles te_root=u.zd
tea.py create_multi_roles te_root=u.zd number=10
'''
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')

def do_config(**kwargs):
    args = dict(number=31)
    args.update(kwargs)
    cnt = args['number']
    role_cfg = {"rolename": "", "specify_wlan": "", "guestpass": True, "description": "",
                "group_attr": "", "zd_admin": ""}
    role_list = []
    for i in range(1, cnt+1):
        role_cfg_tmp = role_cfg.copy()
        role_cfg_tmp['rolename'] = 'Test_Role_%d' % i
        role_list.append(role_cfg_tmp)
    
    return role_list

def do_test(zd, role_list):
    for role_cfg in role_list:
        zd.create_role(**role_cfg)
        logging.info('role [%s] create successfully' % role_cfg['rolename'])
        
    return ("PASS", "[%s] created successfully" % role_list)

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        role_list = do_config(**kwargs)
        res = do_test(zd, role_list)
        do_clean_up() 
        return res
    finally:
        pass


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)