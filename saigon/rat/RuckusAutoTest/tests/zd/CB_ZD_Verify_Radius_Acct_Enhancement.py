"""
"""
import time
import logging
import re
from copy import deepcopy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_server_by_ip_addr
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig


class CB_ZD_Verify_Radius_Acct_Enhancement(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._config_create_linux_pc()
        self._config_start_radius_servers()


    def test(self):
        self._test_verify_radius_acct_enhancement()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''
        pass


    def _cfg_init_test_params(self, conf):
        '''
        conf['tc2f'] is one of the following:
        . 'acct_status_type',
        . 'acct_session_time',
        . 'acct_session_id',
        . 'acct_multi_session_id',
        . 'acct_ruckus_sta_rssi',
        . 'acct_new_interim_update',
        . 'acct_backup_accounting',
        '''
        self.conf = {
            'tc2f': "acct_session_id",
            'server_cfg': {},
            'wlan_cfg': {},
            'sta_tag': '',
            'failover_behavior': "service",
            'ping_timeout_ms': 150 * 1000,
            'check_status_timeout': 120,
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.conf['aaa_static_msg'] = [
            "Primary Server and Secondary Server must be different",
            "cannot be empty",
            "not a valid IP address",
            "Request Timeout must be a number",
            "Max Number of Retries must be a number",
            "Reconnect Primary must be a number",
            "Port is not a valid port number",
        ]

        self.conf['ACCT_PATTERNS'] = {
            'acct_status_interim_update':
                "(?P<attr>Acct-Status-Type)\(\d{1,}\): (?P<value>Alive|Interim-Update)\(\d{1,}\)",

            'acct_status_start':
                "(?P<attr>Acct-Status-Type)\(\d{1,}\): (?P<value>Start)\(\d{1,}\)",

            'acct_status_stop':
                "(?P<attr>Acct-Status-Type)\(\d{1,}\): (?P<value>Stop)\(\d{1,}\)",

            'acct_session_time':
                "(?P<attr>Acct-Session-Time)\(\d{1,}\): (?P<value>\d{1,})",

            'acct_session_id':
                "(?P<attr>Acct-Session-Id)\(\d{1,}\): (?P<value>\w{1,}-\w{1,})",

            'acct_multi_session_id':
                "(?P<attr>Acct-Multi-Session-Id)\(\d{1,}\): (?P<value>\w{1,})",

            'vendor_specific':
                "(?P<attr>Unknown-Attribute): (?P<value>0{1,6}\w{1,})",
        }

        self.errmsg = ""
        self.passmsg = ""


    def _config_create_linux_pc(self):
        '''
        '''
        # Primary Server
        server_tag = server_ip = self.conf['server_cfg']['server_addr']
        if not self.carrierbag.has_key(server_tag):
            server_ins = create_server_by_ip_addr(server_ip)
            self.carrierbag[server_tag] = {}
            self.carrierbag[server_tag]['server_ins'] = server_ins
            service = self.conf['server_cfg']['radiusd_name']
            self.carrierbag[server_tag]['service'] = service

        self.conf['servers'] = {}
        for server_ip in [self.conf['server_cfg']['server_addr']]:
            self.conf['servers'].update({
                server_ip: self.carrierbag[server_ip]
            })


    def _config_start_radius_servers(self):
        '''
        '''
        for server_ip in self.conf['servers'].iterkeys():
            self._test_start_radius(server_ip)


    def _test_start_radius(self, server_ip, timeout = 10):
        '''
        '''
        log_msg = "Start Radius server %s on LinuxPC component [%s]"
        server = self.conf['servers'][server_ip]['server_ins']
        service = self.conf['servers'][server_ip]['service']

        count = 0
        tries = 3
        while count <= tries:
            try:
                logging.debug(log_msg % (service, server_ip))
                server.start_radius_server(service)
                break

            except Exception, e:
                logging.debug(e.message)
                time.sleep(timeout)
                count += 1


    def _test_stop_radius(self, server_ip):
        '''
        '''
        log_msg = "Stop Radius server %s on LinuxPC component [%s]"

        server = self.conf['servers'][server_ip]['server_ins']
        service = self.conf['servers'][server_ip]['service']

        logging.debug(log_msg % (service, server_ip))
        server.stop_radius_server(service)


    def _test_reconnect_station_to_wlan(self):
        '''
        '''
        self.sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        tconfig.remove_all_wlan_from_station(
            self.sta, check_status_timeout = self.conf['check_status_timeout']
        )

        tmethod.assoc_station_with_ssid(
            self.sta, self.conf['wlan_cfg'],
            self.conf['check_status_timeout']
        )

        res, val1, val2 = tmethod.renew_wifi_ip_address(
            self.sta, self.conf['check_status_timeout']
        )


    def _config_start_tshark_capture_packets(self):
        '''
        /usr/sbin/tshark -f "udp port 1813" -i eth0 -w /tmp/tshark_capture.pcap
        '''
        server_ip = self.conf['current_server_ip']
        server = self.conf['servers'][server_ip]['server_ins']
        server_interface = server.get_interface_name_by_ip(server_ip)
        server_port = self.conf['current_server_port']

        server.cmd("pkill tshark")

        cap_file = "/tmp/tshark_capture.pcap"
        server.cmd("rm -f %s" % cap_file)

        cap_filter = "udp port %s" % server_port
        cap_inf = "%s" % server_interface
        cap_file = "/tmp/tshark_capture.pcap"
        cmd = "/usr/sbin/tshark -f '%s' -i %s -w %s &" % (cap_filter, cap_inf, cap_file)
        server.cmd(cmd)

        self.conf['is_sniffing'] = True


    def _config_read_tshark_captured_packets(self):
        '''
        /usr/sbin/tshark -nVr /tmp/tshark_capture.pcap | grep "AVP:"
        '''
        server_ip = self.conf['current_server_ip']
        server = self.conf['servers'][server_ip]['server_ins']

        cap_file = "/tmp/tshark_capture.pcap"
        cmd = "/usr/sbin/tshark -nVr %s" % (cap_file)
        packets_captured = server.do_cmd(cmd)
        #packets_captured = server.cmd(cmd)

        return packets_captured


    def _config_set_default_acct_server(self, server = 'primary'):
        '''
        '''
        self.conf['current_server_ip'] = self.conf['server_cfg']['server_addr']
        self.conf['current_server_port'] = self.conf['server_cfg']['server_port']


    def _config_swap_interim_update(self, interim_update = 3):
        '''
        '''
        self.conf['wlan_cfg']['interim_update'], interim_update = \
            interim_update, self.conf['wlan_cfg']['interim_update']

        return interim_update


    def _test_find_acct_packets(self, patterns_list = [], filter_string = ''):
        '''
        '''
        acct_trap_packets = []
        acct_trap_packets_compelete = []

        packets_captured = self._config_read_tshark_captured_packets()
        packets_captured_list = packets_captured.split('\r\n\r\n')
        logging.debug(packets_captured_list)
        
        #@author: liang aihua,@change: change packet add rule--interim-update+session_time,@since: 2015-5-26
        #for packet in packets_captured:
        #    for pattern in patterns_list:
        #        matcher = re.compile(pattern).search(packet)
        #        if matcher:
        #            result = matcher.groupdict()
        #            acct_trap_packets.append(result)
        for packet in packets_captured_list:
            for pattern in patterns_list:
                matcher = re.compile(pattern).search(packet)
                if matcher:
                    if pattern == patterns_list[len(patterns_list)-1]:
                        acct_trap_packets_compelete.append(packet)
                    else:
                        continue
                else:
                    break
        packet_id_list = []            
        PI_Pattern = "(?P<attr>Packet\sidentifier):(?P<value>.*\(\d+\))"
        acct_trap_packets_tmp = deepcopy(acct_trap_packets_compelete)
        for packet in acct_trap_packets_compelete:
            m = re.compile(PI_Pattern).search(packet)
            if m:
                result = m.groupdict()
                if result not in packet_id_list:
                    packet_id_list.append(result)
                else:
                    acct_trap_packets_tmp.remove(packet)
                    
        for packet in acct_trap_packets_tmp:
            for pattern in patterns_list:
                matcher = re.compile(pattern).search(packet)
                if matcher:
                    result = matcher.groupdict()
                    acct_trap_packets.append(result)

        # finish checking all packets and all patterns
        return acct_trap_packets


    def _test_verify_radius_acct_enhancement(self):
        '''
        '''
        res = {
            'acct_status_type': self._tc_verify_attr_acct_status_type,
            'acct_session_time': self._tc_verify_attr_acct_session_time,
            'acct_session_id': self._tc_verify_attr_acct_session_id,
            'acct_multi_session_id': self._tc_verify_attr_acct_multi_session_id,
            'acct_ruckus_sta_rssi': self._tc_verify_attr_ruckus_sta_rssi,
            'acct_new_interim_update': self._tc_verify_new_interim_update,
            'acct_backup_accounting': self._tc_verify_backup_accounting,

        }[self.conf['tc2f']]()


    def _get_retry_timeout(self):
        '''
        '''
        timeout = int(self.conf['server_cfg']['primary_timeout'])
        timeout = timeout * int(self.conf['server_cfg']['failover_retries'])

        return timeout


    def _get_reconnect_time(self):
        '''
        For Accounting Server Failover,
          reconnect_time = primary_reconnect + interim_update
        '''
        timeout = int(self.conf['server_cfg']['primary_reconnect'])
        interim = int(self.conf['wlan_cfg']['interim_update'])
        timeout = (timeout + interim) * 60

        return timeout


    def _get_interim_update_time(self):
        '''
        '''
        interim = int(self.conf['wlan_cfg']['interim_update'])
        timeout = interim * 60

        return timeout


    def _wait_for_event(self, timeout, event = ""):
        logging.info("Waiting %s seconds for %s event..." % (timeout, event))
        time.sleep(timeout)


    def _test_edit_aaa_cfg(self, server = 'primary', config = 'reachable'):
        '''
        '''
        tmp_port = 1234
        new_cfg = {
            'primary': {
                'server_addr': self.conf['server_cfg']['server_addr'],
                'server_port': {
                    'reachable': self.conf['server_cfg']['server_port'],
                    'unreachable': tmp_port,
                }[config],
            },
            'secondary': {
                'secondary_server_addr': self.conf['server_cfg']['secondary_server_addr'],
                'secondary_server_port': {
                    'reachable': self.conf['server_cfg']['secondary_server_port'],
                    'unreachable': tmp_port,
                }[config],
            }
        }

        lib.zd.aaa.edit_server(self.zd, self.conf['server_cfg']['server_name'], new_cfg[server])


    def _test_make_failover_event(self, server = 'primary', config = 'reachable'):
        '''
        '''
        if self.conf['failover_behavior'] == "config":
            return self._test_edit_aaa_cfg(server, config)

        elif self.conf['failover_behavior'] == "service":
            param = {
                'primary': self.conf['server_cfg']['server_addr'],
                'secondary': self.conf['server_cfg']['secondary_server_addr']
            }[server]
            return {
                'reachable': self._test_start_radius,
                'unreachable': self._test_stop_radius,
            }[config](param)


    def _test_acct_when_client_roaming(self, patterns_list):
        '''
        '''
        self._config_set_default_acct_server()

        self._config_start_tshark_capture_packets()

        self._test_reconnect_station_to_wlan()


        # before roaming
        acct_trap_packets = self._test_find_acct_packets(patterns_list)
        session_id_prior_roaming = acct_trap_packets

        self._config_start_tshark_capture_packets()

        # roaming
        self._test_make_client_roam()


        # after roaming
        acct_trap_packets = self._test_find_acct_packets(patterns_list)
        session_id_after_roaming = acct_trap_packets

        return session_id_prior_roaming, session_id_after_roaming


    def _test_make_client_roam(self):
        '''
        '''
        clients = lib.zd.cac.get_all_clients_briefs(self.zd)
        for client_info in clients.itervalues():
            ap_mac_addr = client_info['ap']
            lib.zd.aps.reboot_ap_by_mac_addr(self.zd, ap_mac_addr)

        time.sleep(30)


    def _test_verify_session_id(
            self, session_id_prior_roaming, session_id_after_roaming
        ):
        '''
        '''
        if not session_id_prior_roaming or not session_id_after_roaming:
            self.errmsg = "Not all Session ID are captured"
            return False

        session_id_list = session_id_prior_roaming
        session_id_list.extend(session_id_after_roaming)
        logging.debug("Acct-Session-Id captured: %s" % session_id_list)

        count = 0
        for i in range(1, len(session_id_list)):
            if session_id_list[i] != session_id_list[i - 1]:
                count += 1

        if count == 0:
            self.errmsg = "No new Session ID generated"
            return False

        return True


    def _test_verify_multi_session_id(
            self, session_id_prior_roaming, session_id_after_roaming
        ):
        '''
        '''
        if not session_id_prior_roaming or not session_id_after_roaming:
            self.errmsg = "Not all Multi Session ID are captured"
            return False

        session_id_list = session_id_prior_roaming
        session_id_list.extend(session_id_after_roaming)
        logging.debug("Multi Session IDs captured: %s" % session_id_list)

        for i in range(1, len(session_id_list)):
            if session_id_list[i] != session_id_list[i - 1]:
                self.errmsg = "Not all Multi Session ID are the same"
                return False

        return True


    def _test_verify_interim_update(self, acct_trap_packets, periods, interval):
        '''
        '''
        session_time_list = []

        for packet in acct_trap_packets:
            if packet['attr'] == "Acct-Session-Time":
                session_time_list.append(int(packet['value']))

        session_time_list = session_time_list[-periods:]
        logging.debug("Acct-Session-Time captured: %s" % session_time_list)
        self.conf['session_time_list'] = session_time_list

        for i in range(1, len(session_time_list)):
            if session_time_list[i] - session_time_list[i - 1] != interval:
                self.errmsg = "Not all Interim-Update are correct: %s" % session_time_list
                return False

        return True


    def _tc_verify_attr_acct_status_type(self):
        '''
        '''
        self._config_set_default_acct_server()

        self._config_start_tshark_capture_packets()

        self._test_reconnect_station_to_wlan()

        patterns_list = [
            self.conf['ACCT_PATTERNS']['acct_status_start'],
        ]
        acct_trap_packets = self._test_find_acct_packets(patterns_list)
        logging.debug(acct_trap_packets)

        if not acct_trap_packets:
            self.errmsg = "Accounting Status Start was not captured"

        if self.errmsg:
            return self.conf

        self.passmsg = "Accounting Status Start was captured"


    def _tc_verify_attr_acct_session_time(self, periods = 3, reconnect_sta = True):
        '''
        '''
        self._config_set_default_acct_server()

        self._config_start_tshark_capture_packets()

        if reconnect_sta:
            self._test_reconnect_station_to_wlan()

        patterns_list = [
            self.conf['ACCT_PATTERNS']['acct_status_interim_update'],
            self.conf['ACCT_PATTERNS']['acct_session_time'],
        ]

        interval = self._get_interim_update_time()
        timeout = periods * interval
        self._wait_for_event(timeout, "Interim-Update")

        acct_trap_packets = self._test_find_acct_packets(patterns_list)

        self._test_verify_interim_update(acct_trap_packets, periods, interval)

        if self.errmsg:
            return self.conf

        self.passmsg = "All Accounting Interim-Update are correct"


    def _tc_verify_attr_acct_session_id(self):
        '''
        '''
        patterns_list = [
            self.conf['ACCT_PATTERNS']['acct_session_id'],
        ]

        session_id_prior_roaming, session_id_after_roaming = \
            self._test_acct_when_client_roaming(patterns_list)

        self._test_verify_session_id(
            session_id_prior_roaming, session_id_after_roaming
        )

        if self.errmsg:
            return self.conf

        self.passmsg = "New Session ID is generated when roaming"


    def _tc_verify_attr_acct_multi_session_id(self):
        '''
        '''
        patterns_list = [
            self.conf['ACCT_PATTERNS']['acct_multi_session_id'],
        ]

        session_id_prior_roaming, session_id_after_roaming = \
            self._test_acct_when_client_roaming(patterns_list)

        self._test_verify_multi_session_id(
            session_id_prior_roaming, session_id_after_roaming
        )

        if self.errmsg:
            return self.conf

        self.passmsg = "All Multi Session IDs are the same"


    def _tc_verify_attr_ruckus_sta_rssi(self, periods = 1):
        '''
        '''
        self._config_set_default_acct_server()

        self._config_start_tshark_capture_packets()

        self._test_reconnect_station_to_wlan()

        patterns_list = [
            self.conf['ACCT_PATTERNS']['vendor_specific'],
        ]

        interval = self._get_interim_update_time()
        timeout = periods * interval
        self._wait_for_event(timeout, "Interim-Update")

        acct_trap_packets = self._test_find_acct_packets(patterns_list)

        if not acct_trap_packets:
            self.errmsg = "Ruckus-Sta-RSSI was not captured"

        if self.errmsg:
            return self.conf

        self.passmsg = "Ruckus-Sta-RSSI was captured"


    def _tc_verify_new_interim_update(self, periods = 3):
        '''
        client-side only as we don't change server's configuration
        '''
        interim_update = self._config_swap_interim_update()

        lib.zd.wlan.edit_wlan(
            self.zd, self.conf['wlan_cfg']['ssid'], self.conf['wlan_cfg']
        )

        self._tc_verify_attr_acct_session_time(periods)

        self._config_swap_interim_update(interim_update)

        lib.zd.wlan.edit_wlan(
            self.zd, self.conf['wlan_cfg']['ssid'], self.conf['wlan_cfg']
        )

        if self.errmsg:
            return self.conf

        self.passmsg = "All Accounting Interim-Update are correct"


    def _tc_verify_backup_accounting(self, periods = 3):
        '''
        client-side only as we don't change server's configuration
        '''
        self._tc_verify_attr_acct_session_time(periods)
        session_time_list_prior_outage = self.conf['session_time_list']

        self._test_make_failover_event('primary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), "Accounting Primary Failover")

        self._test_make_failover_event('primary', 'reachable')
        self._wait_for_event(self._get_reconnect_time(), "Accounting Primary Reconnect")

        self._tc_verify_attr_acct_session_time(periods, False)
        session_time_list_after_reconnect = self.conf['session_time_list']

        logging.debug("Acct-Session-Time captured: %s %s" %
                      (session_time_list_prior_outage,
                      session_time_list_after_reconnect))

        session_time_last_outage = session_time_list_prior_outage[-1:][0]
        session_time_first_reconnect = session_time_list_after_reconnect[0]

        if session_time_first_reconnect <= session_time_last_outage:
            self.errmsg = "Acct-Session-Time is not incremented after Primary Radius reconnection"

        if self.errmsg:
            return self.conf

        self.passmsg = "Acct-Session-Time is incremented after Primary Radius reconnection"

