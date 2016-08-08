"""
Description: This script is used to get the wlan information by sssid from zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi

class CB_ZDCLI_Get_Wlan_By_SSID(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getWlanBySSID()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
#        louis: for carrierbag['wlan_name']
        if conf.has_key('ssid'):
            self.ssid = conf.get('ssid')
        else:
            self.ssid = self.carrierbag['wlan_name']

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _getWlanBySSID(self):
        try:
            self.wlan_info = gwi.get_wlan_by_ssid(self.zdcli, self.ssid)
            logging.info('ZD CLI wlan info: %s' % self.wlan_info)
            
            if not self.wlan_info:
                self.errmsg = 'Did not get wlan information for %s.' % (self.ssid)
            else:
                self.passmsg = 'Get information of WLAN [%s] from ZD CLI successfully' % (self.ssid)
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_wlan_info'] = self.wlan_info
        self.carrierbag['wlan_cfg'] = self.wlan_info
                