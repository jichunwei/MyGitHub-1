"""
Description: This script is used to get all wlan information from zd cli.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.configure_alarm import enable_alarm_event
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZDCLI_Enable_Alarm_Event(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        enable_alarm_event(self.zdcli,self.event) 
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.conf={'event':[]}
        self.conf.update(conf)
        self.event=self.conf['event']
        self.errmsg = ''
        self.passmsg = 'enable alarm event %s successfully'%self.event

        
        