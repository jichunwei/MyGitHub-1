'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
            'name': None, 
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
)


default_cfg = dict(ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54! zqrODRKoyUMq1KNjADvhGeU7tgjt56ap',
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    cfg['zdcli'] = create_zd_cli_by_ip_addr(ip_addr=cfg['ip_addr'],
                                            username=cfg['username'],
                                            password=cfg['password'],
                                            shell_key=cfg['shell_key'])
    return cfg


def do_test(tcfg):
    wlan_conf = {}
    wlan_conf.update(tcfg)
    set_wlan.create_wlan(tcfg['zdcli'], wlan_conf)
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

