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
           1.   Get config
       Test

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

class CB_ATT_GetXmlFile(Test):

    def config(self, conf):
        print 'start config here'
        logging.info('start config here 2')
        # Testing parameters
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {}
        self.conf.update(conf)
        self.cmd_dict = {'request_with_wrong_url': 'ruckus_all_wrong_url',
                    'request_with_wrong_user': 'ruckus_all_wrong_user',
                    'request_with_wrong_password': 'ruckus_all_wrong_password',
                    'request_with_wrong_branchname': 'ruckus_all_wrong_branchname',
                    'with_correct_request_header': 'ruckus_all'}
        self.expected_response_msg = {'request_with_wrong_url': 'File error',
                                 'request_with_wrong_user': 'Authenication error',
                                 'request_with_wrong_password': 'Authenication error',
                                 'request_with_wrong_branchname': 'Include filter string parse error',
                                 'with_correct_request_header': 'Success'}
    def test(self):


        xml_file = DC.getXmlFile(**{'cmd':self.cmd_dict[self.conf['testcase']]})
        logging.debug('Get xml file successfull and save in %s' % xml_file)

        response_msg = DC.getXmlResponseStatus(**{'xml_file_path': xml_file})['msg']
        if self.expected_response_msg[self.conf['testcase']] not in response_msg:
            errmsg = 'The response for the test %s is %s instead of %s'
            self.errmsg = errmsg % (self.conf['testcase'], response_msg, self.expected_response_msg[self.conf['testcase']])
            logging.debug(self.errmsg)
            return ('FAIL', self.errmsg)

        self.passmsg = '[Test %s] The response message "%s" is correct' % (self.conf['testcase'], response_msg)
        logging.debug(self.passmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

