'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswirelesss.com
'''

import logging
import time
from RuckusAutoTest.models import Test

class CB_Station_Stop_Iperf(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',                         
                         )
        self.conf.update(conf)
        self._retrieve_carribag()        
        self.errmsg = ""
        self.passmsg = ""
        
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info("Trying to stop Iperf on station")
        try:
            self.target_station.stop_iperf()
        except:
            self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        self._update_carribag()