"""
Description: This script is used to get all wlan group information from zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_group as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Show_WlanGroup_All(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._showWlanGroupAll()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _showWlanGroupAll(self):
        try:
            self.all_wlan_group = wgs.get_wlan_group_all(self.zdcli)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Get the information of all WLAN group from ZD CLI successfully:%s' % self.all_wlan_group
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_all_wlan_group'] = self.all_wlan_group
                