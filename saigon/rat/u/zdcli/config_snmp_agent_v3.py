'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.02.05
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Config snmp agent v3, enable/disable.

Commands samples:
tea.py u.zdcli.config_snmp_agent_v3
tea.py u.zdcli.config_snmp_agent_v3 ip_addr='192.168.0.10'
tea.py u.zdcli.config_snmp_agent_v3 ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
tea.py u.zdcli.config_snmp_agent_v3 ip_addr='192.168.0.10'
                                    enable='true' ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                    ro_priv_protocol='DES' ro_priv_passphrase='12345678'
                                    rw_sec_name='ruckus-write' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                    rw_priv_protocol='DES' rw_priv_passphrase='12345678'
tea.py u.zdcli.config_snmp_agent_v3 ip_addr='192.168.0.10' enable='false'
'''

import logging

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent


default_zd_cfg = dict(ip_addr = '192.168.0.2', 
                      username = 'admin', 
                      password = 'admin', 
                      shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
                      )

default_agent_v3_cfg = {'version': '3',
                        'enable': 'true',
                        'ro_sec_name': 'ruckus-read',            
                        'ro_auth_protocol': 'MD5',
                        'ro_auth_passphrase': '12345678',
                        'ro_priv_protocol': 'DES',
                        'ro_priv_passphrase': '12345678',
                        'rw_sec_name': 'ruckus-write',
                        'rw_auth_protocol': 'MD5',
                        'rw_auth_passphrase': '12345678',
                        'rw_priv_protocol': 'DES',
                        'rw_priv_passphrase': '12345678',
                        }

def do_config(**kwargs):
    zd_cfg = default_zd_cfg
    agent_v3_cfg = default_agent_v3_cfg
    for k, v in kwargs.items():
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
        if agent_v3_cfg.has_key(k):
            agent_v3_cfg[k] = v
        
    conf = {}
    conf.update(zd_cfg)
        
    conf['v3_cfg'] = agent_v3_cfg
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):
    zdcli = conf['zd_cli']
    logging.info('Config SNMP agent v3.')
    config_snmp_agent(zdcli, conf['v3_cfg'])
    
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