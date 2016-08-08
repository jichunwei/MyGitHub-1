# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ATT_DeviceInfo class verify infomation of ap.

   Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
   1. Build under test is loaded on the AP and Zone Director.

   Required components: AP

   Test parameters: ip_addr - ip address of ap that we want to verify info

   Result type: PASS/FAIL

   Results: PASS: Accepts all valid values, denies all the invalid values with correct alert messages.
            FAIL: Accepts at least one invalid value or denies at least one valid value.

   Messages:
       - if the result is PASS, no message is shown.
       - if the result is FAIL, an error message will be shown.


   Testing procedure:
       Config:
           1.   Get config
       Test
           1.    Get active station and put into carrierbag
           2.    Get active ap and put into carrierbag
       Cleanup:
           1.   Don't need to do anything to clean up.

   How it was tested:
       1. Enter a valid name to this list of invalid names.
       2. Enter an invalid name to the list of valid names.
"""

import os
import time
import logging
from pprint import pprint

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.ap import lib_ATTDataCollection as DC
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_SetUpATTEnvironment(Test):

    def config(self, conf):
        # Testing parameters
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf

    def test(self):
        self._getStations(self.conf)

        self._getActiveAP(self.conf)
        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _getStations(self, conf):
        logging.info('Start get active window stations')
        # Find exactly stations
        station_list = self.testbed.components['Station']

        # get list of station
        list_station = []
        for active_ad in conf['active_ap']['active_ad']:
            for station in active_ad['local_station']:
                local_station = tconfig.getStation(station['ip_addr'], station_list)
                if local_station:
                    list_station.append(local_station)
        self.local_stations = list_station
        self.carrierbag['list_stations'] = self.local_stations
        self.passmsg += "Get %s stations for testing ATT\n" % len(self.local_stations)
        logging.info('Get active window stations successful')


    def _getActiveAP(self, conf):
        logging.info('Start get active aps')
        ip_addr = conf['active_ap']['ip_addr']
        list_ap = self.testbed.components['AP']
        for ap in list_ap:
            if ip_addr == ap.get_ip_addr():
                self.active_ap = ap
                self.passmsg += "Get AP (%s) for testing ATT" % self.active_ap.get_ip_addr()
                logging.info('Get active aps successful')
                self.carrierbag['active_ap'] = self.active_ap
                return

