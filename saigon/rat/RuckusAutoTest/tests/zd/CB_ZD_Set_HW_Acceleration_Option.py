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
        
        
Create on 2012-12-20
@author: kevin.tan@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import service_zd as service

class CB_ZD_Set_HW_Acceleration_Option(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.has_key('zd_type') and self.conf['zd_type'] == 'standby':
            self.zd = self.carrierbag['standby_zd']

        self.passmsg = ''
        self.errmsg = ''

    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()

    def test(self):
        if self.conf['operation'] == 'enable':
            enabled = True
        else:
            enabled = False
        
        try:
            service.set_tunnel_encryption_option(self.zd, enabled)
        except:
            self.errmsg = 'Set ZD tunnel encryption option to %s failed' % self.conf['operation']

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'Set ZD tunnel encryption option to %s passed' % self.conf['operation'])
    
    def cleanup(self):
        self._update_carribag()
