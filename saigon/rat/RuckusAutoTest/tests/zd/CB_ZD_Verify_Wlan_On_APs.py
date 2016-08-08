"""
Description: This script is used to verify the status of the WLAN on the active AP and turn off WLAN on other APs if they are specified.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""


from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Verify_Wlan_On_APs(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyWlanOnAPs()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'Verify all wlans on AP [%s] successfully' % self.active_ap.get_base_mac()  
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.ssid = conf['ssid']
        if conf.get("ap_tag"):
            self.active_ap = self.carrierbag[conf['ap_tag']]['ap_ins']
        
        else:
            self.active_ap = self.carrierbag['active_ap']['AP1']
            
        self.ap_list = self.testbed.components['AP']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyWlanOnAPs(self):
        tmethod.verify_wlan_on_aps(self.active_ap, self.ssid, self.ap_list)
        
        