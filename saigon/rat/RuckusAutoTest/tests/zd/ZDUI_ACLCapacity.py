# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

""" Description: Verify user can configure a large number of ACL entries from ZD webUI.
                Check to make sure the acl-list.xml file in ZD is consistent with user action. 

    Prerequisite (Assumptions about the state of the testbed/DUT):
    1. Desired build is loaded on ZD

    Required components: ZoneDirector
    Test parameters: 'num_entries': number of ACLs configured to ZD, upto ?????
                     'acl_policy'    : "only allow" or "only deny"
    Result type: PASS/FAIL
    Results: PASS if all configured ACL is listed in acl-list.xml, no more, no less

    Test procedure:
    1. Config: delete ACL list if not empty
    2. Test: 
        - Navigate to Configure Access Controls page on ZD WebUI
        - Click Creat New under Access Control Policies
        - Select the button according to specified 'acl_policy'
        - Add specified number of entries with random MAC addresses
        - Grab backup.tgz from System/Backup page
        - Use tac_encrypt tool to decode backup.tgz and extract acl-list.xml
        - Verify acl-list.xml contains all the added MAC and only those   
    3. Cleanup:  

    How is it tested: (to be completed by test code developer)
    1. xxx
    2. xxx
    """

import os
import logging

from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference


class ZDUI_ACLCapacity(Test):


    required_components = []
    parameter_description = {}

    def config(self, conf):
        pass

    def test(self):
        pass
 
    def cleanup(self):
        pass
