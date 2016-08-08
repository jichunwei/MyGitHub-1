"""
Description: Test ZoneDirector SpeedFlex Functionality

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: active_ap     : Symbolic name of the active AP - optional
                    target_station: IP address of target wireless station
                    wlan_cfg      : Association parameters, given as a dictionary - optional

   Result type: PASS/FAIL
   Results: PASS: Can download and run SpeedFlex on client at minimum speed and not higher than maximum speed of current radio
            FAIL: - Can't download SpeedFlex on client
                  - Downlink performance acceptable with no packets loss

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
       - Configure a Wlan
       - Configure Station to Associate with Wlan
       - Login to ZoneDirector and go to Monitor -> Current Client.
       - Open SpeedFlex and download SpeedFlex to client
       - Click on Start to performance SpeedFlex test
       - Verify Download performance result.
   3. Cleanup:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
"""

import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.LinuxPC import *
from RuckusAutoTest.components import Helpers as lib


class ZD_SpeedFlex(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'IP address of target station',
                           'active_ap': 'Symbolic name of the active AP - optional',
                           'wlan_cfg': 'Association parameters, given as a dictionary, optional',
                          }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveAllConfigOnZD()
        self._cfgGetTargetStation()
        self._cfgGetActiveAP()
        self._cfgStopZapd()

    def test(self):
        self._cfgCreateWlanOnZD()
        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._cfgAssociateStationToWlan()
        self._cfgGetStaWifiIpAddress()
        # download speedflex
        self._testDownloadSpeedflex()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._cfgStartSpeedFlex()
        self._testSpeedFlexPerformace()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", self.passmsg)

    def cleanup(self):
        self._cfgRemoveAllConfigOnZDAtCleanup()
        self._cfgRemoveWlanFromStation()
        self._cfgStopSpeedFlex()
        self._cfgStartZapd()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 90,
                         check_wlan_timeout = 45,
                         pause = 2.0,
                         default_acct_svr_port = 1813)

        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()

        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("rat-accounting")
        self.target_station = ""

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

        self.zapd_path = ''

    def _cfgStopZapd(self):
        self.zapd_path = self.target_station.stop_zapd()

    def _cfgRemoveAllConfigOnZD(self):
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _cfgGetTargetStation(self):
        logging.info("Find the target station on the test bed")
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                                       self.testbed.components['Station'],
                                                       check_status_timeout = self.conf['check_status_timeout'],
                                                       remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in the test bed" % self.conf['active_ap'])

#
# test()
#
    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

    def _testVerifyWlanOnAPs(self):
        if self.conf.has_key('active_ap'):
            self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.conf['wlan_cfg']['ssid'], self.testbed.components['AP'])

    def _cfgAssociateStationToWlan(self):
        tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], self.conf['check_status_timeout'])

    def _testDownloadSpeedflex(self):
        speedflex_link = lib.zd.sp.get_speedflex_link(self.zd, self.sta_wifi_if['ip'])
        speedflex_url = "https://%s/%s" % (self.zd.ip_addr, speedflex_link)
        self.speedflex_path = self.target_station.download_speedflex(speedflex_url)
        if not self.speedflex_path:
            self.errmsg = "Can't download speedflex from client"

    def _cfgStartSpeedFlex(self):
        logging.info("Start SpeedFlex on client")
        self.target_station.start_speedflex(self.speedflex_path)

    def _testSpeedFlexPerformace(self):
        speed_rate, packets_loss = lib.zd.sp.run_speedflex_performance(self.zd, self.sta_wifi_if['ip'])
        logging.info("Speed Rate: [%s]; Packets Loss: [%s]" % (speed_rate, packets_loss))
        if self.conf['testcase'] == 'test_download':
            if float(speed_rate.split("Mbps")[0]) == 0.0:
                self.errmsg = "Speedflex return incorrect Speed rate: %s" % speed_rate
            else:
                self.passmsg = "Speedflex can download to Windows %s and perform test" % self.conf['sta_os']
        if self.conf['testcase'] == 'test_running':
            if float(speed_rate.split("Mbps")[0]) == 100.0:
                self.errmsg = "Speedflex return incorrect Speed rate: %s" % speed_rate
            elif float(speed_rate.split("Mbps")[0]) > 100.0 and (self.conf['sta_radio'] == 'g' or  self.conf['ap_radio'] == 'g'):
                self.errmsg = "Speedflex return incorrect Speed rate: %s" % speed_rate
            elif float(speed_rate.split("Mbps")[0]) > 165.0 and (self.conf['sta_radio'] == 'n' or  self.conf['ap_radio'] == 'n'):
                self.errmsg = "Speedflex return incorrect Speed rate: %s" % speed_rate
            elif packets_loss.split(":")[-1] != "0%":
                self.errmsg = "There was %s packets loss while running Speedflex" % packets_loss.split(":")[-1]
            else:
                self.passmsg = "Speedflex can running on 11%s client and 11%s AP at %s and %s Packets Loss" % \
                           (self.conf['sta_radio'], self.conf['ap_radio'], speed_rate, packets_loss)

    def _cfgGetStaWifiIpAddress(self):
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(val2)
        self.sta_wifi_if = {'ip': val1, 'mac': val2.lower()}

#
# cleanup()
#
    def _cfgRemoveAllConfigOnZDAtCleanup(self):
        logging.info("Remove all WLANs configured on the ZD")
        lib.zd.wlan.delete_all_wlans(self.zd)
        logging.info("Remove all AAA servers configured on the ZD")
        lib.zd.aaa.remove_all_servers(self.zd)

    def _cfgRemoveWlanFromStation(self):
        if self.target_station:
            logging.info("Remove all WLANs from the station")
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])

    def _cfgStartZapd(self):
        if self.zapd_path:
            self.target_station.start_zapd(self.zapd_path)

    def _cfgStopSpeedFlex(self):
        if self.speedflex_path:
            self.target_station.stop_speedflex(self.speedflex_path.split("\\")[-1])
