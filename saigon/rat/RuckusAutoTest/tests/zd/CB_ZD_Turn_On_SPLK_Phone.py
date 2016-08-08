import logging
import libZD_TestMethods_v8 as tmethod8

from RuckusAutoTest.models import Test
from RuckusAutoTest.scripts.zd import spectralink_phone_config as splk_cfg

class CB_ZD_Turn_On_SPLK_Phone(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._turn_on_phone()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        msg = "The SPLK Phone [%s] is turned on successfully" %\
              (self.phone)
              
        return self.returnResult("PASS", msg)
        
    def cleanup(self):
        pass
    
    def _cfgInitTestParams(self, conf):
        self.conf = dict(phone='')
        self.conf.update(conf)
        self.errmsg = ''
        self.phone = self.conf['phone']
        self.push_dev = self.testbed.components['PushKeypadDevice']        
        self.pwr_key =splk_cfg.get_ph_cfg(self.phone)['pwr_key']
        
    def _turn_on_phone(self):
        try:
            self.push_dev.turn_on_phone(self.pwr_key)
            tmethod8.pause_test_for(30, 'Wait for Phone[%s] booting' % self.phone)
        except Exception, e:
            logging.info("Error [%s] when turn on phone [%s]" %(e.message, self.phone))
            self.errmsg = e.message
