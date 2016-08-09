"""
Do the operation that releasing target station wifi IP address.
Created on 2012-12-21
@author: sean.chen@ruckuswireless.com
"""

import logging
import time

from RuckusAutoTest.models import Test

class CB_ZD_Release_Station_Wifi_Addr(Test):

    def config(self, conf):
        self._init_test_params(conf)


    def test(self):
        self._release_sta_wifi_addr()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Release station wifi IP address successfully'
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass


    def _init_test_params(self, conf):
        self.conf = {'sta_tag': 'sta1'}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        
    def _release_sta_wifi_addr(self):
        logging.info('Release station wifi IP address')
        try:
            release_count = 0
            while(release_count < 3):
                time.sleep(10)
                self.station.do_release_wifi_ip_address()
                release_count += 1
                
        except Exception, ex:
            self.errmsg = ex.message

