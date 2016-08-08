'''
Created on Nov 11, 2013
@author: cwang@ruckuswireless.com
'''
import logging
import time
from RuckusAutoTest.models import Test

class CB_ATA_Stop_Flow(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(clients=[])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.flowname = self.conf.get('flowname')        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        res = self.ata.stop_flow(flowname = self.flowname)
        logging.info(res)
        return self.returnResult('PASS', 'Flow %s started' % self.flowname)
    
    def cleanup(self):
        self._update_carribag()
        
    def get_ip_addr_by_client_name(self):
        ipaddr = ""
        return ipaddr