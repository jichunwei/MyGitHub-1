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

class CB_AP_CLI_Set_Primary_Secondary_ZD(Test):
    required_components = ['AP']
    parameters_description = {'ap_tag': 'Access point tag'
                              }
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            for active_ap in self.active_ap_list:
                ap_mac = active_ap.base_mac_addr
                logging.info("Set limited ZD discovery settings for %s via AP CLI" % ap_mac)
                systemgroup.set_director(active_ap, self.primary_zd_ip, self.secondary_zd_ip)
                
                logging.info("Rebooting AP %s to take effect" % ap_mac)
                active_ap.reboot()
                    
        except Exception, e:
            self.errmsg = "Fail to set limited ZD discovery setting: [%s]" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Set limited ZD discovery setting correctly: %s" % self.conf            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(ap_tag = '', #or ['ap1', 'ap2']
                         primary_zd_ip = '',
                         secondary_zd_ip = '',
                         )
        
        self.conf.update(conf)
        
        ap_tag = self.conf['ap_tag']
        self.active_ap_list = []
        if ap_tag:
            if type(ap_tag) != list:
                ap_tag_list = [ap_tag]
            else:
                ap_tag_list = ap_tag
                
            for aptag in ap_tag_list:
                self.active_ap_list.append(self.carrierbag[aptag]['ap_ins'])
        else:
            #If no ap_tag is specified, will set all ap as specified values.
            self.active_ap_list = self.testbed.components['AP']
            
        self.primary_zd_ip = self.conf['primary_zd_ip']
        self.secondary_zd_ip = self.conf['secondary_zd_ip']
        self.errmsg = ''
        self.passmsg = ''