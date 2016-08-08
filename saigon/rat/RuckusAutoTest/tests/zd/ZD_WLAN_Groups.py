# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_WLAN_Groups class test basic Wlan Groups feature on ZD. The ability to create/clone/edit and maximum Wlan Group configuration.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'ap_list': 'list AP use for testing assign APs to wlan groups',
            'target_station':'ip address of target station',
            'wgs_cfg':'dictionary of wlan groups parameters',
            'wlan_cfg': 'dictionary of wlan groups parameters, if not provide, test will use default setting from tmethod8.get_default_wlan_cfg',
            'target_ip': 'IP address to test ping',
            'max_wgs':'Maxium wlan groups created for testing',
            'clone_name':'Clone wlan group name',
            'new_description':'new wlan group description'
   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, pass WebAuth, ping to a destination successfully and
                  information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
       - Create Wlan Groups for the test
   3. Cleanup:
       - Remove all Wlan Groups created
       - Remove all Wlan created

   How it is tested?
   - Modify (Add/Delete/Edit) Wlan Group before run test functions
"""

import os
import re
import logging
import time
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_WLAN_Groups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ap_list': 'list AP use for testing assign APs to wlan groups',
                           'target_station':'ip address of target station',
                           'wgs_cfg':'dictionary of wlan groups parameters',
                           'wlan_cfg': 'dictionary of wlan groups parameters,\
                                    if not provide, test will use default setting from tmethod8.get_default_wlan_cfg',
                           'target_ip': 'IP address to test ping',
                           'max_wgs':'Maxium wlan groups created for testing',
                           'clone_name':'Clone wlan group name',
                           'new_description':'new wlan group description'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._cfgGetTargetStation()
        self._findActiveAP()
        self._cfgWlanForAP()


    def test(self):
        self._testCreateWlanGroup()
        if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'clone_wlan_group':
            self._testCloneWlanGroup()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'edit_wlangroup_description':
            self._testEditWlanGroup()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'edit_wlan_member':
            self._testEditWlanGroupMember()
            if self.errmsg: return ("FAIL", self.errmsg)

        # test wlangroup functionality
        self._cfgAssignAPtoWlanGroup()
        self._testWlanIsUp()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testWlanOnNoneActiveAP()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._configClientToAssocWlan()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._get_clientWifiAddress()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testClientCanReachDestination()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
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
        if not self.conf.has_key('wgs_cfg'):
            self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg()
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wgs_cfg = self.conf['wgs_cfg']
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['wlan_cfg']['ssid'])
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        self.active_ap_mac = ''
        # wlangroup used to test
        self.wgs_name = self.wgs_cfg['name']
        if self.conf['max_wgs'] > 1: self.wgs_name = "%s-1" % self.wgs_name
        self.target_ip = self.conf['target_ip']

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)    

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _findActiveAP(self):
        if self.conf.has_key('ap_list'):
            self.ap_list = []
            self.ap_mac_list = []
            for ap in self.conf['ap_list']:
                active_ap = tconfig.get_testbed_active_ap(self.testbed, ap)
                if not active_ap:
                    raise Exception("AP [%s] not found in testbed." % ap)
                active_ap_mac = active_ap.get_base_mac().lower()
                self.ap_list.append(active_ap)
                self.ap_mac_list.append(active_ap_mac)

        # set active Ap as first AP in the list
        self.active_ap = self.ap_list[0]
        self.active_ap_mac = self.ap_mac_list[0]

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
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
        # make sure wlan_cfg['ssid'] is not belong to default wlanGroups
        # so we can isolate an AP to wlan_cfg['ssid'] -- to make 1Wlan 1AP possible
        lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                           self.wlan_cfg['ssid'])


#
# test()
#
    def _testCreateWlanGroup(self):
        default_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        logging.info("Test create %s Wlan Groups" % self.conf['max_wgs'])
        lib.zd.wgs.create_multi_wlan_groups(self.zd, self.conf['wgs_cfg']['name'], self.conf['wlan_cfg']['ssid'], False,
                                          self.conf['wgs_cfg']['description'], int(self.conf['max_wgs']))

        logging.info("verify total WlanGroup create successful")
        current_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        if (current_tot_wgs - default_tot_wgs != int(self.conf['max_wgs'])):
            self.errmsg = "Total Wlan Groups on ZD not match with Wlan Groups created"

        logging.info("verify WlanGroup name created correctly")
        not_found_list = []
        wgs_list = lib.zd.wgs.get_wlan_groups_list(self.zd)
        for i in range(self.conf['max_wgs']):
            wgs_name = "%s-%d" % (self.conf['wgs_cfg']['name'], i + 1)
            if self.conf['max_wgs'] == 1: wgs_name = self.conf['wgs_cfg']['name']

            logging.info("Verify [wlangroup %s] in WlanGroups created" % wgs_name)
            if wgs_name not in wgs_list:
                not_found_list.append(wgs_name)

        if len(not_found_list):
            self.errmsg = "These wlangroups were not found on Wlan Group table: %s" % not_found_list

        if self.conf['test_feature'] == 'max_wlan_group':
            self.passmsg = "Pass create maximum %s wlan group on Zone Director" % self.conf['max_wgs']

    def _testCloneWlanGroup(self):
        default_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        logging.info("Test clone [WlanGroup %s] from [WlanGroup %s]" % (self.conf['wgs_cfg']['name'], self.conf['clone_name']))
        lib.zd.wgs.clone_wlan_group(self.zd, self.conf['wgs_cfg']['name'], self.conf['clone_name'])

        # verify WlanGroup clone successful
        current_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        if (current_tot_wgs - default_tot_wgs <= 0):
            self.errmsg = "Fail to clone Wlan Group from an existing Wlan Group"

        found = lib.zd.wgs.find_wlan_group(self.zd, self.conf['clone_name'])
        if not found:
            self.errmsg = "[wlangroup %s] is not found on Wlan Group table" % self.conf['clone_name']

        # do some negative test
        self._negativeTestCloneWlanGroup()
        if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'clone_wlan_group':
            self.passmsg = "Pass clone wlan group from an exist wlan group"

    def _negativeTestCloneWlanGroup(self):
        default_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        logging.info("[Negative Test] Test clone [WlanGroup %s] without change wlangroup name" % self.conf['wgs_cfg']['name'])
        lib.zd.wgs.clone_wlan_group(self.zd, self.conf['wgs_cfg']['name'], self.conf['wgs_cfg']['name'])

        # verify WlanGroup clone unsuccessful
        current_tot_wgs = lib.zd.wgs.get_total_wlan_groups(self.zd)
        if (current_tot_wgs - default_tot_wgs > 0):
            self.errmsg = "Zone Director not check dupliate wlangroup when clone"

    def _testEditWlanGroup(self):
        logging.info("Test modify wlan group description")
        lib.zd.wgs.edit_wlan_group(self.zd, self.conf['wgs_cfg']['name'], self.wgs_name, self.conf['new_description'])

        # verify WlanGroup description change successful
        wgs_cfg = lib.zd.wgs.get_wlan_group_of_member(self.zd, self.conf['wgs_cfg']['name'], self.conf['wlan_cfg']['ssid'])
        logging.info("New description of [wlangroup %s] is '%s'" % (self.conf['wgs_cfg']['name'], wgs_cfg['description']))
        if self.conf['new_description'] != wgs_cfg['description']:
            self.errmsg = "Fail to change Wlan Group description of [wlangroup %s]" % self.conf['wgs_cfg']['name']

        if self.conf['test_feature'] == 'edit_wlangroup_description':
            self.passmsg = "Pass edit wlan group description"

    def _testEditWlanGroupMember(self):
        logging.info("Test create/delete wlan of wlan group")

        # verify wlan group member can be remove
        lib.zd.wgs.cfg_wlan_member(self.zd, self.conf['wgs_cfg']['name'], self.conf['wlan_cfg']['ssid'], False)
        wgs_cfg = lib.zd.wgs.get_wlan_group_of_member(self.zd, self.conf['wgs_cfg']['name'], self.conf['wlan_cfg']['ssid'])

        if wgs_cfg['wlan_member']['checked']:
            self.errmsg = "Fail to remove [wlan %s] from [wlangroup %s]" % (self.conf['wlan_cfg']['ssid'], self.conf['wgs_cfg']['name'])

        lib.zd.wgs.cfg_wlan_member(self.zd, self.conf['wgs_cfg']['name'], self.conf['wlan_cfg']['ssid'], True)
        wgs_cfg = lib.zd.wgs.get_wlan_group_of_member(self.zd, self.conf['wgs_cfg']['name'], self.conf['wlan_cfg']['ssid'])

        if not wgs_cfg['wlan_member']['checked']:
            self.errmsg = "Fail to add [wlan %s] to [wlangroup %s]" % (self.conf['wlan_cfg']['ssid'], self.conf['wgs_cfg']['name'])

        if self.conf['test_feature'] == 'edit_wlan_member':
            self.passmsg = "Pass add/delete wlan member of wlan group"

    def _cfgAssignAPtoWlanGroup(self):
        support_radio = lib.zd.ap.get_supported_radio(self.zd, self.active_ap_mac)
        for radio in support_radio:
            lib.zd.ap.assign_to_wlan_group(self.zd, self.active_ap_mac , radio, self.wgs_name)
        # wait for ZD put configuration to AP
        time.sleep(self.conf['check_wlan_timeout'])



    # client is connected if not self.errmsg
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

    def _testClientCanReachDestination(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                          self.target_ip,
                                                          ping_timeout_ms = self.conf['ping_timeout'] * 1000)

    def _testWlanIsUp(self):
        logging.info("test [wlan %s] is up on Active AP[%s]" % (self.conf['wlan_cfg']['ssid'], self.active_ap_mac))
        for (wlan_id, wlan) in self.active_ap.get_wlan_info_dict().iteritems():
            if self.active_ap.get_ssid(wlan['wlanID']) == self.conf['wlan_cfg']['ssid'] and wlan['status'] == 'up':
                return

        self.errmsg = "[wlan %s] is not up on Active AP[%s]" % (self.wlan_cfg['ssid'], self.active_ap_mac)

    def _testWlanOnNoneActiveAP(self):
        logging.info("test wlan on AP not belong to [wlangroup %s]" % self.wgs_name)
        for ap in self.ap_list:
            if ap == self.active_ap:
                continue

            for (wlan_id, wlan) in ap.get_wlan_info_dict().iteritems():
                if ap.get_ssid(wlan['wlanID']) == self.wlan_cfg['ssid']:
                    self.errmsg = "ZD send wlan configure to AP not assigned to [wlangroup %s]" % self.wgs_name

#
# cleanup()
#


