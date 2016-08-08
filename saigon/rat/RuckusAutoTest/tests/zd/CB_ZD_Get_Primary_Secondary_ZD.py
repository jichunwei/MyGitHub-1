# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Chris Wang
   @contact: cwang@ruckuswireless.com
   @since: Aug-09, 2010

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       - zd_tag: zd tag. Will get zd components via zd tag in self.testbed.components.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get limited ZD discovery settings.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get limited ZD discovery settings correctly.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd as lib  

class CB_ZD_Get_Primary_Secondary_ZD(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'zd_tag': "zd tag. Will get zd components via zd tag in self.testbed.components",
                              }
    
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Get limited ZD discovery settings via ZD")
            self.zd_discovery_cfg = lib.get_limited_zd_discovery_cfg(self.zd)
            logging.info("Limited ZD discovery cfg: %s" % self.zd_discovery_cfg)
        except Exception, e:
            self.errmsg = "Fail to get limited ZD discovery: %s" % e.message
            
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Get limited ZD discovery correctly: %s" % (self.zd_discovery_cfg)
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['gui_zd_discovery_cfg'] = self.zd_discovery_cfg
    
    def _init_test_params(self, conf):
        self.conf = dict(zd_tag = '')
        self.conf.update(conf)
        
        zd_tag = self.conf.pop('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
            
        self.errmsg = ''
        self.passmsg = ''