 # Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description:
   ZD_System_NTP testscript uses to verify if the 'Use NTP to synchronize the ZoneDirector clock automatically'
   option working or not. This script use for both ZD side and AP side.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 'target_ap': mac address of the AP will be test at the AP side.

   Result type: PASS/FAIL
   Results: PASS: If the datetime on the ZD or AP can synchronize with the NTP server.
            FAIL: If the datetime on the ZD or AP can not synchronize with the NTP server.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Apply the NTP server ipadress for the ZD
       - Change the datetime on the NTP server
   2. Test procedure:
       - Refresh the time on the ZD
       - Check the time on the ZD if it be synchronized correctly or not.
       - In case test for AP side, we check more if the AP get the time on the ZD or not.
   3. Cleanup:
       - Return the datetime on the NTP server
       - Return the default NTP server info on the ZD and refesh the datime on it.

    How it was tested:
        1. Stop the NTP server, make sure the test must be Fail because the NTP server not working
        2. During the test, login and change the date time on NTP server after the ZD synchronized the time.
        3. We have the bug 5631, to verify the script on the test for AP side
"""

import time
import random
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

zd_datetime_format = '%A, %B %d, %Y %I:%M:%S %p'

class ZD_System_NTP(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']

        # Telnet to NTP server
        self._init_NtpServer()

        # Telnet to the AP
        self._init_Ap(conf)

        # Config date time on the ntp server
        self._cfg_Time()

        # Config on the ZD (DUT)
        self._cfg_Zd()


    def test(self):
        t1 = time.time() # Record the time before get date time information from the device
        if self.flag:
            logging.info('Current time on the NTP server: %s' % self.ntp.get_system_time())
            self.ntp.cmd('')
            logging.info('Synchronize date time on the ZoneDirector: %s' %
                         self.zd.get_current_time())
            dv_time_str = self.ap.get_time()
            logging.info('Get the GMT time on the AP: %s' % dv_time_str)
            ntp_time_str = self.ntp.get_gmt_time()
            logging.info('Get the GMT time on the NTP server: %s' % ntp_time_str)
            dv_time = time.mktime(time.strptime(dv_time_str))

        else:
            dv_time_str = self.zd.get_current_time()
            logging.info('Get the current time on the ZD: %s' % dv_time_str)
            ntp_time_str = self.ntp.get_system_time()
            logging.info('Get the system time on the NTP server: %s' % ntp_time_str)
            dv_time = time.mktime(time.strptime(dv_time_str, zd_datetime_format))

        # Record the time before get date time information from the NTP server
        t2 = time.time()
        ntp_time = time.mktime(time.strptime(ntp_time_str))

        # Compare the different time between ZD/AP and NTP server
        dif = abs(dv_time - ntp_time)
        if dif < (t2 - t1):
            return 'PASS', ''

        else:
            return 'FAIL', 'Ruckus Device\'s time: %s. There are %d second(s) \
                   difference from NTP server\'s time: %s'\
                   % (dv_time_str, dif, ntp_time_str)

    def cleanup(self):
        logging.info('Clean up the testing environment...........................')
        try:
            # Set the date time on NTP server base on the current time on the test engine
            # and close the telnet session of NTP server.
            self.ntp.set_date_time(time.strftime('%m%d%H%M%y', time.localtime(time.time())))
            self.ntp.close()
            logging.info('Restore date time on NTP server successfully')
            # Return the cofig on the ZD (DUT)
            self.zd.cfg_ntp(self.ntp_bkup)
            self.zd.get_current_time(True)
            logging.info('Restore NTP config on ZD successfully')

        except:
            self.zd.get_current_time(True)
            logging.info('Cleanup testing environment is not completely')

    def generateSTime(self):
        """
        Generate an random time value follow the format: MMDDHHmmYY
        """
        return '%02d%02d%02d%02d%02d' \
               % (random.randint(1, 12), random.randint(1, 30), random.randint(0, 23),
                  random.randint(0, 59), random.randint(0, 37))

    def _init_NtpServer(self):
        # PHANNT@20100525:
        # re-use components['LinuxServer'] instead of creating a new one
        self.ntp = self.testbed.components['LinuxServer']
        self.ntp.re_init()
        logging.info('Telnet to the NTP server at IP address %s successfully' % \
                     self.ntp.ip_addr)


    def _init_Ap(self, conf):
        self.flag = False
        if conf.has_key('target_ap'):
            self.ap = tconfig.get_testbed_active_ap(self.testbed, conf['target_ap'])
            if self.ap:
                self.flag = True
                logging.info('Telnet to the AP (%s) under ZD successfully' % conf['target_ap'])

            else:
                raise Exception('Target AP %s not found' % conf['target_ap'])

    def _cfg_Time(self):
        try:
            a = self.generateSTime()
            self.ntp.set_date_time(a)
            self.ntp.cmd('')
            time_config = self.ntp.get_system_time()
            logging.info('Setting the date time on NTP server to %s successfully' % time_config)

        except:
            raise Exception('Error during set the date time on the NTP server')

    def _cfg_Zd(self):
        self.ntp_bkup = self.zd.get_ntp_cfg()
        self.zd.cfg_ntp(self.ntp.ip_addr)
        logging.info('Config the  NTP server info on ZD to %s successfully' % self.ntp.ip_addr)

