"""
Description: ZD_GuestAccess_GuestPassPrintout test class tests the operations related to Guest Pass Printouts

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: testcase: name of the test case
                    tag_list: list of tag names embedded in the Guest Pass Printout template, optional
                    template_fname: name of the template file provided by the ZD, optional
                    filesize: size of the HTML file, used by maximum filesize test case
                    number_of_entry: used by the importing maximum Guest Pass Printout test cases

   Result type: PASS/FAIL
   Results: PASS: the Guest Pass Printouts can be created/removed/cloned properly
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all non-default configuration
       - Record current Guest Pass Printouts
   2. Test:
       - Download the default template
       - Try to add/remove/clone a new Guest Pass Printout
       - Try to open different printouts and validate their content when generating the Guest Pass
   3. Cleanup:
       - Remove all non-default configuration created during the execution
"""


import logging
import time
import traceback
import os

import tempfile

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.tests.zd.ZD_GuestAccess_Common import ZD_GuestAccess_Common

class ZD_GuestAccess_GuestPassPrintout(ZD_GuestAccess_Common):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'testcase': 'name of the test case',
                             'tag_list': 'list of tag names embedded in the Guest Pass Printout template, optional',
                             'template_fname': 'name of the template file provided by the ZD, optional',
                             'filesize': 'size of the HTML file, used by maximum filesize test case',
                             'number_of_entry': 'used by the importing maximum Guest Pass Printout test cases'}


    def config(self, conf):
        # the super method should be called first
        ZD_GuestAccess_Common.config(self, conf)

        self.tc2f = {
            'delete-default-gprint': self._testDeleteDefaultGuestPassPrintout,
            'edit-default-gprint': self._testEditDefaultGuestPassPrintout,
            'clone-default-gprint': self._testCloneDefaultGuestPassPrintout,
            'download-gprint-sample': self._testDownloadSampleGuestPassPrintout,
            'import-valid-file': self._testImportFromValidHTMLFile,
            'import-invalid-file': self._testImportFromInvalidHTMLFile,
            'delete-customized-gprint': self._testDeleteCustomizedGuestPassPrintout,
            'edit-customized-gprint': self._testEditCustomizedGuestPassPrintout,
            'clone-customized-gprint': self._testCloneCustomizedGuestPassPrintout,
            'import-maximum-filesize': self._testImportMaximumSizeHTMLFile,
            'import-maximum-entries': self._testImportMaximumGuestPassPrintoutEntries,
            'search-by-name': self._testSearchPrintoutBasedOnName,
            'select-gprints': self._testSelectGuestPassPrintouts,
        }

        self._cfgBackupConfigOnZD()

        self._cfgCreateAuthenticationUser()


    def test(self):
        return ZD_GuestAccess_Common.test(self)


    def cleanup(self):
        self._cfgRemoveAllConfigOnZDAtCleanup()
        self._cfgRemoveFiles()


    def _cfgInitTestParams(self, conf):
        # the super method should be called first to initialize common variables
        ZD_GuestAccess_Common._cfgInitTestParams(self, conf)

        # additional params should be put below
        if conf is None:
            conf = self._getDefaultConfig()
            self.conf = conf
        else:
            self.conf.update(conf)

        self.conf.update({'template_fname': 'guestpass_print.html',
                          'tag_list': ['{GP_GUEST_NAME}',
                                       '{GP_GUEST_KEY}',
                                       '{GP_IF_EFFECTIVE_FROM_CREATION_TIME}',
                                       '{GP_ELSEIF_EFFECTIVE_FROM_FIRST_USE}',
                                       '{GP_ENDIF_EFFECTIVE}',
                                       '{GP_VALID_DAYS}',
                                       '{GP_VALID_TIME}',
                                       '{GP_GUEST_WLAN}'],
                          })

        self.def_gprints = []
        self.sample_fpath = None
        self.temp_fpath = None
        self.modified_gprints = []

        self.gp_conf = {'username': self.conf['username'],
                        'password': self.conf['password'],
                        'guest_fullname': 'Michael Jackson',
                        'duration': '5',
                        'duration_unit': 'Days',
                        'remarks': 'He will sing us "Heal The World"',
                        'key': '',
                        'validate_gprints': True,
                        }


        self.wlan_cfg = conf['wlan_cfg']
        if self.wlan_cfg == {} or not self.wlan_cfg.has_key('ssid'):
            self.wlan_cfg.update({'ssid': 'wlan-gpprintout', 'type': 'guest'})


    def _getDefaultConfig(self):
        conf = {'testcase': '',
                'wlan_cfg': {},
                'auth_server_type': 'local',
                'auth_server_info': {},
                'username': 'local.username',
                'password': 'local.password',
                'number_profile': 5,
                'max_gp_allowable': 1250,
                'guestpass_key': 'ABCDE-FGHIJ',
                }
        return conf


    def _cfgRemoveAllConfigOnZD(self):
        ZD_GuestAccess_Common._cfgRemoveAllConfigOnZD(self)


    def _cfgBackupConfigOnZD(self):
        logging.info("Record the list of the existing Guest Pass Printouts")
        self.def_gprints = lib.zd.ga.get_list_of_guestpass_printout(self.zd)


    def _cfgCreateWlanOnZD(self):
        return ZD_GuestAccess_Common._cfgCreateWlanOnZD(self)


    def _cfgCreateAuthenticationUser(self):
        if self.conf['testcase'] == 'select-gprints':
            logging.info("Create a user account used for generating Guest Pass on the ZD")
            self.zd.create_user(self.conf['username'], self.conf['password'])


    def _cfgAuthServerOnZD(self):
        pass

#
# test()
#
    def _testDeleteDefaultGuestPassPrintout(self):
        logging.info("Try to delete the default Guest Pass Printout")
        try:
            lib.zd.ga.remove_guestpass_printout(self.zd, "Default")
            self.errmsg = "It was able to delete the default Guest Pass Printout"
            return

        except Exception, e:
            expect_msg = self.zd.messages["E_GuestPrintIsDefault"]
            if expect_msg not in e.message:
                raise

            self.passmsg += "The ZD didn't allow removing the default Guest Pass Printout. "

        logging.info("Make sure the entry still exists in the table")
        gprints = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
        gprint_names = [gp['name'] for gp in gprints]
        if "Default" not in gprint_names:
            self.errmsg = "The default Guest Pass Printout was not shown in the table after performing the remove operation"
        else:
            self.passmsg += "The default Guest Pass Printout still existed in the table. "


    def _testEditDefaultGuestPassPrintout(self):
        logging.info("Try to edit the default Guest Pass Printout")
        new_cfg = {'name':'English Default', 'description': 'English version for English users'}
        try:
            lib.zd.ga.edit_guestpass_printout(self.zd, 'Default', new_cfg)
            old_gprint_cfg = [gp for gp in self.def_gprints if gp['name'] == 'Default'][0]
            self.modified_gprints.append([new_cfg['name'], old_gprint_cfg])
            self.passmsg += "It was able to edit the default Guest Pass Printout. "
        except Exception, e:
            self.errmsg = "Unable to edit the default Guest Pass Printout: %s" % e.message


    def _testDownloadSampleGuestPassPrintout(self):
        logging.info("Try to download the sample Customized Guest Pass Printout")
        try:
            self.sample_fpath = lib.zd.ga.download_guestpass_printout_sample(self.zd, self.conf['template_fname'])
        except:
            msg = "Unable to download the sample Customized Guest Pass Printout"
            logging.info(msg)
            self.errmsg = msg
            return

        logging.info("Verify the TAGs embedded inside the downloaded template")
        try:
            sample_f = file(self.sample_fpath, "rt")
            sample_data = sample_f.read()
            sample_f.close()
        except:
            logging.info("Unable to read the file [%s]" % self.sample_fpath)
            raise

        l = []
        for tag in self.conf['tag_list']:
            if tag not in sample_data: l.append(tag)
        if l:
            msg = "The following tags were not found in the template file: %s" % l
            logging.info(msg)
            self.errmsg = msg

        self.passmsg += "The template was downloaded successfully. "


    def _testCloneDefaultGuestPassPrintout(self):
        self._testDownloadSampleGuestPassPrintout()
        if self.errmsg:
            raise Exception(self.errmsg)

        logging.info("Try to clone a new Guest Pass Printout from the default version")
        new_cfg = {'name':'New English', 'description': 'English version for English users', 'html_file': self.sample_fpath}
        try:
            lib.zd.ga.clone_guestpass_printout(self.zd, 'Default', new_cfg)
            self.modified_gprints.append([new_cfg['name'], ])
            self.passmsg += "It was able to clone a new Guest Pass Printout from the default version. "
        except Exception, e:
            self.errmsg = "Unable to clone a new Guest Pass Printout from the default version: %s" % e.message


    def _makeInvalidPrintout(self):
        fd, path = tempfile.mkstemp(suffix = ".bin")
        os.write(fd, os.urandom(5000))
        os.close(fd)
        self.temp_fpath = path


    def _testImportFromValidHTMLFile(self):
        # Download the sample printout
        # The file will be used to create the valid/invalid printouts
        self._testDownloadSampleGuestPassPrintout()
        if self.errmsg:
            raise Exception("Unable to download the Guest Pass Printout sample")

        logging.info("Try to create a new Guest Pass Printout entry from the sample version")
        new_cfg = {'name':'New English', 'description': 'English version for English users', 'html_file': self.sample_fpath}
        try:
            lib.zd.ga.create_guestpass_printout(self.zd, new_cfg)
            self.modified_gprints.append([new_cfg['name'], ])
            self.passmsg += "The valid printout was imported successfully. "
        except Exception, e:
            self.errmsg = "Unable to import the valid printout: %s" % e.message


    def _testImportFromInvalidHTMLFile(self):
        # Generate an invalid printout file
        self._makeInvalidPrintout()
        logging.info("Try to create a new Guest Pass Printout entry from an invalid file")
        new_cfg = {'name':'New English', 'description': 'English version for English users', 'html_file': self.temp_fpath}
        try:
            lib.zd.ga.create_guestpass_printout(self.zd, new_cfg)
            self.errmsg = "It was able to create a Guest Pass Printout from an invalid HTML file"
        except Exception, e:
            self.passmsg += "The invalid HTML file was not imported to a Guest Pass Printout. "


    def _testDeleteCustomizedGuestPassPrintout(self):
        # Create a new Customized Guest Pass Printout
        self._testImportFromValidHTMLFile()
        if self.errmsg:
            raise Exception("Unable to create a customized Guest Pass Printout")
        new_gprint_name = self.modified_gprints[0][0]

        logging.info("Try to remove the customized Guest Pass Printout")
        try:
            lib.zd.ga.remove_guestpass_printout(self.zd, new_gprint_name)
            del self.modified_gprints[0]
            self.passmsg += "The entry was removed successfully. "
        except Exception, e:
            self.errmsg = "Unable to remove the customized Guest Pass Printout: %s" % e.message
            return

        logging.info("Make sure the entry disappears from the table")
        gprints = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
        gprint_names = [gp['name'] for gp in gprints]
        if new_gprint_name in gprint_names:
            self.errmsg = "The customized Guest Pass Printout still existed in the table"
        else:
            self.passmsg += "The default Guest Pass Printout disappeared from the table. "


    def _testEditCustomizedGuestPassPrintout(self):
        # Create a new Customized Guest Pass Printout
        self._testImportFromValidHTMLFile()
        if self.errmsg:
            raise Exception("Unable to create a customized Guest Pass Printout")
        new_gprint_name = self.modified_gprints[0][0]

        logging.info("Try to edit the default Guest Pass Printout")
        new_cfg = {'name':'Updated %s' % new_gprint_name,
                   'description': 'For anyone that speaks English'}
        try:
            lib.zd.ga.edit_guestpass_printout(self.zd, new_gprint_name, new_cfg)
            self.modified_gprints[0][0] = new_cfg['name']
            self.passmsg += "It was able to edit the customized Guest Pass Printout. "
        except Exception, e:
            self.errmsg = "Unable to edit the customized Guest Pass Printout: %s" % e.message


    def _testCloneCustomizedGuestPassPrintout(self):
        # Create a new Customized Guest Pass Printout
        self._testImportFromValidHTMLFile()
        if self.errmsg:
            raise Exception("Unable to create a customized Guest Pass Printout")
        new_gprint_name = self.modified_gprints[0][0]

        logging.info("Try to clone a new Guest Pass Printout from another customized version")
        new_cfg = {'name':'Updated %s' % new_gprint_name,
                   'description': 'For anyone that speaks English',
                   'html_file': self.sample_fpath}
        try:
            lib.zd.ga.clone_guestpass_printout(self.zd, new_gprint_name, new_cfg)
            self.modified_gprints.append([new_cfg['name'], ])
            self.passmsg += "It was able to clone a new Guest Pass Printout from another customized version. "
        except Exception, e:
            self.errmsg = "Unable to clone a new Guest Pass Printout from another customized version: %s" % e.message


    def _appendToPrintoutHTMLFile(self, size):
        tf = open(self.sample_fpath, "rb")
        data = tf.read()
        tf.close()
        data = data.replace("</body>", "%s</body>" % ("A" * (size - len(data))))
        tf = open(self.sample_fpath, "wb")
        tf.write(data)
        tf.close()


    def _testImportMaximumSizeHTMLFile(self):
        # Download the sample printout
        # The file will be used to create the valid/invalid printouts
        self._testDownloadSampleGuestPassPrintout()
        if self.errmsg:
            raise Exception("Unable to download the Guest Pass Printout sample")

        filesize = int(self.conf['filesize'])

        for size in [filesize - 1, filesize, filesize + 1]:
            logging.info("Try to create a new Guest Pass Printout entry from an HTML file of size %s" % size)
            self._appendToPrintoutHTMLFile(size)
            new_cfg = {'name':'New English - %s' % size,
                       'description': 'English version for English users',
                       'html_file': self.sample_fpath}
            try:
                lib.zd.ga.create_guestpass_printout(self.zd, new_cfg)
                self.modified_gprints.append([new_cfg['name'], ])
                if size <= filesize:
                    self.passmsg += "The valid HTML Printout file [size %s] was imported successfully. " % size
                else:
                    self.errmsg = "The invalid HTML Printout file [size %s] was imported without any problem" % size
                    return
            except Exception, e:
                if size <= filesize:
                    self.errmsg = "Unable to import the valid HTML Printout file [size %s]: %s" % (size, e.message)
                    return
                else:
                    self.passmsg += "The invalid HTML Printout file [size %d] was not imported. " % size


    def _testImportMaximumGuestPassPrintoutEntries(self, verify_exceeding = True):
        # Download the sample printout
        # The file will be used to create the valid/invalid printouts
        self._testDownloadSampleGuestPassPrintout()
        if self.errmsg:
            raise Exception("Unable to download the Guest Pass Printout sample")

        number_of_entry = int(self.conf['number_of_entry'])
        number_of_needed_entry = number_of_entry - len(self.def_gprints)

        logging.info("Number of existing Guest Pass Printout in the table: %s" % len(self.def_gprints))
        logging.info("Try to create another %s Guest Pass Printout entries" % number_of_needed_entry)
        new_cfg = {'description': 'English version for English users', 'html_file': self.sample_fpath}
        for i in range(number_of_needed_entry):
            new_cfg['name'] = "English - %s" % (i + 1)
            try:
                lib.zd.ga.create_guestpass_printout(self.zd, new_cfg)
                self.modified_gprints.append([new_cfg['name'], ])
            except Exception, e:
                self.errmsg = "Unable to create the Guest Pass Printout [%s]: %s" % (new_cfg['name'], e.message)
                return
        self.passmsg += "Another %s Guest Pass Printouts were added successfully. " % number_of_needed_entry

        logging.info("Make sure the Printouts are added correctly")
        gprints = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
        if len(gprints) != number_of_entry:
            self.errmsg = "The number of Guest Pass Printouts shown in the table was %s instead of %s" % (len(gprints), number_of_entry)
            return

        if verify_exceeding:
            logging.info("Try to create one more Guest Pass Printout")
            new_cfg['name'] = "English - bad"
            try:
                lib.zd.ga.create_guestpass_printout(self.zd, new_cfg)
                self.modified_gprints.append([new_cfg['name'], ])
                self.errmsg = "The ZD allowed to add one more Guest Pass Printout besides %s existing entries" % number_of_entry
                return
            except Exception, e:
                self.passmsg += "The ZD didn't allow to add one more Guest Pass Printout besides %s existing entries. " % number_of_entry


    def _testSearchPrintoutBasedOnName(self):
        # Try to create a few Printouts which will be used in the search function
        self.conf['number_of_entry'] = 5
        self._testImportMaximumGuestPassPrintoutEntries(verify_exceeding = False)
        if self.errmsg:
            raise Exception(self.errmsg)

        current_gprints = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
        gprint_names = [gp['name'] for gp in current_gprints]
        for name in gprint_names:
            # List of names that should be shown after applying the filter
            expected_names = [x for x in gprint_names if name in x]

            logging.info("Try to get list of Guest Pass Printouts after applying the filter [%s]" % name)
            filtered_names = [gp['name'] for gp in lib.zd.ga.get_list_of_guestpass_printout(self.zd, name)]

            odd_names = [x for x in expected_names if x not in filtered_names]
            if odd_names:
                logging.info("The expected name list: %s" % expected_names)
                logging.info("The filtered name list: %s" % filtered_names)
                self.errmsg = "The filtered names were not as expected when applying the filter [%s]" % name
                return

        self.passmsg += "The ZD showed the Guest Pass Printouts correctly when applying filters. "


    def _testSelectGuestPassPrintouts(self):
        # Try to create a few Printouts which will be used by the Generate Guest Pass function
        self.conf['number_of_entry'] = 5
        self._testImportMaximumGuestPassPrintoutEntries(verify_exceeding = False)
        if self.errmsg:
            raise Exception(self.errmsg)

        logging.info("Generate a Guest Pass on the ZD")
        try:
            info = self.zd.generate_guestpass(**self.gp_conf)
            self.passmsg += "All the Guest Pass Printouts were shown correctly in the Guest Pass Generation page. "
        except Exception, e:
            if "in the Guest Pass Printout" in e.message:
                self.errmsg = e.message
            else:
                raise

#
# cleanup()
#
    def _cfgRemoveAllConfigOnZDAtCleanup(self):
        if self.conf['testcase'] == 'select-gprints':
            logging.info("Remove all Guest Passes created on the Zone Director")
            self.zd.remove_all_guestpasses()

            logging.info("Remove all user accounts")
            self.zd.remove_all_users()

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


