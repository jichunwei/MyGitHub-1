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

class CB_ZD_Verify_AP_IPmode(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.has_key('zd_type') and self.conf['zd_type'] == 'standby':
            self.zd = self.carrierbag['standby_zd']

        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr
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
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.apmac)
        if info['ap_group'] != self.conf['ap_group']:
            self.errmsg += 'active AP is in AP group %s, not in new group %s, ' % (info['ap_group'], self.conf['ap_group'])

        info = lib.zd.ap.get_ap_network_setting_by_mac(self.zd, self.apmac)
        if info['ip_mode'] != self.conf['ip_mode']:
            self.errmsg += 'active AP IP mode of  is %s, not %s, ' % (info['ip_mode'], self.conf['ip_mode'])

        if self.conf.has_key('ip_version') and info['ip_version'] != self.conf['ip_version']:
            self.errmsg += 'active AP IP version of  is %s, not %s, ' % (info['ip_version'], self.conf['ip_version'])

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'IP mode test of AP group passed')
    
    def cleanup(self):
        self._update_carribag()
