'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.04
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify snmp system object values. Set pre-config value for rw objects, 
      then compare the values: pre-config, snmp, cli and gui.

Commands samples:
tea.py u.snmp.zd.verify_sys_ip_info
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' version=2
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' version=3

tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' version=3 oids='all'
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' oids='ip_version,ip_addr_mode,ip_addr' version=2 timeout=30 retries=3
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' oids='ip_version,ip_addr_mode,ip_addr' version=3 timeout=20 retries=3

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' version=2 ro_community='public' rw_community='private' timeout=30 retries=3
tea.py u.snmp.zd.verify_sys_ip_info ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                 ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                 ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                 rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                 rw_priv_protocol='DES' rw_priv_passphrase='12345678'  
                                                                         
Appendix:
Mapping of name and object name:
'ip_version':         'ruckusZDSystemIPVersion',
'ip_addr_mode':       'ruckusZDSystemIPAddrMode',
'ip_addr':            'ruckusZDSystemIPAddress',
'ip_addr_mask':       'ruckusZDSystemIPAddrNetmask',
'ip_gateway':         'ruckusZDSystemIPGateway',
'ip_pri_dns':         'ruckusZDSystemIPPrimaryDNS',
'ip_sec_dns':         'ruckusZDSystemIPSecondaryDNS',
'ipv6_addr_mode':     'ruckusZDSystemIPV6AddressModel',
'ipv6_addr':          'ruckusZDSystemIPV6Address',
'ipv6_prefix_len':    'ruckusZDSystemIPV6PrefixLen',
'ipv6_gateway':       'ruckusZDSystemIPV6Gateway',
'ipv6_pri_dns':       'ruckusZDSystemIPV6PrimaryDNS',
'ipv6_sec_dns':       'ruckusZDSystemIPV6SecondaryDNS',
'''

import logging

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr, create_zd_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zd.system_zd import get_device_ip_settings_all
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli.show_config import get_ip_info

from RuckusAutoTest.components.lib.snmp.zd.sys_ip_info import verify_sys_ip_info_snmp_cli, verify_sys_ip_info_snmp_gui, get_sys_ip_info
from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp, get_update_snmp_cfg)


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

ENABLED = 'ENABLED'
DISABLED = 'DISABLED'

def _get_sys_ip_info_gui(zd_webui):
    '''
    Get related system information from GUI, and refine to snmp dict template.
    Output:
        {}
    '''
    all_sys_ip_info = get_device_ip_settings_all(zd_webui)
    return all_sys_ip_info


def _get_sys_ip_info_cli(zdcli):
    '''
    Get related system information from zd CLI, and refine to snmp dict template.
    Output:
        { }
    Issue: Can't get all ipv4 and ipv6 information from cli.
    '''
    #'Gateway Address', 'IPv6 Address', 'Mode', 'Prefix Length', 'Primary DNS', 'Secondary DNS',    
    cli_sys_ip_info = get_ip_info(zdcli)    
    return cli_sys_ip_info

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
    try:
        is_all = conf['oids'].upper() == 'ALL'
        if not is_all:
            obj_names_list = conf['oids'].split(',')
        else:
            obj_names_list = []

        logging.info('Step 1: Get the value from GUI.')
        gui_values_d = _get_sys_ip_info_gui(conf['zd_webui'])

        logging.info('Step 2: Get all system ip info from CLI')
        cli_values_d = _get_sys_ip_info_cli(conf['zd_cli'])
        
        logging.info('Step 3: Get all system ip info from SNMP')
        snmp_values_d = get_sys_ip_info(conf['snmp'], obj_names_list)

        logging.info('Step 4: Verify snmp values with CLI and GUI')
        if not is_all:
            new_cli_values_d = {}
            new_gui_values_d = {}            

            for name in obj_names_list:
                if cli_values_d.has_key(name):
                    new_cli_values_d[name] = cli_values_d[name]
                if gui_values_d.has_key(name):
                    new_gui_values_d[name] = gui_values_d[name]
                
            cli_values_d = new_cli_values_d
            gui_values_d = new_gui_values_d
            
        result_cli = verify_sys_ip_info_snmp_cli(snmp_values_d, cli_values_d)
        result_gui = verify_sys_ip_info_snmp_gui(snmp_values_d, gui_values_d)
    
        if result_cli:
            conf['result']['SNMPCLI'] = result_cli
        if result_gui:
            conf['result']['SNMPGUI'] = result_gui
                
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
