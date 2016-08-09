"""
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: target_ip     : IP address of a available destination which is used to verify the connectivity
                                    of the wireless station
                    active_ap     : Symbolic name of the active AP - optional
                    target_station: IP address of target wireless station
                    wlan_cfg      : Association parameters, given as a dictionary - optional
                    auth_info     : Information about the authentication method, given as a dictionary
                                    Refer to module aaa_servers_zd to find the keys to define a specific authentication server
                    acct_info     : Information about the accounting server, given as a dictionary - optional

   Result type: PASS/FAIL
   Results: PASS: Trap accounting packet between ZD and Accounting server exchange properly
            FAIL: ZD send incorrect trap accounting packet

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
       - Configure Accounting Servers on ZD
       - Configure a Wlan with Accounting server Enable
       - Configure Station to Associate with Wlan
       - Test Client can reach target_ip address before do specific test
       - Start Capture packets
       - Perfomce accounting test feature
       - Stop Capture packets
       - Verify trap accounting packet between ZD and Accounting server exchange properly
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


class ZD_Accounting(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_ip': 'IP address to test connectivity',
                           'target_station': 'IP address of target station',
                           'active_ap': 'Symbolic name of the active AP - optional',
                           'wlan_cfg': 'Association parameters, given as a dictionary, optional',
                           'auth_info': 'Information about the authentication method, given as a dictionary'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveAllConfigOnZD()
        self._cfgGetTargetStation()
        self._cfgGetActiveAP()
        self._cfgAccountingServer()

    def test(self):
        try:
            self._cfgDefineAuthSourceOnZD()
            #updated by jluh 2013-11-27
            zd_version = ''
            for i in re.finditer(r"\d+", self.zd.get_version()):
                zd_version = i.group()
            #for mainline build '0.0.0.99'
            if self.conf['test_feature'] == 'invalid_accounting_server_info' and '00099' in zd_version:
                self.errmsg = "The acct server is created successfully, when the acct-server share secret is invalid."
                if self.errmsg: return ("FAIL", self.errmsg)
            #for more than build 9.7
            elif self.conf['test_feature'] == 'invalid_accounting_server_info' and int(zd_version) > 9700:
                self.errmsg = "The acct server is created successfully, when the acct-server share secret is invalid."
                if self.errmsg: return ("FAIL", self.errmsg)
            else:
                pass
        except Exception, e:
            logging.info('Alert msg is: %s' % e.message)
            if self.conf['test_feature'] == 'invalid_accounting_server_secret' \
            and "the same ip address. Please use the same shared secret" in e.message:
                self.passmsg = e.message
                return ("PASS", self.passmsg)
                
        self._cfgCreateWlanOnZD()
        self._cfgStartSnifferOnServer()
        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgAssociateStationToWlan()
        self._cfgGetStaWifiIpAddress()
        self._testStationConnectivity()
        if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'enable_disable_account_server':
            self._testEnableDisableAccountingServer()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'invalid_accounting_server_info':
            self._testInvalidAccountingServerInfo()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'interim_update':
            self._testInterimUpdate()
            if self.errmsg: return ("FAIL", self.errmsg)

        if self.conf['test_feature'] == 'sta_join_leave':
            self._testStaJoinAndLeave()
            if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", self.passmsg)

    def cleanup(self):
        self._cfgRemoveAllConfigOnZDAtCleanup()
        self._cfgRemoveWlanFromStation()
        if self.is_sniffing:
            self._cfgStopSnifferOnServer()

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

        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("rat-accounting")

        # Auth information must be provided
        if not self.conf.has_key('auth_info'):
            raise Exception('Authentication configuration was not given')

        # Give the auth server a name
        if self.conf['auth_info']['type'] != "local":
            self.conf['auth_info']['svr_name'] = "Authentication Server"

        # Give the accounting server a name
        if self.conf.has_key('acct_info'):
            self.conf['acct_info']['svr_name'] = "Accounting Server"

        self.zd = self.testbed.components['ZoneDirector']
        self.conf['wlan_cfg']['acct_svr'] = self.conf['acct_info']['svr_name']
        self.conf['wlan_cfg']['auth_svr'] = self.conf['auth_info']['svr_name']

        self.errmsg = ''
        self.passmsg = ''

        self.is_sniffing = False

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

    def _cfgAccountingServer(self):
        acct_server_info = self.testbed.config['server']
        self.acct_svr_ip_addr = acct_server_info['ip_addr']
        self.accounting_server = LinuxPC(acct_server_info)
        logging.info('Telnet to the Accounting Server at IP address %s successfully' % self.acct_svr_ip_addr)

#
# test()
#
    def _cfgDefineAuthSourceOnZD(self):
        if self.conf['auth_info']['type'] == 'local':
            logging.info("Create a user account on the ZoneDirector")
            self.zd.create_user(self.conf['auth_info']['username'], self.conf['auth_info']['password'])
        else:
            logging.info("Create an authentication server on the ZoneDirector")
            server_info = {'server_addr': self.conf['auth_info']['svr_addr'],
                           'server_port': self.conf['auth_info']['svr_port'],
                           'server_name': self.conf['auth_info']['svr_name']}
            if self.conf['auth_info']['type'] == 'ad':
                server_info['win_domain_name'] = self.conf['auth_info']['svr_info']
            elif self.conf['auth_info']['type'] == 'ldap':
                server_info['ldap_search_base'] = self.conf['auth_info']['svr_info']
            elif self.conf['auth_info']['type'] == 'radius':
                server_info['radius_auth_secret'] = self.conf['auth_info']['svr_info']
            lib.zd.aaa.create_server(self.zd, **server_info)

        # Create radius accouting server if required
        if self.conf.has_key('acct_info'):
            logging.info("Create an accounting server on the ZoneDirector")
            server_info = {'server_addr': self.conf['acct_info']['svr_addr'],
                           'server_port': self.conf['acct_info']['svr_port'],
                           'server_name': self.conf['acct_info']['svr_name'],
                           'radius_acct_secret': self.conf['acct_info']['svr_info']}
            lib.zd.aaa.create_server(self.zd, **server_info)

    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

    def _testVerifyWlanOnAPs(self):
        if self.conf.has_key('active_ap'):
            self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.conf['wlan_cfg']['ssid'], self.testbed.components['AP'])

    def _cfgAssociateStationToWlan(self):
        sta_wlan_cfg = self.conf['wlan_cfg'].copy()
        sta_wlan_cfg['use_onex'] = True
        sta_wlan_cfg['username'] = self.conf['auth_info']['username']
        sta_wlan_cfg['password'] = self.conf['auth_info']['password']
        del sta_wlan_cfg['acct_svr']
        tmethod.assoc_station_with_ssid(self.target_station, sta_wlan_cfg, self.conf['check_status_timeout'])

    def _cfgGetStaWifiIpAddress(self):
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(val2)
        self.sta_wifi_if = {'ip': val1, 'mac': val2.lower()}

    def _cfgStartSnifferOnServer(self):
        server_interface = self.accounting_server.get_interface_name_by_ip(self.acct_svr_ip_addr)
        self.accounting_server.start_sniffer("-i %s udp" % (server_interface))
        self.is_sniffing = True

    def _cfgStopSnifferOnServer(self):
        self.accounting_server.stop_sniffer()
        self.is_sniffing = False

    def _testStationConnectivity(self):
        logging.info("Verify the connectivity from the station when associating to a standard WLAN")
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])

    def _testEnableDisableAccountingServer(self):
        self._cfgRemoveWlanFromStation()
        time.sleep(self.conf['pause'])
        self._cfgStopSnifferOnServer()

        # check trap packets on server
        if len(self._findAccountPackets('Value: Start')) == 0:
            self.errmsg = "ZD not sent out trap accounting when client associate to wlan"
            return

        if len(self._findAccountPackets('Value: Stop')) == 0:
            self.errmsg = "ZD not sent out trap accounting when client associate to wlan"
            return

        # Disable Acccounting on Wlan
        new_wlan_cfg = self.conf['wlan_cfg'].copy()
        new_wlan_cfg['acct_svr'] = "Disabled"
        logging.info("Disable Accounting on WLAN [%s]" % new_wlan_cfg['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, new_wlan_cfg['ssid'], new_wlan_cfg)
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

        self._cfgStartSnifferOnServer()
        self._cfgAssociateStationToWlan()
        self._cfgGetStaWifiIpAddress()
        self._cfgStopSnifferOnServer()

        # check trap packets on server
        if len(self._findAccountPackets('Value: Start')):
            self.errmsg = "ZD sent out trap accounting when Accounting server disabled on wlan"
            return

        self.passmsg = "ZD trap accounting packet update send out work properly when enable and disable Accounting Server on wlan"

    def _testInvalidAccountingServerInfo(self):
        self._cfgStopSnifferOnServer()
        logging.info("Check accounting will not send any 'accounting response' packet to Zone Director")
        if len(self._findAccountPackets('Accounting Response', 'dst %s' % self.zd.ip_addr)):
            self.errmsg = "ZD send out trap accounting to incorrect server"
            return

        self.passmsg = "ZD trap accounting packet update send out work properly with Accounting Server"

    def _testInterimUpdate(self):
        logging.info("Check Interim-Update packets between ZoneDirector and ACcounting Server")
        # wait for ZD send out update packet
        self._cfgStopSnifferOnServer()
        self._cfgStartSnifferOnServer()
        time.sleep(int(self.conf['acct_info']['interim_update']) * 3 * 60)
        accounting_packets = self._findAccountPackets('Value: Interim-Update')
        # verify number update packet send out
        if len(accounting_packets) < 2:
            self.errmsg = "ZD not sent out enough the number of interim-udpate packets to Accounting Server"
            return
        # check time between each packet base on packet timestamp receive on sever
        accounting_packets = self._findAccountPackets('.1813')
        interim_update_time_list = []

        for packet in accounting_packets:
            packet_time = "%s %s" % (packet.split()[0], packet.split()[1].split(".")[0])
            interim_update_time_list.append(packet_time)
        logging.debug(interim_update_time_list)
        for i in range(len(interim_update_time_list) - 1):
            update_duration = time.mktime(time.strptime(interim_update_time_list[i + 1], "%Y-%m-%d %H:%M:%S")) - \
                            time.mktime(time.strptime(interim_update_time_list[i], "%Y-%m-%d %H:%M:%S"))
            update_duration = int(round(update_duration / 60))
            if update_duration != int(self.conf['acct_info']['interim_update']):
                self.errmsg = "ZD sent incorrect interim-update duration"
                return

        self.passmsg = "ZD interim packet update send out work properly with Accounting Server"

    def _testStaJoinAndLeave(self):
        self._cfgRemoveWlanFromStation()
        time.sleep(self.conf['pause'])
        self._cfgStopSnifferOnServer()

        # check trap packets on server
        if len(self._findAccountPackets('Value: Start')) == 0:
            self.errmsg = "ZD not sent out trap accounting when client associate to wlan"
            return

        if len(self._findAccountPackets('Value: Stop')) == 0:
            self.errmsg = "ZD not sent out trap accounting when client associate to wlan"
            return

        self.passmsg = "ZD send out trap packet to Accounting Server whenever client join/leave work properly"

    def _findAccountPackets(self, search_pattern = '', filter = ''):
        if self.is_sniffing:
            self._cfgStopSnifferOnServer()
        if filter:
            packets_captured = self.accounting_server.read_sniffer(filter)
        else:
            packets_captured = self.accounting_server.read_sniffer("dst port %s" % self.conf['default_acct_svr_port'])

        acct_trap_packets = []
        for packet in packets_captured:
            if search_pattern in packet:
                acct_trap_packets.append(packet)
        logging.debug(acct_trap_packets)
        return acct_trap_packets

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

