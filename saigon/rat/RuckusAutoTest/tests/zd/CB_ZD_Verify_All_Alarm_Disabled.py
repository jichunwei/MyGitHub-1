'''
@author: west.li@ruckuswireless.com

Description: disable all alarm by web UI

'''


import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import alarm_setting_zd


class CB_ZD_Verify_All_Alarm_Disabled(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        result,msg=alarm_setting_zd.all_email_event_disabled(self.zd)
        if not result:
            self.errmsg=msg
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = 'all alarm event disabled'
            
        
        