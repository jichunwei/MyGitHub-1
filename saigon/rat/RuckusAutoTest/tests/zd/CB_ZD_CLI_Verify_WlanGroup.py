"""
Description: This script is used to verify the wlan group informaton shown in zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_group as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Verify_WlanGroup(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyWlanGroup()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passage)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.gui_wg = self.carrierbag['zdgui_wlan_group']
        self.cli_wg = self.carrierbag['zdcli_wlan_group']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyWlanGroup(self):
        res = wgs.verify_wlan_group(self.cli_wg, self.gui_wg)
        if not res:
            self.errmsg = 'The information of WLAN group shown in ZD CLI is not the same as in ZD GUI'
        else:
            self.passage = 'The information of WLAN group shown in ZD CLI is the same as in ZD GUI'
