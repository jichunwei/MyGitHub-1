# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script use to verify the Zero IT option that Zone Director supporting.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station': IP address of the target station
                    'active_ap': ap symbolic name of the active AP
                    'wlan_config_set': list of 32 WLAN configurations will be test. Default is list of 32 WLANs with "Open - None" encryption.
                    'do_tunnel': True/False ?enable or disable the tunnel mode on Zone Director.
                    'vlan_id': The vlan id will be applied to the WLANs

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Create 32 WLANs on the Zone Director base on the 'wlan_config_set'parameter.
   2. Test:
        - Configure all WLANs enable the Zero IT.
        - Use target stations down load the zero-it configuration file, verify:
            a.    The configuration could be installed on the station successfully.
            b.    32 WLAN profiles are added to station correctly.
            c.    Target station can connect to all WLANs without configure.
            d.    Target station can get correct IP address appropriate with case the tunnel mode or VLAN is enabled.
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

class ZD_MultiWlans_ZeroIT_Integration(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()
        self._cfgActiveAP()

    def test(self):
        # Verify if ZeroIT option work
        self._verifyZeroITFunctionallity()
        # Verify station could access to all wlans
        self._verifyStationCouldAccessAllWlans()

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
                     'wlan_config_set':'set_of_32_open_none_wlans',
                     'do_tunnel': None,
                     'vlan_id': None,
                     'expected_subnet':'',
                     'ip':'',
                     'tested_wlan_list': []
                 }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.target_station = None
        self.active_ap = None

        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        test_conf = {'use_radius': None, 'do_zero_it': True,
                     'do_tunnel':self.conf['do_tunnel'],
                     'vlan_id':self.conf['vlan_id']}
        for wlan in self.wlan_conf_list:
            wlan.update(test_conf)
        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list]

        self.check_status_timeout = 180
        self.break_time = 2
        self.test_wlan_number = 6
        self.errmsg = ''
        self.passmsg = ''
        self.username = 'testuser'
        self.password = 'testpassword'

        self.zd_ip_addr = self.zd.ip_addr
#        self.sta_ip_addr = ".".join(self.zd_ip_addr.split('.')[:-1]) + ".50"
        self.sta_ip_addr = self.get_station_download_ip_addr()
        self.sta_net_mask = utils.get_subnet_mask(self.zd_ip_addr, False)
        self.activate_url = self.zd.get_zero_it_activate_url()

        tmp_list = self.conf['ip'].split("/")
        self.test_ip_addr = tmp_list[0]
        if len(tmp_list) == 2:
            self.expected_subnet_mask = tmp_list[1]
        else:
            self.expected_subnet_mask = ""

        l = self.conf['expected_subnet'].split("/")
        self.expected_subnet = l[0]
        if len(l) == 2:
            self.expected_subnet_mask = l[1]
        else:
            self.expected_subnet_mask = ""

    def _cfgTargetStation(self):
        if self.conf['target_station']:
            self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                           , self.testbed.components['Station']
                                                           , check_status_timeout = self.check_status_timeout
                                                           , remove_all_wlan = True)
            if not self.target_station:
                raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        self.zd.unblock_clients('')

        # Create wlans set for testing
#        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)
        lib.zdcli.set_wlan.create_multi_wlans(self.zdcli, self.wlan_conf_list)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
        
        # Create user for authentication
        self.zd.create_user(self.username, self.password)

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

    def _verifyZeroITFunctionallity(self):
        logging.info("Use zero-it tool to configure %d WLAN profiles on the target station %s"
                     % (len(self.wlan_name_list), self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                 self.sta_net_mask, '', False,
                                                 self.activate_url, self.username, self.password, '')

        time.sleep(4)
        logging.info("Make sure that wlan list on the ZD has the same length as wlan profile list on the station.")
        sta_wlan_list = self.target_station.get_wlan_profile_list()

        diff_wlan_list = [wlan for wlan in self.wlan_name_list if wlan not in sta_wlan_list]
        if diff_wlan_list:
            msg = 'There are %d ZeroIT enabled wlans %s are not configured to station %s'
            self.errmsg = msg % (len(diff_wlan_list), str(diff_wlan_list), self.target_station.get_ip_addr())
            return

    def _verifyStationCouldAccessAllWlans(self):
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
            # Verify station association
            val = self._verifyStationAssociation(verify_wlan_name_list)
            error_at_wlan.extend(val)

        if error_at_wlan:
            self.errmsg = 'The ZeroIT option did not work well on wlans % s' % str(error_at_wlan)
            return

    def _verifyStationAssociation(self, wlan_name_list):
        error_at_wlan = []
        for wlan in wlan_name_list:
            # Disconnect the station from the currently WLAN connection
            self.target_station.disconnect_from_wlan()
            logging.info('Verify on wlan %s' % wlan)
            self.target_station.connect_to_wlan(wlan)
            errmsg = tmethod.check_station_is_connected_to_wlan(self.target_station, self.check_status_timeout, self.break_time)
            if errmsg:
                logging.info(errmsg)
                error_at_wlan.append(wlan)
                continue

            val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout, self.break_time)
            if not val:
                raise Exception(val2)
            sta_wifi_ip_addr = val1
            sta_wifi_mac_addr = val2
            # Verify if vlan then client and target server should be same subnet
            if self.conf['vlan_id']:
                errmsg = self._verifyClientAndDestAtSameSubnet(sta_wifi_ip_addr)
                if errmsg:
                    logging.info(errmsg)
                    error_at_wlan.append(wlan)
                    continue
            # Verify if tunnel mode enabled the station mac address should be in tunnel mode
            if self.conf['do_tunnel']:
                errmsg = self._verifyStationMacInTunnelMode(sta_wifi_mac_addr)
                if errmsg:
                    logging.info(errmsg)
                    error_at_wlan.append(wlan)
                    continue

        return error_at_wlan

    def _verifyClientAndDestAtSameSubnet(self, sta_wifi_ip_addr):
        # Check if the wireless IP address of the station belongs to the subnet of the parameter 'ip'.
        errmsg = ""
        if self.expected_subnet:
            sta_wifi_subnet = utils.get_network_address(sta_wifi_ip_addr, self.expected_subnet_mask)
            if sta_wifi_subnet != self.expected_subnet:
                errmsg = "The wireless IP address '%s' of the target station was not as expected '%s'" % \
                       (sta_wifi_ip_addr, self.expected_subnet)
        elif self.conf.has_key('vlan_id'):
            sta_wifi_subnet = utils.get_network_address(sta_wifi_ip_addr, self.expected_subnet_mask)
            expected_subnet = utils.get_network_address(self.test_ip_addr, self.expected_subnet_mask)
            if sta_wifi_subnet != expected_subnet:
                errmsg = "The wireless IP address '%s' of target station %s has different subnet with '%s'" % \
                       (sta_wifi_ip_addr, self.target_station.get_ip_addr(), self.test_ip_addr)
        return errmsg

    def _verifyStationMacInTunnelMode(self, sta_wifi_mac_addr):
        if self.active_ap:
            ap_mac = self.active_ap.get_base_mac().lower()
        else:
            ap_mac = self.client_info_on_zd["apmac"].lower()
        sta_mac = sta_wifi_mac_addr.lower()

        try:
            errmsg = self.testbed.verify_station_mac_in_tunnel_mode(ap_mac, sta_mac, self.conf['do_tunnel'])
        except Exception, e:
            errmsg = e.message
        return errmsg

    def get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"
