# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Jul 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Linux PC'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Setting the expected option of syslog-ng server on Linux PC
        - Verify if the service is running
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test

class CB_L3Switch_Configure_DHCP_Relay(Test):
    required_components = ['L3Switch']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._configure_dhcp_relay()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'dhcp_relay_conf': {'enable': True,
                                         'vlans': ['301'],
                                         'dhcp_srv_ip': '192.168.0.252'}
                     }
        self.conf.update(conf)
        
        self.l3switch = self.testbed.components['L3Switch']
                        
        self.errmsg = ''
        self.passmsg = ''
    
    def _configure_dhcp_relay(self):
        try:
            self.l3switch.configure_dhcp_relay(**self.conf['dhcp_relay_conf'])
            msg = 'Configure the dhcp relay %s on L3Switch successfully'
            self.passmsg = msg % self.conf['dhcp_relay_conf']
            logging.info(self.passmsg)
        except Exception, e:
            msg = 'Failed to configure the dhcp relay setting on L3Switch: %s'
            self.errmsg = msg % e.message
            logging.info(self.errmsg)
            