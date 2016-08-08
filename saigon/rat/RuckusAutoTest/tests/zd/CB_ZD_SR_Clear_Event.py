
from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.ZoneDirector import ZoneDirector

class CB_ZD_SR_Clear_Event(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.clear_event_log()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'Clear Event log successfully '
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
    def clear_event_log(self):
        self.zd1.clear_all_events()
        self.zd2.clear_all_events()
   
