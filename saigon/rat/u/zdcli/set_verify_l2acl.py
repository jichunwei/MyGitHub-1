'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
             
            }
Examples: 
tea.py u.zdcli.set_verify_l2acl 
'''

import logging
import random

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
    create_zd_by_ip_addr
)
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zdcli import l2_acl_cli

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
    zd_ip_addr = tcfg['ip_addr']
    
    logging.info("[ZD - %s:] Remove all L2ACLs" % zd_ip_addr)
    zd.remove_all_acl_rules()
    
    logging.info("[ZDCLI - %s:] Create 2 ACLs" % zd_ip_addr)
    
    l2acl_conf_list = def_l2acl_conf_list()
    
    for l2acl_conf in l2acl_conf_list:
        l2_acl_cli._create_l2acl(zdcli, l2acl_conf)
        cli_get = l2_acl_cli.show_l2acl_name(zdcli, l2acl_conf['acl_name'])
        logging.info('cli set is:[%s]\n cli_get is: [%s]' %(l2acl_conf,cli_get))
        logging.info('Verify L2 ACL set and get are the same')
        errmsg = l2_acl_cli._verify_l2acl_cliset_cliget(l2acl_conf, cli_get)
        if errmsg:
            return(errmsg)
    
    for l2acl_conf in l2acl_conf_list:
        gui_get = zd.get_acl_info(l2acl_conf['acl_name'])
        logging.info('cli set is:[%s]\n gui_get is: [%s]' %(l2acl_conf,gui_get))
        errmsg = l2_acl_cli._verify_l2acl_cliset_guiget(l2acl_conf, gui_get)
        if errmsg:
            return(errmsg)
        
    edit_l2acl_conf = random.choice(l2acl_conf_list)
    mac = edit_l2acl_conf['mac_entries'][0]
    edit_l2acl_conf.update(dict(new_name = 'new-name' + utils.make_random_string(random.randint(2,24),type = 'alnum')))
    l2_acl_cli._remove_mac_addr_from_l2acl(zdcli, edit_l2acl_conf['acl_name'], mac) 
    l2_acl_cli._rename_l2acl(zdcli, edit_l2acl_conf)  
    
    cli_get = l2_acl_cli.show_l2acl_name(zdcli, edit_l2acl_conf['new_name'])
    
    
    id = cli_get['L2/MAC ACL']['ID'].keys()[0]
    
    cli_get_dict = cli_get['L2/MAC ACL']['ID'][id]
    
    if cli_get_dict['Name'] != edit_l2acl_conf['new_name']:
        return("FAIL, L2 ACL name not renamed")
    
    return ("PASS")


def do_clean_up(tcfg):
    clean_up_rat_env()
    del(tcfg['zdcli'])

def def_l2acl_conf_list():
    l2acl_conf_list = []
    l2acl_conf_list.append(dict(
                                acl_name = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                description = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                mac_entries =_generate_mac_addr(2),
                                policy = 'allow',
                                ))
    
    l2acl_conf_list.append(dict(
                                acl_name = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                description = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                mac_entries =_generate_mac_addr(2),
                                policy = 'deny',
                                ))
    
    return l2acl_conf_list
    
def _generate_mac_addr(num=128):
        mac_list = []
        for i in range(num):            
            mac = [0, 0, 0, 0, 0, i+1]
            mac = ':'.join(map(lambda x: "%02x" % x, mac))
#            if not mac_list.__contains__(mac):
            mac_list.append(mac)
                
        return mac_list

def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res

