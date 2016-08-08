'''
Description:
Created on 2010-8-9
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.ZoneDirector import (ZoneDirector,
                                                    ZoneDirector2)

class CB_ZD_Scaling_Set_Current_ZD(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        if self.zd and (isinstance(self.zd, ZoneDirector) or isinstance(self.zd, ZoneDirector2)):
            self.testbed.components['ZoneDirector'] = self.zd
            self.passmsg = 'Set zd ["%s"] as primary ZoneDirector successfully' % self.conf['zd_key_name']
            logging.info(self.passmsg)
        else:
            self.errmsg = 'Set zd ["%s"] as primary ZoneDirector incorrectly' % self.conf['zd_key_name']
            logging.warning(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
                      
        self._update_carrier_bag()
        
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):        
        zd_key_name = self.conf['zd_key_name']
        if self.carrierbag.has_key(zd_key_name):
            self.zd = self.carrierbag[zd_key_name]
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(zd_key_name='zd1')
        self.conf.update(conf)
        self.zd = None
        self.errmsg = ''
        self.passmsg = ''
    
