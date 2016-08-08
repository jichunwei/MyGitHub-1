from RuckusAutoTest.models import Test

class CB_ZD_Verify_DTIM_On_AP(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._verify_dtim_on_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)        
        return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf.copy()
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.expected_dtim = self.conf['expected_dtim']
        self.ssid = self.conf['ssid']
            
    def _verify_dtim_on_ap(self):
        wlan_id = self.active_ap.ssid_to_wlan_if(self.ssid)
        dtim = self.active_ap.get_dtim_period(wlan_id)
        if dtim.lower() == self.expected_dtim.lower():
            self.passmsg += 'The expected dtim [%s] on AP[%s];' % (dtim, self.active_ap.get_base_mac())
        else:
            self.errmsg += 'The unexpected dtim [%s] on AP[%s]' % (dtim, self.active_ap.get_base_mac())