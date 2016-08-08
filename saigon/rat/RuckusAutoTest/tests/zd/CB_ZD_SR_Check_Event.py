
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd

class CB_ZD_SR_Check_Event(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.check_event_log()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'There are Event Log about %s' % self.find_string
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.find_string = conf['find_string']
        

    def check_event_log(self):
        self.zd1.navigate_to(self.zd1.ADMIN, self.zd1.ADMIN_PREFERENCE)
        self.events_log1 = self.zd1.get_events()
        self.zd2.navigate_to(self.zd2.ADMIN, self.zd2.ADMIN_PREFERENCE)
        self.events_log2 = self.zd2.get_events()
        
        redundancy_zd.check_events(self.events_log1,self.find_string)
        redundancy_zd.check_events(self.events_log2,self.find_string)
       
