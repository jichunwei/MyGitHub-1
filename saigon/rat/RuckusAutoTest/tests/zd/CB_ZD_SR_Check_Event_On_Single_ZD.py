
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd

class CB_ZD_SR_Check_Event_On_Single_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if self.zd_type == 'active':
            self.check_event_log_on_single_zd(self.active_zd)
        
        else:
            self.check_event_log_on_single_zd(self.standby_zd)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'There are Event Log about %s' % self.find_string
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         zd_type = 'active'
                         )
        
        self.conf.update(conf)
        self.zd_type = self.conf['zd_type']
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        self.find_string = self.conf['find_string']
        

    def check_event_log_on_single_zd(self,zd):
        zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)
        events_log = zd.get_events()
#        self.zd2.navigate_to(self.zd2.ADMIN, self.zd2.ADMIN_PREFERENCE)
#        self.events_log2 = self.zd2.get_events()
#        
        redundancy_zd.check_events(events_log,self.find_string)
#        redundancy_zd.check_events(self.events_log2,self.find_string)
       
