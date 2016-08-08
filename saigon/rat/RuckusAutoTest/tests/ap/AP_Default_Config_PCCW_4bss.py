# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AP_Default_Config_PCCW_4bss class tests default custom configuration of PCCW AP
    Author: Toan Trieu
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC
    Test parameters: {'active_ap': 'ip address of active AP',
                      'custom_profile': 'custom profile name in common '}

    Result type: PASS/FAIL

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:

    2. Test:

    3. Cleanup:

    How is it tested:
"""
import time, os
import logging
import tempfile
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *

class AP_Default_Config_PCCW_4bss(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of active AP',
                             'custom_profile': 'custom profile name in common '}

    def config(self, conf):

        self.ap_ip_addr = conf['active_ap']

        logging.info("Find the active AP object")
        self.active_ap = None
        for ap in self.testbed.components['AP']:
            if_info_tmp = ap.get_bridge_if_cfg()
            found = False
            for key, value in if_info_tmp.iteritems():
                if value.has_key('ip_addr'):
                    if value['ip_addr'] == conf['active_ap']:
                        found = True
                        break
            if found:
                self.active_ap = ap
                break
        if not self.active_ap:
            raise Exception("Active AP %s not found in the testbed" % conf['active_ap'])

        # Save current AP ssid and encryption of svcp
        self.svcp = {}
        self.svcp['ssid'] = self.active_ap.get_ssid('wlan0')
        self.svcp['state'] = self.active_ap.get_state('wlan0')
        self.svcp['encryption'] = self.active_ap.get_encryption('wlan0')


    def test(self):
        logging.info("Reboot factory AP")
        self.active_ap.set_factory()

        logging.info("Verifying country code")
        countrycode = self.active_ap.get_country_code()
        logging.info("Current AP country code %s" % countrycode)
        if "HK" not in countrycode:
            return ["FAIL", "Country code is incorrect as specify in default profile setting"]

        logging.info("Verifying telnet access setting key")
        rpmkey_setting = self.active_ap.get_rpm_key("telnet_access_enab_disab")
        logging.info("Current key setting telnet_access_enab_disab on AP is %s" % rpmkey_setting)
        if "Error" in rpmkey_setting:
            return ["FAIL", "key telnet_access_enab_disab doesn't exist"]
        else:
            if rpmkey_setting[0].split('=')[1].strip() != "e":
                return ["FAIL", "key telnet_access_enab_disab value is incorrect as specify in default profile setting"]
        return ["PASS", ""]

    def cleanup(self):
        """ restore AP ssid and encryption of svcp interface """
        if self.active_ap:
            # Change channels of wlan interfaces so that they are not channel 11
            for (wlan_id, wlan) in self.active_ap.get_wlan_info_dict().iteritems():
                self.active_ap.set_channel(wlan['wlanID'], '6')

            logging.info("Turn off svcp interface on the AP")
            self.active_ap.set_state("wlan0", "down")

            logging.info("Restore svcp ssid name back to '%s'" % self.svcp['ssid'])
            self.active_ap.set_ssid('wlan0', self.svcp['ssid'])

            logging.info("Restore encryption setting of svcp to '%s'" % self.svcp['encryption'])
            self.svcp['encryption'].update({'wlan_if':'wlan0'})
            self.active_ap.cfg_wlan(self.svcp['encryption'])
            logging.info("---------- FINISH ----------")

