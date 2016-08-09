"""
Do the operation that target station disconnects from the wlan.
Created on 2012-12-11
@author: sean.chen@ruckuswireless.com
"""

import logging

from RuckusAutoTest.models import Test

class CB_ZD_Station_Disconnect_From_WLAN(Test):

    def config(self, conf):
        self._init_test_params(conf)


    def test(self):
        self._sta_disconnect_from_wlan()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Station disconnects from the wlan successfully'
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
        
    def _sta_disconnect_from_wlan(self):
        logging.info('Station disconnects from the wlan by itself')
        try:
            self.station.disconnect_from_wlan()
            
        except Exception, ex:
            self.errmsg = ex.message

