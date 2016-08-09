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

class CB_ZD_Move_AP_Group_Member(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'is_exist':True, 'move_to_member_list':[]}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''

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
        org_apgrp = self.conf['src_ap_group']
        move_to_ap_group = self.conf['move_to_ap_group']

        try:
            logging.info('Try to move AP[%s] from AP group[%s] to [%s]' % (self.apmac, org_apgrp, move_to_ap_group))

            ap_group.move_aps_to_ap_group(self.zd, 
                                          self.apmac, 
                                          org_apgrp, 
                                          move_to_ap_group)
        except:
            self.errmsg = 'Move AP[%s] from AP group[%s] to [%s] failed' % (self.apmac, org_apgrp, move_to_ap_group)

        time0 = time.time()
        wait_time = 300
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                return self.returnResult('FAIL', 'active AP not connected in %s second after change IP mode when move AP in different groups, ' % wait_time)

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)
                if ap_info['state'].lower().startswith('connected'):
                    break
            except:
                pass

            time.sleep(3)

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', 'Move AP[%s] from AP group[%s] to [%s]  passed' % (self.apmac, org_apgrp, move_to_ap_group))
    
    def cleanup(self):
        self._update_carribag()
