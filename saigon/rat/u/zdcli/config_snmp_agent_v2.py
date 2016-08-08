'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.02.05
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Config snmp agent v2, enable and disable.

Commands samples:
tea.py u.zdcli.config_snmp_agent_v2
tea.py u.zdcli.config_snmp_agent_v2 ip_addr='192.168.0.10'
tea.py u.zdcli.config_snmp_agent_v2 ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
tea.py u.zdcli.config_snmp_agent_v2 ip_addr='192.168.0.10' enable='true' ro_community='public' rw_community='private' contact='cherry.cheng@ruckuswireless.com' location='shenzhen'
tea.py u.zdcli.config_snmp_agent_v2 ip_addr='192.168.0.10' enable='false'
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent

default_zd_cfg = dict(ip_addr = '192.168.0.2', 
                      username = 'admin', 
                      password = 'admin', 
                      shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
                      )

default_agent_v2_cfg = {'version': '2',
                        'enable': 'true',
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
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):
    zdcli = conf['zd_cli']
    logging.info('Config SNMP agent v2.')
    config_snmp_agent(zdcli, conf['v2_cfg'])
    
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