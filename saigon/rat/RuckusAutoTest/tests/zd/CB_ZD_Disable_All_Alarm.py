'''
@author: west.li@ruckuswireless.com

Description: disable all alarm by web UI

'''


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import alarm_setting_zd


class CB_ZD_Disable_All_Alarm(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._disable_all_alarm()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _disable_all_alarm(self):
        logging.info('disable all alarm in zd %s'%self.zd.ip_addr)
        try:
            alarm_setting_zd.disable_all_email_event_alarm(self.zd)
            logging.info("disable all email alarm successfully")
            self.passmsg = 'disable all email alarm successfully'
            
        except Exception, ex:
            self.errmsg = ex.message
            
        
        