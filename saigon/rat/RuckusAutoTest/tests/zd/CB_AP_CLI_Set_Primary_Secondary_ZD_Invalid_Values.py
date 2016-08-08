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

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import systemgroup

class CB_AP_CLI_Set_Primary_Secondary_ZD_Invalid_Values(Test):
    required_components = ['AP']
    parameters_description = {'ap_tag': 'Access point tag'
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Verify invalid value in AP CLI")
            self._verify_invalid_values()
        except Exception, e:
            self.errmsg = "Fail to verify invalid values: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Error message is correct for invalid values: %s" % self.invalid_cfg_list            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(ap_tag = '',
                         invalid_primary_zd_addr_list = [],
                         invalid_secondary_zd_addr_list = [],
                         zd_ip_addr = '192.168.0.2',
                         )
        
        self.conf.update(conf)
        
        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        
        zd_ip_addr = self.conf['zd_ip_addr']
        invalid_cfg_list = []
        for pri_zd_ip in self.conf['invalid_primary_zd_addr_list']:
            new_cfg = {}
            new_cfg['primary_zd_ip'] = pri_zd_ip
            new_cfg['secondary_zd_ip'] = zd_ip_addr
            
            invalid_cfg_list.append(new_cfg)
            
        for sec_zd_ip in self.conf['invalid_secondary_zd_addr_list']:
            new_cfg['primary_zd_ip'] = zd_ip_addr
            new_cfg['secondary_zd_ip'] = sec_zd_ip
            
            invalid_cfg_list.append(new_cfg)
            
        self.invalid_cfg_list = invalid_cfg_list
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_invalid_values(self):
        exp_err_list = ['the primary address is longer than 64', ' the secondary address is longer than 64']
            
        for zd_dis_cfg in self.invalid_cfg_list:
        
            primary_zd_ip = zd_dis_cfg['primary_zd_ip']
            secondary_zd_ip = zd_dis_cfg['secondary_zd_ip']
        
            res = systemgroup.set_director(self.active_ap, primary_zd_ip, secondary_zd_ip)
            
            is_match_err = False
            for exp_err in exp_err_list:
                if exp_err.lower() in res.lower():
                    is_match_err = True
                    break
                
            if not is_match_err:
                self.errmsg = "Error message is incorrect. Config:%s,%s, Error: %s" % (primary_zd_ip, secondary_zd_ip, res)