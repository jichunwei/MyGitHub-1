"""

by louis.lou@ruckuswireless.com
2010-8-31
test procedure:
1.    Clear the ZDs L2 ACL via GUI.
2.    Check via CLI; verify there is no any L2 ACL.
3.    Setup 3 L2 ACLs via GUI.
4.    Check via CLI, verify there are 3 L2 ACLs and the ACLs are corrected.

"""
import logging
from RuckusAutoTest.components import (
    create_zd_cli_by_ip_addr,    
)
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
#from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.components.lib.zdcli import l2_acl_cli as cli

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB')

def do_config(**kwargs):
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    zd = ZoneDirector(default_cfg)
    return dict(zdcli = zdcli, zd = zd)

def do_test(zd, zdcli, **kwargs):
    logging.info("Verify CLI 'show l2acl all' when there are no ACLs")
    verify_no_l2acl(zd,zdcli)
    
    logging.info("Verify CLI 'show l2acl all' when there are ACLs")
    verify_all_l2acl(zd,zdcli)
    
    logging.info("Verify CLI 'show l2acl name $name' when there are ACLs")
    verify_l2acl_name(zd,zdcli)

def do_clean_up(zd,zdcli):
    try:
        del(zdcli)
        zd.s.shut_down_selenium_server()
        del(zd)
                
    except:
        pass
    
    
def verify_no_l2acl(zd,zdcli):
    logging.info('Remove all ACL rules')
    zd.remove_all_acl_rules()
    logging.info('Verfiy there is no ACL in CLI')
    
    acl_name_list = zd.get_all_acl_names()
    if acl_name_list != []:
        return ("FAIL, there are ACLs after remove all ACL rules via GUI")
    
    mac_list = []
    acl_policy = True
    
    l2acl_data = cli.show_l2acl_all(zdcli)
    if not cli.verify_l2acl_all(l2acl_data,acl_name_list,mac_list,acl_policy):
        return ("FAIL")

def verify_all_l2acl(zd,zdcli):
    acl_name_list_zd = ['l2_acl_test1','l2_acl_test2']
    mac_list_zd = ['00:01:02:03:04:01','00:01:02:03:04:02']
    acl_policy_zd = True
    
    zd.create_acl_rule(acl_name_list_zd,mac_list_zd,acl_policy_zd)
    acl_name_list = zd.get_all_acl_names()
    for acl_name in acl_name_list:
        acl_info = zd.get_acl_info(acl_name)
        mac_list = acl_info['mac_entries']
        l2acl_data = cli.show_l2acl_all(zdcli)
        if mac_list == mac_list_zd:
            if not cli.verify_l2acl_all(l2acl_data, acl_name_list, mac_list, acl_policy_zd):
                return ("FAIL")
        else:
            return('FAIL')
        
        
def verify_l2acl_name(zd,zdcli):
    acl_name_list = zd.get_all_acl_names()
    for acl_name in acl_name_list:
        acl_info = zd.get_acl_info(acl_name)
        mac_list = acl_info['mac_entries']
        policy = acl_info['policy']
        if policy == 'allow-all':
            acl_policy = True
        else:
            acl_policy = False
        l2acl_data = cli.show_l2acl_name(zdcli, acl_name)
        
        if not cli.verify_l2acl_name(l2acl_data,acl_name,mac_list,acl_policy):
            return ("FAIL")
        

def main(**kwargs):
    try:
        cfg = do_config(**kwargs)
        zdcli = cfg['zdcli']
        zd = cfg['zd']
        
        res = do_test(zd,zdcli, **kwargs)         
        return res
    finally:
        do_clean_up(zd,zdcli)
    
if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)