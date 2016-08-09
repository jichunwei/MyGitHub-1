
from RuckusAutoTest.models import Test

class CB_ZD_SR_Clear_Up(Test):
    """
    
    shut down and delete ZD2
    """
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'Clear Up the Smart Redundancy Test environment'
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        try:
#            self.zd2.close()
            pass
        except:
            pass
#        self.zd2.s.stop()        
#        del(self.zd2)
        

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
