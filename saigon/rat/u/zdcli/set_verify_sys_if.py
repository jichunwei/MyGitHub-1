'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
             
            }
Examples: 
tea.py u.zdcli.set_verify_sys_if
'''

import logging
import random

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
    create_zd_by_ip_addr
)
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import sys_if_info as sys_if 
from RuckusAutoTest.components.lib.zd import system_zd as sys_zd

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
    
    conf = def_sys_conf()
    
    sys_if_info_bak = sys_if.get_sys_if_info(zdcli)
    '''{'Device IP Address': {'Gateway Address': '192.168.0.253',
                       'IP Address': '192.168.0.2',
                       'Mode': 'Manual',
                       'Netmask': '255.255.255.0',
                       'Primary DNS': '1.1.1.1',
                       'Secondary DNS': '2.2.2.2'},
         'Management VLAN': {'Status': 'Disabled', 'VLAN ID': ''}}
    '''
    logging.info("Set System Interface")
    sys_if.set_sys_if(zdcli, conf)
    
    logging.info("Get System Interface via GUI")
    cli_get = sys_if.get_sys_if_info(zdcli)
    
    logging.info("Verify System Interface between CLI Set and CLI Get")
    verify_cli_set_get(conf,cli_get)
    
    gui_get = sys_zd.get_device_ip_settings(zd)
    '''
    {'gateway': u'192.168.0.253',
     'ip_addr': u'192.168.0.2',
     'ip_alloc': 'manual',
     'netmask': u'255.255.255.0',
     'pri_dns': u'',
     'sec_dns': u'',
     'vlan': u''}
    '''
    verify_cli_set_gui_get(conf,gui_get)
    
    return ("PASS")

def verify_cli_set_get(cli_set,cli_get):
    '''
    cli_set:
        {ip_mode:static, ip_addr:'',...}
    cli_get:
        {'Device IP Address': {'Gateway Address': '192.168.0.253',
                       'IP Address': '192.168.0.2',
                       'Mode': 'Manual',
                       'Netmask': '255.255.255.0',
                       'Primary DNS': '1.1.1.1',
                       'Secondary DNS': '2.2.2.2'},
         'Management VLAN': {'Status': 'Disabled', 'VLAN ID': ''}}
    '''
    cli_get_info = {}
    cli_get_info.update(cli_get['Device IP Address'])
    cli_get_info.update(cli_get['Management VLAN'])
    
    if cli_get_info['Mode'] == 'Manual':
        cli_get_info['Mode'] = 'static'
        if cli_get_info['IP Address'] != cli_set['ip_addr']:
            return('[ZDCLI:] Get IP Address [%s],expect Set[%s]' %(cli_get_info['IP Address'],cli_set['ip_addr']))
        
        if cli_get_info['Netmask'] != cli_set['net_mask']:
            return('[ZDCLI:] Get Netmask [%s],expect Set[%s]' %(cli_get_info['Netmask'],cli_set['net_mask']))
        
        if cli_get_info['Gateway Address'] != cli_set['gateway']:
            return('[ZDCLI:] Get Gateway Address [%s],expect Set[%s]' %(cli_get_info['Gateway Address'],cli_set['gateway']))
        
        if cli_get_info['Primary DNS'] != cli_set['pri_dns']:
            return('[ZDCLI:] Get Primary DNS [%s],expect Set[%s]' %(cli_get_info['Primary DNS'],cli_set['pri_dns']))
        
        if cli_get_info['Secondary DNS'] != cli_set['sec_dns']:
            return('[ZDCLI:] Get Secondary DNS [%s],expect Set[%s]' %(cli_get_info['Secondary DNS'],cli_set['sec_dns']))
        
    if cli_get_info['Mode'].lower() != cli_set['mode'].lower():
        return('[ZDCLI:] Get System Interface IP Mode [%s], expect Set[%s]' %(cli_get_info['Mode'],cli_set['mode']))


def verify_cli_set_gui_get(cli_set,gui_get):
    '''
    gui_get:
    {'gateway': u'192.168.0.253',
     'ip_addr': u'192.168.0.2',
     'ip_alloc': 'manual',
     'netmask': u'255.255.255.0',
     'pri_dns': u'',
     'sec_dns': u'',
     'vlan': u''}
    '''
    if gui_get['ip_alloc'] == 'manual':
        gui_get['ip_alloc'] = 'static'
        if gui_get['ip_addr'] != cli_set['ip_addr']:
            return("[ZDGUI:] Get System Interface IP Address [%s], expect Set[%s]" %(gui_get['ip_addr'],cli_set['ip_addr']))
    
        if gui_get['netmask'] != cli_set['net_mask']:
            return("[ZDGUI:] Get System Interface IP netmask [%s], expect Set[%s]" %(gui_get['netmask'],cli_set['net_mask']))
    
        if gui_get['gateway'] != cli_set['gateway']:
            return("[ZDGUI:] Get System Interface IP gateway [%s], expect Set[%s]" %(gui_get['gateway'],cli_set['gateway']))
    
        if gui_get['pri_dns'] != cli_set['pri_dns']:
            return("[ZDGUI:] Get System Interface IP pri_dns [%s], expect Set[%s]" %(gui_get['pri_dns'],cli_set['pri_dns']))
        
        if gui_get['sec_dns'] != cli_set['sec_dns']:
            return("[ZDGUI:] Get System Interface IP sec_dns [%s], expect Set[%s]" %(gui_get['sec_dns'],cli_set['sec_dns']))
    
    if gui_get['ip_alloc'].lower() != cli_set['mode'].lower():
        return("[ZDGUI:] Get System Interface IP Mode [%s], expect Set[%s]" %(gui_get['ip_alloc'],cli_set['mode']))
    
def do_clean_up(tcfg):
    clean_up_rat_env()
    del(tcfg['zdcli'])

def def_sys_conf():
    conf = {}
    conf['mode'] = 'static'
    conf['ip_addr'] = '192.168.0.2'
    conf['net_mask'] = '255.255.255.0'
    conf['gateway'] = '192.168.0.252'
    conf['pri_dns'] = '192.168.0.253'
    conf['sec_dns'] = '192.168.0.254'
    
    return conf

def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res

