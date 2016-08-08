'''
Created on 2010-7-14

@author: cwang@ruckuswireless.com
tea.py create_multi_aaa_servers te_root=u.zd
'''

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(number=32)
    args.update(kwargs)
    server_cnt = args['number']
    server_cfg = {'server_addr': '192.168.0.252', 'server_port': '1812', 'server_name': 'radius_server',
                  'win_domain_name': '', 'ldap_search_base': '',
                  'ldap_admin_dn': '', 'ldap_admin_pwd': '',
                  'radius_auth_secret': '1234567890', 'radius_acct_secret': ''}
    server_list = []
    for i in range(1, server_cnt+1):
        s_cfg_tmp = server_cfg.copy()
        s_cfg_tmp['server_name'] = 'radius_server_%d' % i
        server_list.append(s_cfg_tmp)
    
    return server_list    

def do_test(zd, server_list):
    for server in server_list:
        lib.zd.aaa.create_server(zd, **server)
    
    return ("PASS", "All servers [%s] create successfully" % server_list)
        

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        server_list = do_config(**kwargs)
        res = do_test(zd, server_list)
        do_clean_up() 
        return res
    finally:
        pass


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)