# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirectorCLI'
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
from RuckusAutoTest.components.lib.zdcli import ap_info_cli

class CB_ZD_CLI_Get_AP_IP_Settings(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:          
            ap_info_dict = {}
            if self.ap_mac_list:
                for ap_mac_addr in self.ap_mac_list:
                    logging.info("Get current AP device IP settings for %s via CLI." % ap_mac_addr)
                    ap_cfg = ap_info_cli.show_ap_info_by_mac(self.zdcli, ap_mac_addr)
                    ap_info_dict[ap_mac_addr] = ap_cfg
            else:
                #Get all aps information if no ap mac address is passed.
                ap_info_dict = ap_info_cli.show_ap_all(self.zdcli)
                
            self.ap_info_dict = ap_info_dict
                
        except Exception, ex:
            self.errmsg = 'Can not get AP device IP settings successfully:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Get AP device IP settings successfully.'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['cli_ap_ip_cfg'] = self.ap_info_dict        
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_mac_list': []}
        self.conf.update(conf)
        
        if type(self.conf['ap_mac_list']) != list:
            self.ap_mac_list = [self.conf['ap_mac_list']]
        else:
            self.ap_mac_list = self.conf['ap_mac_list']
            
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''