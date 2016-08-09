# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get Current ZD device IP setting via GUI
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If get device IP setting successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zd import system_zd as sys

class CB_ZD_Get_Device_IP_Settings(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:          
            logging.info("Get current ZD device IP settings via GUI")
            ip_type = const.IPV6
            self.get_zd_ip_cfg = sys.get_device_ip_settings(self.zd, ip_type)
        except Exception, ex:
            self.errmsg = 'Can not get ZD device IP settings successfully:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Get ZD device IP settings successfully'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['gui_zd_ip_cfg'] = self.get_zd_ip_cfg
        
    def _cfg_init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']