'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.04
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify config snmp agent by cli works well.
     Pre-condition:
        Disable snmp v2 and v3 agent. 
     Steps:
        1. Enable snmp v3 agent.
        2. Check the process works well. [ps -aux|grep 'snmpd']
        3. Execute snmpv3 command to make sure it works.
        4. Enable snmp v2 agent.
        5. Execute snmpv2 command to make sure it works.
        6. Disbale snmp v3 agent.        
        7. Check snmp command: snmpv3 can't work. 
        8. Disbale snmp v2 agent.        
        9. Check snmp command: snmpv2 can't work.
        10. Check the process is disappear. [ps -aux|grep 'snmpd']


Commands samples:
tea.py u.snmp.zd.verify_cfg_agent_cli_en_dis_v3_v2
tea.py u.snmp.zd.verify_cfg_agent_cli_en_dis_v3_v2 ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'

#set agent config for snmp version 2 and 3.
tea.py u.snmp.zd.verify_cfg_agent_cli_en_dis_v3_v2 ro_community='public' rw_community='private'
                         ro_sec_name='ruckus-read' ro_auth_protocol='MD5'
                         ro_auth_passphrase=12345678' ro_priv_protocol='DES' ro_priv_passphrase='12345678',
                         rw_sec_name='ruckus-write' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                         rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import get_sys_snmpv2_info, get_sys_snmpv3_info
from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,get_update_snmp_cfg)
from RuckusAutoTest.components.lib.snmp.zd.snmp_agent_trap import verify_snmp_agent, verify_snmpd_process

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

test_cfg = {'result':{},}

agent_config = {'version': 3,
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
    
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    
    #Update snmp config, get read write config for it.
    snmp_cfg.update(get_update_snmp_cfg(agent_config))    
    conf['snmp'] = create_snmp(snmp_cfg)
    
    conf['agent_cfg'] = agent_config
    
    logging.info('Preparation: Disable snmp agent v2 and v3.')
    agent_config['enabled'] = False
    agent_config['version'] = 2
    config_snmp_agent(conf['zd_cli'], agent_config)
    agent_config['version'] = 3
    config_snmp_agent(conf['zd_cli'], agent_config)
    
    return conf

def do_config(**kwargs):
    return _cfg_test_params(**kwargs)

def do_test(conf):
    try:
        snmp_agent_cfg = conf['agent_cfg']
        res_d = {}
            
        logging.info('Step 1. Enable snmp v3 agent.')
        snmp_agent_cfg['enabled'] = True
        snmp_agent_cfg['version'] = 3
        config_snmp_agent(conf['zd_cli'], snmp_agent_cfg)
        
        logging.info('Current snmp agent info: V2:\n%s V3:\n%s' % (get_sys_snmpv2_info(conf['zd_cli']), get_sys_snmpv3_info(conf['zd_cli'])))
        
        logging.info("Step 2. Check the process works well. [ps -aux|grep 'snmpd']")
        snmp_agent_cfg['enabled'] = True
        result = verify_snmpd_process(conf['zd_cli'], snmp_agent_cfg['enabled'])
        if result:
            res_d['Step 2'] = result
            
        logging.info("Step 3. Execute snmpv3 command to make sure it works.")
        snmp_agent_cfg['enabled'] = True
        snmp_agent_cfg['version'] = 3
        result = verify_snmp_agent(conf['snmp'], conf['zd_cli'], snmp_agent_cfg)
        if result:
            res_d['Step 3'] = result
        
        logging.info('Step 4. Enable snmp v2 agent.')
        snmp_agent_cfg['enabled'] = True
        snmp_agent_cfg['version'] = 2
        config_snmp_agent(conf['zd_cli'], snmp_agent_cfg)
        
        logging.info('Current snmp agent info: V2:\n%s V3:\n%s' % (get_sys_snmpv2_info(conf['zd_cli']), get_sys_snmpv3_info(conf['zd_cli'])))
        
        logging.info("Step 5. Execute snmpv2 command to make sure it works.")
        snmp_agent_cfg['enabled'] = True
        snmp_agent_cfg['version'] = 2
        result = verify_snmp_agent(conf['snmp'], conf['zd_cli'], snmp_agent_cfg)
        if result:
            res_d['Step 5'] = result
        
        logging.info('Step 6. Disbale snmp v3 agent.')
        snmp_agent_cfg['enabled'] = False
        snmp_agent_cfg['version'] = 3
        config_snmp_agent(conf['zd_cli'], snmp_agent_cfg)
        
        logging.info('Current snmp agent info: V2:\n%s V3:\n%s' % (get_sys_snmpv2_info(conf['zd_cli']), get_sys_snmpv3_info(conf['zd_cli'])))
        
        logging.info("Step 7. Check snmpv3 command can't work.")
        snmp_agent_cfg['enabled'] = False
        snmp_agent_cfg['version'] = 3
        result = verify_snmp_agent(conf['snmp'], conf['zd_cli'], snmp_agent_cfg)
        if result:
            res_d['Step 3'] = result
        
        logging.info('Step 8. Disable snmp v2 agent.')
        snmp_agent_cfg['enabled'] = False
        snmp_agent_cfg['version'] = 2
        config_snmp_agent(conf['zd_cli'], snmp_agent_cfg)
        
        logging.info('Current snmp agent info: V2:\n%s V3:\n%s' % (get_sys_snmpv2_info(conf['zd_cli']), get_sys_snmpv3_info(conf['zd_cli'])))
        
        logging.info("Step 9. Check snmpv2 command can't work.")
        snmp_agent_cfg['enabled'] = False
        snmp_agent_cfg['version'] = 2
        result = verify_snmp_agent(conf['snmp'], conf['zd_cli'], snmp_agent_cfg)
        if result:
            res_d['Step 5'] = result
        
        logging.info("Step 10. Check the process is disappear. [ps -aux|grep 'snmpd']")
        snmp_agent_cfg['enabled'] = False
        result = verify_snmpd_process(conf['zd_cli'], snmp_agent_cfg['enabled'])
        if result:
            res_d['Step 10'] = result
                    
        if res_d: 
            conf['result'].update(res_d)
        else:
            conf['result'] = 'PASS'
                
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