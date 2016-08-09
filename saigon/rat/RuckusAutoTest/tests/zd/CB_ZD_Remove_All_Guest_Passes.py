'''
Description:
    config:
        
    test:
    
    cleanup:
    
Created on 2010-6-10
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_All_Guest_Passes(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        lib.zd.ga.delete_all_guestpass(self.zd, self.conf['load_time'])
        logging.info('del end,begin to check if there is guest pass left')
        current_guest_passes = lib.zd.ga.get_all_guestpasses(self.zd)
        cnt = len(current_guest_passes)
        if cnt > 0:
            errmsg = 'remove all failure, there are [%d] guest passes on the web' % cnt
            logging.info(errmsg)
            return ['FAIL', errmsg]
        self.passmsg = "all of guest passes have been removed successfully!"
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        if self.carrierbag.has_key('existed_gp_cfg'):
            del(self.carrierbag['existed_gp_cfg'])
    
    def _init_test_params(self, conf):
        self.conf = dict(load_time = 2)
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.passmsg = ''
        self.errmsg = ''
        