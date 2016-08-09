'''
@author: west.li@ruckuswireless.com

Description: enable a list of alarm by web UI

'''


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import alarm_setting_zd


class CB_ZD_Enable_Alarm(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._enable_alarm()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.alarm_list=conf['alarm_list']
        self.errmsg = ''
        self.passmsg = ''

    def _enable_alarm(self):
        logging.info('disable all alarm in zd %s'%self.zd.ip_addr)
        try:
            alarm_setting_zd.enable_email_event_alarm(self.zd,self.alarm_list)
            msg="enable email alarms %s successfully"%self.alarm_list
            logging.info(msg)
            self.passmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
            
        
        