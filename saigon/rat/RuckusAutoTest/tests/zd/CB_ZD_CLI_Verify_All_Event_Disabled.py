'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure alarm in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_alarm


class CB_ZD_CLI_Verify_All_Event_Disabled(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifi_all_alarm_disabled()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _verifi_all_alarm_disabled(self):
        try:
            res = configure_alarm.all_alarm_event_disable(self.zdcli)
            if res:
                self.passmsg = 'all alarm disabled'
            
            else:
                self.errmsg = 'not all of the alarm disabled'
            
        except Exception, ex:
            self.errmsg = ex.message
            
            