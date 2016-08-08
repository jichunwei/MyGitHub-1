"""
Description: The ZD_GuestAccess_GuestPassGeneration class supports testing the Batch generation of guest passes - 7439

Author: Phan Nguyen
Email: phannt@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
        'testcase': define the test case will be tested,
        'wlan_cfg': optional, the configuration of guest WLAN,
        'auth_server_type': define the authentication server type,
        'auth_server_info': authentication server configuration,
        'username': guest pass generation username,
        'password': guest pass generation password,
        'number_profile': the number guest passes profile will be created,
        'max_gp_allowable': the maximum number of allowable guest passes can be created,
        'guestpass_key': optional, the manual guest pass key,

    Result type: PASS/FAIL
    Results:
        PASS: - Guest Pass can be successfully generated either by a batch with a specified
                number of profile, or a predefined CSV file, or manually with a single specified
                guest pass key.
              - Guest Pass can be deleted successfully.
              - Guest Pass can be displayed correctly via a customized Guest Pass Printout.
              - Guest Pass is expired correctly.
        FAIL: if any of the pass criteria does not match.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

   Test procedure:
   1. Config:
       - Remove all non-default configuration.
       - Record current Guest Pass Printouts.
   2. Test: varies from test case to test case. Please refer to the test plan document for detail.
      In general:
       - Perform Guest Pass generation/deletion/...
       - Verify if it is as expected (i.e. the info was updated correctly on the WebUI).
   3. Cleanup:
       - Remove all non-default configuration created during the execution.
       - Restore the previously saved configuration.
"""

import os
import time
import datetime
import string
from random import choice
import traceback
import logging
import csv

from RuckusAutoTest.tests.zd.ZD_GuestAccess_Common import ZD_GuestAccess_Common
from RuckusAutoTest.components import Helpers as lib

class ZD_GuestAccess_GuestPassGeneration(ZD_GuestAccess_Common):

    def config(self, conf):
        # the super method should be called first
        ZD_GuestAccess_Common.config(self, conf)

        self.tc2f = {
            'generate-usernames-guestpasses': self._testGenerateUsernamesGuestpasses, #TCs 3.1.1-4
            'import_csv_predefined_username': self._testImportCSV, #TCs: 3.1.5-8
            'import_csv_predefined_username_guestpass': self._testImportCSV, #TCs: 3.1.9-12
            'verify-max-guestpass': self._testVerifyMaxGuestPass, # TC 3.1.13
            'verify-gprint-customization': self._testVerifyGuestPassPrintoutCustomization, #TC 3.1.14
            'export-guestpass': self._testExportGuestPass, #TC 3.1.18
            'verify-duplicated-guestpass': self._testVerifyDuplicatedGuestPass, #TC 3.1.19
            'verify-guestpass-manually-generated': self._testVerifyGuestPassManuallyGenerated, # TC 3.1.20
            'delete-guestpass': self._testDeleteGeneratedGuestPass, #TCs 3.1.15, 21
        }

        self._cfgBackupConfigOnZD()


    def test(self):
        # calls the super method
        return ZD_GuestAccess_Common.test(self)


    def cleanup(self):
        # calls the super method
        ZD_GuestAccess_Common.cleanup(self)

    #
    # Config()
    #
    def _cfgInitTestParams(self, conf = None):
        # the super method should be called first to initialize common variables
        ZD_GuestAccess_Common._cfgInitTestParams(self, conf)

        # additional params should be put below
        if conf is None:
            conf = self._getDefaultConfig()
            self.conf = conf
        else:
            self.conf.update(conf)

        self.wlan_cfg = conf['wlan_cfg']
        if self.wlan_cfg == {} or not self.wlan_cfg.has_key('ssid'):
            # Modified by Serena Tan. 2010.11.22
            # To fix bug 16514.
#            self.wlan_cfg.update({'ssid': 'wlan-guestpass', 'type': 'guest'})
            ssid = "wlan-guestpass-%s" % time.strftime("%H%M%S")
            self.wlan_cfg.update({'ssid': ssid, 'type': 'guest'})

        self.dlg_cfg = self._getDefaultDlgConfig()

        self.sample_fpath = None
        self.gprint_cfg = self._getDefaultGPrintConfig()

        self.def_gprints = []
        self.modified_gprints = []


    def _getDefaultConfig(self):
        conf = {'testcase': '',
                'wlan_cfg': {},
                'auth_server_type': 'local',
                'auth_server_info': {},
                'username': 'guesttest',
                'password': 'guesttest',
                'number_profile': 10,
                'max_gp_allowable': 1250,
                'guestpass_key': 'ABCDE-FGHIJ',
                }
        return conf


    def _getDefaultDlgConfig(self):
        zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)
        dlg_cfg = {'dlg_title': "The page at %s says:" % zd_url,
                   'dlg_text_maxgp': "The total number of guest and user accounts reaches maximum allowable size %d" % (self.conf['max_gp_allowable']),
                   'dlg_text_dupgp': 'The key %s already exists. Please enter a different key.',
                   }
        return dlg_cfg


    def _getDefaultGPrintConfig(self):
        gprint_cfg = {'name': 'CustomizedGPPrintout-%s' % time.strftime("%H%M%S"),
                      'description': 'Customized Guest Pass Printout',
                      'html_file': self.sample_fpath,
                      'template_fname': 'guestpass_print.html',
                      'gprint1_old': '</style>',
                      'gprint1_new': '%s\n</style>',
                      'gprint1_needed': '.gptest {font-family: Tahoma; font-size: x-small; font-style: normal; color: #FF0000;}',
                      'gprint2_old': '<strong>{GP_GUEST_KEY}',
                      'gprint2_new': '<strong %s>{GP_GUEST_KEY}',
                      'gprint2_needed': 'class="gptest"',
                      }
        return gprint_cfg


    def _cfgAuthServerOnZD(self):
        ZD_GuestAccess_Common._cfgAuthServerOnZD(self)


    def _cfgBackupConfigOnZD(self):
        logging.info("Record the list of the existing Guest Pass Printouts")
        self.def_gprints = lib.zd.ga.get_list_of_guestpass_printout(self.zd)


    #
    # test()
    #
    def _testGenerateUsernamesGuestpasses(self):
        gp_cfg = self._getDefaultGPConfig('multiple')
        gp_cfg.update({'number_profile': self.conf['number_profile'],
                       'dlg_title': self.dlg_cfg['dlg_title'],
                       'dlg_text': self.dlg_cfg['dlg_text_maxgp'],
                       'validate_gprints': False,
                       })

        self._generate_multiple_guestpass(**gp_cfg)
        if self.errmsg:
            return

        self._verifyGuestPassInfoOnWebUI()


    def _testExportGuestPass(self):
        gp_cfg = self._getDefaultGPConfig('multiple')
        gp_cfg.update({'number_profile': self.conf['number_profile'],
                       'dlg_title': self.dlg_cfg['dlg_title'],
                       'dlg_text': self.dlg_cfg['dlg_text_maxgp'],
                       'validate_gprints': False,
                       })

        self._generate_multiple_guestpass(**gp_cfg)
        if self.errmsg:
            return

        self._verifyGuestPassInfoInRecordFile()


    def _testDeleteGeneratedGuestPass(self):
        logging.info("Try to delete the generated Guest Pass")

        self._generate_single_guestpass()

        guest_name = lib.zd.ga.guestpass_info['single_gp']['guest_name']

        lib.zd.ga.delete_guestpass(self.zd, guest_name)

        logging.info("Make sure the entry disappears from the table")

        try:
            lib.zd.ga.get_guestpass_by_name(self.zd, guest_name)
            errmsg = "The guest pass %s still exists in the table. " % guest_name
            self.errmsg = self.errmsg + errmsg
            logging.debug(errmsg)

        except Exception, e:
            if 'No matched row found' in e.message:
                passmsg = "The guest pass %s disappeared from the table. " % guest_name
                self.passmsg = self.passmsg + passmsg
                logging.info(passmsg)

            else:
                errmsg = e.message
                self.errmsg = self.errmsg + errmsg
                logging.debug(errmsg)


    def _testVerifyDuplicatedGuestPass(self):
        try:
            self._generate_single_guestpass()
            gp_key = lib.zd.ga.guestpass_info['single_gp']['guest_pass']

            # try to generate another guest pass using the key has just been generated
            self._generate_single_guestpass(gp_key)

        except Exception, e:
            if "Please enter a different key" in e.message:
                passmsg = "Duplicated guest pass cannot be used is confirmed! "
                self.passmsg = self.passmsg + passmsg
                return

            else:
                errmsg = "Unable to verify duplicated guest pass generation. "
                self.errmsg = self.errmsg + errmsg
                logging.debug(errmsg)
                raise


    def _testVerifyGuestPassManuallyGenerated(self):
        logging.info("Verify generated guest pass is updated on WebUI")
        try:
            self._generate_single_guestpass()

            expected_info = [self.conf['username'], self.wlan_cfg['ssid']]
            self._verifyGuestPassInfoOnWebUI(expected_info)

        except Exception, e:
            errmsg = "Unable to verify whether generated guest pass is updated on WebUI. "
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise


    def _testVerifyGuestPassPrintoutCustomization(self):
        logging.info("Try to download the sample Guest Pass Printout")
        try:
            self.sample_fpath = lib.zd.ga.download_guestpass_printout_sample(self.zd)
            if not os.path.isfile(self.sample_fpath):
                raise
            else:
                self.gprint_cfg.update({'html_file': self.sample_fpath})

        except Exception, e:
            errmsg = "Unable to download the sample Guest Pass Printout. "
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise
            return

        logging.info("Customize the downloaded Guest Pass Printout sample")
        try:
            tf = open(self.sample_fpath, "rb")
            data = tf.read()
            tf.close()

            data = data.replace(self.gprint_cfg['gprint1_old'], self.gprint_cfg['gprint1_new'] % (self.gprint_cfg['gprint1_needed']))
            data = data.replace(self.gprint_cfg['gprint2_old'], self.gprint_cfg['gprint2_new'] % (self.gprint_cfg['gprint2_needed']))

            tf = open(self.sample_fpath, "wb")
            tf.write(data)
            tf.close()

        except Exception, e:
            errmsg = "Unable to read/write the file [%s]. " % self.sample_fpath
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise
            return

        logging.info("Try to create a new Guest Pass Printout with customized HTML")
        try:
            lib.zd.ga.create_guestpass_printout(self.zd, self.gprint_cfg)
            self.modified_gprints.append([self.gprint_cfg['name'], ])

        except Exception, e:
            errmsg = "Unable to create the Guest Pass Printout [%s]: %s. " % (self.gprint_cfg['name'], e.message)
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise
            return

        logging.info("Generate a single Guest Pass and verify Guest Pass Printout")
        try:
            gp_cfg = self._getDefaultGPConfig('single')
            gp_cfg.update({'validate_gprints': True,
                           'printout_name': self.gprint_cfg['name'],
                           'printout_checker1': self.gprint_cfg['gprint1_new'] % (self.gprint_cfg['gprint1_needed']),
                           'printout_checker2': self.gprint_cfg['gprint2_new'] % (self.gprint_cfg['gprint2_needed']),
                           })

            lib.zd.ga._perform_auth_to_generate_guestpass(self.zd, gp_cfg['username'], gp_cfg['password'])

            lib.zd.ga._generate_single_guestpass(self.zd, **gp_cfg)
            gp_key = lib.zd.ga.guestpass_info['single_gp']['guest_pass']

            if lib.zd.ga._verify_guestpass_printout(self.zd, gp_key, **gp_cfg):
                passmsg = "Guest passes can be printed by using different formats or languages. "
                self.passmsg = self.passmsg + passmsg
                logging.info(passmsg)

            else:
                errmsg = "Failed to verify whether guest passes can be printed by using different formats or languages. "
                self.errmsg = self.errmsg + errmsg
                logging.info(errmsg)

        except Exception, e:
            errmsg = "Failed to verify whether guest passes can be printed by using different formats or languages. "
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            raise


    def _testVerifyMaxGuestPass(self):
        gp_cfg = self._getDefaultGPConfig('multiple')
        gp_cfg.update({'number_profile': self.conf['number_profile'],
                       'dlg_title': self.dlg_cfg['dlg_title'],
                       'dlg_text': self.dlg_cfg['dlg_text_maxgp'],
                       'validate_gprints': False,
                       })

        lib.zd.ga._log_to_generate_guestpass_page(self.zd)
        time.sleep(2)
        idx, idx, total = lib.zd.ga._get_page_range_and_total_number_of_generated_guestpass(self.zd)
        total = int(total)

        count = 0
        while True and count < self.conf['max_gp_allowable']:
            try:
                self._generate_multiple_guestpass(**gp_cfg)
                count = self.conf['number_profile']
                total += count
                passmsg = '%s guest pass(es) were generated on the ZD. ' % total

            except Exception, e:
                if gp_cfg['dlg_text'] in e.message and \
                self.conf['max_gp_allowable'] - total < self.conf['number_profile']:
                    passmsg = passmsg + "ZD does not allow to generate more batch guest passes when maximum allowable size has reached. "
                    self.passmsg = passmsg
                    logging.info(passmsg)

                else:
                    errmsg = "Failed to generate or verify maximum number of guest passes. "
                    self.errmsg = self.errmsg + errmsg
                    logging.info(errmsg)

                    raise

                break

        count = 1
        self._cfgQuickRemoveGuestPass(count)


    def _cfgQuickRemoveGuestPass(self, count):
        # change ZD time to trigger the clear generated guest passes event
        logging.debug("Change ZD time so that all the generated guest passes are expired")
        tmptime = datetime.datetime.now() + datetime.timedelta(days = count * 365)
        os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
        time.sleep(3)
        self.zd.get_current_time(True)

        lib.zd.ga._log_to_generate_guestpass_page(self.zd)
        time.sleep(30)

        logging.debug("Return the previous system time for the ZD")
        tmptime = datetime.datetime.now() - datetime.timedelta(days = count * 365)
        os.system("date %s" % str(tmptime.month) + "-" + str(tmptime.day) + "-" + str(tmptime.year))
        time.sleep(3)
        self.zd.get_current_time(True)

        lib.zd.ga._log_to_generate_guestpass_page(self.zd)
        time.sleep(5)
        idx, idx, total = lib.zd.ga._get_page_range_and_total_number_of_generated_guestpass(self.zd)
        total = int(total)

        # recursive
        if total > 0:
            count += 1
            self._cfgQuickRemoveGuestPass(count)

            if count >= 3:
                logging.debug("Unexpected error with ZD timing event.")
                return


    def _testImportCSV(self):
        self._generateCSVFile()

        gp_cfg = self._getDefaultGPConfig('multiple')
        gp_cfg.update({'profile_file': '\\'.join((os.getcwd(), self.batch_file.name)),
                       'dlg_title': self.dlg_cfg['dlg_title'],
                       'dlg_text': self.dlg_cfg['dlg_text_maxgp'],
                       'validate_gprints': False
                       })

        self._generate_multiple_guestpass(**gp_cfg)

        self._verifyGuestPassInfoOnWebUI()


    def _getDefaultGPConfig(self, type):
        gp_cfg = {'username': self.conf['username'],
                  'password': self.conf['password'],
                  'wlan': self.wlan_cfg['ssid'],
                  'duration': '1',
                  'duration_unit': 'Days',
                  }

        if type == 'single':
            gp_cfg.update({'type': type,
                           'guest_fullname': 'Tester',
                           'remarks': '',
                           'key': self.conf['guestpass_key'],
                           })

        elif type == 'multiple':
            gp_cfg.update({'type': type,
                           })
        else:
            logging.debug("GP config type %s is not supported!!" % type)

        return gp_cfg


    def _generate_single_guestpass(self, guestpass_key = None):
        if guestpass_key is None:
            guestpass_key = self.conf['guestpass_key']

        logging.info("Try to generate a single Guest Pass")
        gp_cfg = self._getDefaultGPConfig('single')
        gp_cfg.update({'key': guestpass_key,
                       'dlg_title': self.dlg_cfg['dlg_title'],
                       'dlg_text': self.dlg_cfg['dlg_text_dupgp'] % guestpass_key,
                       'validate_gprints': False,
                       })

        lib.zd.ga._perform_auth_to_generate_guestpass(self.zd, gp_cfg['username'], gp_cfg['password'])
        lib.zd.ga._generate_single_guestpass(self.zd, **gp_cfg)

        logging.debug("Guest pass was generated successfully, %s" % lib.zd.ga.guestpass_info['single_gp'])


    def _generate_multiple_guestpass(self, **kwarg):
        if kwarg.has_key('profile_file'):
            gen_msg = "Import the CSV file [%s] to generate guest passed." % self.batch_file.name
            pass_msg = 'Guest pass generation by importing the CSV file [%s], %s server successfully. '
            pass_msg = pass_msg % (self.batch_file.name, self.conf['auth_server_type'].upper())
            err_msg = 'Guest pass generation by importing the file failed'

        elif kwarg.has_key('number_profile'):
            gen_msg = "Try to generate %s guest passes automatically." % kwarg['number_profile']
            pass_msg = 'Create %s guest passes automatically using %s server successfully. '
            pass_msg = pass_msg % (kwarg['number_profile'], self.conf['auth_server_type'].upper())
            err_msg = 'Create %s guest passes failed' % self.conf['number_profile']

        logging.info(gen_msg)

        lib.zd.ga.generate_guestpass(self.zd, **kwarg)
        self.passmsg = self.passmsg + pass_msg
        logging.info(pass_msg)


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
                self.expected_webui_info[guestname] = [self.conf['username'], self.wlan_cfg['ssid']]

        elif self.conf['testcase'] == 'import_csv_predefined_username_guestpass':
            logging.info('with predefined username and guestpass')
            for id in range(1, self.conf['number_profile'] + 1):
                guestname = 'AutoGuest-%s' % id
                guestpass = ''.join([choice(string.letters).upper() for i in range(10)])
                guest_user_info_list.append([guestname, '', guestpass])
                self.expected_webui_info[guestname] = [self.conf['username'], self.wlan_cfg['ssid']]
                self.expected_record_info[guestname] = guestpass

        else:
            raise Exception('Do not support to test %s ' % self.conf['testcase'].replace('_', ' '))

        writer.writerows(guest_user_info_list)
        self.batch_file.close()


    def _verifyInfo(self, sourceInfo, expectedInfo, keyOnly = True):
        #
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

        except Exception:
            traceback.print_exc()
            return False

        if self.errkey:
            return False

        return True

    def _parseCSVFile(self, filepath, header = ['Guest-Name', 'Key', 'Remarks', 'Expires']):
        data = {}
        try:
            tmpfile = open(filepath)
            reader = csv.reader(tmpfile)

            for row in reader:
                if row != header:
                    data[row[0]] = row[1]

            tmpfile.close()

            logging.debug('All guest passes information in record file are: %s' % data)

        except Exception, e:
            traceback.print_exc()

        return data


    def _verifyGuestPassInfoOnWebUI(self, expected_info = None):
        if expected_info is None:
            expected_info = [self.conf['username'], self.wlan_cfg['ssid']]

        logging.info("Get all guest passes on WebUI")
        all_guestpass_info = lib.zd.ga.get_all_guestpasses(self.zd)

        all_guestpass_info_on_zd = {}
        for guest_full_name in all_guestpass_info.iterkeys():
            all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info[guest_full_name]['created_by'],
                                                         all_guestpass_info[guest_full_name]['wlan']
                                                         ]

        logging.debug('All guest pass information on Zone Director WebUI are: %s' % all_guestpass_info_on_zd)

        if isinstance(expected_info, dict):
            logging.info('Verify the number of user names and guest passes generated')
            if len(all_guestpass_info) != self.conf['number_profile']:
                errmsg = 'We expect there are %s guest passes created but %s on file. '
                errmsg = errmsg % (self.conf['number_profile'], len(all_guestpass_info))
                self.errmsg = self.errmsg + errmsg
                return

        logging.info('Verify the guest pass information shown on WebUI')
        if not self._verifyInfo(all_guestpass_info_on_zd, expected_info):
            errmsg = 'The creator and wlan information of guest users %s are not %s as expected. '
            errmsg = errmsg % (self.errkey, expected_info)
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            return

        passmsg = 'WebUI was updated correctly %s guest pass(es) created. ' % len(all_guestpass_info_on_zd)
        self.passmsg = self.passmsg + passmsg
        logging.info(passmsg)


    def _verifyGuestPassInfoInRecordFile(self, expected_info = None, keyOnly = True):
        if expected_info is None:
            logging.info("Get all guest passes on WebUI")
            all_guestpass_info = lib.zd.ga.get_all_guestpasses(self.zd)

            all_guestpass_info_on_zd = {}
            for guest_full_name in all_guestpass_info.iterkeys():
                all_guestpass_info_on_zd[guest_full_name] = [all_guestpass_info[guest_full_name]['created_by'],
                                                             all_guestpass_info[guest_full_name]['wlan']
                                                             ]


            logging.debug('All guest pass information on Zone Director WebUI are: %s' % all_guestpass_info_on_zd)
            expected_info = all_guestpass_info_on_zd

        logging.info('Download the generated guest passes record file')
        record_file_path = lib.zd.ga.download_generated_guestpass_record(self.zd, self.conf['username'], self.conf['password'])

        logging.debug("Parse the CSV file")
        all_info_in_file = self._parseCSVFile(record_file_path)

        logging.info('Verify the guest passes in the record file against those on WebUI')
        if not self._verifyInfo(all_info_in_file, expected_info, keyOnly):
            errmsg = 'Expected guest passes, %s, were not found. '
            errmsg = errmsg % self.errkey
            self.errmsg = self.errmsg + errmsg
            logging.info(errmsg)
            return

        passmsg = '%s usernames and guest passes are created and updated to ZD WebUI correctly. '
        passmsg = passmsg % self.conf['number_profile']
        self.passmsg = self.passmsg + passmsg
        logging.info(passmsg)


    #
    # cleanup()
    #
    def _cfgRemoveFiles(self):
        ZD_GuestAccess_Common._cfgRemoveFiles(self)


    def _cfgRemoveAllConfigOnZD(self):
        ZD_GuestAccess_Common._cfgRemoveAllConfigOnZD(self)

        if self.modified_gprints:
            logging.info("Restore the Guest Pass Printouts to original configuration")
            removed_gprints = []
            for x in self.modified_gprints:
                if len(x) == 1:
                    # This item is added to the list
                    removed_gprints.append(x[0])
                elif len(x) == 2:
                    # This item is modified from one existing item
                    # Restore it
                    lib.zd.ga.edit_guestpass_printout(self.zd, x[0], x[1])
            if removed_gprints:
                # Remove the whole list
                lib.zd.ga.remove_guestpass_printout(self.zd, removed_gprints)



