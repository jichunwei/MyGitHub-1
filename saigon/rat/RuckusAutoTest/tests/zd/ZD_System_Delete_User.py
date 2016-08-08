# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Delete_User use to test if we could create an existing user or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'username': the user name that we want to delete.
                    If there no parameter, it mean that we will delete all user.

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If after we delete user(s), user(s) still exist on the user table, or,
   - If we could access to the 'Guest Pass generation URL' by use the deleted user information.
   PASS:
   - If after we delete user(s), user(s) must be removed on the user table and we couldn't access
   to the 'Guest Pass generation URL' by use the deleted user information.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Create the new one(s) if the user doesn't exist
         2. Test procedure:
            - Delete user with 'username' or delete all users when parameter is null
            - Check if the deleted user(s) be removed out of the user table or not
            - Access to the 'Guest Pass generation URL' by use the deleted user information.
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

class ZD_System_Delete_User(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        """
        """
        logging.info('Configuration.......................................')

        # Check and delete user if it existed
        self.conf = conf
        user_list = self.testbed.components['ZoneDirector'].get_user()
        self.testpass = utils.make_random_string(10, "alnum")
        logging.debug("testpass %s" % self.testpass)
        if conf.has_key('username'):
            self.del_all = False
            if conf['username'] not in user_list:
                logging.info('Create user \'%s\' for testing ... ' % conf['username'])
                self.testbed.components['ZoneDirector'].create_user(self.conf['username'], self.testpass)
        else:
            self.del_all = True
            if len(user_list) < 3 :
                logging.info('Create some more users for testing ... ')
                self.testbed.components['ZoneDirector'].create_user('test', self.testpass, number_of_users = 3)
        self.user_list = self.testbed.components['ZoneDirector'].get_user()
        logging.info('List of users that we have on our system: %s' % repr(self.user_list))

    def test(self):
        """
        """
        logging.info('Testing..........................................')
        # Delete user
        if self.del_all:
            try:
                self.testbed.components['ZoneDirector'].remove_all_users()
            except:
                return 'ERROR', 'Can not delete all users'
            user_list = self.testbed.components['ZoneDirector'].get_user()
            if len(user_list) == 0:
                test_user = [random.choice(self.user_list), self.testpass]
                logging.info('Delete all users successfully ...')
            else:
                return 'FAIL', 'After delete all users, we still see %d users: %s on the user table'\
                       % (len(user_list), repr(user_list))
        else:
            try:
                self.testbed.components['ZoneDirector'].delete_user(self.conf['username'])
            except:
                return 'ERROR', 'Can not delete user: \'%s\'' % self.conf['username']
            user_list = self.testbed.components['ZoneDirector'].get_user()
            if self.conf['username'] in user_list:
                return 'FAIL', 'After delete, user \'%s\' is not removed out of user table' % self.conf['username']
            else:
                test_user = [self.conf['username'], self.testpass]
                logging.info('Delete user \'%s\' successfully ...' % self.conf['username'])

        # Check if we could access to the 'Guess pass generation' page or not
        if self.testbed.components['ZoneDirector'].test_user(test_user[0], test_user[1]):
            return 'FAIL', 'User \'%s\' is deleted, but it could login to \'Guess pass generation\' page' % test_user[0]
        else:
            return 'PASS', ''

    def cleanup(self):
        """
        """
        logging.info('Cleaning up the testing environment...........................')


