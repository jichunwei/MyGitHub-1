'''
Created on Nov 1, 2013

@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test

class CB_ATA_Destroy_Client_Group(Test):
    required_components = ['ATA']
    parameters_description = {}
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']        
        self.grpname = self.conf['grpname']        
        
#        self.wlanone, self.wlantwo = self.wlans
#        self.wgone, self.wgtwo = self.wgs
#    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()        
    
    def test(self):
        res = self.ata.destroy_client_group(groupname = self.grpname)
        logging.info(res)
        
        return self.returnResult('PASS', 'Destroy DONE.')
    
    def cleanup(self):
        self._update_carribag()