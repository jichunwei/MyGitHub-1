# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AD_MGMT_Enable_Disable class tests the very basic of Adapter MGMT features.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC

    Test parameters: {'target_station': 'IP address of the remote linux pc',
                      'active_ap':'IP address of the active AP',
                      'active_ad':'IP address of the active adapter',
                      'ip': 'IP address to ping. This is ip address of station behind the AP'}

    Result type: PASS/FAIL
    Results: PASS: When enabling local-link management on both of AP and adapter, AP can ping to adapter's link-local
                    address, and vice versa. But when disabling link-local management on one of two devices
                    (AP and adapter), AP can not ping to adapter's link-local address and vice versa.
             FAIL: If one of the above criteria is not safisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and target station in the testbed.
        - Save the current link-local management configuration on the active AP and active adapter
    2. Test:
        - Turn off all wlans on non-active APs
        - Enable link-local management on the active Ap and active adapter
        - Verify that sta-mgmt on the AP and AD is enabled and is in active state
        - On the AP, do a ping to the link local ip address of the AD. Verify that ping will be succeeded, and vice versa.
        - Disable link-local management on the active AP. Verify that sta-mgmt on the AP is disabled,
        sta-mgmt on the AD is enabled but is in inactive status now.
        - Verify that AP can not ping to the link local ip address of AD and vice versa
    3. Cleanup:
        - Return the previous configuration of link-local management on the AP and AD
        - Down svcp interface on the active AP

    How is is tested:
        - After enabling link-local adapter management on the AP and AD and before doing a ping to link-local ip address
         between them, login to CLI and disable this feature on the AP.
         The script should return FAIL and report that can not ping to link local ip address of AD from AP.
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class AD_MGMT_Enable_Disable(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of the active ap',
                             'active_ad': 'ip address of the active ad',
                             'target_station': 'ip address of remote linux PC',
                             'ip': 'ip address to ping. This is ip address of station behind the AP'}

    def config(self, conf):
        self.target_station = None
        self.active_ap = None
        self.ad_config = {}

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])
        self.ip_addr = conf['ip']
        self.ping_timeout = 30
        self.check_status_timeout = 90
        self.link_local_subnet = "169.254.54.0"
        self.ap_channel = '6'
        self.wlan_if = 'wlan0'

        # Find exactly target station
        self.target_station = getStation(conf['target_station'], self.testbed.components['Station'])
        self.target_sta_ip_addr = getLinuxIpAddr(self.target_station, self.testbed.sta_wifi_subnet)

        # Find the active AP object
        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed, conf['active_ap'], self.testbed.components['AP'],
                                            self.ap_channel, 'wlan0')

        # Get active adapter configuration information
        self.ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)

        logging.info("Save the current link-local management configuration on the active AP and active AD")
        self.cur_ap_sta_mgmt = self.active_ap.get_sta_mgmt('wlan0')
        self.cur_ad_sta_mgmt = self.target_station.get_ad_sta_mgmt(self.ad_config, 'wlan0')

    def test(self):
        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='MGMT_%s' % self.wlan_if,
                        wlan_if='%s' % self.wlan_if)
        logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
        self.active_ap.cfg_wlan(wlan_cfg)

        ad_wlan_cfg = wlan_cfg.copy()
        ad_wlan_cfg['wlan_if'] = 'wlan0'
        logging.info("Configure a WLAN with SSID %s  on the active adapter" % wlan_cfg['ssid'])
        self.target_station.cfg_wlan(self.ad_config, ad_wlan_cfg)

        logging.info("Turn on the svcp interface on the active adapter %s" % self.ad_ip_addr)
        self.target_station.set_ruckus_ad_state(self.ad_config, 'up', 'wlan0')

        # Verify connection between stations
        verifyStaConnection(self.target_station, self.target_sta_ip_addr, self.ip_addr)

        tries = 3
        while tries:
            logging.info("Enable link-local management on the active AP %s" % self.ap_ip_addr)
            self.active_ap.set_sta_mgmt('wlan0', True)

            logging.info("Enable link-local management on the active adapter %s" % self.ad_ip_addr)
            self.target_station.set_ad_sta_mgmt(self.ad_config, 'wlan0', True)
            time.sleep(2)

            logging.info("Verify that STA-Management on the AP and adapter is enabled and is in active state")
            res, msg = verifyStaMGMT(self.active_ap, None, self.check_status_timeout)
            if res == "FAIL":
                return [res, msg]

            res, msg = verifyStaMGMT(None, self.target_station, self.check_status_timeout, self.ad_config)
            if res == "FAIL":
                return [res, msg]
            logging.info("STA-Management is enabled and in active state on the AP and adapter")

            logging.info("Get link local ip address on the active AP and the active adapter")
            # Find link local ip address on the AP
            ap_res = self.active_ap.get_bridge_if_cfg()
            res = self._getLinkLocalIpAddr(ap_res)
            if not res:
                raise Exception("Can not find link local ip address on the AP %s" % self.ap_ip_addr)
            ap_link_local_ip_addr = res
            logging.info("Link local ip address on the AP is: %s" % ap_link_local_ip_addr)

            # Find link local ip address on the adapter
            ad_res = self.target_station.get_ad_if_brd_config(self.ad_config)
            res = self._getLinkLocalIpAddr(ad_res)
            if not res:
                raise Exception("Can not find link local ip address on the adapter" % self.ad_ip_addr)
            ad_link_local_ip_addr = res
            logging.info("Link local ip address on the adapter is: %s" % ad_link_local_ip_addr)

            # Ping
            msg = "Do a ping to the adapter's link local ip address %s " % ad_link_local_ip_addr
            msg += "from the the AP's link local ip address %s" % ap_link_local_ip_addr
            logging.info(msg)
            ap_ping_res = self.active_ap.ping_from_ap(ad_link_local_ip_addr, self.ping_timeout * 1000)
            if ap_ping_res.find("Timeout") != -1:
                logging.info("Ping FAILED")
                msg = "Can not ping to adapter's link local ip address %s " % ad_link_local_ip_addr
                msg += "from the AP while STA-Management is enabled and active"
                return ["FAIL", msg]
            logging.info("Ping from AP to ip address %s successfully" % ad_link_local_ip_addr)

            msg = "Do a ping to the AP's link local ip address %s " % ap_link_local_ip_addr
            msg += "from the the adapter's link local ip address %s" % ad_link_local_ip_addr
            logging.info(msg)
            ad_ping_res = self.target_station.ping_from_ad(self.ad_config, ap_link_local_ip_addr, self.ping_timeout * 1000)
            if ad_ping_res.find("Timeout") != -1:
                logging.info("Ping FAILED")
                msg = "Can not ping to AP's link local ip address %s " % ap_link_local_ip_addr
                msg += "from the adapter while STA-Management is enabled and active"
                return ["FAIL", msg]
            logging.info("Ping from adapter to ip address %s successfully" % ap_link_local_ip_addr)

            msg = "Try to ping from adapter %s to IP address %s of the active AP" % (self.ad_ip_addr, self.ap_ip_addr)
            msg += " to verify routing ability of AP and adapter after enabling sta-mgmt"
            logging.info(msg)
            ad_ping_res = self.target_station.ping_from_ad(self.ad_config, self.ap_ip_addr, self.ping_timeout * 1000)
            if ad_ping_res.find("Timeout") != -1:
                logging.info("Ping FAILED")
                msg = "Can not ping to AP's ip address %s from the adapter %s " % (self.ap_ip_addr, self.ad_ip_addr)
                msg += " while STA-Management is enabled and active"
                return ["FAIL", msg]
            logging.info("Ping from adapter to ip address %s successfully" % self.ap_ip_addr)

            logging.info("Disable STA-Management on the active AP %s" % self.ap_ip_addr)
            self.active_ap.set_sta_mgmt('wlan0', False)
            time.sleep(3)

            logging.info("Verify that STA-Management on the AP is disabled")
            ap_sta_mgmt = self.active_ap.get_sta_mgmt('wlan0')
            if ap_sta_mgmt['enable']:
                return ["FAIL", "The AP STA-Management is still enabled although it's turned off"]

            msg = "Verify that information of link local ip address "
            msg += "does not exist because STA-Management is down"
            logging.info(msg)
            ap_res = self.active_ap.get_bridge_if_cfg()
            res = self._getLinkLocalIpAddr(ap_res)
            if res:
                logging.debug("Link local ip address: %s" % res)
                return ["FAIL", "Link local ip address on the AP does not disappear while STA-Management is disabled"]

            ad_res = self.target_station.get_ad_if_brd_config(self.ad_config)
            res = self._getLinkLocalIpAddr(ad_res)
            if res:
                logging.debug("Link local ip address: %s" % res)
                return ["FAIL", "Link local ip address on the adapter does not disappear while STA-Management is disabled"]
            msg = "Information of link local ip address on the AP and adapter completely disappear "
            msg += "because STA-Management is disabled"
            logging.info(msg)

            # Ping again
            logging.info("From the AP, try to ping to adapter link local ip address %s once more" % ad_link_local_ip_addr)
            ap_ping_res = self.active_ap.ping_from_ap(ad_link_local_ip_addr, self.ping_timeout * 1000)
            if ap_ping_res.find("Timeout") == -1:
                logging.info("Ping OK. Incorrect behavior")
                msg = "Ping from AP to adapter's link local ip address successfully while STA-Manamgement is disabled"
                msg += "and information of link local subnet on the adapter does not exist"
                return ["FAIL", msg]
            logging.info("Ping FAILED. Correct behavior")

            logging.info("From the adapter, try to ping to AP link local ip address %s once more" % ap_link_local_ip_addr)
            ad_ping_res = self.target_station.ping_from_ad(self.ad_config, ap_link_local_ip_addr, self.ping_timeout * 1000)
            if ad_ping_res.find("Timeout") == -1:
                logging.info("Ping OK. Incorrect behavior")
                msg = "Ping from AP to adapter's link local ip address successfully while STA-Manamgement is disabled"
                msg += "and information of link local subnet on the adapter does not exist"
                return ["FAIL", msg]
            logging.info("Ping FAILED. Correct behavior")

            msg = "Try to ping from adapter %s to IP address %s of the active AP" % (self.ad_ip_addr, self.ap_ip_addr)
            msg += " to make sure that AP and adapter does not have routing ability after disabling sta-mgmt"
            logging.info(msg)
            ad_ping_res = self.target_station.ping_from_ad(self.ad_config, self.ap_ip_addr, self.ping_timeout * 1000)
            if ad_ping_res.find("Timeout") == -1:
                logging.info("Ping OK. Incorrect behavior")
                msg = "Adapter %s can ping ip address %s of AP successfully" % (self.ad_ip_addr, self.ap_ip_addr)
                msg += " while STA-Management is disabled"
                return ["FAIL", msg]
            logging.info("Ping FAILED. Correct behavior")

            tries = tries - 1
            if tries:
                logging.info("Finish test steps. Try to perform test enable/disable Link-Local Adapter Management again")
            time.sleep(3)

        return ["PASS", ""]

    def cleanup(self):

        if self.active_ap:
            logging.info("Return the previous status of STA-Management")
            self.active_ap.set_sta_mgmt('wlan0', self.cur_ap_sta_mgmt['enable'])

            logging.info("Down svcp interface on the active AP")
            self.active_ap.set_state('wlan0', 'down')
            time.sleep(2)

        if self.ad_config:
            logging.info("Return the previous status of STA-Management")
            self.target_station.set_ad_sta_mgmt(self.ad_config, 'wlan0', self.cur_ad_sta_mgmt['enable'])

            logging.info("Down svcp interface on the active Adapter")
            self.target_station.set_ruckus_ad_state(self.ad_config, 'down', 'wlan0')

        logging.info("---------- FINISH ----------")

    def _getLinkLocalIpAddr(self, ifconfig_res):
        """
        Get link local ip address of the AP or adapter
        """
        # Find ip address of subinterface bridge that corresponding with svcp interface
        link_local_ip_addr = ""
        for key, value in ifconfig_res.iteritems():
            network = get_network_address(value['ip_addr'], value['mask'])
            if network == self.link_local_subnet:
                link_local_ip_addr = value['ip_addr']
                break
        return link_local_ip_addr
