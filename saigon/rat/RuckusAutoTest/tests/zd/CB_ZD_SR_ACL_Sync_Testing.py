'''
Description:
Created on 2010-7-5
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_SR_ACL_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_l2_acl_sync()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
        self._test_l3_acl_sync()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
        self.passmsg = 'Create/Edit/Delete L2 or L3 ACL can be synchronized to Standby ZD.'
        
        logging.info(self.passmsg)
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
   
        
    def _test_l2_acl_sync(self):
        l2_acl_cfg = dict(acl_name = 'rat-l2-acl-test',
                          description = 'rat-l2-acl-test',
                          allowed_access = True,
                          mac_list = ['00:01:03:99:89:ff'],
                          )
                
        lib.zd.ac.create_l2_acl_policy(self.active_zd, l2_acl_cfg)        
        res = self._verify_l2_acl(l2_acl_cfg['name'])
        if not res:
            return res        
        self.passmsg = 'Created L2 ACL has synchronized to standby ZD'
        logging.info(self.passmsg)
        
        old_acl_name = l2_acl_cfg['acl_name']
        l2_acl_cfg['acl_name'] = 'rat-l2-acl-test-edit'
        lib.zd.ac.edit_l2_acl_policy(self.active_zd, old_acl_name, l2_acl_cfg)        
        res = self._verify_l2_acl(l2_acl_cfg['acl_name'])
        if not res:
            return res
        self.passmsg = 'Modified L2 ACL has synchronized to standby ZD'
        logging.info(self.passmsg)
        
        lib.zd.ac.delete_all_l2_acl_policies(self.active_zd)
        a_acl_cfg = self.active_zd.get_all_acl_names()
        s_acl_cfg = self.standby_zd.get_all_acl_names()
        if not a_acl_cfg:            
            self.errmsg = "Delete L2 ACL haven't take effect."
            logging.warning(self.errmsg)
            return False
        
        if not s_acl_cfg:
            self.errmsg = "L2 ACL has't synchronized to standby ZD"
            logging.warning(self.errmsg)
            return False            
        self.passmsg = 'Deleted L2 ACL has synchronized to standby ZD.'
        logging.info(self.passmsg)        
   
        
    def _verify_l2_acl(self, init_acl_name):
        a_acl_cfg = self.active_zd.get_acl_info(init_acl_name)
        
        if not a_acl_cfg:
            self.errmsg = 'acl [%s]has not created successfully' % init_acl_name
            logging.warning(self.errmsg)
        
        s_acl_cfg = self.standby_zd.get_acl_info(init_acl_name)
        
        res = self._verify_dict(a_acl_cfg, s_acl_cfg)
        
        return res
   
   
    def _test_l3_acl_sync(self):
        rule = dict(order = '3',
                    description = 'rat-acl-sync-3',
                    action = '',
                    dst_addr = '192.168.1.2/24',
                    application = '',
                    protocol = '',
                    dst_port = '') 
               
        r_cfg = dict(name = 'rat-l3-acl-test',
                     description = 'rat-l3-acl-test',
                     default_mode = 'allow-all',
                     rules = [rule])
        
        lib.zd.ac.create_l3_acl_policy(self.active_zd, r_cfg)
        a_r_cfg = lib.zd.ac.get_l3_acl_policy_cfg(self.active_zd, r_cfg['name'])
        s_r_cfg = lib.zd.ac.get_l3_acl_policy_cfg(self.standby_zd, r_cfg['name'])
        if not self._verify_dict(a_r_cfg, s_r_cfg):
            return False
        else:
            self.passmsg = 'created L3 ACL has synchronized to standby ZD.'
            logging.info(self.passmsg)
            
        old_acl_name = r_cfg['name']
        r_cfg['name'] = 'rat-l3-acl-test-edit'
        r_cfg['description'] = 'rat-l3-acl-test-edit'        
        r_cfg['default_mode'] = 'deny-all'
        
        rule_2 = dict(order = '4',
            description = 'rat-acl-sync-4',
            action = '',
            dst_addr = '192.168.2.2/24',
            application = '',
            protocol = '',
            dst_port = '1000')
        r_cfg['rules'] = [rule, rule_2]
        
        lib.zd.ac.edit_l3_acl_policy(self.active_zd, old_acl_name, r_cfg)
        a_r_cfg = lib.zd.ac.get_l3_acl_policy_cfg(self.active_zd, r_cfg['name'])
        s_r_cfg = lib.zd.ac.get_l3_acl_policy_cfg(self.standby_zd, r_cfg['name'])
        if not self._verify_dict(a_r_cfg, s_r_cfg):
            return False
        else:
            self.passmsg = 'modified L3 ACL has synchronized to standby ZD.'
            logging.info(self.passmsg)
            
        lib.zd.ac.delete_all_l3_acl_policies(self.active_zd)
        a_r_cfg = lib.zd.ac.get_l3_acl_policy_cfg(self.active_zd, r_cfg['name'])
        s_r_cfg = lib.zd.ac.get_l3_acl_policy_cfg(self.standby_zd, r_cfg['name'])
        if not a_r_cfg:
            self.errmsg = 'L3 ACL [%s] has not deleted' % r_cfg['name']
            logging.warning(self.errmsg)
            return False
        
        if not s_r_cfg:
            self.errmsg = 'Deleted L3 ACL [%s] has not synchronized to standby zd' % r_cfg['name']
            logging.warning(self.errmsg)
            return False
        self.passmsg = 'Deleted L3 ACL [%s] has taken effect in standby zd' % r_cfg['name']
        logging.info(self.passmsg)
        return True
                
                                                 
    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True        
            
