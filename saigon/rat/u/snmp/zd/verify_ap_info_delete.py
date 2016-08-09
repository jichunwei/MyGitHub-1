'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2010.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    Get aps information from snmp, cli and gui, then verify the related information are same.
    Can verify specified aps, field = '<col name>' value = '<col value>'. E.g. field = 'name' value = 'apsTest'
    
Commands samples:
tea.py u.snmp.zd.verify_aps_info_delete
tea.py u.snmp.zd.verify_aps_info_delete ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_aps_info_delete ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_aps_info_delete ip_addr='192.168.0.10' version=3

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_aps_info_delete ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                      ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                      ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                      rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                      rw_priv_protocol='DES' rw_priv_passphrase='12345678'

#Also can set primary key name and value to verify specified aps.
tea.py u.snmp.zd.verify_aps_info_delete ip_addr='192.168.0.10' version=3 field="mac_addr" value="ap mac addr"
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.snmp.zd.aps_info import get_zd_ap_index_value_mapping, verify_delete_aps

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,
                                                           get_update_snmp_cfg)

zd_cfg = {'ip_addr': '192.168.0.2',
          'username': 'admin',
          'password': 'admin', 
          'shell_key': '!v54!',
          }

snmp_cfg = {'ip_addr': '192.168.0.2',
            'version': 3,
            'timeout': 20,
            'retries': 3,
            }
            
test_cfg = {'value': '',
            'result':{},
            }

agent_config = {'version': 2,
                'enabled': True,
                'ro_community': 'public',
                'rw_community': 'private',
                'contact': 'support@ruckuswireless.com',
                'location': 'shenzhen',
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
    
def _cfg_test_params(**kwargs):
    for k, v in kwargs.items():
        if snmp_cfg.has_key(k):
            snmp_cfg[k] = v
        if test_cfg.has_key(k):
            test_cfg[k] = v
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
        if agent_config.has_key(k):
            agent_config[k] = v
    
    conf = {}
    conf.update(zd_cfg)
    conf.update(test_cfg)
    conf.update(snmp_cfg)
    
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    logging.info('Preparation: Enable snmp agent with config.')
    config_snmp_agent(conf['zd_cli'], agent_config)
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)
    
    return conf

def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):
    logging.info('Step 1: Get ap_id will be deleted.')
    mac_addr_list = conf['value'].split(',')
    
    index_mac_addr_mapping = get_zd_ap_index_value_mapping(conf['snmp'])
    if not mac_addr_list:
        if len(index_mac_addr_mapping)>0:
            mac_addr_list = index_mac_addr_mapping.values()
        else:
            raise Exception('No ap found for this zd.')
        
    logging.info('Step 2: Delete a ap, and verify.')
    err_mac_addr_list = verify_delete_aps(conf['snmp'], mac_addr_list)
    
    if err_mac_addr_list:
        conf['result'] = 'FAIL: The aps are not deleted successfully: %s' % err_mac_addr_list
    else:
        conf['result'] = 'PASS'    
    
    return conf['result']

def do_clean_up(conf):
    clean_up_rat_env()

def main(**kwargs):
    conf = {}
    try:
        if kwargs.has_key('help'):
            print __doc__
        else:
            conf = do_config(**kwargs)
            res = do_test(conf)
            do_clean_up(conf) 
            return res
    except Exception, e:
        logging.info('[TEST BROKEN] %s' % e.message)
        return conf
    finally:
        pass

if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)   