'''
verify session timeout via zdcli
by west.li
@2012.4.9
'''

import time
from RuckusAutoTest.models import Test
import logging

class CB_ZDCLI_Verify_Session_Timeout(Test):

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        self.zdcli.do_shell_cmd('',set_session_timeout=False)
        time_out=self.zdcli.get_session_timeout()
        logging.info('timeout value get from zdcli is %s'%time_out)
        if self.expected_timeout_value==time_out:
            return ('PASS', 'the timeout value get from zdcli is the same as expected(%d)'%time_out)
        else:
            return ('FAIL', 'the timeout value get from zdcli(%d) is not the same as expected(%d)'%(time_out,self.expected_timeout_value))

    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.expected_timeout_value=self.carrierbag['session_time_out']
        logging.info('expected timeout value is %s'%self.expected_timeout_value)
        self.errmsg = ''
        self.passmsg = ''


