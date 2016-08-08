"""
Description: This script is used to edit an exist wlan group in zd.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Edit_WlanGroup(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._editWlanGroup()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.wlan_group = conf['wlan_group']
        self.wgs_cfg = conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _editWlanGroup(self):
        logging.info('Edit the WLAN group [%s] in ZD via GUI with configuration:\n%s.' % (self.wlan_group, self.wgs_cfg))
        
        try:
            wgs.edit_wlan_group_cfg(self.zd, self.wlan_group, self.wgs_cfg)
            
        except Exception, ex:
            self.errmsg = ex.message
        
        logging.info('Edit the Wlan group [%s] successfully!' % self.wlan_group)
        self.passmsg = 'Edit the WLAN group [%s] with configuration [%s] in ZD via GUI successfully' % (self.wlan_group, self.wgs_cfg)
