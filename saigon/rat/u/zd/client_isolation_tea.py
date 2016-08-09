'''
To verify client isolation with using local and full option: 

    Procedure: 
    - Remove all configuration on Zone Director 
    - Create a OPEN-NONE wlan for testing with station
    - Associate stations to wlan 
    - Verify station and ping from station 01 to station 02: 
      + local: 2 clients can ping each others
      + full: 2 clients can not ping each others 
    - Verify stations could ping to destination 
    - Remove all configuration on Zone Director  
 
Examples: 
tea.py u.zd.client_isolation_tea ap_ip_addr=192.168.0.180 sta1_ip_addr=192.168.1.11 sta2_ip_addr=192.168.1.12 isolation_option=local
tea.py u.zd.client_isolation_tea ap_ip_addr=192.168.0.180 sta1_ip_addr=192.168.1.11 sta2_ip_addr=192.168.1.12 isolation_option=full
'''

import logging
import time
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
    sta1_ip_addr = '192.168.1.11',
    sta2_ip_addr = '192.168.1.12',
    ap_ip_addr = '192.168.0.180',
    timeout = 300,
    des_ip = '192.168.0.252',
    ping_timeout_ms = 150 * 1000,
    check_status_timeout = 120, 
    isolation_option = 'local',
)

wlan_cfg_01 = dict(ssid = 'rat-client-isolation-01', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, 
                           do_isolation = "local")

wlan_cfg_02 = dict(ssid = 'rat-client-isolation-02', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False, 
                           do_isolation = "local")


wlangroup_cfg = dict(
    name = 'client-isolation-wlangroup',
    description = 'client-isolation-wlangroup',
    wlan_member = [wlan_cfg_01['ssid']],
    vlan_override = False,
)


default_cfg['wlan_cfg_01'] = wlan_cfg_01
default_cfg['wlan_cfg_02'] = wlan_cfg_02
default_cfg['wlangroup_cfg'] = wlangroup_cfg


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)
    _cfg['wlan_cfg_01']['do_isolation'] = _cfg['isolation_option']
    _cfg['wlan_cfg_02']['do_isolation'] = _cfg['isolation_option']
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg['zd_ip_addr'])
    _cfg['ap'] = create_ruckus_ap_by_ip_addr(_cfg['ap_ip_addr'], 'admin', 'admin')
    _cfg['sta1'] = create_station_by_ip_addr(_cfg['sta1_ip_addr'])
    _cfg['sta2'] = create_station_by_ip_addr(_cfg['sta2_ip_addr'])

    return _cfg


def do_test(cfg): 
    cfg['errmsg'] = ''
    
    _remove_all_cfg_from_zd(cfg['zd'])
    _remove_all_wlan_from_station(cfg, cfg['sta1'])
    _cfg_wlan_on_zd(cfg['zd'], cfg['wlan_cfg_01'])
    _cfg_wlan_on_zd(cfg['zd'], cfg['wlan_cfg_02'])
    _cfg_wlangroup_on_zd(cfg['zd'], cfg['wlangroup_cfg'])
    
    _cfg_remove_wlan_from_default_wlangroup(cfg['zd'], cfg['wlan_cfg_01'])
    _cfg_assign_wlangroup_to_ap(cfg['zd'], cfg['wlangroup_cfg'], cfg['ap']) 
    
    result = _assoc_station_with_ssid(cfg, cfg['sta1'], cfg['wlan_cfg_01'])        
    if not result['errmsg']:
        sta1_wifi_ip_addr, sta1_wifi_mac_addr = _get_sta_wifi_ip(cfg, cfg['sta1'])

    result = _assoc_station_with_ssid(cfg, cfg['sta2'], cfg['wlan_cfg_02'])        
    if not result['errmsg']:
       sta2_wifi_ip_addr, sta2_wifi_mac_addr = _get_sta_wifi_ip(cfg, cfg['sta2'])
    
    if not result['errmsg']:    
        _test_stat_connectivity(cfg, cfg['sta1'], sta2_wifi_ip_addr)
    
    if result['errmsg']:
        cfg['result'] = 'FAIL'
        cfg['errmsg'] = 'Client Isolation behavior work incorrectly'
        
    cfg['result'] = 'PASS'
    return cfg
                                                                                                                  
                                                                                                                                                                           
def do_clean_up(cfg):
    _remove_all_cfg_from_zd(cfg['zd'])
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
        
    return (res['result'], res['errmsg'])

def _cfg_wlan_on_zd(zd, wlan_cfg):
    logging.info("Configure a WLAN with SSID [%s] on the Zone Director" % wlan_cfg['ssid'])
    lib.zd.wlan.create_wlan(zd, wlan_cfg)
    time.sleep(10)

def _cfg_wlangroup_on_zd(zd, wlangroup_cfg):
    logging.info("Configure a WLAN GROUP[%s] on the Zone Director" % wlangroup_cfg['name'])
    lib.zd.wgs.create_wlan_group_2(zd, wlangroup_cfg)
    time.sleep(10)
    
def _cfg_remove_wlan_from_default_wlangroup(zd, wlan_cfg):
    logging.info("remove wlan['%s'] from Default Wlan Group" % wlan_cfg['ssid'])
    lib.zd.wgs.uncheck_default_wlan_member(zd, wlan_cfg['ssid'])
    time.sleep(10)    

def _cfg_assign_wlangroup_to_ap(zd, wlangroup_cfg, ap):
    ap_mac_addr = ap.get_base_mac()
    logging.info("Assign wlangroup[%s] to AP[%s]" % (wlangroup_cfg, ap_mac_addr))
    ap_support_radio = lib.zd.ap.get_supported_radio(zd, ap_mac_addr)
    for radio in ap_support_radio: 
        lib.zd.ap.assign_to_wlan_group(zd, ap_mac_addr, radio, wlangroup_cfg['name'])
    time.sleep(10)

def  _verify_wlan_on_aps(cfg):
    cfg['errmsg'] = tmethod.verify_wlan_on_aps(cfg['ap'], cfg['wlan_cfg']['ssid'])
    return cfg


def _assoc_station_with_ssid(cfg, sta, wlan_cfg):
    cfg['errmsg'] = tmethod.assoc_station_with_ssid(sta, wlan_cfg, cfg['check_status_timeout'])
    return cfg


def _get_sta_wifi_ip(cfg, sta):
    res, wifi_ip_addr, wifi_mac_addr = tmethod.renew_wifi_ip_address(sta, cfg['check_status_timeout'])
    
    if not res:
        raise Exception(wifi_mac_addr)
    
    return wifi_ip_addr, wifi_mac_addr.lower()


def _test_stat_connectivity(cfg, sta1, sta2_wifi_ip_addr):
    if cfg['wlan_cfg_01']['do_isolation'] == 'local':
        cfg['errmsg'] = tmethod.client_ping_dest_is_allowed(sta1, sta2_wifi_ip_addr, ping_timeout_ms = cfg['ping_timeout_ms'])
    if cfg['wlan_cfg_01']['do_isolation'] == 'full':
        cfg['errmsg'] = tmethod.client_ping_dest_not_allowed(sta1, sta2_wifi_ip_addr, ping_timeout_ms = cfg['ping_timeout_ms'])
        
    return cfg    
 
def _remove_all_cfg_from_zd(zd):
    logging.info("Remove all configuration from the Zone Director")
    lib.zd.ap.assign_all_ap_to_default_wlan_group(zd)
    zd.remove_all_cfg()

def _remove_all_wlan_from_station(cfg, sta):
    tconfig.remove_all_wlan_from_station(sta, check_status_timeout = cfg['check_status_timeout'])
