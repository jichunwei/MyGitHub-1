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
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl

class CB_ZD_SR_Create_Multi_mgmtipacl(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        for mgmt in self.mgmt_list:
            mgmt_ip_acl.create_mgmtipacl(self.active_zd, mgmt)
            logging.info('mgmt ip acl [%s] created successfully' % mgmt['name'])
            
        self.passmsg = "mgmt ip acl list [%s] created successfully" % self.mgmt_list        
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']          
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_mgmtipacl'] = self.mgmt_list
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        mgmt_cnt = conf['number']
        mgmt_cfg = {'name':'mgmt-ip-acl-test',
                    'type':'single',
                    'addr':'192.168.2.33',}
        mgmt_cfg.update(conf)
        mgmt_list = []
        for i in range(1, mgmt_cnt +1):
            mgmt_cfg_tmp = mgmt_cfg.copy()
            mgmt_cfg_tmp['name'] = 'mgmt-ip-acl-%d' % i
            mgmt_list.append(mgmt_cfg_tmp)
        
        self.mgmt_list = mgmt_list
        self.errmsg = ''
        self.passmsg = ''