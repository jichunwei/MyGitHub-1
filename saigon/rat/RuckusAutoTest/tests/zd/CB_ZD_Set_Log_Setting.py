'''
Description:
Created on 2010-10-27
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Set_Log_Setting(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        try:
            lib.zd.sys.set_syslog_info(self.zd, self.conf)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
                
        self.log_setting = lib.zd.sys.get_syslog_info(self.zd)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Set log setting correctly')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_log_setting_cfg'] = self.log_setting 
    
    def _init_test_params(self, conf):
        self.conf = dict(log_level = 'show_more', #'warning_and_critical' | 'critical_events_only'
                         enable_remote_syslog = True, # False
                         remote_syslog_ip = '192.168.0.250',)
         
        self.conf.update(conf)       
        self.zd = self.testbed.components['ZoneDirector']            
        self.errmsg = ''
        self.passmsg = ''