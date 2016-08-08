from RuckusAutoTest.models import Test
import time
import logging

class CB_ZD_Clear_Mqstats_On_AP(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._verify_station_connected_on_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)   
        self._clear_mqstats_on_ap()
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
        self.timeout = 30
        
    def _verify_station_connected_on_ap(self):
        wlan_if = self.active_ap.ssid_to_wlan_if(self.ssid)
        start_time = time.time() 
        while (time.time()-start_time) < self.timeout:
            sta_info = self.active_ap.get_station_stats_info(wlan_if)
            if sta_info:
                break
            time.sleep(3)
            logging.debug("wait for wireless station connected")
        if len(sta_info) == 0:
            self.errmsg += "There is no wireless station connected"
                                  
    def _clear_mqstats_on_ap(self):
        wlan_if = self.active_ap.ssid_to_wlan_if(self.ssid)                
        try:
            self.active_ap.clear_mqstats(wlan_if)
            logging.info("clear mqstats on %s of AP [%s]" % (wlan_if, self.active_ap.get_base_mac()))
        except Exception, e:
            self.errmsg += "clear mqstats failure is due to %s" % e.message
        self.passmsg += "clear wlan[%s] mqstats successfully" % wlan_if