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
           1.    Get list stations
           2.    Send iperf for all stations in above list
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

class CB_SendIperfTraffic(Test):

    def config(self, conf):
        # Testing parameters
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf
        self.params = {'timeout' : self.conf['timeout']}
        if self.carrierbag.get('list_stations'):
            self.params['stations'] = self.carrierbag['list_stations']
        if self.carrierbag.get('active_ap'):
            self.params['ap'] = self.carrierbag['active_ap']

    def test(self):

        DC.runIperf(**self.params)
        self.passmsg = 'Finish send traffic for window stations'

        if self.errmsg:
            return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)


    def cleanup(self):
        pass

