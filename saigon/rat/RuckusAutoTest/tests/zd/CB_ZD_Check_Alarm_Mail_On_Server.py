"""
Description: check expected msg in the mail box or not
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import alarm_setting_zd as asz


class CB_ZD_Check_Alarm_Mail_On_Server(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAlarmMailOnServer()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'mail_folder': '/home/lab/Maildir/new/',
                     'mail_to': 'lab@example.net',
                     'is_test_mail': False,
                     'time_out': 600,
                     'expected_msg':''}
        self.conf.update(conf)
        if self.carrierbag.has_key('activity_str'):
            self.conf['expected_msg']=self.carrierbag['activity_str']
        self.mail_server = self.testbed.components['LinuxServer']
        self.mail_server.re_init()
        logging.info('Telnet to the mail server at IP address %s successfully' % \
                     self.mail_server.ip_addr)
        self.passmsg = ''
        self.errmsg = ''
        
    def _verifyAlarmMailOnServer(self):
        try:
            res, msg = asz.check_alarm_mails_on_server(self.mail_server, self.conf['expected_msg'], 
                                                        self.conf['mail_folder'], self.conf['is_test_mail'],
                                                        self.conf['time_out'])
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
        
        except Exception, ex:
            self.errmsg = ex.message

