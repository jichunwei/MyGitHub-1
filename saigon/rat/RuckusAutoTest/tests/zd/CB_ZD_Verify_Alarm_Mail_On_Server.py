"""
Description: This combo test is used to verify alarm mail on mail server  
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Linux Server
Input: 
    - N/A
Output: 
    - PASS: If mailbox on server received alarm mail from Zone Director 
    - FAIL: If mailbox on server did not receive any alarm mail from Zone Director 
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import alarm_setting_zd as asz


class CB_ZD_Verify_Alarm_Mail_On_Server(Test):
    
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
                     'time_out': 300}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.mail_server = self.testbed.components['LinuxServer']
        self.mail_server.re_init()
        logging.info('Telnet to the mail server at IP address %s successfully' % \
                     self.mail_server.ip_addr)
        self.passmsg = ''
        self.errmsg = ''
        
    def _verifyAlarmMailOnServer(self):
        try:
            res, msg = asz.verify_alarm_mails_on_server(self.zd, self.mail_server, self.conf['mail_to'], 
                                                        self.conf['mail_folder'], self.conf['is_test_mail'],
                                                        self.conf['time_out'])
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
        
        except Exception, ex:
            self.errmsg = ex.message

