# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AP_Default_Config_Telsur class tests default custom configuration of Telsur AP
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
    - Look for the active AP
    - Save the current encryption setting of wlan 'svcp'
    2. Test:
    - Reboot factory AP
    - Verify each custom configuration loaded correctly to the AP
    3. Cleanup:
    - Down svcp interface on the AP
    - Restore encryption setting and ssid name of svcp interface

    How is it tested:
    - change custom configuration to incorrect value, verify that script can script can find in correct
    configuration for each case.
"""
import time, os
import logging
import tempfile
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *

class AP_Default_Config_Telsur(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'IP address of active AP',
                             'custom_profile': 'custom profile name in common folder',
                             'wlan_if':'wireless interface need to verify'}

    def config(self, conf):

        self.ap_ip_addr = conf['active_ap']
        self.active_ap = None
        logging.info("Find the active AP object")
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

        logging.info("Verifying ap-bridge of svcp")
        ap_bridge_setting = self.active_ap.get_ap_bridge("wlan0")
        logging.info("Current ap-bridge setting of svcp %s " % ap_bridge_setting)

        if "disabled" not in ap_bridge_setting.lower():
            return ["FAIL", "ap-bridge setting of svcp is %s" % ap_bridge_setting[0].split()[-1]]

        logging.info("Verifying firmware auto upgrade setting")
        fw_upgrade_fm_settings = self.active_ap.get_fw_upgrade_setting()
        logging.info("Current AP firmware auto upgrade setting %s" % fw_upgrade_fm_settings)

        if fw_upgrade_fm_settings['host'] != "192.168.43.120":
            return ["FAIL", "host ip_addr is incorrect"]
        if fw_upgrade_fm_settings['user'] != "telsur":
            return ["FAIL", "user name is incorrect"]
        if fw_upgrade_fm_settings['password'] != "telsursa":
            return ["FAIL", "password is incorrect"]

        # compare video gw have the same subnet with ip_addr for profile ruckus03 only
        if self.active_ap.get_profile().lower() in ['ruckus03']:
            logging.info("verifying gateway of wan and video")
            video_ip_cfg = self.active_ap.get_ip_cfg("video")
            wan_ip_cfg = self.active_ap.get_ip_cfg("wan")

            # compare video gw have the same subnet with ip_addr
            logging.info(video_ip_cfg)
            logging.info(wan_ip_cfg)
            if video_ip_cfg["gw"] != wan_ip_cfg["gw"]:
                return ["FAIL", "default gateway of video & wan are different"]

            logging.info("Verifying subnet of gateway & video interface")
            if (video_ip_cfg["ip_addr"].split(".")[0] != video_ip_cfg["gw"].split(".")[0] or
               video_ip_cfg["ip_addr"].split(".")[1] != video_ip_cfg["gw"].split(".")[1] or
               video_ip_cfg["ip_addr"].split(".")[2] != video_ip_cfg["gw"].split(".")[2]):
                return ["FAIL", "Video gateway and IP address are not the same subnet"]

        return ["PASS", ""]

    def cleanup(self):
        """ restore AP ssid and encryption of svcp interface """
        if self.active_ap:
            # Change channels of wlan interfaces so that they are not channel 11
            for (wlan_id, wlan) in self.active_ap.get_wlan_info_dict().iteritems():
                self.active_ap.set_channel(wlan['wlanID'], '6')

            logging.info("Turn off svcp interface on the AP")
            self.active_ap.set_state('wlan0', 'down')

            logging.info("Restore svcp ssid name back to '%s'" % self.svcp['ssid'])
            self.active_ap.set_ssid('wlan0', self.svcp['ssid'])

            logging.info("Restore encryption setting of svcp to '%s'" % self.svcp['encryption'])
            self.svcp['encryption'].update({'wlan_if':'wlan0'})
            self.active_ap.cfg_wlan(self.svcp['encryption'])
            logging.info("---------- FINISH ----------")

