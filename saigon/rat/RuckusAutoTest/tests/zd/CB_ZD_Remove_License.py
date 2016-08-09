'''
Description:Remove license from ZD WEBUI.
Created on 2010-9-21
@author: cwang@ruckuswireless.com 
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_License(Test):
    '''
    Remove license from ZD WEBUI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            lib.zd.lic.remove_permanent_license(self.zd, self.license_feature)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        self._update_carrier_bag()
        
        return self.returnResult('PASS', 'Remove license [%s] successfully' % self.license_feature)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(license_feature = '')
        self.conf.update(conf)
        self.license_feature = self.conf['license_feature']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
    
