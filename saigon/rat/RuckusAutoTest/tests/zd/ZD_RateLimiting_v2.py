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

import logging
import re
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zdcli import user

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_RateLimiting_v2(Test):
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
        self._cfgActiveAP()

        # Configure wlan on ZD
        self._cfgWlan()

        # Remove wlan on non-active APs
        self._remove_all_wlanOnNonActiveAPs()

    def test(self):
        for wlan_id in range(self.number_of_ssid):
            self.wlan_cfg['ssid'] = "%s-%d" % (self.wlan_ssid, wlan_id + 1)
            self._configClientToAssocWlan(self.wlan_cfg['ssid'])
            if self.errmsg: return ("FAIL", self.errmsg)
            
            #@author: Jane.Guo @since:2013-12 ZF-5457
            if self.wlan_cfg.get('do_webauth'):
                self._doWebAuth()
                if self.errmsg: return ("FAIL", self.errmsg)

            self._get_clientWifiAddress()
            if self.errmsg: return ("FAIL", self.errmsg)

            self._testClientAllowToReachDest()
            if self.errmsg: return ('FAIL', self.errmsg)

            self._testUplinkActiveAP_Shaper()
            if self.errmsg: return ('FAIL', self.errmsg)

            self._testDownlinkActiveAP_Shaper()
            if self.errmsg: return ('FAIL', self.errmsg)

            if self.conf['testcase'] == 'with-zap':
                self._verifyZapUplinkTraffic()
                if self.errmsg: return ('FAIL', self.errmsg)
                self._verifyZapDownlinkTraffic()
                if self.errmsg: return ('FAIL', self.errmsg)

            if self.conf['testcase'] == 'with-zing':
                self._verifyZingUplinkTraffic()
                if self.errmsg: return ('FAIL', self.errmsg)
                self._verifyZingDownlinkTraffic()
                if self.errmsg: return ('FAIL', self.errmsg)

        msg = "ActiveAP[%s %s %s %s] can support RateLimit(UP/DN)[%s/%s] with [%d] WLANs " \
               % (self.conf['active_ap'], self.active_ap.get_ap_model(),
               self.active_ap.get_base_mac(), self.active_ap.ip_addr,
               self.conf['uplink_rate_limit'], self.conf['downlink_rate_limit'], self.number_of_ssid)
        return ("PASS", msg)

    def cleanup(self):
        logging.info("Remove all the configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

    def _initTestParams(self, conf):
        self.conf = {'wlan_conf':{'auth':'open', 'encryption':'none', 'ssid':'rat-ratelimit'},
                     'ping_timeout':10,
                     'check_status_timeout':120,
                     'margin_of_error':0.1,
                     'min_rate':0,
                     'testcase':'with-zing',
                     'uplink_rate_limit':'5Mbps',
                     'downlink_rate_limit':'5Mbps',
                     'active_ap':'',
                     'target_station': None,
                     'sending_time':30,
                     'test_port':3000}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.linuxPC = self.testbed.components['LinuxServer']
        self.active_ap = None
        self.target_station = None
        self.wlan_ssid = tmethod.touch_ssid(self.conf['wlan_conf']['ssid'])
        self.number_of_ssid = conf['number_of_ssid']

        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", self.conf['uplink_rate_limit'], re.I)
        up_rate_opt = '^' + rate_obj.group(1) + self._get_bw_symbol(rate_obj.group(2)) + r"|" + self._get_float_mbps_symbol(rate_obj.group(1), rate_obj.group(2))
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", self.conf['downlink_rate_limit'], re.I)
        down_rate_opt = '^' + rate_obj.group(1) + self._get_bw_symbol(rate_obj.group(2)) + r"|" + self._get_float_mbps_symbol(rate_obj.group(1), rate_obj.group(2))
        self.conf['wlan_conf'].update({'uplink_rate_limit': up_rate_opt,
                                       'downlink_rate_limit': down_rate_opt})
        self.wlan_cfg = self.conf['wlan_conf']

        self.errmsg = ''

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
        self.uplink_ratelimit_w_error_mbps = self.uplink_ratelimit_mbps * (1.0 + self.conf['margin_of_error'])

        rate_obj = re.match("([0-9]+)\s*([k|m]bps)", self.conf['downlink_rate_limit'], re.I)
        if not rate_obj:
            raise Exception("Invalid rate litmit value (%s)" % self.conf['downlink_rate_limit'])
        if re.match(r"(^kbps)", rate_obj.group(2), re.I):
            self.downlink_ratelimit_mbps = float(rate_obj.group(1)) / 1000.0
            self.downlink_ratelimit_kbps = rate_obj.group(1)
        else:
            self.downlink_ratelimit_mbps = float(rate_obj.group(1))
            self.downlink_ratelimit_kbps = int(rate_obj.group(1)) * 1000
        self.downlink_ratelimit_w_error_mbps = self.downlink_ratelimit_mbps * (1.0 + self.conf['margin_of_error'])


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

    def _cfgTargetSation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.conf['check_status_timeout']
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgActiveAP(self):
        if self.conf.get('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.get_base_mac().lower()

    def _remove_all_wlanOnNonActiveAPs(self):
        if self.active_ap:
            for ap in self.testbed.components['AP']:
                if ap is not self.active_ap:
                    logging.info("Remove all WLAN on non-active AP %s" % ap.ip_addr)
                    ap.remove_all_wlan()

            logging.info("Verify WLAN status on the active AP %s" % self.active_ap.ip_addr)
            if not self.active_ap.verify_wlan():
                raise Exception('Not all wlan are up on active AP %s' % self.active_ap.ip_addr)

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _cfgWlan(self):
        for wlan_id in range(self.number_of_ssid):
            self.wlan_cfg['ssid'] = "%s-%d" % (self.wlan_ssid, wlan_id + 1)
            logging.info("Configure a WLAN with SSID %s on the Zone Director with uplink and downlink rate limits %s - %s" % 
                         (self.wlan_cfg['ssid'], self.wlan_cfg['uplink_rate_limit'], self.wlan_cfg['downlink_rate_limit']))
            bugme.do_trace_on('TRACE_RL')
            lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')

    def _verifyZapUplinkTraffic(self):
        logging.info("Send zap traffic from the target station to an uplink destination")
        try:
            traffic_result = self.target_station.send_zap(sip = self.sta_wifi_ip_addr, dip = self.linuxPC.ip_addr,
                                                      period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
        except Exception, e:
            if e.message.find("Test result file was not created") != -1:
                # Re send traffic if it was not done properly
                traffic_result = self.target_station.send_zap(sip = self.sta_wifi_ip_addr, dip = self.linuxPC.ip_addr,
                                                          period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
            else:
                raise

        self._verifyTrafficRate(traffic_result['50.0'], self.uplink_ratelimit_w_error_mbps, self.conf['min_rate'])

    def _verifyZapDownlinkTraffic(self):
        logging.info("Send zap traffic from an station downlink to the target station")
        try:
            traffic_result = self.target_station.send_zap(sip = self.linuxPC.ip_addr, dip = self.sta_wifi_ip_addr,
                                                         period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
        except Exception, e:
            if e.message.find("Test result file was not created") != -1:
                # Re send traffic if it was not done properly
                traffic_result = self.target_station.send_zap(sip = self.linuxPC.ip_addr, dip = self.sta_wifi_ip_addr,
                                                             period = 50000, payload_len = 300, time_run = 30, test_tcp = True)
            else:
                raise

        self._verifyTrafficRate(traffic_result['50.0'], self.downlink_ratelimit_w_error_mbps, self.conf['min_rate'])

    def _verifyZingUplinkTraffic(self):
        # Send uplink traffic from server to target station
        # client: zing --server -u
        # linux server: zing -host client-ip-addr -u
        if re.search(r"(mbps)", self.conf['uplink_rate_limit']):
            self._kill_zing()
            # Send downlink traffic from server to target station
            logging.info("Send Zing traffic from a Wireless Station to Linux Server")
            try:
                traffic_result = self.linuxPC.send_zing(self.wifi['ip_addr'], udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])
            except:
                # Re send traffic if it was not done properly
                traffic_result = self.linuxPC.send_zing(self.wifi['ip_addr'], udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])

            logging.debug(traffic_result)
            self._verifyTrafficRate(traffic_result['50.0'], self.uplink_ratelimit_w_error_mbps, self.conf['min_rate'])


    def _verifyZingDownlinkTraffic(self):
        # Send uplink traffic from server to target station
        # client: zing -host client-ip-addr -u
        # linux server: zing --server -u
        if re.search(r"(mbps)", self.conf['downlink_rate_limit']):
            self._kill_zing()
            # Start Zing server on Linux PC
            self.linuxPC.start_zing_server(port = self.conf['test_port'])
            # Send uplink traffic from Client to server
            logging.info("Send Zing traffic from Linux Server to Wireless Station")
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
            logging.debug(traffic_result)
            self._verifyTrafficRate(traffic_result['50.0'], self.downlink_ratelimit_w_error_mbps, self.conf['min_rate'])

    def _verifyTrafficRate(self, rate_at_50_percentile, allowed_rate, min_rate = 0):
        logging.info("The percentile 50%% is %.3f mbps" % float(rate_at_50_percentile))
        logging.info("The allowed rate limit is %.3f mbps" % allowed_rate)
        if float(rate_at_50_percentile) > allowed_rate:
            msg = "The measured rate was %.3f mbps" % float(rate_at_50_percentile)
            msg += " which is higher than expected (%.3f mbps)" % allowed_rate
            logging.info(msg)
            self.errmsg = msg

        if float(rate_at_50_percentile) <= min_rate:
            msg = 'The measured rate was %.3f mbps' % float(rate_at_50_percentile)
            msg += ' which is lower than expected (%.3f mbps)' % min_rate
            logging.info(msg)
            self.errmsg = msg
            return

    def _kill_zing(self):
        self.linuxPC.kill_zing()
        time.sleep(3)

    def _testUplinkActiveAP_Shaper(self):
        ap_shaper = self.active_ap.get_shaper(self.wlan_cfg['ssid'])
        ap_shaper_up_obj = re.match(r"(\d+)", ap_shaper['up'])
        logging.info("Verify the Shaper[upstream] is %s in ActiveAP[%s]" % (ap_shaper['up'], self.active_ap.get_base_mac()))
        if ap_shaper_up_obj.group(1) != str(self.uplink_ratelimit_kbps):
            self.errmsg = "The shaper[up] setting is %s instead of %s in AP[%s]" % (ap_shaper['up'], self.conf['uplink_rate_limit'], self.active_ap.get_base_mac())

    def _testDownlinkActiveAP_Shaper(self):
        ap_shaper = self.active_ap.get_shaper(self.wlan_cfg['ssid'])
        ap_shaper_dn_obj = re.match(r"(\d+)", ap_shaper['down'])
        logging.info("Verify the Shaper[downstream] is %s in ActiveAP[%s]" % (ap_shaper['down'], self.active_ap.get_base_mac()))
        if ap_shaper_dn_obj.group(1) != str(self.downlink_ratelimit_kbps):
            self.errmsg = "The shaper[down] setting is %s instead of %s in AP[%s]" % (ap_shaper['down'], self.conf['downlink_rate_limit'], self.active_ap.get_base_mac())

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
    
    def _doWebAuth(self):
        self.user_cfg = {'name': 'local_user', 'fullname': '', 'role': 'Default', 'password': 'local_user', 'number': 1}
        res = user.create_user(self.zdcli, self.user_cfg['name'], self.user_cfg['fullname'], self.user_cfg['role'],
                                    self.user_cfg['password'], self.user_cfg['number'])

        if not res:
            self.errmsg = 'Fail to create users in ZD CLI'
        
        arg = tconfig.get_web_auth_params(self.zd, self.user_cfg['name'], self.user_cfg['password'])
        try:
            self.target_station.perform_web_auth(arg)
        except Exception, e:
            #try it again
            logging.warning(e)
            import time
            time.sleep(10)
            self.target_station.perform_web_auth(arg)