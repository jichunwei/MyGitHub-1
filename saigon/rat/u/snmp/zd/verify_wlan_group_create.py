'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2010.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    1. Create wlan groups with test config.
    2. Verify wlan group details: snmp and test config.
    3. Verify wlan group details: snmp, cli and gui.    
    
Commands samples:
tea.py u.snmp.zd.verify_wlan_group_create
tea.py u.snmp.zd.verify_wlan_group_create ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_wlan_group_create ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_wlan_group_create ip_addr='192.168.0.10' version=3
                                          
#Set is_clean is true, will delete groups after testing, set it as false, will keep them. Default is true.                               
tea.py u.snmp.zd.verify_wlan_group_create ip_addr='192.168.0.10' is_clean=true
tea.py u.snmp.zd.verify_wlan_group_create ip_addr='192.168.0.10' is_clean=false                                           

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_wlan_group_create ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                          ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                          ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                          rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                          rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging

from RuckusAutoTest.components import (create_zd_by_ip_addr,create_zd_cli_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli import get_wlan_group as gwg
from RuckusAutoTest.components.lib.zd.wlan_groups_zd import get_all_wlan_group_cfgs_2

from RuckusAutoTest.components.lib.snmp.zd.wlan_group_list import (get_wlan_group_index_value_mapping,
                                                                   get_wlan_groups_by_key_value,
                                                                   gen_wlan_group_test_cfg,
                                                                   create_wlan_groups,
                                                                   verify_wlan_groups_snmp_cli,
                                                                   verify_wlan_groups_snmp_gui,
                                                                   verify_wlan_groups_test_data_snmp,
                                                                   remove_all_wlan_groups,)

from RuckusAutoTest.components.lib.snmp.zd.wlan_list import (create_wlans,remove_all_wlans, 
                                                             get_wlan_index_value_mapping, gen_wlan_test_cfg)

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,
                                                           get_update_snmp_cfg,
                                                           get_dict_key_by_value,)

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
            
test_cfg = {'result':{},
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
    
    conf['zd_webui'] = create_zd_by_ip_addr(conf['ip_addr'],
                                            conf['username'],
                                            conf['password'])
    
    logging.info('Preparation: Enable snmp agent with config.')
    config_snmp_agent(conf['zd_cli'], agent_config)
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)
    
    logging.info('Preparation: Remove all wlan groups and wlans.')    
    remove_all_wlan_groups(conf['snmp'])
    remove_all_wlans(conf['snmp'])
    
    return conf

def _get_wlan_group_info_gui(zd_webui, group_index_name_mapping): 
    '''
    Get wlan group information from gui.
    '''   
    gui_wlan_groups_d = get_all_wlan_group_cfgs_2(zd_webui)
    new_gui_wlan_groups_d = {}
    #Re-organize the dict with key = index/group_id.
    for name, group_d in gui_wlan_groups_d.items():
        index = get_dict_key_by_value(group_index_name_mapping, name)
        new_gui_wlan_groups_d[index] = group_d
    return new_gui_wlan_groups_d

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
    logging.info('Step 1: Create wlan groups by snmp.')
    wlan_name_list = _create_wlans_for_group(conf['snmp'], 3) 
    group_test_cfg_list = gen_wlan_group_test_cfg(wlan_name_list)
    test_date_cfg_d = create_wlan_groups(conf['snmp'], group_test_cfg_list, wlan_name_list)
    
    logging.info('Step 2: Get wlan group information from snmp, cli, gui.')
    snmp_wlan_groups_d = get_wlan_groups_by_key_value(conf['snmp']) 
    cli_wlan_groups_d = gwg.get_wlan_group_all(conf['zd_cli'])
    
    wlan_group_index_name_mapping = get_wlan_group_index_value_mapping(conf['snmp'])
    gui_wlan_groups_d = _get_wlan_group_info_gui(conf['zd_webui'],wlan_group_index_name_mapping)
   
    logging.info('Step 3: Verify the values are same.')
    result_test_data = verify_wlan_groups_test_data_snmp(snmp_wlan_groups_d, test_date_cfg_d)    
    result_cli = verify_wlan_groups_snmp_cli(snmp_wlan_groups_d, cli_wlan_groups_d)
    result_gui = verify_wlan_groups_snmp_gui(snmp_wlan_groups_d, gui_wlan_groups_d)
    
    if result_test_data:
        conf['result']['SNMPTestData'] = result_test_data
    if result_cli:
        conf['result']['SNMPCLI'] = result_cli
    if result_gui:
        conf['result']['SNMPGUI'] = result_gui
    
    if not conf['result']:
        conf['result'] = 'PASS'   
    
    return conf['result']
    
def do_clean_up(conf):
    if conf['is_clean']:
        logging.info('Cleanup: Delete wlan group and wlans.')
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