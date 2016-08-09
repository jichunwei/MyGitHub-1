# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to Change System Name on ZD
Author: Louis Lou
Email: louis.lou@ruckuswireless.com
"""
import os
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Change_System_Name(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            self.zd.set_system_name(self.conf['system_name'])
            self.carrierbag['system_name'] = self.conf['system_name']
           
            msg = 'Set system name to [%s]' % self.conf['system_name']
            return self.returnResult('PASS', msg)
        except:
            self.errmsg = 'Can NOT set system name'
            return self.returnResult("FAIL",self.errmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'system_name':'test'}
        self.conf.update(conf)
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        
