"""
chen.tao 2015-01-06
"""

import logging

from RuckusAutoTest.models import Test

class CB_SW_Destroy_All_Isolate_Groups(Test):
    required_components = ['L3Switch']
    parameter_description = {}

    
    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        try:
            self.switch.delete_all_port_isolate_groups()
            all_isolate_groups_after_del = self.switch.get_all_port_isolate_groups()
        except Exception, ex:
            self.errmsg = ex.message
        if all_isolate_groups_after_del:
            logging.info('The following isolate groups are not deleted:\n%s'%all_isolate_groups_after_del)
            self.errmsg += 'Not all isolate groups are deleted.'
        else:
            self.passmsg += 'All isolate groups are deleted.'
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        
        self.switch = self.testbed.components["L3Switch"]