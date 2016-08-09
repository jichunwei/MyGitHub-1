'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2010.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify the nodes only support snmp v3 [Wlan, Wlan group, AAA servers].
     Preparation:
         Enable snmp agent v2 and v3.
     Steps:
         1. Make sure there is wlan, wlan group, aaa server exist for testing, if not, create one via snmp v3.
         2. Get wlan, wlan group, server info via snmp v2. 
         3. Verify the result via snmp v2 is empty.
    
Commands samples:
tea.py u.snmp.zd.verify_v3_nodes
tea.py u.snmp.zd.verify_v3_nodes ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'

#Also can set related config for agent.
tea.py u.snmp.zd.verify_v3_nodes ip_addr='192.168.0.10' timeout=30 retries=3
                                  ro_community='public' rw_community='private'
                                  ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                  ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                  rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                  rw_priv_protocol='DES' rw_priv_passphrase='12345678'

'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.snmp.zd.wlan_list import get_wlan_index_value_mapping,gen_wlan_test_cfg, create_wlans
from RuckusAutoTest.components.lib.snmp.zd.aaa_servers import get_server_index_value_mapping, gen_server_test_cfg, create_servers
from RuckusAutoTest.components.lib.snmp.zd.wlan_group_list import get_wlan_group_index_value_mapping, gen_wlan_group_test_cfg, create_wlan_groups

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,get_update_snmp_cfg)

zd_cfg = {'ip_addr': '192.168.0.2',
          'username': 'admin',
          'password': 'admin', 
          'shell_key': '!v54!',
          }

snmp_cfg = {'ip_addr': '192.168.0.2',
            'version': 2,
            'timeout': 20,
            'retries': 3,
            }
            
test_cfg = {'field': 'name',  #get wlan based on this field.
            'value': '*',
            'result':{},
            }

agent_config = {'version': 2,
                'enabled': True,
                'ro_community': 'public',
                'rw_community': 'private',
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
    agent_config['version'] = 2
    config_snmp_agent(conf['zd_cli'], agent_config)
    agent_config['version'] = 3
    config_snmp_agent(conf['zd_cli'], agent_config)
        
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)   
    
    return conf

def _create_wlan(snmp):
    '''
    Make sure there is wlans for testing, if no wlan, then create one.
    '''
    snmp_update_cfg = {'version' :  3}    
    snmp.set_config(snmp_update_cfg)
    
    wlan_id_name_mapping = get_wlan_index_value_mapping(snmp)
    
    if len(wlan_id_name_mapping) == 0:
        wlan_test_cfg_list = gen_wlan_test_cfg(size = 1)
        create_wlans(snmp, wlan_test_cfg_list)
        wlan_id_name_mapping = get_wlan_index_value_mapping(snmp)
    
    if len(wlan_id_name_mapping)==0:
        raise Exception('No wlan infomation.')
    
def _create_server(snmp):
    '''
    Make sure there is servers for testing, if no server, then create one.
    '''
    snmp_update_cfg = {'version' :  3}    
    snmp.set_config(snmp_update_cfg)
    
    server_id_name_mapping = get_server_index_value_mapping(snmp)
    
    if len(server_id_name_mapping) == 0:
        server_test_cfg_list = [gen_server_test_cfg()[0]]
        create_servers(snmp, server_test_cfg_list)
        server_id_name_mapping = get_server_index_value_mapping(snmp)
    
    if len(server_id_name_mapping)==0:
        raise Exception('No server infomation.')


def _create_wlan_group(snmp):
    '''
    Make sure there is wlan groups for testing, if no wlan group, then create one.
    '''
    snmp_update_cfg = {'version' :  3}    
    snmp.set_config(snmp_update_cfg)
    
    group_id_name_mapping = get_wlan_group_index_value_mapping(snmp)
    
    if len(group_id_name_mapping) == 0:
        wlan_group_test_cfg_list = gen_wlan_group_test_cfg()
        create_wlan_groups(snmp, wlan_group_test_cfg_list)
        group_id_name_mapping = get_wlan_group_index_value_mapping(snmp)
    
    if len(group_id_name_mapping)==0:
        raise Exception('No wlan group infomation.')
    
def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):
    test_cfg = {'wlan': {'create': _create_wlan, 'get_info': get_wlan_index_value_mapping},
                'wlan group': {'create': _create_wlan_group, 'get_info': get_wlan_group_index_value_mapping},
                'server': {'create': _create_server, 'get_info': get_server_index_value_mapping},
                }
    
    step_index = 1
    
    for key, value in test_cfg.items():
        create_func = value['create']
        get_info_func = value['get_info']
        
        logging.info('Step %s: Verify %s nodes only work for v3.' % (step_index, key))        
        sub_step_index = 1
        logging.info('Step %s.%s: Create %s via snmp v3.' % (step_index, sub_step_index, key))
        create_func(conf['snmp'])
        
        sub_step_index += 1
        logging.info('Step %s.%s: Get %s information with snmp v2.' % (step_index, sub_step_index, key))    
        snmp_update_cfg = {'version' :  2}    
        conf['snmp'].set_config(snmp_update_cfg)
        
        try:
            id_name_mapping = get_info_func(conf['snmp'])
            if len(id_name_mapping) >0:
                conf['result'][key] = 'FAIL: Can also get %s info by snmp v2.' % (key,)
            else:
                conf['result'][key] = 'PASS'            
        except Exception, e:
            logging.warning('Exception:%s' % e)
            conf['result'][key] = 'Exception: %s' % e
        
        step_index += 1    
 
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