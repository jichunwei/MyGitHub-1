'''
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_interface as lib

class CB_ZD_Get_Mgmt_Interface(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        
        try:
            self.mgmt_if_info_zd = lib.get_mgmt_inf(self.zd)
        except Exception, e:
            self.errmsg = "Get Mgmt interface FAIL [%s]" % e.message
            logging.warning(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
             
        self._update_carrier_bag()
        self.passmsg = self.mgmt_if_info_zd
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['mgmt_if_info_zd'] = self.mgmt_if_info_zd
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
