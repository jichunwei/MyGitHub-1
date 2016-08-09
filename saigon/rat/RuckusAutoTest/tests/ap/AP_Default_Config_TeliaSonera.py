# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AP_Default_Config_TeliaSonera class tests default custom configuration of Telia Sonera AP
    Author: Toan Trieu
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP
    Test parameters: {'active_ap'     : 'ip address of active AP',
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
from RuckusAutoTest.common.IPTV_Ratutils import *

class AP_Default_Config_TeliaSonera(Test):
    required_components = ['RuckusAP']
    parameter_description = {'active_ap': 'ip address of active AP',
                             'custom_profile': 'custom profile name in common '}

    def config(self, conf):
        ap_default_cfg_file = os.path.join(".","RuckusAutoTest","common","IPTV_AP_Default_Config.inf")
        self.ap_default_config = loadCustomConfigFile(ap_default_cfg_file)[conf['custom_profile']]
        logging.info("AP default config: %s" %self.ap_default_config)

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
        self.svcp['encryption'] = self.active_ap.get_encryption('wlan0')

        # reset factory AP to let AP load default configuration after reboot
        logging.info("Reboot factory AP")
        self.active_ap.set_factory()

    def test(self):
        logging.info("Verifying default wan IP Address")
        wan_ip_cfg = self.active_ap.get_rpm_key(self.ap_default_config['rpm_default_ipaddr']['key'])
        logging.info(wan_ip_cfg)
        if wan_ip_cfg[0].split("=")[-1].strip() != self.ap_default_config['rpm_default_ipaddr']['value']:
            return ["FAIL", "Wan IP address is incorrect."]

        logging.info("Verifying home interface settings in wlanlist")
        wlan_if_list = self.active_ap.get_wlan_info_dict()
        if len(wlan_if_list) < int(self.ap_default_config['max_wlans']):
            return ["FAIL", "maximum wlan is incorrect"]

        logging.info("Wlanlist: %s" % wlan_if_list)
        found = False
        for (wlan_id, wlan_if) in wlan_if_list.iteritems():
            if wlan_if['name'] == self.ap_default_config['wlan1']['name']:
                found = True
                # default wlan status must be down
                if wlan_if['status'] != self.ap_default_config['wlan1']['state']:
                    return ["FAIL","'home' wlan status is up"]

                # default wlan type is AP
                if wlan_if['type'] != self.ap_default_config['wlan1']['type']:
                    return ["FAIL","'home' wlan type is incorrect"]

                break

        if not found:
            return ["FAIL", "Can't find home interface"]

        logging.info("verify qos configuration option")
        for interface in self.ap_default_config['if_list'].keys():
            qos_cfg_opt = self.active_ap.get_qos_cfg_option(self.ap_default_config['if_list'][interface])
            logging.info("%s QOS configuration options: %s" % (interface, qos_cfg_opt))
            for opt in self.ap_default_config['%s_qos_cfg' % interface].keys():
                logging.info("Verifying QOS Option '%s' " % opt)
                if  qos_cfg_opt[opt] != self.ap_default_config['%s_qos_cfg' % interface][opt]:
                    return ["FAIL", "QOS '%s' is incorrect" % opt]

        # Verify Encryption Setting
        encryption = self.active_ap.get_encryption(self.ap_default_config['if_list']['if2'])
        logging.info(encryption)
        for key in self.ap_default_config['wlan1_encryption'].keys():
            if key.lower() == "ssid":
                # Verify prefix of SSID start with "Home"
                if not encryption[key].startswith("Home"):
                    return ["FAIL", "SSID prefix is incorrect"]
            else:
                if encryption[key] != self.ap_default_config['wlan1_encryption'][key]:
                    return ["FAIL", "Default encryption settings is incorrect"]

        # Verify country code
        countrycode = self.active_ap.get_country_code()
        logging.info("Country Code %s" % countrycode)
        if countrycode != self.ap_default_config['countrycode']:
            return ["FAIL", "Country code is incorrect"]

        logging.info("Verifying firmware upgrade settings")
        fw_upgrade_fm_settings = self.active_ap.get_fw_upgrade_setting()
        logging.info(fw_upgrade_fm_settings)
        for key in self.ap_default_config['fw_settings'].keys():
            if key.lower() != "control":
                if fw_upgrade_fm_settings[key].lower() != self.ap_default_config['fw_settings'][key].lower():
                    return ["FAIL", "Default firmware upgrade setting of \'%s\' is incorrect" % key]
        
        # dhcpc is not available from version 5.3
        if self.active_ap.get_version() < '5.3':
            logging.info("Verifying dhcpc configuration")
            dhcpc_info = self.active_ap.get_dhcpc_info()
            logging.info("dhcpc configuration: %s" % str(dhcpc_info))
            for key in self.ap_default_config['dhcpc_info'].keys():
                if dhcpc_info[key].lower() != self.ap_default_config['dhcpc_info'][key].lower():
                    return ["FAIL", "DHCPC Configuration of \'%s\' is incorrect" % key]

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


