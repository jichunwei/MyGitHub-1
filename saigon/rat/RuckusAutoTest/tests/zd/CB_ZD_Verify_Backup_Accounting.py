"""
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_server_by_ip_addr

class CB_ZD_Verify_Backup_Accounting(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._config_create_linux_pc()
        self._config_start_radius_servers()


    def test(self):
        self._test_verify_backup_accounting()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _cfg_init_test_params(self, conf):
        '''
        conf['tc2f'] is one of the following:
        . 'primary_timeout',
        . 'primary_reconnect',
        . 'server_outage',
        . 'image_upgrade'
        '''
        self.conf = {
            'tc2f': "primary_timeout",
            'server_cfg': {},
            'wlan_cfg': {},
            'failover_behavior': "service",
            'interim_update': '',
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        
        if self.conf['interim_update']:
            #For hotspot wlan, no interim update configuration in wlan.
            self.interim_update = self.conf['interim_update']
        else:
            self.interim_update = self.conf['wlan_cfg']['interim_update']

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
                #Modified by Liang Aihua on 2014-10-8 for error command "service radiusd1 start" 
                #server.start_radius_server(service)
                server.start_radius_server()
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
        #Modified by Liang Aihua on 2014-10-8 for error command "service radiusd1 status"
        #server.stop_radius_server(service)
        server.stop_radius_server()


    def _test_verify_backup_accounting(self):
        '''
        '''
        res = {
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
        interim = int(self.interim_update)        
        timeout = timeout + interim*60
        
        return timeout


    def _get_reconnect_time(self):
        '''
        For Accounting Server Failover,
          reconnect_time = primary_reconnect + interim_update
        '''
        timeout = int(self.conf['server_cfg']['primary_reconnect'])
        #interim = int(self.conf['wlan_cfg']['interim_update'])
        interim = int(self.interim_update)
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


        #MSG_RADIUS_acct_failover=SSID{id} RADIUS accounting server {change} to {server}.
        #SSID[rat-backup-acct-server] RADIUS accounting server [failover] to [secondary 192.168.0.242].
        #SSID[rat-backup-acct-server] RADIUS accounting server [reconnect] to [primary 192.168.0.252].
        if server in ['secondary']:
            server_ip = self.conf['server_cfg']['secondary_server_addr']

        elif server in ['primary']:
            server_ip = self.conf['server_cfg']['server_addr']


        pattern1 = self.zd.messages['MSG_RADIUS_acct_failover']
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
        ZD-186:Failover from Primary to Backup Accounting server
        '''
        self.zd.clear_all_events()
        self._test_make_failover_event('primary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), 'Failover')
        self._test_check_event('failover', 'secondary')
        
        self._test_make_failover_event('primary', 'reachable')
        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')


    def _tc_primary_server_reconnect(self):
        '''
        ZD-187:Failover from Backup to Primary Accounting server
        '''
        self.zd.clear_all_events()
        self._test_make_failover_event('primary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), 'Failover')

        self._test_make_failover_event('primary', 'reachable')
        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')

        self._test_check_event('reconnect', 'primary')


    def _tc_server_outage(self, failover = 'primary'):
        '''
        ZD-188:Primary / Backup Accounting server are gone
        '''
        self.zd.clear_all_events()
        self._test_make_failover_event('primary', 'unreachable')
        self._test_make_failover_event('secondary', 'unreachable')
        self._wait_for_event(self._get_retry_timeout(), 'Failover')
        self._wait_for_event(self._get_reconnect_time(), 'Reconnect')

        self._test_check_event('outage', 'primary')
        self._test_check_event('outage', 'secondary')

        if failover != 'primary':
            self._test_make_failover_event('secondary', 'reachable')
            self._test_check_event('failover', 'secondary')

        if failover != 'secondary':
            self._test_make_failover_event('primary', 'reachable')
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