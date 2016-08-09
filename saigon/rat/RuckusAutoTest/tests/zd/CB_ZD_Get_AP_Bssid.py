import time
import logging

import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

class CB_ZD_Get_AP_Bssid(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        bssid=self.active_ap.get_bssid(self.wlan_if)
        self.carrierbag['bssid_backup']=bssid
        return self.returnResult('PASS', 'ap bssid is %s'%bssid)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_tag':'',
                     'wlan_if':'wlan0'} 
        self.conf.update(conf)

        self.errmsg = ""
        self.passmsg = ""
        
        self.ap_tag = self.conf['ap_tag']
        if self.carrierbag.has_key(self.ap_tag):
            self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        if self.conf.has_key('ap_index'):
            self.ap_mac_list=self.testbed.get_aps_mac_list()
            self.ap_mac=self.ap_mac_list[self.conf['ap_index']]
            self.active_ap = self.testbed.mac_to_ap[self.ap_mac.lower()]
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan_if=self.conf['wlan_if']