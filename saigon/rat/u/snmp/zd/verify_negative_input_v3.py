'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.04.10
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
     Verify negative input for readwrite nodes which support snmpv3: ZD AP, AAA server, Wlan, Wlan group.

Commands samples:
tea.py u.snmp.zd.verify_negative_input_v3
tea.py u.snmp.zd.verify_negative_input_v3 ip_addr='192.168.0.10' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_negative_input_v3 ip_addr='192.168.0.10'
tea.py u.snmp.zd.verify_negative_input_v3 ip_addr='192.168.0.10' version=2

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_negative_input_v3 ip_addr='192.168.0.10' version=3 timeout=30 retries=3
                                          ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                          ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                          rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                          rw_priv_protocol='DES' rw_priv_passphrase='12345678'
'''

import logging

from RuckusAutoTest.components import create_zd_cli_by_ip_addr,clean_up_rat_env

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent

from RuckusAutoTest.components.lib.snmp import snmphelper as helper                                                               
from RuckusAutoTest.components.lib.snmp.zd import sys_info, sys_snmp_info, wlan_group_list, wlan_list, aaa_servers, aps_info

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

test_cfg = {'index': 0,
            'result':{},
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
    
    logging.info('Preparation: Enable snmp agent with config.')
    config_snmp_agent(conf['zd_cli'], agent_config)
    
    #Update snmp config, get read write config for it.
    snmp_cfg.update(helper.get_update_snmp_cfg(agent_config))
    conf['snmp'] = helper.create_snmp(snmp_cfg)
    
    server_cfg = dict(server_name = 'Radius-Auth-Server', type = 'aaa-authentication(3)',
                      server_addr = '192.168.30.252', server_port = '1812', radius_secret = '123456789',
                      backup = 'disable(2)', backup_server_addr = '192.168.30.252',
                      backup_server_port = '0', backup_radius_secret = '123456789',
                      request_timeout = '3', retry_count = '2', retry_interval = '5',)
    
    server_name = server_cfg['server_name']
    
    wlan_cfg = dict(ssid = 'Standard-Open-None', desc = 'Standard open and no encryption', name = 'Standard-Open-None', service_type = 'standardUsage(1)',
                   auth = 'open(1)', encrypt = 'none-enc(6)', wep_key_index = '1', wep_key = '1234567890', wpa_cipher_type = 'none(0)', wpa_key = '1234567890',
                   auth_server_id = '1', wireless_client = 'none(1)', zero_it_activation = 'enable(1)', service_priority = 'high(1)',
                   accounting_server_id = '0', accounting_update_interval = '10', uplink_rate = 'disable(0)', downlink_rate = 'disable(0)',
                   vlan_id = '1', dynamic_vlan = 'disable(2)', hide_ssid = 'false(2)', tunnel_mode = 'false(2)', bg_scanning = 'true(1)',
                   max_clients_per_ap = '100', web_auth = 'enable(1)')
    
    wlan_name = wlan_cfg['name']
    
    wlan_group_cfg = dict(name = 'GroupTest-new1', desc = 'GroupTest1-123',
                          wlan_member = {wlan_name: {'override_type': 'tag(3)', 'vlan_tag': '3'}})
    
    wlan_group_name = wlan_group_cfg['name']
    
    conf['server_cfg_list'] = [server_cfg]
    conf['server_name'] = server_name
    conf['wlan_cfg_list'] = [wlan_cfg]
    conf['wlan_name'] = wlan_name
    conf['wlan_group_cfg_list'] = [wlan_group_cfg]
    conf['wlan_group_name'] = wlan_group_name
    
    logging.info('Preparation: Remove all wlan group, wlans, aaa servers.')
    wlan_group_list.remove_all_wlan_groups(conf['snmp'])
    wlan_list.remove_all_wlans(conf['snmp'])
    aaa_servers.remove_all_servers(conf['snmp'])
    
    logging.debug('SNMP config:%s' % snmp_cfg)

    return conf

def do_config(**kwargs):
    return _cfg_test_params(**kwargs)

def do_test(conf):
    try:
        snmp = conf['snmp']
        
        res_sys_d = {}
        
        logging.info('Step 1: Verify negative input for system basic and snmp info.')
        sys_basic_info_cfg = sys_info.gen_test_data_sys_info_negative()        
        res_sys_basic_d = sys_info.update_sys_info(snmp, sys_basic_info_cfg)
        res_sys_d.update(res_sys_basic_d)
        
        sys_snmp_info_cfg = sys_snmp_info.gen_test_data_sys_snmp_info_negative()
        res_sys_snmp_d = sys_snmp_info.set_sys_snmp_info(snmp, sys_snmp_info_cfg, [], False)
        res_sys_d.update(res_sys_snmp_d)
        
        pass_d, fail_d = helper.verify_error_for_negative(res_sys_d)
        
        result_sys = {}
        if pass_d:
            result_sys['PASS'] = pass_d
        if fail_d:
            result_sys['FAIL'] = fail_d
            
        conf['result']['SYSTEM'] = result_sys
        
        logging.info('Step 1: Create aaa server.')
        aaa_servers.create_aaa_servers(snmp, conf['server_cfg_list'])
        
        logging.info('Step 2: Verify negative input for aaa server.')
        aaa_id_name_mapping = aaa_servers.get_server_index_value_mapping(snmp)        
        server_id = helper.get_dict_key_by_value(aaa_id_name_mapping, conf['server_name'])
        
        if not server_id:
            res_aaa_d = {'Error': 'No aaa server for name %s' % conf['server_name']}
        else:
            res_aaa_d = aaa_servers.update_server_cfg_one_by_one(snmp, server_id, aaa_servers.gen_server_test_cfg_negative())
        
        pass_d, fail_d = helper.verify_error_for_negative(res_aaa_d)       
         
        result_aaa = {}
        if pass_d:
            result_aaa['PASS'] = pass_d
        if fail_d:
            result_aaa['FAIL'] = fail_d
            
        conf['result']['AAA'] = result_aaa
        
        logging.info('Step 4: Create wlan.')
        wlan_list.create_wlans(snmp, conf['wlan_cfg_list'])
        
        logging.info('Step 5: Verify negative input for wlan')
        wlan_id_name_mapping = wlan_list.get_wlan_index_value_mapping(snmp)        
        wlan_id = helper.get_dict_key_by_value(wlan_id_name_mapping, conf['wlan_name'])
        
        if not wlan_id:
            res_wlan_d = {'Error': 'No wlan for name %s' % conf['wlan_name']}
        else:
            res_wlan_d = wlan_list.update_wlan_cfg_one_by_one(snmp, wlan_id, wlan_list.gen_wlan_test_cfg_negative())
        
        pass_d, fail_d = helper.verify_error_for_negative(res_wlan_d)
        
        result_wlan = {}
        if pass_d:
            result_wlan['PASS'] = pass_d
        if fail_d:
            result_wlan['FAIL'] = fail_d
            
        conf['result']['WLAN'] = result_wlan
            
        logging.info('Step 6: Create wlan group.')
        wlan_group_list.create_wlan_groups(snmp, conf['wlan_group_cfg_list'])
        
        logging.info('Step 7: Verify negative input for wlan group.')
        wg_id_name_mapping = wlan_group_list.get_wlan_group_index_value_mapping(snmp)
                
        wlan_group_id = helper.get_dict_key_by_value(wg_id_name_mapping, conf['wlan_group_name'])
        
        if not wlan_group_id:
            res_wlan_group_d = {'Error': 'No wlan group for name %s' % conf['wlan_group_name']}
        else:
            res_wlan_group_d = wlan_group_list.update_wlan_group_cfg_one_by_one(snmp, wlan_group_id, wlan_group_list.gen_wlan_group_cfg_negative())
            
        pass_d, fail_d = helper.verify_error_for_negative(res_wlan_group_d)
        
        result_wlan_group = {}
        if pass_d:
            result_wlan_group['PASS'] = pass_d
        if fail_d:
            result_wlan_group['FAIL'] = fail_d
            
        conf['result']['WLANGROUP'] = result_wlan_group
        
        logging.info('Step 7: Verify negative input for ap config.')
        ap_id_mac_mapping = aps_info.get_zd_ap_index_value_mapping(snmp)
        
        if len(ap_id_mac_mapping) > 0:
            ap_mac = ap_id_mac_mapping.values()[0]
        else:
            res_ap_d = {'Error': 'No AP is joined to ZD.'}
                
        ap_id = helper.get_dict_key_by_value(ap_id_mac_mapping, ap_mac)
        
        if not ap_id:
            res_ap_d = {'Error': 'No ap for mac_addr %s' % ap_mac}
        else:
            res_ap_d = aps_info.update_ap_cfg_one_by_one(snmp, ap_id, aps_info.gen_ap_cfg_negative())
        
        pass_d, fail_d = helper.verify_error_for_negative(res_ap_d)
        
        result_ap = {}
        if pass_d:
            result_ap['PASS'] = pass_d
        if fail_d:
            result_ap['FAIL'] = fail_d
            
        conf['result']['AP'] = result_ap
            
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
