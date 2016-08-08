# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Dec 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       - check_status_timeout: timeout for check status,
       - expected_subnet: Station expected subnet for ipv4. E.g. 192.168.0.0/255.255.255.0
       - expected_subnet_ipv6: Station expected subnet for ipv6.E.g. 2020:db8:1::251/64
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Get station wifi ipv4 and ipv6 address
        - Verify ipv4 and ipv6 address are in expected subnet.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get station wifi address successfully and they are in expected subnet. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l3_acl

class CB_ZD_CLI_Create_L3_ACLs_IPV6(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        logging.info("Create L3/4/IPv6 address Access Control via CLI")
        self._create_l3_acls_ipv6()
        
        if not self.errmsg:
            logging.info("Get L3/4/IPv6 address Access Control via CLI")
            self.current_l3_acls_ipv6 = l3_acl.show_l3acl_ipv6_all(self.zdcli)
            
        if not self.errmsg:
            logging.info("Verify L3/4/IPv6 ACL between CLI set and get")
            err_dict = l3_acl._verify_l3acl_ipv6_cli_set_get(self.l3_acl_cfgs, self.current_l3_acls_ipv6)
            
            if err_dict:
                self.errmsg = "Data between CLI set and get are different: %s" % err_dict
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        else:
            self.passmsg = 'The L3 IPV6 ALCs are created successfully'
            self._update_carrier_bag()
            return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        args = dict(num_of_acls = 32,
                    num_of_rules = 29,
                    l3_acl_cfgs = [])
        
        args.update(conf)
        
        r_cfg = dict(order = '1',
                     description = None,
                     action = '',
                     dst_addr = None,
                     application = None,
                     protocol = None,
                     dst_port = None
                     )        
        
        acl_cnt = args['num_of_acls']
        rule_cnt = args['num_of_rules']
        rule_list = []
        for i in range(3, rule_cnt + 3):
            r_cfg_tmp = r_cfg.copy()
            r_cfg_tmp['order'] = '%d' % i
            rule_list.append(r_cfg_tmp)
            
        acl_list = []
        acl_cfg = {'name':'L3 IPV6 ACL ALLOW ALL', 'description': '','default_mode': 'allow-all', 'rules': rule_list}
        for i in range(1, acl_cnt + 1):
            acl_cfg_tmp = acl_cfg.copy()
            acl_cfg_tmp['name'] = 'Test_ACLs_%d' % i
            acl_list.append(acl_cfg_tmp)
            
        if args['l3_acl_cfgs']:
            self.l3_acl_cfgs = args['l3_acl_cfgs']
        else:
            self.l3_acl_cfgs = acl_list
            
        self.zdcli = self.testbed.components['ZoneDirectorCLI'] 
        
        for l3_acl_cfg in self.l3_acl_cfgs:
            self._add_order_for_rule(l3_acl_cfg)

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['existing_cli_l3_ipv6_acls'] = self.current_l3_acls_ipv6
        
    def _add_order_for_rule(self, l3_acl_cfg):
        rule_list = l3_acl_cfg['rules']
        #There are 4 default rules.
        start_order = 5
        
        if rule_list:
            order = start_order
            for rule in rule_list:
                rule['order'] =  str(order)
                order = order + 1
        
    def _create_l3_acls_ipv6(self):
        try:
            l3_acl.create_l3acl_ipv6(self.zdcli, self.l3_acl_cfgs)
        except Exception, e:
            self.errmsg = '[L3 IPV6 ACL creating failed] %s' % e.message
            logging.debug(self.errmsg)