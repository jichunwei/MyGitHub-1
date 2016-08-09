"""
Description: Test ZoneDirector SNMP Trap Functionality

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: active_ap     : Symbolic name of the active AP - optional
                    target_station: IP address of target wireless station
                    wlan_cfg      : Association parameters, given as a dictionary - optional

   Result type: PASS/FAIL
   Results: PASS: ZoneDirector sent trap message to configure server
            FAIL: -  ZoneDirector didn't send trap message to configure server


   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
       - Enable SNMP Trap on Zone Director
       - Reboot AP to generate trap message / associate station with incorrect authentication settings
       - Verify Zone Director sent out traps message

   3. Cleanup:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
"""

import logging
import random

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.LinuxPC import *
from RuckusAutoTest.components import Helpers as lib


class ZD_SNMP_Trap(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'IP address of target station',
                           'active_ap': 'Symbolic name of the active AP - optional',
                           'wlan_cfg': 'Association parameters, given as a dictionary, optional',
                          }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        if self.conf.has_key('target_station'):
            self._cfgRemoveAllConfigOnZD()
            self._cfgGetTargetStation()

        if self.conf.has_key('active_ap'):
            self._cfgGetActiveAP()

        self._cfgSaveStrapSettings()
        lib.zd.sys.set_snmp_trap_info(self.zd, self.conf['snmp_trap_cfg'])

    def test(self):
        if self.conf['test_case'] in ['ap_join_trap', 'ap_lost_trap']:
            self._testAPJoinLeaveTrap()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'sta_fail_auth_trap':
            self._testStaFailAuthTrap()
            if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", self.passmsg)

    def cleanup(self):
        if self.conf.has_key('target_station'):
            self._cfgRemoveAllConfigOnZDAtCleanup()
            self._cfgRemoveWlanFromStation()
        self._cfgRestoreTrapSettings()
#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 60,
                         check_wlan_timeout = 45,
                         wait_for_trap_msg = 60,
                         pause = 2.0)

        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()

        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("rat-snmp")
        self.zd = self.testbed.components['ZoneDirector']
        self.linux_server = self.testbed.components['LinuxServer']
        self.target_station = ""
        self.active_ap = ""
        if not self.conf.has_key('snmp_trap_cfg'):
            self.conf['snmp_trap_cfg'] = dict(enabled = True, server_ip = "192.168.0.252")

        self.errmsg = ''
        self.passmsg = ''

        self.current_trap_cfg = ''

    def _cfgSaveStrapSettings(self):
        logging.info("Backup current Zone Director SNMP Trap settings")
        self.current_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.zd)


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

    def _cfgGetStaWifiIpAddress(self):
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(val2)
        self.sta_wifi_if = {'ip': val1, 'mac': val2.lower()}

    def _cfgStartSnifferOnServer(self):
        logging.info("Start Sniffer on Trap server")
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])
        self.linux_server.start_sniffer("-i %s udp dst port 162" % (server_interface))
        self.is_sniffing = True

    def _cfgStopSnifferOnServer(self):
        logging.info("Stop Sniffer on Trap server")
        self.linux_server.stop_sniffer()
        self.is_sniffing = False

    def _testAPJoinLeaveTrap(self):
        self._cfgStartSnifferOnServer()
        logging.info("Reboot Active AP to generate Join/Lost Trap")
        self.active_ap.reboot()
        # Wait for AP join to ZD and ZD send out trap message
        time.sleep(self.conf['wait_for_trap_msg'])
        self._cfgStopSnifferOnServer()

        active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['active_ap'])
        trap_packet_pattern = '%s="%s"' % (self.conf['oid'], active_ap_mac.upper())

        if not self._findTrapPackets(trap_packet_pattern):
            self.errmsg = "Zone Director didn't send out SNMP traps"
        else:
            self.passmsg = "Zone Director sent out SNMP traps when AP join/leave work properly"

    def _testStaFailAuthTrap(self):
        self._cfgCreateWlanOnZD()
        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)
        invalid_wlan_cfg = self.conf['wlan_cfg'].copy()
        invalid_wlan_cfg['key_string'] = utils.make_random_string(random.randint(8, 63), "hex")

        self._cfgStartSnifferOnServer()
        logging.info("Configure station to associate with incorrect WLAN settings")
        #Cherry updated: fixed 15062, the ZD will not send out traps unless there has 10 failed event in a certain time.
        for i in range(10):
            tmethod.assoc_station_with_ssid(self.target_station, invalid_wlan_cfg, self.conf['check_status_timeout'])
        
        # Wait for ZD send out trap when Station failed to authenticate
        time.sleep(self.conf['wait_for_trap_msg'])
        self._cfgStopSnifferOnServer()

        sta_wifi_addr, sta_wifi_mac = self.target_station.get_wifi_addresses()
        trap_packet_pattern = '%s="%s"' % (self.conf['oid'], sta_wifi_mac.upper())
        if not self._findTrapPackets(trap_packet_pattern):
            self.errmsg = "Zone Director didn't send out SNMP traps"
        else:
            self.passmsg = "Zone Director sent out SNMP traps when STA failed authentication work properly"


    def _findTrapPackets(self, search_pattern = ''):
        if self.is_sniffing:
            self._cfgStopSnifferOnServer()
        packets_captured = self.linux_server.read_sniffer('', False)
        logging.info("Trap packets received:")
        logging.info(packets_captured)
        if search_pattern in packets_captured.upper():
            return True
        else: return False

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

    def _cfgRestoreTrapSettings(self):
        if self.current_trap_cfg:
            logging.info("Restore Zone Director SNMP Trap settings")
            lib.zd.sys.set_snmp_trap_info(self.zd, self.current_trap_cfg)

