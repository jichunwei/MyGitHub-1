'''
Description: Get NTP Setting from ZD GUI.
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

class CB_ZD_Get_NTP_Setting(Test):
    '''
    Get NTP Setting from ZD GUI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.ntp_setting = self.zd.get_ntp_cfg()
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Get NTP Setting from GUI successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_ntp_cfg'] = self.ntp_setting
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
