'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.04
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Performance testing:
        send snmpwalk commands some times, and verify the result is correct.
     
Commands samples:
tea.py u.snmp.zd.verify_continue_walking
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10' version=2
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10' version=3

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10' version=2 ro_community='public' rw_community='private' timeout=30 retries=3
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                 ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                 ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                 rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                 rw_priv_protocol='DES' rw_priv_passphrase='12345678'

#Specify times to walking.                                     
tea.py u.snmp.zd.verify_continue_walking ip_addr='192.168.0.10' times=30             
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli.sys_basic_info import get_sys_info, get_cfg_sys_info
from RuckusAutoTest.components.lib.zdcli.alarm_info import get_alarm_info

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,get_update_snmp_cfg)
                                                               
from RuckusAutoTest.components.lib.snmp.zd import sys_info

zd_cfg = {'ip_addr': '192.168.0.2',
          'username': 'admin',
          'password': 'admin',
          'shell_key': '!v54!',
          }

#Notes snmp config, user auth info will update from agent_config.
snmp_cfg = {'ip_addr': '192.168.0.2',
            'version': 2,                        
            'timeout': 20,
            'retries': 3,
            }

test_cfg = {'times': 20,
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

def _get_sys_info_cli(zdcli):
    '''
    Get related system information from zd CLI, and refine to snmp dict template.
    '''
    basic_info = get_sys_info(zdcli)['System Overview']
    cfg_info = get_cfg_sys_info(zdcli)
    alarm_info = get_alarm_info(zdcli)

    all_sys_info = {}
    all_sys_info.update(basic_info)
    all_sys_info.update(cfg_info)
    all_sys_info.update(alarm_info)

    return all_sys_info

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
    
    logging.debug('SNMP config:%s' % snmp_cfg)

    return conf

def do_config(**kwargs):
    return _cfg_test_params(**kwargs)

def do_test(conf):
    try:
        times = int(conf['times'])
        
        if times < 1:
            raise Exception('Times must be greater than 1, please change the value.')
        
        logging.info('Step 1: Get info via cli.')
        cli_values_d = _get_sys_info_cli(conf['zd_cli'])
        
        sys_info_d_list = []
                
        result = ''
        logging.info('Step 2: Continue walking %s times.' % (times,))
        for i in range(1,times+1):
            sys_info_d = sys_info.get_sys_info_by_walking(conf['snmp'])
            
            if not sys_info_d:
                result = 'Response is incorrect when do walking in %s time.' % i
                break
            else:
                sys_info_d_list.append(sys_info_d)
            
        if result:
            conf['result'] = 'FAIL: %s, Times: %s, Result: %s' % (result, times, sys_info_d_list)
        else:
            logging.info('Step 3: Verify the result for each walking are same.')
            
            index = 0
            basic_sys_info_d = sys_info_d_list[index]
            
            index += 1
            res_d = {}
            for i in range(index, len(sys_info_d_list)):
                sys_info_d = sys_info_d_list[i]                
                result_dict = sys_info.verify_sys_info(sys_info_d, basic_sys_info_d)
                
                error_list = []
                for value in result_dict.values():
                    if value.find('PASS')< 0:                    
                        error_list.append(value)
                
                if error_list:
                    res_d.update({i+1: 'FAIL:%s' % (error_list,)})
                else:
                    res_d.update({i+1: 'PASS'})
            
            if res_d:
                conf['result']['WalkingResult'] = res_d
                
            logging.info('Step 4: Verify snmp and cli result.')
            result = sys_info.verify_sys_info_snmp_cli(basic_sys_info_d, cli_values_d)
            if result:
                conf['result']['SNMPCLI'] = result
            else:
                conf['result']['SNMPCLI'] = 'PASS'
            
        if not conf['result']:
            conf['result'] = 'PASS'
        
    except Exception, e:
        conf['result'] = {'Exception': 'Message: %s' % (e,)}

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
