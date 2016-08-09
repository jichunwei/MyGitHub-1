# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Alarm_Mail testscript uses to verify the Alarm setting option of Zone Director,
             if it generate an alarm email when it have an alarm or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on Zone Director

   Required components: 'ZoneDirector'
   Required environment: Must be have an noisy environtment when running the script.
   Test parameters: 'mail_to' : the email address that we want ZD sent out an alarm email to.

   Result type: PASS/FAIL
   Results: PASS: If when there is an alarm be trigger on the ZD, the ZD also sent out an
                  alarm email appropriate with.
            FAIL: If the alarm email is not be sent out.
            ERROR: When the test not complete because there on alarm generate during the test

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Config the Alarm setting option on ZD to apply the Email address and the Mail Server IP Address
   2. Test procedure:
       - Clear all alarms on the ZD
       - Clear all amil on the server
       - Try to generate an alarm on the ZD
       - Check if there is any alrm on ZD or not.
       - If there are alarms on ZD, read all amail have on mail server and
       check if there are appropriate alarm email or not.
   3. Cleanup:
       - Clear an uncheck to disable Alarm Settings.

    How it was tested:
        1. Stop the mailserver and run the script,
        the result must be fail because the no mail could save on the server.
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP

class ZD_System_Alarm_Mail(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.timeout = conf['timeout']
        # Telnet to Mail server
        # PHANNT@20100525:
        # re-use components['LinuxServer'] instead of creating a new one
        self.mail_server = self.testbed.components['LinuxServer']
        self.mail_server.re_init()
        logging.info('Telnet to the Mail server at IP address %s successfully' % \
                     self.mail_server.ip_addr)

        # Telnet to the AP is not be managed by ZD but will be the Rogue AP
        self.flag = False
        if conf.has_key('rogue_AP'):
            self.ap = RuckusAP(conf['rogue_AP'])
            self.flag = True

        # Config 'Alarm Setting' option on the ZD
        self.mail_to = conf['email_to']
        self.mail_from = '%s@%s' % (self.zd.username,
                                    self.zd.get_system_name())
        self.zd.set_alarm_email(self.mail_to, self.mail_server.ip_addr)

    def test(self):
        # Clear all Alarms all the ZD
        self.zd.clear_all_alarms()
        # Clear all Email on the Mail server
        self.mail_server.delete_all_mails()

        # Config to genarate an 'Rogue AP Detected' alarm to make sure at lease we have 1 alarm before timeout
        logging.info('Generating some Alarm on the ZD')
        test_ssid = 'Alarm_Email_Test'
        self.zd.remove_all_wlan()
        self.zd.cfg_wlan({'ssid': test_ssid, 'auth':'open', 'encryption':'none',
                          'wpa_ver':'', 'key_string':'', 'key_index':''})

        if self.flag:
            self.ap.set_ssid('svcp', test_ssid)
            self.ap.set_state('svcp', 'up')

        # Get the Alarms list on the ZD
        alarms_list = []
        t1 = time.time() # Record the time before get date time information from the device
        t2 = time.time() - t1

        logging.info('Getting Alarms information on the ZD')
        while len(alarms_list) < 1 and t2 < self.timeout:
            alarms_list = self.zd.get_alarms()
            time.sleep(10)
            t2 = time.time() - t1

        if len(alarms_list) < 1:
            return 'ERROR', 'Test case has not completed. There is no Alarm generated within %s s'\
                   % repr(self.timeout)

        else:
            alarms_info = [[self.mail_from, self.mail_to, i[1], i[3]] for i in alarms_list]
            logging.info('Read mail from mail server')
            time.sleep(60)
            alarms_mail = self.mail_server.read_mails()

            logging.info('Checking if the ZD sent out appropriate alarm email or not')
            for i in alarms_info:
                if i not in alarms_mail:
                    result, message = 'FAIL', 'The ZD did not generate an alarm email about \'%s\' alarm' % i[3]

                else:
                    result, message = 'PASS', ''

            return result, message

    def cleanup(self):
        # Clear the 'Alarm Setting' on the AP
        self.zd.set_alarm_email(' ', ' ', False)
        try:
            self.ap.close()

        except:
            pass

        logging.info('Cleaning up the testing environment successfully')

