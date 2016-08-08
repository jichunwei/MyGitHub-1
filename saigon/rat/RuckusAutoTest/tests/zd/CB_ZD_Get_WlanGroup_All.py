"""
Description: This script is used to get all wlan group information from zd gui.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


from pprint import pformat
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Get_WlanGroup_All(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getWlanGroupAll()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getWlanGroupAll(self):
        logging.info('Get the information of all WLAN group from ZD via GUI.')
        try:
            self.all_wlan_group = wgs.get_all_wlan_group_cfgs_2(self.zd)
            
        except Exception, ex:
            self.errmsg = ex.message
        
        logging.info('The information of all WLAN group shown in ZD GUI is:\n%s.' % pformat(self.all_wlan_group))
        self.passmsg = 'Get the information of all WLAN group from ZD GUI successfully:%s' % self.all_wlan_group
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_all_wlan_group'] = self.all_wlan_group
                