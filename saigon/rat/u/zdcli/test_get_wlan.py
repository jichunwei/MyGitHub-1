'''
Author: Serena Tan
Email: serena.tan@ruckuswireless.com

To verify whether the wlan information getting form ZD CLI is correct after configuring in GUI:
    + Start the ZD and ZD CLI.
    + Remove all configuration from ZD via GUI.
    + Get all wlan information from ZD CLI by command [show wlan all].
    + Verify whether there is no wlan in ZD CLI. 
    + Create a radius server.
    + Configure 32 WLANs including 13 encryption types via GUI.         
    + Get all wlan information from ZD CLI by command [show wlan all].
    + Verify whether the informaiton of all wlan is correct.
    + Get the information of a wlan by ssid from ZD CLI by command [show wlan name {ssid}].
    + Verify whether the information of the wlan is correct.
    + Delete all wlan via GUI.
    + Get all wlan information from ZD CLI by command [show wlan all].
    + Verify whether there is no wlan in ZD CLI. 
    + Get the information of a wlan by ssid from ZD CLI by command [show wlan name {ssid}].
    + Verify whether the wlan does not exist.

Examples: 
tea.py u.zdcli.get_wlan_info
'''

import logging
import random
import time
import copy
from pprint import pformat

from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi
from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd.aaa_servers_zd import (
    create_server,
    remove_all_servers,
)


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54! zqrODRKoyUMq1KNjADvhGeU7tgjt56ap',
                   ras_ip_addr = '192.168.0.252',
                   ras_port = '1812',
                   ras_name = '',
                   radius_auth_secret = '1234567890',)


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
       
    _ras_cfg = {}
    _ras_cfg['server_addr'] = cfg.pop('ras_ip_addr')
    _ras_cfg['server_port'] = cfg.pop('ras_port')
    _ras_cfg['server_name'] = cfg.pop('ras_name')
    _ras_cfg['radius_auth_secret'] = cfg.pop('radius_auth_secret')
    cfg['ras_cfg'] = _ras_cfg
    
    cfg['zd'] = create_zd_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'])
    
    _remove_all_cfg_from_zd(cfg['zd'])
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    
    return cfg


def do_test(tcfg):
    zdcli = tcfg['zdcli']
    zd = tcfg['zd']
    ras_cfg = tcfg['ras_cfg']
    
    wlan_info = gwi.get_wlan_all(zdcli)
    re = gwi.verify_wlan_info_all(wlan_info, None)
    if not re:
        return ("FAIL", 'There are wlans in ZD CLI but not in ZD GUI.')
    
    create_server(zd, **ras_cfg)    
    
    wlan_cfg_list = _generate_wlan_cfg_list(ras_cfg['server_addr'])
    
    wlan_zd.create_multi_wlans(zd, wlan_cfg_list)
    
    wlan_info = gwi.get_wlan_all(zdcli)
    re = gwi.verify_wlan_info_all(wlan_info, wlan_cfg_list)
    if not re:
        return ("FAIL", 'Fail to verify all wlan information shown in ZD CLI.')
 
    wlan_info = gwi.get_wlan_by_ssid(zdcli, wlan_cfg_list[31]['ssid'])
    re = gwi.verify_wlan_info(wlan_info, wlan_cfg_list[31])
    if not re:
        return ("FAIL", 'Fail to verify the wlan [%s] information shown in ZD CLI.' % wlan_cfg_list[31]['ssid'])
 
    wlan_zd.delete_all_wlans(zd)
    
    wlan_info = gwi.get_wlan_all(zdcli)
    re = gwi.verify_wlan_info_all(wlan_info, None)
    if not re:
        return ("FAIL", 'There are wlans in ZD CLI but not in ZD GUI.')
    
    wlan_info = gwi.get_wlan_by_ssid(zdcli, wlan_cfg_list[31]['ssid'])
    re = gwi.verify_wlan_info(wlan_info, None)
    if not re:
        return ("FAIL", 'The wlan [%s] exists in ZD CLI but not in ZD GUI.' % wlan_cfg_list[31]['ssid'])    
 
    return ("PASS", "Test getting wlan information from ZD CLI successfully!")
  
  
def do_clean_up(tcfg):
    remove_all_servers(tcfg['zd'])
    clean_up_rat_env()
    del(tcfg['zdcli'])


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res


def _remove_all_cfg_from_zd(zd):
    logging.info("Remove all configuration from the Zone Director")
    zd.remove_all_cfg()
    wlan_zd.delete_all_wlans(zd)

    
def _generate_wlan_cfg_list(ras_ip_addr): 
    logging.info('Generate a list of 32 wlan configuration')
    
    _wlan_cfgs = []
    _wlan_cfgs.append(dict(ssid = "", auth = "open", wpa_ver = "", encryption = "none",
                          key_index = "" , key_string = "",
                          username = "", password = "", auth_svr = ""))
    
    _wlan_cfgs.append(dict(ssid = "", auth = "open", wpa_ver = "", encryption = "WEP-64",
                          key_index = "1" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))
    
    _wlan_cfgs.append(dict(ssid = "", auth = "open", wpa_ver = "", encryption = "WEP-128",
                          key_index = "1" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = ""))
    
    _wlan_cfgs.append(dict(ssid = "", auth = "shared", wpa_ver = "", encryption = "WEP-64",
                          key_index = "" , key_string = utils.make_random_string(10, "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "shared", wpa_ver = "", encryption = "WEP-128",
                          key_index = "" , key_string = utils.make_random_string(26, "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = utils.make_random_string(random.randint(8, 63), "hex"),
                          username = "", password = "", auth_svr = ""))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA2", encryption = "TKIP",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))

    _wlan_cfgs.append(dict(ssid = "", auth = "EAP", wpa_ver = "WPA2", encryption = "AES",
                          key_index = "" , key_string = "",
                          username = "ras.eap.user", password = "ras.eap.user", auth_svr = ras_ip_addr))
    
    wlan_cfgs = []
    number = 1
    key_index = 1
    
    while True:
        for i in range(len(_wlan_cfgs)):
            if number > 32:
                for j in range(len(wlan_cfgs)):
                    logging.info('[%s]\n%s' % (wlan_cfgs[j]['ssid'], pformat(wlan_cfgs[j], 4, 120)))
                return wlan_cfgs
            
            conf = copy.deepcopy(_wlan_cfgs[i])
            conf['ssid'] = "zdcli-wlan-%s-%d" % (time.strftime("%H%M%S"), number)
            
            if _wlan_cfgs[i]['auth'] == 'shared':
                if key_index < 5:
                    conf['key_index'] = "%d" % key_index
                    wlan_cfgs.append(conf)
                    key_index += 1
                    number += 1                  
            else:
                wlan_cfgs.append(conf)
                number += 1
