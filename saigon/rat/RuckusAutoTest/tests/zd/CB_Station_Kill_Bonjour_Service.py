'''
Created on 2013-10-08
@author: ye.songnan@odc-ruckuswireless.com
description:
   Kill process of all bonjour services.
'''
import logging
import time

from RuckusAutoTest.models import Test

class CB_Station_Kill_Bonjour_Service(Test):
    '''
    Kill process of all bonjour services.
       
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self): 
        while True:
            res = self.target_station.kill_proc(self.proc_name)
            if 'Process does not exist.' in res:
                self.errmsg = ''
                break
            else:
                logging.info(res)
                    
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass
    

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = 'Process dns-sd killed.'
        self.conf = dict(
                         proc_name = 'dns-sd'
                         )
        
        self.conf.update(conf)
        self.proc_name = self.conf['proc_name']
        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']        
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass

