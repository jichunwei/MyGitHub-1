'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2012.11.19
@author: cherry.cheng@ruckuswireless.com (developed)
@summary:
   For ER-140: UniL - 9.4.0.0.110 - OID ruckusZDWLANAPDescription does not return any value 
    Support snmpv2 and v3.
    Set AP description.    
    Get ap information from cli
    Get ap information from snnp.
    Verify ap information between snmp and cli
    
Commands samples:
tea.py u.snmp.zd.verify_wlan_ap_info
tea.py u.snmp.zd.verify_wlan_ap_info ip_addr='192.168.0.2' username='admin' password='admin' shell_key='!v54!'
tea.py u.snmp.zd.verify_wlan_ap_info ip_addr='192.168.0.2'
tea.py u.snmp.zd.verify_wlan_ap_info ip_addr='192.168.0.2' version=3

#Also can set related config for agent, user read write account when execute snmp get commands.
tea.py u.snmp.zd.verify_wlan_ap_info ip_addr='192.168.0.2' version=3 timeout=30 retries=3
                                      ro_sec_name='ruckus-read' ro_auth_protocol='MD5' ro_auth_passphrase='12345678'
                                      ro_priv_protocol='DES' ro_priv_passphrase='12345678' 
                                      rw_sec_name='ruckus-read' rw_auth_protocol='MD5' rw_auth_passphrase='12345678'
                                      rw_priv_protocol='DES' rw_priv_passphrase='12345678'

#Also can set ap mac address verify specified ap information.
tea.py u.snmp.zd.verify_wlan_ap_info ip_addr='192.168.0.10' version=2 ap_mac_addr="11:22:33:44:55:66"
'''
import random
import logging
from pprint import pformat

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr,clean_up_rat_env)

from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli_ap_info
from RuckusAutoTest.components.lib.zdcli import configure_ap as cli_config_zd_ap_info
from RuckusAutoTest.components.lib.snmp.zd import wlan_aps_info as snmp_wlan_ap_info
from RuckusAutoTest.components.lib.snmp import snmphelper as snmp_helper

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
            
test_cfg = {'ap_mac_addr': '*',
            'ap_desc': 'APtest%04d' % random.randrange(1,9999),
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

def _get_ap_info_cli(zd_cli, ap_mac_addr):
    '''
    Get all ap information from cli.
    '''
    cli_aps_list = []
    
    if type(ap_mac_addr) == list:
        cli_aps_d = {}
        for ap_mac in ap_mac_addr:
            cli_ap_d = cli_ap_info.show_ap_info_by_mac(zd_cli, ap_mac)
            cli_aps_list.extend(cli_ap_d['AP']['ID'].values())
    else:
        if ap_mac_addr == '*':
            cli_aps_d = cli_ap_info.show_ap_all(zd_cli)
            
        cli_aps_list = cli_aps_d['AP']['ID'].values()
            
    return cli_aps_list

def _get_ap_info_cli_desc(zd_cli, ap_mac_list):    
    """
    Get AP information: description.
    """
    ap_desc_list = []
    for ap_mac_addr in ap_mac_list:
        cli_ap_d = cli_ap_info.show_ap_info_by_mac(zd_cli, ap_mac_addr)
        cli_ap_value = cli_ap_d['AP']['ID'].values()[0]
        ap_desc_list.append({'mac_addr': ap_mac_addr,
                             'description': cli_ap_value.get('Description')})
    
    return ap_desc_list

def _restore_ap_desc(zd_cli, ap_desc_list):
    """
    Restore AP description informration.
    """
    res, err_msg = cli_config_zd_ap_info.configure_aps(zd_cli, ap_desc_list)
    
    return res, err_msg

def _config_ap_desc(zd_cli, ap_mac_addr, desc):
    """
    Set AP description information.
    """
    ap_cfg = {'mac_addr': ap_mac_addr,
              'description': desc,}
    
    res, err_msg = cli_config_zd_ap_info.configure_ap(zd_cli, ap_cfg)
    
    return res, err_msg

def _convert_cli_aps_d(cli_aps_list):
    """
    Convert cli aps dict, convert key as desc.
    """
    new_aps_d = {}
    for ap_d in cli_aps_list:
        key = ap_d['MAC Address'].upper()
        new_aps_d[key] = ap_d
        
    return new_aps_d
    
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
    snmp_cfg.update(snmp_helper.get_update_snmp_cfg(agent_config))    
    conf['snmp'] = snmp_helper.create_snmp(snmp_cfg)
    
    logging.info('Preparation: Get AP Mac Address.')
    ap_mac_addr = conf['ap_mac_addr']
    cli_aps_list = _get_ap_info_cli(conf['zd_cli'], ap_mac_addr)    
    
    ap_mac_list = []
    if ap_mac_addr == '*':
        for ap_d in cli_aps_list:
            ap_mac_list.append(ap_d['MAC Address'])
    else:
        ap_mac_list = [ap_mac_list]        
        
    conf['ap_mac_list'] = ap_mac_list
        
    logging.info('Preparation: Backup AP description.')
    conf['bak_ap_config'] = _get_ap_info_cli_desc(conf['zd_cli'], ap_mac_list)    
    
    logging.info('Preparation: Set AP description')
    for ap_mac_addr in ap_mac_list:
        desc = 'AP desc test %04d' % random.randrange(1,9999)
        res, msg = _config_ap_desc(conf['zd_cli'], ap_mac_addr, desc)        
        if not res: logging.warning("Set desc failed:%s" % msg)
    
    return conf

def do_config(**kwargs):    
    return _cfg_test_params(**kwargs)

def do_test(conf):
    ap_mac_list = conf['ap_mac_list']
    logging.info('Step 1: Get aps information from cli.')
    cli_aps_list = _get_ap_info_cli(conf['zd_cli'], ap_mac_list)
    cli_aps_d = _convert_cli_aps_d(cli_aps_list)
    
    logging.info('CLI values:\n%s' % pformat(cli_aps_d,2,20))
            
    logging.info('Step 2: Get aps information from snmp.')
    snmp_aps_d = snmp_wlan_ap_info.get_zd_aps_by_mac_addr(conf['snmp'], ap_mac_list)
    logging.info('SNMP values:\n%s' % pformat(snmp_aps_d,2,20))
    
    logging.info('Step 3: Verify the values are same.')
    result_cli = snmp_wlan_ap_info.verify_aps_dict_snmp_cli(snmp_aps_d, cli_aps_d)    
    if result_cli:
        conf['result'] = result_cli
    else:
        if not conf['result']:
            conf['result'] = 'PASS'
         
    return conf['result']
    
def do_clean_up(conf):
    logging.info("Restore AP configureion:%s" % conf['bak_ap_config'])
    res, msg = _restore_ap_desc(conf['zd_cli'], conf['bak_ap_config'])
    if not res:
        logging.warning("Set desc failed:%s" % msg)
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