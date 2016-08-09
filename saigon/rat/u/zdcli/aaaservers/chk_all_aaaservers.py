'''
Created on 2010-10-26
@author: cwang@ruckuswireless.com

tea.py chk_all_aaaservers te_root=u.zdcliu.zdcli.aaaservers
'''

from RuckusAutoTest.components.lib.zdcli import aaa_servers as svr_lib
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,  
)

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    args = dict()
    args.update(kwargs)
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    res_d = svr_lib.get_all_aaa_servers(zdcli)
    return (zdcli, res_d)

def do_test(zdcli, res_d):
    aaa = res_d['AAA']
    id = aaa['ID']
    svr_list = id.values()
    ad_server = {
        'server_name': 'ACTIVE_DIRECTORY',
        'server_addr': '192.168.0.250',
        'server_port': '389',
        'win_domain_name': 'rat.ruckuswireless.com',
    }
    
    ldap_server = {
        'server_name': 'LDAP',
        'server_addr':'192.168.0.252',
        'server_port':'389',
        'ldap_search_base':'dc=example,dc=net',
        'ldap_admin_dn': 'cn=Manager,dc=example,dc=net',
        'ldap_admin_pwd': 'lab4man1'
    }
   

    radius_server = {
        'server_name': 'RADIUS',
        'server_addr': '192.168.0.252',
        'radius_auth_secret': '1234567890',
        'server_port': '1812'
    }
    
        
    radius_acc_server = {
        'server_name': 'RADIUS Accounting',
        'server_addr': '192.168.0.252',
        'radius_acct_secret': '1234567890',
        'server_port': '1813'
    }
    pass_msg = []
    err_msg = []
    for svr_d in svr_list:
        name = svr_d['Name']
        if name == ad_server['server_name']:
            _chk_svr_info(zdcli, ad_server, svr_d, name, svr_lib.AD, pass_msg, err_msg)
        elif name == ldap_server['server_name']:
            _chk_svr_info(zdcli, ldap_server, svr_d, name, svr_lib.LDAP, pass_msg, err_msg)                        
        elif name == radius_server['server_name']:
            _chk_svr_info(zdcli, radius_server, svr_d, name, svr_lib.RADIUS, pass_msg, err_msg)            
        elif name == radius_acc_server['server_name']:
            _chk_svr_info(zdcli, radius_acc_server, svr_d, name, svr_lib.RADIUS_ACC, pass_msg, err_msg)
    
    if err_msg:
        return ("FAIL", err_msg)
    elif len(pass_msg) < 4:
        return ("FAIL", 'Miss some of servers, please check')
    else:
        return ("PASS", pass_msg)

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    
    try:
        zdcli, res_d = do_config(**kwargs)
        res = do_test(zdcli, res_d)
        return res
    finally:
        do_clean_up()


def _chk_svr_info(zdcli, gui_d, cli_d, name, type, pass_msg, error_msg):
    r, c = svr_lib.verify_aaa_server_by_type(zdcli, gui_d, cli_d, type)
    if r:
        pass_msg.append('server [%s] existed and information checking is correct' % name)
    else:
        error_msg.append(c)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)