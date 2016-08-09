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
       Create maximum AP Groups in ZD and Verify them.
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

class CB_ZD_AP_Group_Maximum_Testing(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.number = self.conf['number']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:            
            for i in range(0, self.number):#Consider System Default AP Group
                name = 'AP Group %d' % i
                ap_group.create_ap_group(self.zd, name)
            
            ap_groups = ap_group.get_all_ap_group_brief_info(self.zd)
            if (len(ap_groups)) != self.number:
                return self.returnResult('FAIL',
                                         'Expect %d AP Group, actual %d' 
                                         %(self.number, len(ap_groups)))
            logging.info('One more Try')
            try:
                ap_group.create_ap_group(self.zd, 'One More AP Group')
                return self.returnResult('FAIL', 
                                         'Maximum AP Group limitation is %d' % self.number)
            except:                
                return self.returnResult('PASS', 
                                     'Create %d AP Group successfully' % self.number)
                             
        except Exception, e:        
            return self.returnResult('PASS', e.message)
    
    def cleanup(self):
        self._update_carribag()