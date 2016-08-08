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

class CB_ZD_CLI_Get_Mgmt_IPV6_ACLs(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Get all management ipv6 acls via ZD CLI")
            self.cli_all_acls_list = mgmt_ip_acl.show_all_mgmt_acl_ipv6(self.zdcli)
        except Exception, ex:
            self.errmsg = 'Get mgmt ipv6 acl failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Get management ivp6 acl via ZD GUI successfully'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['cli_mgmt_ipv6_acl_list'] = self.cli_all_acls_list
        
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
            
        self.errmsg = ''
        self.zdcli = self.testbed.components['ZoneDirectorCLI']