# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Create_User use to test if we could create a new user with default role
             and using that user or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'user': The information of user that we want to create.
                            'username': user name
                            'password': user password
                            'fullname': full name of user

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If after we create new user, this user doesn't exist on the user table, or,
   - If we could not access to the 'Guest Pass generation URL' by use the new user information.
   PASS:
   - If after we create new user, user exists on the user table and we access successfully
   to the 'Guest Pass generation URL' by use the new user information.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Delete if the user existed
         2. Test procedure:
            - Create new user with 'user_info'
            - Check if the new user is added to the user table or not
            - Access to the 'Guest Pass generation URL' by use the new user information.
         3. Cleanup:

    How it was tested:

"""
import os
import time
import logging
import random
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils

class ZD_System_Create_User(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        """
        """
        logging.info('Configuration.......................................')
        # Delete all wlan, all users and all roles that we have in our system
        self.testbed.components['ZoneDirector'].remove_all_users()
        self.testbed.components['ZoneDirector'].remove_all_roles()
        self.testbed.components['ZoneDirector'].remove_all_wlan()
        
        if conf.has_key('user'):
            self.create_max = False
            self.user_info = conf['user']
            # Check and delete user if it existed
            user_list = self.testbed.components['ZoneDirector'].get_user()
            if self.user_info['username'] in user_list:
                self.testbed.components['ZoneDirector'].delete_user(self.user_info['username'])
                logging.info('Delete an existing user \'%s\' on our system successfuly')
        else:
            self.create_max = True
            if conf.has_key('max_users'):
                self.max_users = conf['max_users']
            else:
                self.max_users = 1024
            self.testbed.components['ZoneDirector'].remove_all_users()
            logging.info('Delete all users before create max number (%d) of users' % self.max_users)

    def test(self):
        """
        """
        logging.info('Testing..........................................')
        self._cfg_create_default_guessaccess_wlan()
        # Create new user
        if self.create_max == False:
            if self.user_info.has_key('fullname'):
                fullname = self.user_info['fullname']
            else:
                fullname = ''
            try:
                self.testbed.components['ZoneDirector'].create_user(self.user_info['username'], self.user_info['password'], fullname)
                test_user = [[self.user_info['username'], self.user_info['password']]]
            except:
                return 'ERROR', 'Can not create user: \'%s\'' % self.user_info['username']
            logging.info('Create user \'%s\' successfully ...' % self.user_info['username'])
        else:
            number_users = self.testbed.components['ZoneDirector'].get_number_users()
            print number_users
            password = utils.make_random_string(10, 'alpha')
            create_number = self.max_users - number_users
            if create_number > 0:
                try:
                    self.testbed.components['ZoneDirector'].create_user('test', password, number_of_users = create_number)
                except:
                    result, message = 'FAIL', 'Can not create %d users' % (number_users + 1)

            number_users = self.testbed.components['ZoneDirector'].get_number_users()

            if number_users == self.max_users:
                user_list = self.testbed.components['ZoneDirector'].get_user()
                if number_users > 4:
                    test_user = [[user_list[0], password],
                                 [user_list[number_users / 4], password],
                                 [user_list[number_users / 2], password],
                                 [user_list[number_users - 1], password]]
                else:
                    test_user = [[i, password] for i in user_list]
                logging.info('Create %d user(s) successfully ...' % number_users)
            else:
                return 'FAIL', 'Number of users has been created is \'%d\', but not \'%d\'' % (number_users, self.max_users)

        # Check if we could access to the 'Guess pass generation' page or not
        for i in test_user:
            if self.testbed.components['ZoneDirector'].test_user(i[0], i[1]):
                result, message = 'PASS', ''
            else:
                result, message = 'FAIL', 'User \'%s\' is created, but it can not login to \'Guess pass generation\' page ...' % i[0]
                break

        return result, message

    def cleanup(self):
        """
        """
        logging.info('Cleaning up the testing environment...........................')
        #
        if not self.create_max:
            user_list = self.testbed.components['ZoneDirector'].get_user()
            if self.user_info['username'] in user_list:
                self.testbed.components['ZoneDirector'].delete_user(self.user_info['username'])
                logging.info('Delete user \'%s\' successfully ...' % self.user_info['username'])
        else:
            self.testbed.components['ZoneDirector'].remove_all_users()
            logging.info('Delete all user successfully ...')
        self.testbed.components['ZoneDirector'].remove_all_wlan()

    def _cfg_create_default_guessaccess_wlan(self):
        self.wlan1 = dict(ssid = 'Wlan1', auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                          key_index = "", key_string = "testpass",
                          username = "test1", password = "testpass",
                          ras_addr = "", ras_port = "", ras_secret = "", ad_addr = "",
                          ad_port = "", ad_domain = "")

        self.wlan1['use_web_auth'] = True
        self.wlan1['use_guest_access'] = True
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan1)
