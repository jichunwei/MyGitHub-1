'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import os
import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.admin_license import *

class CB_ZD_Delete_All_SR_License(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        try:
            delete_all_license(self.zd)
        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', 'All licenses are deleted successfully!')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'zd_tag':''}
        self.conf.update(conf)

        self.errmsg = ''
        self.passmsg = ''

        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']