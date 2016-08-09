'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.04
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify snmp system object values. Set pre-config value for rw objects, 
      then compare the values: pre-config, snmp, cli and gui.

Commands samples:
tea.py u.snmp.zd.verify_sys_info
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' version=2
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' version=3

tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' version=3 oids='all'
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' oids='system_name,ip_addr,mac_addr' version=2 timeout=30 retries=3
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' oids='system_name,ip_addr,mac_addr' version=3 timeout=20 retries=3

#Can set specified new value of object for updating, format is <object name>='<new value>'.  
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' system_name='CherryTest'

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' version=2 ro_community='public' rw_community='private' timeout=30 retries=3
tea.py u.snmp.zd.verify_sys_info ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                 ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                 ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                 rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                 rw_priv_protocol='DES' rw_priv_passphrase='12345678'
                                        
Appendix:
Mapping of abbr name and object name:
    'system_name':             'ruckusZDSystemName',
    'ip_addr':                 'ruckusZDSystemIPAddr',
    'mac_addr':                'ruckusZDSystemMacAddr',
    'uptime':                  'ruckusZDSystemUptime',
    'model':                   'ruckusZDSystemModel',
    'licensed_aps':            'ruckusZDSystemLicensedAPs',
    'serial_number':           'ruckusZDSystemSerialNumber',
    'version':                 'ruckusZDSystemVersion',
    'country_code':            'ruckusZDSystemCountryCode',
    'ntp_enable':              'ruckusZDSystemTimeWithNTP',
    'ntp_server':              'ruckusZDSystemTimeNTPServer',
    'syslog_enable':           'ruckusZDSystemLogWithSysLog',
    'syslog_server':           'ruckusZDSystemSysLogServer',
    'fm_enable':               'ruckusZDSystemFlexMasterEnable',
    'fm_server':               'ruckusZDSystemFlexMasterServer',
    'fm_interval':             'ruckusZDSystemFlexMasterInterval',
    'email_enable':            'ruckusZDSystemEmailTriggerEnable',
    'email_addr':              'ruckusZDSystemEmailAddress',
    'smtp_server':             'ruckusZDSystemSMTPServerName',
    'smtp_server_port':        'ruckusZDSystemSMTPServerPort',
    'smtp_auth_username':      'ruckusZDSystemSMTPAuthUsername',
    'smtp_auth_pwd':           'ruckusZDSystemSMTPAuthPassword',
    'smtp_encrypt_options':    'ruckusZDSystemSMTPEncryptionOptions'                   
'''

import logging

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr, create_zd_by_ip_addr,clean_up_rat_env)


from RuckusAutoTest.components.lib.zd.dashboard_zd import get_system_info
from RuckusAutoTest.components.lib.zd.system_zd import (get_syslog_info,
                                                        get_fm_mgmt_info,
                                                        get_ntp_config)
from RuckusAutoTest.components.lib.zd.alarm_setting_zd import get_alarm_setting

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
                'rw_priv_protocol': None,
                'rw_priv_passphrase': '12345678',
                }

def _get_sys_info_gui(zd_webui):
    '''
    Get related system information from GUI, and refine to snmp dict template.    
    '''
    all_sys_info = {}

    sys_info_d = get_system_info(zd_webui)
    # {'label': u'Japan', 'value': u'JP'},
    country_code_d = zd_webui.get_country_code()    
    ntp_cfg = get_ntp_config(zd_webui)
    syslog_info_d = get_syslog_info(zd_webui)
    fm_mgmt_info_d = get_fm_mgmt_info(zd_webui)
    alarm_info_d = get_alarm_setting(zd_webui)

    all_sys_info.update(sys_info_d)
    all_sys_info['Country Code'] = country_code_d
    all_sys_info['NTP'] = ntp_cfg
    all_sys_info['Log'] = syslog_info_d
    all_sys_info['FM'] = fm_mgmt_info_d
    all_sys_info['Alarm'] = alarm_info_d
    
    return all_sys_info


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
    test_data_cfg = sys_info.gen_test_data_sys_info()
    
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
        is_all = conf['oids'].upper() == 'ALL'
        if is_all:
            obj_names_list = []
        else:
            obj_names_list = conf['oids'].split(',')

        logging.info('Step 1: Set pre-config value by snmp.')
        test_data_cfg = conf['test_data']        
        sys_info.update_sys_info(conf['snmp'], test_data_cfg, obj_names_list)
        
        logging.info('Step 2: Get the values by snmp.')
        snmp_values_d = sys_info.get_sys_info(conf['snmp'], obj_names_list)        

        logging.info('Step 3: Get the values from GUI.')
        gui_values_d = _get_sys_info_gui(conf['zd_webui'])
        
        logging.info('Step 4: Get the values from CLI')
        cli_values_d = _get_sys_info_cli(conf['zd_cli'])
        
        logging.info('Step 5: Verify pre-config, snmp, CLI and GUI values.')
        if not is_all:
            #Need to update later, based on cli and gui dict is not converted now.
            new_cli_values_d = {}
            new_gui_values_d = {} 
            new_test_data_cfg = {}           
            for name in obj_names_list:                
                if cli_values_d.has_key(name):
                    new_cli_values_d[name] = cli_values_d[name]
                if gui_values_d.has_key(name):
                    new_gui_values_d[name] = gui_values_d[name]
                if test_data_cfg.has_key(name):
                    new_test_data_cfg[name] = test_data_cfg[name]                                        
                else:
                    raise Exception('Name %s is not exist in system objects list.' % name)
            
            cli_values_d = new_cli_values_d
            gui_values_d = new_gui_values_d
            
        result = sys_info.verify_sys_info_snmp_test_data(snmp_values_d, test_data_cfg)        
        if result:
            conf['result']['SNMPTestData'] = result
            
        result = sys_info.verify_sys_info_snmp_cli(snmp_values_d, cli_values_d)
        if result:
            conf['result']['SNMPCLI'] = result
            
        result = sys_info.verify_sys_info_snmp_gui(snmp_values_d, gui_values_d)
        if result:
            conf['result']['SNMPGUI'] = result
            
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
