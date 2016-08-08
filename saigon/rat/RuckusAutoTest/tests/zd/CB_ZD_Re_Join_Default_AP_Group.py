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
       -AP re-join back to Default group.           
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2011-11-7
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers

class CB_ZD_Re_Join_Default_AP_Group(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        ap_group.delete_all_ap_group(self.zd)
        ap_group_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, 'System Default')
        aps_dict = Helpers.zd.aps.get_all_ap_briefs(self.zd)
        mac_list = aps_dict.keys()        
        members_list = ap_group_cfg['members_info']
        
        for mac in mac_list:
            fnd = False
            for member in members_list:
                if member['mac'] == mac:
                    fnd = True
                    break
            if not fnd:
                return self.returnResult('FAIL', 'AP %s have not been found in default group' % mac)
            
        
        return self.returnResult('PASS', 'All AP have moved back to System default group')
    
    def cleanup(self):
        self._update_carribag()