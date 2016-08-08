'''
To test wlan with different encryption types:
    Open_System, 
    Open_WEP_64_key_1, 
    Open_WEP_128_key_1, 
    Shared_WEP_64_key_1,
    Shared_WEP_128_key_1, 
    WPA_PSK_TKIP, 
    WPA_PSK_AES, 
    WPA2_PSK_TKIP, 
    WPA2_PSK_AES, 
    EAP_WPA_TKIP_RADIUS, 
    EAP_WPA_AES_RADIUS, 
    EAP_WPA2_TKIP_RADIUS, 
    EAP_WPA2_AES_RADIUS.

    + Start the ZD, AP and Station.
    + Remove all configuration from ZD.
    + Remove all WLANs from the station.
    + If use radius server, create the radius server.
    + Configure a WLAN with a encryption type on ZD.
    + Verify the status of the WLAN on AP. 
    + Configure a WLAN on the station with the same configuration as the WLAN on ZD and ssociation the Station.         
    + Get the WIFI IP address and MAC address of the station.
    + Verify whether the station can ping to the target IP. 
    + Verify the information of the station shown on ZD.
    + Verify the information of the station shown on AP.
        
Examples: 
tea.py u.zd.encryption_types_tea type=Open_System ap_ip_addr=192.168.0.1 radio_mode=ng
tea.py u.zd.encryption_types_tea type=EAP_WPA_TKIP_RADIUS ap_ip_addr=192.168.0.1 radio_mode=na
'''

import logging
import time
import random

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_station_by_ip_addr,
    create_ruckus_ap_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.common import Ratutils as utils


encryption_index = {
    'Open_System' : 0,
    'Open_WEP_64_key_1' : 1,
    'Open_WEP_128_key_1' : 2,
    'Shared_WEP_64_key_1' : 3,
    'Shared_WEP_128_key_1' : 4,
    'WPA_PSK_TKIP' : 5,
    'WPA_PSK_AES' : 6,
    'WPA2_PSK_TKIP' : 7,
    'WPA2_PSK_AES' : 8,
    'EAP_WPA_TKIP_RADIUS' : 9,
    'EAP_WPA_AES_RADIUS' : 10,
    'EAP_WPA2_TKIP_RADIUS' : 11,
    'EAP_WPA2_AES_RADIUS' : 12,
}

default_cfg = dict(
    type = 'Open_System',
    radio_mode = 'ng',
    ap_ip_addr = '192.168.0.1',
    zd_ip_addr = '192.168.0.2',
    sta_ip_addr = '192.168.1.11',
    ras_ip_addr = '192.168.0.252',
    des_ip = '192.168.0.252',
    ping_timeout_ms = 150 * 1000,
    check_status_timeout = 120,
)


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)
    
    wlan_cfgs = _define_wlan_cfgs(_cfg['radio_mode'], _cfg['ras_ip_addr'])
    index = encryption_index[_cfg['type']]
    _cfg['wlan_cfg'] = wlan_cfgs[index]
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg['zd_ip_addr'])
    _cfg['ap'] = create_ruckus_ap_by_ip_addr(_cfg['ap_ip_addr'], 'admin', 'admin')
    _cfg['sta'] = create_station_by_ip_addr(_cfg['sta_ip_addr'])

    return _cfg


def do_test(cfg): 
    cfg['errmsg'] = ''
    
    _remove_all_cfg_from_zd(cfg['zd'])
    
    _remove_all_wlan_from_station(cfg)
    
    _create_auth_server(cfg['zd'], cfg['wlan_cfg'])
    
    _cfg_wlan_on_zd(cfg['zd'], cfg['wlan_cfg'])
    
    _verify_wlan_on_aps(cfg)    
    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg
    
    _assoc_station_with_ssid(cfg)        
    if not cfg['errmsg']:
        _get_sta_wifi_ip(cfg)
        _test_stat_connectivity(cfg)
    else:
        _test_wlan_in_the_air(cfg)

    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg
    
    _verify_station_info_on_ZD(cfg)  
    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg
    
    _verify_station_info_on_ap(cfg)
    if cfg['errmsg']:
        cfg['result'] = 'FAIL'
        return cfg
    
    cfg['result'] = 'PASS'
    return cfg
                                                                                                                  
                                                                                                                                                                                  
def do_clean_up(cfg):
    _remove_all_cfg_from_zd(cfg['zd'])
    
    _remove_all_wlan_from_station(cfg)
    
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)

    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
        
    return (res['result'], res['errmsg'])
    

def _define_wlan_cfgs(radio_mode, ras_ip_addr):
    ssid = "rat-encryptions-11%s-%s" % (radio_mode, time.strftime("%H%M%S"))
    
    wlan_cfgs = []
    wlan_cfgs.append(dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "WEP-64",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "WEP-64",
                           key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "open", wpa_ver = "", encryption = "WEP-128",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "WEP-128",
                           key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "shared", wpa_ver = "", encryption = "WEP-64",
                           sta_auth = "shared", sta_wpa_ver = "", sta_encryption = "WEP-64",
                           key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "shared", wpa_ver = "", encryption = "WEP-128", sta_auth = "shared", sta_wpa_ver = "",
                           sta_encryption = "WEP-128", key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                           sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False))

    wlan_cfgs.append(dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                           sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True))

    wlan_cfgs.append(dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                           sta_auth = "EAP", sta_wpa_ver = "WPA", sta_encryption = "AES",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True))

    wlan_cfgs.append(dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                           sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True))

    wlan_cfgs.append(dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                           sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                           key_index = "" , key_string = "",
                           username = "ras.eap.user", password = "ras.eap.user", ras_addr = ras_ip_addr, ras_port = "1812",
                           ras_secret = "1234567890", use_radius = True))

    return wlan_cfgs
 
 
def _remove_all_cfg_from_zd(zd):
    logging.info("Remove all configuration from the Zone Director")
    zd.remove_all_cfg()


def _create_auth_server(zd, wlan_cfg):    
    if wlan_cfg['auth'] == "EAP":
        if wlan_cfg['use_radius']:
            logging.info("Create an radius server")
            zd.create_radius_server(wlan_cfg['ras_addr'], wlan_cfg['ras_port'], wlan_cfg['ras_secret'])
        else:
            logging.info("Create a user on the ZoneDirector")
            zd.create_user(wlan_cfg['username'], wlan_cfg['password'])


def _cfg_wlan_on_zd(zd, wlan_cfg):
    logging.info("Configure a WLAN with SSID [%s] on the Zone Director" % wlan_cfg['ssid'])
    zd.cfg_wlan(wlan_cfg)
    time.sleep(10)


def  _verify_wlan_on_aps(cfg):
    cfg['errmsg'] = tmethod.verify_wlan_on_aps(cfg['ap'], cfg['wlan_cfg']['ssid'])


def _assoc_station_with_ssid(cfg):
    cfg['errmsg'] = tmethod.assoc_station_with_ssid(cfg['sta'], cfg['wlan_cfg'], cfg['check_status_timeout'])


def _get_sta_wifi_ip(cfg):
    res, val1, val2 = tmethod.renew_wifi_ip_address(cfg['sta'], cfg['check_status_timeout'])
    
    if not res:
        raise Exception(val2)
    
    cfg['sta_wifi_ip_addr'] = val1
    cfg['sta_wifi_mac_addr'] = val2.lower()


def _test_stat_connectivity(cfg):
    cfg['errmsg'] = tmethod.client_ping_dest_is_allowed(cfg['sta'], cfg['des_ip'], ping_timeout_ms = cfg['ping_timeout_ms'])

 
def _test_wlan_in_the_air(cfg):
    cfg['errmsg'] = tmethod.verify_wlan_in_the_air(cfg['sta'], cfg['ssid'])
   

def _verify_station_info_on_ZD(cfg):
    wlan_cfg = cfg['wlan_cfg']
    
    logging.info("Verify information of the target station shown on the Zone Director")
    
    if cfg['radio_mode'] == 'g' or wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:
        expected_radio_mode = ['802.11b/g', '802.11a']     
    else:
        expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        
    if wlan_cfg['auth'] == 'EAP':
        expected_ip = wlan_cfg['username']
    else:
        expected_ip = cfg['sta_wifi_ip_addr']
            
    exp_client_info = {"ip": expected_ip, 
                       "status": "Authorized", 
                       "wlan": cfg['wlan_cfg']['ssid'],
                       "radio": expected_radio_mode, 
                       "apmac": cfg['ap'].base_mac_addr}
    
    cfg['errmsg'], cfg['client_info_on_zd'] = tmethod.verify_zd_client_status(cfg['zd'], cfg['sta_wifi_mac_addr'], exp_client_info, cfg['check_status_timeout'])


def _verify_station_info_on_ap(cfg):
    cfg['errmsg'] = tmethod.verify_station_info_on_ap(cfg['ap'], cfg['sta_wifi_mac_addr'], cfg['wlan_cfg']['ssid'], cfg['client_info_on_zd']['channel'])


def _remove_all_wlan_from_station(cfg):
    tconfig.remove_all_wlan_from_station(cfg['sta'], check_status_timeout = cfg['check_status_timeout'])

