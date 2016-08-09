'''
Description:
Created on 2010-7-8
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl as acl

class CB_ZD_SR_Mgmt_ACL_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_mgmt_acl_sync()
        if self.errmsg:
            return('FAIL', self.errmsg)
        self.passmsg = 'Create/Modified/Delete ACL can synchronized to standby ZD correctly'
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
    
    def _test_mgmt_acl_sync(self):
        cfg_list = [{'name': 'test2', 'type':'range', 'addr': '192.168.0.4-192.168.0.254', },
                    {'name': 'test1', 'type':'single', 'addr': '192.168.0.10', },
                    {'name': 'test3', 'type':'subnet', 'addr': '192.168.0.10/24', },
                    ]
        for cfg in cfg_list:
            acl.create_mgmtipacl(self.active_zd, cfg)
            time.sleep(1)
                
        logging.info('Try to verify Management ACL')
        a_cfg_list = acl.get_all_mgmtipacl(self.active_zd)
        s_cfg_list = acl.get_all_mgmtipacl(self.standby_zd)
        size = len(a_cfg_list)
        if size < len(cfg_list):
            self.errmsg = 'Mgmt ACL list has not create correctly'
            return False
        for i in range(size):
            a_cfg = a_cfg_list[i]
            b_cfg = s_cfg_list[i]
            if not self._verify_dict(a_cfg, b_cfg):
                return False
        
        self.passmsg = 'Created Mgmt ACL list has synchronized to standby ZD successfully'
        logging.info(self.passmsg)
        edit_cfg = cfg_list[0]
        old_name = edit_cfg['name']
        edit_cfg['name'] = 'test4'
        edit_cfg['type'] = 'range'
        edit_cfg['addr'] = '192.168.1.4-192.168.1.254'
        acl.edit_mgmtipacl(self.active_zd, old_name, edit_cfg)
        
        logging.info('Try to verify Management ACL')
        a_cfg_list = acl.get_all_mgmtipacl(self.active_zd)
        s_cfg_list = acl.get_all_mgmtipacl(self.standby_zd)
        size = len(a_cfg_list)
                
        for i in range(size):
            a_cfg = a_cfg_list[i]
            b_cfg = s_cfg_list[i]
            if not self._verify_dict(a_cfg, b_cfg):
                return False
            
        self.passmsg = 'Modified Mgmt ACL list has synchronized to standby ZD successfully'
        logging.info(self.passmsg)
        
        acl.delete_all_mgmtipacl(self.active_zd)
        
        a_cfg_list = acl.get_all_mgmtipacl(self.active_zd)
        s_cfg_list = acl.get_all_mgmtipacl(self.standby_zd)
        if a_cfg_list:
            self.errmsg = 'Some of Mgmt ACL have not been deleted correctly'
            return False
        
        if s_cfg_list:
            self.errmsg = "Active ZD's Mgmt ACL has been clean, but haven't synchronized to standby ZD"
            return False
        
        self.passmsg = 'Deleted Mgmt ACL list has been synchronized to standby ZD successfully'
        logging.info(self.passmsg)
        return True 
                  

    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True 
        
    
