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

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import systemgroup

class CB_AP_CLI_Get_Verify_Primary_Secondary_ZD(Test):
    required_components = ['AP']
    parameters_description = {'ap_tag': 'Access point tag'
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        exp_primary_zd_ip = self.conf['primary_zd_ip']
        exp_secondary_zd_ip = self.conf['secondary_zd_ip']
    
        retry_count = 3
        for i in range(1, retry_count+1):
            err_msg = ''
            
            try:
                #Retry three times.
                logging.info("Get limited ZD discovery settings via AP CLI - %s time" % i)
                zd_discovery_cfg = systemgroup.get_director(self.active_ap)
                
                if self.conf['is_verify']:
                    logging.info("Verify limited ZD discovery in AP CLI - %s time" % i)
                    logging.debug("ZD discovery cfg: %s;Expected: %s, %s" % (zd_discovery_cfg, exp_primary_zd_ip, exp_secondary_zd_ip))
                    err_msg = self._verify_primary_secondary_ap_cli(zd_discovery_cfg, exp_primary_zd_ip, exp_secondary_zd_ip)
                    
                logging.debug("Time %s, Result: %s" % (i, err_msg))
            except Exception, ex:
                err_msg = "Exception:%s" % ex.message
            
            #If fail to verify, wait for some time and verify again.
            if not err_msg: 
                break
            else:
                time.sleep(20)
                
        if err_msg:
            self.errmsg = err_msg
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Get and verify limited ZD discovery setting correctly"            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(ap_tag = '',
                         is_verify = True,
                         primary_zd_ip = '',
                         secondary_zd_ip = '',
                         )
        
        self.conf.update(conf)
        
        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_primary_secondary_ap_cli(self, zd_discovery_cfg, exp_primary_zd_ip, exp_secondary_zd_ip):
        '''
        Verify primary and secondary in AP CLI.
        '''
        err_msg = ''
        primary_zd_ip = zd_discovery_cfg['primary_controller']
        secondary_zd_ip = zd_discovery_cfg['secondary_controller']
        
        if primary_zd_ip == 'n/a':
            primary_zd_ip = ''
        if secondary_zd_ip == 'n/a':
            secondary_zd_ip = ''
            
        if primary_zd_ip.lower() != exp_primary_zd_ip.lower():
            err_msg = "Primary ZD IP/ADDR is incorrect in AP CLI. Expected: %s, Actual: %s" % (exp_primary_zd_ip, primary_zd_ip) 
        if secondary_zd_ip.lower() != exp_secondary_zd_ip.lower():
            err_msg = "Secondary ZD IP/ADDR is incorrect in AP CLI. Expected: %s, Actual: %s" % (exp_secondary_zd_ip, secondary_zd_ip)
            
        return err_msg