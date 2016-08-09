"""
Description: This combo test is used to cleanup all mail on server mail 
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Linux Server
Input: 
    - mail_folder: path to mail folder on Mail Server (Linux) 
Output: 
    - PASS: If all mails in mailbox can delete successful.
    - FAIL: If any mail in mailbox can not delete because of permission or error. 
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from copy import deepcopy
import logging


class CB_ZD_Clear_Alarm_MailBox(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        i=10
        while(i>0):
            i=i-1
            logging.info("Delete all email from mail server")
            self.mail_server.delete_all_mails(self.conf['mail_folder'])

            if len(self.mail_server.get_mails_list(self.conf['mail_folder'])) == 0: 
                self.passmsg = 'All mail on server deleted successful.' 
                return self.returnResult('PASS', self.passmsg)
            
        self.errmsg = "some mail on mailbox can not removed"
        return self.returnResult("FAIL", self.errmsg) 

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':120,
                     'mail_folder': '/home/lab/Maildir/new/'}
        self.mail_server = self.testbed.components['LinuxServer']

        self.mail_server.re_init()
        logging.info('Telnet to the Mail server at IP address %s successfully' % \
                     self.mail_server.ip_addr)
