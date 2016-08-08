'''
Author: Louis
Email: louis.lou@ruckuswireless.com
Parameters:
conf = {
             
            }
Examples: 
tea.py u.zdcli.set_verify_l3acl 
'''

import logging
import random

from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,
    clean_up_rat_env,
    create_zd_by_ip_addr
)
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import l3_acl 
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
    zd_ip_addr = tcfg['ip_addr']
    
    logging.info("[ZD - %s:] Remove all L3ACLs" % zd_ip_addr)
    zd.remove_all_acl_rules()
    
    logging.info("[ZDCLI - %s:] Create 2 ACLs" % zd_ip_addr)
    
    l3acl_conf_list = def_l3acl_conf_list()
    
    for l3acl_conf in l3acl_conf_list:
        l3_acl._create_l3acl(zdcli, l3acl_conf)
        cli_get = l3_acl.show_l3acl_name(zdcli, l3acl_conf['acl_name'])
        logging.info('cli set is:[%s]\n cli_get is: [%s]' %(l3acl_conf,cli_get))
        logging.info('Verify L3 ACL set and get are the same')
        errmsg = l3_acl._verify_l3acl_cliset_cliget(l3acl_conf, cli_get)
#        if errmsg:
#            return(errmsg)
    
    for l3acl_conf in l3acl_conf_list:
        gui_get = acl.get_l3_acl_policy_cfg(zd,l3acl_conf['acl_name'])
        logging.info('cli set is:[%s]\n gui_get is: [%s]' %(l3acl_conf,gui_get))
        errmsg = l3_acl._verify_l3acl_cliset_guiget(l3acl_conf, gui_get)
#        if errmsg:
#            return(errmsg)
        
    edit_l3acl_conf = random.choice(l3acl_conf_list)
    edit_l3acl_conf.update(dict(new_name = 'new-name' + utils.make_random_string(random.randint(2,24),type = 'alnum')))
    l3_acl._rename_l3acl(zdcli, edit_l3acl_conf)  
    
    cli_get = l3_acl.show_l3acl_name(zdcli, edit_l3acl_conf['new_name'])

    if cli_get['Name'] != edit_l3acl_conf['new_name']:
        return("FAIL, L2 ACL name not renamed")
    if errmsg:
        return(errmsg)
    
    return ("PASS")


def do_clean_up(tcfg):
    clean_up_rat_env()
    del(tcfg['zdcli'])

def def_l3acl_conf_list():
    l3acl_conf_list = []
    l3acl_conf_list.append(dict(
                                acl_name = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                description = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                policy = 'allow',
                                rule_conf_list = [ dict(
                                                        rule_order = 3,
                                                        rule_description =utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                                        rule_type = 'allow',
                                                        rule_destination_addr =random.choice(['1.1.1.1/24','Any']),
                                                        rule_destination_port =random.choice([random.randint(1,65534),'Any']),
                                                        rule_protocol = random.choice([random.randint(0,254),'Any'])
                                                        ),
                                                    dict(
                                                        rule_order = 4,
                                                        rule_description =utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                                        rule_type = 'deny',
                                                        rule_destination_addr =random.choice(['10.1.0.1/24','Any']),
                                                        rule_destination_port =random.choice([random.randint(1,65534),'Any']),
                                                        rule_protocol = random.choice([random.randint(0,254),'Any'])
                                                        )
                                                  ]
                                ))
    
    l3acl_conf_list.append(dict(
                                acl_name = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                description = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                policy = 'deny',
                                rule_conf_list = [ dict(
                                                        rule_order = 3,
                                                        rule_description =utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                                        rule_type = 'deny',
                                                        rule_destination_addr =random.choice(['10.0.1.1/24','Any']),
                                                        rule_destination_port =random.choice([random.randint(1,65534),'Any']),
                                                        rule_protocol = random.choice([random.randint(0,254),'Any'])
                                                        ),
                                                    dict(
                                                        rule_order = 4,
                                                        rule_description =utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                                        rule_type = 'allow',
                                                        rule_destination_addr =random.choice(['10.1.1.1/24','Any']),
                                                        rule_destination_port =random.choice([random.randint(1,65534),'Any']),
                                                        rule_protocol = random.choice([random.randint(0,254),'Any'])
                                                         )
                                                  ]
                                ))
    
    return l3acl_conf_list
    

def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res

