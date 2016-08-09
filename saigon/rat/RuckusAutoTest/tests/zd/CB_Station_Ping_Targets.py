'''
Description:
    Ping target list as:
        ["172.21.0.252/32", "172.22.0.252/32", 
         "172.23.0.252/32", "172.24.0.252/32", 
         "172.25.0.252/32", "172.26.0.252/32",
         "10.0.0.0/24", "10.1.0.0/24", 
         "10.2.0.0/24", "10.3.0.0/24", 
         "10.4.0.0/24", "10.5.0.0/24", 
         "10.6.0.0/24", "10.7.0.0/24", 
         "10.8.0.0/24", "10.9.0.0/24"]

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
        
        
Create on 2011-7-26
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_Station_Ping_Targets(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'ping_timeout_ms': 15 * 1000,
                     'target_ip_list': ['192.168.0.252'],
                     'allow': False,#ping allow(True|False) in target list.
                     'sta_tag': 'sta_1'
                     }
        self.conf.update(conf)
        self.target_list = self.conf['target_ip_list']
        self.allow = self.conf['allow']                
        self.errmsg = ''
        self.passmsg = ''        
        
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        for subnet in self.target_list:
            ip, mask = subnet.split("/")
            if mask == "32":
                logging.info("The restricted destination: %s" % ip)
                if not self.allow:
                    self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, ip,
                                                                       ping_timeout_ms = self.conf['ping_timeout_ms'])
                else:
                    self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, 
                                                                      ping_timeout_ms = self.conf['ping_timeout_ms'])
                if self.errmsg:
                    return self.returnResult('FAIL', self.errmsg)
        if not self.allow:
            return  self.returnResult('PASS', "The station could not transmit traffic to destinations in restricted subnet list. ")
        else:
            return self.returnResult('PASS', "The station could transmit traffic to destinations in restricted subnet list. ")
                             
    
    def cleanup(self):
        self._update_carribag()
