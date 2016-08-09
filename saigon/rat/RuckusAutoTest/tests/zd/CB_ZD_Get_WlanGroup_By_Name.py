"""
Description: This script is used to get the wlan group information by name from zd gui.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from pprint import pformat
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Get_WlanGroup_By_Name(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getWlanGroupByName()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.name = conf['name']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getWlanGroupByName(self):
        logging.info('Get the information of WLAN group [%s] via ZD GUI.' % self.name)
        try:
            self.wlan_group = wgs.get_wlan_group_cfg(self.zd, self.name)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        logging.info('The information of WLAN group [%s] shown in ZD GUI is:\n%s.' % (self.name, pformat(self.wlan_group)))
        self.passmsg = 'Get the information of WLAN group [%s] via ZD GUI successfully:%s' % (self.name, self.wlan_group)
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_wlan_group'] = self.wlan_group
                