"""
Description: Test ZoneDirector SNMP Functionality

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
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.LinuxPC import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import snmp_hlp as snmphlp


class ZD_SNMP(Test):
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

        self._cfgSaveSNMPSettings()
        self._cfgEnableSNMP()

    def test(self):
        if self.conf.has_key('target_station'):
            self._cfgCreateWlanOnZD()
            self._testVerifyWlanOnAPs()
            if self.errmsg: return ("FAIL", self.errmsg)
            self._cfgAssociateStationToWlan()
            self._cfgGetStaWifiIpAddress()

        if self.conf['test_case'] == 'mib-walk':
            self._testStandardOIDs()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'ruckusZDSystemInfo':
            self._testRuckusZDSystemInfo()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'ruckusZDSystemStats':
            self._testRuckusZDSystemStats()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'ruckusZDWlANInfo':
            self._testRuckusZDWLANInfo()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'ruckusZDWLANAPInfo':
            self._testRuckusZDWLANAPInfo()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'ruckusZDWLANStaInfo':
            self._testRuckusZDWLANStaInfo()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'checkAPList':
            self._testAPList()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'checkSta_list':
            self._testSta_list()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'checkRougeAPList':
            self._testRougeAPList()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_case'] == 'negativeOID':
            self._testNegativeOID()
            if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", self.passmsg)

    def cleanup(self):
        self._cfgRestoreSNMPSettings()
        if self.conf.has_key('target_station'):
            self._cfgRemoveAllConfigOnZDAtCleanup()
            self._cfgRemoveWlanFromStation()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 90,
                         check_wlan_timeout = 45,
                         pause = 2.0,
                         test_case = '')

        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()

        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("rat-snmp")
        self.target_station = ""

        if not self.conf.has_key('snmp_agent_cfg'):
            self.conf['snmp_agent_cfg'] = dict(enabled = True,
                                               contact = "support@ruckuswireless.com",
                                               location = "880 West Maude Avenue Suite 16",
                                               ro_community = "public",
                                               rw_community = "private")

        self.zd = self.testbed.components['ZoneDirector']
        self.current_snmp_agent_cfg = ""
        self.current_snmp_trap_cfg = ""

        self.errmsg = ''
        self.passmsg = ''

    def _cfgRemoveAllConfigOnZD(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
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

    def _cfgEnableSNMP(self):
        lib.zd.sys.set_snmp_agent_info(self.zd, self.conf['snmp_agent_cfg'])

    def _cfgSaveSNMPSettings(self):
        # backup SNMP for restore in cleanup
        logging.info("Backup Current SNMP setting on Zone Director")
        self.current_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.zd)
        self.current_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.zd)

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

    def _testStandardOIDs(self):
        for oid in ["1.3.6.1.2.1.1.1", "1.3.6.1.2.1.1.2", "1.3.6.1.2.1.1.3",
                    "1.3.6.1.2.1.1.4", "1.3.6.1.2.1.1.5", "1.3.6.1.2.1.1.6"]:
            self.conf['oid'] = oid
            varBindTable = self._doSNMPGet()
            if self.errmsg: return

            varBindTable = self._doSNMPGetNext()
            if self.errmsg: return

        varBindTable = self._doSNMPGetBulk()
        if self.errmsg: return
        self.passmsg = "SNMP MIB-WALK work properly"

    def _testRuckusZDSystemInfo(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetBulk()
        if self.errmsg: return
        self.passmsg = "SNMP can get info in ruckusZDSystemInfo"

    def _testRuckusZDSystemStats(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetBulk()
        if self.errmsg: return
        self.passmsg = "SNMP can get info in ruckusZDSystemStats"

    def _testRuckusZDWLANInfo(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetBulk()
        if self.errmsg: return
        self.passmsg = "SNMP can get info in ruckusZDWlanInfo"

    def _testRuckusZDWLANAPInfo(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetBulk()
        if self.errmsg: return
        self.passmsg = "SNMP can get info in ruckusZDWlanAPInfo"

    def _testRuckusZDWLANStaInfo(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetBulk()
        if self.errmsg: return
        self.passmsg = "SNMP can get info in ruckusZDWlanStaInfo"

    def _testAPList(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        self.passmsg = "SNMP can get AP list correctly"

    def _testSta_list(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        self.passmsg = "SNMP can get Station list correctly"

    def _testRougeAPList(self):
        varBindTable = self._doSNMPGet()
        if self.errmsg: return
        # verify information received
        varBindTable = self._doSNMPGetNext()
        if self.errmsg: return
        # verify information received
        self.passmsg = "SNMP can get Rouge list correctly"

    def _testNegativeOID(self):
        try:
            varBindTable = self._doSNMPGet()
            if self.errmsg: return
        except Exception, e:
            print e.message

        try:
            varBindTable = self._doSNMPGetNext()
            if self.errmsg: return
        except Exception, e:
            print e.message

    def _doSNMPGet(self):
        logging.info("Test GET method to get info from OID [%s] which are supported" % self.conf['oid'])
        oid = [int(x) for x in self.conf['oid'].split('.')]
        oid.append(0)
        oid = tuple(oid)
        varBindTable = snmphlp.snmp_get(self.zd.ip_addr, self.conf['snmp_agent_cfg']['ro_community'], oid)
        if not len(varBindTable):
            self.errmsg = "Can't perform GET method for OID [%s] " % self.conf['oid']
        return varBindTable

    def _doSNMPGetNext(self):
        logging.info("Test GET-NEXT method to get info from OIDs[%s] which are supported" % self.conf['oid'])
        oid = tuple([int(x) for x in self.conf['oid'].split('.')])
        varBindTable = snmphlp.snmp_get_next(self.zd.ip_addr, self.conf['snmp_agent_cfg']['ro_community'], oid)
        if not len(varBindTable):
            self.errmsg = "Can't perform GET-NEXT method for OID [%s] " % self.conf['oid']
        return varBindTable

    def _doSNMPGetBulk(self):
        logging.info("Test GET-BULK method to get info from OIDs[%s] which are supported" % self.conf['oid'])
        oid = tuple([int(x) for x in self.conf['oid'].split('.')])
        varBindTable = snmphlp.snmp_get_bulk(self.zd.ip_addr, self.conf['snmp_agent_cfg']['ro_community'], oid)
        if not len(varBindTable):
            self.errmsg = "Can't perform GET-BULK method for OID [%s] " % self.conf['oid']
        return varBindTable


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

    def _cfgRestoreSNMPSettings(self):
        logging.info("Restore Current SNMP setting on Zone Director")
        if self.current_snmp_agent_cfg:
            lib.zd.sys.set_snmp_agent_info(self.zd, self.current_snmp_agent_cfg)
        if self.current_snmp_trap_cfg:
            lib.zd.sys.set_snmp_trap_info(self.zd, self.current_snmp_trap_cfg)
