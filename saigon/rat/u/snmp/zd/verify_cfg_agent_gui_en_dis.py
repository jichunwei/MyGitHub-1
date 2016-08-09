'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.04
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify config snmp agent by gui works well. 
     Steps:
        1. Enable snmp v2/v3 agent.
        2. Check the process works well. [ps -aux|grep 'snmpd']
        3. Execute snmp command to make sure it works.
        4. Disbale snmp v2/v3 agent.
        5. Check the process snmpd is disappear.
        6. Execute snmp command, error is displayed. 

Commands samples:
tea.py u.snmp.zd.verify_cfg_agent_gui_en_dis
tea.py u.snmp.zd.verify_cfg_agent_gui_en_dis ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_cfg_agent_gui_en_dis ip_addr='192.168.0.10' version=2
tea.py u.snmp.zd.verify_cfg_agent_gui_en_dis ip_addr='192.168.0.10' version=3

#set agent config.
tea.py u.snmp.zd.verify_cfg_agent_gui_en_dis version=2 ro_community='public' rw_community='private'
tea.py u.snmp.zd.verify_cfg_agent_gui_en_dis version=3 ro_sec_name='ruckus-read' ro_auth_protocol='MD5'
                         ro_auth_passphrase=12345678' ro_priv_protocol='DES' ro_priv_passphrase='12345678',
                         rw_sec_name='ruckus-write' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                         rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging
import copy

from RuckusAutoTest.components import (create_zd_by_ip_addr,create_zd_cli_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zd.system_zd import set_snmp_agent_info, set_snmp_agent_v3_info
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,
                                                           get_update_snmp_cfg)
from RuckusAutoTest.components.lib.snmp.zd.snmp_agent_trap import verify_snmp_agent



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

test_cfg = {'result':{},
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
    
    conf['zd_webui'] = create_zd_by_ip_addr(conf['ip_addr'],
                                            conf['username'],
                                            conf['password'])
    
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)
    
    conf['agent_cfg'] = agent_config
    
    return conf

def _config_snmp_agent_gui(zd_webui, snmp_agent_cfg):
    agent_cfg = {}
    agent_cfg.update(snmp_agent_cfg)
    agent_cfg['enabled'] = snmp_agent_cfg['enabled']
    
    if snmp_agent_cfg['version'] == 2:
        agent_cfg['contact'] = snmp_agent_cfg['contact']
        agent_cfg['location'] = snmp_agent_cfg['location']
        agent_cfg['ro_community'] = snmp_agent_cfg['ro_community']
        agent_cfg['rw_community'] = snmp_agent_cfg['rw_community']          
        set_snmp_agent_info(zd_webui, agent_cfg)
    elif snmp_agent_cfg['version'] == 3:
        agent_cfg['ro_sec_name'] = snmp_agent_cfg['ro_sec_name']
        agent_cfg['ro_auth_protocol'] = snmp_agent_cfg['ro_auth_protocol']
        agent_cfg['ro_auth_passphrase'] = snmp_agent_cfg['ro_auth_passphrase']
        agent_cfg['ro_priv_protocol'] = snmp_agent_cfg['ro_priv_protocol']
        agent_cfg['ro_priv_passphrase'] = snmp_agent_cfg['ro_priv_passphrase']
        agent_cfg['rw_sec_name'] = snmp_agent_cfg['rw_sec_name']
        agent_cfg['rw_auth_protocol'] = snmp_agent_cfg['rw_auth_protocol']
        agent_cfg['rw_auth_passphrase'] = snmp_agent_cfg['rw_auth_passphrase']
        agent_cfg['rw_priv_protocol'] = snmp_agent_cfg['rw_priv_protocol']
        agent_cfg['rw_priv_passphrase'] = snmp_agent_cfg['rw_priv_passphrase']
        set_snmp_agent_v3_info(zd_webui, agent_cfg)
            
def do_config(**kwargs):
    return _cfg_test_params(**kwargs)

def do_test(conf):
    try:
        snmp_agent_cfg = conf['agent_cfg']
        zdcli = conf['zd_cli']
        
        logging.info('Preparation: Disable snmp agent v2 and v3.')        
        agent_cfg_copy = copy.deepcopy(snmp_agent_cfg)
        agent_cfg_copy['enabled'] = False
        agent_cfg_copy['version'] = 2
        config_snmp_agent(zdcli, agent_cfg_copy)
        agent_cfg_copy['version'] = 3
        config_snmp_agent(zdcli, agent_cfg_copy)
                
        logging.info('Step 1: Enable snmp agent.')
        snmp_agent_cfg['enabled'] = True
        _config_snmp_agent_gui(conf['zd_webui'],snmp_agent_cfg)
        
        logging.info('Step 2: Verify agent is enabled.')        
        res = verify_snmp_agent(conf['snmp'], conf['zd_cli'], snmp_agent_cfg)
        if res:
            conf['result'].update(res)
            
        logging.info('Step 3: Disable snmp agent.')
        snmp_agent_cfg['enabled'] = False
        _config_snmp_agent_gui(conf['zd_webui'],snmp_agent_cfg)
            
        logging.info('Step 4: Verify snmp agent is disabled.')
        res = verify_snmp_agent(conf['snmp'], conf['zd_cli'], snmp_agent_cfg)
            
        if res: 
            conf['result'].update(res)
                
    except Exception, e:
        conf['result'] = {'Exception': 'Message: %s' % (e,)}
        
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