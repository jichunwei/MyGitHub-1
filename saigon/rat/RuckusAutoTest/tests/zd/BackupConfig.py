# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description: test current build's ability to backup config

    Prerequisite (Assumptions about the state of the testbed/DUT):
    1. Desired build is load on the DUT

    Required components: DUT (both RuckusAP and ZoneDirector)
    Test parameters: 'initconfig' : configuration of the DUT before and after upgrade
    Result type: PASS/FAIL
    Results: PASS if the backup file can be saved???
             FAIL otherwise

    Messages: 
        - If PASS, pass 
        - If FAIL, prints out the reason for failure 

    Test procedure:
    1. Config: pass
    2. Test: Verify backup files can be retrieved (backup.tgz for ZD, suport.txt for AP)
    3. Cleanup: pass

    How is it tested: (to be completed by test code developer)
    1. xxx
    2. xxx
"""

import os
import logging

from RuckusAutoTest.models import Test


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class BackupConfig(Test):


    required_components = []
    parameter_description = {}

    def config(self, conf):
        pass

    def test(self):
        pass
 
    def cleanup(self):
        pass
