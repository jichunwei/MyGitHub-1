"""
Description: The ZD_WLAN_DPSK_Generation class supports testing the Batch Generation for
             Dynamic PSK - 9640

Author: Phan Nguyen
Email: phannt@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
        'testcase': define the test case will be tested,
        'wlan_cfg': optional, the configuration of guest WLAN,
        'auth_server_type': optional, define the authentication server type,
        'auth_server_info': optional, authentication server configuration,
        'psk_expiration': PSK Expiration duration,
        'number_of_dpsk': the number of DPSK will be created,
        'max_dpsk_allowable': the maximum number of allowable DPSK can be created,
        'check_status_timeout': timeout period for wireless client association, traffic sending..
        'expected_response_time': expected response time to perform an action,
        'target_ping_ip': optional, target station's IP Address to send traffic to

    Result type: PASS/FAIL
    Results:
        PASS: - DSPK can be successfully generated either by a batch with a specified
                number of profile, or a predefined CSV file.
              - DSPK can be deleted successfully.
              - DSPK is expired correctly.
              - DSPK can be exported to csv file.
        FAIL: if any of the pass criteria does not match.

    Messages: If FAIL the test script returns a message related to the criterion
              that is not satisfied.

   Test procedure:
   1. Config:
       - Remove all non-default configuration.
   2. Test:
      Varies from test case to test case. Please refer to the test plan document for detail.
      In general:
       - Perform DSPK generation/deletion/client association...
       - Verify if it is as expected (i.e. the info was updated correctly on the WebUI).
   3. Cleanup:
       - Remove all non-default configuration created during the execution.
"""

import os
import time
import datetime
import logging
import csv

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class ZD_WLAN_DPSK_Generation(Test):

    def config(self, conf):
        self._cfgInitTestParams(conf)

        self._cfgRemoveAllConfigOnZD()

        self._cfgCreateWlanOnZD()

        self.loadtime_stepout = self.zd.conf['loadtime_stepout']
        self.zd.conf['loadtime_stepout'] = self.conf['expected_response_time'] * 1000


    def test(self):
        self.tc2f[self.conf['testcase']]()

        if self.errmsg:
            return ("FAIL", self.errmsg)

        return ("PASS", self.passmsg.strip())


    def cleanup(self):
        self._cfgRemoveFiles()

        self.zd.conf['loadtime_stepout'] = self.loadtime_stepout


    #
    # Config()
    #
    def _cfgInitTestParams(self, conf = None):
        self.tc2f = {
            'batch-dpsk': self._testGenerateMutipleDPSK,
            'import-dpsk': self._testImportCSV,
            'export-dpsk': self._testExportDPSK,
            'delete-dpsk': self._testDeleteDPSK,
            'dpsk-expiration': self._testDPSKExpiration,
            'dpsk-scalability': self._testScalabilityDPSK,
            'max-dpsk': self._testVerifyMaxDPSK,
        }

        self.zd = self.testbed.components['ZoneDirector']
        self.station = self.testbed.components['Station']

        self.errmsg = ''
        self.passmsg = ''

        self.filelist = []

        self.conf = self._getDefaultConfig()
        self.conf.update(conf)

        self.wlan_cfg = self._getDefaultWlanConfig()
        self.wlan_cfg.update(conf['wlan_cfg'])

        self.dlg_cfg = self._getDefaultDlgConfig()

        # expire time in hours, obtained from the WebUI's source HTML
        # (PSK Expiration: <select id="expire">)
        self.expire_time = \
            {'Unlimited': 0,
             'One day': 24,
             'One week': 168,
             'Two weeks': 336,
             'One month': 720,
             'Two months': 1440,
             'Three months': 2160,
             'Half a year': 4380,
             'One year': 8760,
             'Two years': 17520,
             }

        self.sample_fpath = None

        self.sta_wifi_mac_addr = None
        self.sta_wifi_ip_addr = None

        # internal timer task for DPSK deletion, in minutes
        self.internal_timer = 20


    def _getDefaultConfig(self):
        conf = {'testcase': '',
                'wlan_cfg': {},
                'auth_server_type': 'local',
                'auth_server_info': {},
                'psk_expiration': 'One day',
                'number_of_dpsk': 100,
                'max_dpsk_allowable': 1000,
                'check_status_timeout': 150,
                'expected_response_time': 30,
                'target_station_ip': '192.168.1.11',
                'target_ping_ip': '192.168.0.252',
                }

        return conf


    def _getDefaultWlanConfig(self):
        conf = {'ssid': 'wlan-dpsk',
                'auth': 'PSK',
                'wpa_ver': 'WPA',
                'encryption': 'AES',
                'type': 'standard',
                'key_string': '1234567890',
                'key_index': '',
                'auth_svr': '',
                'do_zero_it': True,
                'do_dynamic_psk': True,
                }

        return conf


    def _getDefaultDlgConfig(self):
        zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)

        # The total number of DPSK accounts has reached the maximum \
        # allowable size.  Please contact your network administrator to \
        # remove unused accounts before creating new ones.
        dlg_text_maxdpsk = self.zd.messages['E_FailDpskExceedMax']
        dlg_text = dlg_text_maxdpsk.split('.')[0]

        conf = {'dlg_title': "The page at %s says:" % zd_url,
                'dlg_text_maxdpsk': dlg_text,
                }

        return conf


    def _getNumOfPSKs(self, pause = 5):
        self.zd.navigate_to(self.zd.MONITOR, self.zd.MONITOR_GENERATED_PSK_CERTS)
        time.sleep(pause)

        total = self.zd._get_total_number(self.zd.info['loc_mon_total_generated_psk_span'],
                                          "Generated Dynamic-PSK")

        return int(total)


    def _getDefaultDPSKConfig(self, facility = None):
        conf = {'psk_expiration': self.conf['psk_expiration'],
                'wlan': self.wlan_cfg['ssid'],
                'dlg_title': self.dlg_cfg['dlg_title'],
                'dlg_text': self.dlg_cfg['dlg_text_maxdpsk'],
                'expected_response_time': self.conf['expected_response_time']
                }

        if facility == 'number_of_dpsk':
            conf.update({'number_of_dpsk': self.conf['number_of_dpsk'],
                        })

        elif facility == 'profile_file':
            conf.update({'profile_file': '',
                        })
        return conf

    #
    # test()
    #

    def _testGenerateMutipleDPSK(self):
        conf = self._getDefaultDPSKConfig('number_of_dpsk')

        self._generate_multiple_dpsk(conf)
        if self.errmsg:
            return

        self._verifyDPSKInfoOnWebUI()


    def _testExportDPSK(self):
        conf = self._getDefaultDPSKConfig('number_of_dpsk')

        self._generate_multiple_dpsk(conf)
        if self.errmsg:
            return

        self._verifyDPSKInfoInRecordFile()


    def _testDeleteDPSK(self):
        conf = self._getDefaultDPSKConfig('number_of_dpsk')

        self._generate_multiple_dpsk(conf)
        if self.errmsg:
            return

        logging.info('Try to delete the generated PSKs')
        self.zd._remove_all_generated_psks()

        if self.errmsg:
            return

        logging.info("Make sure the entries disappear from the table")
        total = self._getNumOfPSKs()

        if total != 0:
            self.errmsg = 'Error in deleting generated PSKs'

        self.passmsg = 'Generated PSKs can be deleted successfully.'


    def _testVerifyMaxDPSK(self):
        conf = self._getDefaultDPSKConfig('number_of_dpsk')
        conf.update({'repeat': False})

        self._generateLargeDPSK(conf, self.conf['max_dpsk_allowable'])


    def _generateLargeDPSK(self, conf, number):
        count = 0
        while True and count <= 1:
            try:
                self._generate_multiple_dpsk(conf)
                total = self._getNumOfPSKs(self.conf['expected_response_time'])
                if number - total < self.conf['number_of_dpsk']:
                    count += 1

            except Exception, e:
                self._checkExceptionOfDPSK(e)
                break


    def _testScalabilityDPSK(self):
        # first phase
        self._generateCSVFile()

        conf = self._getDefaultDPSKConfig('profile_file')
        conf.update({'profile_file': '\\'.join((os.getcwd(), self.batch_file.name)),
                     'repeat': False,
                     })

        self._generateLargeDPSK(conf, self.conf['max_dpsk_allowable'] / 2)


        # second phase
        conf = self._getDefaultDPSKConfig('number_of_dpsk')
        conf.update({'repeat': False})

        self._generateLargeDPSK(conf, self.conf['max_dpsk_allowable'])

        self.passmsg += "Actions are performed within %s seconds. " % \
                        self.conf['expected_response_time']


    def _checkExceptionOfDPSK(self, e):
        total = self._getNumOfPSKs(self.conf['expected_response_time'])
        if self.dlg_cfg['dlg_text_maxdpsk'] in e.message:
            passmsg = '%s PSKs were generated on the ZD. ' % total
            passmsg = passmsg + "ZD does not allow to generate more batch PSKs " \
                                 "when maximum allowable size has reached. "
            self.passmsg = passmsg
            logging.info(passmsg)

        elif 'ZD took over %s seconds to perform the action.' % \
              self.conf['expected_response_time'] in e.message:
            self.errmsg = self.errmsg + e.message
            logging.info(e.message)
            raise

        else:
            errmsg = "Failed to generate large number of PSKs. "
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise


    def _testImportCSV(self):
        self._generateCSVFile()

        conf = self._getDefaultDPSKConfig('profile_file')
        conf.update({'profile_file': '\\'.join((os.getcwd(), self.batch_file.name)),
                     })

        self._generate_multiple_dpsk(conf)
        if self.errmsg:
            return

        self._verifyDPSKInfoOnWebUI()


    def _generate_multiple_dpsk(self, dpsk_conf):
        if dpsk_conf.has_key('profile_file'):
            gen_msg = "Import the CSV file [%s] to generate Dynamic PSKs. " % \
                      self.batch_file.name
            pass_msg = "Dynamic PSKs generation by importing the CSV file [%s] successfully. "
            pass_msg = pass_msg % self.batch_file.name

        elif dpsk_conf.has_key('number_of_dpsk'):
            gen_msg = "Try to generate %s Dynamic PSKs automatically." % \
                      dpsk_conf['number_of_dpsk']
            pass_msg = "%s Dynamic PSKs were generated successfully. "
            pass_msg = pass_msg % dpsk_conf['number_of_dpsk']

        logging.info(gen_msg)

        #Serena Tan. 2010.12.7. To fix bug 16593.
        self.zd.login(True)

        lib.zd.wlan.generate_multiple_dpsk(self.zd, dpsk_conf)
        logging.info(pass_msg)


    def _generateCSVFile(self):
        # Delete the file if it exists
        try:
            os.remove('batch_dpsk_file.csv')
        except: pass

        self.batch_file = open('batch_dpsk_file.csv', 'wb')
        writer = csv.writer(self.batch_file)
        dpsk_info_list = []
        self.expected_webui_info = {}

        logging.info("Generate a CSV file with predefined user names")
        for id in range(1, self.conf['number_of_dpsk'] + 1):
            dpsk_info = 'Predefined-DPSK-User-%s' % id
            dpsk_info_list.append([dpsk_info])
            self.expected_webui_info[dpsk_info] = [self.wlan_cfg['ssid']]

        writer.writerows(dpsk_info_list)
        self.batch_file.close()


    def _verifyInfo(self, sourceInfo, expectedInfo, keyOnly = True):
        if not isinstance(sourceInfo, dict) or expectedInfo is None:
            logging.debug("Either expectedInfo is None or sourceInfo is not a dict")
            return False

        if isinstance(expectedInfo, dict):
            if sourceInfo == expectedInfo:
                return True

        self.errkey = []
        try:
            if isinstance(expectedInfo, dict):
                for key in expectedInfo.keys():
                    # either the key does not exist, or its value is not identical to the expected one
                    if key in sourceInfo.keys():
                        if not keyOnly and expectedInfo[key] != sourceInfo[key]:
                            self.errkey.append(key)

                    else:
                        self.errkey.append(key)

            else:
                for key in sourceInfo.keys():
                    if sourceInfo[key] != expectedInfo:
                        self.errkey.append(key)

        except Exception, e:
            logging.debug(e.message)
            return False

        if self.errkey:
            return False

        return True


    def _parseCSVFile(self, filepath,
                      header = ['User Name', 'Passphrase', 'WLAN', 'Mac Address', 'Expires']):
        data = {}
        try:
            tmpfile = open(filepath)
            reader = csv.reader(tmpfile)

            for row in reader:
                if row != header and len(row) > 0:
                    data[row[0]] = row[1]

            tmpfile.close()

            logging.debug('All generated PSKs information in record file are: %s' % data)

        except Exception, e:
            logging.debug(e.message)

        return data


    def _verifyDPSKInfoOnWebUI(self, expected_info = None):
        if expected_info is None:
            expected_info = [self.wlan_cfg['ssid']]

        logging.info("Get all generated PSKs on WebUI")
        all_dpsk_info = self.zd.get_all_generated_psks_info()

        all_dpsk_info_on_zd = {}
        for dpsk_info in all_dpsk_info:
            all_dpsk_info_on_zd[dpsk_info['user']] = [dpsk_info['wlans']]
        logging.debug('All PSKs information on ZD WebUI are: %s' % all_dpsk_info_on_zd)

        if isinstance(expected_info, dict):
            logging.info('Verify the number of generated PSKs')
            if len(all_dpsk_info) != self.conf['number_of_dpsk']:
                errmsg = 'We expect there are %s PSKs created but %s on file. '
                errmsg = errmsg % (self.conf['number_of_dpsk'], len(all_dpsk_info))
                self.errmsg = self.errmsg + errmsg
                return

        logging.info('Verify the PSKs information shown on WebUI')
        if not self._verifyInfo(all_dpsk_info_on_zd, expected_info):
            errmsg = 'The wlan information of PSKs %s are not %s as expected. '
            errmsg = errmsg % (self.errkey, expected_info)
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            return

        passmsg = 'WebUI was updated correctly %s PSKs created. ' % len(all_dpsk_info_on_zd)
        self.passmsg = self.passmsg + passmsg
        logging.info(passmsg)


    def _verifyDPSKInfoInRecordFile(self, expected_info = None, keyOnly = True):
        if expected_info is None:
            logging.info("Get all generated PSKs on WebUI")
            all_dpsk_info = self.zd.get_all_generated_psks_info()

            all_dpsk_info_on_zd = {}
            for dpsk_info in all_dpsk_info:
                all_dpsk_info_on_zd[dpsk_info['user']] = [dpsk_info['wlans']]

            logging.debug('All PSKs information on ZD WebUI are: %s' % all_dpsk_info_on_zd)
            expected_info = all_dpsk_info_on_zd

        logging.info('Download the generated PSKs record file')
        record_file_path = lib.zd.wlan.download_generated_dpsk_record(
                               self.zd, filename_re = "batch_dpsk_\d{6}_\d{2}_\d{2}.csv",
                               pause = 3)
        self.filelist.append(record_file_path)

        logging.debug("Parse the CSV file")
        all_info_in_file = self._parseCSVFile(record_file_path)

        logging.info('Verify the PSKs in the record file against those on WebUI')
        if not self._verifyInfo(all_info_in_file, expected_info, keyOnly):
            errmsg = 'Expected PSKs, %s, were not found. '
            errmsg = errmsg % self.errkey
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            return

        passmsg = '%s generated PSKs were generated successfully and they are found ' \
                  'in the record file. '
        passmsg = passmsg % self.conf['number_of_dpsk']
        self.passmsg = self.passmsg + passmsg
        logging.info(passmsg)


    def _cfgRemoveAllWlanProfilesOnStation(self):
        self.target_station = None
        for station in self.station:
            if station.get_ip_addr() == self.conf['target_station_ip']:
                # Found the target station
                self.target_station = station
                self._cfgRemoveStationWlanProfiles()
                break

        if self.target_station is None:
            errmsg = "Target station % s not found. " % self.conf['target_station']
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise Exception(errmsg)


    def _cfgRemoveStationWlanProfiles(self):
        logging.info("Remove all WLAN profiles on the remote station")
        self.target_station.remove_all_wlan()

        logging.info("Make sure the target station %s disconnects from wireless network" %
                     self.target_station.get_ip_addr())

        errorMsg = "The station did not disconnect from wireless network within %d seconds"

        return self._checkConnectionStatus("disconnected",
                                           self.conf['check_status_timeout'],
                                           errorMsg)


    def _checkConnectionStatus(self, status, timeout, errorMsg):
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == status:
                return True

            time.sleep(1)
            if time.time() - start_time > timeout:
                errmsg = errorMsg % timeout
                self.errmsg = self.errmsg + errmsg
                raise Exception(errmsg)


    def _checkValidDPSKExpiration(self, dpsk_info):
        max_expire_time = self.zd.get_current_time()
        max_expire_time = time.strftime("%Y/%m/%d %H:%M:%S",
                                        time.strptime(max_expire_time, "%A, %B %d, %Y %H:%M:%S %p"))
        max_expire_time = time.mktime(time.strptime(max_expire_time.split()[0], "%Y/%m/%d")) \
                        + self.expire_time[self.conf['psk_expiration']] * 3600

        dpsk_expire_time = dpsk_info['expired_time']
        dpsk_expire_time = time.mktime(time.strptime(dpsk_expire_time.split()[0], "%Y/%m/%d"))

        if dpsk_expire_time != max_expire_time:
            logging.info("The configured expire time for Generated PSK is: %s" % dpsk_expire_time)
            logging.info("The right expire time for Generated PSK is: %s" % max_expire_time)
            errmsg = "The expire time for the Generated PSK %s is not right. " % self.guest_pass
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)


    def _checkExpirityStatus(self):
        # Make sure that target station status is not "Authorized" after doing
        # authentication with expired PSK
        time.sleep(2)
        logging.info("Verify information of the target station shown on the ZD")
        client_info_on_zd = None
        start_time = time.time()

        contd = True
        while contd:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    if client['status'] == 'Authorized':
                        logging.debug("Active Client: %s" % str(client))
                        errmsg = "Station status is %s after doing authentication " \
                                 "with expired PSK. " % client['status']
                        self.errmsg = self.errmsg + errmsg
                        logging.debug(errmsg)
                        return

                    client_info_on_zd = client
                    contd = False

                    break #the for loop

            if not contd or time.time() - start_time > self.conf['check_status_timeout']:
                logging.debug("Active Client: %s" % str(client_info_on_zd))
                logging.info("The status of station is %s now" % client_info_on_zd['status'])

                break #the while loop

        if not client_info_on_zd:
            logging.debug("Active Client List: %s" % str(active_client_list))
            errmsg = "ZD didn't show any info about the target station (with MAC %s). " % \
                     self.sta_wifi_mac_addr
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)


    def _associateClient(self, dpsk_info):
        logging.info("Configure a WLAN with SSID %s on the target station %s" %
                     (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        client_wlan_cfg = self.wlan_cfg
        client_wlan_cfg.update({'key_string': dpsk_info['passphrase']})
        self.target_station.cfg_wlan(client_wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")

        errorMsg = "The station didn't associate to the wireless network after %d seconds"

        self._checkConnectionStatus("connected", self.conf['check_status_timeout'], errorMsg)

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % \
                     self.target_station.get_ip_addr())

        start_time = time.time()

        while time.time() - start_time < self.conf['check_status_timeout']:
            self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = \
                self.target_station.get_wifi_addresses()

            if self.sta_wifi_mac_addr and self.sta_wifi_ip_addr \
            and self.sta_wifi_ip_addr != "0.0.0.0" \
            and not self.sta_wifi_ip_addr.startswith("169.254"):
                break

            time.sleep(1)


    def _checkTraffic(self, when = 'Expired'):
        logging.info("Ping to %s from the target station" % self.conf['target_ping_ip'])
        ping_result = self.target_station.ping(self.conf['target_ping_ip'], 10 * 1000)

        if when == 'Expired':
            if ping_result.find("Timeout") != -1:
                logging.info('Ping FAILED. Correct behavior.')
            else:
                logging.info('Ping OK. Incorrect behavior.')
                self.errmsg += "The target station could send traffic after its PSK had been expired"

        elif when == 'Authorized':
            if ping_result.find("Timeout") != -1:
                logging.info('Ping FAILED. Incorrect behavior.')
                self.errmsg += "The target station could not send traffic after %s seconds" % \
                                self.conf['check_status_timeout']
            else:
                logging.info('Ping OK. Correct behavior.')


    def _checkAuthStatus(self, dpsk_info):
        logging.info("Verify information of the target station shown on the ZD")
        timed_out = False
        start_time = time.time()

        while True:
            all_good = True
            client_info_on_zd = None

            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                logging.debug("Found info of a station: %s" % client)
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    client_info_on_zd = client
                    if client['status'] != 'Authorized':
                        if timed_out:
                            errmsg = "The station status shown on ZD was %s instead of "\
                                     "'Authorized'" % client['status']
                            self.errmsg = self.errmsg + errmsg
                            logging.debug(errmsg)
                            return

                        all_good = False
                        break

                    if client['ip'] != dpsk_info['user']:
                        if timed_out:
                            errmsg = "The station username shown on ZD was %s instead of %s" % \
                                     (client['ip'], self.dpsk_info['user'])
                            self.errmsg = self.errmsg + errmsg
                            logging.debug(errmsg)
                            return

                        all_good = False
                        break

                    if client['wlan'] != dpsk_info['wlans']:
                        if timed_out:
                            errmsg = "The station's SSID shown on ZD was %s instead of %s" % \
                                     (client['wlan'], self.dpsk_info['wlans'])
                            self.errmsg = self.errmsg + errmsg
                            logging.debug(errmsg)
                            return

                        all_good = False
                        break

            # End of for

            # Quit the loop if everything is good
            if client_info_on_zd and all_good: break

            # Otherwise, sleep
            time.sleep(1)

            timed_out = time.time() - start_time > self.check_status_timeout
            # And report error if the info is not available
            if not client_info_on_zd and timed_out:
                errmsg = "ZD didn't show any info about the target station "\
                         "while it had been associated"
                self.errmsg = self.errmsg + errmsg
                logging.debug(errmsg)
                return

        # End of while


    def _testDPSKExpiration(self):
        conf = self._getDefaultDPSKConfig('number_of_dpsk')
        self._generate_multiple_dpsk(conf)

        logging.info('Download the generated PSKs record file')
        record_file_path = lib.zd.wlan.download_generated_dpsk_record(
                               self.zd, filename_re = "batch_dpsk_\d{6}_\d{2}_\d{2}.csv",
                               pause = 3)
        self.filelist.append(record_file_path)

        #logging.debug("Parse the CSV file")
        all_dpsk_file = self._parseCSVFile(record_file_path)

        logging.info("Get all generated PSKs on WebUI")
        all_dpsk_webui = self.zd.get_all_generated_psks_info()

        keys = ""
        for dpsk_info in all_dpsk_webui:
            dpsk_info.update({'passphrase': all_dpsk_file[dpsk_info['user']]})

            self._checkValidDPSKExpiration(dpsk_info)

            self._cfgRemoveAllWlanProfilesOnStation()

            self._associateClient(dpsk_info)

            self._checkAuthStatus(dpsk_info)

            self._checkTraffic(when = 'Authorized')

            # Change ZD system time to make Generated PSK expired by changing the PC time
            # and ZD is synced with this new PC time
            logging.info("The PSK %s is valid until %s" % \
                         (dpsk_info['user'], dpsk_info['expired_time']))
            logging.info("Change ZD time so that all the generated PSKs are expired")

            tmptime = datetime.datetime.now() + \
                        datetime.timedelta(hours = self.expire_time[self.conf['psk_expiration']],
                                           minutes = self.internal_timer)

            os.system("date %s" % str(tmptime.month) + "-" + \
                      str(tmptime.day) + "-" + str(tmptime.year))
            time.sleep(5)
            self.zd.get_current_time(True)

            try:
                self._cfgRemoveAllWlanProfilesOnStation()

                self._associateClient(dpsk_info)

                self._checkExpirityStatus()

                self._checkTraffic(when = 'Expired')

            except:
                raise

            finally:
                logging.info("Return the previous system time for ZD")
                tmptime = datetime.datetime.now() - \
                            datetime.timedelta(hours = self.expire_time[self.conf['psk_expiration']],
                                               minutes = self.internal_timer)

                os.system("date %s" % str(tmptime.month) + "-" + \
                          str(tmptime.day) + "-" + str(tmptime.year))
                time.sleep(5)
                self.zd.get_current_time(True)

            keys += dpsk_info['user'] + ', '

        self.passmsg += "PSKs expired correctly: [%s]" % keys


    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] on the ZD" % self.wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

    #
    # cleanup()
    #
    def _cfgRemoveFiles(self):
        for afile in self.filelist:
            if afile:
                os.remove(afile)


    def _cfgRemoveAllConfigOnZD(self):
        logging.info("Remove all WLANs configured on the ZD")
        lib.zd.wlan.delete_all_wlans(self.zd)

        logging.info("Remove all Generated PSKs on the ZD")
        self.zd._remove_all_generated_psks()

