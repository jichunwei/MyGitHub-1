'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
             
            }
Examples: 
tea.py u.zdcli.set_verify_mgmt_if
'''

import logging
import random

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
    create_zd_by_ip_addr
)
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as mgmt 
from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt_if
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
    
    mgmt_if_conf = def_mgmt_if_conf()
    
    mgmt.set_mgmt_if(zdcli, mgmt_if_conf)

    
    mgmt_if_cli_get = mgmt.show_mgmt_if_info(zdcli)
    '''
        {'Management Interface': {'IP Address': '192.168.1.2',
                          'Netmask': '255.255.255.0',
                          'Status': 'Disabled',
                          'VLAN': ''}}
    '''
    cli_get = mgmt_if_cli_get['Management Interface']
    
    mgmt_if_gui_get = mgmt_if.get_mgmt_inf(zd)
    '''
    {'IP Address': u'192.168.1.2',
     'Netmask': u'255.255.255.0',
     'Status': 'Disabled',
     'VLAN': u''}
    '''
    logging.info("Verify CLI Set and CLI Get")
    
    verify_cli_set_get(mgmt_if_conf,cli_get)
    
    logging.info("Verify CLI Set and GUI Get")
    verify_cli_set_get(mgmt_if_conf,mgmt_if_gui_get)
    
    return ("PASS")

def verify_cli_set_get(cli_set,get):
    temp = {}
    map = key_map()
    for key,value in map.items():
        if key in cli_set.keys():
            temp[value] = cli_set[key]
    
    for key in temp:
        if temp[key] != get[key]:
            return("FAIL, CLI Set[%s]:[%s] is different Get[%s]" %(key,temp[key],get[key]))
        


def key_map():
    map = {'ip_addr':'IP Address',
           'net_mask':'Netmask',
           'vlan_id':'VLAN'
           } 
    return map
    
def do_clean_up(tcfg):
    clean_up_rat_env()
    del(tcfg['zdcli'])

def def_mgmt_if_conf():
    conf = {}
    conf['ip_addr'] = '192.168.1.2'
    conf['net_mask'] = '255.255.255.0'
    conf['vlan_id'] = random.randint(2,4094)
    
    return conf

def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res

