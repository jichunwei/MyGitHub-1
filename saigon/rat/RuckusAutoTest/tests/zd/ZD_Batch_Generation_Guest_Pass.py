# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is support to test the batch guest pass test cases
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:  'testcase': define the test case will be tested,
                     'wlan_cfg': optional, the configuration of guest WLAN,
                     'auth_server_type': define the authentication server type,
                     'auth_server_info': authentication server configuration,
                     'username': testing user use to generate guest pass,
                     'password': testing user password,
                     'number_profile': the number guest passes profile will be create in csv file to test

   Result type: PASS/FAIL
   Results: PASS: If we could generate the guest passes by importing the batch file
            FAIL: If we could not generate the guest passes by importing the batch file

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Cleanup all non-default setting of Zone Director
   2. Test:
       - Create the guest WLAN and setup authentication server
       - Generate the guest passes by import the batch file (.csv)
       - Verify the information of guest pass on webui and in the record file
   3. Cleanup:
   - Cleanup all non-default setting of Zone Director
"""

import os
import string
import csv
import time
from random import choice
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class ZD_Batch_Generation_Guest_Pass(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'testcase': 'define the test case will be tested',
                           'wlan_cfg': 'optional, the configuration of guest WLAN',
                           'auth_server_type': 'define the authentication server type',
                           'auth_server_info': 'authentication server configuration',
                           'username': 'testing user use to generate guest pass',
                           'password': 'testing user password',
                           'number_profile': 'the number guest passes profile will be create in csv file to test',
                          }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveAllConfigOnZD()

    def test(self):
        passmsg = []
        self._cfgCreateWlanOnZD()
        self._cfgAuthServerOnZD()
        self._generateCSVFile()

        self._testImportCSV()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        passmsg.append(self.passmsg)

        self._testVerifyGuestPassInfoOnWebUI()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        passmsg.append(self.passmsg)

        if self.conf['testcase'] == 'import_csv_predefined_username_guest_pass':
            self._testVerifyGuestPassInfoInRecordFile()
            if self.errmsg:
                return ('FAIL', self.errmsg)
            passmsg.append(self.passmsg)

        return ('PASS', ', '.join(passmsg))

    def cleanup(self):
        self._cfgRemoveAllConfigOnZD()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = {'testcase': '',
                     'wlan_cfg': {},
                     'auth_server_type': 'local',
                     'auth_server_info': {},
                     'username': 'guesttest',
                     'password': 'guesttest',
                     'number_profile': 10}

        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

#
# test()
#
    def _cfgCreateWlanOnZD(self):
        wlan_cfg = {'ssid':'Test_WLAN-%s' % time.strftime("%H%M%S"),
                    'type':'guest'}
        self.conf['wlan_cfg'].update(wlan_cfg)

        logging.info("Create WLAN [%s] as a Guest Access WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

    def _cfgAuthServerOnZD(self):
        if self.conf['auth_server_type'] == 'local':
            logging.info('Create user "%s" on Zone Director' % self.conf['username'])
            self.zd.create_user(self.conf['username'], self.conf['password'])
            logging.info('Use "Local Database" to generate and authenticate the guest passes')
            self.zd.set_guestpass_policy('Local Database')
        elif self.conf['auth_server_type'] == 'radius':
            logging.info('Create an Radius server on Zone Director')
            lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])
            logging.info('Use "Radius Server" to generate and authenticate the guest passes')
            self.zd.set_guestpass_policy(self.conf['auth_server_info']['server_name'])
        else:
            raise Exception('Do not support to test with  "%s" authentication server' % self.conf['auth_server_type'].upper())

    def _generateCSVFile(self):
        # Delete the file if it's existing
        try:
            os.remove('batch_file.csv')
        except: pass

        self.batch_file = open('batch_file.csv', 'wb')
        writer = csv.writer(self.batch_file)
        guest_user_info_list = []
        self.expected_webui_info = {}
        self.expected_record_info = {}

        logging.info("Generate a CSV file:")
        if self.conf['testcase'] == 'import_csv_predefined_username':
            logging.info('with predefined username')
            for id in range(1, self.conf['number_profile'] + 1):
                guestname = 'AutoGuest-%s' % id
                guest_user_info_list.append([guestname])
                self.expected_webui_info[guestname] = [self.conf['username'], self.conf['wlan_cfg']['ssid']]

        elif self.conf['testcase'] == 'import_csv_predefined_username_guest_pass':
            logging.info('with predefined username and guestpass')
            for id in range(1, self.conf['number_profile'] + 1):
                guestname = 'AutoGuest-%s' % id
                guestpass = ''.join([choice(string.letters).upper() for i in range(10)])
                guest_user_info_list.append([guestname, '', guestpass])
                self.expected_webui_info[guestname] = [self.conf['username'], self.conf['wlan_cfg']['ssid']]
                self.expected_record_info[guestname] = guestpass

        else:
            raise Exception('Do not support to test %s ' % self.conf['testcase'].replace('_', ' '))
        writer.writerows(guest_user_info_list)
        self.batch_file.close()

    def _testImportCSV(self):
        logging.info("Import the CSV file [%s] to generate guest passed" % self.batch_file.name)
        guestpass_setting = {'type': 'multiple',
                             'wlan': self.conf['wlan_cfg']['ssid'],
                             'profile_file': '\\'.join((os.getcwd(), self.batch_file.name)),
                             'username': self.conf['username'],
                             'password': self.conf['password']}
        try:
            lib.zd.ga.generate_guestpass(self.zd, **guestpass_setting)
            passmsg = 'Guest pass generation by importing the CSV file [%s], %s server successfully'
            self.passmsg = passmsg % (self.batch_file.name, self.conf['auth_server_type'].upper())
        except Exception, e:
            self.errmsg = '[Guest pass generation by importing the file failed] %s' % e.message

    def _testVerifyGuestPassInfoOnWebUI(self):
        logging.info("Verify guest passes information on Zone Director's WebUI")
        all_guestpass_info = lib.zd.ga.get_all_guestpasses(self.zd)
        all_guestpass_info_on_zd = {}

        for guest_full_name in all_guestpass_info.iterkeys():
            all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info[guest_full_name]['created_by'],
                                                         all_guestpass_info[guest_full_name]['wlan']
                                                         ]

        logging.debug('All guest pass information on Zone Director WebUI are: %s' % all_guestpass_info_on_zd)
        logging.debug('The guest passes information in file "%s" are: %s' % (self.batch_file.name,
                                                                             self.expected_webui_info))
        if all_guestpass_info_on_zd == self.expected_webui_info:
            self.passmsg = 'The guest pass information on WebUI are correctly '
            logging.info(self.passmsg)
            return

        errguest = []
        for guestpass in self.expected_webui_info.keys():
            if self.expected_webui_info[guestpass] != all_guestpass_info_on_zd[guestpass]:
                errguest.append(guestpass)
        if errguest:
            self.errmsg = 'The guest user %s are in the CSV file but be not created' % errguest
            logging.info(self.errmsg)

    def _testVerifyGuestPassInfoInRecordFile(self):
        logging.info('Download the generated guest passed record file and verify the guest passes information')
        record_file_path = lib.zd.ga.download_generated_guestpass_record(self.zd,
                                                                    self.conf['username'],
                                                                    self.conf['password'])
        record_file = open(record_file_path)
        reader = csv.reader(record_file)
        all_info_in_file = {}
        for row in reader:
            if row != ['Guest-Name', 'Key', 'Remarks', 'Expires']:
                all_info_in_file[row[0]] = row[1]
        record_file.close()

        logging.debug('All guest passes information in record file are: %s' % all_info_in_file)
        logging.debug('The guest passes information in file "%s" are: %s' % (self.batch_file.name,
                                                                             self.expected_record_info))

        if all_info_in_file == self.expected_record_info:
            self.passmsg = 'The guest pass information in generated guest passes record file are correctly'
            logging.info(self.passmsg)
            return

        errguest = []
        for guestpass in self.expected_record_info.keys():
            if self.expected_record_info[guestpass] != all_info_in_file[guestpass]:
                errguest.append(guestpass)
        if errguest:
            self.errmsg = 'The guest user %s are in the CSV file but be not created' % errguest
            logging.info(self.errmsg)
#
# cleanup()
#
    def _cfgRemoveAllConfigOnZD(self):
        logging.info("Remove all WLANs configured on the ZD")
        lib.zd.wlan.delete_all_wlans(self.zd)
        logging.info('Reset to use "Local Database" to generate and authenticate the guest passes')
        self.zd.set_guestpass_policy('Local Database')
        logging.info("Remove all AAA servers configured on the ZD")
        lib.zd.aaa.remove_all_servers(self.zd)
        logging.info("Remove all user")
        self.zd.remove_all_users()
        logging.info("Remove all guest passes")
        lib.zd.ga.delete_all_guestpass(self.zd)

