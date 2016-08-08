# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: AssocPing Test class tests the ability of a station to associate with an AP with a given security configuration.
The ability to associate is confirmed via a ping test.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP'
   Test parameters: 'timeout': 'Maximum length of time in seconds to wait for association and ping to complete',
                    'ip': 'IP address to ping',
                    'target_station': 'ip address of target station',
                    'wlan_cfg': 'dictionary of association parameters'
   Result type: PASS/FAIL
   Results: PASS: target station can associate and ping successful to destination ip within timeout
            FAIL: target station can't associate or ping to destination

   Messages:
       - if the result is pass, it shows the amount of time after finish setup profile for wireless station
   until wireless station receive ping reply.
       - if the result is fail, it shows 'time out exceed'

   Test procedure:
   1. Config:
       - Remove All wlan on DUT (e.g ZD, AP, Ruckus Station)
       - Configure 1 wlan with SSID and security setting in test parameters
       - Telnet to remote wireless STA and remove all wireless profile
       - Verify that wireless station is completed disconnect
       - Configure wireless profile for remote wireless STA

   2. Test engine send command to ask remote wireless STA send ping traffic, fail if can't ping to destination ip
   3. Cleanup:
       - Remove all wlan config on AP and ZD
       - Remove wireless profile on remote wireless STA
       - Verify that wireless station is completed disconnect after remove wireless profile.

   How is it tested:
   1. While test running, manually login to AP and change the SSID. It will verify that test script can covert associate fail
   2. While test running, manually login to AP and modify security setting. It will verify that test script can covert associate fail
   3. Change IP address on the destination PC to verify "timeout exceed"
   4. Capture packets on the air with encryption Auth(Open) Encryption(None) compare time length associate success until reply packet with
   result message on this test case.

"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class AssocPing(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'timeout': 'Maximum length of time in seconds to wait for association and ping to complete',
                           'ip': 'IP address to ping',
                           'target_station': 'ip address of target station',
                           'active_ap': 'mac address of target ap',
                           'wlan_cfg': 'dictionary of association parameters' }
    def config(self, conf):
        # Testing parameters
        self.timeout = int(conf['timeout'])
        self.ip_addr = conf['ip']

        # Find target component object
        found = False
        for comp in self.testbed.components['Station']:
            if isinstance(comp, Station.Station):
                if comp.get_ip_addr() == conf['target_station']:
                    self.comp = comp
                    found = True
                    break
        if not found:
            raise Exception("Target station % s not found" % conf['target_station'])

        logging.info("Remove any WLAN if existed on the DUT")
        self.testbed.dut.remove_all_wlan()

        logging.info("Configure a WLAN with SSID %s on the DUT" % conf['wlan_cfg']['ssid'])
        self.testbed.dut.cfg_wlan(conf['wlan_cfg'])

        found = False
        for comp in self.testbed.components['AP']:
            if isinstance(comp, RuckusAP):
                if comp.get_base_mac().upper() == conf['active_ap'].upper():
                    found = True
                else:
                    logging.info("Remove all WLAN in non-active AP %s" % comp.get_base_mac())
                    comp.remove_all_wlan()
        if not found:
            raise Exception("Active AP %s not found" % conf['active_ap'])

        logging.info("Remove any WLAN profiles on the remote station")
        self.comp.remove_all_wlan()

        logging.info("Make sure the station disconnects from the wireless networks")
        start_time = time.time()
        current_time = start_time
        while current_time - start_time <= 20:
            res = self.comp.get_current_status()
            if res == "disconnected":
                break
            time.sleep(1)
            current_time = time.time()
        if current_time - start_time > 20:
            raise Exception("The station did not disconnect from the wireless networks")
        logging.info("It has disconnected from the wireless networks")

        logging.info("Configure a WLAN profile with SSID %s on the remote station" % conf['wlan_cfg']['ssid'])
        self.comp.cfg_wlan(conf['wlan_cfg'])

    def test(self):
        logging.info("Ping to %s from the station" % self.ip_addr)
        res = self.comp.ping(self.ip_addr, self.timeout * 1000)
        if res.find("Timeout exceeded") != -1:
            logging.info("Ping FAILED")
            return ["FAIL", res]
        logging.info("Ping OK")
        return ("PASS", "Ping time ~~ %s second(s)" % res)

    def cleanup(self):
        logging.info("Remove all the WLANs on the DUT")
        self.testbed.dut.remove_all_wlan()

        logging.info("Remove all WLAN profiles on the remote station")
        self.comp.remove_all_wlan()

        logging.info("Make sure the station disconnects from the wireless networks")
        start_time = time.time()
        current_time = start_time
        while current_time - start_time <= 20:
            res = self.comp.get_current_status()
            if res == "disconnected":
                break
            time.sleep(1)
            current_time = time.time()
        if current_time - start_time > 20:
            raise Exception("The station did not disconnect from the wireless networks")
        logging.info("It has disconnected from the wireless networks")

