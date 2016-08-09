'''
Created on 2010-10-26
@author: cwang@ruckuswireless.com

tea.py chk_ldap_server te_root=u.zdcliu.zdcli.aaaservers
'''

from RuckusAutoTest.components.lib.zdcli import aaa_servers as svr_lib
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,  
)

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    args = dict(server_name = 'LDAP')
    args.update(kwargs)
    server_name = args['server_name']
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    res_d = svr_lib.get_aaa_server_by_name(zdcli, server_name)
    return (zdcli, res_d)

def do_test(zdcli, res_d):
    aaa = res_d['AAA']
    id = aaa['ID']
    svr_d = id.values()[0]
    ldap_server = {
        'server_name': 'LDAP',
        'server_addr':'192.168.0.252',
        'server_port':'389',
        'ldap_search_base':'dc=example,dc=net',
        'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
        'ldap_admin_pwd': 'lab4man1'
    }
    r, c = svr_lib.verify_aaa_server_by_type(zdcli, ldap_server, svr_d, svr_lib.LDAP)
    if r:
        return ("PASS", "")
    else:
        return ("FAIL", c)

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    
    try:
        zdcli, res_d = do_config(**kwargs)
        res = do_test(zdcli, res_d)
        return res
    finally:
        do_clean_up()


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)