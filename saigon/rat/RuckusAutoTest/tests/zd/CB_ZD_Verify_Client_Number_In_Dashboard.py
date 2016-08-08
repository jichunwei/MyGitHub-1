'''
by west
verify the client number is correct in dashboard
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import dashboard_zd

class CB_ZD_Verify_Client_Number_In_Dashboard(Test):
    '''
    Get system devices info from ZD's GUI dash board.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        device_info = dashboard_zd.get_devices_info(self.zd)
        sta_number=device_info['num-client']
        if not str(self.conf['sta_number'])==str(sta_number):
            self.errmsg='sta number error:%s instead of %s'%(sta_number,self.conf['sta_number'])
        self._update_carrier_bag()
        if self.errmsg:
            self.returnResult('FAIL',self.errmsg)
        return self.returnResult('PASS', 'sta number is correct')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'sta_number':'',}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
