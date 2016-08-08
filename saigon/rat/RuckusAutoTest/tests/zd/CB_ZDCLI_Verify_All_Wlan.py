"""
Description: This script is used to verify all wlan informaton shown in zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZDCLI_Verify_All_Wlan(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyAllWlan()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passage)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'wlan_cfg_list': None}
        self.conf.update(conf)
        self.gui_wlan_cfg_list = self.conf['wlan_cfg_list']
        self.cli_wlan_info_dict = self.carrierbag['zdcli_wlan_info']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyAllWlan(self):
        res = gwi.verify_wlan_info_all(self.cli_wlan_info_dict, self.gui_wlan_cfg_list)
        if not res:
            self.errmsg = 'Fail to verify wlan information shown in ZD CLI.'
        else:
            self.passage = 'Verify wlan information shown in ZD CLI successfully.'
