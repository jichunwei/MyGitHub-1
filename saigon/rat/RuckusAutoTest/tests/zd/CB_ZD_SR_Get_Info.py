'''
Description:
louis.lou@ruckuswireless.com
get Smart Redundancy information on ZD GUI
    
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd as sr
class CB_ZD_SR_Get_Info(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
                
        self.sr_info_on_zd = sr.get_sr_info(self.zd)
        self._update_carrier_bag()
        self.passmsg = 'SR info on ZD: %s' % self.sr_info_on_zd
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['sr_info_on_zd'] = self.sr_info_on_zd
    
    def _init_test_params(self, conf):
        self.conf = dict(zd = 'zd1')
        self.conf.update(conf)
        self.zd = self.carrierbag[self.conf['zd']]        
        self.errmsg = ''
        self.passmsg = ''
    
