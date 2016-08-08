# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description:
   The test API support to create the DHCP Relay server on Zone Director WebUI
   Author: An Nguyen
   Email: an.nguyen@ruckuswireless.com
   Since: Dec 2012

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            
   Result type: PASS/FAIL
   Results: PASS: If the expected process is successful
            FAIL: If the AP could not complete the expected process

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Mesh is enabled is required.
   2. Test:
       - Verify the testing process           
   3. Cleanup:
       - 

   How it is tested?
       -

"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_DHCP_Relay_Server(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        res, msg = self._verify_creating_dhcp_relay_server()
        
        return self.returnResult(res, msg)
        
    def cleanup(self):
        pass    
    
    
    def _init_test_parameters(self, conf):
        self.conf = {'negative_test': False,
                     'dhcp_relay_svr_cfg': {}}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']    
        
        self.passmsg = ''
        self.errmsg = ''      
        
    def _create_dhcp_relay_server(self):
        try:
            lib.zd.dhcpr.create_dhcp_relay_svr(self.zd, **{'svr_cfg': self.conf['dhcp_relay_svr_cfg']})
            self.passmsg = 'Create the DHCP relay server %s successfully' % self.conf['dhcp_relay_svr_cfg']
        except Exception, e:
            self.errmsg = e.message
    
    def _verify_creating_dhcp_relay_server(self):
        logging.info('Verify to create the DHCP relay server: %s' % self.conf['dhcp_relay_svr_cfg'])
        self._create_dhcp_relay_server()
        
        # Return the result base on the negative test option
        if self.errmsg:
            if self.conf['negative_test']:
                passmsg = '[Correct behavior]: %s' % self.errmsg
                logging.info(passmsg)
                return ('PASS', passmsg)
            else:
                logging.info(self.errmsg)
                return ('FAIL', self.errmsg)
        else:
            if self.conf['negative_test']:
                errmsg = '[Incorrect behavior]: %s' % self.passmsg
                logging.info(errmsg)
                return ('FAIL', errmsg)
            else:
                logging.info(self.passmsg)
                return ('PASS', self.passmsg)