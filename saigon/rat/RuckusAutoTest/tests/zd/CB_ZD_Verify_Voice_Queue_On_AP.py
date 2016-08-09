from RuckusAutoTest.models import Test
import logging

class CB_ZD_Verify_Voice_Queue_On_AP(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._verify_voice_queue_on_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)        
        return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf.copy()
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.ssid = self.conf['ssid']
        self.phone_mac = self.conf['phone_mac']
            
    def _verify_voice_queue_on_ap(self):
        wlan_if = self.active_ap.ssid_to_wlan_if(self.ssid)
        logging.info("Verify voice queue increase on %s of AP [%s]" %(wlan_if, self.active_ap.get_base_mac()) )
        mq_data = self.active_ap.get_mqstats(wlan_if)
        if not mq_data.has_key(self.phone_mac):
            self.errmsg = 'There is no station [%s] connected' % self.phone_mac
        voice_queue = mq_data[self.phone_mac]['voice']['enq']
        logging.debug("get voice enq on %s of AP [%s]" % (wlan_if, self.active_ap.get_base_mac()))
        if int(voice_queue) < 1000:
            self.errmsg += "The voice packets don't go into voice queue"
        else:
            self.passmsg += "There are %s packets go into voice queue" % voice_queue 