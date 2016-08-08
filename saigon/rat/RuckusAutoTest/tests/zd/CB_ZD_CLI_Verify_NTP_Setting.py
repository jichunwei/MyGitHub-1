'''
Description:
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test

class CB_ZD_CLI_Verify_NTP_Setting(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self._update_carrier_bag()
        
        return self.returnResult('PASS', 'NTP Setting checking is correct')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_ntp_cfg = self.carrierbag['existed_ntp_cfg']
        self.cli_sys_cfg_info = self.carrierbag['existed_zdcli_sys_cfg_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
