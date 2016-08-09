# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: this script use to test the custom update of ATT AP
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
        - Change the customer id follow the customer id in the custom file
        - Set factory the AP to apply the custom setting
        - Verify the ATT custom setting is applied to the AP or not.

    3. Cleanup:
        -
"""

import time
import logging
import tempfile
import pdb

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class CB_Verify_AP_Custom_Setting(Test):
    required_components = ['RuckusAP']
    parameter_description = {'active_ap': 'ip address of active ap'}

    def config(self, conf):
        self._initTestParams(conf)
        if self.carrierbag.has_key('active_ap'):
            self.active_ap = self.carrierbag['active_ap']
        else:
            self._getActiveAP(conf)
            self.carrierbag['active_ap'] = self.active_ap

    def test(self):
        self._changeCustomerID()
        self._set_factory()

        self._verifyATTCustomSetting()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParams(self, conf):
        self.conf = {'custom_setting': {'country_code': 'US',
                                        'remote_mgmt':'none',
                                        'dc_info':'enabled',
                                        'fw_info': {'host':'cpe.sbcglobal.net',
                                                    'control':'bbt/data/ruckus_firmware/fwcntrl_7811.rcks',
                                                    'user':'ftpdrop',
                                                    'password':'hand2bbt',}}}

        self.verify_fuction = {'country_code': self._verifyCountryCode,
                               'remote_mgmt': self._verifyRemoteMgmt,
                               'dc_info': self._verifyDataCollectionOption,
                               'fw_info': self._verifyFWSeting}

        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''

    def _getActiveAP(self):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(self.conf['active_ap'])
        logging.info('Find the active AP object')
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, self.conf['active_ap'],
                                                    self.testbed.components['AP'], '', '')

    def _changeCustomerID(self):
        logging.debug('Change custommer ID to %s' % self.carrierbag['customer_id'])
        self.active_ap.change_board_data('Customer ID', self.carrierbag['customer_id'])

    def _set_factory(self):
        logging.debug('Set factory AP')
        self.active_ap.set_factory()

    def _verifyATTCustomSetting(self):
        passmsg = ''
        for key in self.conf['custom_setting'].keys():
            self.verify_fuction[key]()
            if self.errmsg: return
            passmsg = self.passmsg if not passmsg else passmsg + '; ' + self.passmsg

        self.passmsg = passmsg
        logging.debug(self.passmsg)

    def _verifyCountryCode(self):
        logging.debug('Verify the country code')
        country_code = self.active_ap.get_country_code()
        if country_code.upper() != self.conf['custom_setting']['country_code'].upper():
            errmsg = '[Error] The current country code is "%s" instead of "%s" as expected'
            self.errmsg = errmsg % (country_code, self.conf['custom_setting']['country_code'])
            logging.debug(self.errmsg)
            return
        self.passmsg = 'The country code "%s" is correct' % country_code

    def _verifyFWSeting(self):
        logging.debug('Verify the FW setting')
        fw_info = self.active_ap.get_fw_upgrade_setting()
        expected_fw_info = self.conf['custom_setting']['fw_info']
        for key in expected_fw_info.keys():
            if fw_info[key] != expected_fw_info[key]:
                errmsg = 'The FW setting %s value is "%s" instead of "%s" as expected'
                self.errmsg = errmsg % (key, fw_info[key], expected_fw_info[key])
                logging.debug(self.errmsg)
                return
        self.passmsg = 'The FW setting %s is correct' % fw_info

    def _verifyRemoteMgmt(self):
        logging.debug('Verify the remote-mgmt option')
        remote_mgmt = self.active_ap.get_remote_mgmt()['remote_mgmt']
        if remote_mgmt.upper() != self.conf['custom_setting']['remote_mgmt'].upper():
            errmsg = '[Error] The current remote-mgmt option is "%s" instead of "%s" as expected'
            self.errmsg = errmsg % (remote_mgmt, self.conf['custom_setting']['remote_mgmt'])
            logging.debug(self.errmsg)
            return
        self.passmsg = 'The remote-mgmt option is "%s" as expected' % remote_mgmt

    def _verifyDataCollectionOption(self):
        logging.debug('Verify the data collection option')
        dc_info = self.active_ap.get_dc_info()['status']
        if dc_info.upper() != self.conf['custom_setting']['dc_info'].upper():
            errmsg = '[Error] The current DC option is "%s" instead of "%s" as expected'
            self.errmsg = errmsg % (dc_info, self.conf['custom_setting']['dc_info'])
            logging.debug(self.errmsg)
            return
        self.passmsg = 'The data collection setting %s is correct' % dc_info
