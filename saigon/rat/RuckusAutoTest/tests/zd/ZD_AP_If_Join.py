# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_AP_Join Test class tests the ability of AP to join the ZoneDirector and get the right wlan configuration.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 'auto_approval': 'This is the bool value used to decide if the verified APs is automatically approved
                                     to join the ZD or not.
                                     If auto_approval is True, the APs will automatically discover and join the ZD.
                                     If auto_approval is False, the APs will be manually approved to join the ZD',
                    'active_ap'    : Mac address of the tested AP (XX:XX:XX:XX:XX:XX)

   Result type: PASS/FAIL
   Results: PASS: The AP can join the ZD (manually or automatically), be made provision from ZD successfully,
                   and be in RUN state at the CLI mode, and get the right wlan configuration.
            FAIL:  If one of the above criteria is not met.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all wlan on the ZD
       - Configure 1 wlan with SSID "Netanya_AP_Control", authentication  is open, and encryption is none
       - Navigate to Configure/Access Points page, remove the tested AP out of the Access Points table
       - Set AP approval policy based on the 'auto_approval' value
   2. Test:
       -  Navigate to the Monitor/Access Points to verify that the entry of the tested AP does not appear in the AP-Summary table
       -  If auto_approval is True, APs should discover and join the ZoneDirector successfully.
          If auto_approval is False, APs should be manual approved by clicking "allow" span at
          Monitor/AccessPoints page.
       -  Checking the status of the tested AP in the AP-Summary table is "Connected" (Provision successfully).
       -  At AP CLI mode, using command "get director-info" to make sure that AP is in the RUN state
       -  At AP CLI mode, using command "get wlanlist" to make sure that AP gets the right wlan configuration
   3. Cleanup:
       - Remove all wlan on ZD
       - Return the old AP approval policy for the ZoneDirector

    How it was tested:
    1. After ZD makes provision for the tested AP successfully, telnet to the AP, using command "set state wlan0 down".
    The test script will return FAIL result because AP is not in the right status when made provision from the ZD
"""

import time
import logging
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components.lib.zd import add_mgmt_interface as add_if
from RuckusAutoTest.components.lib.zd import system_zd as sys_zd
from RuckusAutoTest.tests.zd import libZD_TestMethods_Bugs as bust
from RuckusAutoTest.components import create_zd_by_ip_addr
from RuckusAutoTest.components.lib.zd import mgmt_vlan_zd as MVLAN


class ZD_AP_If_Join(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {'auto_approval' : 'This is the bool value uses to decide if the tested AP \
                             is automatically approved to join the ZoneDirector or not',
                             'active_ap'     : 'mac address of the tested ap (XX:XX:XX:XX:XX:XX)'}

    def config(self, conf):

        self.zd = self.testbed.components['ZoneDirector']
        self.flag = False
        self.auto_approval = conf['auto_approval']
        ssid = "Netanya_AP_Control"
        if conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, conf['active_ap'])
            self.mac_addr = self.active_ap.get_base_mac().lower()
        if self.active_ap:
            self.flag = True
        else:
            raise Exception("Active AP not found in test bed")

        self.vlan = conf['vlan'] if conf.has_key('vlan') else ''
        self.new_ip = conf['new_ip'] if conf.has_key('new_ip') else ''
        self.mgmt_vlan = conf['mgmt_vlan'] if conf.has_key('mgmt_vlan') else ''

        if conf.has_key('interface'):
            self.interface = conf['interface']

        # Make sure that the tested AP is connecting to the Zone Director
        start_time = time.time()
        timeout = 150
        while True:
            verified_ap = self.zd.get_all_ap_info(self.mac_addr)
            if verified_ap:
                if verified_ap['status'].lower().startswith("connected"):
                    break
            if time.time() - start_time > timeout:
                raise Exception("The AP %s disconnected from the ZD" % self.mac_addr)

        self.model = verified_ap['model']
        self.old_status = self.zd.get_ap_policy_approval()

        logging.info("Get current configuration of AP %s on the ZD" % self.mac_addr)
        self.ap_cfg = self.zd.get_ap_cfg(self.mac_addr)

        logging.info("Remove all confurations on the ZoneDirector")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        self.wlan_conf = conf['wlan_conf'] if conf.has_key('wlan_conf') else ''
        if conf.has_key('wlan_conf'):
            logging.info("Configure a WLAN with SSID %s on the ZoneDirector" % ssid)
            self.zd.cfg_wlan(conf['wlan_conf'])

        if self.mgmt_vlan:
            MVLAN.set_ap_mgmt_vlan_info(self.zd, {'mgmt_vlan': self.mgmt_vlan})

        if self.interface:
            add_if.enable_mgmt_interface(self.zd, self.interface)

        logging.info("Remove AP %s out of the AccessPoints table" % self.mac_addr)
        self.zd.set_ap_policy_approval(self.auto_approval)
        self.zd.remove_approval_ap(self.mac_addr)

        # Make sure that the tested AP does not exist in the AP-Summary table
        if self.zd.get_all_ap_info(self.mac_addr):
            raise Exception("AP %s still exists in the ZD after removing it" % self.model)
        logging.info("AP %s is removed out of the AP-Summary table now" % self.model)

        #Config vlan for zd
        if self.vlan:
            sys_zd.change_zd_vlan(self.zd, {'vlan':self.vlan})
            time.sleep(150)
            self.zd = create_zd_by_ip_addr(ip_addr=self.new_ip, username = self.zd.username,
                                            password = self.zd.password)

    def test(self):

        if self.interface:
            test_if = bust.login_zd(self.interface['add_if_ip'], self.zd.username, self.zd.password, 60)
            if not test_if:
                return ["FAIL", "The external ZD interface is not in the RUN state"]

        if not self.auto_approval:
            logging.info("Manual approval for AP %s to join the ZoneDirector" % self.model)
            timeout = 120
            start_time = time.time()
            while True:
                ap_info = self.zd.get_all_ap_info(self.mac_addr)
                if ap_info:
                    if ap_info['status'].lower().startswith("approval"):
                        logging.info("The AP %s is in the \"Approval Pending\" status now")
                        logging.info("Approve for this AP to join the ZD: %s" % str(ap_info))
                        self.zd.allow_ap_joining(ap_info['mac'])
                        break
                if time.time() - start_time > timeout:
                    if ap_info:
                        logging.debug("AP info: %s" % str(ap_info))
                        return ["FAIL", "The AP %s is in %s status instead of \"Pending Approval\" \
                                status after %d seconds" % (self.model, ap_info['status'], timeout)]
                    return ["FAIL", "The AP %s does not appear in the AP-Summary table after %d seconds" %
                            (self.model, timeout)]

        logging.info("Wait for the ZoneDirector makes provision for the AP %s" % self.model)
    #JLIN@20100624 since ap code is more bigger in saigon, delay more time to wait ap recovered
        approval_timeout = 240
        start_approval_time = time.time()
        while True:
            self.ap_info = self.zd.get_all_ap_info(self.mac_addr)
            if self.ap_info:
                if self.ap_info['status'].lower().startswith("connected"):
                    logging.info("The provision process for the AP %s is completed successfully" % self.model)
                    break
            if (time.time() - start_approval_time) > approval_timeout:
                if self.ap_info:
                    return ["FAIL", "The AP %s is in the %s status instead of \"Connected\" status after %d seconds" %
                            (self.model, self.ap_info['status'], approval_timeout)]
                return ["FAIL", "The AP %s still does not appear in the AP-Summary table after %d seconds" %
                        (self.model, approval_timeout)]

        time.sleep(2)
        # Make sure that the AP is in RUN state at CLI mode
        self.active_ap.verify_component()

        if not (self.ap_info and tconfig.is_same_if(self.ap_info['ip_addr'],self.zd.get_cfg()['ip_addr'])) :
            return ["FAIL", "The AP %s is not in the same ZD internal interface" % self.model]
        if self.active_ap.get_director_info() != "RUN":
            return ["FAIL", "The AP %s is not in the RUN state" % self.model]
        logging.info("The AP %s is in RUN state now" % self.model)

        # Verify wlan information in AP
        if self.wlan_conf:
            if not self.active_ap.verify_wlan():
                return ["FAIL", "The AP %s got the wrong wlan configuration from the ZoneDirector" % self.model]
            logging.info("The AP %s has received the right wlan configuration from the ZoneDirector" % self.model)

        return ["PASS", "AP cannot join external ZD interface"]

    def cleanup(self):
        logging.info("Remove all the WLANs on the ZoneDirector")
        self.zd.remove_all_wlan()

        logging.info("Return to the old approval policy for ZoneDirector")
        self.zd.set_ap_policy_approval(self.old_status['approval'])

        time.sleep(10)
        logging.info("Return the old configuration for AP %s" % self.mac_addr)
        self.zd.set_ap_cfg(self.ap_cfg)
        logging.info("-------- FINISHED --------\n")

