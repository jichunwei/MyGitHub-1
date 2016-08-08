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
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_RateLimiting_WlanGroups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'uplink_rate_limit': 'A string represents the rate limit configured for uplink',
                           'downlink_rate_limit': 'A string represents the rate limit configured for downlink',
                           'margin_of_error': 'A float number represents the acceptable level of error',
                           'target_station': 'IP address of target station',
                           'active_ap':'mac address (NN:NN:NN:NN:NN:NN)of target ap which client will associate to',
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
        #self._cfgZoneDirector()
        self._cfgRemoveZDWlanGroupsAndWlan()

        # Activate the active APs
        self._findActiveAP()
        
        self._cfg_wlanForAP()
        
        self._isolateAPWithWlanGroups()

    def test(self):
        for wlan_id in range(self.number_of_ssid):
            self.wlan_cfg['ssid'] = "%s-%d" % (self.wlan_ssid, wlan_id + 1)
            self._configClientToAssocWlan(self.wlan_cfg['ssid'])
            if self.errmsg: return ("FAIL", self.errmsg)
            
            self._get_clientWifiAddress()
            if self.errmsg: return ("FAIL", self.errmsg)
            
            self._testClientAllowToReachDest()
            if self.errmsg: return ('FAIL', self.errmsg)
            
            self._testUplinkActiveAP_Shaper()
            if self.errmsg: return ('FAIL', self.errmsg)
            
            self._testDownlinkActiveAP_Shaper()
            if self.errmsg: return ('FAIL', self.errmsg)
            
            self._verifyZingUplinkTraffic()
            if self.errmsg: return ('FAIL', self.errmsg)
            
            self._verifyZingDownlinkTraffic()
            if self.errmsg: return ('FAIL', self.errmsg)
                
            self._cfgTargetSation()

        msg = "ActiveAP[%s %s %s %s] can support RateLimit(UP/DN)[%s %s] with WLANs[%d] " \
            % (self.conf['active_ap'], self.active_ap.get_ap_model(),
                self.active_ap.get_base_mac(), self.active_ap.ip_addr,
                self.conf['uplink_rate_limit'], self.conf['downlink_rate_limit'], self.number_of_ssid)
        return ("PASS", msg)

    def cleanup(self):
        #self._cfgRemoveZDWlanGroupsAndWlan()
        pass

    def _initTestParams(self, conf):
        # Define test parameters
        # Security setting used for the test is open-none
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3,
                          radio_mode = '',
                          sending_time = 30,
                          test_port = 3000,
                          wlan_cfg = {})
        self.conf.update(conf)
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", conf['uplink_rate_limit'], re.I)
        up_rate_opt = '^' + rate_obj.group(1) + self._get_bw_symbol(rate_obj.group(2)) + r"|" + self._get_float_mbps_symbol(rate_obj.group(1), rate_obj.group(2))
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", conf['downlink_rate_limit'], re.I)
        down_rate_opt = '^' + rate_obj.group(1) + self._get_bw_symbol(rate_obj.group(2)) + r"|" + self._get_float_mbps_symbol(rate_obj.group(1), rate_obj.group(2)) 
        self.conf['wlan_cfg'] = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                                 'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': False,
                                 'ad_domain': '', 'ad_port': '', 'key_string': '',
                                 'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': '',
                                 'uplink_rate_limit': up_rate_opt,
                                 'downlink_rate_limit': down_rate_opt}
        self.conf['wlan_cfg']['ssid'] = "rat-ratelimit"
        self.wlan_ssid = tmethod.touch_ssid(self.conf['wlan_cfg']['ssid']) 
        #if not self.conf.has_key('wgs_cfg'):
        #    self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg(self.conf['radio_mode'])
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wgs_cfg = self.conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.linuxPC = self.testbed.components['LinuxServer']
        self.error_margin = conf['margin_of_error']
        self.number_of_ssid = conf['number_of_ssid']
        self.traffic_srv_addr = conf['traffic_srv_addr']
        self.target_station = None
        self.errmsg = ''
        self.test_rate_opt = ['1mbps', '2mbps', '5mbps', '10mbps', '20mbps', '50mbps']

    def _calculate_rate_value(self):
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", self.conf['uplink_rate_limit'], re.I)
        if not rate_obj:
            raise Exception("Invalid rate litmit value (%s)" % self.conf['uplink_rate_limit'])
        if re.match(r"(^kbps)", rate_obj.group(2), re.I):
            self.uplink_ratelimit_mbps = float(rate_obj.group(1)) / 1000.0
            self.uplink_ratelimit_kbps = rate_obj.group(1)
        else:
            self.uplink_ratelimit_mbps = float(rate_obj.group(1))
            self.uplink_ratelimit_kbps = int(rate_obj.group(1)) * 1000
        self.uplink_ratelimit_w_error_mbps = self.uplink_ratelimit_mbps * (1.0 + self.error_margin)

        rate_obj = re.match("([0-9]+)\s*([k|m]bps)", self.conf['downlink_rate_limit'], re.I)
        if not rate_obj:
            raise Exception("Invalid rate litmit value (%s)" % self.conf['downlink_rate_limit'])
        if re.match(r"(^kbps)", rate_obj.group(2), re.I):
            self.downlink_ratelimit_mbps = float(rate_obj.group(1)) / 1000.0
            self.downlink_ratelimit_kbps = rate_obj.group(1)
        else:
            self.downlink_ratelimit_mbps = float(rate_obj.group(1))
            self.downlink_ratelimit_kbps = int(rate_obj.group(1)) * 1000
        self.downlink_ratelimit_w_error_mbps = self.downlink_ratelimit_mbps * (1.0 + self.error_margin)

    def _cfgTargetSation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                      , self.testbed.components['Station']
                                                      , check_status_timeout = self.conf['check_status_timeout']
                                                      , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])
        
    def _findActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in testbed." % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.get_base_mac().lower()

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

    def _cfg_wlanForAP(self):
        for wlan_id in range(self.number_of_ssid):
            self.wlan_cfg['ssid'] = "%s-%d" % (self.wlan_ssid, wlan_id + 1)
            logging.info("Configure a WLAN with SSID %s on the Zone Director with uplink and downlink rate limits %s - %s" % 
                         (self.wlan_cfg['ssid'], self.wlan_cfg['uplink_rate_limit'], self.wlan_cfg['downlink_rate_limit']))
            bugme.do_trace_on('TRACE_RL')
            self.zd.cfg_wlan(self.wlan_cfg)
            lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                           self.wlan_cfg['ssid'])
        
        
    def _isolateAPWithWlanGroups(self):
        (self.wgs_apinfo, self.ap_xstatus) = \
            tmethod8.assign_1ap_to_exist_wlan_with_wlan_groups(self.zd,
                                                         self.active_ap_mac,
                                                         self.wgs_cfg)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')

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

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        #logging.info("Remove all Wlan Groups on the Zone Director.")
        #lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        #logging.info("Remove all WLAN on the Zone Director.")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        
    def _configClientToAssocWlan(self, wlan_ssid):
        self.wlan_cfg['ssid'] = wlan_ssid
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station,
                                                    self.wlan_cfg,
                                                    self.conf['check_status_timeout'])

    def _get_clientWifiAddress(self):
        (isOK, ip_addr, mac_addr) = tmethod.renew_wifi_ip_address(self.target_station,
                                                                self.conf['check_status_timeout'])
        if not isOK:
            self.errmsg = mac_addr
        else:
            self.wifi = dict(ip_addr = ip_addr, mac_addr = mac_addr)
            
    def _testClientAllowToReachDest(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                          self.wifi['ip_addr'],
                                                          ping_timeout_ms = self.conf['ping_timeout'] * 1000)

    def _testUplinkActiveAP_Shaper(self):
        ap_shaper = self.active_ap.get_shaper(self.wlan_cfg['ssid'])
        ap_shaper_up_obj = re.match(r"(\d+)", ap_shaper['up'])
        logging.info("Verify the Shaper[upstream] is %s in ActiveAP[%s]" % (ap_shaper['up'], self.active_ap.get_base_mac()))
        if ap_shaper_up_obj.group(1) != str(self.uplink_ratelimit_kbps):
            self.errmsg = "The shaper[up] setting is %s instead of %s in AP[%s]" % (ap_shaper['up'], self.conf['uplink_rate_limit'], self.active_ap.get_base_mac())        
        
    def _testUplinkPerformance(self):
        up_rate = self.conf['uplink_rate_limit'].replace(' ', '').lower()
        if up_rate in self.zap_test_opt:
            logging.info("Send traffic from the target station to an uplink destination")
            uplink_performance = self._zapTest(self.target_station, self.wifi['ip_addr'], self.traffic_srv_addr)
            logging.info("The allowed rate limit is %.3f mbps" % self.uplink_ratelimit_w_error_mbps)
            if uplink_performance > self.uplink_ratelimit_w_error_mbps:
                self.errmsg = "The measured rate was %.3f mbps" % uplink_performance
                self.errmsg += " which is higher than expected (%.3f mbps)" % self.uplink_ratelimit_w_error_mbps
                self.errmsg += " on WLAN %s" % self.wlan_cfg['ssid']
    
    def _testDownlinkActiveAP_Shaper(self):
        ap_shaper = self.active_ap.get_shaper(self.wlan_cfg['ssid'])
        ap_shaper_dn_obj = re.match(r"(\d+)", ap_shaper['down'])
        logging.info("Verify the Shaper[downstream] is %s in ActiveAP[%s]" % (ap_shaper['down'], self.active_ap.get_base_mac()))
        if ap_shaper_dn_obj.group(1) != str(self.downlink_ratelimit_kbps):
            self.errmsg = "The shaper[down] setting is %s instead of %s in AP[%s]" % (ap_shaper['down'], self.conf['downlink_rate_limit'], self.active_ap.get_base_mac())               
            
    def _testDownlinkPerformance(self):
        down_rate = self.conf['downlink_rate_limit'].replace(' ', '').lower()
        if down_rate in self.zap_test_opt:
            logging.info("Send traffic from an uplink station downlink to the target station")
            downlink_performance = self._zapTest(self.target_station, self.traffic_srv_addr, self.wifi['ip_addr'])
            logging.info("The allowed rate limit is %.3f mbps" % self.downlink_ratelimit_w_error_mbps)
            if downlink_performance > self.downlink_ratelimit_w_error_mbps:
                self.errmsg = "The measured rate was %.3f mbps" % downlink_performance
                self.errmsg += " which is higher than expected (%.3f mbps)" % self.downlink_ratelimit_w_error_mbps
                self.errmsg += " on WLAN %s" % self.wlan_cfg['ssid']

    def _zapTest(self, sta, zapd_host1, zapd_host2):
        try:
            zap_res = sta.send_zap(sip = zapd_host1,
                                  dip = zapd_host2,
                                  period = 50000,
                                  payload_len = 1400,
                                  time_run = 30,
                                  qos = "0xa0",
                                  test_tcp = False)
        except Exception, e:
            if e.message.find("Test result file was not created") != -1:
                # Resend traffic if it was not done properly
                zap_res = sta.send_zap(sip = zapd_host1,
                                      dip = zapd_host2,
                                      period = 50000,
                                      payload_len = 1400,
                                      time_run = 30,
                                      qos = "0xa0",
                                      test_tcp = False)       
            else:
                raise

        logging.info("The percentile 50%% is %.3f mbps" % zap_res["50.0"])        
        return zap_res["50.0"]

    def _verifyZingUplinkTraffic(self):
        # only send zing traffice on rate limit more than 1mbps
        if re.search(r"(mbps)", self.conf['uplink_rate_limit']):        
            # Send downlink traffic from server to target station
            logging.info("[uplink] Send Zing traffic from wireless station to Linux server")
            try:
                traffic_result = self.linuxPC.send_zing(self.wifi['ip_addr'], udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])
            except:
                # Re send traffic if it was not done properly
                traffic_result = self.linuxPC.send_zing(self.wifi['ip_addr'], udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])
    
            logging.info(traffic_result)
            self._verifyTrafficRate(traffic_result['50.0'], self.uplink_ratelimit_w_error_mbps)

    def _verifyZingDownlinkTraffic(self):
        # only send zing traffice on rate limit more than 1mbps
        if re.search(r"(mbps)", self.conf['downlink_rate_limit']):
            self._kill_zing()
            # Start Zing server on Linux PC
            self.linuxPC.start_zing_server(port = self.conf['test_port'])
            # Send uplink traffic from Client to server
            logging.info("[downlink]Send Zing traffic from Linux server to wireless station")
            try:
                traffic_result = self.target_station.send_zing(host = self.linuxPC.ip_addr, udp = True, port = self.conf['test_port'],
                                                              sending_time = self.conf['sending_time'])
            except Exception, e:
                if "Test result file was not created" in e.message:
                    # Re send traffic if it was not done properly
                    traffic_result = self.target_station.send_zing(host = self.linuxPC.ip_addr, udp = True, port = self.conf['test_port'],
                                                                  sending_time = self.conf['sending_time'])
                else:
                    raise
    
            self._verifyTrafficRate(traffic_result['50.0'], self.downlink_ratelimit_w_error_mbps)
    
    def _verifyTrafficRate(self, rate_at_50_percentile, allowed_rate):
        logging.info("The percentile 50%% is %.3f mbps" % float(rate_at_50_percentile))
        logging.info("The allowed rate limit is %.3f mbps" % allowed_rate)
        if float(rate_at_50_percentile) > allowed_rate: 
            msg = "The measured rate was %.3f mbps" % float(rate_at_50_percentile)
            msg += " which is higher than expected (%.3f mbps)" % allowed_rate
            logging.info(msg)
            self.errmsg = msg

    def _kill_zing(self):
        self.linuxPC.kill_zing()
        time.sleep(3)

