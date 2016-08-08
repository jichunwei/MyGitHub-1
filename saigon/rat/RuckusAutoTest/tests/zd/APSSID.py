# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils


# Note that the name of the Test class must match the name of this file for ease of runtime-reference
# Please make sure the following module docstring is accurate since it will be used in report generation.

class APSSID(Test):
    """Description: APSSID Test class test the ability of AP taking any string of printable
       ASCII characters, of length 32 or less.

       Prerequisite (Assumptions about the state of the testbed/DUT):
       1. Build under test is loaded on the AP

       Required components: RuckusAP
       Test parameters: 'wlan_if':'wlan0', the wlan interface ID to be tested
       Result type: PASS/FAIL 
       Results: PASS: get ssid returns the correct ssid set previouly for any random string generated.
                FAIL: set and get ssid disagree. Msg displays the set_ssid and get_ssid strings                       

       Test procedure:
       1. Config: Turn on the wlan interface to be tested, record current SSID
       2. Generate a random string of printable ASCII characters
       3. Use AP cli to set the ssid
       4. Use AP cli to get the ssid, Fail if disagree
       5. Repeat steps 2 to 4 with string length from 1 to 32
       6. Return pass if no failure
       7. Cleanup: Put back orignal SSID

       How is it tested:
       1. While test running, manually login to AP and change the SSID.
       2. Discovered current AP implementation doesn't accept '#' as leading character
    """

    required_components = ['RuckusAP']
    parameter_description = {'wlan_if':'The ID of the wlan interface to run test'}

    def config(self, conf):
        logging.info("Turn on the targeted wlan interface %s" % conf['wlan_if'])
        self.wlan_if = conf['wlan_if']
        self.testbed.AP.set_state(self.wlan_if, 'up')
        self.oldSSID = self.testbed.AP.get_ssid(self.wlan_if)
        
    def test(self):
        for length in range(1, 32):
            set_ssid = utils.make_random_string(length)
            self.testbed.AP.set_ssid(self.wlan_if, set_ssid)
            get_ssid = self.testbed.AP.get_ssid(self.wlan_if)
            logging.debug("Set ssid %s: %s " % (self.wlan_if, set_ssid))
            logging.debug("Get ssid %s: %s " % (self.wlan_if, get_ssid))
            if not set_ssid == get_ssid:
                return "FAIL", "set SSID %s: %s get SSID: %s" % (self.wlan_if, set_ssid, get_ssid)
                break;
            
        return "PASS", "Accepted 1 to 32 Random ASCII characters"

    def cleanup(self):
        logging.info("Set the SSID back to the orignal name %s" % self.oldSSID)
        self.testbed.AP.set_ssid(self.wlan_if, self.oldSSID)

