# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: July 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector'
   Test parameters:
       - 'mac_addr': 'ap mac address',
       - 'mac_addr_list': 'ap mac address list',
       - 'auto_approval': 'is ap auto approval',
       - 'is_need_approval': 'need to do manual approval',
       - 'timeout': 'timeout for ap join',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - If need do manual approval, approval the ap in mac address list.
        - Verify ap joins and verify ap component via cli.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: AP joins successfully. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Reboot_AP(Test):
    required_components = ['AccessPoint']
    parameters_description = {'ap_tag': 'ap tag'}

    def config(self, conf):
        self._init_test_params(conf) 
    
    def test(self):
        # An Nguyen: an.nguyen@ruckuswireless.com
        # Nov 2012: add the option to let ZD reboot AP. By default AP reboot itself via CLI
        if self.conf['reboot'] == 'by ap':
            self._reboot_ap_by_ap_cli()
        elif self.conf['reboot'] == 'by zd':
            self._reboot_ap_by_zd()      
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'ap_tag': '',
                     'reboot': 'by ap'}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag = self.conf['ap_tag']        
        self.ap = self.carrierbag[self.ap_tag]['ap_ins']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _reboot_ap_by_ap_cli(self):
        logging.info("Rebooting AP via CLI to take effect")
        try:
            self.ap.reboot()
            self.passmsg = 'Reboot AP %s successfully' % self.ap.base_mac_addr
        except Exception, e:
            self.errmsg = 'Can not reboot AP[%s] via AP CLI: %s' % (self.ap.base_mac_addr, e.message)
            
    def _reboot_ap_by_zd(self):
        logging.info("On ZD WebUI reboot AP to take effect")
        try:
            lib.zd.aps.reboot_ap_by_mac_addr(self.zd, self.ap.base_mac_addr)
            time.sleep(10)
            self.passmsg = 'Reboot AP %s successfully' % self.ap.base_mac_addr
        except Exception, e:
            self.errmsg = 'Can not reboot AP[%s] via ZD WebUI: %s' % (self.ap.base_mac_addr, e.message)