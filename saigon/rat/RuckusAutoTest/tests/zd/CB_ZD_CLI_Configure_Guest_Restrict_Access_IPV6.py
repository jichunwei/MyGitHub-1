# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Jan 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirectorCLI'
   Test parameters:
    --restricted_ipv6_access_list: restricted ipv6 access will be configured.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Configure restricted ipv6 access via ZD CLI
        - Get restricted ipv6 access via ZD CLI
        - Compare data between set and get
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If configure guest ipv6 access successfully and data are same between set and get
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_guestaccess as guest_access

class CB_ZD_CLI_Configure_Guest_Restrict_Access_IPV6(Test):
    required_components = ['ZoneDirectorCLI']
    test_parameters = {'restricted_ipv6_access_list': 'restricted ipv6 access list will be configured'}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        try:
            logging.info("Configure guest restricted ipv6 access via ZD CLI")
            res_cfg_access = ''
            for ipv6_access in self.restricted_ipv6_access_list:
                logging.info("Create guest ipv6 access order %s-%s" % (ipv6_access['order'], ipv6_access['description']))
                result, err_list = guest_access.config_guest_restrict_access_ipv6(self.zdcli, ipv6_access['order'], **ipv6_access)
                
                if not result:
                    res_cfg_access += 'Cfg:%s, Error:%s;' % (ipv6_access, err_list)
                    
            if res_cfg_access:
                self.errmsg = "Configure guest ipv6 access list failed"
                logging.warning("Configure guest restricted ipv6 access list failed: %s" % res_cfg_access)
                
            if not self.errmsg:
                logging.info("Get guest restricted ipv6 access via ZD CLI")
                cli_guest_access_info = guest_access.get_restricted_access(self.zdcli)
                if cli_guest_access_info.get('restricted_ipv6_access'):
                    cli_get_ipv6_access_dict = cli_guest_access_info['restricted_ipv6_access']
                    if cli_get_ipv6_access_dict.has_key('rules'):
                        cli_get_ipv6_access_dict = cli_get_ipv6_access_dict['rules']
                    else:
                        cli_get_ipv6_access_dict = {}
                    #Remove default guest ipv6 access from cli get. Default order is 1.    
                    for order_id in cli_get_ipv6_access_dict.keys():
                        if int(order_id) < 2:
                            cli_get_ipv6_access_dict.pop(order_id)
                    self.cli_get_ipv6_access_dict = cli_get_ipv6_access_dict
                    
                    logging.info("Verify data between CLI set and CLI get")         
                    res_access_list = guest_access.verify_restricted_ipv6_access_cli_set_get(self.restricted_ipv6_access_list, self.cli_get_ipv6_access_dict)
                
                    if res_access_list:
                        self.errmsg = "Data between CLI set and get are different: %s" % res_access_list
                else:
                    self.errmsg = "Don't get restricted ipv6 access list"
                
        except Exception, ex:
            self.errmsg = "Exception: %s" % ex.message
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "Configure guest ipv6 access list via ZD CLI successfully"
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'restricted_ipv6_access_list': []}
        self.conf.update(conf)
        
        self.restricted_ipv6_access_list = self.conf['restricted_ipv6_access_list']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['cli_restricted_ipv6_access_dict'] = self.cli_get_ipv6_access_dict