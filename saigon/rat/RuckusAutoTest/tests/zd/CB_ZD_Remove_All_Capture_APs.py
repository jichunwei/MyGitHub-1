'''
Description:

Procedure:
    
Create on 2012-03-10
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import packet_capture as pcap


class CB_ZD_Remove_All_Capture_APs(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            pcap.remove_capture_aps(self.zd, remove_all = True)
            self.passmsg = 'Remove all APs from capture APs table successfully'
            
        except Exception, e:
            self.errmsg = e.message
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        pass
            
    def _update_carribag(self):
        pass
    
