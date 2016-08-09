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

class CB_ZD_CLI_Create_Mgmt_IPV6_ACLs(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'mgmt_acl_list': 'management acl list'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Create management ipv6 acls via ZD CLI")
            err_dict = mgmt_ip_acl.create_multi_mgmt_acls_ipv6(self.zdcli, self.mgmt_ipv6_acl_list)           
            
            if err_dict:
                self.errmsg = "Create mgmt ipv6 acl failed: %s" % err_dict
                
            if not self.errmsg:
                logging.info("Get all management ipv6 acls via ZD CLI")
                self.cli_all_acls_list = mgmt_ip_acl.show_all_mgmt_acl_ipv6(self.zdcli)
                
                logging.info("Compare data between CLI set and get")
                self._compare_cli_set_get()
        except Exception, ex:
            self.errmsg = 'Create and compare mgmt ipv6 acl failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Create management ipv6 acls via ZD CLI and data are same between set and get successfully'
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
        self.conf = {'mgmt_acl_list': []}        
        self.conf.update(conf)
        
        self.mgmt_ipv6_acl_list = self.conf['mgmt_acl_list']
            
        self.errmsg = ''
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def _create_mgmt_acls(self, ipv6_acl):
        errmsg = ''
        try:
            mgmt_ip_acl.create_multi_mgmt_acls_ipv6(self.zdcli, self.mgmt_ipv6_acl_list)            
        except Exception,ex:
            errmsg = 'Create Mgmt IPV6 ACL Failed: %s' % ex.message
        return errmsg
            
    def _compare_cli_set_get(self):
        if self.mgmt_ipv6_acl_list and self.cli_all_acls_list:
            res = mgmt_ip_acl.compare_mgmt_ipv6_acl_cli_set_get(self.mgmt_ipv6_acl_list, self.cli_all_acls_list)
        else:
            if self.mgmt_ipv6_acl_list == self.cli_all_acls_list:
                res = "No mgmt acl in CLI set and get"
            elif not self.mgmt_ipv6_acl_list:
                res = "No mgmt acl in CLI set"
            elif not self.cli_all_acls_list:
                res = "No mgmt acl in CLI get"
        if res:
            self.errmsg = "Data between CLI set and get are different: %s" % res