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

class CB_ZD_SR_Create_Multi_L2ACL(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        acl_cfg = self.acl_list.pop()
        acl_name = acl_cfg['acl_name']
        self.active_zd.create_acl_rule([acl_name], acl_cfg['mac_list'], acl_cfg['acl_policy'])
        logging.info("ACL [%s] create successfully" % acl_cfg['acl_name'])
        
        for acl_cfg in self.acl_list:
            #just clone rules, don't create new rules
            acl_cfg['rules'] = None
            self.active_zd.clone_acl_rule(acl_name, acl_cfg)
            logging.info("ACL [%s] clone successfully" % acl_cfg['acl_name'])
        
        self.passmsg = "ACLs [%s]create successfully" % self.acl_list
        
        passmsg.append(self.passmsg)
        self._update_carrier_bag()        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']         
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_l2_acl_list'] = self.acl_list
    
    def _init_test_params(self, conf):
        self.conf = dict(num_of_acl_entries = 32,
                         num_of_mac = 128,
                         acl_policy = True)
        self.conf.update(conf)
        acl_list = []
        acl_cnt = conf['num_of_acl_entries']
        mac_cnt = conf['num_of_mac']
        mac_list = self._generate_mac_addr(mac_cnt)
        for i in range(1, acl_cnt+1):        
            acl_cfg = dict(acl_name = 'Test_ACLs_%d' % i, 
                           acl_policy = self.conf['acl_policy'], 
                           mac_list = mac_list)
            acl_list.append(acl_cfg)
        
        self.acl_list = acl_list            
        self.errmsg = ''
        self.passmsg = ''

    def _generate_mac_addr(self, num=128):
        mac_list = []
        for i in range(num):            
            mac = [0, 0, 0, 0, 0, i+1]
            mac = ':'.join(map(lambda x: "%02x" % x, mac))
    #            if not mac_list.__contains__(mac):
            mac_list.append(mac)
                
        return mac_list

      
