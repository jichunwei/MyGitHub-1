'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.02.05
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Config snmp trap: format is version 2 or 3, and related settings.

Commands samples:
tea.py u.zdcli.config_snmp_trap
tea.py u.zdcli.config_snmp_trap ip_addr='192.168.0.10'
tea.py u.zdcli.config_snmp_trap ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
tea.py u.zdcli.config_snmp_trap ip_addr='192.168.0.10' version='2' server_ip='192.168.0.2'
tea.py u.zdcli.config_snmp_trap ip_addr='192.168.0.10' version='3' sec_name='ruckus-read' server_ip='192.168.0.2' auth_protocol='MD5' 
                                auth_passphrase='12345678' priv_protocol='DES' priv_passphrase='12345678'
tea.py u.zdcli.config_snmp_trap ip_addr='192.168.0.10' enable='false'
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_trap

default_zd_cfg = dict(ip_addr = '192.168.0.2', 
                      username = 'admin', 
                      password = 'admin', 
                      shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
                      )

default_trap_cfg = {'version': '2',
                    'enable': 'true',
                    'sec_name': 'ruckus-read',
                    'server_ip': '192.168.0.2',
                    'auth_protocol': 'MD5',
                    'auth_passphrase': '12345678',
                    'priv_protocol': 'DES',
                    'priv_passphrase': '12345678',
                    }

def do_config(**kwargs):
    zd_cfg = default_zd_cfg
    trap_cfg = default_trap_cfg
    for k, v in kwargs.items():
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
        if trap_cfg.has_key(k):
            trap_cfg[k] = v
        
    conf = {}
    conf.update(zd_cfg)
        
    conf['trap_cfg'] = trap_cfg
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):
    zdcli = conf['zd_cli']
    logging.info('Config SNMP trap.')
    config_snmp_trap(zdcli, conf['trap_cfg'])
    
    return('PASS')

def do_clean_up(conf):
    pass    
    
def main(**kwargs):
    cfg = {}
    try:
        cfg = do_config(**kwargs)        
        res = do_test(cfg)         
        return res
    finally:
        do_clean_up(cfg)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)