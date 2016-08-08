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
        - 'ap_mac_list': 'AP mac address list'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Compare the data between GUI get and CLI get          
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

class CB_ZD_Verify_AP_IP_Settings_GUI_CLI_Get(Test):
    required_components = []
    parameters_description = {'ap_mac_list': 'AP mac address list'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Verify AP device IP settings for %s between GUI get and CLI" % self.ap_mac_list)
            
            err_dict = {}
            for ap_mac_addr in self.ap_mac_list:
                errmsg = ''
                gui_get_ap_cfg = {}
                cli_get_ap_cfg = {}
                if self.gui_get_ap_ip_cfg.has_key(ap_mac_addr):
                    gui_get_ap_cfg = self.gui_get_ap_ip_cfg[ap_mac_addr]
                else:
                    errmsg = "No AP IP setting of GUI get"
                    
                if self.cli_get_ap_ip_cfg.has_key(ap_mac_addr):
                    cli_get_ap_cfg = self.cli_get_ap_ip_cfg[ap_mac_addr]['AP']['ID'].values()[0]
                else:
                    errmsg += "No AP IP setting of CLI get"
                    
                if not errmsg:
                    errmsg = apcli.verify_ap_ip_cfg_gui_cli_get(gui_get_ap_cfg, cli_get_ap_cfg)
                
                if errmsg:
                    err_dict[ap_mac_addr] = errmsg
                    
            if err_dict:
                self.errmsg = 'Data of AP IP setting are different between CLI set and get: %s' % err_dict
                
        except Exception, ex:
            self.errmsg = 'Compare GUI get and CLI get failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            pass_msg = 'GUI get and CLI get data are same'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_mac_list': []}
        self.conf.update(conf)
        
        if type(self.conf['ap_mac_list']) != list:
            self.ap_mac_list = [self.conf['ap_mac_list']]
        else:
            self.ap_mac_list = self.conf['ap_mac_list']
                
        self.gui_get_ap_ip_cfg = self.carrierbag['gui_ap_ip_cfg']
        self.cli_get_ap_ip_cfg = self.carrierbag['cli_ap_ip_cfg']
            
        self.errmsg = ''