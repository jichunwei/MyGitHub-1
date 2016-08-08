"""
Description: This script is used to get the wlan group information by name from zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_group as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Show_WlanGroup_By_Name(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._showWlanGroupByName()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.name = conf['name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _showWlanGroupByName(self):
        try:
            self.wlan_group = wgs.get_wlan_group_by_name(self.zdcli, self.name)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Get the information of WLAN group [%s] from ZD CLI successfully:%s' % (self.name, self.wlan_group)
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_wlan_group'] = self.wlan_group
                