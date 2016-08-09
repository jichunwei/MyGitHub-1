# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""

import os
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Data_Plane_Test(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgTargetStation()

    def test(self):
        self._verifyExistingWLANs()

        self._verifyTheStationConnection()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'dest_ip': '192.168.0.252',
                     'check_status_timeout': 360,
                     'ping_timeout': 180,
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.conf['check_status_timeout']
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _verifyTheStationConnection(self):
        # Verify if station could access to network and do ping to the server
        for wlan_cfg in self.carrierbag['existing_wlans_cfg']:
            self._verifyStaConnectToWLAN(wlan_cfg)
            if self.errmsg: return
            
            self._verifyPingTraffic()
            if self.errmsg: return


        self.target_station.remove_all_wlan()
        time.sleep(5)
        passmsg = 'Station connected to WLANs %s and ping to server %s successfully'
        self.passmsg = passmsg % ([wlan['ssid'] for wlan in self.carrierbag['existing_wlans_cfg']], self.conf['dest_ip'])

    def _verifyStaConnectToWLAN(self, wlan_cfg):
        # Try to connect the station to the network
        self.target_station.remove_all_wlan()
        time.sleep(10)
        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_cfg, self.conf['check_status_timeout'])
        if errmsg:
            self.errmsg = '[Connect failed]: %s' + errmsg
            logging.info(self.errmsg)
            return
            
        time.sleep(10)
        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not val:
            raise Exception(val2)

        logging.info('Station connected to WLAN[%s] successfully' % wlan_cfg['ssid'])

    def _verifyPingTraffic(self):
        # Try to ping to the server
        errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['dest_ip'],
                                                     ping_timeout_ms = self.conf['ping_timeout'] * 1000)
        if errmsg:
            logging.info(errmsg)
            self.errmsg = errmsg
            return

        logging.info('The station ping to %s successfully' % self.conf['dest_ip'])

    def _verifyExistingWLANs(self):
        existing_wlan = self.zd.get_wlan_list()
        expected_wlan = [wlan_cfg['ssid'] for wlan_cfg in self.carrierbag['existing_wlans_cfg']]

        if sorted(existing_wlan) != sorted(expected_wlan):
            msg = 'The existing WLANs are %s instead of %s' % (existing_wlan, expected_wlan)
            logging.debug(msg)
            raise Exception(msg)
