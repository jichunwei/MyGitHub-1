'''
Description:Set NTP configuration.
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test


class CB_ZD_Set_NTP_Setting(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        self.zd.cfg_ntp(self.ntp_server)
        self.ntp_cfg = self.zd.get_ntp_cfg()
        self._update_carrier_bag()
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_ntp_cfg'] = self.ntp_cfg
    
    def _init_test_params(self, conf):
        self.conf = dict(ntp_server = '192.168.0.252')
        self.conf.update(conf)
        self.ntp_server = self.conf['ntp_server']
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
