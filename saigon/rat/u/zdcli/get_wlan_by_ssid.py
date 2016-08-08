'''
Author: Serena Tan
Email: serena.tan@ruckuswireless.com

Description: To get the information of wlan by ssid from ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username: default value is 'admin'
    password: default value is 'admin'
    shell_key: default value is '!v54!'

Examples: 
tea.py u.zdcli.get_wlan_by_ssid ssid=xxx shell_key='!v54! xxx'
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   )


def do_config(kwargs):
    ssid = kwargs.get('ssid','')
    if not ssid:
        msg = 'Please input the ssid, using: tea.py u.zdcli.get_wlan_by_ssid ssid=xxx'
        raise Exception(msg)
    
    _cfg = default_cfg
    _cfg.update(kwargs)
    _cfg['zdcli'] = create_zd_cli_by_ip_addr(_cfg['zd_ip_addr'], _cfg['username'], _cfg['password'], _cfg['shell_key'])
    
    return _cfg


def do_test(tcfg):
    gwi.get_wlan_by_ssid(tcfg['zdcli'], tcfg['ssid'])

    return ("PASS", "Get the wlan [%s] from ZD CLI successfully" % tcfg['ssid'])

  
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
