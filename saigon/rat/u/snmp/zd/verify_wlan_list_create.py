'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.02.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    Steps:
       1. Create wlans [Now only support Standard Usage] with test config.
       2. Verify config data and snmp values.
       3. Verify snmp values with CLI and GUI.       
    
Commands samples:
tea.py u.snmp.zd.verify_wlan_list_create
tea.py u.snmp.zd.verify_wlan_list_create ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_wlan_list_create ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_wlan_list_create ip_addr='192.168.0.10' version=3

#Set is_clean is true, will delete wlans after testing, set it as false, will keep them. Default is true.                               
tea.py u.snmp.zd.verify_wlan_list_create ip_addr='192.168.0.10' is_clean=true
tea.py u.snmp.zd.verify_wlan_list_create ip_addr='192.168.0.10' is_clean=false

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_wlan_list_create ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                         ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                         ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                         rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                         rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging

from RuckusAutoTest.components import (create_zd_by_ip_addr,create_zd_cli_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi
from RuckusAutoTest.components.lib.zd.wlan_zd import get_wlan_conf_detail

from RuckusAutoTest.components.lib.snmp.zd.aaa_servers import get_auth_server_id,get_acct_server_id, get_all_servers_id_name_mapping

from RuckusAutoTest.components.lib.snmp.zd.wlan_list import (get_wlans_by_key_value, get_wlan_index_value_mapping, 
                                                             gen_wlan_test_cfg, create_wlans,
                                                             remove_all_wlans, 
                                                             verify_wlans_test_data_snmp,
                                                             verify_wlans_dict_snmp_cli,
                                                             verify_wlans_dict_snmp_gui,
                                                             convert_wlan_test_data_cfg)

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
            
test_cfg = {'result':{},
            'is_clean': True,}

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
   
    logging.info('Preparation: Remove all wlans.')
    remove_all_wlans(conf['snmp'])
    
    return conf

def _get_wlan_info_gui(zd_webui, wlan_names_d, wlan_name):    
    wlans_list = {}
    for index,name in wlan_names_d.items():
        if wlan_name == '*' or name.upper() == wlan_name.upper():
            #logging.debug('Index = %s, Name = %s' % (index,name))
            wlan_detail_d = get_wlan_conf_detail(zd_webui, name)
            if wlan_detail_d:
                wlans_list[index] = wlan_detail_d      
            
    return wlans_list

def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):   
    logging.info('Step 1: Create wlans by snmp.')
    auth_server_id = get_auth_server_id(conf['snmp'])
    account_server_id = get_acct_server_id(conf['snmp'])
    
    test_data_cfg = gen_wlan_test_cfg(auth_server_id, account_server_id)
    wlan_cfg_dict = create_wlans(conf['snmp'],test_data_cfg)   
    
    logging.info('Step 2: Get wlan information from snmp, cli, gui.')
    all_server_id_name_mapping = get_all_servers_id_name_mapping(conf['snmp'])
    
    snmp_wlans_d = get_wlans_by_key_value(conf['snmp'], all_server_id_name_mapping)
    # Get index and name mapping for wlan.
    wlan_index_names_mapping = get_wlan_index_value_mapping(conf['snmp'])
    key_value = '*'
    gui_wlans_d = _get_wlan_info_gui(conf['zd_webui'], wlan_index_names_mapping, key_value)
    cli_wlans_d = gwi.get_wlan_all(conf['zd_cli'])
    
    logging.info('Step 3: Verify the values are same.')
    new_wlan_cfg_dict = {}
    for index, wlan_cfg in wlan_cfg_dict.items():
        new_wlan_cfg_dict[index] = convert_wlan_test_data_cfg(wlan_cfg, all_server_id_name_mapping)
        
    result_test_data = verify_wlans_test_data_snmp(snmp_wlans_d, new_wlan_cfg_dict)    
    result_cli = verify_wlans_dict_snmp_cli(snmp_wlans_d, cli_wlans_d)
    result_gui = verify_wlans_dict_snmp_gui(snmp_wlans_d, gui_wlans_d)
    
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
        logging.info('Cleanup: Delete all wlans.')
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