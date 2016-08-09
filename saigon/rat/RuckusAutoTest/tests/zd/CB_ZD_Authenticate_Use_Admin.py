'''
set session timeout via web UI
by west.li
@2012.4.9
'''

import time
from RuckusAutoTest.models import Test
import logging

class CB_ZD_Authenticate_Use_Admin(Test):

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        self.zd.authenticate_use_admin()
        return ('PASS', 'set ZD Authenticate using the admin name and password successfully')

    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf={}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''


