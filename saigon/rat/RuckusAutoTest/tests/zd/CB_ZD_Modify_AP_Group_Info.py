'''
Description:
   Modify AP group information, such as radio band info of ZF7321/ZF7321-u, etc.
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

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Modify_AP_Group_Info(Test):
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
        apgrp_name = self.conf['ap_group']
        try:
            if self.conf.get('ap_model'):
                if self.conf.get('apgrp_radioband'):
                    ap_group.set_ap_group_radio_band_by_ap_model(self.zd, apgrp_name, self.conf['ap_model'], self.conf['apgrp_radioband'])
        except:
            self.errmsg = 'Set AP group[%s] radio band info failed' % apgrp_name

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'AP group[%s] radio band info setting passed' % apgrp_name)
    
    def cleanup(self):
        self._update_carribag()
