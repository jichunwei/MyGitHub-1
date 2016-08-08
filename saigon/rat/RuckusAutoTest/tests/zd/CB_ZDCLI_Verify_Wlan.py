"""
Description: This script is used to verify a wlan informaton shown in zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZDCLI_Verify_Wlan(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyWlan()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'wlan_cfg': None}
        self.conf.update(conf)
        self.gui_wlan_cfg = self.conf['wlan_cfg']
        self.zdcli_wlan_info = self.carrierbag['zdcli_wlan_info']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyWlan(self):
        res = gwi.verify_wlan_info(self.zdcli_wlan_info, self.gui_wlan_cfg)
        if not res:
            self.errmsg = 'Fail to verify the wlan information shown in ZD CLI.'
        else:
            self.passage = 'Verify the wlan information shown in ZD CLI successfully.'
