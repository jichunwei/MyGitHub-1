from RuckusAutoTest.models import Test

class CB_ZD_Verify_Directed_Bcast_On_AP(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._verify_directed_bcast_on_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)        
        return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf.copy()
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.expected_directed_thr = self.conf['expected_directed_thr']
        self.ssid = self.conf['ssid']
                  
    def _verify_directed_bcast_on_ap(self):
        wlan_id = self.active_ap.ssid_to_wlan_if(self.conf['ssid'])
        directed_thr = self.active_ap.get_directed_thr(wlan_id)
        if directed_thr.lower() == self.expected_directed_thr.lower():
            self.passmsg = 'The expected directed bcast [%s] on AP[%s];' % (directed_thr, self.active_ap.get_base_mac())
        else:
            self.errmsg = 'The unexpected directed bcast [%s] on AP[%s]' % (directed_thr, self.active_ap.get_base_mac())
