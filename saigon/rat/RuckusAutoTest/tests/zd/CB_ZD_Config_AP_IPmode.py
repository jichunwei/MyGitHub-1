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

class CB_ZD_Config_AP_IPmode(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr

    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()

    def test(self):
        try:
            if self.conf.has_key('ap_group'):
                lib.zd.ap.set_ap_general_by_mac_addr(self.zd, self.apmac, ap_group=self.conf['ap_group'])
                time.sleep(2)
    
            lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, self.conf['ip_mode'])
        except:
            return self.returnResult('FAIL', 'Set AP-group  belonging and IP mode of active AP[%s] configuration failed' % self.apmac)
        
        time0 = time.time()
        wait_time = 180
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                return self.returnResult('FAIL', 'active AP not connected in %s second after change IP mode, ' % wait_time)

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)
                if ap_info['state'].lower().startswith('connected'):
                    break
            except:
                pass

            time.sleep(3)

        return self.returnResult('PASS', 'IP mode test of AP group passed')
    
    def cleanup(self):
        self._update_carribag()
