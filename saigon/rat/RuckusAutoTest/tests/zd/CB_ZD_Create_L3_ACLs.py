# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Create_L3_ACLs(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyCreateL3ACLs()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._updateCarrierBag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        args = dict(num_of_acls = 32,
                    num_of_rules = 29,)
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
        acl_list = []
        rule_list = []
        for i in range(3, rule_cnt + 3):
            r_cfg_tmp = r_cfg.copy()
            r_cfg_tmp['order'] = '%d' % i
            rule_list.append(r_cfg_tmp)
            
        acl_cfg = {'name':'L3 ACL ALLOW ALL', 'description': '','default_mode': 'allow-all', 'rules': rule_list}
        for i in range(1, acl_cnt + 1):
            acl_cfg_tmp = acl_cfg.copy()
            acl_cfg_tmp['name'] = 'Test_ACLs_%d' % i
            acl_list.append(acl_cfg_tmp)    
                        
        self.conf = {'l3_acl_cfgs': acl_list}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyCreateL3ACLs(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            lib.zd.ac.create_multi_l3_acl_policies(self.zd, self.conf['l3_acl_cfgs'])
            self.passmsg = 'The L3 ALCs %s are created successfully' % self.conf['l3_acl_cfgs']
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[L3 ACL creating failed] %s' % e.message
            logging.debug(self.errmsg)

    def _updateCarrierBag(self):
        self.carrierbag['existing_l3_acls'] = lib.zd.ac.get_all_l3_acl_policies(self.zd)

