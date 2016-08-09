# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_SystemName class tests the System Name of the Zone Director.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'

   Test parameters: no. But we can add more values to the list 'valid_name_list' and 'invalid_name_dict' in the code.
                    However, if you are about to add more items to the invalid_name_dict,
                    please add the prefix of the corresponding alert messages.

   Result type: PASS/FAIL

   Results: PASS: Accepts all valid names, denies all the invalid names with correct alert messages.
            FAIL: Accepts at least one invalid name or an incorrect alert appears or denies at least one valid name

   Messages:
       - if the result is PASS, no message is shown
       - if the result is FAIL, it shows the reason for this failure

   Test procedure:
       Config:
           - Navigate to the Dashboard page, get the current System Name.
       Test:
           - Navigate to Configure --> System
           - Apply each item in the below applied list to the system name then apply the changes
           - Verify if the ZD web UI reacts properly. A message should be shown if the system name is invalid,
            else no message is shown and system name should be changed.
           - Check if the name is changed properly.
       Cleanup:
           - Cleanup the environment by setting the System Name to its original name.

    Applied list for System Name:
       1.   Valid name ('Jimmy',..)
       2.   Name separated by space ('Truc Ha',...)
       3.   Name with numbers only ('12345678',..)
       4.   Name longer than 32 characters ('a_name_that_is_longer_than_32_characters',...)
       5.   Name with invalid characters ('myn@me',.. )
       6.   Name followed by space(s) ('Jimmy    ',...)
       7.   Name preceeded by space(s) ('      Jimmy',...)
       8.   Empty name

    How is is tested:
       Change the error message in the 'invalid_name_dict', the scritp should return FAIL.

"""

import os
import time
import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_SystemName(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        print "Get the current System Name."
        self.system_name = self.testbed.components['ZoneDirector'].get_system_name()
        logging.info("The current System Name is '%s'" % self.system_name)

    def test(self):
        # List of valid IP addresses
        valid_name_list = ['system_name', '12345678'] #@author: Jane.Guo @since: 2013-09 behavior change
        # A dict of invalid names with the corresponding prefix of the alert messages.
        invalid_name_dict = {'Jimmy system':'the system name can only contain up to', \
                             'Jimmy@a':'the system name can only contain up to', \
                             'Jimmy_sys tem':'the system name can only contain up to', \
                             '':'system name cannot be empty'}

        for name in valid_name_list:
            logging.info("Apply the value '%s' to the System Name" % name)
            try:
                self.testbed.components['ZoneDirector'].set_system_name(name)
            # Valid System Name, no message should be shown
            except Exception, e:
                return ["FAIL", "Zone Director does not accept a valid name '%s'. The message is '%s'" % (name, e.message)]

        for name, msg in invalid_name_dict.items():
            logging.info("Apply the value '%s' to the System Name" % name)
            try:
                self.testbed.components['ZoneDirector'].set_system_name(name)
                return ["FAIL", "Zone Director accepts the invalid System Name '%s'" % name]
            except Exception, e:
                logging.debug('print e.message %s' % e.message)
                if e.message == "System Name has not been set on the Dashboard page":
                    return ["FAIL", "Zone Director accepts the invalid value '%s', but %s" % (name, e.message)]
                else:
                    if not re.search(msg, e.message, re.I): #not e.message.lower().startswith(msg):
                        return ("FAIL", "The wrong message '%s' has been shown when applying the value %s to System Name.\
                        The correct message should start with '%s'" % (e.message, name, msg))

        return ["PASS", ""]

    def cleanup(self):
        print "Clean up: Set the System Name to its original one"
        self.testbed.components['ZoneDirector'].set_system_name(self.system_name)
        logging.info("Clean up successfully")

