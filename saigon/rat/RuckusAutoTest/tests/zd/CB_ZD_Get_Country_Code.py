'''
Description:
Created on 2010-11-5
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test

class CB_ZD_Get_Country_Code(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.country_code = self.zd.get_country_code()
        self._update_carrier_bag()        
        return self.returnResult('PASS', 'Get country code information successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_country_code'] = self.country_code 
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
