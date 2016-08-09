'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.12.20
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Get snmp agent v2, v3 and snmp trap information via GUI.

Commands samples:
tea.py u.zd.snmp.get_snmp_info
tea.py u.zd.snmp.get_snmp_info ip_addr='192.168.0.10'
tea.py u.zd.snmp.get_snmp_info ip_addr='192.168.0.10' username='admin' password='admin'
'''

import logging
from pprint import pformat

from RuckusAutoTest.components import create_zd_by_ip_addr
from RuckusAutoTest.components.lib.zd.system_zd import get_snmp_agent_info, get_snmp_agent_v3_info, get_snmp_trap_info

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')

def do_config(**kwargs):
    zd_cfg = default_cfg
    for k, v in kwargs.items():
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
    conf = {}
    conf.update(zd_cfg)
            
    conf['zd'] = create_zd_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):    
    logging.info('Show SNMP agent v2, v3 and trap Info')    
    snmpv2_info = get_snmp_agent_info(conf['zd'])
    snmpv3_info = get_snmp_agent_v3_info(conf['zd'])
    trap_info = get_snmp_trap_info(conf['zd'])

    logging.info('SNMP agent v2 info:\n %s' % pformat(snmpv2_info,2,20))
    logging.info('SNMP agent v3 info:\n %s' % pformat(snmpv3_info,2,20))
    logging.info('SNMP trap info:\n %s' % pformat(trap_info,2,20))
    
    return('PASS')

def do_clean_up(conf):
    try:
        if conf.has_key('zd'):
            conf['zd'].stop()
            del(conf['zd'])
    except:
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