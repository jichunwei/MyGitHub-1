'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.12.20
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Config snmp trap via GUI: format is version 2 or 3, and related settings.

Commands samples:
tea.py u.zd.snmp.set_snmp_trap
tea.py u.zd.snmp.set_snmp_trap ip_addr='192.168.0.10'
tea.py u.zd.snmp.set_snmp_trap ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
tea.py u.zd.snmp.set_snmp_trap ip_addr='192.168.0.10' version='2' "trap_info={'1': {'server_ip':'192.168.0.10'}"
tea.py u.zd.snmp.set_snmp_trap ip_addr='192.168.0.10' version='3' trap_info="{'1': {sec_name='ruckus-read' server_ip='192.168.0.2' auth_protocol='MD5' 
                                auth_passphrase='12345678' priv_protocol='DES' priv_passphrase='12345678'}}"
tea.py u.zd.snmp.set_snmp_trap ip_addr='192.168.0.10' enabled=False
'''

import logging

from RuckusAutoTest.components import create_zd_by_ip_addr
from RuckusAutoTest.components.lib.zd.system_zd import set_snmp_trap_info

default_zd_cfg = dict(ip_addr = '192.168.0.2', 
                      username = 'admin', 
                      password = 'admin', 
                      )

#Default trap configuration for trap version 2.
default_trap_cfg = {'version': '2',
                    'enabled': True,
                    '1': {'server_ip':'192.168.0.10'},
                    '2': {'server_ip':'192.168.0.11'},
                    }

'''
default_trap_cfg = {'version': '3',
                    'enabled': True,
                    '1': {'sec_name': 'ruckus-read',
                          'server_ip': '192.168.0.2',
                          'auth_protocol': 'MD5',
                          'auth_passphrase': '12345678',
                          'priv_protocol': 'DES',
                          'priv_passphrase': '12345678',
                          },
                   }
'''

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
    conf['zd'] = create_zd_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):
    zd = conf['zd']
    logging.info('Config SNMP trap.')
    set_snmp_trap_info(zd, conf['trap_cfg'])
    
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