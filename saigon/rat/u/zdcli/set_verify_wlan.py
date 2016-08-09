'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
            'name':None,
            'ssid': None, 
            'description': None, 
            'type': '',
            'hotspot_name': '',
                        
            'auth': '', #Authentication
            'encryption': '', 
            'key_string': '', 
            'key_index': '', 
            'passphrase':'',
            'auth_server': '',
            'algorithm':'',
            'eap_type':None,
            
            'web_auth': None, 
            'client_isolation': None, 
            'zero_it': None, 
            'priority':'',
            
            'acc_server':None,
            'interim':None,
            'l2acl':'',
            'l3acl': '', 
            'rate_limit_uplink': '', 
            'rate_limit_downlink': '',
            'vlan_id':'',
            'hide_ssid':None, # Closed System
            'tunnel_mode': None, 
            'bgscan':None,
            'load_balance':None,
            'max_clients':None,
            'dvlan': None,
            }
Examples: 
tea.py u.zdcli.config_wlan 
'''

import logging
import random
import time
import copy

from RuckusAutoTest.components.lib.zdcli import set_wlan
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
    create_zd_by_ip_addr
)
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.components.lib.zdcli import get_wlan_info
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi


default_cfg = dict(ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54! zqrODRKoyUMq1KNjADvhGeU7tgjt56ap',
                   )
def _generate_wlan_cfg_list():
    
    auth_server = 'test'
    _wlan_cfgs = []
    _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(2,32),type = 'alpha'),
                           ssid = 'open-none-'+ utils.make_random_string(random.randint(1,22),type = 'alpha'),
                           description = utils.make_random_string(random.randint(1,64),type = 'alpha'),
                           type = 'standard-usage'
                           ))
    
    _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(2,32),type = 'alpha'),
                           ssid = 'open-wep-64'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
                           auth = "open", encryption = "wep-64",
                           key_index = random.randint(1,4) , key_string = utils.make_random_string(10, "hex"),
                           type = 'guest-access'
                           ))
    
    _wlan_cfgs.append(dict(name = 'open-wep-128'+ utils.make_random_string(random.randint(1,20),type = 'alpha'),
                           auth = "open", encryption = "wep-128",
                           key_index = random.randint(1,4) , key_string = utils.make_random_string(26, "hex"),
                           type ='hotspot',hotspot_name = 'test'
                           ))
    
    _wlan_cfgs.append(dict(name= 'share-wep-64-' + utils.make_random_string(random.randint(1,19),type = 'alpha'),
                           auth = "shared", encryption = "wep-64",
                           key_string = utils.make_random_string(10, "hex"),
                           key_index = random.randint(1,4),
                           client_isolation = 'none'
                           ))

    _wlan_cfgs.append(dict(name = 'share-wep-128-' + utils.make_random_string(random.randint(1,18),type = 'alpha'),
                           auth = "shared", encryption = "wep-128",
                           key_string = utils.make_random_string(26, "hex"),
                           key_index = random.randint(1,4),
                           client_isolation = 'local'
                           ))

    _wlan_cfgs.append(dict(name = 'open-wpa-'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
                           auth = "open", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           client_isolation = 'full'
                           ))
    

    _wlan_cfgs.append(dict(name = 'open-wpa2-'+ utils.make_random_string(random.randint(1,20),type = 'alpha'),
                           auth = "open", encryption = "wpa2",algorithm = random.choice(['AES','auto']),
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           priority = 'low'
                           ))

    _wlan_cfgs.append(dict(name = 'open-wpa-mixed'+ utils.make_random_string(random.randint(1,18),type = 'alpha'),
                           auth = "open", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           priority = 'high'
                           ))

    _wlan_cfgs.append(dict(name = 'mac-none-'+ utils.make_random_string(random.randint(1,23),type = 'alpha'),
                           auth = 'mac',
                           encryption ='none',
                           auth_server = auth_server,
                           max_clients = random.randint(1, 100)
                           ))
    
    _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(2,32),type = 'alpha'),
                           ssid = 'mac-wep-64'+ utils.make_random_string(random.randint(1,22),type = 'alnum'),
                           auth = "mac", encryption = "wep-64",
                           key_index = random.randint(1,4) , key_string = utils.make_random_string(10, "hex"),
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'mac-wep-128-'+ utils.make_random_string(random.randint(1,20),type = 'alnum'),
                           auth = "mac", encryption = "wep-128",
                           key_index = random.randint(1,4) , key_string = utils.make_random_string(26, "hex"),
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'mac-wpa-'+ utils.make_random_string(random.randint(1,22),type = 'alnum'),
                           auth = "mac", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           auth_server = auth_server
                           ))

    _wlan_cfgs.append(dict(name = 'mac-wpa2-'+ utils.make_random_string(random.randint(1,21),type = 'alnum'),
                           auth = "mac", encryption = "wpa2", algorithm = random.choice(['TKIP','AES','auto']),
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           auth_server = auth_server
                           ))

    _wlan_cfgs.append(dict(name = 'mac-wpa-mixed'+ utils.make_random_string(random.randint(1,19),type = 'alnum'),
                           auth = "mac", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
                           passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                           auth_server = auth_server))
    
    _wlan_cfgs.append(dict(name = 'dot1x-eap-sim-'+ utils.make_random_string(random.randint(1,17),type = 'alnum'),
                           auth = 'dot1x-eap',
                           encryption = 'none',
                           eap_type = 'EAP-SIM',
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-eap-sim-local-'+ utils.make_random_string(random.randint(1,11),type = 'alnum'),
                           auth = 'dot1x-eap',
                           encryption = 'none',
                           eap_type = 'EAP-SIM',
                           auth_server = 'local'
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-eap-peap-'+ utils.make_random_string(random.randint(1,17),type = 'alnum'),
                           auth = 'dot1x-eap',
                           encryption = 'none',
                           eap_type = 'PEAP',
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-eap-peap-local-'+ utils.make_random_string(random.randint(1,11),type = 'alnum'),
                           auth = 'dot1x-eap',
                           encryption = 'none',
                           eap_type = 'PEAP',
                           auth_server = 'local'
                           ))
    
    _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(1,32),type = 'alpha'),
                           ssid = 'dot1x-wep-64-'+ utils.make_random_string(random.randint(1,19),type = 'alnum'),
                           auth = "dot1x-eap", encryption = "wep-64",
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(1,32),type = 'alpha'),
                           ssid = 'dot1x-wep-64-local-'+ utils.make_random_string(random.randint(1,13),type = 'alnum'),
                           auth = "dot1x-eap", encryption = "wep-64",
                           auth_server = 'local'
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-wep-128-'+ utils.make_random_string(random.randint(1,18),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wep-128",
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-wep-128-local-'+ utils.make_random_string(random.randint(1,11),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wep-128",
                           auth_server = 'local'
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-wpa-'+ utils.make_random_string(random.randint(1,22),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-wpa-local-'+ utils.make_random_string(random.randint(1,10),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
                           auth_server = 'local'
                           ))

    _wlan_cfgs.append(dict(name = 'dot1x-wpa2-'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wpa2", algorithm = random.choice(['TKIP','AES','auto']),
                           auth_server = auth_server
                           ))
    
    _wlan_cfgs.append(dict(name = 'dot1x-wpa2-local-'+ utils.make_random_string(random.randint(1,15),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wpa2", algorithm = random.choice(['TKIP','AES','auto']),
                           auth_server = 'local'
                           ))

    _wlan_cfgs.append(dict(name = 'dot1x-wpa-mixed'+ utils.make_random_string(random.randint(1,17),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
                           auth_server = auth_server))  
    
    _wlan_cfgs.append(dict(name = 'dot1x-wpa-mixed-local'+ utils.make_random_string(random.randint(1,10),type = 'alpha'),
                           auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
                           auth_server = 'local'
                           )) 
    
    logging.info('Generate a list of [%d] wlans configuration',len(_wlan_cfgs))
    
    return _wlan_cfgs
                

def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    cfg['zdcli'] = create_zd_cli_by_ip_addr(ip_addr=cfg['ip_addr'],
                                            username=cfg['username'],
                                            password=cfg['password'],
                                            shell_key=cfg['shell_key'])
    
    cfg['zd'] = create_zd_by_ip_addr(ip_addr=cfg['ip_addr'],)
    return cfg


def do_test(tcfg):
    zdcli = tcfg['zdcli']
    zd = tcfg['zd']
    lib.zd.wlan.delete_all_wlans(zd)
    wlan_conf_list = _generate_wlan_cfg_list()

    logging.info('Create 21 WLANs via CLI')
    set_wlan.create_multi_wlans(zdcli, wlan_conf_list)
    logging.info("Wlan config list is %s" % wlan_conf_list)
    
    wlan_info_cli = get_wlan_info.get_wlan_all(zdcli)
    logging.info("get wlan info %s" % wlan_info_cli)
   
    if not set_wlan.verify_wlan_all_between_set_and_get(wlan_conf_list, wlan_info_cli):
        return("FAIL", "Wlan config are different wlan CLI Get")
    
    zd.s.refresh()
    
    wlan_name_list = wlan_zd.get_wlan_list(zd)
    
    gui_get = wlan_zd.get_all_wlan_conf_detail(zd, wlan_name_list)

    logging.info("GUI info is %s" % gui_get)
    
    if not set_wlan.verify_wlan_between_cli_set_and_gui_get(wlan_conf_list, gui_get):
        return("FAIL", "Wlan config are different with GUI Get")
    
    wlan_name = random.choice(wlan_name_list)
    set_wlan.remove_wlan_config(zdcli,wlan_name)

    wlan_info = gwi.get_wlan_by_ssid(zdcli, wlan_name)
    if not set_wlan._verify_wlan_after_remove_cfg(wlan_info):
            return('FAIL', 'There are configurations after removing configurations on ZD')
    
    return ("PASS", "Create wlan information from ZD CLI successfully!")
  
  
def do_clean_up(tcfg):
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

