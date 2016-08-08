# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script use to test the Rate limiting option on the Zone Director
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station': IP address of the target station
                    'active_ap': the AP symbolic name of the active AP. It is the Mesh AP or Root AP
                    'wlan_config_set': list of 32 WLAN configurations will be test.
                                       Default is list of 32 WLANs with 'Open - None' encryption.
                    'uplink_rate_limit'/'downlink_rate_limit': the uplink/downlink rate limit value will be applied to test.

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Create 32 WLANs on the Zone Director base on the 'wlan_config_set'parameter.
   2. Test:
       - Disable all wireless interfaces of the non-active APs.
       - Modify each wlan to enable the Rate-Limit with the uplink/downlink rate limit value.
       - Connect target station to each wlan, transmit the data between uplink and downlink and check udp protocol.
       - Verify the throughput is the same as setting.
   3. Cleanup:
       - Return all non-default setting on Zone Director

   How it is tested?

"""

import os
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_MultiWlans_Rate_Limit_Integration(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    test_parameters = {'target_station': 'IP address of the target station',
                       'active_ap': 'the AP symbolic name of the active AP. It is the Mesh AP or Root AP',
                       'wlan_config_set': 'list of 32 WLAN configurations will be test',
                       'uplink_rate_limit':'the uplink rate limit value will be applied to test',
                       'downlink_rate_limit': 'the downlink rate limit value will be applied to test'}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()
        self._cfgActiveAP()

    def test(self):
        # Verify Rate Limit option on all wlan
        self._verifyRateLimitIntegration()

        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    def _initTestParameter(self, conf):
        self.conf = {'target_station':'',
                     'active_ap':'',
                     'server_ip':'192.168.0.252',
                     'uplink_rate_limit': '5Mbps',
                     'downlink_rate_limit': '5Mbps',
                     'margin_of_error':0.1,
                     'min_rate':0,
                     'sending_time':30,
                     'wlan_config_set':'set_of_32_open_none_wlans',
                     'tested_wlan_list': [],
                     'test_port':3000}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.linuxPC = self.testbed.components['LinuxServer']
        self.target_station = None
        self.server_ip = self.linuxPC.ip_addr

        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", self.conf['uplink_rate_limit'], re.I)
        up_rate_opt = rate_obj.group(1) + tconfig.get_bw_symbol(rate_obj.group(2))
        rate_obj = re.match(r"([0-9]+)\s*([k|m]bps)", self.conf['downlink_rate_limit'], re.I)
        down_rate_opt = rate_obj.group(1) + tconfig.get_bw_symbol(rate_obj.group(2))
        rate_limit_value = {'uplink_rate_limit': up_rate_opt, 'downlink_rate_limit': down_rate_opt}

        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        for wlan in self.wlan_conf_list:
            wlan.update(rate_limit_value)

        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list]
        self.check_status_timeout = 180
        self.break_time = 2
        self.test_wlan_number = 6
        self.error_margin = self.conf['margin_of_error']
        self.errmsg = ''
        self.passmsg = ''

        # Calculate the allowed rate value base on the input parameters
        self.allowed_uplink_rate = tconfig.calculate_rate_value(self.conf['uplink_rate_limit'], self.error_margin)
        self.allowed_downlink_rate = tconfig.calculate_rate_value(self.conf['downlink_rate_limit'], self.error_margin)

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                           , self.testbed.components['Station']
                                                           , check_status_timeout = self.check_status_timeout
                                                           , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

        # Get mac address of wireless adapter on the target station.
        # This address is used as the restricted mac address in an ACL rule
        sta_wifi_ip_addr = None
        self.sta_wifi_mac_addr = None
        try:
            sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
        except:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)


        self.zd.unblock_clients('')
        # Create an Radius server on Zone Director if there is any WLAN use the MAC authentication
        use_server = False
        for wlan in self.wlan_conf_list:
            if wlan['auth'] == 'mac':
                wlan.update({'auth_svr':self.conf['auth_server_info']['server_name']})
                use_server = True
        if use_server:
            logging.info('Configure the external server on Zone Director')
            lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])

        # Create wlans set for testing
        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')

    def _cfgActiveAP(self):
        if self.conf.has_key('active_ap'):
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

    def _verifyRateLimitIntegration(self):
        error_at_wlan = []
        # Remove all wlan members out of Default group
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', self.wlan_name_list, False)
        last_asigned_wlans = []
        logging.info('Verify on wlans %s' % self.conf['tested_wlan_list'])
        verify_wlan_conf_list = []
        for i in self.conf['tested_wlan_list']:                
            verify_wlan_conf_list.append(self.wlan_conf_list[i])

        # Remove all assigned wlans out of Default group
        if last_asigned_wlans:
            lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', last_asigned_wlans, False)
        # Apply the selected wlans to Default group for testing
        verify_wlan_name_list = [wlan['ssid'] for wlan in verify_wlan_conf_list]
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', verify_wlan_name_list, True)
        last_asigned_wlans = verify_wlan_name_list
        # Remove all wlans on the non active APs
        self._remove_all_wlanOnNonActiveAPs()

        # Verify station association and traffic sending
        val = self._verifyStationAssociationAndTrafficSending(verify_wlan_conf_list)
        error_at_wlan.extend(val)

        if error_at_wlan:
            self.errmsg = 'Rate Limit Option did not work well on wlans %s' % str(error_at_wlan)
        else:
            self.passmsg = 'Rate limit Option worked well on %d wlans' % len(self.wlan_conf_list)

    def _verifyStationAssociationAndTrafficSending(self, wlan_conf_list):
        # Verify for each of wlans
        error_at_wlan = []
        for wlan in wlan_conf_list:
            logging.info('Verify Rate Limiting Option on wlan %s [%s]' % (wlan['ssid'], str(wlan)))
            # Check if target station could access to wlan and ping to target ip
            sta_wifi_ip_addr = self._checkStationAssociationWithWlan(wlan)

            logging.info('Sending uplink traffic from station [%s]' % sta_wifi_ip_addr)
            val = self._verifyStationTraffic(sta_wifi_ip_addr,
                                            self.allowed_uplink_rate, self.conf['min_rate'], True)
            if val:
                logging.info('[Error at wlan "%s"] %s' % (wlan['ssid'], val))
                error_at_wlan.append(wlan['ssid'])
                continue

            logging.info('Sending downlink traffic from station [%s]' % self.server_ip)
            val = self._verifyStationTraffic(self.server_ip,
                                             self.allowed_downlink_rate, self.conf['min_rate'], False)
            if val:
                logging.info('[Error at wlan "%s"] %s' % (wlan['ssid'], val))
                error_at_wlan.append(wlan['ssid'])
                continue

        return error_at_wlan

    def _checkStationAssociationWithWlan(self, wlan_conf):
        tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, self.check_status_timeout, self.break_time)
        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout, self.break_time)
        if not val:
            raise Exception(val2)
        else:
            sta_wifi_ip_addr = val1
            sta_wifi_mac_addr = val2

        # Verify if client is authorized
        # Verify if the client is authorized with the user name is its wifi MAC
        errmsg, client_info = tmethod.verify_zd_client_is_authorized(self.zd, sta_wifi_ip_addr,
                                                                 sta_wifi_mac_addr,
                                                                 self.check_status_timeout)
        if errmsg:
            raise Exception(errmsg)

        # Verify if the station could ping to the server before send traffic
        errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.server_ip)
        if errmsg:
            raise Exception(errmsg)

        return sta_wifi_ip_addr

    def _verifyStationTraffic(self, host, allowed_rate, min_rate = 0, is_uplink = False):
        self._kill_zing()
        if is_uplink:
            # Send uplink traffic from server to target station
            logging.info("Send Zing traffic from a Wireless Station to Linux Server")
            try:
                traffic_result = self.linuxPC.send_zing(host, udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])
            except:
                # Re send traffic if it was not done properly
                traffic_result = self.linuxPC.send_zing(host, udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])
 
        else:
            # Send downlink traffic from server to target station
            logging.info("Send Zing traffic from Linux Server to Wireless Station")
            self.linuxPC.start_zing_server(port = self.conf['test_port'])                             
            try:
                traffic_result = self.target_station.send_zing(**dict(host=host, udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time']))
            except:
                # Re send traffic if it was not done properly
                traffic_result = self.target_station.send_zing(**dict(host=host, udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time']))

        logging.info("The percentile 50%% is %.3f mbps" % float(traffic_result["50.0"]))
        logging.info("The allowed rate limit is %.3f mbps" % allowed_rate)
        if float(traffic_result["50.0"]) > allowed_rate:
            msg = "The measured rate was %.3f mbps" % float(traffic_result["50.0"])
            msg += " which is higher than expected (%.3f mbps)" % allowed_rate
            return msg
        rate_at_50_percentile = float(traffic_result["50.0"])
        if float(traffic_result["50.0"]) <= min_rate:
            msg = 'The measured rate was %.3f mbps' % float(rate_at_50_percentile)
            msg += ' which is lower than expected (%.3f mbps)' % min_rate
            logging.info(msg)
            self.errmsg = msg
            return

        return None

    def _kill_zing(self):
        self.linuxPC.kill_zing()
        time.sleep(3)

