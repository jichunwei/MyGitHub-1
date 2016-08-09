'''
Created on Oct 31, 2013
@author: cwang@ruckuswireless.com
'''
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import AtaWrapper as AW

class CB_ATA_Set_Channel(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):        
        self.conf = {'port_name':self.testbed.wifi_01,
                     'channel':self.testbed.fiveg_channel,
                     'band':AW.fiveg_band,}
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']                        
        logging.info("====Initialize Params DONE====")
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):           
        res = self.ata.set_band_channel(**self.conf)        
        return self.returnResult('PASS', 'Set Channel %s DONE.' % self.conf)
    
    def cleanup(self):
        self._update_carribag()
