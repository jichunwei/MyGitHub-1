# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_RateLimiting Test class tests the ability of ZD to control the uplink and downlink rate limits
on the wireless clients

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'uplink_rate_limit': 'A string represents the rate limit configured for uplink',
                    'downlink_rate_limit': 'A string represents the rate limit configured for downlink',
                    'margin_of_error': 'A float number represents the acceptable level of error',
                    'target_station': 'IP address of target station',
                    'traffic_srv_addr': 'IP address of the zapd server in the distribution network',
                    'number_of_ssid': 'Number of SSID should be verified on Zone Director'
                    'active_ap': the symbolic name or mac address of the active ap

   Result type: PASS/FAIL/ERROR
   Results: PASS: the measured rate limits should not be higher than the configured values within the
                  given margin of error
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Configure a WLAN with simple security setting
       - Configure uplink and downlink rate limits for this WLAN
       - Configure a WLAN profile on the target station with the same security setting
       - Keep WLAN interface 'Up' only in the Active APs, 'down' in none active ones.
   2. Test:
       - Perform a ping from the target station to a destination uplink
       - Run zap to send traffic from the target station to a destination uplink
       - Verify that the percentile 50% result is within the configured rate limit
       - Run zap to send traffic from a system in the distribution network downlink to the target station
       - Verify that the percentile 50% result is within the configured rate limit
   3. Cleanup:
       - Remove all wlan configuration
       - Remove wireless profile on remote wireless STA
       - Verify that wireless station is completely disconnected after removing the wireless profile.

   How it is tested?
       - Right after the rate limits are configured on the ZD, open another browser, login to ZD, and
         disable the rate limits for the WLAN. This results in the measured rates are higher than the
         given values and the script should report FAIL
"""

import os
import re
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_RateLimiting(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'uplink_rate_limit': 'A string represents the rate limit configured for uplink',
                           'downlink_rate_limit': 'A string represents the rate limit configured for downlink',
                           'margin_of_error': 'A float number represents the acceptable level of error',
                           'target_station': 'IP address of target station',
                           'traffic_srv_addr': 'IP address of the zapd server in the distribution network',
                           'number_of_ssid': 'Number of SSID should be verified on Zone Director'}

    def config(self, conf):
        # Init testing pararmeters
        self._initTestParams(conf)

        # Calculate rate limit value from testing parameters
        self._calculate_rate_value()

        # Configuration on the target station to cleanup the wlan interface and wireless connections
        self._cfgTargetSation()

        # Configuration on Zone Director for testing
        self._cfgZoneDirector()

        # Activate the active APs
        self._cfgActiveAPs()

    def test(self):
        for wlan_id in range(self.number_of_ssid):
            self.wlan_cfg['ssid'] = "%s-%d" % (self.ssid_prefix, wlan_id + 1)
            logging.info("Verify rate limit rules on the WLAN %s" % self.wlan_cfg['ssid'])
            logging.info("Configure a WLAN profile with SSID %s on the target station %s" % (self.wlan_cfg['ssid'],
                                                                                             self.target_station.get_ip_addr()))
            self.target_station.cfg_wlan(self.wlan_cfg)

            logging.info("Make sure the station associates to the WLAN")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "connected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station didn't associate to the WLAN '%s' after %d seconds" % \
                                    (self.wlan_cfg['ssid'], self.check_status_timeout))

            logging.info("Renew IP address of the wireless adapter on the target station")
            self.target_station.renew_wifi_ip_address()

            logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % 
                         self.target_station.get_ip_addr())
            start_time = time.time()
            sta_wifi_ip_addr = None
            sta_wifi_mac_addr = None
            while time.time() - start_time < self.check_status_timeout:
                sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
                if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0":
                    break
                time.sleep(1)
            logging.debug("Wifi IP: %s ---- Wifi MAC: %s" % (sta_wifi_ip_addr, sta_wifi_mac_addr))
            if not sta_wifi_mac_addr:
                msg = "Unable to get MAC address of the wireless adapter of the target station %s" % \
                      self.target_station.get_ip_addr()
                raise Exception(msg)
            if not sta_wifi_ip_addr:
                msg = "Unable to get IP address of the wireless adapter of the target station %s" % \
                      self.target_station.get_ip_addr()
                raise Exception(msg)
            if sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169.254"):
                msg = "The target station %s could not get IP address from DHCP server" % \
                      self.target_station.get_ip_addr()
                return ("FAIL", msg)

            logging.info("Verify connection from the target station to the traffic server")
            ping_result = self.target_station.ping(self.traffic_srv_addr, 5 * 1000)
            if ping_result.find("Timeout") != -1:
                logging.info("Ping FAILED. Incorrect behavior")
                return ("FAIL", "The target station could not ping to %s" % self.traffic_srv_addr)
            else:
                logging.info("Ping OK. Correct behavior")

            logging.info("Send traffic from the target station to an uplink destination")
            try:
                zap_res = self.target_station.send_zap(sip = sta_wifi_ip_addr, dip = self.traffic_srv_addr,
                                                      period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
            except Exception, e:
                if e.message.find("Test result file was not created") != -1:
                    # Resend traffic if it was not done properly
                    zap_res = self.target_station.send_zap(sip = sta_wifi_ip_addr, dip = self.traffic_srv_addr,
                                                          period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
                else:
                    raise

            logging.info("The percentile 50%% is %.3f mbps" % zap_res["50.0"])
            logging.info("The allowed rate limit is %.3f mbps" % self.uplink_ratelimit_w_error_mbps)
            if zap_res["50.0"] > self.uplink_ratelimit_w_error_mbps:
                msg = "The measured rate was %.3f mbps" % zap_res["50.0"]
                msg += " which is higher than expected (%.3f mbps)" % self.uplink_ratelimit_w_error_mbps
                msg += " on WLAN %s" % self.wlan_cfg['ssid']
                return ("FAIL", msg)

            if zap_res["50.0"] <= self.min_rate:
                msg = "The measured rate was %.3f mbps" % zap_res["50.0"]
                msg += " which is lower than expected (%.3f mbps)" % self.min_rate
                msg += " on WLAN %s" % self.wlan_cfg['ssid']
                return ("FAIL", msg)

            logging.info("Send traffic from an uplink station downlink to the target station")
            try:
                zap_res = self.target_station.send_zap(sip = self.traffic_srv_addr, dip = sta_wifi_ip_addr,
                                                      period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
            except Exception, e:
                if e.message.find("Test result file was not created") != -1:
                    # Resend traffic if it was not done properly
                    zap_res = self.target_station.send_zap(sip = self.traffic_srv_addr, dip = sta_wifi_ip_addr,
                                                          period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
                else:
                    raise

            logging.info("The percentile 50%% is %.3f mbps" % zap_res["50.0"])
            logging.info("The allowed rate limit is %.3f mbps" % self.downlink_ratelimit_w_error_mbps)
            if zap_res["50.0"] > self.downlink_ratelimit_w_error_mbps:
                msg = "The measured rate was %.3f mbps" % zap_res["50.0"]
                msg += " which is higher than expected (%.3f mbps)" % self.downlink_ratelimit_w_error_mbps
                msg += " on WLAN %s" % self.wlan_cfg['ssid']
                return ("FAIL", msg)

            if zap_res["50.0"] <= self.min_rate:
                msg = "The measured rate was %.3f mbps" % zap_res["50.0"]
                msg += " which is lower than expected (%.3f mbps)" % self.min_rate
                msg += " on WLAN %s" % self.wlan_cfg['ssid']
                return ("FAIL", msg)

            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                    self.check_status_timeout)

            logging.info("Finish verifying rate limit rules for the WLAN %s" % self.wlan_cfg['ssid'])

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the configuration on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                    self.check_status_timeout)

    def _initTestParams(self, conf):
        # Define test parameters
        # Security setting used for the test is open-none
        self.conf = conf
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", conf['uplink_rate_limit'], re.I)
        up_rate_opt = '^' + rate_obj.group(1) + self._get_bw_symbol(rate_obj.group(2)) + r"|" + self._get_float_mbps_symbol(rate_obj.group(1), rate_obj.group(2))
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", conf['downlink_rate_limit'], re.I)
        down_rate_opt = '^' + rate_obj.group(1) + self._get_bw_symbol(rate_obj.group(2)) + r"|" + self._get_float_mbps_symbol(rate_obj.group(1), rate_obj.group(2))
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': False,
                         'ad_domain': '', 'ad_port': '', 'ssid': 'rat-rate-limit-testing', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': '',
                         'uplink_rate_limit': up_rate_opt,
                         'downlink_rate_limit': down_rate_opt}
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.error_margin = conf['margin_of_error']
        self.min_rate = conf.get('min_rate') if conf.get('min_rate') else 0
        self.number_of_ssid = conf['number_of_ssid']
        self.traffic_srv_addr = conf['traffic_srv_addr']
        self.ssid_prefix = "rat-rate-limit-testing-wlan"
        self.target_station = None

    def _calculate_rate_value(self):
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", self.conf['uplink_rate_limit'], re.I)
        if not rate_obj:
            raise Exception("Invalid rate litmit value (%s)" % self.conf['uplink_rate_limit'])
        if re.match(r"(^kbps)", rate_obj.group(2), re.I):
            self.uplink_ratelimit_mbps = float(rate_obj.group(1)) / 1000.0
        else:
            self.uplink_ratelimit_mbps = float(rate_obj.group(1))
        self.uplink_ratelimit_w_error_mbps = self.uplink_ratelimit_mbps * (1.0 + self.error_margin)

        rate_obj = re.match("([0-9]+)\s*([k|m]bps)", self.conf['downlink_rate_limit'], re.I)
        if not rate_obj:
            raise Exception("Invalid rate litmit value (%s)" % self.conf['downlink_rate_limit'])
        if re.match(r"(^kbps)", rate_obj.group(2), re.I):
            self.downlink_ratelimit_mbps = float(rate_obj.group(1)) / 1000.0
        else:
            self.downlink_ratelimit_mbps = float(rate_obj.group(1))
        self.downlink_ratelimit_w_error_mbps = self.downlink_ratelimit_mbps * (1.0 + self.error_margin)

    def _cfgTargetSation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.check_status_timeout
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgActiveAPs(self):
        # Get the Actice APs and disable all wlan interface (non mesh interface) in non active aps
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if self.active_ap:
                for ap in self.testbed.components['AP']:
                    if ap is not self.active_ap:
                        logging.info("Remove all WLAN on non-active AP %s" % ap.get_base_mac())
                        ap.remove_all_wlan()

                logging.info("Verify WLAN status on the active AP %s" % self.active_ap.get_base_mac())
                if not self.active_ap.verify_wlan():
                    return ("FAIL", "WLAN %s on active AP %s is not up" % (self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid']),
                                                                           self.active_ap.get_base_mac()))

            else:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        for wlan_id in range(self.number_of_ssid):
            self.wlan_cfg['ssid'] = "%s-%d" % (self.ssid_prefix, wlan_id + 1)
            logging.info("Configure a WLAN with SSID %s on the Zone Director with uplink and downlink rate limits %s - %s" % 
                         (self.wlan_cfg['ssid'], self.wlan_cfg['uplink_rate_limit'], self.wlan_cfg['uplink_rate_limit']))
            bugme.do_trace_on('TRACE_RL')
            self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

    def _get_bw_symbol(self, rate_unit):
        if re.match(r"\s*kbps", rate_unit, re.I):
            return r"\s*[kK]bps"
        elif re.match(r"\s*mbps", rate_unit, re.I):
            return r"\s*[mM]bps"
        else:
            return None

    def _get_float_mbps_symbol(self, rate_value, rate_unit):
        if re.match(r"\s*kbps", rate_unit, re.I):
            return r"^%.2f\s*[mM]bps" % (float(rate_value) / 1000.0)
        
        elif re.match(r"\s*mbps", rate_unit, re.I):
            return r"^%.2f\s*[mM]bps" % float(rate_value)
        
        else:
            return ""

