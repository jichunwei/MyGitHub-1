"""
Description: This script is used to get all wlan information from zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZDCLI_Get_All_Wlan(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getAllWlanInfo()
        
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

    def _getAllWlanInfo(self):
        try:
            self.wlan_info = gwi.get_wlan_all(self.zdcli)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Get all wlan information from zd cli successfully'
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_wlan_info'] = self.wlan_info
        
        