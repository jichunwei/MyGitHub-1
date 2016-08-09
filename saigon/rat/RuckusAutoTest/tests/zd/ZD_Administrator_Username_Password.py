# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_Administrator_Username_Password Test class tests the ability of the Zone Director to configure the
             username and password of the administrator account

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'verify_username': a boolean value indicates to verify username of the account
                    'verify_password':  a boolean value indicates to verify password of the account
   Result type: PASS/FAIL/ERROR
   Results: PASS: if the username/password can be changed successfully; the username/password can be
                  used to login the ZD's webui
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Record current configuration of the administrator account
   2. Test:
       - For each valid username/password, try to configure to use it
       - If the username/password has been changed successfully, try to login to the ZD with it
       - Restore the configuration of the administrator account to the original values
   3. Cleanup:

"""

import os
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_Administrator_Username_Password(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._backupConfig()

    def test(self):
        if self.valid_usernames and self.invalid_usernames:
            self._test_usernames(self.valid_usernames, positive_test = True)
            self._test_usernames(self.invalid_usernames, positive_test = False)

        if self.valid_passwords and self.invalid_passwords:
            self._testPasswords(self.valid_passwords, positive_test = True)
            self._testPasswords(self.invalid_passwords, positive_test = False)

        if self.fail_msg:
            return ("FAIL", self.fail_msg.strip())
        return ("PASS", "")

    def cleanup(self):
        if self.current_admin_cfg:
            self.current_admin_cfg['admin_old_pass'] = self.last_working_password
            self.zd.set_admin_cfg(self.current_admin_cfg)

    def _cfgInitTestParams(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.valid_usernames = self.invalid_usernames = None
        self.valid_passwords = self.invalid_passwords = None
        self.current_admin_cfg = None
        self.last_working_password = self.zd.password
        self.fail_msg = ""
        # JLIN@20081112 change invalid username "zd_admin" to valid, invalid password "zd@admin", "zd_admin", "zd-admin" to valid
        if conf.has_key('verify_username') and conf['verify_username']:
            self.valid_usernames = ["zdadmin", "zdadmin123", "zd.admin.123", "zd_admin",
                                    "%s%s" % (utils.make_random_string(1, "alpha"), utils.make_random_string(31, "alnum"))]
            self.invalid_usernames = [".zdadmin", "123zdadmin", "zd~admin", "zd`admin", "zd!admin", "zd@admin",
                                      "zd#admin", "zd$admin", "zd%admin", "zd^admin", "zd&admin", "zd*admin",
                                      "zd(admin", "zd)admin", "zd-admin", "zd+admin", "zd=admin",
                                      "zd{admin", "zd[admin", "zd}admin", "zd]admin", "zd|admin", "zd\\admin",
                                      "zd:admin", "zd;admin", "zd\"admin", "zd'admin", "zd<admin", "zd,admin",
                                      "zd>admin", "zd?admin", "zd/admin",
                                      "%s%s" % (utils.make_random_string(1, "alpha"), utils.make_random_string(32, "alnum"))]
        elif conf.has_key('verify_password') and conf['verify_password']:
            self.valid_passwords = ["zdadmin", "zdadmin123", "zd.admin.123", "zd@admin", "zd_admin", "zd-admin", 
                                      "zd admin", "zd~admin", "zd`admin", "zd!admin",
                                      "zd#admin", "zd$admin", "zd%admin", "zd^admin", "zd&admin", "zd*admin",
                                      "zd(admin", "zd)admin", "zd+admin", "zd=admin",
                                      "zd{admin", "zd[admin", "zd}admin", "zd]admin", "zd|admin", "zd\\admin",
                                      "zd:admin", "zd;admin", "zd\"admin", "zd'admin", "zd<admin", "zd,admin",
                                      "zd>admin", "zd?admin", "zd/admin", utils.make_random_string(32, "alnum")]
            self.invalid_passwords = ["zd", "123", "", utils.make_random_string(33, "alnum")]
        else:
            raise Exception("Test parameter not found")

    def _backupConfig(self):
        self.current_admin_cfg = self.zd.get_admin_cfg()
        # The password read from ZD's webUI is all *
        # Replace it with the infor stored on ZD object
        self.current_admin_cfg['admin_pass1'] = self.zd.password
        self.current_admin_cfg['admin_pass2'] = self.zd.password

    def _test_usernames(self, username_list, positive_test):
        for username in username_list:
            # Change admin's username to a new one
            logging.info("Try to set administrator account's name to '%s'" % username)
            try:
                admin_info = {'admin_name': username, 'admin_old_pass': self.zd.password}
                self.zd.set_admin_cfg(admin_info)
            except Exception, e:
                logging.info("Catched exception: %s" % e.message)
                if positive_test:
                    self.fail_msg += "The ZD didn't accept the valid username '%s'. " % username
                continue

            logging.info("Try to login to the ZD with the new administrator's username")
            self._testLogin(username = username, valid = positive_test)

            logging.info("Restore the administrator's username to original value")
            admin_info = {'admin_name': self.current_admin_cfg['admin_name'], 'admin_old_pass': self.zd.password}
            self.zd.set_admin_cfg(admin_info)

    def _testPasswords(self, password_list, positive_test):
        for password in password_list:
            # Change admin's username to a new one
            logging.info("Try to set administrator account's password to '%s'" % password)
            try:
                admin_info = {'admin_pass1': password, 'admin_pass2': password, 'admin_old_pass': self.last_working_password}
                self.zd.set_admin_cfg(admin_info)
            except Exception, e:
                logging.info("Catched exception: %s" % e.message)
                if positive_test:
                    self.fail_msg += "The ZD didn't accept the valid password '%s'. " % password
                continue

            logging.info("Try to login to the ZD with the new administrator's password")
            self._testLogin(password = password, valid = positive_test)

            logging.info("Restore the administrator's password to original value")
            admin_info = {'admin_pass1':self.current_admin_cfg['admin_pass1'],
                          'admin_pass2':self.current_admin_cfg['admin_pass2'],
                          'admin_old_pass': self.last_working_password}
            self.zd.set_admin_cfg(admin_info)
            self.last_working_password = admin_info['admin_pass1']

    def _testLogin(self, username = "", password = "", valid = True):
        current_username = self.zd.username
        current_password = self.zd.password

        if username:
            self.zd.username = username
        elif password:
            self.zd.password = password
        else:
            logging.debug("No parameter was given")
            return

        try:
            self.zd.login()
            login_ok = True
            logging.info("Logged in successfully")
            self.last_working_password = self.zd.password
        except:
            login_ok = False
            logging.info("Unable to login")

        self.zd.username = current_username
        self.zd.password = current_password

        if username:
            s = "username '%s'" % username
        else:
            s = "password '%s'" % password
        if valid and not login_ok:
            self.fail_msg += "Unable to login with valid %s. " % s
        if not valid and login_ok:
            self.fail_msg += "It was able to login with invalid %s. " % s

