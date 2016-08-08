'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.12.30
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
    Only support snmp version 3.
    Steps:
       1. Create aaa servers [Now only support radius auth and radius accounting] with test config.
       2. Verify config data and snmp values.
       3. Verify snmp values with CLI and GUI.    
    
Commands samples:
tea.py u.snmp.zd.verify_aaa_servers_create
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10' version=3
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10' version=3 timeout='30' retries='4'
                                           
#Set is_clean is true, will delete aaa servers after testing, set it as false, will keep them. Default is true.                               
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10' is_clean=true
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10' is_clean=false                                           

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_aaa_servers_create ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                           ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                           ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                           rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                           rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging

from RuckusAutoTest.components import (create_zd_by_ip_addr,create_zd_cli_by_ip_addr, clean_up_rat_env)

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli.aaa_servers import get_all_aaa_servers 
from RuckusAutoTest.components.lib.zd.aaa_servers_zd import get_all_server_cfg_list

from RuckusAutoTest.components.lib.snmp.zd.aaa_servers import (get_servers_by_key_value,
                                                               verify_servers_dict_snmp_cli,
                                                               verify_servers_dict_snmp_gui,
                                                               create_servers,gen_server_test_cfg,remove_all_servers,                                                                
                                                               verify_servers_test_data_snmp,
                                                               get_server_index_value_mapping)

from RuckusAutoTest.components.lib.snmp.zd.wlan_list import remove_all_wlans

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,
                                                           get_update_snmp_cfg,
                                                           get_dict_key_by_value)

zd_cfg = {'ip_addr': '192.168.0.2',
          'username': 'admin',
          'password': 'admin',
          'shell_key': '!v54!', 
          }
            
test_cfg = {'result':{},
            'is_clean': True,
            }

#Notes snmp config, user auth info will update from agent_config.
snmp_cfg = {'ip_addr': '192.168.0.2',
            'version': 3,                       
            'timeout': 20,
            'retries': 3,
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
    
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    conf['zd_webui'] = create_zd_by_ip_addr(conf['ip_addr'],
                                            conf['username'],
                                            conf['password'])
    
    logging.info('Preparation: Enable snmp agent with config.')
    config_snmp_agent(conf['zd_cli'], agent_config)
    
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)  
    
    logging.info('Preparation: Remove all aaa_servers.')
    remove_all_wlans(conf['snmp'])
    remove_all_servers(conf['snmp'])
    
    return conf

def _get_aaa_server_info_cli(zdcli):
    '''
    Get aaa server info from cli.
    Server id =1 is local database, 2 is guest access. 
    '''
    cli_servers_d = get_all_aaa_servers(zdcli)['AAA']['ID']
    # Remove index =1 and 2.
    for key in cli_servers_d.keys():
        if int(key) in [1,2]:
            cli_servers_d.pop(key)
            
    return cli_servers_d
            
def _get_aaa_server_info_gui(zd_webui, index_name_mapping):
    '''
    Get aaa server info from gui.
    '''
    aaa_servers_list = get_all_server_cfg_list(zd_webui)
    
    gui_servers_d = {}
    # Re-organize the list to a dict, key is index.
    for server_d in aaa_servers_list:
        new_index = get_dict_key_by_value(index_name_mapping, server_d['server_name'])       
        if new_index:
            gui_servers_d.update({new_index: server_d})
        else:
            raise Exception("Can't get index by aaa server name.")
    
    return gui_servers_d

def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):   
    logging.info('Step 1: Create aaa_servers by snmp.')
    server_cfg_list = gen_server_test_cfg()
    res, server_cfg_dict = create_servers(conf['snmp'], server_cfg_list)
    
    logging.info('Step 2: Get aaa servers information from snmp, cli, gui.')
    snmp_servers_d = get_servers_by_key_value(conf['snmp'])
    server_index_names_mapping = get_server_index_value_mapping(conf['snmp'])
    gui_servers_d = _get_aaa_server_info_gui(conf['zd_webui'],server_index_names_mapping)
    cli_servers_d = _get_aaa_server_info_cli(conf['zd_cli'])
    
    logging.info('Step 2: Verify the values are same.')        
    result_test_data = verify_servers_test_data_snmp(snmp_servers_d, server_cfg_dict)
    result_cli = verify_servers_dict_snmp_cli(snmp_servers_d, cli_servers_d)
    result_gui = verify_servers_dict_snmp_gui(snmp_servers_d, gui_servers_d)
    
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
        logging.info('Cleanup: Delete aaa servers.')
        remove_all_wlans(conf['snmp'])
        remove_all_servers(conf['snmp'])
        
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