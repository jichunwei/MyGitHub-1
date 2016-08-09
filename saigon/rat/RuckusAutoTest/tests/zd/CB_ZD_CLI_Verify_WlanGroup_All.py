"""
Description: This script is used to verify all wlan group informaton shown in zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_group as wgs
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_CLI_Verify_WlanGroup_All(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyWlanGroupAll()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passage)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.gui_wgs = self.carrierbag['zdgui_all_wlan_group']
        self.cli_wgs = self.carrierbag['zdcli_all_wlan_group']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyWlanGroupAll(self):
        res = wgs.verify_wlan_group_all(self.cli_wgs, self.gui_wgs)
        if not res:
            self.errmsg = 'The WLAN group informatin shown in ZD CLI is not the same as in ZD GUI'
        else:
            self.passage = 'All WLAN group information shown in ZD CLI is the same as in ZD GUI'
