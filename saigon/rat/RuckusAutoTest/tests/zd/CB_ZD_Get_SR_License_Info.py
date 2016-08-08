'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import os
import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.admin_license import *
from RuckusAutoTest.components.lib.zd import dashboard_zd

class CB_ZD_Get_SR_License_Info(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        try:
            license_AP_num = get_licensed_AP_total_num(self.zd)
            zd_original_AP_num = dashboard_zd.get_zd_original_AP_num(self.zd)
            AP_num = license_AP_num + zd_original_AP_num
            if self.zd_tag:
                self.carrierbag['%s_licensed_ap_num'%self.zd_tag]=AP_num
            else:
                self.carrierbag['zd_licensed_ap_num']=AP_num
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', 'Get zd ap num successfully!')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'zd_tag':''}
        self.conf.update(conf)

        self.errmsg = ''
        self.passmsg = ''

        self.zd_tag = self.conf.get('zd_tag')
        if self.zd_tag:
            self.zd = self.carrierbag[self.zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']