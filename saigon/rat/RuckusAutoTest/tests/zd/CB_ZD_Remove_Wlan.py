'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-11-1
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Remove_Wlan(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ssid=None)
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ssid = self.conf.get('ssid')
        if not self.ssid:
            self.ssid = self.conf.get('wlan_name')
        if not self.ssid:
            raise "ssid not specified"    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        #edit by West
        wlan_list = Helpers.zd.wlan.get_wlan_list(self.zd)
        if self.ssid in wlan_list:
            try:
                Helpers.zd.wlan.del_wlan(self.zd, self.ssid)
            except Exception, e:
                return self.returnResult('FAIL', e.message)
        
        else:
            msg = 'Not found WLAN %s' % self.ssid
            logging.error(msg)
            return self.returnResult('FAIL', msg)
            
        return self.returnResult('PASS', 'Remove WLAN %s DONE' % self.ssid)
    
    def cleanup(self):
        self._update_carribag()