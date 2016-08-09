# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.
'''
Description:
   This script is support to verify the subnet of wifi ipaddress which is the expected in the station.
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
        
       
Create on Jul 19, 2011
@author: Jacky Luh
@email: jluh@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
#from RuckusAutoTest.components import Helpers as lib

class CB_Station_Verify_Expected_Subnet(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    
    def _init_params(self, conf):
        self.conf = dict(expected_subnet_mask = "")
        self.conf.update(conf)
        if self.conf.has_key('expected_subnet'):
            l = self.conf['expected_subnet'].split("/")
            self.expected_subnet = l[0]
            if len(l) == 2:
                self.expected_subnet_mask = l[1]
            else:
                self.expected_subnet_mask = ""
        else:
            self.expected_subnet = ""
            self.expected_subnet_mask = ""
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.passmsg = ''
        self.errmsg = ''
    
    
    def _retrieve_carribag(self):
        if self.carrierbag.has_key('Station'):
            self.sta_wifi_ip_addr = self.carrierbag['Station'][self.conf['sta_tag']]['sta_wifi_ip_addr']
        else:
            self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        
    
    def _update_carribag(self):
        pass
    
    
    def _verify_active_ap_connection_mode(self):
        logging.info("Verify the subnet address of the wireless client")
        self.sta_wifi_ip_network_addr = utils.get_network_address(self.sta_wifi_ip_addr, self.expected_subnet_mask)
        if self.expected_subnet != self.sta_wifi_ip_network_addr:
            self.errmsg = "The leased IP address was '%s', which is not in the expected subnet '%s'" % \
                          (self.sta_wifi_ip_network_addr, self.expected_subnet)
        
                                                         
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    
    def test(self):
        self._verify_active_ap_connection_mode()
        self._update_carribag()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = "The leased IP address was '%s', which is in the expected subnet '%s'" % \
                       (self.sta_wifi_ip_network_addr, self.expected_subnet)
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass
