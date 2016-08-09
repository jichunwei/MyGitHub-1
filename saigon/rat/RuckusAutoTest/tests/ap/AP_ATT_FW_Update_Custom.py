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

#import time
import logging
#import tempfile
#import pdb

from RuckusAutoTest.models import Test
#from RuckusAutoTest.common.Ratutils import logging
import libIPTV_TestConfig as tconfig
#import libIPTV_TestMethods as tmethod

class AP_ATT_FW_Update_Custom(Test):
    required_components = ['RuckusAP']
    parameter_description = {'active_ap': 'ip address of active ap'}

    def config(self, conf):
        self._initTestParams(conf)
        self._getActiveAP(conf)
        self._setFWOption()

    def test(self):
        self._verifyFWUpdateCustom()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        self._changeCustomerID()
        self._set_factory()

        self._verifyATTCustomSetting()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg += ', ' + self.passmsg

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParams(self, conf):
        self.conf = {'fw_info': {},
                     'att_custom_setting': {'country_code': 'US',
                                            'remote_mgmt':'none',
                                            'dc_info':'enabled',
                                            'fw_info': {'host':'cpe.sbcglobal.net',
                                                        'control':'bbt/data/ruckus_firmware/fwcntrl_7811.rcks',
                                                        'user':'ftpdrop',
                                                        'password':'hand2bbt',}}}

        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''

    def _getActiveAP(self, conf):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        logging.info('Find the active AP object')
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], '', '')

        logging.info('Remove all custom file on the AP')
        self.active_ap.remove_all_custom_file()

    def _setFWOption(self):
        self.active_ap.change_fw_setting(self.conf['fw_info'])

    def _changeCustomerID(self):
        logging.debug('Change custommer ID to %s' % self.customer_id)
        self.active_ap.change_board_data('Customer ID', self.customer_id)

    def _set_factory(self):
        logging.debug('Set factory AP')
        self.active_ap.set_factory()

    def _verifyFWUpdateCustom(self):
        logging.debug('Update the custom file')
        self.active_ap.fw_update_custom()
        custom_file = self.active_ap.get_custom_file_list()[0]
        if not custom_file:
            self.errmsg = '[Update Custom Error] The custom file does not exist after updating'
            logging.debug(self.errmsg)
            return
        self.customer_id = custom_file.split('.')[0]
        self.passmsg = 'The custom file is updated successfully'
        logging.debug(self.passmsg)

    def _verifyATTCustomSetting(self):
        logging.debug('Verify the country code')
        country_code = self.active_ap.get_country_code()
        if country_code.upper() != self.conf['att_custom_setting']['country_code'].upper():
            errmsg = '[Error] The current country code is "%s" instead of "%s" as expected'
            self.errmsg = errmsg % (country_code, self.conf['att_custom_setting']['country_code'])
            logging.debug(self.errmsg)
            return

        logging.debug('Verify the FW setting')
        fw_info = self.active_ap.get_fw_upgrade_setting()
        expected_fw_info = self.conf['att_custom_setting']['fw_info']
        for key in expected_fw_info.keys():
            if fw_info[key] != expected_fw_info[key]:
                errmsg = 'The FW setting %s value is "%s" instead of "%s" as expected'
                self.errmsg = errmsg % (key, fw_info[key], expected_fw_info[key])
                logging.debug(self.errmsg)
                return

        logging.debug('Verify the remote-mgmt option')
        remote_mgmt = self.active_ap.get_remote_mgmt()['remote_mgmt']
        if remote_mgmt.upper() != self.conf['att_custom_setting']['remote_mgmt'].upper():
            errmsg = '[Error] The current remote-mgmt option is "%s" instead of "%s" as expected'
            self.errmsg = errmsg % (remote_mgmt, self.conf['att_custom_setting']['remote_mgmt'])
            logging.debug(self.errmsg)
            return

        logging.debug('Verify the data colection option')
        dc_info = self.active_ap.get_dc_info()['status']
        if dc_info.upper() != self.conf['att_custom_setting']['dc_info'].upper():
            errmsg = '[Error] The current DC option is "%s" instead of "%s" as expected'
            self.errmsg = errmsg % (dc_info, self.conf['att_custom_setting']['dc_info'])
            logging.debug(self.errmsg)
            return

        passmsg = 'The information of country code[%s], FW setting [%s],'
        passmsg += 'remote-mgmt[%s], data collection[%s] are correctly'
        self.passmsg = passmsg % (country_code, fw_info, remote_mgmt, dc_info)
        logging.debug(self.passmsg)
