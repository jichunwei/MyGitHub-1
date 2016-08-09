# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will
# be used in report generation.

"""
Description: ZD_System_Create_Role use to test if we could create a new role
             and using that role or not.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
        'role': The information of role that we want to create.
        'name': role name
        'allow_all_wlan': True/False
        'allow_guestpass_generate': True/False

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If after we create new role, this role doesn't exist on the role table, or,
   - If we could not access to the 'Guest Pass generation URL' by use the
     new role information.
   PASS:
   - If after we create new role, role exists on the role table and we access
     successfully to the 'Guest Pass generation URL' by use the new role information.

   Messages:
   - If FAIL the test script returns a message related to the criteria that is
     not satisfied

   Test procedure:
     1. Config:
        - Delete if the role existed
     2. Test procedure:
        - Create new role with 'role_info'
        - Check if the new role is added to the roles table or not
        - Apply the role to a user
        - Access to the 'Guest Pass generation URL' by use the user with with role.
     3. Cleanup:

    How it was tested:

"""

import logging

from RuckusAutoTest.models import Test

class ZD_System_Create_Role(Test):
    required_components = ['ZoneDirector', 'Station']
    parameter_description = {}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        # Delete all wlan, all users and all roles that we have in our system
        self.zd.remove_all_users()
        self.zd.remove_all_roles()
        self.zd.remove_all_wlan()

        # Get configurate option for the role
        self.role_option = conf['role']
        self.timeout = 180

        # Create 2 wlan with Web Authentication using local database.
        self.testuser = ['testuser', 'testpass']
        self.wlan1 = dict(ssid = 'Wlan1', auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                          key_index = "", key_string = "testpass",
                          username = "test1", password = "testpass",
                          ras_addr = "", ras_port = "", ras_secret = "", ad_addr = "",
                          ad_port = "", ad_domain = "")

        self.wlan2 = dict(ssid = 'Wlan2', auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                          sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                          key_index = "", key_string = "testpass",
                          username = "test2", password = "testpass",
                          ras_addr = "", ras_port = "", ras_secret = "", ad_addr = "",
                          ad_port = "", ad_domain = "")

        self.wlan1['use_web_auth'] = True
        self.wlan1['use_guest_access'] = True
        logging.info("Create user %s on the ZD" % self.wlan1['username'])
        self.zd.create_user(self.wlan1['username'], self.wlan1['password'])
        self.zd.cfg_wlan(self.wlan1)

        self.wlan2['use_web_auth'] = True
        self.wlan2['use_guest_access'] = True
        logging.info("Create user %s on the ZD" % self.wlan2['username'])
        self.zd.create_user(self.wlan2['username'], self.wlan2['password'])
        self.zd.cfg_wlan(self.wlan2)

    def test(self):
        # Create new role
        try:
            allow = self.role_option['allow_generate_guestpass']
            if self.role_option['allow_all_wlan'] == False:
                self.zd.create_role(rolename = self.role_option['rolename'],
                                    specify_wlan = self.wlan1['ssid'],
                                    guestpass = allow)
            else:
                self.zd.create_role(rolename = self.role_option['rolename'],
                                    guestpass = allow)
        except:
            return 'FAIL', 'Can not create the role: %s' % self.role_option['rolename']

        # Check if the new role have on roles table or not
        role_list = self.zd.get_role()
        if self.role_option['rolename'] not in role_list:
            return 'FAIL', 'After be created there no role \'%s\' in the roles table' % \
                            self.role_option['rolename']

        # Apply role for test user
        try:
            user_list = self.zd.get_user()
            if self.testuser[0] in user_list:
                self.zd.delete_user(self.testuser[0])

            self.zd.create_user(self.testuser[0], self.testuser[1],
                                role = self.role_option['rolename'])
        except:
            return 'FAIL', 'Can not apply the role \'%s\' for user' % self.role_option[0]

        # Check if user could generate guestpass or not
        check_generate = self.zd.test_user(self.testuser[0], self.testuser[1])
        if allow != check_generate:
            return 'FAIL', 'The role have allow guestpass generation is %s, but result \
                            when we test it is %s' % (repr(allow), repr(check_generate))

        return 'PASS', ''

    def cleanup(self):
        # Delete all wlan, user and role that we have
        self.zd.remove_all_users()
        self.zd.remove_all_roles()
        self.zd.remove_all_wlan()

