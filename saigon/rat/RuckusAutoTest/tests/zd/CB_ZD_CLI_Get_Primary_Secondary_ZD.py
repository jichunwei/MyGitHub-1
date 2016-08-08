# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: April 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirectorCLI'
   Test parameters:
       - zd_tag: zd tag. Will get zd components via zd tag in self.testbed.components.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get limited ZD discovery settings via ZD CLI.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get limited ZD discovery settings correctly.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import config_ap_policy as lib

class CB_ZD_CLI_Get_Primary_Secondary_ZD(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'zd_tag': "zd tag. Will get zd components via zd tag in self.testbed.components",
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Get limited ZD discovery settings via CLI")
            errmsg = ''
            tries = 5
            for i in range(1,tries+1):
                try:
                    logging.info("Try %s time" % i)
                    self.zd_discovery_cfg = lib.get_limited_zd_discovery(self.zdcli)
                    logging.debug("Time %s, result %s" % (i, self.zd_discovery_cfg))
                    if self.zd_discovery_cfg:
                        break
                    else:
                        time.sleep(10)
                except Exception, ex:
                    errmsg = "Error: %s" % ex.message
                    logging.warning(errmsg)
            
            if errmsg:
                self.errmsg = errmsg
        except Exception, e:
            self.errmsg = "Fail to get limited ZD discovery setting: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Get limited ZD discovery setting correctly: %s" % self.zd_discovery_cfg            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['cli_zd_discovery_cfg'] = self.zd_discovery_cfg
    
    def _init_test_params(self, conf):
        self.conf = dict(enabled = True,
                         primary_zd_ip = '192.168.0.2',
                         secondary_zd_ip = '192.168.0.3',
                         keep_ap_setting = False,
                         prefer_prim_zd = False,
                         zd_tag = '')
        
        self.conf.update(conf)
        
        zd_tag = self.conf.pop('zd_tag')
        
        if zd_tag:
            self.zdcli = self.carrierbag[zd_tag]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
            
        self.errmsg = ''
        self.passmsg = ''