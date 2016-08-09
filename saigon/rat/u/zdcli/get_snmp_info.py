'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.02.05
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Get snmp agent v2, v3 and snmp trap information.

Commands samples:
tea.py u.zdcli.get_snmp_info
tea.py u.zdcli.get_snmp_info ip_addr='192.168.0.10'
tea.py u.zdcli.get_snmp_info ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB'
'''

import logging
from pprint import pformat

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import get_sys_snmpv2_info,get_sys_snmpv3_info,get_sys_snmp_trap_info

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    zd_cfg = default_cfg
    for k, v in kwargs.items():
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
    conf = {}
    conf.update(zd_cfg)
            
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    return conf

def do_test(conf):    
    logging.info('Show SNMP agent v2, v3 and trap Info')    
    snmpv2_info = get_sys_snmpv2_info(conf['zd_cli'])
    snmpv3_info = get_sys_snmpv3_info(conf['zd_cli'])
    trap_info = get_sys_snmp_trap_info(conf['zd_cli'])

    logging.info('SNMP agent v2 info:\n %s' % pformat(snmpv2_info,2,20))
    logging.info('SNMP agent v3 info:\n %s' % pformat(snmpv3_info,2,20))
    logging.info('SNMP trap info:\n %s' % pformat(trap_info,2,20))
    
    return('PASS')

def do_clean_up(conf):
    try:
        if conf.has_key('zd_cli'):
            conf['zd_cli'].close()
            del(conf['zd_cli'])
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