# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: Vlan_Upgrade class tests ability of queuing traffic when streaming with the given conditions.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP
    Test parameters: {'active_ap':'ip address of the tested AP',
                             'ap_model':'model of the tested AP',
                             'latest_build':'build number of the latest release',
                             'upgraded_build':'build is used to upgrade'}

    Result type: PASS/FAIL/N/A

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.
             N/A: If the test procedure need to run on specific model

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP
        - Save fw setting
    2. Test:
        - Load AP to the latest release
        - Create some VLANs on the AP
        - Verify that VLANs are created correctly in the latest release
        - Upgrade to the tested build
        - Make sure that VLAN information is still correct
    3. Cleanup:
        - Return the previous fw setting for AP
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class Vlan_Upgrade(Test):
    required_components = ['RuckusAP']
    parameter_description = {'active_ap':'ip address of the tested AP',
                             'ap_model':'model of the tested AP',
                             'latest_build':'build number of the latest release',
                             'upgraded_build':'build is used to upgrade'}
    def config(self, conf):
        self._defineTestParams(conf)
        self._getActiveAP(conf)
        self._saveConfig()

    def test(self):
        if self.active_ap.get_device_type().lower() != self.ap_model:
            return ["N/A","The AP model is not correct. Skip this test cases"]

        logging.info("Upgrade AP to the latest release [%s]" % self.latest_build)
        self._upgrade(self.latest_build)

        logging.info("[AP Build: %s]: add some VLANs to the AP" % self.latest_build)
        self.vlancfg_1st = self._defineVlanParams(self._getIntfNum('wlan0'), self.vlanid_1st, True)
        self.vlancfg_2nd = self._defineVlanParams(self._getIntfNum('wlan7'), self.vlanid_2nd, False)

        logging.info("Create 2 VLAN %s and %s on the AP" % (self.vlanid_1st, self.vlanid_2nd))
        self.active_ap.create_vlan(self.vlancfg_1st)
        time.sleep(2)
        self.active_ap.create_vlan(self.vlancfg_2nd)

        # Get vlan info when AP's running the latest release
        logging.info("Verify that the vlan configuration is correct when AP's running the latest release [%s]" %
                     self.latest_build)
        vlan_info_latest_build = self.active_ap.get_vlan_info()
        logging.debug(self._analyzeVlanInfo(vlan_info_latest_build, self.latest_build))

        res, msg = self._compareVlanInfo(vlan_info_latest_build,
                                         self.vlancfg_1st,
                                         self.latest_build)
        if res == "FAIL": return res, msg
        res, msg = self._compareVlanInfo(vlan_info_latest_build,
                                         self.vlancfg_2nd,
                                         self.latest_build)
        if res == "FAIL": return res, msg
        logging.info("[Build %s]: Vlan is configured correctly" % self.latest_build)

        logging.info("Upgrade AP from build [%s] to build [%s]" % (self.latest_build, self.upgraded_build))
        self._upgrade(self.upgraded_build)
        time.sleep(5)

        msg = "Verify that Vlan Configuration does not change after upgrading AP from "
        msg += "build [%s] to build [%s]" % (self.latest_build, self.upgraded_build)
        logging.info(msg)
        vlan_info_after_upgrade = self.active_ap.get_vlan_info()
        logging.debug(self._analyzeVlanInfo(vlan_info_after_upgrade, self.upgraded_build))

        res, msg = self._compareVlanInfo(vlan_info_after_upgrade,
                                         self.vlancfg_1st,
                                         self.upgraded_build)
        if res == "FAIL": return res, msg
        res, msg = self._compareVlanInfo(vlan_info_after_upgrade,
                                         self.vlancfg_2nd,
                                         self.upgraded_build)
        if res == "FAIL": return res, msg
        logging.info("Vlan Configuration is still correct after upgrading from build [%s] to build [%s]" %
                     (self.latest_build, self.upgraded_build))
        return ["PASS", ""]

    def cleanup(self):
        logging.info("Return the previous fw setting for AP")
        self.active_ap.change_fw_setting(self.old_fw_info)

        logging.info("Remove all VLANs out of the AP")
        self.active_ap.remove_all_vlan()
        logging.info("------------ FINISH ---------------\n")

    def _compareVlanInfo(self, all_vlans_info, compared_vlan, build):
        find_vlan = False
        for vlan in all_vlans_info:
            if vlan['vlan_id'] == compared_vlan['vlan_id']:
                for key in vlan.keys():
                    if key != 'vlan_name':
                        temp = vlan[key].split()
                        for e in temp:
                            if not e in compared_vlan[key]:
                                return ["FAIL", "[Build %s]: Vlan configuration is not correct" % build]
                find_vlan = True
                break
        if not find_vlan:
            return ["FAIL", "[Build %s]: There is no VLAN [%s] in VLAN table" % (build, vlan_id)]

        return ["PASS", ""]

    def _analyzeVlanInfo(self, vlan_info, build):
        msg = "[Build: %s]: Vlan Configuration: \n" % build
        for vlan in vlan_info:
            msg += "\tVLAN %s: " % vlan['vlan_id']
            if vlan.has_key('vlan_name'):
                msg += " Name: %s" % vlan['vlan_name']
            if vlan.has_key('native_wlan'):
                msg += " ----- Wlan: %s" % vlan['native_wlan']
            if vlan.has_key('eth_tagged_port'):
                msg += " ----- Tagged port: %s" % vlan['eth_tagged_port']
            if vlan.has_key('eth_native_port'):
                msg += " ----- Native port: %s" % vlan['eth_native_port']
            msg += "\n"

        return msg

    def _upgrade(self, build):
        # Create control file
        cntrl_file = self.active_ap.create_ctrl_file_ap(self.ftpserv['rootpath'], build)
        self.fw_conf['control'] = cntrl_file

        # Config fw setting for AP and upgrade
        self.active_ap.change_fw_setting(self.fw_conf)
        self.active_ap.upgrade_sw(build)
        time.sleep(3)

        # Remove control file
        os.remove(cntrl_file)

    def _getActiveAP(self, conf):
        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], "", "")

        logging.info("Remove all VLANs out of the active AP")
        self.active_ap.remove_all_vlan()

    def _saveConfig(self):
        logging.info("Save AP firmware setting")
        self.old_fw_info = self.active_ap.get_fw_upgrade_setting()

    def _defineVlanParams(self, wlan_if, vlan_id, tagged = True):

        vlan_cfg = dict(native_wlan=wlan_if,
                        vlan_id=vlan_id)
        if tagged: vlan_cfg['eth_tagged_port'] = self._defineEthIntfList(True)
        else: vlan_cfg['eth_native_port'] = self._defineEthIntfList(False)

        return vlan_cfg

    def _defineEthIntfList(self, vlan_tagged = True):
        # Define ethernet port list for VLAN
        active_eth_interface = self.active_ap.get_eth_inferface_name()
        eth_list = self.active_ap.get_all_eth_interface()
        temp = []
        for eth in eth_list:
            if not vlan_tagged:
                if active_eth_interface != eth['interface']:
                    temp.append(str(self._getIntfNum(eth['interface'])))
            else:
                temp.append(str(self._getIntfNum(eth['interface'])))
        eth_port_list = " ".join(temp)

        return eth_port_list

    def _defineTestParams(self, conf):
        self.ap_model = conf['ap_model']
        self.latest_build = conf['latest_build']
        self.upgraded_build = conf['upgraded_build']
        self.ftpserv = self.testbed.ftpserv

        self.fw_conf = dict(auto=False,
                            control='',
                            host=self.ftpserv['ip_addr'],
                            proto='ftp',
                            user=self.ftpserv['username'],
                            password=self.ftpserv['password'])
        logging.info('fw cfg: %s' % pformat(self.fw_conf))

        self.vlanid_1st = '4094'
        self.vlanid_2nd = '1999'
        self.vlancfg_1st = {}
        self.vlancfg_2nd = {}

    def _getIntfNum(self, interface):
        pat_interface = "([0-9]+$)"
        num = -1
        inf_obj = re.search(pat_interface, interface)
        if inf_obj: num = str(inf_obj.group(1))
        else: raise Exception("Wrong interface name")

        return num

