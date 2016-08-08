"""
Description: cbZD_AssocTest is a combo test that use to configure client to associate to a wlan or a list of wlan and send traffic (ping test)

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
    - 'target_ip': destination IP address that client will send traffic to
    - 'target_station': IP address of wireles station
    - 'target_wlan_list': a list of wlan that client will associte and send traffic
   Result type: PASS/FAIL
   Results: PASS: if client can associate to all wlan and send traffic succesful
            FAIL: if client can't associate to wlan or can't send traffic to target ip address


   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from copy import deepcopy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme


class cbZD_AssocTest(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                          }

    def config(self, conf):
        self.conf = dict(check_status_timeout = 90,
                         check_wlan_timeout = 3,
                         ping_timeout = 60,
                         pause = 2.0)

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = ""
        self.zd = self.testbed.components['ZoneDirector']
        self.conf.update(self.carrierbag)
        self.target_wlan_list = self.conf['target_wlan_list']
        for target_wlan in self.target_wlan_list:
            if not self.conf.has_key(target_wlan):
                raise Exception("There is no wlan_cfg on Carrierbag for Wlan[%s] to test associate and ping" % target_wlan)

        self.target_ip = self.conf['target_ip']
        self.target_station = None

    def test(self):
        self._cfgGetTargetStation()

        for target_wlan in self.target_wlan_list:
            self.conf['wlan_cfg'] = deepcopy(self.conf[target_wlan])
            self._cfgRemoveWlanFromStation()
            self._cfgAssociateStationToWlan()
            self._testClientCanReachDestination()

            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
        return self.returnResult("PASS", "Client can associate and ping to target station successful")

    def cleanup(self):
        pass

    def _cfgGetTargetStation(self):
        logging.info("Find the target station on the test bed")
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                                       self.testbed.components['Station'],
                                                       check_status_timeout = self.conf['check_status_timeout'],
                                                       remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgRemoveWlanFromStation(self):
        if self.target_station:
            logging.info("Remove all WLANs from the station")
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])

    def _cfgAssociateStationToWlan(self):
        tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], self.conf['check_status_timeout'])

    def _testClientCanReachDestination(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                           self.target_ip,
                                                           ping_timeout_ms = self.conf['ping_timeout'] * 1000)

