# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: this script use to test the custom update for AP
    Author: An Nguyen
    Email: nnan@s3solutions.com.vn
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP
    Test parameters: {'active_ap': 'ip address of active ap'}

    Result type: PASS/FAIL

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        -
    2. Test:
        - Load the custom file by using command "fw update custom"
        - Verify if the custom file exists

    3. Cleanup:
        -
"""

#import time
import logging
#import tempfile
#import pdb

from RuckusAutoTest.models import Test
#from RuckusAutoTest.common.Ratutils import logging
import libIPTV_TestConfig as tconfig
#import libIPTV_TestMethods as tmethod

class CB_AP_FW_Update_Custom(Test):
    required_components = ['RuckusAP']
    parameter_description = {'active_ap': 'ip address of active ap'}

    def config(self, conf):
        self._initTestParams(conf)
        if self.carrierbag.has_key('active_ap'):
            self.active_ap = self.carrierbag['active_ap']
        else:
            self._getActiveAP()
            self.carrierbag['active_ap'] = self.active_ap
        self._setFWOption()

    def test(self):
        self._verifyFWUpdateCustom()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParams(self, conf):
        self.conf = {'fw_info': {},
                    }
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''

    def _getActiveAP(self):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(self.conf['active_ap'])
        logging.info('Find the active AP object')
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, self.conf['active_ap'],
                                                    self.testbed.components['AP'], '', '')

        logging.debug('Remove all custom file on the AP')
        self.active_ap.remove_all_custom_file()

    def _setFWOption(self):
        self.active_ap.change_fw_setting(self.conf['fw_info'])

    def _verifyFWUpdateCustom(self):
        logging.debug('Update the custom file')
        self.active_ap.fw_update_custom()
        custom_file = self.active_ap.get_custom_file_list()[0]
        if not custom_file:
            self.errmsg = '[Update Custom Error] The custom file does not exist after updating'
            logging.debug(self.errmsg)
            return
        customer_id = custom_file.split('.')[0]
        self.carrierbag['customer_id'] = customer_id
        self.passmsg = 'The custom file is updated successfully'
        logging.debug(self.passmsg)