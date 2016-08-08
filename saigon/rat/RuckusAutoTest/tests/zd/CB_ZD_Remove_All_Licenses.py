'''
Description:Remove all of licenses from ZD WEBUI.
Created on 2010-9-21
@author: cwang@ruckuswireless.com    
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_All_Licenses(Test):
    '''
    Remove all of licenses from ZD WEBUI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:                    
            lib.zd.lic.remove_all_permanent_licenses(self.zd)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        self._update_carrier_bag()
        
        return self.returnResult('PASS', 'All of licenses have been removed successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
