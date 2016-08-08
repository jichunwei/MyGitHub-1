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
        
        
Create on 2012-10-10
@author: kevin.tan@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_AP_Group_Info(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'is_exist': True}
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
        apgrp = self.conf['ap_group']
        try:
            info = ap_group.get_ap_group_ip_mode_by_name(self.zd, apgrp)
            if info['ip_mode'] != self.conf['ip_mode']:
                self.errmsg += 'IP mode of AP group[%s] is %s, not %s, ' % (apgrp, info['ip_mode'], self.conf['ip_mode'])
            
            if self.conf.has_key('ap_tag'):
                active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
                apmac = active_ap.base_mac_addr
                
        except:
            if self.conf['is_exist'] == False:
                return self.returnResult('PASS', 'AP group[%s] group name not exist, passed' % apgrp)
        
            self.errmsg = 'Get AP group[%s] info failed' % apgrp

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'AP group[%s] info verification passed' % apgrp)
    
    def cleanup(self):
        self._update_carribag()
