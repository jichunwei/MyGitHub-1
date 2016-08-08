# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Aprial 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'L3Switch'
   Test parameters:
       N/A
        
   Test procedure:
    1. Config:
        - initialize test parameters
        - Get switch from testbed.components
        - Get interface from carrier bag                
    2. Test:
        - Enable interface on Switch
        - Disable interface on Switch
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: The interface of specified ZD are enabled. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test

class CB_ZD_Get_Switch_Interface(Test):
    required_components = ['L3Switch']
    parameters_description = {'zd_tag': 'zd tag',
                              'enable': 'If true, enable interface, else disable interface',
                              'is_zd_up': 'If zd is up,get interface via zd mac address, else get interface from carrierbag'}
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        try:
            logging.info("Get ZD mac address")
            self.zd_mac_addr = self.zd.mac_addr
            
            logging.info("Get interface by mac address %s" % self.zd_mac_addr)
            self.interface = self.sw.mac_to_interface(self.zd_mac_addr)
        
        except Exception, ex:
            self.errmsg = "Error:%s" % ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrierbag()            
            msg = 'Get interface [%s] for %s' % (self.interface, self.zd_mac_addr)
            return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = {'zd_tag': '',
                     'if_tag': 'interface',
                     }
        
        self.conf.update(conf)
        
        self.if_tag = self.conf['if_tag']
        
        zd_tag = self.conf['zd_tag']
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        #Get Switch component from carrier bag or testbed.components.
        self.sw = self.testbed.components['L3Switch']
        
    def _update_carrierbag(self):
        self.carrierbag[self.if_tag] = self.interface
        