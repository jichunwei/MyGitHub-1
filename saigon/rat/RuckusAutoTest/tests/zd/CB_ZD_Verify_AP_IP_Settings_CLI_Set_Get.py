# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - set_ip_cfg: ZD ip configuration has been set.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Compare the data between CLI get and set          
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as apcli


class CB_ZD_Verify_AP_IP_Settings_CLI_Set_Get(Test):
    required_components = []
    parameters_description = {'set_ip_cfg': 'ZD IP configuration.',
                              'ap_mac_list': 'ap mac address list'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Verify CLI set and get values for AP device IP settings")
            
            err_dict = {}
            
            for ap_mac_addr in self.ap_mac_list:
                errmsg = ''
                if self.cli_get_ap_ip_cfg.has_key(ap_mac_addr):
                    cli_get_ap_cfg = self.cli_get_ap_ip_cfg[ap_mac_addr]['AP']['ID'].values()[0]
                    errmsg = apcli.verify_ap_ip_cfg_cli_get_set(self.cli_set_ap_ip_cfg, cli_get_ap_cfg)
                else:
                    errmsg = "No AP IP setting of CLI get"
                
                if errmsg:
                    err_dict[ap_mac_addr] = errmsg
                    
            if err_dict:
                self.errmsg = 'Data of AP IP setting are different between CLI set and get: %s' % err_dict
             
        except Exception, ex:
            self.errmsg = 'CLI set and get failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            pass_msg = 'CLI get and set data are same'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'set_ip_cfg': {},
                     'ap_mac_list': []}
        self.conf.update(conf)
        
        if type(self.conf['ap_mac_list']) != list:
            self.ap_mac_list = [self.conf['ap_mac_list']]
        else:
            self.ap_mac_list = self.conf['ap_mac_list']
        
        self.cli_set_ap_ip_cfg = self.conf['set_ip_cfg']        
        self.cli_get_ap_ip_cfg = self.carrierbag['cli_ap_ip_cfg']
            
        self.errmsg = ''