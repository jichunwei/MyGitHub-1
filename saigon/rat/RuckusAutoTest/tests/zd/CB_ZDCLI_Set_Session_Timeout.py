'''
set session timeout via zdcli
by west.li
@2012.4.9
'''

import time
from RuckusAutoTest.models import Test
import logging

class CB_ZDCLI_Set_Session_Timeout(Test):

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        if not self.conf.has_key('session_timeout'):
            time_out=int(time.time())%1431+10
        else:
            time_out=self.conf['session_timeout']
        logging.info('time out value to set:%s'%time_out)
        result,msg=self.zdcli.set_session_timeout(time_out)
        if result:
            if time_out>0 and time_out<1441:
                self.carrierbag['session_time_out']=time_out
            return ('PASS', msg)
        else:
            return ('FAIL', msg)

    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''


