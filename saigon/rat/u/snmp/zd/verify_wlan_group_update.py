'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2010.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    Steps:
        1. Create a new wlan group.
        2. Update the setting of wlan group.
        3. Verify the value is updated with config.
    
Commands samples:
tea.py u.snmp.zd.verify_wlan_group_update
tea.py u.snmp.zd.verify_wlan_group_update ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_wlan_group_update ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_wlan_group_update ip_addr='192.168.0.10' version=3

#Set is_clean is true, will delete groups after testing, set it as false, will keep wlan groups. Default is true.                               
tea.py u.snmp.zd.verify_wlan_group_update ip_addr='192.168.0.10' is_clean=true
tea.py u.snmp.zd.verify_wlan_group_update ip_addr='192.168.0.10' is_clean=false

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_wlan_group_update ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                          ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                          ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                          rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                          rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent

from RuckusAutoTest.components.lib.snmp.zd.wlan_group_list import (gen_wlan_group_update_test_cfg, 
                                                                   remove_all_wlan_groups, 
                                                                   create_wlan_groups,
                                                                   verify_update_wlan_group)
from RuckusAutoTest.components.lib.snmp.zd.wlan_list import remove_all_wlans, get_wlan_index_value_mapping,gen_wlan_test_cfg, create_wlans

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,get_update_snmp_cfg)

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
            
test_cfg = {'field': 'name',  #get wlan based on this field.
            'value': '*',
            'result':{},
            'is_clean': True,
            }

agent_config = {'version': 3,
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
    
    logging.info('Remove all wlan groups and wlans.')
    remove_all_wlan_groups(conf['snmp'])
    remove_all_wlans(conf['snmp'])
    
    return conf

def _create_wlans_for_group(snmp, wlan_count):
    '''
    Create some wlans, with specified len, return wlan name list.
    '''
    wlan_id_name_mapping = get_wlan_index_value_mapping(snmp)
    
    if len(wlan_id_name_mapping) < wlan_count:
        list_size = wlan_count - len(wlan_id_name_mapping)
        test_data_cfg = gen_wlan_test_cfg(size = list_size)        
        create_wlans(snmp,test_data_cfg)
        wlan_id_name_mapping = get_wlan_index_value_mapping(snmp)
        
    wlan_name_list = wlan_id_name_mapping.values()
    return wlan_name_list
    
def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):
    logging.info('Step 1: Create a wlan group.')
    wlan_name_list = _create_wlans_for_group(conf['snmp'], 3)
    logging.info('Wlan name list: %s' % wlan_name_list)
    new_wlans_group_cfg_list, update_wlan_cfg = gen_wlan_group_update_test_cfg(conf['snmp'], wlan_name_list)
    logging.info('Create wlan:%s, \nupdate config:%s' % (new_wlans_group_cfg_list, update_wlan_cfg))    
    wlan_group_cfg_list = create_wlan_groups(conf['snmp'], new_wlans_group_cfg_list, wlan_name_list)
    group_id = wlan_group_cfg_list.keys()[0]
    
    logging.info('Step 2: Update wlan group config, and verify it is updated.')
    result = verify_update_wlan_group(conf['snmp'], group_id, update_wlan_cfg)
    
    if result:
        conf['result'] = result
    
    if not conf['result']:
        conf['result'] = 'PASS'       
        
    return conf['result']
    
def do_clean_up(conf):
    if conf['is_clean']:
        logging.info('Delete wlan group and wlans.')
        remove_all_wlan_groups(conf['snmp'])        
        remove_all_wlans(conf['snmp'])
    
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