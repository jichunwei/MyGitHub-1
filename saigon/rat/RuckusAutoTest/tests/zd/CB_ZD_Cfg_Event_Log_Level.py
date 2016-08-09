'''
2014-09-03
Author: chen.tao@odc-ruckuswireless.com
Description:
To set event log level to high,medium and low.
It is medium by default.
'''
from RuckusAutoTest.models import Test
class CB_ZD_Cfg_Event_Log_Level(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):        

        try:
            self.zd.set_event_log_level(log_level = self.conf['log_level'])
            self.passmsg = 'Set event log level to %s successfully'%self.conf['log_level'] 
        except Exception, e:
            self.errmsg = 'Failed to set event log level to %s'%self.conf['log_level']
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:        
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):

        self.conf = {'log_level':'high'
                     }
        self.conf.update(conf)        
        if conf.get('zd_tag'):
            self.zd = self.carrierbag[conf.get('zd_tag')]
        else:
            self.zd = self.testbed.components['ZoneDirector']     
        self.errmsg = ''
        self.passmsg = ''
        
