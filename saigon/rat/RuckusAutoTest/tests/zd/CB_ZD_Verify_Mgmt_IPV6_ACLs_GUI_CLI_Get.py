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
        - 'ap_mac_list': 'AP mac address list',
        - 'ip_cfg': 'AP IP configuration.'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set AP device IP setting as specified via CLI
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If set device IP setting successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import mgmt_ip_acl

class CB_ZD_Verify_Mgmt_IPV6_ACLs_GUI_CLI_Get(Test):
    required_components = []
    parameters_description = {}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Compare management ipv6 acl between gui get and cli get")
            res = mgmt_ip_acl.compare_mgmt_ipv6_acl_gui_cli_get(self.gui_get_mgmt_ipv6_acl, self.cli_get_mgmt_ipv6_acl)
            if res:
                self.errmsg = "Data between gui and cli get are different: %s" % res
        except Exception, ex:
            self.errmsg = 'Compare data failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Data between GUI get and CLI get are same'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        '''
        Mgmt acl dict sample:
            {'name': 'mgmt ip acl name',
             'type': 'single|prefix,
             'addr': 'single addr|addr and prefix split with /',
             }
        '''
        self.conf = {}        
        self.conf.update(conf)
        
        self.gui_get_mgmt_ipv6_acl = self.carrierbag['gui_mgmt_ipv6_acl_list']
        self.cli_get_mgmt_ipv6_acl = self.carrierbag['cli_mgmt_ipv6_acl_list']
            
        self.errmsg = ''