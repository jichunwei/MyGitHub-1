"""
Configure ABF on ZD.
Created on 2012-12-13
@author: sean.chen@ruckuswireless.com
"""

import logging
import time

from RuckusAutoTest.models import Test

class CB_ZD_Config_ABF(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._set_abf_on_zd()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Configure ABF successfully'
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'do_abf': True, 'rate_limit': 10}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _set_abf_on_zd(self):
        logging.info('Configure ABF on ZD')
        try:
            self.zd.set_abf(do_abf = self.conf['do_abf'], 
                            rate_limit = self.conf['rate_limit'])
        except Exception, ex:
            self.errmsg = ex.message
