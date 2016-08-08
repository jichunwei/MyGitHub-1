# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Syslog testscript uses to test the 'Log Settings' option in case we use an externel Syslog server.
             It will verify the syslog is record on the syslog server or not on both ZD side and AP side.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 'target_ap': mac address of the AP will be test at the AP side.

   Result type: PASS/FAIL
   Results: PASS: If the syslog is recorded on both Ruckus device (ZD or AP) and syslog server.
            FAIL: If the syslog is not recorded on the syslog server or is recorded wrong.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Apply the Syslog server IP adrress on the ZD to use this server.
   2. Test procedure:
       - Excute some actions on the ZD (or AP at AP side) to generate the syslog events.
         (In this testscript I try to create a new wlan and change state of use 'http' option of AP)
       - Get the syslog events on the ZD (or AP).
       - Get the syslog messages on the server.
       - Verify if the syslog events on ruckus devide is recorded on the syslog server is correctly or not.
   3. Cleanup:
       - Return the default of 'Log Settings' option.

    How it was tested:
        1. Disable syslog server and check the test result. It must be Fail in this case.
        2. Clear all syslog on the server after the sript get syslog events be created.
        Test result must be Fail in this case.
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components.lib.zd import system_zd


zd_time_format = '%Y/%m/%d %H:%M:%S'
log_time_format = '%b  %d %H:%M:%S %Y'

class ZD_System_Syslog(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        # Telnet to Syslog server
        self._initSyslogServer()

        # Find out the AP under test
        self._initAp(conf)

        # Config the Syslog settings on the ZD
        self.zd.cfg_syslog_server(True, self.syslog_server.ip_addr, 'high')
        logging.info('Setting the syslog server ipadress to: %s successfully' % \
                     self.syslog_server.ip_addr)

    def test(self):
        # Update time on the testing device
        run_time = time.time()
        self.syslog_server.cmd('')
        syslog_ser_current_time = self.syslog_server.get_system_time()
        self.syslog_server.cmd('')
        syslog_ser_time = time.mktime(time.strptime(syslog_ser_current_time))
        syslog_year = syslog_ser_current_time.split()[-1]

        zd_current_time = self.zd.get_current_time()
        zd_time = time.mktime(time.strptime(zd_current_time, '%A, %B %d, %Y %I:%M:%S %p'))
        self.zd.remove_all_wlan()

        self.syslog_server.clear_syslog_messages()
        logging.info('Clear all syslog on the syslog server successfully')

        self.zd.clear_all_events()
        logging.info('Clear all events on the ZD successfully')

        if self.flag:
            if '  Server IP         : %s' % self.syslog_server.ip_addr in self.ap.get_syslog('info'):
                ap_year = self.ap_current_time.split()[-1]
                self.ap.cfg_syslog('disable')
                self.ap.cfg_syslog('enable')
                logging.info('Cleanup and enable syslog on AP successfully')

                # Setting option http on AP to genarate log
                self.ap.cmd('set http enable')
                self.ap.cmd('set http disable')
                logging.info('Genarate log on the AP successfully')
                time.sleep(10)

                ap_log = self.ap.get_syslog('log')
                logging.info('Get syslog on the AP successfully: %s' % repr(ap_log))
                time.sleep(90)

                ser_log = self.syslog_server.get_syslog_messages_from(' %s ' % self.ap.ip_addr)
                logging.info('Get syslog for the AP (%s) on the Syslog server successfully: %s'\
                             % (self.ap.ip_addr, repr(ser_log)))

                logging.info('Analizing syslog data ....................................................')
                dv_log = [[time.mktime(time.strptime(i.split('RuckusAP')[0] + ap_year, log_time_format)), \
                           i.split('RuckusAP')[1].split(': ')[1]] for i in ap_log if ': ' in i]
                sys_log = [[time.mktime(time.strptime(i.split('%s' % self.ap.ip_addr)[0] + syslog_year, log_time_format)), \
                            i.split('%s' % self.ap.ip_addr)[1].split(': ')[1]] for i in ser_log \
                            if ': ' in i.split('%s' % self.ap.ip_addr)[1]]

            else:
                return 'FAIL', 'Syslog info on the AP: %s is not correct with syslog server: %s' \
                       % (self.ap.get_syslog('info')[2], self.syslog_server.ip_addr)

        else:
            # Create a new wlan to genarate log on the ZD
            self.zd.cfg_wlan(\
                {'ssid':'Syslog_Test', 'auth':'open', 'encryption':'none', 'wpa_ver':'', 'key_string':'', 'key_index':''})
            logging.info('Genarate log on the ZD successfully')

            zd_log = self.zd.get_events()
            logging.info('Get all events on the ZD successfully: %s' % repr(zd_log))
            time.sleep(120)
            ser_log = self.syslog_server.get_syslog_messages_from('%s syslog:' % self.zd.ip_addr)
            logging.info('Get syslog for the ZD (%s) on the Syslog server successfully: %s'\
                         % (self.zd.ip_addr, repr(ser_log)))

            logging.info('Analizing syslog data ....................................................')
#            ver = self.zd.get_version()
#            if ver.startswith('9.0') or ver.startswith('9.1'):
#                tmp = 'syslog: '
#            else:
#                tmp = 'syslog: eventd_to_syslog():'
                
#            tmp = system_zd.get_sys_log()
            tmp = "syslog: "
            dv_log = [[time.mktime(time.strptime(i[0], zd_time_format)), i[3]] for i in zd_log]
            sys_log = [[time.mktime(time.strptime(i.split('%s %s'\
#            sys_log = [[time.mktime(time.strptime(i.split('%s syslog: '\
#            sys_log = [[time.mktime(time.strptime(i.split('%s syslog: eventd_to_syslog():'\
                        % (self.zd.ip_addr, tmp))[0] + syslog_year, log_time_format)), \
#                        i.split('%s syslog: ' % self.zd.ip_addr)[1]] for i in ser_log]
#                        i.split('%s syslog: eventd_to_syslog():' % self.zd.ip_addr)[1]] for i in ser_log]
                        i.split('%s %s' % (self.zd.ip_addr, tmp))[1]] for i in ser_log]

        logging.info('Comparring syslog data ....................................................')
        dv_log_times = [i[0] for i in dv_log]
        dv_log_events = [i[1] for i in dv_log]
        sys_log_times = [i[0] for i in sys_log]
        sys_log_events = [i[1].strip() for i in sys_log]

        result = 'PASS'
        comment = ''

        run_time = time.time() - run_time
        print run_time

        while result == 'PASS':
            if self.flag:
                for i in dv_log_times:
                    if self.ap_time - i > run_time:
                        result, comment = 'FAIL', 'The log time recorded on the AP (%s) is not correct (now is: %s)'\
                              % (time.ctime(i), self.ap_current_time)
                        break
                if result == 'FAIL': break

                for i in sys_log_times:
                    if syslog_ser_time - i > run_time:
                        result, comment = 'FAIL', 'The log time recorded on the Syslog server (%s) is not correct(now is: %s)'\
                              % (time.ctime(i), syslog_ser_current_time)
                        break
                if result == 'FAIL': break
                
                bEvent = False
                for i in dv_log_events:
                    for element in sys_log_events:
                        if i in element:
                            bEvent = True
                            break
                    if bEvent:
                        bEvent = False
                    else:
                        result, comment = 'FAIL', 'The log \'%s\' on ZD is not recorded on the Syslog server' % repr(i)
                        break

            else:
                for i in dv_log_times:
                    if zd_time - i > run_time:
                        result, comment = 'FAIL', 'The log time recorded on the ZD (%s) is not correct (now is: %s)'\
                              % (time.ctime(i), zd_current_time)
                        break
                if result == 'FAIL': break

                bEvent = False
                for i in dv_log_events:
                    for element in sys_log_events:
                        if i in element:
                            bEvent = True
                            break
                    if bEvent:
                        bEvent = False
                    else:
                        result, comment = 'FAIL', 'The log \'%s\' on ZD is not recorded on the Syslog server' % repr(i)
                        break
            break
        logging.info('result: %s, comment: %s' % (result,comment))
        return result, comment

    def cleanup(self):
        # Restore all config on ZD
        self.zd.remove_all_wlan()
        self.zd.cfg_syslog_server()

        # Close the telnet session on the syslog server
        self.syslog_server.close()
        logging.info('Cleanup testing environment successfully')

    def _initAp(self, conf):
        self.flag = False
        if conf.has_key('target_ap'):
            self.ap = tconfig.get_testbed_active_ap(self.testbed, conf['target_ap'])
            if self.ap:
                self.ap_current_time = self.ap.get_time()
                self.ap_time = time.mktime(time.strptime(self.ap.get_time()))
                self.flag = True

            else:
                raise Exception('Target AP %s not found' % conf['target_ap'])

    def _initSyslogServer(self):
        # PHANNT@20100525:
        # re-use components['LinuxServer'] instead of creating a new one
        self.syslog_server = self.testbed.components['LinuxServer']
        self.syslog_server.re_init()
        logging.info('Telnet to the Syslog server at IP address %s successfully' % \
                     self.syslog_server.ip_addr)
