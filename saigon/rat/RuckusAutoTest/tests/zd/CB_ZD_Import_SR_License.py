'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import os
import re
import logging
import os
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.admin_license import *

class CB_ZD_Import_SR_License(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        try:
            license_path = r"d:\%s"%self.conf['license_name']
            import_license(self.zd,license_path)
        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
            if self.negative:
                return self.returnResult('PASS', self.errmsg)
            else:
                return self.returnResult('FAIL', self.errmsg)
        else:
            msg = 'Import license to ZD successfully.'
            if self.negative:
                return self.returnResult('FAIL', msg)
            else:
                return self.returnResult('PASS', msg)


    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'license_dir':'',
                     'license_name':'',
                     'zd_tag':'',
                     'negative':False
                     }

        self.conf.update(conf)

        self.errmsg = ''
        self.passmsg = ''
        self.negative = self.conf['negative']
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
