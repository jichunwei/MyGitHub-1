"""
    Description:
        Configure WPA-Mixed encryption support from 9.0 
    Prerequisites:
       - Wireless Station with RatToolAgent running
       - Zone Director with 1 AP under ZD control
    usage:
        tea.py <wpa_mixed key/value> ...
        
        where <scaling_zd_restart key/value pair> are:
        - zd_ip_addr = '192.168.0.2' 
        - sta_ip_addr = '192.168.1.11'
        - test_name = "WPA-Mixed PSK TKIP - Station WPA-TKIP"
        notes: support test name values: 
        - "WPA-Mixed PSK TKIP - Station WPA-TKIP"
        - "WPA-Mixed PSK AES - Station WPA EAS"
        - "WPA-Mixed PSK TKIP - Station WPA2 TKIP"
        - "WPA-Mixed PSK AES - Station WPA2 AES"
        - "WPA-Mixed PSK Auto - Station WPA TKIP"
        - "WPA-Mixed PSK Auto - STA WPA AES"
        - "WPA-Mixed PSK Auto - Station WPA2 TKIP"
        - "WPA-Mixed PSK Auto - Station WPA2 AES"
        
    Examples:
        tea.py wpa_mixed te_root=u.zd.encryptions test_name="WPA-Mixed PSK TKIP - Station WPA-TKIP"
        tea.py wpa_mixed te_root=u.zd.encryptions zd_ip_addr='192.168.0.2' sta_ip_addr='192.168.1.11' test_name="WPA-Mixed PSK TKIP - Station WPA TKIP"

"""
import logging, time
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_station_by_ip_addr,
    clean_up_rat_env,
)

default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    sta_ip_addr = '192.168.1.11',
    check_status_timeout = 120,
    ping_timeout_ms = 150 * 1000
)

components = dict()
wlan_cfg = dict()

wlan_cfg_list = dict()    
wlan_cfg_list['WPA-Mixed PSK TKIP - Station WPA TKIP'] =  {'auth': 'PSK',
          'encryption': 'TKIP',
          'key_string': 'f2322696c801b45bc63e8cd8c33842a7ce37bcd1f912d869948e6828358d34',
          'ssid': 'rat-encryptions-wpa-mixed',
          'sta_auth': 'PSK',
          'sta_encryption': 'TKIP',
          'sta_wpa_ver': 'WPA',            
          'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK AES - Station WPA EAS'] = {'auth': 'PSK',
         'encryption': 'AES',
         'key_string': '3c29a84e8bc1357615dca',
         'ssid': 'rat-encryptions-wpa-mixed',
         'sta_auth': 'PSK',
         'sta_encryption': 'AES',
         'sta_wpa_ver': 'WPA',
         'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK TKIP - Station WPA2 TKIP'] = {'auth': 'PSK',
         'encryption': 'TKIP',
         'key_string': '4a0f19d85a8f4818c4470cf68af4fc459ade606da69d920c4d5bf571',
         'ssid': 'rat-encryptions-wpa-mixed',
         'sta_auth': 'PSK',
         'sta_encryption': 'TKIP',
         'sta_wpa_ver': 'WPA2',
         'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK AES - Station WPA2 AES'] =  {'auth': 'PSK',
          'encryption': 'AES',
          'key_string': 'cbd56100ee',
          'ssid': 'rat-encryptions-11g-230218',
          'sta_auth': 'PSK',
          'sta_encryption': 'AES',
          'sta_wpa_ver': 'WPA2',
          'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK Auto - Station WPA TKIP'] = {'auth': 'PSK',
              'encryption': 'Auto',
              'key_string': '8d32e379824340ec6db21f5849419c63b6ddaaaf1e3',
              'ssid': 'rat-encryptions-11g-230218',
              'sta_auth': 'PSK',
              'sta_encryption': 'TKIP',
              'sta_wpa_ver': 'WPA',
              'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK Auto - STA WPA AES'] = {'auth': 'PSK',
             'encryption': 'Auto',
             'key_string': 'df16f4b7684cf',
             'ssid': 'rat-encryptions-11g-230218',
             'sta_auth': 'PSK',
             'sta_encryption': 'AES',
             'sta_wpa_ver': 'WPA',
             'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK Auto - Station WPA2 TKIP'] = {'auth': 'PSK',
             'encryption': 'Auto',
             'key_string': '9e21a2b4bad414e32ca0357f636866075e09a4739e98220e3aacff170',
             'ssid': 'rat-encryptions-11g-230218',
             'sta_auth': 'PSK',
             'sta_encryption': 'TKIP',
             'sta_wpa_ver': 'WPA2',
             'wpa_ver': 'WPA_Mixed'}

wlan_cfg_list['WPA-Mixed PSK Auto - Station WPA2 AES'] = {'auth': 'PSK',
             'encryption': 'Auto',
             'key_string': '461ce288b703b14866e677f17638b521be7ede1059f2',
             'ssid': 'rat-encryptions-11g-230218',
             'sta_auth': 'PSK',
             'sta_encryption': 'AES',
             'sta_wpa_ver': 'WPA2',
             'wpa_ver': 'WPA_Mixed'}

def do_config( **kwargs ):
    global components
    # Connect to ZD and remove all configuration
    components['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))
    components['zd'].remove_all_cfg()
    # Connect to wireless station
    components['sta'] = create_station_by_ip_addr(default_cfg.pop('sta_ip_addr'))
 
def do_test(**kwargs ):
    # create wlan on ZD
    lib.zd.wlan.create_wlan(components['zd'],wlan_cfg)
    time.sleep(10)
    # test client associate to ssid  
    errmsg = test_station_assoc_with_ssid(wlan_cfg)    
    if errmsg: return ('FAIL', errmsg)
    
    sta_wifi_ip_addr, sta_wifi_mac_addr = cfg_get_sta_wifi_ipaddress()    
    if not sta_wifi_ip_addr: 
        return ('FAIL', 'Station failed to get ip address after associted to wlan[%s]' % wlan_cfg['ssid'])    
  
    errmsg = test_station_connectivity(kwargs['target_ip'])
    
    if errmsg: return ('FAIL', errmsg)
    return {'PASS':''}

def do_clean_up():
    components['zd'].remove_all_cfg()
    
def test_station_assoc_with_ssid(wlan_cfg):
    if wlan_cfg['wpa_ver'] == "WPA_Mixed":
        wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
        wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
    errmsg = tmethod.assoc_station_with_ssid(components['sta'], wlan_cfg, 120)
    return errmsg 

def cfg_get_sta_wifi_ipaddress():
    # Renew the IP address of the wireless adapter on the wireless station
    res, val1, val2 = tmethod.renew_wifi_ip_address(components['sta'], default_cfg['check_status_timeout'])

    if not res:
        raise Exception(val2)

    sta_wifi_ip_addr = val1
    sta_wifi_mac_addr = val2.lower()
    return sta_wifi_ip_addr, sta_wifi_mac_addr

def test_station_connectivity(target_ip):
    return tmethod.client_ping_dest_is_allowed(components['sta'], target_ip, ping_timeout_ms = default_cfg['ping_timeout_ms'])    
           
def usage():
    print """
    Description:
        Configure WPA-Mixed encryption support from 9.0 
    Prerequisites:
       - Wireless Station with RatToolAgent running
       - Zone Director with 1 AP under ZD control
    usage:
        tea.py <wpa_mixed key/value> ...
        
        where <scaling_zd_restart key/value pair> are:
        - zd_ip_addr = '192.168.0.2' 
        - sta_ip_addr = '192.168.1.11'
        - test_name = "WPA-Mixed PSK TKIP - Station WPA-TKIP"
        notes: support test name values: 
        - "WPA-Mixed PSK TKIP - Station WPA-TKIP"
        - "WPA-Mixed PSK AES - Station WPA EAS"
        - "WPA-Mixed PSK TKIP - Station WPA2 TKIP"
        - "WPA-Mixed PSK AES - Station WPA2 AES"
        - "WPA-Mixed PSK Auto - Station WPA TKIP"
        - "WPA-Mixed PSK Auto - STA WPA AES"
        - "WPA-Mixed PSK Auto - Station WPA2 TKIP"
        - "WPA-Mixed PSK Auto - Station WPA2 AES"
        
    Examples:
        tea.py wpa_mixed te_root=u.zd.encryptions test_name="WPA-Mixed PSK TKIP - Station WPA-TKIP"
        tea.py wpa_mixed te_root=u.zd.encryptions zd_ip_addr='192.168.0.2' sta_ip_addr='192.168.1.11' test_name="WPA-Mixed PSK TKIP - Station WPA TKIP"
    """
    
def main( **kwargs ):
    global wlan_cfg, default_cfg
    mycfg = dict(
                 debug=False,
                 target_ip = '192.168.0.252',
                 )
    mycfg.update(kwargs)
    if mycfg.has_key('test_name'): 
        wlan_cfg = wlan_cfg_list[mycfg['test_name']]
    else: 
        usage()
        return {"FAIL": "Missing test name" }
    
    if mycfg.has_key('zd_ip_addr'): 
        default_cfg['zd_ip_addr'] = mycfg['zd_ip_addr']

    if mycfg.has_key('sta_ip_addr'): 
        default_cfg['sta_ip_addr'] = mycfg['sta_ip_addr']
        
    do_config( **mycfg )    
    try:     
        msg = do_test(**mycfg)
        if msg.has_key('FAIL'):
            logging.error(msg['FAIL'])
            do_clean_up()
            return {"FAIL": msg }
        
        do_clean_up()
        
        return {"PASS":""}
    
    finally:
        components['zd'].s.shut_down_selenium_server()    