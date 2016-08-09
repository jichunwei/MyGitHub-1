'''
Description:
    Remove all self service guest pass on zd Web.
       
Create on 2015-4-15
@author: yanan.yu
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_All_SelfService_Guest_Passes(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        
        self._delete_all_selfservice_guestpass() 
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        
        self.passmsg = "all of self service guest passes have been removed successfully!"
        return ("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(load_time = 2)
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.passmsg = ''
        self.errmsg = ''
  
        
    def _delete_all_selfservice_guestpass(self):
        
        lib.zd.ga.delete_all_selfservice_guestpass(self.zd, self.conf['load_time'])
        logging.info('del end,begin to check if there is guest pass left')
        
        current_guest_passes = lib.zd.ga.get_all_selfguestpasses(self.zd)
        cnt = len(current_guest_passes)
        if cnt > 0:
            self.errmsg = 'remove all selfservice guestpass failure, there are [%d] guest passes on the web' % cnt
            logging.info(self.errmsg)
            return False
        else:
            return True
    

        