'''
Remove AP Group with given AP name
Created on 2011-11-3
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group


class CB_ZD_Remove_AP_Group(Test):

    def config(self, conf):
        self.conf = {'name':'AP_Group_Test'}
        self.conf.update(**conf)
        self.name = self.conf['name']
        self.zd = self.testbed.components['ZoneDirector']
    
    
    def test(self):
        try:
            rows = ap_group.query_ap_group_brief_info_by_name(self.zd, 
                                                              self.name)
            if not rows:
                return self.returnResult("PASS", 
                                         "AP Group %s hasn't been found" % self.name)
                
            ap_group.delete_ap_group_by_name(self.zd, self.name)
            return self.returnResult('PASS', 'AP Group %s deleted' % self.name)
        
        except Exception, e:
            return self.returnResult('FAIL', 'Failure Delete AP Group %s' % self.name)
    
        
    def cleanup(self):
        pass

