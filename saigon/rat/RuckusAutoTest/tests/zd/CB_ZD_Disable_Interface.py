import logging
from RuckusAutoTest.models import Test

class CB_ZD_Disable_Interface(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        logging.info('Disable Standby ZD interface %s' % self.interface)
        self.sw.disable_interface(self.interface)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
       
        self._update_carrierbag()
        msg = 'The Switch interface[%s] was disable' % self.interface
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         )
        
        self.conf.update(conf)
        self.sw = self.carrierbag['sw']
        self.interface = self.carrierbag['interface']
        
    def _update_carrierbag(self):
#        self.carrierbag['interface'] = self.interface
        pass