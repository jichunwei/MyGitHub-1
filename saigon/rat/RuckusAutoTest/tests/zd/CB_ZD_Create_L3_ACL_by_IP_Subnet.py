# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
This script is used to create a single L3 ACL with two default rules,and a user rule.
The 3rd rule can be used to allow/deny a specific subnet.
Input: L3 acl config, including the rules config
Output: Result PASS(the acl is created),or FAIL(the acl could not be created)

Author: chen.tao@odc-ruckuswireless.com
Since:2013-05-13
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_control_zd as AC

class CB_ZD_Create_L3_ACL_by_IP_Subnet(Test):

    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        try:
          AC.create_l3_acl_policy(self.zd,self.conf)
          return ("PASS", "L3_ACL %s is created successfully." % self.conf['name'])	
        except:
          return ("FAIL", "L3_ACL %s is not created." % self.conf['name'])
                          
    def oncleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        rules = [{'order': '3',
                  'description': '',
                  'action': 'Allow',
       		      'dst_addr': r'192.168.0.0/24',
                  'application': 'Any',
                  'protocol': '',
                  'dst_port': ''}]
                             
        self.conf = {'name':'L3_ACL_For_Test',
                     'description':'',
                     'default_mode':'deny-all',
                     'rules':rules}
        
        self.conf.update(conf)
                
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']
        else:
            self.zd = self.testbed.components['ZoneDirector']
                 
        self.errmsg = ''
        self.passmsg = ''


    
