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
       Checking 'System Default' AP Group can't delete.   
       Checking 'System Default' AP Group name can't change.          
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

class CB_ZD_AP_Group_System_Default_Testing(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'default_name':'System Default'}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.default_name = self.conf['default_name']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self.passmsg = ''
        self.errmsg = ''
    
    def test(self):
        #Try to delete 'system default' ap group
        try:
            ap_group.delete_ap_group_by_name(self.zd, self.default_name)
            return self.returnResult('FAIL',
                                    '[Incorrect behavior] System Default AP Group have been deleted')
        except Exception, e:
            if 'The default AP group cannot be deleted' in e.message:
                self.passmsg += '[Correct behavior] %s' % e.message
            else:
                return self.returnResult('FAIL', 
                                         '[Incorrect behavior]Expected result:\
                                         The default AP Group cannot be deleted,\
                                          Actual result%s' % e.message)
        
        #Try to update name of 'system default'.
        try:
            ap_group.update_ap_group_name(self.zd, self.default_name, 'new_name')
            return self.returnResult('FAIL', 
                                     '[Incorrect behavior] System Default AP Group name can change')
        except Exception, e:
            self.passmsg += ',[Correct behavior] %s' % e.message
            
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        self._update_carribag()