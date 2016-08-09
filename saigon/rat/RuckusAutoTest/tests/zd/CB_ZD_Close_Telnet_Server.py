# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: close telnet server in zd
by west.li
"""

import logging

from RuckusAutoTest.models import Test

class CB_ZD_Close_Telnet_Server(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            self.zd.configure_telnet_server(False)
            logging.info('telnet server disabled successfully')
            msg = 'telnet server is disabled' 
            return self.returnResult('PASS', msg)
        except Exception,e:
            self.errmsg = 'telnet server disable failed,%s'%e.message
            return self.returnResult("FAIL",self.errmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        
