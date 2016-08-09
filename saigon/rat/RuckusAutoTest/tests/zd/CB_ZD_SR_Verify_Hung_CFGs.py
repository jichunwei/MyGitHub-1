'''
Description:
Created on 2010-7-16
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class CB_ZD_SR_Verify_Hung_CFGs(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
        
        
    def test(self):
        err_msg_list = []
        if not self._verify_maxinum_users():
            err_msg_list.append('Users have not synchronized successfully')
        
        if not self._verify_maxinum_roles():
            err_msg_list.append('Roles have not synchronized successfully')
        
        if not self._verify_maxinum_wlan_wgs():
            err_msg_list.append('WLAN or wlangroups have not synchronized successfully')
        
        if not self._verify_maxinum_l2_acl():
            err_msg_list.append('L2 ACL have not synchronized successfully')
        
        if not self._verify_maxinum_l3_acl():
            err_msg_list.append('L3 ACL have not synchronized successfully')
        
        if not self._verify_maxinum_mgmtipacl():
            err_msg_list.append('MGMT IP ACL have not synchronized successfully')
        
        if not self._verify_maxinum_guest_pass():
            err_msg_list.append('Guest Pass have not synchronized successfully')
        
        if not self._verify_full_aaa_servers():
            err_msg_list.append('AAA servers have not synchronized successfully')
        
        if not self._verify_maxinum_dpsk():
            err_msg_list.append('DPSK have not synchronized successfully')
        
        if not self._verify_maxinum_hotspot():
            err_msg_list.append('Hotspot entities have not synchronized successfully')
        
        if not self._verify_full_maps():
            err_msg_list.append('Maps have not synchronized successfully')
        
        if err_msg_list:
            logging.warning(err_msg_list)
            return self.returnResult('FAIL', err_msg_list)
            
        self._update_carrier_bag()
        return self.returnResult("PASS", "All of CFGs have been synchronized successfully")
    
    def cleanup(self):
        pass
#        self._clean_env()
        
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(
#                         num_of_mgmtipacl = 16,
#                         num_of_wlans = 32, 
#                         num_of_wgs = 31,
#                         num_of_roles = 32, 
#                         num_of_users = 6000,
#                         num_of_acl_entries = 32,
#                         num_of_mac = 128,
#                         acl_policy = True,
#                         num_of_l3acls = 32,
#                         num_of_l3rules = 29,
#                         num_of_maps = 40,
#                         map_path = 'D:\\p4\\tools\\rat-branches\\saigon\\rat\\RuckusAutoTest\\scripts\\zd\\maps\\map_test.png',
#                         guestpass_count = 10000,
#                         max_gp_allowable = 10000,
#                         dpsk_count = 6000,
#                         num_of_hotspots = 32,
#                         num_of_rules = 16,
#                         num_of_server = 32,
                         ) 
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_maxinum_mgmtipacl(self):
        from RuckusAutoTest.components.lib.zd import mgmt_ip_acl as acl
        a_list = acl.get_all_mgmtipacl(self.active_zd)
        s_list = acl.get_all_mgmtipacl(self.standby_zd)
        if a_list == s_list and len(a_list) > 0:            
            return True
        else:
            return False
        
    def _verify_maxinum_wlan_wgs(self):
        a_wgs = lib.zd.wgs.get_total_wlan_groups(self.active_zd)
        s_wgs = lib.zd.wgs.get_total_wlan_groups(self.standby_zd)
        if a_wgs == s_wgs and a_wgs > 0:
            return True
        else:
            return False
            
    def _verify_maxinum_roles(self):
        a_role_num = self.active_zd.get_role_total_numbers()
        s_role_num = self.standby_zd.get_role_total_numbers()
        if a_role_num == s_role_num and a_role_num > 1 :            
            return True
        else:
            return False
    
    def _verify_maxinum_users(self): 
        from RuckusAutoTest.components.lib.zd import user
        a_users = int(user.get_all_users_total_number(self.active_zd, is_nav = True))
        s_users = int(user.get_all_users_total_number(self.standby_zd, is_nav = True))
        if a_users == s_users and a_users > 0 :            
            return True
        else:
            return False
    
    def _verify_maxinum_l2_acl(self):
        a_l2_acls = self.active_zd.get_all_acl_names()
        s_l2_acls = self.standby_zd.get_all_acl_names()
        if a_l2_acls == s_l2_acls and len(a_l2_acls) > 0:
            return True
        else:
            return False
        
    def _verify_maxinum_l3_acl(self):
        a_l3_acls = lib.zd.ac.get_all_l3_acl_policies(self.active_zd)
        s_l3_acls = lib.zd.ac.get_all_l3_acl_policies(self.standby_zd)
        if a_l3_acls == s_l3_acls and len(a_l3_acls) > 0:
            return True
        else:
            return False
    
    def _verify_full_maps(self): 
        a_maps = self.active_zd.get_maps_info()
        s_maps = self.standby_zd.get_maps_info()
        if a_maps == s_maps and len(a_maps) > 0:
            return True
        else:
            return False
    
    def _verify_full_aaa_servers(self): 
        a_total_servers = self.active_zd.get_total_auth_server()
        s_total_servers = self.standby_zd.get_total_auth_server()
        if a_total_servers == s_total_servers and int(a_total_servers) > 0 :            
            return True
        else:
            return False
        
    def _verify_maxinum_guest_pass(self):
        a_ga = int(lib.zd.ga.get_all_guestpasses_total_numbers(self.active_zd))
        s_ga = int(lib.zd.ga.get_all_guestpasses_total_numbers(self.standby_zd))
        if a_ga == s_ga and a_ga > 0:
            return True
        else:
            return False
        
    def _verify_maxinum_dpsk(self):
        a_dpsk = int(self.active_zd.get_all_generated_psks_total_numbers(timeout = 50))
        s_dpsk = int(self.standby_zd.get_all_generated_psks_total_numbers(timeout = 50))
        if a_dpsk == s_dpsk and a_dpsk > 0:
            return True
        else:
            return False
        
    def _verify_maxinum_hotspot(self):
        a_hotspot = lib.zd.wispr.get_total_profiles(self.active_zd)
        s_hotspot = lib.zd.wispr.get_total_profiles(self.standby_zd)
        if a_hotspot == s_hotspot and a_hotspot > 0:            
            return True
        else:
            return False