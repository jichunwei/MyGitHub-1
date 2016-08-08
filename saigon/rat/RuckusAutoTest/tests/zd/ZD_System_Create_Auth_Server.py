# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: To verify if authentication server could create on ZD (Radius or Active Directory Server)

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
       - 'server_name': Server Name displays in Authentication Servers table
       - 'server': IP Address of authentication server
       - 'port': server listens port
       - 'secret': secrect string of Radius Server
       - 'domain': domain name of Active Directory Server

   Parameters Example for Radius Server:
       - {'secret': '1234567890', 'port': '1812', 'server_name': 'radius_server', 'server': '192.168.0.252'}
   Parameters example for Active Directory Server:
       - {'domain': 'rat.ruckuswireless.com', 'port': '389', 'server_name': 'AD_Server', 'server': '192.168.0.250'}
   Result type: PASS/FAIL
   Results:
   FAIL:
   - If the total number of servers doesn't match with server created
   PASS:
   - If the total number of servers matches with server created

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Delete all authentication sever on the ZD
         2. Test procedure:
            - Create Authentication servers with the setting from parameters
            - Verify the total number of server in authentication server table match with server created
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

class ZD_System_Create_Auth_Server(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf.copy()
        logging.info("Removing all Authentication server")
        self.testbed.components['ZoneDirector'].remove_all_auth_servers()

    def test(self):
        logging.debug(self.conf)
        result, msg = ["", ""]
        if self.conf.has_key('number_server'):
            for i in range(self.conf['number_server']):
                server_name = "%s_%s" % (self.conf['server_name'], str(i))
                tconfig.create_auth_server(zd = self.testbed.components['ZoneDirector'],
                                 server_name = server_name, **self.conf)
            # wait for ZD update infor
            time.sleep(2)
            total_auth_server = self.testbed.components['ZoneDirector'].get_total_auth_server()
            logging.info("Total server created %s" % total_auth_server)
            if total_auth_server == str(self.conf['number_server']):
                result, msg = ("PASS", "")
            else:
                result, msg = ("FAIL", "Total Auth Server created %s in stead of %d" %
                               (total_auth_server, self.conf['number_server']))
        else:
            tconfig.create_auth_server(zd = self.testbed.components['ZoneDirector'], **self.conf)
            total_auth_server = self.testbed.components['ZoneDirector'].get_total_auth_server()

            logging.info("Total server created %s" % total_auth_server)
            if total_auth_server == "1":
                result, msg = ("PASS", "")
            else:
                result, msg = ("FAIL", "Can't create authentication server")

        return (result, msg)

    def cleanup(self):
        logging.info("Removing all Authentication server")
        self.testbed.components['ZoneDirector'].remove_all_auth_servers()

