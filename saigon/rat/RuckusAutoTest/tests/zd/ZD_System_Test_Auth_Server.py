# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: To verify if ZD could authenticate to an exist authentication server

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
       - 'server_name': Server Name displays in Authentication Servers table
       - 'server': IP Address of authentication server
       - 'port': server listens port
       - 'secret': secrect string of Radius Server
       - 'domain': domain name of Active Directory Server
       - 'user': user used to test authenticate
       - 'password': password of that username on authentication server

   Parameters example for Radius Server:
       - {'domain': 'rat.ruckuswireless.com', 'server_name': 'AD_Server', 'server': '192.168.0.250',
          'user': 'rat', 'password': '1234567890@AD', 'port': '389'}

   Parameters example for Active Directory Server:
       - {'server_name': 'radius_server', 'server': '192.168.0.252', 'secret': '1234567890',
          'user': 'ras.local.user', 'password': 'ras.local.user', 'port': '1812'}

   Parameters example for Local Database:
       - {'password': 'local.user', 'user': 'local.user', 'server_name': 'Local Database'}
   Result type: PASS/FAIL
   Results:
   FAIL:
   - If user can't authenticate with authentication server
   PASS:
   - If user can authenticate with authentication server and ZD display success message

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Delete all authentication sever on the ZD
         2. Test procedure:
            - Create Authentication servers with the setting from parameters
            - Use input 'user' and 'password' to authenticate in Test Authentication Settings table.
            - Click on test button to test authenticate
            - Verify return message. If username and password are correct, ZD should return message
              "Success! The user will be assigned a role of "Default""
         3. Cleanup:
            - Delete all authentication server.

    How it was tested:

"""
import os
import time
import logging
import random
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils

class ZD_System_Test_Auth_Server(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf.copy()
        logging.info("Removing all Authentication server and users in Local Database")
        self.testbed.components['ZoneDirector'].remove_all_auth_servers()
        self.testbed.components['ZoneDirector'].remove_all_users()

        logging.debug(self.conf)
        tconfig.create_auth_server(self.testbed.components['ZoneDirector'], **self.conf)

    def test(self):
        result, msg = ["", ""]
        auth_msg = self.testbed.components['ZoneDirector'].test_authenticate(self.conf['server_name'],
                                                                            self.conf['user'], self.conf['password'])
        if "Success" in auth_msg:
            result, msg = ("PASS", "")
        else:
            result, msg = ("FAIL", auth_msg)
        return (result, msg)

    def cleanup(self):
        logging.info("Removing all Authentication server and users in Local Database")
        self.testbed.components['ZoneDirector'].remove_all_auth_servers()
        self.testbed.components['ZoneDirector'].remove_all_users()





