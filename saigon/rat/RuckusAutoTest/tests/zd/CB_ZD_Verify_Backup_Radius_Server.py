"""
"""
import time
import logging
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_server_by_ip_addr
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig


class CB_ZD_Verify_Backup_Radius_Server(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._config_create_linux_pc()


    def test(self):
        self._test_verify_backup_radius_server()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''


    def _cfg_init_test_params(self, conf):
        '''
        conf['tc2f'] is one of the following:
        . 'configurable',
        . 'primary_timeout',
        . 'primary_reconnect',
        . 'server_outage',
        . 'image_upgrade'
        '''
        self.conf = {
            'tc2f': "primary_timeout",
            'server_cfg': {},
            'wlan_cfg': {},
            'sta_tag': '',
            'failover_behavior': "service",
            'negative_condition': "same_ip",
            'ping_timeout_ms': 150 * 1000,
            'check_status_timeout': 120,
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.conf['aaa_static_msg'] = [
            "Primary Server and Secondary Server must be different",
            "First Server and Second Server must be different",
            "cannot be empty",
            "not a valid IP address",
            "Request Timeout must be a number",
            "Max Number of Retries must be a number",
            "Reconnect Primary must be a number",
            "Port is not a valid port number",
        ]

        self.errmsg = ""
        self.passmsg = ""


    def _config_create_linux_pc(self):
        '''
        '''
        if self.conf['failover_behavior'] != "service":
            return

        # Primary Server
        server_tag = server_ip = self.conf['server_cfg']['server_addr']
        if not self.carrierbag.has_key(server_tag):
            server_ins = create_server_by_ip_addr(server_ip)
            self.carrierbag[server_tag] = {}
            self.carrierbag[server_tag]['server_ins'] = server_ins
            service = self.conf['server_cfg']['radiusd_name']
            self.carrierbag[server_tag]['service'] = service


        # Secondary Server
        server_tag = server_ip = self.conf['server_cfg']['secondary_server_addr']
        if not self.carrierbag.has_key(server_tag):
            server_ins = create_server_by_ip_addr(server_ip)
            self.carrierbag[server_tag] = {}
            self.carrierbag[server_tag]['server_ins'] = server_ins
            service = self.conf['server_cfg']['secondary_radiusd_name']
            self.carrierbag[server_tag]['service'] = service


        self.conf['servers'] = {}
        for server_ip in [self.conf['server_cfg']['server_addr'],
                          self.conf['server_cfg']['secondary_server_addr']]:
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


    def _test_verify_backup_radius_server(self):
        '''
        '''
        res = {
            'configurable': self._tc_server_configurable_negative,
            'primary_timeout': self._tc_primary_server_timeout,
            'primary_reconnect': self._tc_primary_server_reconnect,
            'server_outage': self._tc_server_outage,
            'image_upgrade': self._tc_combination_with_upgrade,

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
        interim = 0 #int(self.conf['wlan_cfg']['interim_update'])
        timeout = (timeout + interim) * 60

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


    def _test_check_event(self, change = 'failover', server = 'secondary'):
        '''
        change = ['failover', 'reconnect', 'outage']
        server = ['secondary', 'primary']
        '''
        self.passmsg = ""
        logging.info("Verify All Events/Activities for the '%s' event message" % change)
        self.zd.re_navigate()
        events_log = self.zd.get_events()
        logging.info(events_log)


        #MSG_RADIUS_auth_failover=SSID{id} RADIUS authenticaion server {change} to {server}.
        #SSID[rat-backup-radius-server] RADIUS authenticaion server [failover] to [secondary 192.168.0.250].
        #SSID[rat-backup-radius-server] RADIUS authenticaion server [reconnect] to [primary 192.168.0.252].

        if server in ['secondary']:
            server_ip = self.conf['server_cfg']['secondary_server_addr']

        elif server in ['primary']:
            server_ip = self.conf['server_cfg']['server_addr']


        pattern1 = self.zd.messages['MSG_RADIUS_auth_failover']
        pattern1 = pattern1.replace('{id}', '[%s]' % self.conf['wlan_cfg']['ssid'])
        pattern1 = pattern1.replace('{change}', '[%s]' % change)
        pattern1 = pattern1.replace('{server}', '[%s %s]' % (server, server_ip))

        #MSG_RADIUS_service_outage=Radius server {server} has not responded to multiple requests.  {reason}.
        #Radius server [192.168.0.242] has not responded to multiple requests. [This server may be down or unreachable.].
        pattern2 = self.zd.messages['MSG_RADIUS_service_outage']
        pattern2 = pattern2.replace('{server}', '[%s]' % server_ip)
        pattern2 = pattern2.replace('  {reason}.', '')

        for event in events_log:
            if (change in ['outage'] and pattern2 in event[-1]) or \
            (change in ['failover', 'reconnect'] and \
             pattern1 in event[-1] and change in pattern1):
                self.passmsg = self.passmsg + "The '%s' event is generated. " % change
                self.passmsg = self.passmsg + event[-1]
                self.errmsg = ""

        if not self.passmsg:
            self.errmsg = "There is no '%s' event message generated when radius server is down" % change


    def _tc_primary_server_timeout(self):
        '''
        ZD-183:Failover from Primary to Secondary RADIUS Server
        '''
        self.zd.clear_all_events()

        self._test_make_failover_event('primary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), 'Failover')

        self._test_reconnect_station_to_wlan()
        self._test_check_event('failover', 'secondary')

        self._test_make_failover_event('primary', 'reachable')
        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')


    def _tc_primary_server_reconnect(self):
        '''
        ZD-184:Primary Server Reconnection after Failover
        '''
        self.zd.clear_all_events()

        self._test_make_failover_event('primary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), 'Failover')

        self._test_reconnect_station_to_wlan()

        self._test_make_failover_event('primary', 'reachable')
        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')

        self._test_reconnect_station_to_wlan()
        self._test_check_event('reconnect', 'primary')


    def _tc_server_outage(self, failover = 'primary'):
        '''
        ZD-185:Primary/Secondary RADIUS Availability
        '''
        self.zd.clear_all_events()

        self._test_make_failover_event('primary', 'unreachable')
        self._test_make_failover_event('secondary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), 'Failover')
        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')

        self._test_reconnect_station_to_wlan()
        self._test_check_event('outage', 'primary')
        self._test_check_event('outage', 'secondary')

        if failover != 'primary':
            self._test_make_failover_event('secondary', 'reachable')
            self._test_reconnect_station_to_wlan()
            self._test_check_event('failover', 'secondary')

        if failover != 'secondary':
            self._test_make_failover_event('primary', 'reachable')
            self._test_reconnect_station_to_wlan()
            self._test_check_event('reconnect', 'primary')

        self._test_make_failover_event('primary', 'reachable')
        self._test_make_failover_event('secondary', 'reachable')

        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')


    def _tc_combination_with_upgrade(self):
        '''
        ZD-189:Restore previous configuration when Imaged upgrade/downgrade

        To verify the Backup Accounting Server function works properly after
        ZD has been upgraded (9.0 to 9.2 based on default config)
        '''
        self._tc_primary_server_timeout()


    def _tc_server_configurable_negative(self):
        '''
        Primary/Secondary RADIUS - Configurable

        Negative test for invalid IP address. ZD fires an alert if invalid
        IP address is entered.
          1. Both Primary and Secondary RADIUS servers have the same IP address
          2. IP Address = "0.0.0.0"
          3. IP Address = "255.255.255.255"
          4. Only input one IP address
          (5. Valid IP address) <- Skip
          6. Wildcard Characters (ex. "*", "?"...)
        '''
        neg_cfg = {
            'same_ip': self.conf['server_cfg']['secondary_server_addr'],
            'zero_ip': '0.0.0.0',
            'broadcast_ip': '255.255.255.255',
            'missing_ip': '',
            'wildcard': '192.168.0.???',
        }

        tmp_cfg = copy.deepcopy(self.conf['server_cfg'])
        tmp_cfg.update({
            'server_name': "RadiusAuth-Invalid",
            'server_addr': neg_cfg[self.conf['negative_condition']]
        })

        logging.info("Verify ZD fires an alert when invalid Radius config provided")
        try:
            lib.zd.aaa.create_server(self.zd, **tmp_cfg)

        except Exception, e:
            for msg in self.conf['aaa_static_msg']:
                if msg in e.message:
                    self.passmsg = "Catch the invalid server settings error [%s]" % e.message
                    self.errmsg = ""
                    break

            else:
                self.errmsg = "Catch the error when creating a server [%s]" % e.message

