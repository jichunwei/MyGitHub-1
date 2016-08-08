'''
To verify speedflex on multiple hop mesh AP: 

    Procedure: 
    - Remove all configuration on Zone Director
    - Perform speedflex test between Zone Director and Root/Mesh AP 
    - Perform speedflex test between 2 Root/Mesh AP 
    - Remove all configuration on Zone Director  
 
Examples: 
tea.py u.zd.speedflex_on_multihop_meshap_tea ap_ip_addr_list=['192.168.0.177']
tea.py u.zd.speedflex_on_multihop_meshap_tea ap_ip_addr_list=['192.168.0.177'] rate_limit=1
'''

import logging
import time, re
import random, pdb
from pprint import pformat

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_server_by_ip_addr,
    create_station_by_ip_addr,
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components import Helpers as lib

default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    sta_ip_addr = '192.168.1.11',
    ap_ip_addr_list =['192.168.0.177'],
    l3_switch_ip_addr = '192.168.0.253',
    timeout = 300,
    des_ip = '192.168.0.252',
    ping_timeout_ms = 150 * 1000,
    check_status_timeout = 120, 
    rate_limit = 100, 
    default_rate_limit = 100,
    min_rate = 0, 
    max_rate = 500,
)

wlan_cfg = dict(ssid = 'rat-speedflex-on-multihops', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False)

default_cfg['wlan_cfg'] = wlan_cfg


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg['zd_ip_addr'])
    _cfg['l3_switch'] = create_l3_switch_by_ip_addr(_cfg['l3_switch_ip_addr'])
    _cfg['ap_list'] = []
    for ap_ip_addr in _cfg['ap_ip_addr_list']:
        _cfg['ap_list'].append(create_ruckus_ap_by_ip_addr(ap_ip_addr, 'admin', 'admin'))
    _cfg['sta'] = create_station_by_ip_addr(_cfg['sta_ip_addr'])

    return _cfg


def do_test(cfg): 
    cfg['errmsg'] = ''
    
    _remove_all_cfg_from_zd(cfg['zd'])
    _remove_all_wlan_from_station(cfg)
    
    _cfg_rate_limit(cfg)
    
    # perform speedflex test between ZD & AP
    ap_mac_list = [cfg['ap_list'][0].get_base_mac()]
    result = _test_multihop_speedflex(cfg['zd'], ap_mac_list)
    
    if result['errmsg']:
        cfg['errmsg'] =  result['errmsg']
        cfg['result'] = 'FAIL'
        return cfg

    # perform speedflex test between 2 APs
    if len(cfg['ap_list']) >=2: 
        ap_mac_list = [cfg['ap_list'][0].get_base_mac(), cfg['ap_list'][1].get_base_mac()]
        result = _test_multihop_speedflex(cfg['zd'], ap_mac_list)
        if result['errmsg']: 
            cfg['errmsg'] =  result['errmsg']
            cfg['result'] = 'FAIL'
            return cfg
    
    _cfg_wlan_on_zd(cfg['zd'], cfg['wlan_cfg'])
    result = _assoc_station_with_ssid(cfg)        
    if not result['errmsg']:
        _get_sta_wifi_ip(cfg)
        cfg = _test_stat_connectivity(cfg)
    else: 
        cfg['errmsg'] =  result['errmsg']
        cfg['result'] = 'ERROR'
        return cfg
            
    cfg['result'] = 'PASS'
    return cfg
                                                                                                                  
                                                                                                                                                                           
def do_clean_up(cfg):
    _remove_rate_limit(cfg)
    _remove_all_cfg_from_zd(cfg['zd'])
    clean_up_rat_env()


def main(**kwa):
    if kwa.has_key('ap_ip_list'):
        kwa['ap_list_list'] = eval(kwa['ap_list_list'])
        
    tcfg = do_config(kwa)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
        
    return (res['result'], res['errmsg'])

def create_l3_switch_by_ip_addr(ip_addr = '', username = '', password = ''):
    return _create_l3_switch(dict(ip_addr = ip_addr, username = username, password = password))

def _create_l3_switch(cfg = {}):
    from pprint import pformat
    import logging
    from RuckusAutoTest.components import NetgearL3Switch
    p = dict(
        ip_addr = '192.168.0.3',
        username = 'admin',
        password = '',
        enable_password = '',
        timeout = 15,
        init = True,
        debug = 0
    )
    p.update(cfg)

    # this conversion is for Switch expected config
    p['config'] = dict(
        username = p.pop('username'),
        password = p.pop('password'),
    )
    logging.info('Creating L3 Switch component [%s]' % p['ip_addr'])
    logging.debug(pformat(p))
    l3_switch = NetgearL3Switch.NetgearL3Switch(p)

    return l3_switch


def _cfg_wlan_on_zd(zd, wlan_cfg):
    logging.info("Configure a WLAN with SSID [%s] on the Zone Director" % wlan_cfg['ssid'])
    zd.cfg_wlan(wlan_cfg)
    time.sleep(10)


def  _verify_wlan_on_aps(cfg):
    cfg['errmsg'] = tmethod.verify_wlan_on_aps(cfg['ap'], cfg['wlan_cfg']['ssid'])
    return cfg


def _assoc_station_with_ssid(cfg):
    cfg['errmsg'] = tmethod.assoc_station_with_ssid(cfg['sta'], cfg['wlan_cfg'], cfg['check_status_timeout'])
    return cfg


def _get_sta_wifi_ip(cfg):
    res, val1, val2 = tmethod.renew_wifi_ip_address(cfg['sta'], cfg['check_status_timeout'])
    
    if not res:
        raise Exception(val2)
    
    cfg['sta_wifi_ip_addr'] = val1
    cfg['sta_wifi_mac_addr'] = val2.lower()


def _test_stat_connectivity(cfg):
    cfg['errmsg'] = tmethod.client_ping_dest_is_allowed(cfg['sta'], cfg['des_ip'], ping_timeout_ms = cfg['ping_timeout_ms'])
    return cfg
 
def _remove_all_cfg_from_zd(zd):
    logging.info("Remove all configuration from the Zone Director")
    zd.remove_all_cfg()

def _remove_all_wlan_from_station(cfg):
    tconfig.remove_all_wlan_from_station(cfg['sta'], check_status_timeout = cfg['check_status_timeout'])
    
def _test_multihop_speedflex(zd, ap_mac_list):
    result = lib.zd.sp.run_multihop_speedflex_performance(zd, ap_mac_list)
    logging.info("Speedflex Performance Result: %s" % pformat(result))
    result['errmsg'] = ''
    uplink_rate = float(re.split("[MK]+bps",result['uplink']['rate'])[0])
    uplink_packets_loss = result['uplink']['packets_loss'].split(":")[-1]
     
    downlink_rate = float(re.split("[MK]+bps",result['downlink']['rate'])[0])
    downlink_packets_loss = result['downlink']['packets_loss'].split(":")[-1]
    
    if "Kbps" in result['uplink']['rate']: 
        uplink_rate = uplink_rate / 1024
    if "Kbps" in result['downlink']['rate']: 
        downlink_rate = downlink_rate / 1024
    
    if uplink_rate <= default_cfg['min_rate'] or uplink_rate > default_cfg['max_rate']:
        result['errmsg'] = "Speedflex return incorrect speed uplink rate: %s" % result['uplink']['rate']

    if downlink_rate <= default_cfg['min_rate'] or downlink_rate > default_cfg['max_rate']:
        result['errmsg'] = "Speedflex return incorrect speed rate for downlink: %s" % result['downlink']['rate']


    if downlink_packets_loss != "0%" or uplink_packets_loss != "0%":
        result['errmsg'] = "Speedflex return high packets loss uplink packets loss[%s] - downlink packets loss[%s]" \
                            % (result['uplink']['packets_loss'], result['downlink']['packets_loss'])


    return result

def _cfg_rate_limit(cfg):
    logging.info("Change rate limit on netgear switch to %s Mbps" % cfg['rate_limit'])
    cfg['l3_switch'].set_bandwidth("1/0/1-1/0/25", cfg['rate_limit'])
    
def _remove_rate_limit(cfg):
    logging.info("Change rate limit on netgear switch to default: %s" % cfg['default_rate_limit'])
    cfg['l3_switch'].set_bandwidth("1/0/1-1/0/25", cfg['default_rate_limit'])
    
    
    