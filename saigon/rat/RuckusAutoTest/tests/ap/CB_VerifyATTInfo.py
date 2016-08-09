# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ATT_DeviceInfo class verify infomation of ap.

   Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
   1. Build under test is loaded on the AP and Zone Director.

   Required components: AP

   Test parameters: ip_addr - ip address of ap that we want to verify info

   Result type: PASS/FAIL

   Results: PASS: Accepts all valid values, denies all the invalid values with correct alert messages.
            FAIL: Accepts at least one invalid value or denies at least one valid value.

   Messages:
       - if the result is PASS, no message is shown.
       - if the result is FAIL, an error message will be shown.


   Testing procedure:
       Config:
           1.   Get active_ap and active_station from carrier bag
       Test
           1.     Get cli info
           2.     Get xml info
           3.     Compare values between cli and xml
       Cleanup:
           1.   Don't need to do anything to clean up.

   How it was tested:
       1. Enter a valid name to this list of invalid names.
       2. Enter an invalid name to the list of valid names.
"""

import os
import time
import logging
from pprint import pprint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.ap import lib_ATTDataCollection as DC
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_VerifyATTInfo(Test):

    def config(self, conf):
        # Testing parameters
        self.errmsg = ''
        self.passmsg = ''
        self.params = {}
        self.conf = conf
        self.params = {
            'info' : self.conf['info'],
            'type' : self.conf['type'],
            'path' : self.conf['path'],
            'active_ap' : self.conf['active_ap']
        }
        if self.carrierbag.get('active_ap'):
            self.params['ap'] = self.carrierbag['active_ap']

        if self.carrierbag.get('list_stations'):
            self.params['stations'] = self.carrierbag['list_stations']


    def test(self):
        # get cli info
        self._getCliInfo()

        # get xml info
        self._getXmlInfo()

        # verify info
        self._verifyInfo()

        if self.errmsg:
            return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)


    def cleanup(self):
        pass

    def _getCliInfo(self):
        cli_info = DC.getCliInfo(**self.params)
        self.params['cli_info'] = cli_info[self.conf['info']]
        logging.info("Get info from cli : %s\n" % self.params['cli_info'])

    def _getXmlInfo(self):
        xml_file = DC.getXmlFile(**self.params)
        self.params['xml_file_path'] = xml_file

        xml_info = DC.getXmlInfo(**self.params)
        self.params['xml_info'] = xml_info[self.conf['info']]
        logging.info("Get info from xml file : %s\n" % self.params['xml_info'])

    def _verifyInfo(self):
        verify_result = DC.verifyInfo(**self.params)
        if not verify_result:
            self.errmsg = 'Verify info %s. Info get from xml: %s, info get from cli: %s' % (self.conf['info'], self.params['xml_info'], self.params['cli_info'])
        else:
            self.passmsg = 'Verify info %s. Info get from xml: %s, info get from cli: %s' % (self.conf['info'], self.params['xml_info'], self.params['cli_info'])