# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Clone_User use to test if we could clone a new user using an existed user role
             and using that user or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'user': The information of user that we want to create.
                            'username': user name
                            'password': user password
                            'fullname': full name of user
                    'exist_user': user name of the existed user that we want to clone from.

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If the info get to clone is not match with the info of user we clone from, or
   - If after we clone an user, this user doesn't exist on the user table, or
   - If we could not access to the 'Guest Pass generation URL' by use the new user information.
   PASS:
   - If after we clone user, user exists on the user table and we access successfully
   to the 'Guest Pass generation URL' by use the new user information.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Delete if the user existed
            - Create a new one if the 'exist_user' doesn't have
         2. Test procedure:
            - Clone new user with 'user_info' using the 'exist_user'
            - Check if the new user is added to the user table or not
            - Access to the 'Guest Pass generation URL' by use the new user information.
         3. Cleanup:
            - delete user

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

class ZD_System_Clone_User(Test):
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
        
        self.user_info = conf['user']
        # Check and delete user if it existed
        user_list = self.testbed.components['ZoneDirector'].get_user()
        if self.user_info['username'] in user_list:
            self.testbed.components['ZoneDirector'].delete_user(self.user_info['username'])

        # Check and create a new one with password is 'lab4man1' with default role if the 'exist_user' doesn't exist
        self.exist_user = conf['exist_user']
        self.existed = True
        if conf['exist_user'] not in user_list:
            self.existed = False
            self.testbed.components['ZoneDirector'].create_user(conf['exist_user'], utils.make_random_string(10, "alnum"))

    def test(self):
        """
        """
        logging.info('Testing..........................................')
        self._cfg_create_default_guessaccess_wlan()
        # Clone new user using an existed user
        if self.user_info.has_key('fullname'):
            fullname = self.user_info['fullname']
        else:
            fullname = ''
        try:
            self.testbed.components['ZoneDirector'].clone_user(self.exist_user, self.user_info['username'], self.user_info['password'], fullname)
        except:
            return ('FAIL', 'Can not clone user: \'%s\' using the existed user: \'%s\''
                    % (self.user_info['username'], self.exist_user))
        logging.info('Clone user: \'%s\' using the existed user: \'%s\' successfully ...'
                     % (self.user_info['username'], self.exist_user))

        # Check if we could access to the 'Guess pass generation' page or not
        if self.testbed.components['ZoneDirector'].test_user(self.user_info['username'], self.user_info['password']):
            return 'PASS', ''
        else:
            return 'FAIL', 'User \'%s\' is cloned using existing user: \'%s\ %s,'\
                   % (self.user_info['username'], self.exist_user, 'but it cannot login to \'Guess pass generation\' page')


    def cleanup(self):
        """
        """
        logging.info('Cleaning up the testing environment...........................')
        user_list = self.testbed.components['ZoneDirector'].get_user()
        if self.existed == False and (self.exist_user in user_list):
            self.testbed.components['ZoneDirector'].delete_user(self.exist_user)
        if self.user_info['username'] in user_list:
            self.testbed.components['ZoneDirector'].delete_user(self.user_info['username'])
            logging.info('Delete user \'%s\' successfully ...' % self.user_info['username'])
        
        self.testbed.components['ZoneDirector'].remove_all_users()
        self.testbed.components['ZoneDirector'].remove_all_roles()
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

