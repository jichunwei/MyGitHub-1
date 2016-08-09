'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
             
            }
Examples: 
tea.py u.zdcli.set_verify_sr
'''

import logging
import random

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
    create_zd_by_ip_addr
)
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr 
from RuckusAutoTest.components.lib.zd import redundancy_zd as sr_zd
from RuckusAutoTest.components.lib.zd import access_control_zd as acl

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
    
    cfg['zd'] = create_zd_by_ip_addr(ip_addr=cfg['ip_addr'],)
    return cfg


def do_test(tcfg):
    zdcli = tcfg['zdcli']
    zd = tcfg['zd']
    
    sr_conf = def_sr_conf()
    
    sr.set_sr_peer_ip(zdcli, sr_conf)
    sr.set_sr_secret(zdcli, sr_conf)

    
    sr_cli_get = sr.show_sr_info(zdcli)
    '''
    {'Smart Redundancy': {'Peer IP Address': '',
                      'Shared Secret': '',
                      'Status': 'Disabled'}}
    '''
    
    sr_gui_get = sr_zd.get_sr_info(zd)
    '''
    {'Peer IP Address': u'192.168.0.3',
     'Shared Secret': u'ucyw6k1tcb0',
     'State': 'Disabled'}
    '''
    logging.info("Verify CLI Set and CLI Get")
    if sr_conf['peer_ip_addr'] != sr_cli_get['Smart Redundancy']['Peer IP Address']:
        return("FAIL, peer ip addr is different")
    
    if sr_conf['secret'] != sr_cli_get['Smart Redundancy']['Shared Secret']:
        logging.info("SR Config secret is [%s] and CLI Get is [%s]" %(sr_conf['secret'],sr_cli_get['Smart Redundancy']['Shared Secret']))
        return("FAIL, Secret is different")
    
    
    if sr_conf['peer_ip_addr'] != sr_gui_get['Peer IP Address']:
        return("FAIL, peer ip addr is different")
    
    if sr_conf['secret'] != sr_gui_get['Shared Secret']:
        return("FAIL, Secret is different")
    
    
    
    
    
    return ("PASS")


def do_clean_up(tcfg):
    clean_up_rat_env()
    del(tcfg['zdcli'])

def def_sr_conf():
    conf = {}
    conf['peer_ip_addr'] = '192.168.0.3'
    conf['secret'] = utils.make_random_string(random.randint(1,15),type = 'alnum')
    
    return conf

def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res

