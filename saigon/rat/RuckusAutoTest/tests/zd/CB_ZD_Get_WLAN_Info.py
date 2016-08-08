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
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Get_WLAN_Info(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlan_name = None,
                         pause = 10,#by default
                         )
        self.conf.update(conf)
        self.wlan_name = self.conf.get('wlan_name')
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         self.carrierbag['existed_wlan_info'] = self.wlan_info
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            time.sleep(self.conf.get('pause', 10))
            self.wlan_info = Helpers.zd.wlan.get_wlan_info_detail(self.zd, self.wlan_name)
            self._update_carribag()                       
        except Exception, e:
            logging.error(e.message)
            import traceback
            logging.debug(traceback.format_exc())
            self.carrierbag['existed_wlan_info'] = {}
            return self.returnResult('FAIL', e.message)
            
        return self.returnResult('PASS', 'Get WLAN %s DONE' % self.wlan_name)
    
    def cleanup(self):
        pass