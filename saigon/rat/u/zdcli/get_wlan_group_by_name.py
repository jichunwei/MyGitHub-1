'''
Author: Serena Tan
Email: serena.tan@ruckuswireless.com

Description: To get the information of wlan group by name from ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username: default value is 'admin'
    password: default value is 'admin'
    shell_key: default value is '!v54!'

Examples: 
tea.py u.zdcli.get_wlan_group_by_name name=xxx shell_key='!v54! xxx'
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import get_wlan_group as gwg


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    name = kwargs.get('name','')
    if not name:
        msg = 'Please input the name, using: tea.py u.zdcli.get_wlan_group_by_name name=xxx'
        raise Exception(msg)
    
    _cfg = default_cfg
    _cfg.update(kwargs)
    _cfg['zdcli'] = create_zd_cli_by_ip_addr(_cfg['zd_ip_addr'], _cfg['username'], _cfg['password'], _cfg['shell_key'])
    
    return _cfg


def do_test(tcfg):
    gwg.get_wlan_group_by_name(tcfg['zdcli'], tcfg['name'])

    return ("PASS", "Get the wlan group [%s] from ZD CLI successfully" % tcfg['name'])

  
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
