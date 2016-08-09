'''
Remove all configuration from ZDCLI.
Created on 2012-7-4
@author: cwang@ruckuswireless.com
'''

import logging
import time
import traceback

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr,
                                       create_zd_by_ip_addr, 
                                       clean_up_rat_env)

from RuckusAutoTest.components import Helpers

default_cfg = dict(ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   )

def config():
    cnt = 3
    while cnt:
        try:
            # Initialize the DUT component
            zd = create_zd_by_ip_addr(**default_cfg)
            break;
        except Exception, e:
            cnt = cnt-1                    
            logging.debug(traceback.format_exc())
    
    zdcli = create_zd_cli_by_ip_addr(**default_cfg)
    return (zd, zdcli)

def test(zd, zdcli):    
    ap_mac_list = Helpers.zd.aps.get_all_ap_mac_list(zd)
    Helpers.zdcli.system.default_system_name(zdcli)
    Helpers.zdcli.guest_access.default_guest_access_setting(zdcli)
    
    logging.info("Choose 'Local Database' for zero-it")
    Helpers.zdcli.dpsk.default_zero_it_auth_svr(zdcli)
    
    logging.info("Remove all dynamic-certs out of the Generate Dynamic-Certs table")
    zd._remove_all_generated_certs()

    logging.info("Remove all dynamic-PSKs out of the Generate Dynamic-PSKs table")
    zd._remove_all_generated_psks()

    logging.info("Remove all active clients")
    zd.remove_all_active_clients()

    logging.info("Remove all guest pass entries from the Generated Guest Passes table")
    zd.remove_all_guestpasses()
    
    logging.info("Remove all guest ACL rules except the default rule")
    Helpers.zdcli.guest_access.delete_all_guest_restrict_access(zdcli)

    logging.info("Remove all users from the Users table")
    Helpers.zdcli.user.delete_all_users(zdcli)

    logging.info("Remove all roles from the Roles table")
    Helpers.zdcli.roles.delete_all_roles(zdcli)
    
    logging.info("Default WLAN Groups for All APs")
    Helpers.zdcli.aps.default_wlan_groups_by_mac_addr(zdcli, ap_mac_list)
    logging.info("Default AP Group for All APs")
    Helpers.zdcli.aps.default_ap_group_by_mac_addr(zdcli, ap_mac_list)
    logging.info("Remove all wlan groups from the WLAN Groups table")        
    Helpers.zdcli.wgs.remove_all_wlan_groups(zdcli)
    
    logging.info("Remove all wlan from the WLANs table")
    Helpers.zdcli.wlan.remove_all_wlans(zdcli)

    logging.info("Remove all ACL rules from the Access Controls table")
    Helpers.zdcli.l2acl.delete_all_l2acls(zdcli)
    Helpers.zdcli.l3acl.delete_all_l3acls(zdcli)        

    logging.info("Remove all profiles from the Hotspot Services table")
    Helpers.zdcli.hotspot.delete_all_hotspots(zdcli)

    logging.info("Remove all AAA servers")
    Helpers.zdcli.configure_aaa_servers.delete_all_servers(zdcli)
    
    return ("PASS", "Remove all configuration form ZD successfully")

def cleanup():
    pass


def main(**kwargs):    
    zd, zdcli = config()
    s_time = time.time()
    res = None  
    try:
        res = test(zd, zdcli)
    finally:
        cleanup()
        logging.info('Elapse time%d' % (time.time() - s_time))
        
    return res
