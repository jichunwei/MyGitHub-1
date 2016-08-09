'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.12.20
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Config snmp agent v3 via GUI, enable/disable.

Commands samples:
tea.py u.zd.snmp.set_snmp_agent_v3
tea.py u.zd.snmp.set_snmp_agent_v3 ip_addr='192.168.0.10'
tea.py u.zd.snmp.set_snmp_agent_v3 ip_addr='192.168.0.10' username='admin' password='admin'
tea.py u.zd.snmp.set_snmp_agent_v3 ip_addr='192.168.0.10'
                                    enabled=True ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                    ro_priv_protocol='DES' ro_priv_passphrase='12345678'
                                    rw_sec_name='ruckus-write' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                    rw_priv_protocol='DES' rw_priv_passphrase='12345678'
tea.py u.zd.snmp.set_snmp_agent_v3 ip_addr='192.168.0.10' enabled=False
'''

import logging

from RuckusAutoTest.components import create_zd_by_ip_addr
from RuckusAutoTest.components.lib.zd.system_zd import set_snmp_agent_v3_info


default_zd_cfg = dict(ip_addr = '192.168.0.2', 
                      username = 'admin', 
                      password = 'admin'
                      )

default_agent_v3_cfg = {'version': '3',
                        'enabled': True,
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
    conf['zd'] = create_zd_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):
    zd = conf['zd']
    logging.info('Config SNMP agent v3 via GUI.')
    set_snmp_agent_v3_info(zd, conf['v3_cfg'])
    
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