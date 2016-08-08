'''
Created on 2011-3-15
@author: serena.tan@ruckuswireless.com

Description:

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    name: 

Examples: 
tea.py u.zdcli.get_role_by_name shell_key='!v54! xxx' name=xxx
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import roles


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    name = kwargs.get('name','')
    if not name:
        msg = 'Please input the name, using: tea.py u.zdcli.get_role_by_name name=xxx'
        raise Exception(msg)
    
    _cfg = default_cfg
    _cfg.update(kwargs)
    
    _cfg['zdcli'] = create_zd_cli_by_ip_addr(_cfg['zd_ip_addr'], _cfg['username'], _cfg['password'], _cfg['shell_key'])
    
    return _cfg


def do_test(tcfg):
    roles.get_role_info_by_name(tcfg['zdcli'], tcfg['name'])
        
    return ("PASS", "Get the role [%s] from ZD CLI successfully" % tcfg['name'])

  
def do_clean_up(tcfg):
    del(tcfg['zdcli'])


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res
