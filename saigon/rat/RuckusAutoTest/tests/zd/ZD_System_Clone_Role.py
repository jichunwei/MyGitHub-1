# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Clone_Role use to test if we could clone a new role with existing role
             and using that role or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'role_name': role name
                    'exist_role': name of existing role

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If after we clone new role, this role doesn't exist on the role table, or,
   - If we could not access to the 'Guest Pass generation URL' by use the new role information.
   PASS:
   - If after we clone new role, role exists on the role table and we could apply it to a user.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Delete if the role existed
         2. Test procedure:
            - clone new role using existing role
            - Check if the new role is added to the roles table or not
            - Apply the role to a user
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

class ZD_System_Clone_Role(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        # Delete all users and all roles that we have in our system
        self.testbed.components['ZoneDirector'].remove_all_users()
        self.testbed.components['ZoneDirector'].remove_all_roles()

        self.conf = conf
        # Create a role as existing role for testing
        self.testbed.components['ZoneDirector'].create_role(rolename = self.conf['exist_role'])

    def test(self):
        # Create new role
        try:
            self.testbed.components['ZoneDirector'].clone_role(self.conf['exist_role'], self.conf['rolename'])
        except:
            return 'FAIL', 'Can not clone the role: %s' % self.conf['rolename']

        # Check if the new role have on roles table or not
        role_list = self.testbed.components['ZoneDirector'].get_role()
        if self.conf['rolename'] not in role_list:
            return 'FAIL', 'After be cloned there no role \'%s\' in the roles table' % self.conf['rolename']

        # Create a new user using the new role
        try:
            self.testuser = {'name': 'Test', 'password': 'testpass'}
            self.testbed.components['ZoneDirector'].create_user(self.testuser['name'], self.testuser['password'], \
                                                               role = self.conf['rolename'])
        except:
            return 'FAIL', 'Can not apply the role \'%s\' for user' % self.conf['rolename']

        return 'PASS', ''

    def cleanup(self):
        # Delete all user and role that we have
        self.testbed.components['ZoneDirector'].remove_all_users()
        self.testbed.components['ZoneDirector'].remove_all_roles()


