'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure alarm in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_alarm


class CB_ZD_CLI_Configure_Alarm(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._configureAlarm()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.alarm_cfg = conf['alarm_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _configureAlarm(self):
        try:
            res, msg = configure_alarm.configure_alarm(self.zdcli, self.alarm_cfg)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
            
            