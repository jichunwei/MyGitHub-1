'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.04
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify snmp system object values. Set pre-config value for rw objects, 
      then compare the values: pre-config, snmp, cli and gui.
    Notes: Based on set one snmp node, need to wait some time, only get and verify the value now.

Commands samples:
tea.py u.snmp.zd.verify_sys_snmp_info
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' version=2
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' version=3

tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' version=3 oids='all'
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' oids='trap_enable,trap_version,v2_trap_server' version=2 timeout=30 retries=3
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' oids='trap_enable,trap_version,v2_trap_server' version=3 timeout=20 retries=3

#Can set specified new value of object for updating, format is <object name>='<new value>'.  
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' trap_enable=1

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' version=2 ro_community='public' rw_community='private' timeout=30 retries=3
tea.py u.snmp.zd.verify_sys_snmp_info ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                 ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                 ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                 rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                 rw_priv_protocol='DES' rw_priv_passphrase='12345678'
                                        
Appendix:
Mapping of name and object name:
'trap_enable':         'ruckusZDSystemSNMPTrapEnable',
'trap_version':        'ruckusZDSystemSNMPTrapVersion',
'v2_trap_server':      'ruckusZDSystemSNMPV2TrapServer1',
'v3_trap_user':        'ruckusZDSystemSNMPV3TrapUser',
'v3_trap_server':      'ruckusZDSystemSNMPV3TrapServer1',
'v3_trap_auth':        'ruckusZDSystemSNMPV3TrapAuth',
'v3_trap_auth_key':    'ruckusZDSystemSNMPV3TrapAuthKey',
'v3_trap_priv':        'ruckusZDSystemSNMPV3TrapPrivacy',
'v3_trap_priv_key':    'ruckusZDSystemSNMPV3TrapPrivacyKey',
'v2_enable':           'ruckusZDSystemSNMPEnable',
'v2_ro_user':          'ruckusZDSystemSNMPROCommunity',
'v2_rw_user':          'ruckusZDSystemSNMPRWCommunity',
'v2_contact':          'ruckusZDSystemSNMPSysContact',
'v2_location':         'ruckusZDSystemSNMPSysLocation',
'v3_enable':           'ruckusZDSystemSNMPV3Enable',
'v3_ro_user':          'ruckusZDSystemSNMPV3RoUser',
'v3_ro_auth':          'ruckusZDSystemSNMPV3RoAuth',
'v3_ro_auth_key':      'ruckusZDSystemSNMPV3RoAuthKey',
'v3_ro_priv':          'ruckusZDSystemSNMPV3RoPrivacy',
'v3_ro_priv_key':      'ruckusZDSystemSNMPV3RoPrivacyKey',
'v3_rw_user':          'ruckusZDSystemSNMPV3RwUser',
'v3_rw_auth':          'ruckusZDSystemSNMPV3RwAuth',
'v3_rw_auth_key':      'ruckusZDSystemSNMPV3RwAuthKey',
'v3_rw_priv':          'ruckusZDSystemSNMPV3RwPrivacy',
'v3_rw_priv_key':      'ruckusZDSystemSNMPV3RwPrivacyKey',  
'''

import logging

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr, create_zd_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zd.system_zd import (get_snmp_agent_info, get_snmp_agent_v3_info, get_snmp_trap_v3_info)
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import get_sys_snmpv2_info, get_sys_snmpv3_info, get_sys_snmp_trap_info

from RuckusAutoTest.components.lib.snmp.snmphelper import (create_snmp,get_update_snmp_cfg, is_disabled)
from RuckusAutoTest.components.lib.snmp.zd.sys_snmp_info import (gen_test_data_sys_snmp_info, 
                                                                 set_sys_snmp_info,
                                                                 get_sys_snmp_info,
                                                                 verify_sys_snmp_info_snmp_cli, 
                                                                 verify_sys_snmp_info_snmp_gui, 
                                                                 verify_sys_snmp_info_snmp_test_data,
                                                                 _convert_cli_to_snmp_temp,)

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

def _get_sys_snmp_info_gui(zd_webui):
    '''
    Get related system information from GUI, and refine to snmp dict template.
    Output:       
    '''    
    gui_sys_snmp_info = {}

    gui_sys_snmp_info['v2_agent'] = get_snmp_agent_info(zd_webui)
    gui_sys_snmp_info['v3_agent'] = get_snmp_agent_v3_info(zd_webui)
    gui_sys_snmp_info['trap'] = get_snmp_trap_v3_info(zd_webui)
    
    return gui_sys_snmp_info

def _get_sys_snmp_info_cli(zdcli):
    '''
    Get related system information from zd CLI, and refine to snmp dict template.
    Output:
        
    '''
    cli_sys_snmp_info = {}

    cli_sys_snmp_info['v2_agent'] = get_sys_snmpv2_info(zdcli)
    cli_sys_snmp_info['v3_agent'] = get_sys_snmpv3_info(zdcli)
    cli_sys_snmp_info['trap'] = get_sys_snmp_trap_info(zdcli)

    return cli_sys_snmp_info

def _cfg_test_params(**kwargs):
    test_data_cfg = gen_test_data_sys_snmp_info()

    for k, v in kwargs.items():
        if snmp_cfg.has_key(k):
            snmp_cfg[k] = v
        if test_cfg.has_key(k):
            test_cfg[k] = v
        if zd_cfg.has_key(k):
            zd_cfg[k] = v
        if test_data_cfg.has_key(k):
            test_data_cfg[k] = v
        if agent_config.has_key(k):
            agent_config[k] = v

    conf = {}
    conf.update(zd_cfg)
    conf.update(test_cfg)
    conf.update(snmp_cfg)

    conf['test_data'] = test_data_cfg
    
    conf['zd_cli'] = create_zd_cli_by_ip_addr(**zd_cfg)
    conf['zd_webui'] = create_zd_by_ip_addr(conf['ip_addr'],
                                            conf['username'],
                                            conf['password'])
    
    logging.info('Preparation: Enable snmp agent.')
    agent_config['version'] = 2
    config_snmp_agent(conf['zd_cli'], agent_config)
    agent_config['version'] = 3
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
            
        original_snmp_agent_config = conf['snmp'].get_config()
            
        logging.info('Step 1: Set pre-config value from SNMP.')
        test_data_cfg = conf['test_data']
        set_sys_snmp_info(conf['snmp'], test_data_cfg, obj_names_list)
        
        logging.info('Step 2: Get the values from SNMP.')
        snmp_values_d = get_sys_snmp_info(conf['snmp'], obj_names_list)

        logging.info('Step 3: Get the values from GUI.')
        gui_values_d = _get_sys_snmp_info_gui(conf['zd_webui'])

        logging.info('Step 4: Get the values from CLI')
        cli_values_d = _get_sys_snmp_info_cli(conf['zd_cli'])
        logging.info('Current info via cli:%s' % cli_values_d)

        logging.info('Step 5: Verify pre-config, snmp, CLI and GUI values.')
        if not is_all:
            new_test_data_cfg = {}
            new_cli_values_d = {}
            new_gui_values_d = {}
            for name in obj_names_list:
                if test_data_cfg.has_key(name):
                    new_test_data_cfg[name] = test_data_cfg[name]
                else:
                    raise Exception('Name %s is not exist in system snmp objects list.' % name)
                    
                if cli_values_d.has_key(name):
                    new_cli_values_d[name] = cli_values_d[name]
                if gui_values_d.has_key(name):
                    new_gui_values_d[name] = gui_values_d[name]

            test_data_cfg = new_test_data_cfg
            cli_values_d = new_cli_values_d
            gui_values_d = new_gui_values_d
        
        result = verify_sys_snmp_info_snmp_test_data(snmp_values_d, test_data_cfg)        
        if result:
            conf['result']['SNMPTestData'] = result
        
        result = verify_sys_snmp_info_snmp_cli(snmp_values_d, cli_values_d)
        if result:
            conf['result']['SNMPCLI'] = result
            
        result = verify_sys_snmp_info_snmp_gui(snmp_values_d, gui_values_d)
        if result:
            conf['result']['SNMPGUI'] = result
                
        cli_values_d = _convert_cli_to_snmp_temp(cli_values_d)
        result = verify_sys_snmp_info_snmp_test_data(cli_values_d, test_data_cfg)        
        if result:
            conf['result']['CLITestData'] = result
             
        logging.info('Step 6: Restore snmp agent config.')
        config_snmp_agent(conf['zd_cli'], original_snmp_agent_config)
        
        logging.info('Step 7: Verify disable snmp agent via SNMP.')
        version = str(conf['version'])
            
        test_data_cfg = {}
        key = 'v%s_enable' % version
        test_data_cfg[key] = '2'  #Disabled        
    
        # Disbale snmp agent v2 and v3.
        set_sys_snmp_info(conf['snmp'], test_data_cfg)
        
        import time
        time.sleep(20)
        
        enabled = ''
        if version == '2':
            snmp_agent = get_sys_snmpv2_info(conf['zd_cli'])                
            if snmp_agent.has_key('Status'):
                enabled = snmp_agent['Status']
        else:
            snmp_agent = get_sys_snmpv3_info(conf['zd_cli'])
            if snmp_agent.has_key('status'):
                enabled = snmp_agent['status']
            
        if enabled:
            if is_disabled(enabled):
                res = 'PASS: Disable snmp agent v%s via SNMP successfully.' % version
            else:
                res = "FAIL: Disable snmp agent v%s failed. Actual: %s" % (version, enabled)
        else:
            res = "FAIL: Didn't get snmp agent v%s enabled setting via ZD CLI. CLI values: %s" % (version, snmp_agent)
            
        conf['result']['DISABLEAGENT'] = res
        
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