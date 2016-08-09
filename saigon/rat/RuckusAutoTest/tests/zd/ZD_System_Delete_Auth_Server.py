# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: To verify if ZD could delete an existing authentication server

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
       - 'server_name': Server Name displays in Authentication Servers table
       - 'server': IP Address of authentication server
       - 'port': server listens port
       - 'secret': secrect string of Radius Server
       - 'domain': domain name of Active Directory Server
       - 'number_server': Number of server will created
       - 'delete_server': server id will be deleted or 'all' delete all authentication servers

   Parameters Example for Radius Server:
       {'server_name': 'radius_server', 'delete_server': '2', 'number_server': 2, 'server': '192.168.0.252',
       'secret': '1234567890', 'port': '1812'}
       or
       {'server_name': 'radius_server', 'delete_server': 'all', 'number_server': 2, 'server': '192.168.0.252',
       'secret': '1234567890', 'port': '1812'}
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
            - Create Authentication servers with the setting from parameters
         2. Test procedure:
            - Find 'delete_server' and click on checkbox then click delete.
            - If 'delete_server' is 'all', click on select all and click delete until all servers were deleted.
            - Verify server delete work correct.
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

class ZD_System_Delete_Auth_Server(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf.copy()
        logging.info("Removing all Authentication server")
        self.testbed.components['ZoneDirector'].remove_all_auth_servers()
        # Create some authentication servers
        if self.conf.has_key('number_server'):
            for i in range(self.conf['number_server']):
                server_name = "%s_%s" % (self.conf['server_name'], str(i))
                self.conf.update(dict(server_name=server_name))
                tconfig.create_auth_server(zd = self.testbed.components['ZoneDirector'], 
                                           **self.conf)
            total_auth_server = self.testbed.components['ZoneDirector'].get_total_auth_server()
            logging.info("Total server created %s" % total_auth_server)

    def test(self):
        logging.debug(self.conf)
        result, msg = ["", ""]

        if self.conf['delete_server'].upper() == "ALL":
            self.testbed.components['ZoneDirector'].remove_all_auth_servers()
            total_auth_server = self.testbed.components['ZoneDirector'].get_total_auth_server()
            if total_auth_server == "0":
                result, msg = ("PASS", "")
            else:
                result, msg = ("FAIL", "Can't delete All Authentication Server")

        else:
            self.testbed.components['ZoneDirector'].delete_auth_server(self.conf['server_name'])
            total_auth_server = self.testbed.components['ZoneDirector'].get_total_auth_server()
            number_server = self.conf['number_server'] - 1
            if total_auth_server == str(number_server):
                result, msg = ("PASS", "")
            else:
                result, msg = ("FAIL", "Can't delete Authentication Server")

        return (result, msg)

    def cleanup(self):
        logging.info("Removing all Authentication server")
        self.testbed.components['ZoneDirector'].remove_all_auth_servers()

