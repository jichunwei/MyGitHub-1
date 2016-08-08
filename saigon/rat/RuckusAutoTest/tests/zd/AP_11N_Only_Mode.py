# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'wgs_cfg':'dictionary of wlan groups parameters',
            'wlan_cfg': 'dictionary of wlan groups parameters, if not provide, test will use default setting from tmethod8.get_default_wlan_cfg',

   Result type: PASS/FAIL
   Results: PASS: if 11N-Only Mode only allow 11n or 11a/n client associate to AP
            FAIL: if 11N-Only Mode allow 11b/g/n client associate to AP

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
        - Configure a WLAN and Wlan Group on AP
        - Assign Wlan Group to AP under test.
        - Enable/Disable 11N-Only Mode for AP
        - Associate client to AP and verify associate depend on 11N-Mode and client radio following these criteria:
          + success if client radio mode is 11n or 11a/n and 11N-Only Mode is enabled
          + not success if client radio mode is 11b/g/n and 11N-Only Mode is eanbled
          + success if 11N-Only mode disable

   3. Cleanup:
       - Remove all Wlan Groups created
       - Remove all Wlan created
       - Restore 11N-Only Mode on Zone Director
"""

import os
import re
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class AP_11N_Only_Mode(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station'    : 'ip address of target station',
                           'wlan_group_cfg'    : 'dictionary of wlan groups parameters',
                           'wlan_cfg'          : 'dictionary of wlan groups parameters,\
                                                 if not provide, test will use default setting from tmethod8.get_default_wlan_cfg'
                           }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._cfgGetTargetStation()
        self._cfgGetActiveAP()
        self._cfgSave11nModeConfiguration()

    def test(self):
        self._cfgCreateWlanOnZD()
        self._cfgCreateWlanGroup()
        self._cfgAssignAPtoWlanGroup()
        self._cfg_ap11nOnlyMode()
        self._testClientToAssocWlan()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        lib.zd.ap.assign_to_default_wlan_group(self.zd, self.active_ap_mac)
        lib.zd.wgs.remove_wlan_groups(self.zd)
        self.zd.remove_all_cfg()
        self._remove11nOnlyMode()

#
# config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(check_status_timeout = 30,
                          check_wlan_timeout = 30,
                          active_ap = ''
                          )
        self.conf.update(conf)

        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()
        if not self.conf.has_key('wlan_group_cfg'):
            self.conf['wlan_group_cfg'] = tmethod8.get_default_wlan_groups_cfg()

        self.wlan_cfg = self.conf['wlan_cfg']
        self.wlan_group_cfg = self.conf['wlan_group_cfg']
        default_ssid = self.conf['wlan_cfg']['ssid']
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['wlan_cfg']['ssid'])

        # update ssid in wlan group
        self.wlan_group_cfg['wlan_member'][self.conf['wlan_cfg']['ssid']] = self.wlan_group_cfg['wlan_member'][default_ssid].copy()
        del self.wlan_group_cfg['wlan_member'][default_ssid]

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        self.target_station = ''
        self.ap_11n_mode = ''

    def _cfgSave11nModeConfiguration(self):
        self.ap_11n_mode = lib.zd.ap.get_11n_mode_only_info(self.zd)

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        logging.info("Remove all Wlan Groups on the Zone Director.")
        lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        logging.info("Remove all WLAN on the Zone Director.")
        self.zd.remove_all_cfg()

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in the test bed" % self.conf['active_ap'])

            self.active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['active_ap'])

    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        # make sure wlan_cfg['ssid'] is not belong to default wlanGroups
        # so we can isolate an AP to wlan_cfg['ssid'] -- to make 1Wlan 1AP possible
        lib.zd.wgs.uncheck_default_wlan_member(self.zd, self.wlan_cfg['ssid'])

#
# test()
#
    def _cfgCreateWlanGroup(self):
        lib.zd.wgs.create_new_wlan_group(self.zd, self.wlan_group_cfg)

    def _cfgAssignAPtoWlanGroup(self):
        support_radio = lib.zd.ap.get_supported_radio(self.zd, self.active_ap_mac)
        for radio in support_radio:
            if radio == self.conf['radio']:
                lib.zd.ap.assign_to_wlan_group(self.zd, self.active_ap_mac , radio, self.wlan_group_cfg['name'])
        # wait for ZD put configuration to AP
        tmethod8.pause_test_for(10, "Wait for ZD put Wlan configuration to AP")

    def _cfg_ap11nOnlyMode(self):
        if self.conf['mode_11n']:
            logging.info("Enable 11N-Only Mode on Zone Director")
            for radio in ["2.4G", "5G"]: lib.zd.ap.set_11n_mode_only_info(self.zd, radio, "N/AC-only")
        else:
            logging.info("Disable 11N-Only Mode on Zone Director")
            for radio in ["2.4G", "5G"]: lib.zd.ap.set_11n_mode_only_info(self.zd, radio, "Auto")

    def _testClientToAssocWlan(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station,
                                                    self.wlan_cfg,
                                                    self.conf['check_status_timeout'])
        if self.conf['mode_11n']:
            if self.conf['sta_support_radio'] in ['11a/b/g'] and self.errmsg:
                self.errmsg = ''
                self.passmsg = '11N-only mode work properly'
                return
            if self.conf['sta_support_radio'] in ['11a/b/g'] and not self.errmsg:
                if self.wlan_cfg['encryption'] not in ["WEP-64", "WEP-128", "TKIP"]: 
                    self.errmsg = '11N-only mode allow 11b/g/n client connect to AP'
                    return
            if self.errmsg: self.passmsg = '11N-only mode work properly'
        else:
            if self.errmsg: self.errmsg = '11N-only mode was disable but client can\'t associte to AP'
            else: self.passmsg = '11N-only mode work properly'

# cleanup()
#
    def _remove11nOnlyMode(self):
        if self.ap_11n_mode:
            for radio in self.ap_11n_mode.keys():
                lib.zd.ap.set_11n_mode_only_info(self.zd, radio, self.ap_11n_mode[radio])
