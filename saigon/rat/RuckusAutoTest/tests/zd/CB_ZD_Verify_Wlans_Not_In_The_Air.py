'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify if the target station could see the SSID of WLANs broadcasted in the air.
'''


import logging
import time

from RuckusAutoTest.models import Test


class CB_ZD_Verify_Wlans_Not_In_The_Air(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyWlansNotInTheAir()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _initTestParameters(self, conf):
        self.conf = dict(ssid_list = [],
                         target_station = "",
                         check_timeout = 120)
        self.conf.update(conf)
        
        if self.conf['target_station']:
            self.target_station = self.carrierbag['station_list'][self.conf['target_station']]

        else:
            self.target_station = self.carrierbag['station']

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ""
        self.passmsg = ""
    
    def _verifyWlansNotInTheAir(self):
        logging.info("Verify if the target station could see the ssid %s broadcasted in the air" % self.conf['ssid_list'])
        start_time = time.time()
        while True:
            time.sleep(10)
            self.target_station.restart_adapter()
            for ssid in self.conf['ssid_list']:
                res = self.target_station.check_ssid(ssid)
                if res == ssid:
                    self.errmsg = "The station can see wlan [%s] in the air" % ssid
                    return
            
            if time.time() - start_time > self.conf['check_timeout']:
                self.passmsg = "The station can't see wlans %s in the air within %d seconds" % (self.conf['ssid_list'], self.conf['check_timeout'])
                return
                
    