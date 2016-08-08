'''
Created on 2012-7-4
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.components import Helpers


class Branch(object):
    """
    Support most of branches, 
        like before Saigon(9.0), Saigon(9.0), Toranto(9.1), Mainline(0.0)
    """
    def __init__(self, zd, zdcli):
        self.zd = zd
        self.zdcli = zdcli
        
    def remove_all_cfg(self, ap_mac_list=[]):
        pass
    
class Saigon(Branch):
    def __init__(self, zd, zdcli):
        super(Saigon, self).__init__(zd, zdcli)
    
    def remove_all_cfg(self, ap_mac_list=[]):
        self.zd.set_system_name("Ruckus")
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
        self.zd.set_guestpass_policy("Local Database")
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
        self.zd._set_zero_it_cfg("Local Database")
        self.zd._remove_all_generated_certs()
        self.zd._remove_all_generated_psks()

        self.zd.remove_all_active_clients()

        # @author: Candy Li 2014-4-23, to fix bug ZF-8140        
        Helpers.zd.wgs.remove_wlan_groups(self.zd, ap_mac_list)
        self.zd.remove_all_wlan()
        
        self.zd.remove_all_acl_rules()
        self.zd.remove_all_guestpasses()
        Helpers.zd.ga.remove_all_restricted_subnet_entries(self.zd)
        
        Helpers.zdcli.roles.delete_all_roles(self.zdcli)
        Helpers.zdcli.user.delete_all_users(self.zdcli)
        
        Helpers.zd.wispr.remove_all_profiles(self.zd)
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        Helpers.zd.ga.delete_default_guestaccess_policy(self.zd)
        self.zd.remove_all_auth_servers()

class Older(Branch):
    """
    Before Saigon
    """
    def __init__(self, zd, zdcli):
       super(Older, self).__init__(zd, zdcli)
    
    def remove_all_cfg(self, ap_mac_list=[]):        
        self.zd.remove_all_cfg(ap_mac_list)

class Toranto(Branch):
    def __init__(self, zd, zdcli):
       super(Toranto, self).__init__(zd, zdcli)
    
    def remove_all_cfg(self, ap_mac_list=[]):        
        Helpers.zdcli.system.default_system_name(self.zdcli)
        Helpers.zdcli.guest_access.delete_all_guest_access_profiles(self.zdcli)
        
        logging.info("Choose 'Local Database' for zero-it")
        Helpers.zdcli.dpsk.default_zero_it_auth_svr(self.zdcli)
        
        logging.info("Remove all dynamic-certs out of the Generate Dynamic-Certs table")
        self.zd._remove_all_generated_certs()

        logging.info("Remove all dynamic-PSKs out of the Generate Dynamic-PSKs table")
        self.zd._remove_all_generated_psks()

        logging.info("Remove all active clients")
        self.zd.remove_all_active_clients()

        logging.info("Remove all guest pass entries from the Generated Guest Passes table")
        self.zd.remove_all_guestpasses()
        
#        logging.info("Remove all guest ACL rules except the default rule")
#        Helpers.zdcli.guest_access.delete_all_guest_restrict_access(self.zdcli)

        logging.info("Remove all users from the Users table")
        Helpers.zdcli.user.delete_all_users(self.zdcli)

        logging.info("Remove all roles from the Roles table")
        Helpers.zdcli.roles.delete_all_roles(self.zdcli)
        
        logging.info("Default WLAN Groups for All APs")
        Helpers.zdcli.aps.default_wlan_groups_by_mac_addr(self.zdcli, ap_mac_list)
        logging.info("Default AP Group for All APs")
        Helpers.zdcli.aps.default_ap_group_by_mac_addr(self.zdcli, ap_mac_list)
        logging.info("Remove all wlan groups from the WLAN Groups table")        
        Helpers.zdcli.wgs.remove_all_wlan_groups(self.zdcli)
        
        logging.info("Remove all wlan from the WLANs table")
        Helpers.zdcli.wlan.remove_all_wlans(self.zdcli)

        logging.info("Remove all ACL rules from the Access Controls table")
        Helpers.zdcli.l2acl.delete_all_l2acls(self.zdcli)
        Helpers.zdcli.l3acl.delete_all_l3acls(self.zdcli)        

        logging.info("Remove all profiles from the Hotspot Services table")
        Helpers.zdcli.hotspot.delete_all_hotspots(self.zdcli)

        logging.info("Remove all AAA servers")
        Helpers.zdcli.configure_aaa_servers.delete_all_servers(self.zdcli)
                
    
class Mainline(Branch):
    def __init__(self, zd, zdcli):
       super(Mainline, self).__init__(zd, zdcli)
    
    def remove_all_cfg(self, ap_mac_list=[]):        
        Helpers.zdcli.system.default_system_name(self.zdcli)
        Helpers.zdcli.guest_access.default_guest_access_setting(self.zdcli)
        
        logging.info("Choose 'Local Database' for zero-it")
        Helpers.zdcli.dpsk.default_zero_it_auth_svr(self.zdcli)
        
        logging.info("Remove all dynamic-certs out of the Generate Dynamic-Certs table")
        self.zd._remove_all_generated_certs()

        logging.info("Remove all dynamic-PSKs out of the Generate Dynamic-PSKs table")
        self.zd._remove_all_generated_psks()

        logging.info("Remove all active clients")
        self.zd.remove_all_active_clients()

        logging.info("Remove all guest pass entries from the Generated Guest Passes table")
        self.zd.remove_all_guestpasses()
        
        logging.info("Remove all guest ACL rules except the default rule")
        Helpers.zdcli.guest_access.delete_all_guest_restrict_access(self.zdcli)

        logging.info("Remove all users from the Users table")
        Helpers.zdcli.user.delete_all_users(self.zdcli)

        logging.info("Remove all roles from the Roles table")
        Helpers.zdcli.roles.delete_all_roles(self.zdcli)
        
        logging.info("Default WLAN Groups for All APs")
        Helpers.zdcli.aps.default_wlan_groups_by_mac_addr(self.zdcli, ap_mac_list)
        logging.info("Default AP Group for All APs")
        Helpers.zdcli.aps.default_ap_group_by_mac_addr(self.zdcli, ap_mac_list)
        logging.info("Remove all wlan groups from the WLAN Groups table")        
        Helpers.zdcli.wgs.remove_all_wlan_groups(self.zdcli)
        
        logging.info("Remove all wlan from the WLANs table")
        Helpers.zdcli.wlan.remove_all_wlans(self.zdcli)

        logging.info("Remove all ACL rules from the Access Controls table")
        Helpers.zdcli.l2acl.delete_all_l2acls(self.zdcli)
        Helpers.zdcli.l3acl.delete_all_l3acls(self.zdcli)        

        logging.info("Remove all profiles from the Hotspot Services table")
        Helpers.zdcli.hotspot.delete_all_hotspots(self.zdcli)

        logging.info("Remove all AAA servers")
        Helpers.zdcli.configure_aaa_servers.delete_all_servers(self.zdcli)


def get_branch_obj(zd, zdcli):
    ver = zd.get_version()
    if ver[:-4] in ['9.0','9.5','9.6', '9.7', '9.8','0.0','9.9', '9.10','9.12']:#@yuyanan 2014-7-17 bug:ZF-9236
        obj = Saigon(zd, zdcli)
    elif ver[:-4] in ['8.9', '8.7', '8.6']:
        obj = Older(zd, zdcli)
    else:
        obj = Toranto(zd, zdcli)
    
    return obj

def remove_all_cfg(zd, zdcli):
    ap_mac_list = Helpers.zd.aps.get_all_ap_mac_list(zd)
    obj = get_branch_obj(zd, zdcli)
    obj.remove_all_cfg(ap_mac_list)
