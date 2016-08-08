# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description: Test the association negotiation between client and AP succeeded as expected.

    Prerequisite (Assumptions about the state of the testbed/DUT):
    1. Build under test is loaded on the AP
    2. Client is configured in the correct state

    Required components: RuckusAP, Station
    Test parameters: 'wlan_if'   :'wlan0', the wlan interface ID to be tested
                     'capability':'HT', the string in AP "get station wlan info" representing the capability
                     'target_station': 'ip address of target station',
                     'wlan_cfg': 'dictionary of association parameters'
    Result type: PASS/FAIL 
    Results: PASS: AP returns the expected capability string
                FAIL: AP returns unexpected string. Message should include the string expected, the string AP returns                       

    Test procedure:
    1. Config: 
        - Remove All wlan on DUT (e.g ZD, AP)
        - Configure 1 wlan with SSID and security setting in test parameters
        - Telnet to remote wireless STA and remove all wireless profile
        - Verify that wireless station is completed disconnect
        - Configure wireless profile for remote wireless STA  
    2. Test:
        - Verify station is connected
        - On AP, "get station 'wlan_if' list all
        - Verify the return results contains expected 'capability'
        - If no, return FAIL
    3. Cleanup: 
        - Remove all wlan config on AP and ZD
        - Remove wireless profile on remote wireless STA
        - Verify that wireless station is completed disconnect after remove wireless profile.

    How is it tested:
    1. xxx
    2. xxx
"""

import os
import logging

from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class AssocCapability(Test):

    required_components = []
    parameter_description = {}

    def config(self, conf):
        pass

    def test(self):
        pass
 
    def cleanup(self):
        pass

