'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.04.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify negative input for readwrite nodes which support snmpv2: system information [basic and snmp], ZD AP.

Commands samples:
tea.py u.snmp.zd.verify_negative_input_v2
tea.py u.snmp.zd.verify_negative_input_v2 ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_negative_input_v2 ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_negative_input_v2 ip_addr='192.168.0.10' version=2

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_negative_input_v2 ip_addr='192.168.0.10' version=2 ro_community='public' rw_community='private' timeout=30 retries=3
          
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent

from RuckusAutoTest.components.lib.snmp import snmphelper as helper                                                               
from RuckusAutoTest.components.lib.snmp.zd import sys_info, sys_snmp_info

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

test_cfg = {'oids': 'all',
            'index': 0,
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
    snmp_cfg.update(helper.get_update_snmp_cfg(agent_config))
    conf['snmp'] = helper.create_snmp(snmp_cfg)
    
    return conf

def do_config(**kwargs):
    return _cfg_test_params(**kwargs)

def do_test(conf):
    try:
        is_all = conf['oids'].upper() == 'ALL'
        if is_all:
            obj_names_list = []
        else:
            obj_names_list = conf['oids'].split(',')
            
        res_d = {}
        
        snmp = conf['snmp']
        
        sys_basic_info_cfg = sys_info.gen_test_data_sys_info_negative()        
        res_sys_basic_d = sys_info.update_sys_info(snmp, sys_basic_info_cfg, obj_names_list)
        res_d.update(res_sys_basic_d)
        
        sys_snmp_info_cfg = sys_snmp_info.gen_test_data_sys_snmp_info_negative()
        res_sys_snmp_d = sys_snmp_info.set_sys_snmp_info(snmp, sys_snmp_info_cfg, obj_names_list, False)
        res_d.update(res_sys_snmp_d)
        
        pass_d, fail_d = helper.verify_error_for_negative(res_d)
        
        if pass_d:
            conf['result']['PASS'] = pass_d
        else:
            conf['result']['FAIL'] = fail_d            
            
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
