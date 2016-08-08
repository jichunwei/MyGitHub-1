# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to verify active ap exists on test bed
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import os
import re
import time
import logging
import libZD_TestConfig as tconfig

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Find_Active_AP(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):
        self._findActiveAP()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag['active_ap'] = self.active_ap
        msg = 'Find Active AP [%s] on ZD Successfully' % (self.active_ap_mac)
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
            
    def _findActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap={}
            self.active_ap_mac=[]
            if type(self.conf['active_ap']) in (list, tuple):
                i = 1
                for ap in self.conf['active_ap']:
                    self.active_ap['AP'+str(i)] = tconfig.get_testbed_active_ap(self.testbed, ap)
                    self.active_ap_mac.append(self.active_ap['AP'+str(i)].get_base_mac())
                    if not self.active_ap['AP'+str(i)]:
                        self.errmsg = "Active AP [%s] not found in testbed." % ap
                    i += 1
            else: 
                self.active_ap['AP1'] = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
                self.active_ap_mac.append(self.active_ap['AP1'].get_base_mac())
                if not self.active_ap:
                    self.errmsg = "Active AP [%s] not found in testbed." % self.conf['active_ap']

