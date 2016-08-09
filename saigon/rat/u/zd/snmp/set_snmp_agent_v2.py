'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.12.20
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Config snmp agent v2 via GUI, enable and disable.

Commands samples:
tea.py u.zd.snmp.set_snmp_agent_v2
tea.py u.zd.snmp.set_snmp_agent_v2 ip_addr='192.168.0.10'
tea.py u.zd.snmp.set_snmp_agent_v2 ip_addr='192.168.0.10' username='admin' password='admin' 
tea.py u.zd.snmp.set_snmp_agent_v2 ip_addr='192.168.0.10' enabled=True ro_community='public' rw_community='private' contact='cherry.cheng@ruckuswireless.com' location='shenzhen'
tea.py u.zd.snmp.set_snmp_agent_v2 ip_addr='192.168.0.10' enabled=False
'''

import logging

from RuckusAutoTest.components import create_zd_by_ip_addr
from RuckusAutoTest.components.lib.zd.system_zd import set_snmp_agent_info

default_zd_cfg = dict(ip_addr = '192.168.0.2', 
                      username = 'admin', 
                      password = 'admin', 
                      )

default_agent_v2_cfg = {'version': '2',
                        'enabled': True,
                        'ro_community': 'public',
                        'rw_community': 'private',
                        'contact': 'support@ruckuswireless.com',
                        'location': 'Shenzhen',
                        }

def do_config(**kwargs):
    zd_cfg = default_zd_cfg
    agent_v2_cfg = default_agent_v2_cfg
    for k, v in kwargs.items():
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
        if agent_v2_cfg.has_key(k):
            agent_v2_cfg[k] = v
        
    conf = {}
    conf.update(zd_cfg)
        
    conf['v2_cfg'] = agent_v2_cfg
    conf['zd'] = create_zd_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):
    zd = conf['zd']
    logging.info('Config SNMP agent v2 via GUI.')
    set_snmp_agent_info(zd, conf['v2_cfg'])
    
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