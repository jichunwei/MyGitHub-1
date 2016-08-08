'''
To verify ping and trace route function on Zone Director Web UI: 

    Procedure: 
    - Remove all configuration on Zone Director 
    - Create a OPEN-NONE wlan for testing with station
    - Associate station to wlan 
    - Verify station and ping to destination
    - Perform ping test for AP from AP Monitor page 
    - Perform trace route test for AP from AP Monitor page 
    - Perform ping test for station from current active client page  
    - Perform trace route test for station from current active client page 
    - Remove all configuration on Zone Director  
 
Examples: 
tea.py u.zd.ping_traceroute_tea ap_ip_addr=192.168.0.180 sta_ip_addr=192.168.1.11
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
    sta_ip_addr = '192.168.1.11',
    ap_ip_addr = '192.168.0.180',
    timeout = 300,
    des_ip = '192.168.0.252',
    ping_timeout_ms = 150 * 1000,
    check_status_timeout = 120
)

wlan_cfg = dict(ssid = 'rat-ping-traceroute', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False)

default_cfg['wlan_cfg'] = wlan_cfg


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg['zd_ip_addr'])
    _cfg['ap'] = create_ruckus_ap_by_ip_addr(_cfg['ap_ip_addr'], 'admin', 'admin')
    _cfg['sta'] = create_station_by_ip_addr(_cfg['sta_ip_addr'])

    return _cfg


def do_test(cfg): 
    cfg['errmsg'] = ''
    
    _remove_all_cfg_from_zd(cfg['zd'])
    _remove_all_wlan_from_station(cfg)
    _cfg_wlan_on_zd(cfg['zd'], cfg['wlan_cfg'])
    
    result = _assoc_station_with_ssid(cfg)        
    if not result['errmsg']:
        _get_sta_wifi_ip(cfg)
        cfg = _test_stat_connectivity(cfg)
    
    result = _test_ping_on_ap(cfg)
    if result['errmsg']:
        cfg['errmsg'] = result['errmsg']
        cfg['result'] = 'FAIL' 
        return cfg

    result = _test_traceroute_on_ap(cfg)
    if result['errmsg']:
        cfg['errmsg'] = result['errmsg']
        cfg['result'] = 'FAIL' 
        return cfg

    result = _test_ping_on_sta(cfg)
    if result['errmsg']:
        cfg['errmsg'] = result['errmsg']
        cfg['result'] = 'FAIL' 
        return cfg

    result = _test_traceroute_on_sta(cfg)
    if result['errmsg']:
        cfg['errmsg'] = result['errmsg']
        cfg['result'] = 'FAIL' 
        return cfg
        
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
    
 
def _test_ping_on_ap(cfg):
    ap_mac = cfg['ap'].get_base_mac()
    logging.info("Open ping and trace route windows for AP[%s]" % ap_mac)
    lib.zd.aps.open_pingtool_by_mac_addr(cfg['zd'], ap_mac)
    
    # verify ip address when ping traceroute windows open is the same with AP ip address 
    logging.info("Verify default IP address display when open ping traceroute windows for AP[%s]" % ap_mac)
    current_ip_addr = lib.zd.pt.get_current_ip_addr(cfg['zd'])
    if current_ip_addr != cfg['ap'].ip_addr: 
        cfg['errmsg'] = "Default IP address is '%s' instead of '%s'" % (current_ip_addr, cfg['ap'].ip_addr)
        
    # verify ping command to AP 
    logging.info("Verify ping command to AP IP Address[%s]" % cfg['ap'].ip_addr)
    result = lib.zd.pt.perform_ping_test(cfg['zd'])
    logging.info("Ping result: %s" % result)
    
    # close ping trace route windows
    logging.info("Close Ping & Trace Route window")
    lib.zd.pt.close_ping_traceroute_windows(cfg['zd'])
    return cfg

def _test_traceroute_on_ap(cfg):
    ap_mac = cfg['ap'].get_base_mac()
    logging.info("Open ping and trace route windows for AP[%s]" % ap_mac)
    lib.zd.aps.open_pingtool_by_mac_addr(cfg['zd'], ap_mac)
    
    # verify ip address when ping traceroute windows open is the same with AP ip address 
    logging.info("Verify default IP address display when open ping traceroute windows for AP[%s]" % ap_mac)
    current_ip_addr = lib.zd.pt.get_current_ip_addr(cfg['zd'])
    if current_ip_addr != cfg['ap'].ip_addr: 
        cfg['errmsg'] = "Default IP address is '%s' instead of '%s'" % (current_ip_addr, cfg['ap'].ip_addr)
        
    # verify trace route command to AP 
    logging.info("Verify trace route command to AP IP Address[%s]" % cfg['ap'].ip_addr)
    result = lib.zd.pt.perform_traceroute_test(cfg['zd'])
    logging.info("Trace route: %s" % result)
    if "Timeout" in result: 
        cfg['errmsg'] = result
    
    # close ping trace route windows
    logging.info("Close Ping & Trace Route window")
    lib.zd.pt.close_ping_traceroute_windows(cfg['zd'])
    return cfg

    
def _test_ping_on_sta(cfg):
    sta_mac_addr = cfg['sta_wifi_mac_addr']
    logging.info("Open ping and trace route windows for Station[%s]" % cfg['sta_wifi_ip_addr'])
    lib.zd.cac.open_client_pingtool_by_mac_addr(cfg['zd'], sta_mac_addr)
    
    # verify ip address when ping traceroute windows open is the same with AP ip address 
    logging.info("Verify default IP address display when open ping traceroute windows for STA[%s]" % cfg['sta_wifi_ip_addr'])
    current_ip_addr = lib.zd.pt.get_current_ip_addr(cfg['zd'])
    if current_ip_addr != cfg['sta_wifi_ip_addr']: 
        cfg['errmsg'] = "Default IP address is '%s' instead of '%s'" % (current_ip_addr, cfg['sta_wifi_ip_addr'])
        
    # verify ping command to STA 
    logging.info("Verify ping command to STA IP Address[%s]" % cfg['sta_wifi_ip_addr'])
    result = lib.zd.pt.perform_ping_test(cfg['zd'])
    logging.info("Result: %s" % result)
    if "Timeout" in result: 
        cfg['errmsg'] = result
    
    # close ping trace route windows
    logging.info("Close Ping & Trace Route window")
    lib.zd.pt.close_ping_traceroute_windows(cfg['zd'])

    return cfg

def _test_traceroute_on_sta(cfg):
    sta_mac_addr = cfg['sta_wifi_mac_addr']
    logging.info("Open ping and trace route windows for Station[%s]" % cfg['sta_wifi_ip_addr'])
    lib.zd.cac.open_client_pingtool_by_mac_addr(cfg['zd'], sta_mac_addr)
    
    # verify ip address when ping traceroute windows open is the same with AP ip address 
    logging.info("Verify default IP address display when open ping traceroute windows for STA[%s]" % cfg['sta_wifi_ip_addr'])
    current_ip_addr = lib.zd.pt.get_current_ip_addr(cfg['zd'])
    if current_ip_addr != cfg['sta_wifi_ip_addr']: 
        cfg['errmsg'] = "Default IP address is '%s' instead of '%s'" % (current_ip_addr, cfg['sta_wifi_ip_addr'])
        
    # verify trace route command to STA 
    logging.info("Verify ping command to STA IP Address[%s]" % cfg['sta_wifi_ip_addr'])
    result = lib.zd.pt.perform_traceroute_test(cfg['zd'])
    logging.info("Result: %s" % result)
    
    # close ping trace route windows
    logging.info("Close Ping & Trace Route window")
    lib.zd.pt.close_ping_traceroute_windows(cfg['zd'])
    
    return cfg
    
 
def _remove_all_cfg_from_zd(zd):
    logging.info("Remove all configuration from the Zone Director")
    zd.remove_all_cfg()

def _remove_all_wlan_from_station(cfg):
    tconfig.remove_all_wlan_from_station(cfg['sta'], check_status_timeout = cfg['check_status_timeout'])
