'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2010.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    Get aps information from snmp, cli and gui, then verify the related information are same.
    Can verify specified aps, field = '<col name>' value = '<col value>'. E.g. field = 'name' value = 'apsTest'
    
Commands samples:
tea.py u.snmp.zd.verify_aps_info_get
tea.py u.snmp.zd.verify_aps_info_get ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_aps_info_get ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_aps_info_get ip_addr='192.168.0.10' version=3

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_aps_info_get ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                      ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                      ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                      rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                      rw_priv_protocol='DES' rw_priv_passphrase='12345678'

#Also can set primary key name and value to verify specified aps.
tea.py u.snmp.zd.verify_aps_info_get ip_addr='192.168.0.10' version=3 field="mac_addr" value="ap mac addr"
'''

import logging
from pprint import pformat

from RuckusAutoTest.components import (create_zd_by_ip_addr,create_zd_cli_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli.ap_info_cli import show_ap_all
from RuckusAutoTest.components.lib.zd.access_points_zd import get_ap_config_by_mac

from RuckusAutoTest.components.lib.snmp.zd.aps_info import (get_zd_aps_by_key_value, 
                                                            verify_aps_dict_snmp_cli,verify_aps_dict_snmp_gui,
                                                            get_zd_ap_index_value_mapping)

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
            
test_cfg = {'field': 'mac_addr',  #get aps based on this field.
            'value': '*',
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

def _get_ap_info_gui(zd_webui, index_mac_addr_mapping):
    '''
    Get ap info from gui. Based on the result is incorrect, will hold on.
    '''    
    new_gui_aps_info = {}
    
    for index, mac_addr in index_mac_addr_mapping.items():              
        gui_d = get_ap_config_by_mac(zd_webui, mac_addr)   
        gui_d.update({'mac_addr': mac_addr})     
        new_gui_aps_info[index] = gui_d
    
    return new_gui_aps_info

def _get_ap_info_cli(zd_cli):
    '''
    Get all ap information from cli.
    '''
    cli_aps_d = show_ap_all(zd_cli)
    
    if cli_aps_d.has_key('AP'):
        cli_aps_d = cli_aps_d['AP']['ID']
        
    return cli_aps_d

    
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

def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):    
    logging.info('Step 1: Get aps information from snmp, cli, gui.')
    key_col = conf['field']
    key_value = conf['value']
    is_all = key_value == '*'
    
    index_mac_addr_mapping = get_zd_ap_index_value_mapping(conf['snmp'])
    
    if not is_all:        
        ap_index = get_dict_key_by_value(index_mac_addr_mapping, key_value)
        
        if not ap_index:
            raise Exception('No ap with mac address: %s' % key_value)
        
    snmp_aps_d = get_zd_aps_by_key_value(conf['snmp'], key_col, key_value)
    gui_aps_d = _get_ap_info_gui(conf['zd_webui'], index_mac_addr_mapping)
    cli_aps_d = _get_ap_info_cli(conf['zd_cli'])    
    logging.info('GUI values:\n%s' % pformat(gui_aps_d,2,20))
    logging.info('CLI values:\n%s' % pformat(cli_aps_d,2,20))
    logging.info('SNMP values:\n%s' % pformat(snmp_aps_d,2,20))
    
    if not is_all:
        cli_aps_d = { ap_index: cli_aps_d[ap_index]}
        
    logging.info('Step 2: Verify the values are same.')
    result_cli = verify_aps_dict_snmp_cli(snmp_aps_d, cli_aps_d)    
    if result_cli:
        conf['result']['SNMPCLI'] = result_cli
        
    result_gui = verify_aps_dict_snmp_gui(snmp_aps_d, gui_aps_d)
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