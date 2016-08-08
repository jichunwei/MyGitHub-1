# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
       - 'num_of_acls': 'num of acls, default is 32',
       - 'num_of_rules': 'num of rules, default is 29',
       - 'l3_acl_cfgs': 'l3 acl configuration.'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Create L3 IPV6 acls based on l3_acl_cfg via ZD GUI
        - Get all l3 ipv6 acls via ZD GUI
        - Compare data between set and get
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If configure l3 ipv6 acls successfully and data are same between set and get
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_L3_ACLs_IPV6(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'num_of_acls': 'num of acls, default is 32',
                             'num_of_rules': 'num of rules, default is 29',
                             'l3_acl_cfgs': 'l3 acl configuration.'}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        try:
            logging.info("Create L3/4/IPv6 address Access Control via GUI")
            self._create_l3_acls_ipv6()
            
            if not self.errmsg:
                logging.info("Get L3/4/IPv6 address Access Control via GUI")
                self.current_l3_acls_ipv6 = lib.zd.ac.get_all_l3_ipv6_acl_cfgs(self.zd)
            if not self.errmsg:
                logging.info("Verify L3/4/IPv6 ACL between GUI set and get")
                res_compare_acl = lib.zd.ac._verify_l3acl_ipv6_guiset_guiget(self.l3_acl_cfgs, self.current_l3_acls_ipv6)
                
                if res_compare_acl:
                    self.errmsg = "Data between GUI set and get are different: %s" % res_compare_acl            
        except Exception, e:
            self.errmsg = '[L3 IPV6 ACL creating failed] %s' % e.message
            logging.debug(self.errmsg)
        
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
            
        self.zd = self.testbed.components['ZoneDirector']
        
        for l3_acl_cfg in self.l3_acl_cfgs:
            self._add_order_for_rule(l3_acl_cfg)

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['existing_l3_ipv6_acls'] = self.current_l3_acls_ipv6
        
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
            lib.zd.ac.create_multi_l3_ipv6_acl_policies(self.zd, self.l3_acl_cfgs)
        except Exception, e:
            self.errmsg = '[L3 IPV6 ACL creating failed] %s' % e.message
            logging.debug(self.errmsg)