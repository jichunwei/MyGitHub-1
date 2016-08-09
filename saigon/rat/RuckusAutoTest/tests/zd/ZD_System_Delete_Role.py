# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_System_Delete_Role use to test if we could clone a new role with existing role
             and using that role or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'role_name': role name if None mean that we will delete all role.

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
            - Create if the role does not exist
         2. Test procedure:
            - Delete the role
            - Check if the new role is removed out the roles table or not
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

class ZD_System_Delete_Role(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf
        # Create roles as existing roles for testing\
        role_list = self.testbed.components['ZoneDirector'].get_role()
        self.delete_all = True
        if self.delete_all:
            if len(role_list) < 4:
                for i in range(3):
                    self.testbed.components['ZoneDirector'].create_role(rolename = 'testrole_%d' % i)
        if self.conf.has_key('rolename'):
            self.delete_all = False
            if self.conf['rolename'] not in role_list:
                self.testbed.components['ZoneDirector'].create_role(rolename = self.conf['rolename'])

    def test(self):
        # Remove all Users
        self.testbed.components['ZoneDirector'].remove_all_users()

        if self.delete_all:
            # Delete all role
            role_list_before = self.testbed.components['ZoneDirector'].get_role()
            try:
                self.testbed.components['ZoneDirector'].remove_all_roles()
            except:
                return 'FAIL', 'Can not delete all role'
            role_list = self.testbed.components['ZoneDirector'].get_role()
            for i in role_list_before:
                if i != 'Default' and i in role_list:
                    return 'FAIL', 'After be deleted all, there still has roles:  \'%s\' in the roles table'\
                           % repr(role_list)

            return 'PASS', ''

        else:
            # Delete role
            #try:
            self.testbed.components['ZoneDirector'].remove_all_roles(self.conf['rolename'])
            #except:
                #return 'FAIL', 'Can not delete the role: %s' % self.conf['rolename']
            # Check if the new role have on roles table or not
            role_list = self.testbed.components['ZoneDirector'].get_role()
            if self.conf['rolename'] in role_list:
                return 'FAIL', 'After be deleted, there still has role \'%s\' in the roles table'\
                       % self.conf['rolename']

            return 'PASS', ''
    def cleanup(self):
        pass


