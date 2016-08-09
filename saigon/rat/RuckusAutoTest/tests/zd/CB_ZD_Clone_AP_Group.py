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
       Clone a AP Group and if check success or not.            
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

class CB_ZD_Clone_AP_Group(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'clone_name':'AP_Group_Test',
                     'new_name':'AP_Group_Test_Cloned'
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.clone_name = self.conf['clone_name']
        self.new_name = self.conf['new_name']
        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            ap_group_found = ap_group.query_ap_group_brief_info_by_name(self.zd, 
                                                                        self.clone_name,
                                                                        op = 'xeq'
                                                                        )
            if not ap_group_found:#Create a new one if haven't found it.
                ap_group.create_ap_group(self.zd, self.clone_name)
                
            ap_group.clone_ap_group(self.zd, self.clone_name, self.new_name)
            old_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, self.clone_name)
            new_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, self.new_name)
            #We don't check aps_info and memebers_info
            old_cfg.pop('aps_info')
            old_cfg.pop('members_info')
            new_cfg.pop('aps_info')
            new_cfg.pop('members_info')
#            if old_cfg != new_cfg:
#                logging.warning(old_cfg)
#                logging.warning(new_cfg)                
#                return self.returnResult('FAIL', 'Cloned object is different with clone object.')
            
            return self.returnResult('PASS', 'Clone AP Group %s, original %s successfully' % (old_cfg, new_cfg))
                
        except Exception, e:            
            return self.returnResult('FAIL', 'Clone action error %s' %  e.message)
    
    def cleanup(self):
        self._update_carribag()
        
        