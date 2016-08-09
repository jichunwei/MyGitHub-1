"""
Description: CB_ZD_Create_Wlan_On_Standalone_AP a combo test that create a list of different wlan for testing on stand-alone AP

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
    - 'wlan_cfg_list': a list of dictionary of wlan configuration to create a wlan on Zone Director
   Result type: PASS/FAIL
   Results: PASS: if all wlan create successful
            FAIL: if any wlan can't create

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

"""

import logging

from RuckusAutoTest.models import Test

class CB_ZD_Set_AP_Wlan_Bssid(Test):
    parameter_description = {
                          }
    def config(self, conf):
        self.conf = {'ap_tag':'',
                     'wlan_if':'wlan0'}

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = "set bssid successfully"
        
        self.wlan_if=self.conf['wlan_if']

        if self.carrierbag.has_key('stand_alone_ap'):
            self.active_ap = self.carrierbag['stand_alone_ap']
            
        self.ap_tag = self.conf['ap_tag']
        if self.carrierbag.has_key(self.ap_tag):
            self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        
        self.bssid=self.carrierbag['bssid_backup']
        

    def test(self):
        self.carrierbag['bssid_backup']=self.active_ap.get_bssid(self.wlan_if)
        logging.info('bssid before set is %s'%self.carrierbag['bssid_backup'])
        if not self.active_ap.set_bssid(self.wlan_if,self.bssid):
            self.errmsg='set BSSID Failed'
        bssid=self.active_ap.get_bssid(self.wlan_if)
        if bssid!=self.bssid:
            self.errmsg='BSSID not correct after reboot %s instead of %s'%(bssid,self.bssid)
        if self.carrierbag.has_key('stand_alone_ap'):
            self.carrierbag['stand_alone_SSID']=self.bssid
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
