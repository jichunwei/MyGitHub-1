'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2011-8-16
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Hotspot_Check_VLAN_Subnet(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'expected_subnet':'VLAN subnet configuration',
                              'sta_tag': 'sta_1'}
    
    def _init_params(self, conf):
        self.conf = dict(expected_subnet = None,
                         sta_tag = 'sta_1')
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']    
        l = self.conf['expected_subnet'].split("/")
        self.conf['expected_subnet'] = l[0]
        if len(l) == 2:
            self.conf['expected_mask'] = l[1]
        else:
            self.conf['expected_mask'] = ""
    
    def _retrieve_carribag(self):        
        self.wifi_ip_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_ip_addr']        
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info("Verify the subnet address of the wireless station")
        net_addr = utils.get_network_address(self.wifi_ip_addr, self.conf['expected_mask'])
        if self.conf['expected_subnet'] != net_addr:
            self.errmsg = "The leased IP address was [%s], which is not in the expected subnet [%s]" % \
                          (self.wifi_ip_addr, self.conf['expected_subnet'])  
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'Expected subnet %s is matched' % self.conf['expected_subnet'])
     
    
    def cleanup(self):
        self._update_carribag()