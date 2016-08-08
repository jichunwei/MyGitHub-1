# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_WLAN_Groups class test basic Wlan Groups feature on ZD. The ability to create/clone/edit and maximum Wlan Group configuration.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
        'client_roam'    : 'True/False: Test client roaming'
        'map_roam'       : 'True/False: Test MAP roaming'
        'root_ap_01'     : 'Root AP symbolic name on testbed. Should be the same model or running same radio mode'
        'root_ap_02'     : 'Root AP symbolic name on testbed.Should be the same model or running same radio mode'
        'mesh_ap'        : 'Root AP symbolic name on testbed. Should be the same model or running same radio mode'
        'target_station' : 'ip address of target station'
        'target_ip'      : 'IP address to test ping',
        'wgs_cfg_list'   : 'dictionary of wlan groups parameters',
        'wlan_cfg'       : 'dictionary of wlan groups parameters'}

   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, pass WebAuth, ping to a destination successfully and
                  information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
   - Remove All ZD Wlan Groups and Wlan configuration
   - Create Wlan and Wlan Groups with VLAN, WlanGroup Vlan Override and Tunnel Mode Provide in test params

   2. Test:
   - Assign Wlan Groups configuration to APs under test
   - Test Wlan configuration deployed to APs correctly.
   - Configure wireless station to associate wlan of wlangroup.
   - Verify wireless station can ping to target_ip without any problem.

   3. Cleanup:
   - Remove All ZD Wlan Groups and Wlan configuration

   How it is tested?
   -
"""

import os
import re
import logging
import time
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from pprint import pformat, pprint

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_WLAN_Groups_Integration(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
        'client_roam': 'True/False: Test client roaming',
        'map_roam': 'True/False: Test MAP roaming',
        'root_ap_01': 'Root AP symbolic name on testbed. Should be the same model or running same radio mode',
        'root_ap_02': 'Root AP symbolic name on testbed.Should be the same model or running same radio mode',
        'mesh_ap': 'Root AP symbolic name on testbed. Should be the same model or running same radio mode',
        'target_station': 'ip address of target station',
        'target_ip': 'IP address to test ping',
        'wgs_cfg_list': 'dictionary of wlan groups parameters',
        'wlan_cfg': 'dictionary of wlan groups parameters'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        if self.conf['map_roam']:
            self._cfgFormMesh()
        self._cfgGetTargetStation()
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._cfgWlanForAP()

    def test(self):
        self._testCreateWlanGroup()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgAssignAPtoWlanGroup()
        self._testWlanIsUp()
        if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['map_roam']:
            self._testMapRoam()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['client_roam']:
            self._testClientRoam()
            if self.errmsg: return ("FAIL", self.errmsg)
        else:
            self._configClientToAssocWlan()
            if self.errmsg: return ("FAIL", self.errmsg)

            self._get_clientWifiAddress()
            if self.errmsg: return ("FAIL", self.errmsg)

            self._testClientCanReachDestination()
            if self.errmsg: return ("FAIL", self.errmsg)

        self._testVlanOverride()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testTunnelMode()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        if self.conf['map_roam']:
            self._restoreMAPCfg()

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

#
# config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3)
        self.conf.update(conf)

        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()

        if not self.conf.has_key('wgs_cfg_list'):
            self.conf['wgs_cfg_list'] = []
            self.conf['wgs_cfg_list'].append(tmethod8.get_default_wlan_groups_cfg())

        self.wlan_cfg = self.conf['wlan_cfg']
        self.wgs_cfg_list = self.conf['wgs_cfg_list']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        self.current_map_cfg = None
        self.target_ip = self.conf['target_ip']
        self.expected_subnet = self.conf['expected_subnet'].split("/")[0]
        self._convertSymAPtoMAC()

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgFormMesh(self):
        logging.info("Forming Mesh testbed for MAP Roam testing")
        self.testbed.form_mesh([self.conf['root_ap_01']], [(self.conf['mesh_ap'], [self.conf['root_ap_01']])])

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        
       
    def _convertSymAPtoMAC(self):
        self.conf['root_ap_01'] = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['root_ap_01'])
        self.conf['root_ap_02'] = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['root_ap_02'])
        self.conf['mesh_ap'] = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['mesh_ap'])

        self.root_ap_01 = self.testbed.mac_to_ap[self.conf['root_ap_01']]
        self.root_ap_02 = self.testbed.mac_to_ap[self.conf['root_ap_02']]
        self.mesh_ap = self.testbed.mac_to_ap[self.conf['mesh_ap']]

    def _cfgWlanForAP(self):
        logging.info("Create a default Wlan with Auth[%s] and Encryption[%s]" %
                     (self.wlan_cfg['auth'], self.wlan_cfg['encryption']))
        if self.wlan_cfg['auth'] == "EAP":
            logging.info("Create an authentication server on the ZoneDirector")
            if self.wlan_cfg['use_radius']:
                self.zd.create_radius_server(self.wlan_cfg['ras_addr'],
                                          self.wlan_cfg['ras_port'],
                                          self.wlan_cfg['ras_secret'])
            else:
                logging.info("Create a user on the ZoneDirector")
                self.zd.create_user(self.wlan_cfg['username'],
                                    self.wlan_cfg['password'])

        self.zd.cfg_wlan(self.wlan_cfg)
        # make sure wlan_cfg['ssid'] is not belong to default wlanGroups
        # so we can isolate an AP to wlan_cfg['ssid'] -- to make 1Wlan 1AP possible
        lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                           self.wlan_cfg['ssid'])

    def _configClientToAssocWlan(self):
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

#
# test()
#
    def _testCreateWlanGroup(self):
        default_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        for wgs_cfg in self.wgs_cfg_list:
            lib.zd.wgs.create_new_wlan_group(self.zd, wgs_cfg)
        current_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)

        if current_tot_wgs == default_tot_wgs:
            self.errmsg = "Fail to create new WlanGroup"

    def _cfgAssignAPtoWlanGroup(self):
        for wgs in self.wgs_cfg_list:
            for ap in wgs['ap_list']:
                ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap)
                support_radio = lib.zd.ap.get_supported_radio(self.zd, ap_mac)
                for radio in support_radio:
                    lib.zd.ap.assign_to_wlan_group(self.zd, ap_mac, radio, wgs['name'])

        # wait for ZD put configuration to AP
        time.sleep(self.conf['check_wlan_timeout'])

    def _testWlanIsUp(self):
        for wgs in self.wgs_cfg_list:
            for ap_name in wgs['ap_list']:
                ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap_name)
                ap = self.testbed.mac_to_ap[ap_mac]
                logging.info("test [wlan %s] is up on Active AP[%s]" % (self.conf['wlan_cfg']['ssid'], ap_mac))

                for (wlan_id, wlan) in ap.get_wlan_info_dict().iteritems():
                    if ap.get_ssid(wlan['wlanID']) == self.conf['wlan_cfg']['ssid'] and wlan['status'] == 'up':
                        return

                self.errmsg = "[wlan %s] is not up on Active AP[%s]" % (self.wlan_cfg['ssid'], ap_mac)

    def _testClientCanReachDestination(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                           self.target_ip,
                                                           ping_timeout_ms = self.conf['ping_timeout'] * 1000)

    def _testClientToAssocBSSID(self, bssid):
        self.errmsg = tmethod8.assoc_station_with_bssid(self.target_station, self.wlan_cfg,
                                                      bssid, self.conf['check_status_timeout'])

    def _testClientRoam(self):
        # associate client to RAP
        self._testClientToAssocBSSID(self._getAPBSSID(self.root_ap_01))
        if self.errmsg: return
        self._get_clientWifiAddress()
        if self.errmsg: return
        self._testClientCanReachDestination()
        if self.errmsg: return

        # associate client to MAP
        self._testClientToAssocBSSID(self._getAPBSSID(self.mesh_ap))
        if self.errmsg: return
        self._get_clientWifiAddress()
        if self.errmsg: return
        self._testClientCanReachDestination()
        if self.errmsg: return
        vlan_override_setting = {True: 'Enable Vlan Override', False: 'Disable Vlan Override'}[self.conf['vlan_override']]
        tunnel_setting = {True: 'With Tunnel', False: 'Without Tunnel'}[self.conf['tunnel']]
        if len(self.wgs_cfg_list) > 2:
            self.passmsg = "Different Wlan Group Client Roam with %s, %s work properly" % (vlan_override_setting, tunnel_setting)
        else:
            self.passmsg = "Client Roam with %s, %s work properly" % (vlan_override_setting, tunnel_setting)

    def _getAPBSSID(self, ap):
        for (wlan_id, wlan) in ap.get_wlan_info_dict().iteritems():
            if ap.get_ssid(wlan['wlanID']) == self.wlan_cfg['ssid']:
                return wlan['bssid']

        return ""


    def _testMapRoam(self):
        self.current_map_cfg = self.zd.get_ap_cfg(self.conf['mesh_ap'])
        self.new_map_cfg = self.current_map_cfg.copy()
        self.new_map_cfg['mesh_uplink_aps'] = []
        logging.info('Update uplink selection of MAP for roaming to new RAP')
        self.new_map_cfg['mesh_uplink_aps'].append(self.conf['root_ap_02'])
        self.zd.set_ap_cfg(self.new_map_cfg)
        # waiting for MAP updated configuration and roam to new RAP
        time.sleep(self.conf['check_status_timeout'])
        map_info = self.zd.get_all_ap_info(self.conf['mesh_ap'])
        vlan_override_setting = {True: 'Enable Vlan Override', False: 'Disable Vlan Override'}[self.conf['vlan_override']]
        tunnel_setting = {True: 'With Tunnel', False: 'Without Tunnel'}[self.conf['tunnel']]
        logging.debug("MAP status after change uplink selection \n%s" % pformat(map_info))
        if 'connected' in map_info['status'].lower():
            if len(self.wgs_cfg_list) > 2:
                self.passmsg = "Pass Different WlanGroup MAP Roam with %s, %s work properly" % (vlan_override_setting, tunnel_setting)
            else:
                self.passmsg = "Pass MAP Roam with %s, %s work properly" % (vlan_override_setting, tunnel_setting)
        else:
            self.errmsg = "MAP unable to reconnect after update uplink selection"

    def _testVlanOverride(self):
        logging.info("Make sure that the wireless station has got an IP address assigned to the VLAN")
        sta_wifi_subnet = utils.get_network_address(self.wifi['ip_addr'], self.expected_subnet)
        if sta_wifi_subnet != self.expected_subnet:
            errmsg = "The wireless IP address '%s' of the target station was not as expected subnet '%s'"
            errmsg = errmsg % (self.wifi['ip_addr'], self.expected_subnet)

    def _testTunnelMode(self):
        if self.wlan_cfg['do_tunnel']:
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(self.conf['root_ap_01'], self.wifi['mac_addr'], True)
            if not self.errmsg: return
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(self.conf['mesh_ap'], self.wifi['mac_addr'], True)
            if not self.errmsg: return
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(self.conf['root_ap_02'], self.wifi['mac_addr'], True)
#
# cleanup()
#
    def _moveAPtoDefaultWlanGroups(self):
        for wgs in self.wgs_cfg_list:
            for ap in wgs['ap_list']:
                ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap)
                support_radio = lib.zd.ap.get_supported_radio(self.zd, ap_mac)
                for radio in support_radio:
                    lib.zd.ap.assign_to_wlan_group(self.zd, ap_mac, radio, 'Default')

    def _restoreMAPCfg(self):
        if self.conf['map_roam']:
            self.testbed.form_mesh([self.conf['mesh_ap']], [])
        if self.current_map_cfg:
            self.zd.set_ap_cfg(self.current_map_cfg)

