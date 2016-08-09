'''
Description:
Created on 2010-8-10
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Get_Wlans_List(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        message = []
        try:
            self.wlans_list = lib.zd.wlan.get_wlan_list(self.zd)
        except Exception, e:
            self.errmsg = "Get WLAN name list Fail [%s]" % e.message
            logging.warning(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
             
        self._update_carrier_bag()
        
        return self.returnResult("PASS", message)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existing_wlans_list'] = self.wlans_list
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']     
        self.errmsg = ''
        self.passmsg = ''
    
