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
        
        
Create on 2011-8-18
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_WebAuth_Check_VLAN_Subnet(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'vlan_id':'',}
    
    def _init_params(self, conf):
        self.conf = dict(ip = None,    
                         sta_tag = 'sta_1',
                         )
        self.conf.update(conf)        
        tmp_list = self.conf['ip'].split("/")
        self.test_ip_addr = tmp_list[0]
        if len(tmp_list) == 2:
            self.expected_subnet_mask = tmp_list[1]
        else:
            self.expected_subnet_mask = ""  
        
        self.errmsg = ''
        self.msg = ''         
        
            
    def _retrieve_carribag(self):        
        self.wifi_ip_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_ip_addr']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):        
        sta_wifi_subnet = utils.get_network_address(self.wifi_ip_addr, self.expected_subnet_mask)
        expected_subnet = utils.get_network_address(self.test_ip_addr, self.expected_subnet_mask)
        if sta_wifi_subnet != expected_subnet:
            self.errmsg = "The wireless IP address '%s' of target station %s has different subnet with '%s'" % \
                          (self.sta_wifi_ip_addr, self.wifi_ip_addr, self.test_ip_addr)  
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', 'Expected subnet %s is matched' % self.conf['ip'])           
        
    def cleanup(self):
        self._update_carribag()