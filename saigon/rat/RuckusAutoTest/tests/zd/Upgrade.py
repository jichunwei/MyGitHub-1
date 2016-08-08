# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description: test current build's ability to upgrade to a different firmware 

    Prerequisite (Assumptions about the state of the testbed/DUT):
    1. Desired build is load on the DUT

    Required components: DUT
    Test parameters: 'toBuild'              : the full name of the build to be upgraded to, e.g. previous FCS build
                     'proto'                : protocol used by the upgrade process
                     'setfactory'           : set factory or not after update
                     'factorydefault_config': the factory default config (backup.tgz for ZD or rpmkeys for AP) for each build
    Result type: PASS/FAIL
    Results: PASS if the version after upgrade matches 'toBuild'
             FAIL otherwise

    Messages: 
        - If PASS, it shows the amount of time DUT took for the upgrade: from apply the upgrade
             till DUT UpgradeSW() returns successfully which include AP connecting back in ZD case. 
        - If FAIL, prints out the reason for failure 

    Test procedure:
    1. Config: 
        - Backup current config (backup.tgz for ZD, rpmkeys for AP)
    2. Test:
        - Upgrade SW
        - set factory or not according to test parameter
        - Reboot device
        - wait for devices to come back (including APs under ZD), Verify version
        - verify configuration is restored
    3. Cleanup: 
        - restore to the build version before Upgrade (without factory default)

    How is it tested: (to be completed by test code developer)
    1. xxx
    2. xxx
"""

import os
import logging

from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class Upgrade(Test):


    required_components = []
    parameter_description = {}

    def config(self, conf):
        pass

    def test(self):
        pass
 
    def cleanup(self):
        pass
