'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2010.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    Get wlan information from snmp, cli and gui, then verify the related information are same.
    Can verify specified wlan, field = '<col name>' value = '<col value>'. E.g. field = 'name' value = 'WlanTest'
    
Commands samples:
tea.py u.snmp.zd.verify_wlan_list_get
tea.py u.snmp.zd.verify_wlan_list_get ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_wlan_list_get ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_wlan_list_get ip_addr='192.168.0.10' version=3

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_wlan_list_get ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                      ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                      ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                      rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                      rw_priv_protocol='DES' rw_priv_passphrase='12345678'

#Also can set primary key name and value to verify specified wlan.
tea.py u.snmp.zd.verify_wlan_list_get ip_addr='192.168.0.10' version=3 field="name" value="wlan_name"
'''

import logging

from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.components import (create_zd_by_ip_addr,create_zd_cli_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi
from RuckusAutoTest.components.lib.zd.wlan_zd import get_wlan_conf_detail

from RuckusAutoTest.components.lib.snmp.zd.wlan_list import (get_wlans_by_key_value,verify_wlans_dict_snmp_cli,verify_wlans_dict_snmp_gui, 
                                                             get_wlan_index_value_mapping)
from RuckusAutoTest.components.lib.snmp.zd.aaa_servers import get_all_servers_id_name_mapping

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,
                                                           get_update_snmp_cfg,                                                           
                                                           get_dict_key_by_value)

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
    
    conf['zd_webui'] = create_zd_by_ip_addr(conf['ip_addr'],
                                            conf['username'],
                                            conf['password'])
    
    logging.info('Preparation: Enable snmp agent with config.')
    config_snmp_agent(conf['zd_cli'], agent_config)
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)
    
    return conf

def _get_wlan_info_gui(zd_webui, wlan_names_d, wlan_name):    
    wlans_list = {}
    for index,name in wlan_names_d.items():
        if wlan_name == '*' or compare(name, wlan_name, 'eq'):                        
            wlan_detail_d = get_wlan_conf_detail(zd_webui, name)
            wlans_list[index] = wlan_detail_d      
            
    return wlans_list

def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):
    logging.info('Step 1: Get wlan information from snmp, cli, gui.')
    key_col = conf['field']
    key_value = conf['value']
    is_all = key_value == '*'    
    # Get index and name mapping for wlan.
    wlan_index_name_mapping = get_wlan_index_value_mapping(conf['snmp'])
    
    if not is_all:
        wlan_id = get_dict_key_by_value(wlan_index_name_mapping, key_value)
        if not wlan_id:
            raise Exception('The wlan "%s" does not exist' %  key_value)
        
    server_id_name_mapping = get_all_servers_id_name_mapping(conf['snmp'])    
    snmp_wlans_d = get_wlans_by_key_value(conf['snmp'], server_id_name_mapping, key_col, key_value)
    gui_wlans_d = _get_wlan_info_gui(conf['zd_webui'], wlan_index_name_mapping, key_value)
    cli_wlans_d = gwi.get_wlan_all(conf['zd_cli'])
    
    if not cli_wlans_d:
        cli_wlans_d = {}
    if not is_all:
        cli_wlans_d = {wlan_id : cli_wlans_d[wlan_id]}
        
    logging.info('Step 2: Verify the values are same.')
    result_cli = verify_wlans_dict_snmp_cli(snmp_wlans_d, cli_wlans_d)
    result_gui = verify_wlans_dict_snmp_gui(snmp_wlans_d, gui_wlans_d)
    
    if result_cli:
        conf['result']['SNMPCLI'] = result_cli
    if result_gui:
        conf['result']['SNMPGUI'] = result_gui 
    
    if not conf['result']:
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