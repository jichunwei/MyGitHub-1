'''
Description: Find SIMAP agent by vm_ip_addr
Created on 2010-7-28
@author: cwang@ruckuswireless.com 
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.simap import vm_controller as CTL 

class CB_Scaling_Find_SimAP_Server(Test):
    '''
    Find SIMAP agent by vm_ip_addr
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []        
        self.sim_agent = CTL.SimAPsAgent()
        self.sim_agent.touch_tcfg(self.conf)
        self.sim_agent.connect_te()
        self._update_carrier_bag()        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_sim_agent'] = self.sim_agent
    
    def _init_test_params(self, conf):
        self.conf = dict(vm_ip_addr = '172.18.35.150')
        self.conf.update(conf)            
        self.errmsg = ''
        self.passmsg = ''
    
