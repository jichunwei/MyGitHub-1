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
       - enabled: default is True, enable/disable limited zd discovery.
       - primary_zd_ip: default is '192.168.0.2', primary zd ip or domain name.
       - secondary_zd_ip: default is '192.168.0.3', secondary zd ip or domain name.
       - keep_ap_setting: default is False, keep ap setting.
       - prefer_prim_zd: default is False, prefer primary zd.
       - zd_tag: zd tag. Will get zd components via zd tag in self.testbed.components.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Configure limited ZD discovery with valid values via ZD CLI.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: The values are updated successfully.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import config_ap_policy as lib

class CB_ZD_CLI_Set_Primary_Secondary_ZD(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'enabled': "default is True, enable/disable limited zd discovery",
                              'primary_zd_ip': "default is '192.168.0.2', primary zd ip or domain name",
                              'secondary_zd_ip': "default is '192.168.0.3', secondary zd ip or domain name",
                              'keep_ap_setting': "default is False, keep ap setting",
                              'prefer_prim_zd': "default is False, prefer primary zd",
                              'zd_tag': "zd tag. Will get zd components via zd tag in self.testbed.components",
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Configure limited ZD discovery settings via CLI")
            err_list = lib.cfg_limited_zd_discovery(self.zdcli, self.conf)
            if err_list:
                self.errmsg = "Fail configure limited ZD discovery: %s" % err_list
                logging.debug(self.errmsg)          
        except Exception, e:
            self.errmsg = "Set primary and secondary ZDs failure: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            if self.conf.get('enabled'):
                self.passmsg = "Set limited ZD discovery correctly: %s" % self.conf
            else:
                self.passmsg = "Set limited ZD discovery correctly: %s" % self.conf.get('enabled')
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
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