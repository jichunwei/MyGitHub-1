"""
Description: This script is support to stop back ground traffic on remote station
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import logging
from RuckusAutoTest.models import Test

class CB_ZD_Stop_Back_Ground_Traffic(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._stop_back_ground_traffic()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        passmsg = 'Stop back group traffic on station [%s] successfully' % self.bg_sta.ip_addr
        return self.returnResult('PASS', passmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf.copy()
        self.bg_sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        if self.carrierbag[self.conf['sta_tag']].has_key('back_ground_traffic_enable'):
            self.back_ground_traffic_enable = self.carrierbag[self.conf['sta_tag']]['back_ground_traffic_enable']
        
    def _stop_back_ground_traffic(self):
        if self.back_ground_traffic_enable:
            self.carrierbag[self.conf['sta_tag']]['back_ground_traffic_enable']=False
            return self.bg_sta.do_cmd('ZA.kill_zap_thread')
        else:
            logging.info("No Back Ground Traffic running")
            self.errmsg = "No Back Ground Traffic runnig"
