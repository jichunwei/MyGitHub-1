'''
verify session timeout via web UI
by west.li
@2012.4.9
'''

from RuckusAutoTest.models import Test
import logging

class CB_ZD_Verify_Session_Timeout(Test):

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        time_out=self.zd.get_session_timeout()
        logging.info('timeout value get from zd web UI is %s'%time_out)
        if self.expected_timeout_value==time_out:
            return ('PASS', 'the timeout value get from zd web UI is the same as expected(%d)'%time_out)
        else:
            return ('FAIL', 'the timeout value get from zd web UI(%d) is not the same as expected(%d)'%(time_out,self.expected_timeout_value))

    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('session_time_out'):
            self.expected_timeout_value=self.carrierbag['session_time_out']
        if self.conf.has_key('session_timeout'):
            self.expected_timeout_value=self.conf['session_timeout']
        logging.info('expected timeout value is %s'%self.expected_timeout_value)
        
        self.errmsg = ''
        self.passmsg = ''


