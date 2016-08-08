import time
import logging
import libZD_TestMethods_v8 as tmethod8

from RuckusAutoTest.models import Test
from RuckusAutoTest.scripts.zd import spectralink_phone_config as splk_cfg

class CB_ZD_Turn_Off_SPLK_Phone(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._turn_off_phone()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        msg = "The SPLK Phone [%s] is turned off successfully" %\
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
        self.pwr_key = self.end_key = splk_cfg.get_ph_cfg(self.phone)['pwr_key']
        self.send_key = splk_cfg.get_ph_cfg(self.phone)['send_key']
              
    def _turn_off_phone(self):
        try:
            logging.info('push end key of phone [%s] to stop traffic' % self.phone )
            self.push_dev.push_end_key(self.end_key)
            time.sleep(3)
            logging.info('turn off phone [%s]' % self.phone)
            self.push_dev.turn_off_phone(self.pwr_key)
        except Exception, e:
            logging.info("Error [%s] when turn off phone [%s]" % (e.message, self.phone))
            self.errmsg = e.message
